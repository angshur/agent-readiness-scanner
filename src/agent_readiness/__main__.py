import argparse
import json
import sys

from .scoring import load_rubric, score


def main(argv=None):
    p = argparse.ArgumentParser(prog="agent-readiness", description="Score a platform's agent-readiness.")
    p.add_argument("profile", help='JSON file: {"q1": 0, "q2": 1, ...} (option index per question)')
    p.add_argument("--json", action="store_true", help="print machine-readable output")
    args = p.parse_args(argv)
    with open(args.profile) as fh:
        answers = json.load(fh)
    rubric = load_rubric()
    unknown = [k for k in answers if k not in {q["id"] for q in rubric.questions}]
    if unknown:
        print("unknown question ids: %s" % ", ".join(unknown), file=sys.stderr)
        return 2
    result = score(answers, rubric)
    if args.json:
        print(json.dumps(result, indent=2))
        return 0
    print("Overall: %d/100 - %s" % (round(result["overall"]), result["band"]))
    for c in rubric.categories:
        print("  %-22s %3d/100" % (c["name"], round(result["categories"][c["id"]])))
    for g in result["gaps"][:5]:
        print("  gap: " + g["text"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
