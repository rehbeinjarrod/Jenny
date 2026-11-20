"""Tests for the forecast script, at its interface: `python3 forecast.py
<project dir> <plan dir>` over a Project's records and the plan's
`inputs.json`, writing `forecast.json` (exit 0), naming input problems
(exit 1) or naming what can't be read (exit 2).

The fixture Project, `fixture/projects/garden-club`, keeps a frozen
`plans/plan-v3/` with its `inputs.json` and the `forecast.json` the script
must reproduce byte for byte.

Run: python3 -m unittest discover -s acceptance/forecast
"""

import datetime
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills" / "plan" / "scripts" / "forecast.py"
FIXTURE = Path(__file__).resolve().parent / "fixture" / "projects" / "garden-club"
PLAN = "plans/plan-v3"
DATE_KEYS = ("likely_start", "likely_finish", "very_likely_finish")


def weeks(*done, first=datetime.date(2026, 6, 1)):
    return [{"week": (first + datetime.timedelta(weeks=i)).isoformat(), "done": d}
            for i, d in enumerate(done)]


class Project:
    """A copy of the fixture Project in a temporary folder."""

    def __init__(self, plan=PLAN):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name) / "garden-club"
        shutil.copytree(FIXTURE, self.root)
        self.plan = self.root / plan
        if plan != PLAN:
            shutil.copytree(self.root / PLAN, self.plan)
        for out in [self.plan / "forecast.json", *self.plan.glob("gantt*.mmd")]:
            out.unlink()

    def close(self):
        self._tmp.cleanup()

    def path(self, rel):
        return self.root / rel

    def edit(self, rel, old, new):
        p = self.path(rel)
        text = p.read_text(encoding="utf-8")
        assert old in text, (rel, old)
        p.write_text(text.replace(old, new, 1), encoding="utf-8")

    def write(self, rel, text):
        p = self.path(rel)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")

    def inputs(self):
        return json.loads((self.plan / "inputs.json").read_text(encoding="utf-8"))

    def set_inputs(self, data):
        (self.plan / "inputs.json").write_text(json.dumps(data, indent=2), encoding="utf-8")

    def change_inputs(self, change):
        data = self.inputs()
        change(data)
        self.set_inputs(data)

    def run(self):
        """(exit code, stderr lines, forecast.json text or None)."""
        p = subprocess.run([sys.executable, str(SCRIPT), str(self.root), str(self.plan)],
                           capture_output=True, text=True)
        out = self.plan / "forecast.json"
        return p.returncode, p.stderr.splitlines(), out.read_text(encoding="utf-8") if out.exists() else None

    def forecast(self):
        code, err, text = self.run()
        assert code == 0, err
        return json.loads(text)

    def charts(self):
        """{file name: text} for each Gantt the last run wrote."""
        return {p.name: p.read_text(encoding="utf-8") for p in sorted(self.plan.glob("gantt*.mmd"))}

    def check(self):
        """(exit code, stderr lines) of `forecast.py --check` on the plan."""
        p = subprocess.run([sys.executable, str(SCRIPT), "--check", str(self.plan)],
                           capture_output=True, text=True)
        return p.returncode, p.stderr.splitlines()


def epic_md(eid, feature, depends=(), enablers=(), covers=None, te_enables=None):
    head = "Code: GC\nEpic: %s\nFeature: %s\n" % (eid, feature)
    if te_enables:
        head += "Technical Enabler: yes\nEnables: %s\n" % te_enables
    body = "\n## Covers\n\n%s\n\n## Depends on\n\n%s\n" % (
        "- " + covers if covers else "None.",
        "\n".join("- %s (a dependency): must be built first." % d for d in depends) or "None.")
    if enablers:
        body += "\n## Enabler Stories\n\n" + "\n".join(enablers) + "\n"
    return "# %s · Epic %s\n\n%s%s\n## External items\n\nNone yet.\n" % (eid, eid[-3:], head, body)


