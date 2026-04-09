# Strategy Thinking Frameworks

Last Updated: 2026-04-09

## What This Document Is For

Each framework here is a portable mental model — a named, reusable thinking tool that can be applied in different contexts to make better strategy decisions. They are not checklists. They are ways of framing a question so that the important considerations surface naturally.

Use these during strategy formation, during reviews, and when pushing back on a quality approach that does not feel right but is hard to articulate why.

---

## The Risk-First Filter

### The Question It Answers

Before writing a test: what risk does this test protect against?

### How To Use It

State the risk in plain language before writing the test or defining the scenario. A risk has three components:

- **What can go wrong** — the specific failure mode
- **Who is affected** — the user, the business, the system
- **What the consequence is** — transaction fails, data is corrupted, user is locked out, revenue is impacted

Examples of a risk clearly stated:
> "If the payment confirmation step is broken, a user who has been charged will not receive a confirmation, the order will not be created, and the transaction will need manual resolution."

> "If the session token is not invalidated on logout, an attacker who acquires the token can access the account after the legitimate user has logged out."

If you cannot state the risk with this specificity, you may be writing a test out of habit rather than out of a genuine quality need.

### Why It Matters

Most suites contain tests written because a feature was built, not because a risk was identified. The risk-first filter reverses this: start from what can go wrong, then design the test that would catch it. This produces tests with higher signal density than feature-first test design.

### Application in Strategy

Rank test scenarios by risk severity and likelihood. The highest-priority scenarios are those where: the impact of the failure is high AND the probability of the failure is non-trivial AND the failure is not already caught by another layer.

---

## The Automation Viability Check

### The Question It Answers

Is this scenario worth automating right now?

### How To Use It

Before writing automation for a scenario, verify four criteria:

| Criterion | Question |
|---|---|
| **Stable** | Will this behaviour still be the correct behaviour in three months? Is it likely to change with ongoing development? |
| **High-value** | Does this scenario protect a significant business risk, cover a critical path, or have consequences if it fails? |
| **Repeated** | Will this check need to run many times — on every commit, or multiple times per day — to provide value? |
| **Falsifiable** | Can the test produce a clear pass or fail signal? Is there a deterministic expected result that the automation can assert against? |

If the answer to any of these is no, automation is likely not the right tool for this scenario right now.

- **Unstable**: manual testing + revisit for automation when stable
- **Low-value**: deprioritise or remove from scope
- **Not repeated**: a one-time check does not benefit from the overhead of automation implementation
- **Not falsifiable**: exploratory testing or manual review is the right approach

### Why It Matters

Teams that automate first and ask these questions later accumulate automation debt: a growing suite of tests that were sensible to write at the time but now require maintenance without providing proportional value.

### Application in Strategy

Apply this check in sprint planning when estimating test automation stories. Apply it in retrospectives when reviewing the automation backlog. Use it to justify automation deprioritisation to stakeholders who expect everything to be automated.

---

## The Layer Before Climbing

### The Question It Answers

Before adding E2E or integration test coverage for a scenario: could a lower layer give the same confidence more cheaply?

### The Reasoning

Every testing layer has a cost — execution time, maintenance cost, environmental dependencies, flakiness risk. Higher layers (E2E, integration) have higher costs than lower layers (unit, component, API). For the same business risk, a test at a lower layer is strictly better if it can provide the same confidence.

### The Test Pyramid Applied

```
E2E / UI — highest cost, highest environmental dependency, slowest
  Integration / API — moderate cost, moderate environmental dependency
    Component — low cost, minimal environmental dependency
      Unit — lowest cost, no environmental dependency
```

Before adding a new E2E scenario, ask: is there a reason this cannot be covered at the API layer? Before adding an API test, ask: is there a reason this cannot be covered at the unit layer?

Reasons that justify the higher layer:
- The risk specifically involves the interaction between layers (the API layer cannot catch a rendering defect in the UI)
- The behaviour requires a real database or external service to be meaningful (some integration scenarios cannot be faked without losing the signal)
- The user journey itself is the unit of risk (a complete checkout flow cannot be meaningfully tested at the component level)

If none of these reasons apply, a lower layer is the correct choice.

### Anti-Pattern It Guards Against

