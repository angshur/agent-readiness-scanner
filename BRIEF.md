# Product brief: Agent-Readiness Scanner
**Owner:** Angshuman Rudra · **Status:** v1 shipped (browser + CLI), validation pending

**Problem.** Teams build agent integrations against vendor APIs and discover blockers late: coarse auth, unsafe retries, no audit trail. There is no quick way to size the gap before committing.

**User.** PMs, engineering leads and agent builders doing vendor due diligence on a marketing or sales platform.

**Decision it supports.** Build now, build with workarounds, or wait for the vendor to close specific gaps.

**What v1 does.** Nine questions across Auth, Write Safety, Observability and Developer Experience; a 0-100 score; a verdict; a ranked gap list; a shareable summary.

**Success measures.** (1) A second reviewer reaches the same verdict on 15+ real vendors at least 80% of the time. (2) A builder can name the top blocker from the report without reading the docs. (3) Verdicts survive weight changes (measured: 98%+ stable).

**Out of scope.** Live API probing, accounts, history, PDF export, vendor comparison.

**Risks.** Self-report is only as good as the person answering. Weights are unvalidated. "Not applicable" answers are penalized.

**Open decisions.** Model "not applicable" explicitly? Weight write safety higher for destructive-capable platforms?