def milestone_md(mid, members, target="none"):
    lines = "\n".join("- " + m for m in members) or "Not sliced yet."
    return ("# %s · Milestone %s\n\nCode: GC\nMilestone: %s\nOutcome: o\nSuccess metric: m\n"
            "Target: %s\nInternal: no\nSource: GC-SRC-001\n\n## Members\n\n%s\n" % (mid, mid[-3:], mid, target, lines))


class Mini(Project):
    """An empty Project of the given Epics and Milestones, with plan-v1
    inputs: constant Throughput of 2 a week, engineer ranges, k of 2."""

    def __init__(self, epics, milestones, ranges, done_per_week=2):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name) / "mini"
        self.plan = self.root / "plans" / "plan-v1"
        self.write("project.md", "# GC · Mini\n\nCode: GC\nSlug: mini\nName: Mini\n")
        self.plan.mkdir(parents=True)
        for eid, text in epics.items():
            self.write("epics/%s-e/epic.md" % eid, text)
        for mid, text in milestones.items():
            self.write("milestones/%s-m.md" % mid, text)
        self.set_inputs({
            "throughput": {"from": "typed", "weeks": weeks(*[done_per_week] * 12)},
            "finished_epics": [],
            "epics": {},
            "ranges": {e: {"low": n, "high": n} for e, n in ranges.items()},
            "start": "2026-11-23",
            "in_flight": 2,
        })


def by_id(forecast):
    return {**{e["epic"]: e for e in forecast["epics"]}, **{m["milestone"]: m for m in forecast["milestones"]}}


class Case(unittest.TestCase):
    def project(self, *args, cls=Project, **kw):
        p = cls(*args, **kw)
        self.addCleanup(p.close)
        return p


class Pinned(Case):
    def test_the_fixture_forecast_is_reproduced_byte_for_byte(self):
        code, err, text = self.project().run()
        self.assertEqual(code, 0, err)
        self.assertEqual(text, (FIXTURE / PLAN / "forecast.json").read_text(encoding="utf-8"))

    def test_the_fixture_gantt_is_reproduced_byte_for_byte(self):
        p = self.project()
        p.forecast()
        self.assertEqual(p.charts(), {"gantt.mmd": (FIXTURE / PLAN / "gantt.mmd").read_text(encoding="utf-8")})

    def test_the_same_seed_gives_byte_identical_output(self):
        a, b = self.project().run()[2], self.project().run()[2]
        self.assertIsNotNone(a)
        self.assertEqual(a, b)

    def test_the_seed_is_the_plan_version(self):
        f = self.project(plan="plans/plan-v7").forecast()
        self.assertEqual((f["seed"], f["trials"]), (7, 10000))


class Properties(Case):
    def variants(self):
        """The fixture, and versions of it with other seeds and inputs."""
        yield self.project().forecast()
        yield self.project(plan="plans/plan-v11").forecast()
        p = self.project()
        p.change_inputs(lambda d: (d["epics"].clear(), d["ranges"].clear(), d.update(in_flight=1)))
        yield p.forecast()
        p = self.project()
        p.change_inputs(lambda d: d.update(in_flight=3))
        yield p.forecast()

    def test_85_percent_is_never_before_50_percent(self):
        for f in self.variants():
            for row in f["epics"] + f["milestones"]:
                self.assertLessEqual(row["likely_finish"], row["very_likely_finish"], row)

    def test_an_epic_starts_no_later_than_it_finishes(self):
        for f in self.variants():
            for row in f["epics"]:
                self.assertLessEqual(row["likely_start"], row["likely_finish"], row)

    def test_a_milestone_finishes_no_earlier_than_its_latest_member(self):
        for f in self.variants():
            rows = by_id(f)
            for m in f["milestones"]:
                for key in ("likely_finish", "very_likely_finish"):
                    latest = max(rows[e][key] for e in m["members"])
                    self.assertGreaterEqual(m[key], latest, (m["milestone"], key))

    def test_more_stories_never_gives_an_earlier_date(self):
        base = by_id(self.project().forecast())
        changes = {
            "more open Stories on a handed-off Epic": lambda d: d["epics"]["GC-EPC-001"].update(open=12),
            "a higher engineer range": lambda d: d["ranges"]["GC-EPC-004"].update(low=8, high=14),
            "bigger finished Epics": lambda d: [f.update(stories=f["stories"] + 3) for f in d["finished_epics"]],
        }
        for what, change in changes.items():
            p = self.project()
            p.change_inputs(change)
            after = by_id(p.forecast())
            for rid, row in base.items():
                for key in DATE_KEYS[1:]:
                    self.assertGreaterEqual(after[rid][key], row[key], (what, rid, key))

    def test_dates_are_fridays(self):
        f = self.project().forecast()
        for row in f["epics"] + f["milestones"]:
            for key in DATE_KEYS:
                if row.get(key):
                    self.assertEqual(datetime.date.fromisoformat(row[key]).weekday(), 4, (row, key))