[The UI Pyramid Inversion](STRATEGY-ANTI-PATTERNS.md#the-ui-pyramid-inversion) — building a suite that is disproportionately heavy at the top of the pyramid because that is where testing started.

---

## The Release Decision Check

### The Question It Answers

At release time: what questions does the current test report actually answer for the person making the release decision?

### How To Use It

Write down the questions that define release readiness. For example:

1. Are all critical business flows working?
2. Are there any performance regressions against the previous baseline?
3. Were there any high-severity defects found that are not closed?
4. Did the compliance and security checks pass?
5. Are there any known risks that have not been mitigated?

Now review the actual test outputs that exist. For each release readiness question, is there a specific, reliable test or check that produces a clear answer?

Where there is no answer — or where the answer is "sort of, but you have to look through these forty test results and make your own judgment" — that gap is the highest-priority improvement in the quality strategy.

### Why It Matters

Most teams have test reports that answer the questions nobody asked ("did 87% of our unit tests pass?") and do not answer the questions that matter ("did the checkout flow work end-to-end?"). The release decision check exposes this gap explicitly.

A quality gate should be a gate — a binary pass/fail condition that the release decision-maker can read in two minutes, not a detailed technical report that requires interpretation.

### Application in Strategy

Run this check quarterly. Each gap between a release readiness question and the available quality signal is a strategy improvement opportunity. Prioritise closing the gaps for the highest-risk questions first.

---

## The Shift-Left / Shift-Right Balance Check

### The Question It Answers

Is the quality strategy appropriately balanced between preventing defects before production (shift-left) and detecting defects in production (shift-right)?

### The Two Directions

**Shift-left:** Move quality activity earlier in the delivery cycle — closer to requirements, design, and development. The earlier a defect is caught, the cheaper it is to fix. This is the intuition behind unit tests, code review, static analysis, and early acceptance criteria definition.

**Shift-right:** Extend quality activity into production. Production is the only place where the real system is running under real load with real users and real data. Monitoring, alerting, synthetic probes, feature flags, and canary releases are shift-right quality mechanisms.

### The Balance Problem

Teams with a strong shift-left orientation sometimes assume that a thorough CI pipeline means production quality is assured. It does not. The CI pipeline tests what was predicted to fail. Production surfaces what was not predicted. The gap between these is closed by shift-right practices, not by more unit tests.

Teams with a strong shift-right orientation sometimes have weak pre-production quality gates. Defects reach production frequently, and the operating model is to detect and fix them quickly. This is appropriate for some product types (pre-revenue, internal tools) but inappropriate for others (financial transactions, health records, regulated products).

### How To Use It

For the system you are designing a strategy for, identify:

- What shift-left mechanisms exist? (unit tests, code review, SAST, early acceptance criteria)
- What shift-right mechanisms exist? (monitoring, alerting, synthetic probes, feature flags, production logging)
- Are there obvious gaps in either direction?

The balance point depends on the system type. High-reliability systems (financial, medical) require strong shift-left — defects must not reach production frequently. High-velocity consumer products may tolerate more shift-right, using feature flags and rapid rollback as quality mechanisms. Name the appropriate balance explicitly in the strategy.

---

## The Assumption Visibility Rule

### The Question It Answers

What assumptions is this strategy depending on, and are they visible?

### How To Use It

Every test strategy contains assumptions. Common assumptions:

- The requirements are complete and stable enough to automate against
- The test environments accurately represent production
- The test data is representative of real scenarios
- The performance SLAs are agreed and known
- The team has the skills and capacity to maintain the automation estate
- The third-party dependencies behave as documented

For each assumption, ask: what happens to the strategy if this assumption is wrong? Is this risk documented?

### Why It Matters

Strategies fail in predictable ways when their assumptions fail silently. An automation suite built on the assumption of stable requirements becomes a maintenance burden when requirements change. A performance testing strategy built on the assumption that staging is representative of production will produce misleading results if staging is under-resourced.

Making assumptions visible serves two purposes: it allows stakeholders to validate them (and sometimes provide information that changes them), and it creates a record that can be referenced when investigating why a quality approach did not work as expected.

### Application in Strategy

Include an explicit assumptions section in every strategy document. Review assumptions at retrospectives. When a strategy or test approach is not working as expected, check the assumptions log first — the most common root cause is a broken assumption that was never stated.

---

## Quick Reference

| Framework | Core Question | Best Applied When |
|---|---|---|
| Risk-First Filter | What risk does this test protect against? | Designing test scenarios |
| Automation Viability Check | Is this worth automating now? | Sprint planning; automation backlog |
| Layer Before Climbing | Could a lower layer give the same confidence? | Deciding between E2E and API/unit coverage |
| Release Decision Check | What questions does the test report answer? | Quality gate design; strategy reviews |
| Shift-Left / Shift-Right Balance | Is the strategy balanced across the delivery cycle? | Strategy formation; quarterly reviews |
| Assumption Visibility Rule | What is this strategy assuming, and is it visible? | Strategy documentation; any failure investigation |

---

## Comparison Tables

### Greenfield vs. Brownfield Strategy

| Dimension | Greenfield | Brownfield |
|---|---|---|
| Starting point | Blank slate — build the right foundations | Existing behaviour to protect |
| First priority | Foundations: unit → API → E2E, in that order | Regression confidence for the critical paths |
| Automation sequencing | Build from lower layers upward | Stabilise and triage before expanding |
| Risk of doing wrong | Building the wrong foundations; expensive to change later | Regression during change; existing customers affected |
| Definition of done | New features have proportionate test coverage at each layer | Existing tests are reliable; new features do not break the suite |

### Tight Timeline vs. Long Horizon

| Dimension | Tight Timeline | Long Horizon |
|---|---|---|
| Automation focus | Critical path only; defer everything else | Broad coverage; build proportionately |
| Manual testing role | High — fills the gap automation cannot | Decreasing over time as automation matures |
| Risk posture | Explicit tradeoffs, communicated to stakeholders | Invest in sustainability and layered depth |
| Key failure mode | Trying to build too much; finishing nothing | Over-investing early; neglecting coverage as the system grows |

### No Automation vs. Weak Automation vs. Mature Automation

| State | What It Needs |
|---|---|
| No automation | Foundations: layer ownership, tooling choice, first coverage areas |
| Automation exists but weak | Stabilise and simplify before scaling; triage unreliable tests |
| Automation mature | Optimise: governance, reporting, release quality, pyramid rebalancing |

### Deterministic vs. LLM-Assisted Strategy Generation (this repo)

| Dimension | Deterministic | LLM-Assisted |
|---|---|---|
| Input required | Structured YAML or normalised artifact bundle | Same — LLM receives the same bundle |
| Output quality | Rule-driven, consistent, predictable | Synthesis quality; more narrative depth |
| Failure mode | Cannot produce output outside the rule set | LLM unavailable or generates invalid output |
| Fallback | Terminates with exit code 1 or 2 | Falls back to deterministic renderer (exit code 3) |
| Best used when | High consistency requirement; no LLM available | Richer output required; LLM provider reachable |
