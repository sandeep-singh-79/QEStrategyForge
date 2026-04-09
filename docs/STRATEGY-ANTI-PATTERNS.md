# Strategy Anti-Patterns

Last Updated: 2026-04-09

## What This Document Is For

Each entry is a named, recognisable mistake in test strategy — a pattern that appears sensible, is widely adopted, and consistently produces worse outcomes than a better alternative. The format is: what it looks like, why teams fall into it, what the actual harm is, and what to do instead.

These are not theoretical mistakes. Every one of these patterns is common in real teams and real organisations. Recognising them by name is the first step to avoiding them — and to having a productive conversation about them with stakeholders who may not see the problem.

---

## The Coverage Number Trap

### What It Looks Like

The team's quality progress is reported in terms of number of tests, percentage code coverage, or number of test cases in a test management tool. Stakeholders ask "how many tests do we have?" or "what is our code coverage?" as quality gates. Activity metrics are treated as quality outcomes.

### Why Teams Fall Into It

Test count and code coverage are easy to measure and easy to report. They produce a visible number that appears to answer the question "are we testing enough?" They also respond to management pressure — if a manager asks for more tests, the team can write more tests and show the number going up.

### The Actual Harm

A test suite of a thousand tests that covers the wrong behaviour provides less real protection than fifty tests that cover the actual business risks. A 95% code coverage figure tells you that 95% of lines were executed during tests; it tells you nothing about whether those tests would detect a defect in the business logic, or whether the remaining 5% contains a critical path.

Teams optimising for the number build large suites with low signal density. When defects escape, the large number becomes an embarrassment rather than a defence. The real measure of a test suite's quality is defect escape rate, release confidence, and how often the suite catches real regressions — none of which are visible in test count.

### What To Do Instead

Measure risk coverage, not line coverage. For each critical business flow, name the risk that the test suite is protecting against. Review the test strategy regularly against the actual defects found in production — they are a map to what the suite is missing. When asked "how many tests do we have?", redirect the conversation to "what are we protected against, and what are we not?"

---

## The Automation First Fallacy

### What It Looks Like

The team writes automation for a newly developed feature before that feature is stable. Requirements are still changing. The feature is being refactored. The acceptance criteria are not finalised. The team writes the automation anyway, because "we should automate as we go."

### Why Teams Fall Into It

Automation-as-you-go is a sound principle when applied correctly. Teams learn it as a general rule and apply it universally, without distinguishing between features that are ready to automate and features that are not.

### The Actual Harm

Automation written against unstable requirements is maintenance debt, not investment. Every time the feature changes, the automation must be updated. The team spends capacity maintaining automation instead of building coverage for stable, high-value behaviours. The maintenance burden compounds until the automation suite is perceived as a liability rather than an asset.

A subtler harm: the team builds false confidence in coverage of a feature that the automation no longer correctly describes, because the maintenance has fallen behind the feature changes.

### What To Do Instead

Apply the automation viability check before writing automation for any feature: is this behaviour stable? Is it agreed? Is it high-value? Is it falsifiable? If the feature is in active development with changing requirements, manual testing is the correct approach until it stabilises. Automation is most valuable for stable, repeated, high-value behaviours — not for features in flux.

---

## The UI Pyramid Inversion

### What It Looks Like

The team has a large test suite, but almost all of it is in the UI or E2E layer. There are hundreds or thousands of Selenium or Playwright tests covering journeys through the full stack. There are few or no unit tests, and limited API-layer tests.

The suite is slow (full runs take an hour or more), fragile (tests fail when the UI changes), and expensive to maintain. The team treats this as the normal cost of testing.

### Why Teams Fall Into It

UI automation is intuitive and visible. You can see it running. It exercises the real product. It produces obvious value for non-technical stakeholders who can watch the tests execute. It also mirrors how a human tester would verify the product. Teams start here and never build the lower layers.

### The Actual Harm

The test pyramid inverted: all confidence at the top, almost nothing underneath. The cost compounds with product growth — more features mean more UI tests, longer runs, more maintenance. Confidence actually decreases because the suite becomes slower and more flaky as it grows, so engineers start skipping it, working around failures, or marking tests as known-flaky rather than fixing them.

Business logic defects that could be caught in two seconds by a unit test take ten minutes to catch (or miss entirely) in an E2E test that involves the database, the network, and the full rendering stack.