class Model(Case):
    def test_order_is_topological_then_milestone_then_id(self):
        f = self.project().forecast()
        # 004 is a Technical Enabler that 002 and 003 wait on; 001 is in
        # the first Milestone.
        self.assertEqual([e["epic"] for e in f["epics"]], ["GC-EPC-001", "GC-EPC-004", "GC-EPC-002", "GC-EPC-003"])

    def test_count_sources_are_named(self):
        rows = by_id(self.project().forecast())
        self.assertEqual({e: rows[e]["count_source"] for e in ("GC-EPC-001", "GC-EPC-002", "GC-EPC-004")},
                         {"GC-EPC-001": "stories", "GC-EPC-002": "history", "GC-EPC-004": "range"})
        self.assertEqual(rows["GC-EPC-001"]["counts_read"], "2026-11-17")

    def test_a_fully_done_epic_drops_out(self):
        p = self.project()
        p.change_inputs(lambda d: d["epics"]["GC-EPC-001"].update(open=0, done=8))
        row = by_id(p.forecast())["GC-EPC-001"]
        self.assertEqual((row["count_source"], row["likely_finish"], row["no_date"]), ("done", None, None))

    def test_milestone_target_and_share_meeting_it(self):
        m = by_id(self.project().forecast())["GC-MIL-002"]
        self.assertEqual(m["target"], "2027-01-22")
        self.assertTrue(0 < m["target_met_share"] < 1, m)
        self.assertIsNone(by_id(self.project().forecast())["GC-MIL-001"]["target_met_share"])

    def test_a_milestone_with_a_feature_not_sliced_yet_has_no_date(self):
        p = self.project()
        p.edit("milestones/GC-MIL-002-opening-day.md", "- GC-FEA-003 · Plot fees",
               "- GC-FEA-003 · Plot fees\n- GC-FEA-009 · Plot swaps")
        rows = by_id(p.forecast())
        self.assertEqual(rows["GC-MIL-002"]["no_date"], "member GC-FEA-009 has no Epic yet")
        self.assertIsNone(rows["GC-MIL-002"]["likely_finish"])
        self.assertIsNotNone(rows["GC-EPC-003"]["likely_finish"])

    def test_a_milestone_whose_members_are_all_done_has_nothing_to_forecast(self):
        p = self.project()
        p.change_inputs(lambda d: d["epics"]["GC-EPC-001"].update(open=0, done=8))
        m = by_id(p.forecast())["GC-MIL-001"]
        self.assertEqual((m["likely_finish"], m["target_met_share"], m["no_date"]), (None, None, None))

    def test_each_epic_names_the_epics_it_waits_on(self):
        rows = by_id(self.project().forecast())
        # 002 names 004, and covers GC-REQ-003, which 001's Enabler Story
        # enables; 003 names GC-REQ-003, which 002 covers, and covers a
        # Requirement the Technical Enabler 004 enables.
        self.assertEqual({e: rows[e]["depends_on"] for e in ("GC-EPC-001", "GC-EPC-002", "GC-EPC-003")},
                         {"GC-EPC-001": [], "GC-EPC-002": ["GC-EPC-001", "GC-EPC-004"],
                          "GC-EPC-003": ["GC-EPC-002", "GC-EPC-004"]})

    def test_a_target_names_who_set_it(self):
        rows = by_id(self.project().forecast())
        self.assertEqual(rows["GC-MIL-002"]["target_source"], "set by Ana Ruiz")
        self.assertIsNone(rows["GC-MIL-001"]["target_source"])

    def test_critical_path_follows_the_latest_finishing_chain(self):
        rows = by_id(self.project().forecast())
        for e in ("GC-EPC-004", "GC-EPC-002", "GC-EPC-003"):
            self.assertEqual(rows[e]["critical_share"], 1.0, e)
        self.assertEqual(rows["GC-EPC-001"]["critical_share"], 0.0)


