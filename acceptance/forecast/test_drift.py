"""Tests for the drift script, at its interface: `python3 drift.py
<project dir> <plan dir>` compares a Plan folder with the latest earlier
Plan version whose `plan.md` has a `Shown:` line, prints the date moves and
input differences (exit 0), and writes nothing; exit 2 names what can't be
read.

Each test copies the forecast fixture Project, marks its frozen `plan-v3`
shown, and makes a `plan-v4` beside it with the forecast script.

Run: python3 -m unittest discover -s acceptance/forecast
"""

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "skills" / "plan" / "scripts"
FIXTURE = Path(__file__).resolve().parent / "fixture" / "projects" / "garden-club"
RECORD = "# GC · plan-v%d: Garden club\n\nCode: GC\nPlan: plan-v%d\nMade: 2026-11-17\n"
SHOWN = "Shown: 2026-11-20 to Ana Ruiz\n"


def percent(share):
    return "%d%%" % round(share * 100)


class Plans:
    """A copy of the fixture Project, its plan-v3 shown to Ana Ruiz."""

    def __init__(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name) / "garden-club"
        shutil.copytree(FIXTURE, self.root)
        self.record(3, SHOWN)

    def close(self):
        self._tmp.cleanup()

    def folder(self, n):
        return self.root / "plans" / ("plan-v%d" % n)

    def record(self, n, *shown):
        self.folder(n).mkdir(parents=True, exist_ok=True)
        (self.folder(n) / "plan.md").write_text(RECORD % (n, n) + "".join(shown), encoding="utf-8")

    def edit(self, rel, old, new):
        p = self.root / rel
        text = p.read_text(encoding="utf-8")
        assert old in text, (rel, old)
        p.write_text(text.replace(old, new, 1), encoding="utf-8")

    def make(self, n, change=lambda d: None):
        """plan-v<n> from plan-v3's inputs, changed by `change`, forecast."""
        inputs = json.loads((self.folder(3) / "inputs.json").read_text(encoding="utf-8"))
        change(inputs)
        self.folder(n).mkdir(parents=True, exist_ok=True)
        (self.folder(n) / "inputs.json").write_text(json.dumps(inputs, indent=2), encoding="utf-8")
        p = subprocess.run([sys.executable, str(SCRIPTS / "forecast.py"), str(self.root), str(self.folder(n))],
                           capture_output=True, text=True)
        assert p.returncode == 0, p.stderr
        return self.forecast(n)

    def forecast(self, n):
        return json.loads((self.folder(n) / "forecast.json").read_text(encoding="utf-8"))

    def drift(self, n):
        """(exit code, stdout lines, stderr)."""
        p = subprocess.run([sys.executable, str(SCRIPTS / "drift.py"), str(self.root), str(self.folder(n))],
                           capture_output=True, text=True)
        return p.returncode, p.stdout.splitlines(), p.stderr

    def tree(self):
        return {str(p.relative_to(self.root)): p.read_bytes() for p in sorted(self.root.rglob("*")) if p.is_file()}


def rows(forecast):
    return {**{e["epic"]: e for e in forecast["epics"]}, **{m["milestone"]: m for m in forecast["milestones"]}}


class Case(unittest.TestCase):
    def setUp(self):
        self.plans = Plans()
        self.addCleanup(self.plans.close)

    def ok(self, n):
        code, out, err = self.plans.drift(n)
        self.assertEqual(code, 0, err)
        return out


class Against(Case):
    def test_measured_against_the_shown_version_and_who_saw_it(self):
        self.plans.make(4)
        self.assertEqual(self.ok(4)[0], "Drift from plan-v3 (shown 2026-11-20 to Ana Ruiz) to plan-v4")

    def test_the_latest_shown_version_wins_and_its_latest_shown_line(self):
        shutil.copytree(self.plans.folder(3), self.plans.folder(2))
        self.plans.record(3, SHOWN, "Shown: 2026-11-27 to the committee\n")
        self.plans.make(5)
        self.assertEqual(self.ok(5)[0], "Drift from plan-v3 (shown 2026-11-27 to the committee) to plan-v5")

    def test_a_version_never_shown_is_passed_over(self):
        shutil.copytree(self.plans.folder(3), self.plans.folder(2))
        self.plans.record(3)
        self.plans.make(4)
        self.assertEqual(self.ok(4)[0], "Drift from plan-v2 (shown 2026-11-20 to Ana Ruiz) to plan-v4")

    def test_none_shown_says_so(self):
        self.plans.record(3)
        self.plans.make(4)
        self.assertEqual(self.ok(4), ["No Plan version before plan-v4 has a `Shown:` line, "
                                      "so there is nothing to measure drift against."])

    def test_a_version_after_the_one_compared_is_not_used(self):
        self.plans.make(4)
        self.plans.record(4, SHOWN)
        self.assertEqual(self.ok(4)[0], "Drift from plan-v3 (shown 2026-11-20 to Ana Ruiz) to plan-v4")

    def test_it_writes_nothing(self):
        self.plans.make(4, lambda d: d.update(start="2026-11-30"))
        before = self.plans.tree()
        self.ok(4)
        self.assertEqual(self.plans.tree(), before)