### What To Do Instead

Build from the bottom up. New coverage for a feature should include unit tests for the business logic (fast, isolated, cheap to maintain) and API tests for the service contract (faster than UI, more stable) before adding E2E coverage for the journey. As the lower layers mature, selectively retire E2E tests that duplicate coverage that a faster layer now provides. Track the layer distribution over time and move deliberately toward a healthier pyramid.

---

## The Siloed QA Team

### What It Looks Like

Testing is done by a separate QA team, at the end of the sprint or at the end of the release. Developers write code. The QA team tests it. If bugs are found, they are returned to development for fixes. The quality gate is a sign-off from the QA team before release.

### Why Teams Fall Into It

QA as a separate function has a long history. It provides specialised expertise, independent verification, and a clear separation of responsibility. These are real advantages in some contexts. The pattern becomes an anti-pattern when it is the only quality mechanism — when quality is only the QA team's job, to be applied at the end.

### The Actual Harm

Late defect discovery is expensive. A defect found by QA after a sprint is complete costs more to fix than a defect caught during development. A defect found after release costs more still. The siloed model maximises the time between defect introduction and defect discovery.

More subtly: when quality is someone else's job, engineers do not take ownership of it. Pull requests are submitted with insufficient unit test coverage because "QA will test it." Code is written without considering testability because "that's QA's problem." The culture does not improve because the structural incentive pushes in the wrong direction.

### What To Do Instead

Quality is a team property, not a team's job title. Engineers write unit tests for their own code. QA's role shifts from "does this work?" to "what are we missing?" — risk-based, exploratory, and consultative rather than functional verification. Definition of done includes test coverage criteria. The team as a whole is accountable for quality signals, not a separate function that absorbs blame.

---

## The Deferred Compliance

### What It Looks Like

The team is building in a regulated domain — financial services, healthcare, insurance — but treats compliance as a future concern. "We'll add the audit trail before launch." "We'll handle the GDPR compliance in Phase 2." "The security review can happen once the product is more stable." The team prioritises feature delivery and plans to add compliance in a later sprint.

### Why Teams Fall Into It

Compliance work is less visible than feature work. It does not produce user-visible functionality. Stakeholders pushing for feature progress rarely push for compliance progress with the same urgency — until an audit or a regulatory review creates a crisis.

### The Actual Harm

Retrofitting compliance is significantly harder than building it in. An audit trail that was not part of the data model from the start requires a schema migration, historical data backfilling, and a data engineering effort that the team did not budget for. A consent management flow that was not in the original design may require rethinking user flows that are already built and tested.

The legal risk is also real. Operating a regulated product without the required controls — even in a pre-launch or beta phase — can create regulatory exposure in some jurisdictions.

### What To Do Instead

Treat compliance requirements as features. An audit trail has functional requirements, acceptance criteria, and validation tests. Put it in the backlog alongside the business features, and sequence it before the business features that depend on it. Make the compliance roadmap visible and credible from the project start. Involve legal and compliance functions at the design stage, not the review stage.