class Gantt(Case):
    """The Mermaid Gantt beside `forecast.json`, and `--check`, which reads
    a plan folder's charts back against its `forecast.json`."""

    def test_check_passes_the_charts_as_written(self):
        p = self.project()
        p.forecast()
        self.assertEqual(p.check(), (0, []))

    def test_check_catches_a_bar_date_that_is_not_the_forecasts(self):
        p = self.project()
        p.forecast()
        p.edit("%s/gantt.mmd" % PLAN, "GC_EPC_002, 2026-12-18, 2027-01-01", "GC_EPC_002, 2026-12-18, 2027-01-08")
        code, err = p.check()
        self.assertEqual(code, 1, err)
        self.assertEqual(err, ["gantt.mmd:24: `GC_EPC_002` is likely 1 Jan, 2026-12-18 to 2027-01-08, tagged crit; "
                               "forecast.json calls for likely 1 Jan, 2026-12-18 to 2027-01-01, tagged crit"])

    def test_check_catches_a_missing_milestone_diamond_and_an_after(self):
        p = self.project()
        p.forecast()
        p.edit("%s/gantt.mmd" % PLAN, "    target 22 Jan :crit, milestone, GC_MIL_002_target, 2027-01-22, 0d\n", "")
        p.edit("%s/gantt.mmd" % PLAN, "GC_EPC_003, 2027-01-08,", "GC_EPC_003, after GC_EPC_002,")
        code, err = p.check()
        self.assertEqual(code, 1, err)
        self.assertTrue(any("`GC_MIL_002_target` from forecast.json has no bar" in l for l in err), err)
        self.assertTrue(any("explicit dates" in l for l in err), err)

    def test_check_catches_a_row_with_no_bar(self):
        p = self.project()
        p.forecast()
        p.edit("%s/gantt.mmd" % PLAN, "    section Plot fees\n", "    section Plot fees\n    section Plot swaps\n")
        self.assertEqual(p.check(), (1, ["gantt.mmd:26: a section with no bar"]))

    def test_check_catches_a_critical_epic_drawn_plain(self):
        p = self.project()
        p.forecast()
        p.edit("%s/gantt.mmd" % PLAN, ":crit, GC_EPC_004,", ":GC_EPC_004,")
        self.assertEqual(p.check()[0], 1)

    def test_undated_epics_and_milestones_get_no_row(self):
        p = self.project()
        p.change_inputs(lambda d: d.update(finished_epics=d["finished_epics"][:4]))
        p.forecast()
        chart = p.charts()["gantt.mmd"]
        for gone in ("Plot booking", "Plot fees", "Opening day"):
            self.assertNotIn(gone, chart)
        for kept in ("section Member sign-up", "section Payments platform (groundwork)",
                     "section ◆ Walking skeleton (members)"):
            self.assertIn(kept, chart)
        self.assertEqual(p.check(), (0, []))

    def test_a_target_on_the_very_likely_day_is_one_red_diamond(self):
        p = self.project()
        p.edit("milestones/GC-MIL-002-opening-day.md", "Target: 2027-01-22", "Target: 2027-01-29")
        p.forecast()
        chart = p.charts()["gantt.mmd"]
        self.assertIn("    target = by 29 Jan :crit, milestone, GC_MIL_002_target, 2027-01-29, 0d\n", chart)
        self.assertNotIn("GC_MIL_002_by", chart)

    def test_no_dated_epic_writes_no_chart(self):
        p = self.project()
        p.change_inputs(lambda d: d["throughput"].update(weeks=weeks(4, 4, 4)))
        p.forecast()
        self.assertEqual(p.charts(), {})

    def test_a_name_with_mermaid_punctuation_still_reads_back(self):
        p = self.project()
        p.edit("epics/GC-EPC-002-plot-booking/epic.md", "· Plot booking", "· Plot booking: #2; online")
        p.forecast()
        self.assertIn("    section Plot booking - no. 2, online\n", p.charts()["gantt.mmd"])
        self.assertEqual(p.check(), (0, []))

    def big(self, n):
        """n Epics, one Feature each, the first half in GC-MIL-001 and the
        rest in GC-MIL-002, each 2 Stories."""
        ids = ["GC-EPC-%03d" % i for i in range(1, n + 1)]
        epics = {e: epic_md(e, "GC-FEA-%03d" % i) for i, e in enumerate(ids, start=1)}
        half = n // 2
        mils = {"GC-MIL-001": milestone_md("GC-MIL-001", ["GC-FEA-%03d" % i for i in range(1, half + 1)]),
                "GC-MIL-002": milestone_md("GC-MIL-002", ["GC-FEA-%03d" % i for i in range(half + 1, n + 1)])}
        return self.project(epics, mils, {e: 2 for e in ids}, cls=Mini)

    def test_up_to_20_epics_is_one_chart(self):
        p = self.big(20)
        p.forecast()
        self.assertEqual(list(p.charts()), ["gantt.mmd"])

    def test_over_20_epics_is_a_chapter_per_milestone(self):
        p = self.big(22)
        p.forecast()
        charts = p.charts()
        self.assertEqual(list(charts), ["gantt-GC-MIL-001.mmd", "gantt-GC-MIL-002.mmd"])
        for mid, first, last in (("GC-MIL-001", 1, 11), ("GC-MIL-002", 12, 22)):
            chart = charts["gantt-%s.mmd" % mid]
            self.assertTrue(chart.startswith("---\ndisplayMode: compact\n"), mid)
            self.assertEqual(re.findall(r"section Epic (\d+)", chart),
                             ["%03d" % i for i in range(first, last + 1)], mid)
            self.assertEqual(re.findall(r"section ◆ (.+)", chart), ["Milestone %s" % mid[-3:]], mid)
        self.assertEqual(p.check(), (0, []))