class Moves(Case):
    def test_each_moved_date_is_named_old_to_new(self):
        old = rows(self.plans.forecast(3))
        new = rows(self.plans.make(4, lambda d: d["epics"]["GC-EPC-001"].update(open=12)))
        out = self.ok(4)
        moved = 0
        for rid, row in new.items():
            for key, word in (("likely_finish", "likely"), ("very_likely_finish", "very likely")):
                if row[key] != old[rid][key]:
                    moved += 1
                    line = next(l for l in out if l.startswith("- `%s`" % rid))
                    self.assertIn("%s %s → %s" % (word, old[rid][key], row[key]), line)
        self.assertGreater(moved, 0, "the change moves some dates")

    def test_a_milestones_chance_of_meeting_its_target_is_named(self):
        old = rows(self.plans.forecast(3))["GC-MIL-002"]
        new = rows(self.plans.make(4, lambda d: d["epics"]["GC-EPC-001"].update(open=12)))["GC-MIL-002"]
        self.assertNotEqual(old["target_met_share"], new["target_met_share"])
        line = next(l for l in self.ok(4) if l.startswith("- `GC-MIL-002`"))
        self.assertIn("chance of meeting the target %s → %s"
                      % (percent(old["target_met_share"]), percent(new["target_met_share"])), line)

    def test_unmoved_rows_are_listed_once(self):
        self.plans.make(4)
        out = self.ok(4)
        unmoved = [r for r, row in rows(self.plans.forecast(4)).items()
                   if row == rows(self.plans.forecast(3))[r] or all(
                       row.get(k) == rows(self.plans.forecast(3))[r].get(k)
                       for k in ("likely_finish", "very_likely_finish", "target_met_share"))]
        self.assertTrue(unmoved)
        line = " ".join(l for l in out if l.startswith("- No move: "))
        for r in unmoved:
            self.assertIn("`%s`" % r, line)

    def test_an_epic_that_lost_its_date_says_why(self):
        def drop(d):
            d["epics"].clear()
            d["ranges"].clear()
            d["finished_epics"] = d["finished_epics"][:2]
        new = rows(self.plans.make(4, drop))
        line = next(l for l in self.ok(4) if l.startswith("- `GC-EPC-004`"))
        self.assertIn("→ no date (%s)" % new["GC-EPC-004"]["no_date"], line)

    def test_an_epic_new_since_the_shown_version(self):
        shutil.copytree(self.plans.root / "epics/GC-EPC-003-plot-fees", self.plans.root / "epics/GC-EPC-005-plot-swaps")
        self.plans.edit("epics/GC-EPC-005-plot-swaps/epic.md", "GC-EPC-003 · Plot fees", "GC-EPC-005 · Plot swaps")
        self.plans.edit("epics/GC-EPC-005-plot-swaps/epic.md", "Epic: GC-EPC-003", "Epic: GC-EPC-005")
        self.plans.edit("epics/GC-EPC-005-plot-swaps/epic.md", "- GC-REQ-005", "None.")
        new = rows(self.plans.make(4))["GC-EPC-005"]
        line = next(l for l in self.ok(4) if l.startswith("- `GC-EPC-005`"))
        self.assertEqual(line, "- `GC-EPC-005` Plot swaps: new since plan-v3, likely %s, very likely %s"
                         % (new["likely_finish"], new["very_likely_finish"]))


    def test_a_row_undated_in_both_whose_reason_changed(self):
        def undated(d):
            d["epics"].clear(); d["ranges"].clear(); d["finished_epics"] = d["finished_epics"][:2]
        old = rows(self.plans.make(4, undated))["GC-EPC-004"]
        self.plans.record(4, SHOWN)
        new = rows(self.plans.make(5, lambda d: (undated(d), d["throughput"].update(weeks=d["throughput"]["weeks"][:3]))))
        new = new["GC-EPC-004"]
        self.assertNotEqual(old["no_date"], new["no_date"])
        line = next(l for l in self.ok(5) if l.startswith("- `GC-EPC-004`"))
        self.assertIn("no date (%s) → no date (%s)" % (old["no_date"], new["no_date"]), line)

    def test_a_target_newly_set_shows_its_chance(self):
        self.plans.edit("milestones/GC-MIL-001-walking-skeleton-members.md", "Target: none",
                        "Target: 2027-01-08 set by Ana Ruiz")
        new = rows(self.plans.make(4))["GC-MIL-001"]
        line = next(l for l in self.ok(4) if l.startswith("- `GC-MIL-001`"))
        self.assertIn("chance of meeting the target no target → %s" % percent(new["target_met_share"]), line)


