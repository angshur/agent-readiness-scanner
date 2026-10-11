"""Score how ready a platform's API is for autonomous AI agents.

The rubric (questions, option scores, category weights) lives in rubric.json and is
extracted from the web demo, so the CLI and the browser tool cannot drift apart.
"""
import json
import os

_DEFAULT_RUBRIC = os.path.join(os.path.dirname(__file__), "..", "..", "rubric.json")


class Rubric:
    def __init__(self, data):
        self.categories = data["categories"]
        self.bands = sorted(data["bands"], key=lambda b: -b["min"])
        self.questions = data["questions"]
        self._by_id = {q["id"]: q for q in self.questions}
        total = sum(c["weight"] for c in self.categories)
        if total != 100:
            raise ValueError("category weights must sum to 100, got %s" % total)

    def question(self, qid):
        return self._by_id[qid]

    def band(self, overall):
        for b in self.bands:
            if overall >= b["min"]:
                return b["label"]
        return self.bands[-1]["label"]


def load_rubric(path=None):
    with open(path or _DEFAULT_RUBRIC) as fh:
        return Rubric(json.load(fh))


def score(answers, rubric=None, weights=None):
    """answers: {question_id: option_index}. Unanswered questions are skipped.

    weights: optional {category_id: weight} override (used by the sensitivity eval).
    Returns overall (0-100 float), per-category scores, verdict band and gaps (worst first).
    """
    rubric = rubric or load_rubric()
    totals = {c["id"]: 0.0 for c in rubric.categories}
    counts = {c["id"]: 0 for c in rubric.categories}
    gaps = []
    for q in rubric.questions:
        idx = answers.get(q["id"])
        if idx is None:
            continue
        opt = q["options"][idx]
        totals[q["category"]] += opt["score"]
        counts[q["category"]] += 1
        if opt["gap"]:
            gaps.append({"question": q["id"], "score": opt["score"], "text": opt["gap"]})
    categories = {}
    overall = 0.0
    for c in rubric.categories:
        avg = totals[c["id"]] / (counts[c["id"]] or 1)
        categories[c["id"]] = avg
        w = (weights or {}).get(c["id"], c["weight"])
        overall += avg * (w / 100.0)
    gaps.sort(key=lambda g: g["score"])
    return {
        "overall": overall,
        "band": rubric.band(overall),
        "categories": categories,
        "gaps": gaps,
        "answered": sum(counts.values()),
    }