class Enablers(Case):
    """Constant Throughput of 2 a week makes every trial alike. A has two
    Enabler Stories among 10; B has 4 Stories."""

    ENS = ["- **GC-ENS-001** Login · Enables: none · Depends on: none",
           "- **GC-ENS-002** Audit log · Enables: none · Depends on: none"]

    def mini(self, b_depends):
        return self.project({
            "GC-EPC-001": epic_md("GC-EPC-001", "GC-FEA-001", enablers=self.ENS),
            "GC-EPC-002": epic_md("GC-EPC-002", "GC-FEA-002", depends=[b_depends]),
        }, {}, {"GC-EPC-001": 10, "GC-EPC-002": 4}, cls=Mini)

    def test_a_dependency_on_an_enabler_story_waits_only_for_that_epics_enabler_stories(self):
        rows = by_id(self.mini("GC-ENS-002").forecast())
        # Week 1: A's two Enabler Stories. B starts week 2, sharing 1 a week.
        self.assertEqual(rows["GC-EPC-001"]["likely_start"], "2026-11-27")
        self.assertEqual(rows["GC-EPC-002"]["likely_start"], "2026-12-04")
        self.assertEqual(rows["GC-EPC-002"]["likely_finish"], "2026-12-25")
        self.assertEqual(rows["GC-EPC-001"]["likely_finish"], "2027-01-08")

    def test_a_dependency_on_the_epic_waits_for_all_of_it(self):
        rows = by_id(self.mini("GC-EPC-001").forecast())
        self.assertEqual(rows["GC-EPC-001"]["likely_finish"], "2026-12-25")
        self.assertEqual(rows["GC-EPC-002"]["likely_start"], "2027-01-01")
        self.assertEqual(rows["GC-EPC-002"]["likely_finish"], "2027-01-08")

    def test_an_enabler_story_enabling_another_epics_requirement_holds_that_epic(self):
        p = self.project({
            "GC-EPC-001": epic_md("GC-EPC-001", "GC-FEA-001", covers="GC-REQ-001", enablers=[
                "- **GC-ENS-001** Login · Enables: GC-REQ-002 · Depends on: none",
                "- **GC-ENS-002** Audit log · Enables: none · Depends on: none"]),
            "GC-EPC-002": epic_md("GC-EPC-002", "GC-FEA-002", covers="GC-REQ-002"),
        }, {}, {"GC-EPC-001": 10, "GC-EPC-002": 4}, cls=Mini)
        self.assertEqual(by_id(p.forecast())["GC-EPC-002"]["likely_start"], "2026-12-04")

    def test_a_handed_off_epic_with_its_enabler_stories_done_holds_nothing(self):
        p = self.mini("GC-ENS-002")
        p.change_inputs(lambda d: d["epics"].update({"GC-EPC-001": {"open": 8, "done": 2, "read": "2026-11-17"}}))
        rows = by_id(p.forecast())
        self.assertEqual(rows["GC-EPC-002"]["likely_start"], "2026-11-27")


