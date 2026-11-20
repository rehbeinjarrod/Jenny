"""Tests for the Throughput script, at its interface: `python3 throughput.py
<jira.json> --today YYYY-MM-DD [--leave-out KEY,...] [--into inputs.json]`
over what the Atlassian MCP returned for the two done-item searches, printing
the weekly Throughput, finished Epics, never-in-progress items and left-out
items as JSON (exit 0), naming input problems (exit 1) or naming what can't
be read (exit 2).

Run: python3 -m unittest discover -s acceptance/forecast
"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills" / "plan" / "scripts" / "throughput.py"
FIXTURE = ROOT / "acceptance" / "fixtures" / "jira" / "hall-done-items.json"

TODAY = "2026-11-19"  # a Thursday: the last full week is that of 2026-11-09


def item(key, done="2026-11-10T10:00:00.000+1100", parent=None, parent_done=False, level=0,
         resolution="Done", status="Done", category="done", labels=(), created="2026-11-01T09:00:00.000+1100",
         category_changed=None):
    fields = {
        "issuetype": {"name": "Story" if level == 0 else "Sub-task", "hierarchyLevel": level},
        "status": {"name": status, "statusCategory": {"key": category}},
        "resolution": {"name": resolution} if resolution else None,
        "resolutiondate": done if resolution else None,
        "statuscategorychangedate": category_changed or done,
        "created": created,
        "labels": list(labels),
    }
    if parent:
        fields["parent"] = {"key": parent, "fields": {
            "issuetype": {"name": "Epic", "hierarchyLevel": 1},
            "status": {"name": "Done" if parent_done else "In Progress",
                       "statusCategory": {"key": "done" if parent_done else "indeterminate"}}}}
    return {"key": key, "fields": fields}


class Run:
    def __init__(self, done, never=(), extra=()):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        self.jira = self.dir / "jira.json"
        self.jira.write_text(json.dumps({"done": done, "never_in_progress": list(never)}), encoding="utf-8")
        self.extra = list(extra)

    def __call__(self, *args, today=TODAY):
        p = subprocess.run([sys.executable, str(SCRIPT), str(self.jira), "--today", today, *self.extra, *args],
                           capture_output=True, text=True)
        return p.returncode, p.stdout, p.stderr.splitlines()

    def out(self, *args, today=TODAY):
        code, out, err = self(*args, today=today)
        assert code == 0, err
        return json.loads(out)

    def close(self):
        self._tmp.cleanup()


class ThroughputTest(unittest.TestCase):
    def run_on(self, done, never=()):
        r = Run(done, never)
        self.addCleanup(r.close)
        return r

    def test_weeks_run_from_the_oldest_item_to_the_last_full_week_with_zero_weeks_kept(self):
        r = self.run_on([item("H-1", "2026-10-21T12:00:00.000+1100"), item("H-2", "2026-10-22T12:00:00.000+1100"),
                         item("H-3", "2026-11-12T09:00:00.000+1100")])
        out = r.out()
        self.assertEqual(out["weeks"], [{"week": "2026-10-19", "done": 2}, {"week": "2026-10-26", "done": 0},
                                        {"week": "2026-11-02", "done": 0}, {"week": "2026-11-09", "done": 1}])
        self.assertEqual(out["window"], {"from": "2026-10-19", "to": "2026-11-09"})

    def test_an_item_done_this_week_waits_for_the_week_to_end(self):
        r = self.run_on([item("H-1", "2026-11-10T10:00:00.000+1100"), item("H-2", "2026-11-17T10:00:00.000+1100")])
        out = r.out()
        self.assertEqual(out["weeks"], [{"week": "2026-11-09", "done": 1}])
        self.assertEqual(out["left_out"], [{"key": "H-2", "reason": "done this week, which has not ended"}])

    def test_history_stops_at_52_weeks(self):
        r = self.run_on([item("H-1", "2025-06-02T10:00:00.000+1000"), item("H-2", "2026-11-10T10:00:00.000+1100")])
        out = r.out()
        self.assertEqual(len(out["weeks"]), 52)
        self.assertEqual(out["weeks"][0]["week"], "2025-11-17")
        self.assertEqual(out["left_out"], [{"key": "H-1", "reason": "done before the 52 weeks read"}])

    def test_the_status_category_change_date_stands_in_when_no_resolution_is_set(self):
        r = self.run_on([item("H-1", resolution=None, category_changed="2026-11-03T10:00:00.000+1100")])
        self.assertEqual(r.out()["weeks"], [{"week": "2026-11-02", "done": 1}, {"week": "2026-11-09", "done": 0}])

    def test_wont_do_by_resolution_status_or_label_is_left_out(self):
        r = self.run_on([item("H-1"), item("H-2", resolution="Won't Do"), item("H-3", status="Won't Do"),
                         item("H-4", status="Cancelled"), item("H-5", labels=["wontdo"]),
                         item("H-6", resolution="Duplicate")])
        out = r.out()
        self.assertEqual(out["weeks"], [{"week": "2026-11-09", "done": 1}])
        self.assertEqual(out["left_out"], [
            {"key": "H-2", "reason": "won't do: resolution Won't Do"},
            {"key": "H-3", "reason": "won't do: status Won't Do"},
            {"key": "H-4", "reason": "won't do: status Cancelled"},
            {"key": "H-5", "reason": "won't do: label wontdo"},
            {"key": "H-6", "reason": "won't do: resolution Duplicate"},
        ])

    def test_never_in_progress_items_are_counted_and_named(self):
        r = self.run_on([item("H-1"), item("H-2", created="2026-11-02T09:00:00.000+1100")], never=["H-2"])
        out = r.out()
        self.assertEqual(out["weeks"], [{"week": "2026-11-09", "done": 2}])
        self.assertEqual(out["never_in_progress"], [{"key": "H-2", "done": "2026-11-10"}])
        self.assertEqual(out["left_out"], [])

    def test_never_in_progress_and_closed_within_the_hour_is_closed_without_work(self):
        r = self.run_on([item("H-1"), item("H-2", created="2026-11-10T09:30:00.000+1100")], never=["H-2"])
        out = r.out()
        self.assertEqual(out["weeks"], [{"week": "2026-11-09", "done": 1}])
        self.assertEqual(out["never_in_progress"], [])
        self.assertEqual(out["left_out"], [{"key": "H-2", "reason": "closed without work: never in progress, "
                                                                    "done within an hour of being made"}])

    def test_the_operator_leaves_out_a_never_in_progress_item(self):
        r = self.run_on([item("H-1"), item("H-2", created="2026-11-02T09:00:00.000+1100")], never=["H-2"])
        out = r.out("--leave-out", "H-2")
        self.assertEqual(out["weeks"], [{"week": "2026-11-09", "done": 1}])
        self.assertEqual(out["never_in_progress"], [])
        self.assertEqual(out["left_out"], [{"key": "H-2", "reason": "left out by the Operator"}])

    def test_a_left_out_key_not_read_is_a_problem(self):
        r = self.run_on([item("H-1")])
        code, out, err = r("--leave-out", "H-9")
        self.assertEqual(code, 1)
        self.assertEqual(err, ["--leave-out: H-9 is not a done item read"])
        self.assertEqual(out, "")

    def test_items_below_standard_level_or_not_done_are_not_counted(self):
        r = self.run_on([item("H-1"), item("H-2", level=-1), item("H-3", category="indeterminate", status="In Review")])
        out = r.out()
        self.assertEqual(out["weeks"], [{"week": "2026-11-09", "done": 1}])
        self.assertEqual(out["left_out"], [{"key": "H-2", "reason": "not a standard-level item"},
                                           {"key": "H-3", "reason": "not done: status In Review"}])

    def test_finished_epics_count_every_standard_level_child_read(self):
        r = self.run_on([item("H-1", parent="H-10", parent_done=True), item("H-2", parent="H-10", parent_done=True),
                         item("H-3", parent="H-11", parent_done=False), item("H-4", parent="H-12", parent_done=True),
                         item("H-5", parent="H-12", parent_done=True, resolution="Won't Do"), item("H-6")])
        self.assertEqual(r.out()["finished_epics"], [{"key": "H-10", "stories": 2}, {"key": "H-12", "stories": 1}])

    def test_a_finished_epic_counts_its_real_work_done_outside_the_weeks_counted(self):
        r = self.run_on([item("H-1", parent="H-10", parent_done=True),
                         item("H-2", "2025-06-02T10:00:00.000+1000", parent="H-10", parent_done=True),
                         item("H-3", "2026-11-17T10:00:00.000+1100", parent="H-10", parent_done=True),
                         item("H-4", parent="H-10", parent_done=True, created="2026-11-01T09:00:00.000+1100")],
                        never=["H-4"])
        out = r.out("--leave-out", "H-4")
        self.assertEqual(out["finished_epics"], [{"key": "H-10", "stories": 3}])
        self.assertEqual(out["counted"], 1)

    def test_an_epic_closed_as_wont_do_is_not_finished(self):
        i = item("H-1", parent="H-10", parent_done=True)
        i["fields"]["parent"]["fields"]["status"]["name"] = "Won't Do"
        r = self.run_on([i])
        self.assertEqual(r.out()["finished_epics"], [])

    def test_resolutions_match_whatever_their_case(self):
        r = self.run_on([item("H-1", resolution="done"), item("H-2", resolution="FIXED")])
        self.assertEqual(r.out()["counted"], 2)

    def test_closed_without_work_holds_when_one_time_is_a_bare_date(self):
        r = self.run_on([item("H-1", "2026-11-10T00:30:00.000+1100", created="2026-11-10")], never=["H-1"])
        self.assertEqual(r.out()["left_out"][0]["key"], "H-1")

    def test_a_field_of_the_wrong_shape_is_named(self):
        i = item("H-1")
        i["fields"]["labels"] = "wontdo"
        r = self.run_on([i])
        code, out, err = r()
        self.assertEqual(code, 1)
        self.assertEqual(err, ["jira.json: `done[0]` (H-1): `labels` is not a list"])

    def test_an_inputs_json_not_in_utf8_is_unreadable(self):
        r = self.run_on([item("H-1")])
        bad = r.dir / "inputs.json"
        bad.write_bytes(b"\xff\xfe{}")
        code, out, err = r("--into", str(bad))
        self.assertEqual(code, 2)

    def test_no_counted_items_gives_no_weeks(self):
        r = self.run_on([item("H-1", resolution="Won't Do")])
        out = r.out()
        self.assertEqual(out["weeks"], [])
        self.assertEqual(out["counted"], 0)

    def test_into_sets_the_weeks_and_finished_epics_of_inputs_json_and_keeps_the_rest(self):
        r = self.run_on([item("H-1", parent="H-10", parent_done=True)])
        inputs = r.dir / "inputs.json"
        inputs.write_text(json.dumps({"throughput": {"from": "Jira: x, run 2026-11-19", "weeks": []},
                                      "finished_epics": [], "epics": {}, "ranges": {}, "start": "2026-11-23",
                                      "in_flight": 2}), encoding="utf-8")
        r.out("--into", str(inputs))
        data = json.loads(inputs.read_text(encoding="utf-8"))
        self.assertEqual(data["throughput"], {"from": "Jira: x, run 2026-11-19",
                                              "weeks": [{"week": "2026-11-09", "done": 1}]})
        self.assertEqual(data["finished_epics"], [{"key": "H-10", "stories": 1}])
        self.assertEqual((data["start"], data["in_flight"]), ("2026-11-23", 2))

    def test_a_malformed_item_is_named(self):
        r = self.run_on([item("H-1"), {"key": "H-2"}])
        code, out, err = r()
        self.assertEqual(code, 1)
        self.assertEqual(err, ["jira.json: `done[1]` (H-2) has no `fields`"])

    def test_a_missing_file_is_unreadable(self):
        p = subprocess.run([sys.executable, str(SCRIPT), "/nonexistent/jira.json", "--today", TODAY],
                           capture_output=True, text=True)
        self.assertEqual(p.returncode, 2)
        self.assertIn("/nonexistent/jira.json", p.stderr)

    def test_the_hall_fixture(self):
        """The Check fixture: 26 weeks to 2026-11-09, two won't-do items, one
        closed without work, two never in progress, one finished Epic."""
        p = subprocess.run([sys.executable, str(SCRIPT), str(FIXTURE), "--today", TODAY],
                           capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stderr)
        out = json.loads(p.stdout)
        self.assertEqual(out["window"], {"from": "2026-05-18", "to": "2026-11-09"})
        self.assertEqual(len(out["weeks"]), 26)
        self.assertEqual(out["counted"], 60)
        self.assertEqual(sum(w["done"] for w in out["weeks"]), 60)
        self.assertEqual([n["key"] for n in out["never_in_progress"]], ["HALL-41", "HALL-57"])
        self.assertEqual(sorted(x["key"] for x in out["left_out"]), ["HALL-33", "HALL-48", "HALL-63"])
        self.assertEqual(out["finished_epics"], [{"key": "HALL-2", "stories": 9}, {"key": "HALL-5", "stories": 11},
                                                 {"key": "HALL-8", "stories": 8}])


if __name__ == "__main__":
    unittest.main()