class Inputs(Case):
    def inputs(self, n=4):
        out = self.ok(n)
        return out[out.index("## Inputs") + 1:]

    def test_nothing_changed(self):
        shutil.copytree(self.plans.folder(3), self.plans.folder(4))
        (self.plans.folder(4) / "plan.md").unlink()
        self.assertEqual(self.inputs(), ["- No input changed."])

    def test_throughput_weeks_added_and_changed(self):
        def change(d):
            d["throughput"]["weeks"][-1]["done"] = 1
            d["throughput"]["weeks"].append({"week": "2026-09-21", "done": 4})
            d["throughput"]["from"] = "typed by Sam, 2026-11-24"
        self.plans.make(4, change)
        got = self.inputs()
        self.assertIn("- Throughput: 16 → 17 weeks of history (normal → normal); added 2026-09-21: 4; "
                      "changed 2026-09-14: 5 → 1", got)
        self.assertIn("- Throughput from: Jira: project = GARD AND statusCategory = Done, run 2026-11-17 → "
                      "typed by Sam, 2026-11-24", got)

    def test_story_counts_ranges_start_and_in_flight(self):
        def change(d):
            d["epics"]["GC-EPC-001"].update(open=3, done=5, read="2026-11-24")
            d["ranges"]["GC-EPC-004"].update(low=6, high=10)
            d["ranges"]["GC-EPC-003"] = {"low": 2, "high": 4}
            d.update(start="2026-11-30", in_flight=3)
            d["finished_epics"].append({"key": "GARD-6", "stories": 5})
        self.plans.make(4, change)
        got = self.inputs()
        for line in ("- `GC-EPC-001` Story counts: 6 open, 2 done, read 2026-11-17 → 3 open, 5 done, read 2026-11-24",
                     "- `GC-EPC-004` range: 5 to 9 → 6 to 10",
                     "- `GC-EPC-003` range: none → 2 to 4",
                     "- Finished Epics: 5 → 6",
                     "- Start: 2026-11-23 → 2026-11-30",
                     "- In flight: 2 → 3"):
            self.assertIn(line, got)

    def test_depends_on_and_milestone_members(self):
        self.plans.edit("epics/GC-EPC-003-plot-fees/epic.md",
                        "- GC-REQ-003 (Members book a plot): must be built before this Epic can work.",
                        "- GC-EPC-001 (Member sign-up): must be built before this Epic can work.")
        self.plans.edit("milestones/GC-MIL-001-walking-skeleton-members.md", "- GC-FEA-001 · Member sign-up",
                        "- GC-FEA-001 · Member sign-up\n- GC-FEA-002 · Plot booking")
        self.plans.make(4)
        got = self.inputs()
        self.assertIn("- `GC-EPC-003` Depends on: adds `GC-EPC-001`; drops `GC-EPC-002`", got)
        # GC-FEA-002 holds Plot booking and the Payments platform it needs.
        self.assertIn("- `GC-MIL-001` members: adds `GC-EPC-002`, `GC-EPC-004`", got)

    def test_a_milestone_target(self):
        self.plans.edit("milestones/GC-MIL-002-opening-day.md", "Target: 2027-01-22 set by Ana Ruiz",
                        "Target: 2027-02-05 set by Ana Ruiz")
        self.plans.make(4)
        self.assertIn("- `GC-MIL-002` target: 2027-01-22 set by Ana Ruiz → 2027-02-05 set by Ana Ruiz",
                      self.inputs())


    def test_a_shown_version_from_before_target_sources_names_no_false_target_move(self):
        old = json.loads((self.plans.folder(3) / "forecast.json").read_text(encoding="utf-8"))
        for m in old["milestones"]:
            m.pop("target_source")
        (self.plans.folder(3) / "forecast.json").write_text(json.dumps(old), encoding="utf-8")
        self.plans.make(4)
        self.assertFalse([l for l in self.inputs() if "target:" in l], self.inputs())


class Unreadable(Case):
    def test_no_forecast_in_the_plan_folder(self):
        self.plans.folder(4).mkdir()
        code, out, err = self.plans.drift(4)
        self.assertEqual((code, out), (2, []))
        self.assertIn("forecast.json", err)

    def test_a_plan_folder_not_named_by_version(self):
        shutil.copytree(self.plans.folder(3), self.plans.root / "plans" / "latest")
        p = subprocess.run([sys.executable, str(SCRIPTS / "drift.py"), str(self.plans.root),
                            str(self.plans.root / "plans" / "latest")], capture_output=True, text=True)
        self.assertEqual(p.returncode, 2)
        self.assertIn("plan-v<N>", p.stderr)


if __name__ == "__main__":
    unittest.main()