class History(Case):
    def with_weeks(self, *done):
        p = self.project()
        p.change_inputs(lambda d: d["throughput"].update(weeks=weeks(*done)))
        return p.forecast()

    def test_under_5_weeks_gives_no_dates(self):
        f = self.with_weeks(4, 4, 4, 4)
        self.assertEqual((f["history"]["weeks"], f["history"]["status"]), (4, "too short"))
        for row in f["epics"] + f["milestones"]:
            self.assertIsNone(row["likely_finish"], row)
            self.assertTrue(row["no_date"], row)
        self.assertIn("under 5 weeks", f["epics"][0]["no_date"])

    def test_5_to_10_weeks_gives_early_dates(self):
        for n in (5, 10):
            f = self.with_weeks(*[4] * n)
            self.assertEqual(f["history"]["status"], "early", n)
            for row in f["epics"]:
                self.assertTrue(row["early"], (n, row))
                self.assertIsNotNone(row["likely_finish"], (n, row))

    def test_11_weeks_or_more_is_normal(self):
        f = self.with_weeks(*[4] * 11)
        self.assertEqual(f["history"]["status"], "normal")
        self.assertFalse(any(row["early"] for row in f["epics"]))

    def test_only_the_last_26_weeks_count(self):
        # 4 old weeks of nothing, then 26 of 4: the zeros fall outside.
        f = self.with_weeks(*([0] * 4 + [4] * 26))
        self.assertEqual(f["history"]["weeks"], 26)
        g = self.with_weeks(*[4] * 26)
        self.assertEqual([e["likely_finish"] for e in f["epics"]], [e["likely_finish"] for e in g["epics"]])

    def test_a_missing_calendar_week_finished_no_stories(self):
        p = self.project()
        rows = weeks(*[4] * 11)
        del rows[5]
        p.change_inputs(lambda d: d["throughput"].update(weeks=rows))
        f = p.forecast()
        self.assertEqual((f["history"]["weeks"], f["history"]["status"]), (11, "normal"))
        g = self.with_weeks(*([4] * 5 + [0] + [4] * 5))
        self.assertEqual(f["epics"], g["epics"])

    def test_weeks_are_calendar_weeks(self):
        # Any day names its week: Wednesdays read the same as Mondays.
        p = self.project()
        p.change_inputs(lambda d: d["throughput"].update(
            weeks=weeks(*[4] * 11, first=datetime.date(2026, 6, 3))))
        self.assertEqual(p.forecast()["epics"], self.with_weeks(*[4] * 11)["epics"])

    def test_no_stories_in_the_window_gives_no_dates(self):
        f = self.with_weeks(*[0] * 12)
        self.assertTrue(all(row["no_date"] for row in f["epics"]))

    def test_too_few_finished_epics_and_no_range_leaves_that_epic_and_downstream_undated(self):
        p = self.project()
        p.change_inputs(lambda d: (d.update(finished_epics=d["finished_epics"][:4]),
                                   d["ranges"].update({"GC-EPC-003": {"low": 2, "high": 4}})))
        rows = by_id(p.forecast())
        self.assertEqual(rows["GC-EPC-002"]["count_source"], "none")
        self.assertIn("fewer than 5 finished Epics and no engineer range", rows["GC-EPC-002"]["no_date"])
        self.assertIn("waits on GC-EPC-002", rows["GC-EPC-003"]["no_date"])
        self.assertIsNone(rows["GC-EPC-003"]["likely_finish"])
        self.assertIn("GC-EPC-002", rows["GC-MIL-002"]["no_date"])
        for dated in ("GC-EPC-001", "GC-EPC-004", "GC-MIL-001"):
            self.assertIsNotNone(rows[dated]["likely_finish"], dated)

    def test_five_finished_epics_are_enough_to_resample(self):
        rows = by_id(self.project().forecast())
        self.assertEqual(rows["GC-EPC-002"]["count_source"], "history")

    def test_an_engineer_range_dates_an_epic_without_history(self):
        p = self.project()
        p.change_inputs(lambda d: (d.update(finished_epics=[]),
                                   d["ranges"].update({"GC-EPC-002": {"low": 3, "high": 6},
                                                       "GC-EPC-003": {"low": 2, "high": 4}})))
        rows = by_id(p.forecast())
        self.assertTrue(all(rows[e]["likely_finish"] for e in ("GC-EPC-002", "GC-EPC-003", "GC-MIL-002")))


