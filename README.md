# Agent-Readiness Scanner

Score how ready a platform's API is for autonomous AI agents, the way a security grader scores a website. Nine questions, four weighted categories, a 0-100 score, a verdict and a ranked list of gaps.

- **Browser demo:** open `web/index.html` (no build, no server).
- **CLI:** `PYTHONPATH=src python3 -m agent_readiness profile.json`
- **One rubric:** `rubric.json` is extracted from the browser demo (`tools/extract_rubric.js`), and a test fails if the two drift apart.

## Why it exists
Agents fail on APIs for boring reasons: account-wide API keys, writes that are not safe to retry, no audit log, no sandbox. Teams find out after the build. This sizes the gap before.

## Rubric
| Category | Weight | Questions |
|---|---|---|
| Auth & Access | 25 | public API, auth model |
| Write Safety | 30 | write support, idempotency, reversibility |
| Observability | 25 | audit log via API, webhooks |
| Developer Experience | 20 | rate limits in headers, sandbox / MCP docs |

Verdicts: 80+ Agent-Ready, 60+ Partially Ready, 35+ Significant Gaps, below that Not Agent-Ready.

## Evaluation (see `eval/results.md`)
Run: `python3 eval/run_eval.py` (seeded and deterministic). Tests: `python3 -m unittest discover -s tests`.

| Check | Result |
|---|---|
| Unit and property tests | 12 pass: bounds, weights, exhaustive "improving an answer never lowers the score", band boundaries, web/CLI rubric parity |
| Calibration: 6 archetype profiles vs the band I wrote down before scoring | **5 of 6 match** |
| Robustness: category weights wrong by up to +/-10 points, 1,000 trials | band changes in 0.3% of profile-trials; ranking flips in 1.8% of pairs |

**The miss:** I expected `legacy_enterprise` to land in "Significant Gaps". It scored 28 (Not Agent-Ready), because four answers score zero and the rubric counts a missing control as a full loss. I kept the expectation as written rather than editing it to pass. Either the rubric is harsh on legacy platforms, or my expectation was generous. A second reviewer should decide.

## Limits
- Self-reported questionnaire. It does not call any API.
- Archetypes are mine, so calibration is not validation. The weights are a judgment, not measured. The robustness check shows verdicts are stable to wrong weights, not that the weights are right.
- "Read-only" platforms score zero on write questions that do not apply to them. Not applicable is not modeled yet.

## Next step
Label 15-20 real vendors from their public API documentation (each answer with a source link and date), have a second person label the same set, and report inter-rater agreement and the rubric's rank correlation with a human "ready / not ready" judgment.