**See also:** [Situation 5 — High-Regulation Domain](SITUATIONS-CATALOGUE.md#situation-5--high-regulation-domain), [Edge Case C — Compliance-Heavy Domain, Startup Speed](SITUATIONS-CATALOGUE.md#edge-case-c--compliance-heavy-domain-startup-speed)

---

## The Tool-First Strategy

### What It Looks Like

A team selects a testing tool — Selenium, Playwright, Cypress, Postman, LoadRunner, a test management platform — and announces that this is their test strategy. The tool choice is the first decision made. Questions about what to test, why, and at what level are answered later, informed by what the tool makes easy.

### Why Teams Fall Into It

Tools are tangible. Purchasing a tool, installing it, and demonstrating it produces visible progress. It is also easier to get budget for a tool purchase than for a strategy workshop. The tool becomes the frame through which the testing approach is designed.

### The Actual Harm

Tool-first strategies produce testing that fits the tool's model rather than the system's risk profile. A team with a Selenium licence will write Selenium tests for everything, regardless of whether a unit test or an API test would give better signal more cheaply. A team with a test management platform will structure their work to produce the reports the platform excels at, rather than the quality information the team actually needs.

When the tool is wrong for the context — a UI automation tool for an API-heavy backend, a scripted test management platform for a context that needs exploratory testing — the quality strategy is constrained by the wrong tool from the start.

### What To Do Instead

Define the risk profile, the testing approach, and the layer strategy before selecting tools. Tools should serve the strategy, not define it. Once the testing approach is clear — what to test, at what layer, at what cadence, with what kind of assertion — identify the tools that best support that approach. Different layers may use different tools, and that is correct.

---

## The Fake Green

### What It Looks Like

The CI pipeline is consistently green. All tests pass. The team reports that quality is in a good state. But production incidents persist. Defects are found by customers. Post-incident investigations reveal that the failing behaviour was not covered by any test.

The pipeline is green but not reliable as a quality signal.

### Why Teams Fall Into It

Teams are rewarded for green pipelines. Flaky tests are suppressed or quarantined rather than fixed, reducing the noise but also reducing the signal. Tests are written to cover the paths developers expect to succeed, not the paths that fail in production. Automation is added to prove that specific scenarios work, not to discover whether the system is correct.

### The Actual Harm

A false quality signal is worse than no quality signal. It produces a false sense of safety that leads to under-investment in other quality activities (exploratory testing, production monitoring, incident response process). The team believes quality is good because the pipeline is green, while defects escape steadily.

The insidious version of this pattern is the suite that was once meaningful but has decayed: tests were written for features that were later changed, updated tests were not written for the changes, and the suite now covers the old behaviour while missing the current one.

### What To Do Instead

Measure pipeline effectiveness, not just pipeline state. Track: how many production defects were not caught by CI? Which test suite areas have not changed in over six months while the product has? What is the flakiness rate and what happens to quarantined tests? Treat the gap between CI results and production quality as a quality metric in itself. Invest in production observability (monitoring, alerting, synthetic probes) as a complementary layer that the pipeline cannot replace.

**See also:** [Edge Case D — Mature Automation, No Observability](SITUATIONS-CATALOGUE.md#edge-case-d--mature-automation-no-observability)

---

## The Never-Retire Rule

### What It Looks Like

The test suite grows indefinitely. Tests are added every sprint. Tests are never deleted. The justification is: "We might need this test. It represents work we did. Deleting tests means losing coverage."

Over time, the suite contains tests for deprecated features, tests for removed functionality, tests that are permanently failing and marked as skip, and tests that duplicate other tests at a less efficient layer.

### Why Teams Fall Into It

Deleting tests feels risky. What if the test was covering something that still matters? What if deleting it causes a gap? The path of least resistance is to leave old tests in place and add new ones.

### The Actual Harm

An indefinitely growing suite becomes slower, harder to understand, and harder to maintain. The signal-to-noise ratio decreases. Engineers stop reading the full test output because too many tests produce irrelevant output. Maintenance cost increases with the suite size, not just with the new coverage. The suite becomes a legacy asset that nobody can safely change.

A specific harm: tests covering removed or deprecated functionality may actively obscure real defects, because they produce failures that engineers learn to ignore.

### What To Do Instead

Establish explicit test retirement criteria and treat them as part of the team's definition of done for any removal or deprecation of functionality. A test should be retired when: the behaviour it covers has been removed; it is covering behaviour now covered by a faster, more reliable test at a lower layer; it has been flaky for more than a defined period without a fix; or it is no longer relevant to any part of the current risk profile. Retiring tests is a quality activity, not a quality reduction.

---

## Quick Reference

| Anti-Pattern | Root Cause | Signal That You're In It |
|---|---|---|
| Coverage Number Trap | Measuring activity instead of risk | Stakeholders ask "how many tests?" |
| Automation First Fallacy | Automating before stability | High automation maintenance burden on new features |
| UI Pyramid Inversion | Starting and staying at the top | Slow suite, high flakiness, low unit coverage |
| Siloed QA Team | Quality as function, not property | Defects found late; engineers don't own tests |
| Deferred Compliance | Treating compliance as overhead | Bulk compliance effort pre-launch |
| Tool-First Strategy | Tool purchase before strategy | Testing shaped by tool's strengths, not risk profile |
| Fake Green | False confidence in green pipeline | Production incidents from untested scenarios |
| Never-Retire Rule | Risk aversion around deletion | Suite grows indefinitely; run time increases quarterly |