MIL1 = "milestones/GC-MIL-001-walking-skeleton-members.md"


class DerivedTarget(Case):
    """A `derived from plan-v<N>` target is the very likely date that frozen
    Plan version gave the Milestone."""

    def test_a_derived_target_is_the_named_plans_very_likely_date(self):
        p = self.project(plan="plans/plan-v4")
        p.edit(MIL1, "Target: none", "Target: derived from plan-v3")
        m = by_id(p.forecast())["GC-MIL-001"]
        frozen = by_id(json.loads((FIXTURE / PLAN / "forecast.json").read_text(encoding="utf-8")))["GC-MIL-001"]
        self.assertEqual((m["target"], m["target_source"]), (frozen["very_likely_finish"], "derived from plan-v3"))
        self.assertTrue(0 <= m["target_met_share"] <= 1, m)

    def test_a_derived_target_from_a_plan_that_is_not_there_is_named(self):
        p = self.project(plan="plans/plan-v4")
        p.edit(MIL1, "Target: none", "Target: derived from plan-v9")
        code, err, text = p.run()
        self.assertEqual(code, 1, err)
        self.assertIsNone(text)
        self.assertIn("%s: `Target: derived from plan-v9`: there is no plans/plan-v9/forecast.json"
                      % (p.path(MIL1)), err)

    def test_a_derived_target_from_a_plan_with_no_date_for_it_is_named(self):
        p = self.project(plan="plans/plan-v4")
        frozen = json.loads((p.root / PLAN / "forecast.json").read_text(encoding="utf-8"))
        for m in frozen["milestones"]:
            m.update(likely_finish=None, very_likely_finish=None)
        (p.root / PLAN / "forecast.json").write_text(json.dumps(frozen), encoding="utf-8")
        p.edit(MIL1, "Target: none", "Target: derived from plan-v3")
        code, err, _ = p.run()
        self.assertEqual(code, 1, err)
        self.assertIn("%s: `Target: derived from plan-v3`: plan-v3 gives `GC-MIL-001` no very likely date"
                      % (p.path(MIL1)), err)


