import itertools
import json
import os
import shutil
import subprocess
import sys
import unittest

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(ROOT, "src"))
from agent_readiness import load_rubric, score  # noqa: E402

R = load_rubric()


def answers(opt):
    return {q["id"]: opt for q in R.questions}


class ScoringTests(unittest.TestCase):
    def test_weights_sum_to_100(self):
        self.assertEqual(sum(c["weight"] for c in R.categories), 100)

    def test_best_and_worst_answers(self):
        self.assertAlmostEqual(score(answers(0), R)["overall"], 100.0)
        self.assertAlmostEqual(score(answers(2), R)["overall"], 0.0)

    def test_every_question_has_best_option_first(self):
        for q in R.questions:
            scores = [o["score"] for o in q["options"]]
            self.assertEqual(scores, sorted(scores, reverse=True), q["id"])

    def test_improving_one_answer_never_lowers_score(self):
        base = answers(2)
        for q in R.questions:
            prev = score(base, R)["overall"]
            for opt in range(len(q["options"]) - 1, -1, -1):
                cur = dict(base)
                cur[q["id"]] = opt
                s = score(cur, R)["overall"]
                self.assertGreaterEqual(s + 1e-9, prev, (q["id"], opt))
                prev = s

    def test_score_stays_in_range_for_random_profiles(self):
        qids = [q["id"] for q in R.questions]
        sizes = [len(q["options"]) for q in R.questions]
        for combo in itertools.islice(itertools.product(*[range(n) for n in sizes]), 0, 20000, 7):
            s = score(dict(zip(qids, combo)), R)["overall"]
            self.assertTrue(0.0 <= s <= 100.0)

    def test_gaps_sorted_worst_first_and_only_for_flawed_answers(self):
        gaps = score(answers(2), R)["gaps"]
        self.assertEqual(len(gaps), 9)
        self.assertEqual([g["score"] for g in gaps], sorted(g["score"] for g in gaps))
        self.assertEqual(score(answers(0), R)["gaps"], [])

    def test_unanswered_questions_are_skipped(self):
        r = score({"q1": 0}, R)
        self.assertEqual(r["answered"], 1)

    def test_band_boundaries(self):
        self.assertEqual(R.band(80), "Agent-Ready")
        self.assertEqual(R.band(79.9), "Partially Ready")
        self.assertEqual(R.band(60), "Partially Ready")
        self.assertEqual(R.band(35), "Significant Gaps")
        self.assertEqual(R.band(34.9), "Not Agent-Ready")

    def test_bad_weights_rejected(self):
        data = json.load(open(os.path.join(ROOT, "rubric.json")))
        data["categories"][0]["weight"] += 5
        with self.assertRaises(ValueError):
            type(R)(data)


class ParityTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"), "node not installed")
    def test_rubric_json_matches_web_demo(self):
        out = subprocess.check_output(
            ["node", os.path.join(ROOT, "tools", "extract_rubric.js"), os.path.join(ROOT, "web", "index.html")])
        self.assertEqual(json.loads(out), json.load(open(os.path.join(ROOT, "rubric.json"))))


class CliTests(unittest.TestCase):
    def run_cli(self, profile):
        env = dict(os.environ, PYTHONPATH=os.path.join(ROOT, "src"))
        return subprocess.run([sys.executable, "-m", "agent_readiness", profile],
                              capture_output=True, text=True, env=env)

    def test_cli_scores_example_profile(self):
        p = os.path.join(ROOT, "eval", "profiles", "ideal.json")
        # profile files carry a metadata key; the CLI must reject unknown keys loudly
        r = self.run_cli(p)
        self.assertEqual(r.returncode, 2)
        self.assertIn("_expect_band", r.stderr)

    def test_cli_ok_on_clean_profile(self):
        tmp = os.path.join(ROOT, "tests", "_tmp_profile.json")
        json.dump({"q1": 0, "q2": 0}, open(tmp, "w"))
        try:
            r = self.run_cli(tmp)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("Overall:", r.stdout)
        finally:
            os.remove(tmp)


if __name__ == "__main__":
    unittest.main()