class InputProblems(Case):
    def assertProblem(self, p, *fragments):
        code, err, text = p.run()
        self.assertEqual(code, 1, err)
        self.assertIsNone(text, "nothing is written on exit 1")
        for frag in fragments:
            self.assertTrue(any(frag in line for line in err), (frag, err))
        return err

    def test_a_cycle_is_named(self):
        p = self.project()
        p.edit("epics/GC-EPC-004-payments-platform/epic.md", "## Depends on\n\nNone.",
               "## Depends on\n\n- GC-EPC-003 (Plot fees): must be built first.")
        self.assertProblem(p, "a cycle in `Depends on`: ", "GC-EPC-003", "GC-EPC-004")

    def test_an_unknown_epic_in_depends_on_is_named(self):
        p = self.project()
        p.edit("epics/GC-EPC-002-plot-booking/epic.md", "- GC-EPC-004 (", "- GC-EPC-009 (")
        self.assertProblem(p, "`Depends on`: `GC-EPC-009` is not an Epic in the Project")

    def test_an_unknown_enabler_story_is_named(self):
        p = self.project()
        p.edit("epics/GC-EPC-001-member-sign-up/epic.md", "Depends on: none", "Depends on: GC-ENS-007")
        self.assertProblem(p, "`GC-ENS-007` is not an Enabler Story in the Project")

    def test_a_requirement_no_epic_covers_is_named(self):
        p = self.project()
        p.edit("epics/GC-EPC-003-plot-fees/epic.md", "- GC-REQ-003 (", "- GC-REQ-042 (")
        self.assertProblem(p, "no Epic covers `GC-REQ-042`")

    def test_a_milestone_with_no_members_is_named(self):
        p = self.project()
        p.edit("milestones/GC-MIL-001-walking-skeleton-members.md", "- GC-FEA-001 · Member sign-up", "Not sliced yet.")
        self.assertProblem(p, "`GC-MIL-001` has no members")


    def test_malformed_inputs_are_named_one_per_line(self):
        p = self.project()
        p.change_inputs(lambda d: (d.pop("start"), d["epics"]["GC-EPC-001"].update(open=-1),
                                   d["ranges"].update({"GC-EPC-004": {"low": 9, "high": 5}}),
                                   d["throughput"]["weeks"].append({"week": "June", "done": 3}),
                                   d.update(in_flight=0, extra=1)))
        err = self.assertProblem(p, "inputs.json: `start`", "inputs.json: `epics.GC-EPC-001`",
                                 "inputs.json: `ranges.GC-EPC-004`", "inputs.json: `throughput.weeks[16]`",
                                 "inputs.json: `in_flight`", "inputs.json: `extra` is not a known key")
        self.assertEqual(len(err), 6, err)

    def test_two_rows_in_one_calendar_week_are_named(self):
        p = self.project()
        p.change_inputs(lambda d: d["throughput"]["weeks"].append({"week": "2026-06-04", "done": 1}))
        self.assertProblem(p, "the week of 2026-06-04 is also `throughput.weeks[0]`")

    def test_inputs_that_are_not_json_are_named(self):
        p = self.project()
        (p.plan / "inputs.json").write_text("{not json", encoding="utf-8")
        self.assertProblem(p, "inputs.json: not valid JSON")

    def test_an_epic_in_inputs_that_is_not_in_the_project_is_named(self):
        p = self.project()
        p.change_inputs(lambda d: d["ranges"].update({"GC-EPC-099": {"low": 1, "high": 2}}))
        self.assertProblem(p, "inputs.json: `ranges`: `GC-EPC-099` is not an Epic in the Project")

    def test_a_plan_folder_not_named_by_version_is_named(self):
        p = self.project(plan="plans/latest")
        self.assertProblem(p, "not named plan-v<N>")


class Unreadable(Case):
    def assertUnreadable(self, p, fragment, args=None):
        cmd = [sys.executable, str(SCRIPT)] + (args or [str(p.root), str(p.plan)])
        r = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn(fragment, r.stderr)
        self.assertFalse((p.plan / "forecast.json").exists())

    def test_no_inputs_file(self):
        p = self.project()
        (p.plan / "inputs.json").unlink()
        self.assertUnreadable(p, "inputs.json: no such file")

    def test_no_project_folder(self):
        p = self.project()
        self.assertUnreadable(p, "no such Project folder", [str(p.root / "nope"), str(p.plan)])

    def test_a_record_that_is_not_utf8(self):
        p = self.project()
        p.path("epics/GC-EPC-002-plot-booking/epic.md").write_bytes(b"# GC-EPC-002 \xff\xfe\n")
        self.assertUnreadable(p, "not UTF-8 text")


if __name__ == "__main__":
    unittest.main()
