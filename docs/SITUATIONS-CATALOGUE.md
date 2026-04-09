# Strategy Situations Catalogue

Last Updated: 2026-04-09

## Purpose

Each situation is a full case study. It describes a real engagement type, the specific risk profile it creates, the strategy decisions that follow, the tradeoffs you are accepting, what good looks like when it is working, and the mistakes teams most commonly make.

Read these situationally — find the one that most resembles your current context and use it as a thinking frame, not a checklist.

---

## Core Situations

---

### Situation 1 — Tight Timeline

**The Setup**

A team has a fixed delivery date that cannot move. Budget or contract scope limits what work can realistically be done. The QE team is typically small relative to the delivery surface, and stakeholders are focused on the feature list, not the test plan.

**The Risk Profile**

The primary risk is releasing with insufficient confidence in the critical path. Secondary risks are: wasting limited capacity on low-value coverage, under-communicating tradeoffs to stakeholders (so failures become surprises), and building automation that is too broad to complete or too brittle to trust.

There is also a hidden risk: teams in this situation often produce the illusion of coverage — tests that exist but are shallow, unreliable, or not connected to release decisions.

**The Strategy Decision**

1. Name the must-pass scenarios. Not "regression" — specific business-critical flows that, if broken, would block the release or cause immediate customer harm.
2. Build a minimum viable test baseline around those flows only. Smoke, critical-path, and release-risk scenarios. Nothing else until those are stable.
3. Make tradeoffs explicit and visible. Document what is not being covered and why. This is a quality decision, not a quality failure — but only if the people making release decisions can see it.
4. Defer automation build-out on anything that is not stable or not yet agreed. Automating unstable features burns capacity and produces unreliable signals.
5. Maximise manual exploratory effort on high-risk, high-churn areas. That is where judgment adds the most value under pressure.

**The Tradeoff**

You are trading breadth for depth and speed. A narrow, well-understood release baseline is more useful than a wide, unreliable one. You are not trying to prove the whole system works. You are trying to prove that the most important things work well enough to release.

**What Good Looks Like**

Three months in: the critical-path scenarios are automated, reliable, and gating releases in CI/CD. The deferred areas have a prioritised backlog. Stakeholders understand the coverage boundary and make release decisions based on known information, not hope.

**Common Mistakes**

- Trying to automate everything and finishing nothing
- Not documenting exclusions, then being surprised when a deferred area breaks in production
- Using test count as a progress metric — finishing 200 tests that don't cover the real risks
- Over-investing in the test framework infrastructure at the expense of writing the actual tests

**Related Anti-Patterns:** [The Coverage Number Trap](STRATEGY-ANTI-PATTERNS.md#the-coverage-number-trap), [The Automation First Fallacy](STRATEGY-ANTI-PATTERNS.md#the-automation-first-fallacy)

---

### Situation 2 — Legacy System

**The Setup**

The system has been running for years. The codebase is large, partially undocumented, and maintained by a mix of people who remember how it was built and people who do not. There may be automation, but it is likely concentrated in the UI layer and may be fragile. There is production behaviour that nobody fully understands but everyone depends on.

**The Risk Profile**

The primary risk is regression — changing something that breaks existing behaviour in a way that is only discovered after release. Secondary risks are: test brittleness (tests that fail for environmental reasons rather than real defects), loss of SME knowledge over time, and the tendency to keep adding tests without ever retiring broken or redundant ones.

There is a subtler risk: teams in this situation often have high test counts but low confidence. The suite runs slowly, is flaky, and nobody trusts the results enough to use them as a real quality gate.

**The Strategy Decision**

1. Start with the business-critical flows, not the technical surface. Know which journeys, if broken, would cause the most harm. These are your highest-priority regression targets regardless of what automation already exists.
2. Audit existing automation. For each test or suite, make an explicit decision: retire, stabilise, refactor, or expand. Tests that are too brittle to be reliable should be retired. Tests that cover real risk but run unreliably should be stabilised before being scaled.
3. Favour API and service-layer testing where the legacy UI is the brittleness source. If the business logic lives in a service layer, test it there. Use UI automation only for the flows where the UI interaction itself is part of the risk.
4. Protect before you modernise. If the system is being re-platformed or refactored, establish a regression baseline first. Do not start the modernisation before you can detect regressions.
5. Treat SME knowledge capture as a quality activity. Where automated tests cannot yet exist, documented exploratory sessions and bug reports are a valid interim.

**The Tradeoff**

You are trading speed of new coverage for stability of existing confidence. A reliable subset is more valuable than a broad, unreliable suite. This is frustrating when stakeholders want to see new tests, but the right answer in a legacy context is almost always to fix the suite you have before expanding it.

**What Good Looks Like**

Three months in: flaky tests have been retired or stabilised. The critical-path flows have reliable API-layer coverage. The UI automation is smaller and more targeted. The suite runs faster. Developers trust the results enough to be unblocked by a green run.

**Common Mistakes**

- Treating legacy automation as a sunk cost that must be preserved rather than a liability that should be evaluated
- Building new automation on top of a fragile foundation without stabilising it first
- Using test run time as a success metric rather than defect escape rate or release confidence
- Underestimating how much of the system behaviour lives in undocumented SME knowledge

**Related Anti-Patterns:** [The Never-Retire Rule](STRATEGY-ANTI-PATTERNS.md#the-never-retire-rule), [The UI Pyramid Inversion](STRATEGY-ANTI-PATTERNS.md#the-ui-pyramid-inversion)

---

### Situation 3 — Greenfield Product

**The Setup**

A new system is being built from scratch. The team has freedom to choose the architecture, the tooling, and the quality practices. There are no legacy tests to maintain, no brittle environments to work around, and no accumulated technical debt — yet.

**The Risk Profile**

The primary risk is building poor foundations and then inheriting them forever. Greenfield teams often underestimate how quickly their clean slate decays. The second phase of a greenfield project is usually brownfield.

Secondary risks are: front-loading too much automation infrastructure before the product is stable enough to test reliably; building at the wrong layer (too much UI, too little unit and API); and embedding quality gates late, after patterns are already set.

**The Strategy Decision**

1. Build from the bottom up. Unit tests for business logic. Component tests for modules. API/contract tests for service boundaries. UI automation only for critical user journeys, added after the lower layers carry baseline confidence.
2. Embed quality gates in CI/CD from the first sprint. A green build gate that runs in under five minutes — starting with a small test set — is more valuable than a comprehensive suite that takes an hour and blocks nobody.
3. Define the test strategy before writing the first feature. The decisions made in week one (layer ownership, naming conventions, where boundary tests live, how data is managed) shape everything that follows. They are much harder to change at month six.
4. Set automation viability criteria. A scenario is worth automating if it is stable, high-value, repeated, and falsifiable. New features in active development often fail this test — automate them after they settle.
5. Think about observability from day one. Logging, tracing, and monitoring are part of the quality system, not a separate concern for production later.

**The Tradeoff**

You are trading early velocity for long-term maintainability. Investing in foundations slows down the first few sprints but compounds into much lower automation maintenance cost over the following year. Teams that skip this almost always end up redoing it from a much more constrained position.

**What Good Looks Like**

Six months in: the test pyramid is proportionate — most confidence comes from unit and API layers, UI automation is targeted and stable. CI/CD gates run in under ten minutes for the majority of commits. No single person owns the test suite. Coverage grows with the product rather than lagging it.

**Common Mistakes**

- Treating the test strategy as something to write after the first release
- Starting with E2E test automation because it is intuitive and visible, while leaving lower layers thin
- Writing automation for features that are still changing rapidly, then maintaining it instead of building the real coverage
- Not aligning on layer ownership within the team — so everyone writes tests at whichever layer is most comfortable

**Related Anti-Patterns:** [The Automation First Fallacy](STRATEGY-ANTI-PATTERNS.md#the-automation-first-fallacy), [The Tool-First Strategy](STRATEGY-ANTI-PATTERNS.md#the-tool-first-strategy)

---

### Situation 4 — Brownfield Product

**The Setup**

The product has been live for years. It has customers, a production track record, and existing automation of some kind. A team is being asked to improve quality, accelerate delivery, or reduce defect escape rate — without breaking what already works.

**The Risk Profile**

The primary risk is regression during change. Brownfield systems have implicit contracts — observable behaviour that customers depend on, even if it is undocumented. Breaking that behaviour unintentionally is the most common source of high-severity incidents.

Secondary risks are: carrying automation that is technically complete but strategically wrong (wrong scope, wrong layer, wrong frequency), under-investing in the API and service layer because the UI automation already "feels" like coverage, and treating modernisation as a clean-slate problem when it is actually a transition problem.

**The Strategy Decision**

1. Audit the existing automation before writing a single new test. For each test or suite: what risk does it protect? How reliable is it? How expensive is it to maintain? Is it at the right layer? This audit takes time but is not optional — building on a poor foundation is multiplying a problem.
2. Establish a regression baseline for the highest-risk business flows before any significant change. If you are re-platforming, migrating, or refactoring, you need a before-state you can test against.
3. Prioritise API-layer coverage for the core business logic. UI automation is valuable at the journey level; API automation is valuable at the contract and logic level. At brownfield scale, you need both — but the API layer typically has the most coverage gap.
4. Retire tests that are unreliable or no longer relevant. A leaner, trustworthy suite is more useful than a large, noisy one. Establish a convention for when tests get retired — failing for over N runs without a fix, covering functionality that has been removed, or running so slowly they are always skipped.
5. Sequence automation growth with delivery. New automation should be written as part of feature delivery, not as a separate backlog item. This is how the suite grows proportionally.

**The Tradeoff**

You are trading the perception of progress (new test count) for actual quality improvement (reliable, trustworthy coverage at the right layers). Brownfield improvement is slower and less visible than greenfield build-out, but the risk of getting it wrong is higher because real users are depending on the system every day.

**What Good Looks Like**

Six months in: flaky tests have been retired or fixed. The API layer has material coverage for the core business flows. UI automation covers the critical user journeys reliably. The suite runs in a predictable time window and is used as a real quality gate — not just a reporting exercise.

**Common Mistakes**

- Treating brownfield as greenfield — writing a strategy that assumes a clean slate when you are carrying real inheritance
- Adding new coverage on top of a flaky foundation without stabilising it
- Never retiring old tests because they represent "work done"
- Optimising for the test count number rather than the reliability and relevance of what exists

**Related Anti-Patterns:** [The Never-Retire Rule](STRATEGY-ANTI-PATTERNS.md#the-never-retire-rule), [The UI Pyramid Inversion](STRATEGY-ANTI-PATTERNS.md#the-ui-pyramid-inversion)

---

### Situation 5 — High-Regulation Domain

**The Setup**

The system operates in a domain with regulatory obligations — financial services, healthcare, insurance, government, defence, or similar. Compliance is not optional. Audit trails, traceability, data controls, and approvals are part of the delivery obligation, not optional add-ons.

**The Risk Profile**

The primary risk is not functional defects — it is compliance failure. A system that works correctly but lacks the required audit trail, the required data segregation, or the required approval chain can expose the organisation to regulatory action regardless of functional quality.

Secondary risks are: treating compliance as a documentation activity rather than a tested capability; building a testing strategy that covers functional behaviour well but has no coverage of the compliance controls themselves; and discovering compliance gaps late, when remediating them is expensive and time-consuming.

**The Strategy Decision**

1. Map the regulatory obligations to testable requirements before writing the test strategy. What specifically must be demonstrated? What must be traceable? What must be auditable? These become first-class test scenarios, not footnotes.
2. Automate the traceability, not just the tests. A compliance test that passes but cannot be linked back to the requirement it covers is insufficient in an audit. Requirement → test → result traceability must be part of the test infrastructure.
3. Treat data controls as test scenarios. Data residency, access controls, PII handling, retention and deletion — these need to be explicitly tested, not assumed to be correct because the feature works.
4. Be conservative about AI-generated recommendations. In regulated domains, a recommendation that cannot be explained or attributed is a compliance liability. Use AI to accelerate drafting and gap analysis; do not use it to make final compliance determinations.
5. Build the governance model before you need it. Approval chains, sign-off processes, audit log format, and retention policies are easier to build into the system early than to retrofit.

**The Tradeoff**

You are trading delivery velocity for compliance assurance. The cost of failing an audit or a regulatory review is almost always higher than the cost of building compliance into the delivery process from the start. This is a context where "we'll add the audit trail later" is a genuinely dangerous decision.

**What Good Looks Like**

The compliance controls are tested explicitly and regularly. Traceability links exist from requirement to test to result. The audit package for a given release can be produced without a manual assembly exercise. Regulatory reviews do not produce surprises because the control gaps were found in testing, not by the regulator.

**Common Mistakes**

- Treating compliance as a sign-off activity at the end of the release
- Assuming that functional test coverage implies compliance coverage
- Relying on AI-generated recommendations for compliance interpretation without human review
- Building the governance model after the product is already in operation

**Related Anti-Patterns:** [The Deferred Compliance](STRATEGY-ANTI-PATTERNS.md#the-deferred-compliance), [The Siloed QA Team](STRATEGY-ANTI-PATTERNS.md#the-siloed-qa-team)

---

### Situation 6 — Microservices / Distributed System

**The Setup**

The product is composed of many small services, each independently deployable, often owned by different teams. The business flows cross service boundaries. Integration is through APIs, events, or queues. There may be ten or twenty services involved in a single user-facing journey.

**The Risk Profile**

The primary risk is integration failure — services change their contracts independently, and failures at boundaries are only discovered when the consumer tries to use the new or changed producer. In monolithic systems this is a compile-time or merge-time problem. In distributed systems it is a runtime problem, often in production.

Secondary risks are: test ownership fragmentation (each team tests their service, nobody tests the whole), end-to-end test flakiness that compounds as the number of service dependencies increases, and environment complexity that makes reliable integration testing expensive.

**The Strategy Decision**

1. Make contract testing load-bearing. Consumer-driven contract tests (e.g. using Pact, or OpenAPI validation) catch breaking changes at the boundary before they reach integration environments. Each service team owns their side of the contracts they participate in. This is cheaper, faster, and more reliable than end-to-end integration testing for catching interface regressions.
2. Define test ownership per layer. Unit and component tests: service team's responsibility. Contract tests: shared responsibility between consumer and provider teams. End-to-end journey tests: owned by a platform or QE team with cross-service visibility. Without explicit ownership, end-to-end coverage becomes a shared assumption with no single accountable owner.
3. Use E2E sparingly. A small suite of business-critical journey tests, running against a stable integration environment, is more useful than a large E2E suite that is permanently flaky because one of its twelve dependencies is unstable. Invest in making the small set reliable rather than growing it.
4. Invest in observability as a quality layer. In a distributed system, structured logs, distributed tracing, and alerting are part of how you detect failures. They are not a production-only concern. Build them in from the start and include them in the quality strategy.
5. Manage environment dependencies explicitly. Know which service depends on which others. Version the contracts. Have a clear policy for what version of a dependency is used in each test environment. Environment drift is a primary cause of unreliable integration test results.

**The Tradeoff**

You are trading the simplicity of a monolithic test model for the resilience of a distributed one. Contract testing is more complex to set up but far more scalable. End-to-end testing is intuitive but does not scale reliably past a certain service count. The teams that succeed here invest in the contract layer early and treat it as a first-class part of the delivery process.

**What Good Looks Like**

Contract tests catch breaking changes before they reach shared environments. Each service team has clear test scope and ownership. The small E2E suite is stable and gating. Distributed tracing makes failures in integration environments diagnosable in minutes rather than hours. New services join an existing pattern, not a new bespoke one.

**Common Mistakes**

- Relying entirely on E2E tests to catch integration regressions, then being surprised when they become unmanageable
- Assuming each team will test the integration layer without explicit ownership assignment
- Growing the E2E suite without investment in reliability, until it runs for hours and nobody trusts it
- Treating observability as a production operations concern rather than a quality infrastructure concern

**Related Testing Deep-Dive:** [Contract Testing](TESTING-TYPE-CONTRACT.md)

---

### Situation 7 — High-Frequency Release Cadence (CI/CD-Native)

**The Setup**

The team deploys multiple times per day. There is no manual regression window. The quality gate is the pipeline. Releases are automated, and quality decisions must be made in minutes, not days.

**The Risk Profile**

The primary risk is that the pipeline quality signal is too slow, too noisy, or too incomplete to be trustworthy at this cadence. If the pipeline takes forty-five minutes and is occasionally flaky, it is not a real quality gate — it is a bureaucratic checkpoint that is routinely overridden or ignored.

Secondary risks are: progressive delivery controls (feature flags, canary releases) not being part of the quality strategy; production observability gaps that mean defects are found by customers rather than by monitoring; and the pipeline becoming a bottleneck rather than an accelerator.

**The Strategy Decision**

1. Build the pipeline in layers. A first gate — unit tests, linting, security scanning, critical API tests — should run in under five minutes and gate every commit. Longer-running integration and E2E tests run on a separate schedule (post-merge, nightly) and gate deployments to higher environments. Every layer of the pipeline must have a known expected duration and a clear gate condition.
2. Treat flaky tests as pipeline blockers, not background noise. A test that fails intermittently poisons the signal for everything else. Track flakiness rates. Any test that fails without a corresponding code change gets quarantined and fixed or retired.
3. Include progressive delivery in the quality model. Feature flags, canary deployments, and dark launches are quality mechanisms, not just deployment mechanisms. A canary that routes 5% of traffic to a new version and is monitored for error rate increase is a production quality gate. Include it in the strategy.
4. Design for shift-right. Synthetic monitoring, real-user monitoring, error budgets, and SLO-based alerting are how you detect quality issues that were not caught by the pipeline. The strategy should name which production signals are monitored, what thresholds trigger action, and who is responsible.
5. Guard the pipeline run time actively. Every test added has a time cost. Every dependency on an external service in a critical-path test is a potential source of flakiness. Gate additions actively. Require the pipeline to stay within defined time bounds as a named quality criterion.

**The Tradeoff**

You are trading test breadth for pipeline speed and reliability. The most common failure mode is building a pipeline that is technically complete but practically unusable — so slow and noisy that engineers work around it rather than through it. A smaller, reliable, fast pipeline is almost always more valuable than a comprehensive, slow, flaky one.

**What Good Looks Like**

The first-stage pipeline runs in under five minutes. The full pipeline runs in under twenty. Flakiness rate is measured and close to zero for the critical path. Progressive delivery is used for significant new features. Production error rate is monitored against an SLO. Incidents are detected by monitoring, not by customers.

**Common Mistakes**

- Building a single flat pipeline that runs everything sequentially and takes forty-five minutes
- Not measuring or acting on flakiness until it becomes a critical problem
- Treating progressive delivery as a deployment team concern rather than a quality concern
- Having no production quality signal — treating "deploy succeeded" as equivalent to "quality is acceptable"

**Related Anti-Patterns:** [The Fake Green](STRATEGY-ANTI-PATTERNS.md#the-fake-green)

---

### Situation 8 — Mobile-First or Cross-Platform Product

**The Setup**

The product is delivered on mobile devices — iOS, Android, or both — possibly alongside a web version. The device surface is large: multiple OS versions, screen sizes, hardware capabilities, and network conditions. Testing every combination is not possible.

**The Risk Profile**

The primary risk is device fragmentation — the product works on the test devices but not on the devices customers actually use. This is particularly acute for older OS versions and lower-end hardware. The secondary risk is flakiness: mobile automation frameworks are inherently less stable than API testing because they interact with the rendered UI and the device OS, both of which are outside the team's control.

A third risk is the assumption that the strategy can be lifted from web testing and applied to mobile without adaptation. Mobile lifecycle events (backgrounding, interrupts, low memory, network transitions) are not present in web or API testing and are a significant source of production defects.

**The Strategy Decision**

1. Define the device matrix deliberately. The full combination of OS versions and device types is too large to test completely. Choose a priority tier (latest two major OS versions, top-selling device categories by market share for your target demographic) and a coverage tier (older OS versions that have significant user base). Be explicit about what is not covered.
2. Push logic down and out of the UI layer. Business logic in the UI layer is both harder to test and more fragile. If the application architecture allows it, unit-test the business logic separately from the UI. API-layer automation for the backend interaction is more stable than UI automation for the same behaviour.
3. Use emulators for repeatability, real devices for confidence. Emulators run faster and are more reliable as a CI/CD pipeline gate. Real-device testing (via device farm or physical devices) is more expensive and slower but catches device-specific issues that emulators miss. Use both: emulators for the fast feedback loop, real device for the pre-release confidence gate.
4. Test mobile-specific behaviour explicitly. Backgrounding and foregrounding, network interruption and recovery, low storage conditions, notification handling, deep links, and permission changes are all mobile-specific risk scenarios. They need to be in the test strategy, not assumed to be covered by generic functional tests.
5. Accept a higher flakiness tolerance at the UI layer and compensate elsewhere. Mobile UI automation will always have some flakiness. Compensate by having strong and reliable coverage at the API and unit layers, so mobile UI flakiness is a signal about mobile-specific risk, not about whether the core product works.

**The Tradeoff**

You are trading full coverage (impossible) for deliberate triage. The device matrix question has no correct answer — only a defensible one. Document why you chose the priority matrix you chose. Document what you are not testing and what risk that carries.

**What Good Looks Like**

The device priority matrix is documented and reviewed each quarter. Emulator-based automation gates the CI pipeline. Real-device testing runs before significant releases. Mobile-specific scenarios have explicit test coverage. The team tracks which OS versions are generating disproportionate crash reports and adjusts the priority matrix accordingly.

**Common Mistakes**

- Using a device matrix that reflects what the team has access to, rather than what customers actually use
- Not testing mobile-specific lifecycle events and then being surprised by production crashes
- Applying web UI testing patterns directly to mobile without adaptation
- Treating emulator-passing as equivalent to device-passing for a pre-release quality gate

---

### Situation 9 — Data-Heavy System (Analytics / Data Platform / ML Pipeline)

**The Setup**

The core of the product is data transformation, aggregation, or model inference. Business logic lives in the transformation pipeline rather than in traditional application code. The output of the system is a dataset, a model, a report, or a prediction — not a UI interaction or an API response.

**The Risk Profile**

The primary risk is silent correctness failure — the pipeline runs successfully, produces output, but the output is wrong in ways that are not immediately obvious. Data drift, schema mismatches, incorrect aggregations, and model quality degradation are all failures that pass without error unless the test strategy explicitly looks for them.

Secondary risks are: pipeline observability gaps (knowing the pipeline ran, but not whether the output is correct), schema contract drift between producer and consumer data systems, and the absence of a regression baseline for the output data — so there is no way to know whether a change in output is intentional or a defect.

**The Strategy Decision**

1. Define correctness assertions for the output data, not just the pipeline execution. A green pipeline run is not a quality signal. The strategy must include assertions about what the output data should contain, exclude, or aggregate to. These are your functional tests for a data system.
2. Establish a reference dataset and a comparison baseline. For any significant transformation or model, maintain a small, well-understood reference input and its expected output. Run the pipeline against it on every change and assert that the output matches. This is the data equivalent of a unit test.
3. Test schema contracts between producer and consumer systems. When the upstream system changes its schema, the downstream consumer breaks silently. Schema contract validation — asserting that the agreed schema is still being delivered — should run as part of the CI/CD pipeline.
4. Build data quality monitors for production. Data volumes, null rates, value distributions, and freshness checks are production quality signals. They belong in the quality strategy, not the operations runbook. A sharp drop in data volume or an unexpected null rate spike is a quality incident, not just an operational alert.
5. Include model quality metrics in the release gate (for ML systems). Accuracy, precision, recall, F1, or domain-specific metrics should be asserted against a minimum threshold before a new model version is promoted. Model regression — a new version performing worse than the previous one — is a defect.

**The Tradeoff**

You are trading familiar test patterns (functional, UI, API) for data-native ones (assertions, reference datasets, schema contracts, quality monitors). Teams that apply traditional software testing patterns to data systems typically produce high test count and low quality confidence. The right tests here are different in kind, not just different in subject matter.

**What Good Looks Like**

The pipeline has a reference test dataset with explicit output assertions. Schema contracts are tested automatically on every deployment. Production data quality monitors are running and alerting on out-of-bound conditions. For ML systems, model quality metrics are included in the release gate and tracked over time.

**Common Mistakes**

- Treating successful pipeline execution as a quality signal
- Writing integration tests for the pipeline orchestration but not asserting on the output data quality
- Discovering schema drift in production rather than in CI/CD
- Not maintaining a regression baseline for model quality over time

---

### Situation 10 — Third-Party Integration Heavy

**The Setup**

A significant portion of the product's functionality depends on external services: payment gateways, identity providers, shipping APIs, ERP systems, communication platforms, mapping services. Some of these integrations are critical path. The team does not own, cannot modify, and often cannot test against real versions of these services in development environments.

**The Risk Profile**

The primary risk is boundary failure — the integration breaks because the external API changed, returned an unexpected response, degraded in performance, or became temporarily unavailable. The team discovers this through a production incident rather than in testing.

Secondary risks are: over-trusting vendor quality (assuming the third-party service works correctly and only testing your side of the integration), under-investing in the integration seam (the parsing, error handling, and retry logic on your side), and building automation that depends directly on live third-party services and thereby introduces reliability problems into the test suite.

**The Strategy Decision**

1. Define your integration boundary precisely. Your team is responsible for: correctly calling the third-party API, correctly parsing the response, correctly handling error cases and edge cases in the contract, and correctly propagating or recovering from failures. The vendor is responsible for the rest. Test what is yours to own — not what is the vendor's to own.
2. Use test doubles (stubs, mocks, service virtualization) for third-party services in development and CI/CD. Live third-party APIs introduce flakiness, costs, rate limits, and data side effects into your test suite. A controlled stub that returns predictable responses is more useful for CI/CD automation. Use live third-party calls only at the integration environment level and above.
3. Test your error handling, not just the happy path. The third-party service will eventually return a 429, a 503, a malformed response, or an unexpected payload. These scenarios are predictable and must be tested. Stub the third-party response to return each of these conditions and assert that your system handles them correctly.
4. Monitor the live integration in production. Synthetic probes that make real calls to third-party services and assert expected behaviour are a production quality layer. They catch degradations, API version changes, and contract drift before your users do.
5. Build integration contract tests where the third party supports it. Some providers publish OpenAPI or JSON Schema specifications. Validate your code against those schemas as part of CI/CD. When the provider updates their spec, the contract test catches the change.

**The Tradeoff**

You are trading the certainty of live testing for the reliability and speed of controlled testing. You cannot fully replicate a third-party service, but you can test your side of the integration very thoroughly with controlled inputs. The combination of good stub-based CI/CD coverage and production synthetic monitoring is almost always better than relying on live third-party calls in the pipeline.

**What Good Looks Like**

All third-party interactions in CI/CD use controlled stubs. Error cases (rate limits, timeouts, malformed responses, API errors) are explicitly tested. Production synthetic monitors are running against each critical integration. When the third-party changes their API, the contract test catches it before it reaches production.

**Common Mistakes**

- Testing only the happy path against the third-party and assuming errors will not occur
- Running CI/CD tests against live third-party services and dealing with flakiness as a permanent cost
- Assuming vendor quality is your quality guarantee — it is not
- Discovering a third-party API change through a production incident

---

### Situation 11 — Security-First Domain (FinTech, HealthTech, DefTech)

**The Setup**

The system handles sensitive data — financial transactions, health records, identity credentials, or classified information. Security is not an add-on concern; it is a core product property. Breaches are high-impact by nature, and the regulatory consequences of a security failure in these domains are severe.

**The Risk Profile**

The primary risk is a security vulnerability that is discovered after deployment — or by an attacker before it is discovered internally. OWASP Top 10 vulnerabilities (injection, broken authentication, sensitive data exposure, etc.) are the well-known surface. The less-obvious risk is that security testing is treated as a separate, periodic activity rather than a continuous quality layer embedded in the delivery process.

Secondary risks are: compliance controls (PCI-DSS, HIPAA, SOC 2) not being tested — only documented; pen testing findings that are not fed back into the CI/CD coverage; and the assumption that security is the security team's job rather than a shared quality responsibility.

**The Strategy Decision**

1. Run SAST in the build pipeline on every commit. Static application security testing catches known vulnerability patterns (SQL injection, hardcoded credentials, insecure dependencies) at the earliest possible point. SAST should gate the build, not just report.
2. Run SCA (software composition analysis) on every dependency update. Third-party libraries are a primary source of known vulnerabilities (CVEs). Tools like Dependabot, Snyk, or OWASP Dependency-Check should run on every dependency change and gate merges on high-severity findings.
3. Run DAST against deployed environments on a scheduled basis. Dynamic application security testing probes the running application for exploitable vulnerabilities. It is slower and heavier than SAST but catches runtime vulnerabilities that static analysis cannot. Run it against staging on every significant release.
4. Include security scenarios in the functional test suite. Authentication boundary tests, authorisation matrix tests (who can access what), input validation tests, and sensitive data handling tests are ordinary test scenarios in a security-first domain. They belong in the main test suite, not in a separate security repository.
5. Feed pen test findings back into the automated test suite. When a pen test identifies a vulnerability, the fix should be accompanied by an automated test that would have caught it. This builds a regression library from real findings.

**The Tradeoff**

You are trading delivery speed for security assurance. Security gates add time to the pipeline. Dependency scanning will produce findings that require triaging. Pen testing will surface issues that require remediation before release. This cost is real, but it is always less than the cost of a security incident in a domain where the data involved is inherently sensitive.

**What Good Looks Like**

SAST runs on every commit and gates the build. Dependency scan runs on every PR. DAST runs on every release to staging. Authorization boundary scenarios are in the automated test suite. Pen test findings are retested after remediation and converted into automated regression tests.

**Common Mistakes**

- Treating security testing as a separate phase rather than a continuous quality layer
- Running pen tests but not tracking whether the findings were retested after remediation
- Not including authorisation and authentication boundary tests in the functional test suite
- Assuming that passing functional tests implies passing security posture

**Related Testing Deep-Dive:** [Security Testing in the Pipeline](TESTING-TYPE-SECURITY.md)

---

### Situation 12 — Performance-Critical System (Trading, Real-Time, High-Volume)

**The Setup**

The system has explicit performance requirements. Response latency, throughput, concurrency, and availability targets are defined and known. In trading systems, millisecond latency matters. In real-time systems, jitter is a defect. In high-volume systems, throughput at peak load is a release gate.

**The Risk Profile**

The primary risk is that functional testing passes and performance testing is deferred — so a performance regression or capacity limit is discovered in production under load. The second risk is that performance testing is conducted once (pre-launch) rather than continuously, so regressions introduced by later changes are caught late.

A subtler risk is conflating performance testing types — running a load test when a stress test is needed, or running a soak test without a baseline to compare against. Each type of performance test answers a different question, and using the wrong one gives a false sense of assurance.

**The Strategy Decision**

1. Define performance SLAs as testable requirements before writing the performance test strategy. Without a specific target (p95 response time < 200ms at 500 concurrent users), performance testing has no pass/fail condition. It becomes observation, not validation.
2. Run a subset of performance tests in CI/CD on every significant change. A lightweight baseline test — smaller user load than peak, shorter duration — that asserts the p95 response time is within bound catches regressions early. It does not need to simulate peak load; it needs to detect trends.
3. Run full load and stress tests before every significant release, including releases to staging. These are your release quality gate for performance. Results should be compared against the previous release baseline, not just against an absolute threshold.
4. Treat performance regressions as defects. A change that increases p95 response time by 40% may be acceptable if it is understood and justified, but it must be a conscious decision, not an invisible drift. Flag it, review it, accept it with a record, or fix it.
5. Include soak and endurance testing for systems with memory management risks. A system that performs well for twenty minutes but degrades over four hours has a real production defect. Soak tests are the only way to catch it before it becomes an incident.

**The Tradeoff**

You are trading test infrastructure cost and pipeline complexity for production confidence. Performance test environments cost more to run. Full load tests take longer. But the cost of a performance incident in a trading system or a high-volume platform is almost always higher than the cost of the infrastructure to catch it earlier.

**What Good Looks Like**

Performance SLAs are documented and agreed before the first performance test is written. A baseline performance test runs in CI/CD and gates all significant changes. Full load tests run before every release to staging. Results are tracked over time and compared to prior releases. Soak tests run on a weekly or release cadence for memory-sensitive systems.

**Common Mistakes**

- Deferring performance testing to the last sprint before launch
- Running performance tests without a defined baseline to compare against
- Treating performance testing as a one-time activity rather than a continuous quality gate
- Conflating load, stress, and soak tests — running all three as "load tests" and answering none of the three questions correctly

**Related Testing Deep-Dive:** [Performance Testing Types](TESTING-TYPE-PERFORMANCE.md)

---

## Edge Case Scenarios

These are the harder situations that do not fall cleanly into one archetype. Real engagements almost always have some element of a mismatch — the system is greenfield but the team is not, or the automation is mature but it is at the wrong layer, or the domain is regulated but the timeline is startup speed. These scenarios describe the most common mismatches and what the strategy must account for when they appear.

---

### Edge Case A — Greenfield System, Brownfield Organisation

**The Setup**

A new product is being built. The architecture is clean. The codebase starts empty. On paper this is a greenfield opportunity. But the team is operating inside an organisation whose culture, processes, infrastructure, and tooling are established years ago. CI/CD maturity may be low. Approval processes are heavyweight. The operations team has a fixed set of supported tools. Security reviews take weeks.

**The Risk Profile**

The primary risk is building a quality strategy for the system that you have, not the organisation that you are operating in. A strategy that assumes fast pipeline feedback, team ownership of automation, and continuous deployment will fail in an organisation where those conditions do not exist — regardless of how sensible the strategy is on paper.

Secondary risks: the team builds the right foundations in isolation, only to have them bypassed by the surrounding organisation's processes. The greenfield product inherits the brownfield constraints of its deployment environment.

**The Strategy Decision**

1. Separate what you can control (the product's test design, the team's practices) from what you must negotiate (pipeline integration, tooling approvals, deployment cadence).
2. Design the quality gates to be compatible with the organisation's actual delivery cycle. If releases are monthly, a daily-deploy quality strategy is not wrong in theory but will not be adopted in practice.
3. Identify which brownfield constraints are temporary (will change as the org matures) and which are structural (not going to change in the lifetime of this project). The strategy should accommodate structural constraints, not fight them.
4. Build in a way that makes modernisation possible later. Even if CI/CD is not available today, structure the tests so they can be integrated into a pipeline when it arrives.

**The Core Tension**

You want to make quality decisions for the system you are building. You must make quality decisions for the organisation you are operating in. Getting this balance wrong — treating the org as if it is already where you want it to be — is the fastest way to produce a strategy that is technically correct and practically ignored.

**Common Mistakes**

- Writing a strategy that assumes the target organisational state rather than the current one
- Treating "best practice" as achievable without identifying the specific changes needed to get there
- Building quality infrastructure that the team cannot maintain because it depends on org capabilities that do not yet exist

---

### Edge Case B — Strong Automation, Wrong Layer

**The Setup**

The team has invested seriously in automation. There are hundreds or thousands of tests. The CI pipeline runs them on every commit. The test count is a source of pride. But the pyramid is inverted: almost everything is in the UI or E2E layer, with very little at the unit or API level.

**The Risk Profile**

The primary risk is that the large, slow, flaky E2E suite is providing less real quality confidence than the team believes. Individual E2E tests are expensive to maintain and slow to run. As the system grows, the suite takes longer to execute, flakiness increases, and the cost of keeping it current rises steeply.

The subtler risk is institutional — the team has significant investment in the existing approach and may resist the evidence that the pyramid needs to be rebalanced.

**The Strategy Decision**

1. Audit the current suite by layer. Quantify what percentage of tests are at each level. Calculate the total pipeline time contribution by layer. Identify the flakiest tests and determine whether they are flaky because of the feature being tested or because of the test layer they are running on.
2. Build the missing layers by adding test coverage at unit and API levels as new features are delivered. Do not wait for a dedicated "pyramid rebalancing" project. Use feature delivery as the vehicle.
3. Retire E2E tests that duplicate coverage that now exists at a lower layer. A stable behaviour covered by an API test does not need to be covered by a UI journey that runs five minutes and is flaky 10% of the time.
4. Set a target layer distribution and track it over time. Not a fixed ratio — but a named direction of travel. Every quarter, the unit:API:E2E ratio should move toward the target.

**The Core Tension**

The team's investment in existing automation is real. Retiring tests feels like losing work. The goal is not to delete what was built — it is to move the confidence layer down over time to where it is faster, cheaper, and more reliable.

**Common Mistakes**

- Continuing to add E2E tests because that is the existing pattern, even when lower layers would give better signal
- Not retiring E2E tests when lower-layer coverage replaces them
- Treating a high test count at any layer as equivalent to a high-quality test strategy

**Related Anti-Patterns:** [The UI Pyramid Inversion](STRATEGY-ANTI-PATTERNS.md#the-ui-pyramid-inversion)

---

### Edge Case C — Compliance-Heavy Domain, Startup Speed

**The Setup**

A startup or scale-up is operating in a regulated domain — HealthTech, FinTech, InsurTech. The investors and the business model require fast iteration. The regulatory framework requires auditability, traceability, data controls, and approval chains. Both of these requirements are real and non-negotiable.

**The Risk Profile**

The primary risk is assuming that one of the two requirements can be deferred. Teams that defer compliance to a later phase almost always discover that retrofitting it is significantly harder than building it in. Teams that defer velocity to meet compliance requirements often lose the commercial opportunity they were trying to capture.

**The Strategy Decision**

1. Identify the non-negotiable regulatory requirements and make them features, not overhead. An audit trail is a feature. A consent management flow is a feature. A data retention policy is a feature. Build them with the same discipline as any other feature, and test them with the same discipline.
2. Automate traceability from the start. Requirement → test → result linkage is the compliance artefact. If you build it as a manual exercise, it will not scale. If you build it as an automated output, it is cheap to maintain and cheap to audit.
3. Define the minimum viable compliance posture for each release phase. Not everything needs to be present from day one, but the roadmap to compliance must be explicit and credible. Know what you are deferring, why, and what the risk of that deferment is.
4. Involve your legal and compliance function early, not at the end. Discovering in week twelve that a feature design is incompatible with data residency requirements is expensive. Discovering it in week two is a conversation.

**The Core Tension**

Fast iteration and compliance are not opposites, but they are in tension. The resolution is not to pick one — it is to make compliance activities as automated, lightweight, and continuous as possible so they do not become a speed block.

**Common Mistakes**

- Treating compliance as a pre-launch checklist rather than a continuous quality property
- Building the audit trail manually, then finding it cannot scale with the product
- Assuming the regulator will be lenient with a startup — some are, some are not

**Related Anti-Patterns:** [The Deferred Compliance](STRATEGY-ANTI-PATTERNS.md#the-deferred-compliance)

---

### Edge Case D — Mature Automation, No Observability

**The Setup**

The team has a comprehensive, reliable test suite. CI/CD is working. The pipeline is green. But production incidents keep happening — bugs that were not caught in testing, performance degradations under real load, failures that only occur at specific data states or user volumes.

**The Risk Profile**

The primary risk is the assumption that a green CI pipeline equates to production quality. It does not. The CI pipeline tests what you predicted would fail. Production surfaces what you did not predict. The gap between the two is closed by production observability — not by adding more tests.

**The Strategy Decision**

1. Build a production quality signal layer. Structured logging, distributed tracing, error rate monitoring, and SLO-based alerting tell you how the system behaves under real conditions. These are not an operations concern — they are a quality concern.
2. Add synthetic monitoring for critical production journeys. A synthetic probe that exercises the most critical user flows on a schedule against the live system will catch production regressions that the CI pipeline cannot. It should be part of the quality strategy.
3. Use production data to improve test coverage. Error logs and support tickets from production are a map to the test gaps. Any defect found in production that was not caught by the test suite is a signal about what the test suite is missing.
4. Define an error budget and treat burning it as a quality incident. If the system is allowed a certain error rate (e.g. 0.1% of requests), spending that budget in three days is a quality event with a root cause to investigate, not just an operations metric.

**The Core Tension**

Testing is a prediction about what will fail. Observability is a measurement of what does fail. Both are part of a complete quality strategy. Teams that focus exclusively on the prediction side and not the measurement side produce a false sense of quality assurance.

**Common Mistakes**

- Treating a green CI pipeline as a quality assurance guarantee for production
- Discovering production defects through customer support tickets rather than monitoring
- Not feeding production defects back into the CI/CD test suite

**Related Anti-Patterns:** [The Fake Green](STRATEGY-ANTI-PATTERNS.md#the-fake-green)

---

### Edge Case E — High Team Turnover / Knowledge Fragility

**The Setup**

The team has significant churn. The people who built the automation — who understand the test architecture, the data setup, the environment assumptions, the fragile hacks — are no longer present. Tests break when changes are made and the cause is not clear. New team members cannot contribute to the test suite without a long ramp-up period.

**The Risk Profile**

The primary risk is maintenance paralysis — the test suite has high inherent value but is practically unusable without specialised knowledge. The team defaults to skipping or ignoring the suite rather than fixing it, which is how automation debt accumulates into a system that provides no real quality signal.

**The Strategy Decision**

1. Prioritise simplification over expansion. The most valuable thing a team in this situation can do is to make the existing suite understandable and maintainable by any reasonably competent engineer. Reduce abstractions. Eliminate cleverness. Make the data setup visible and self-contained.
2. Document the architecture, not the individual tests. A single, well-maintained architecture guide that explains how the test suite is organised, what each layer tests, how environments work, and how data is managed is more valuable than inline comments on individual test files.
3. Make each test self-contained where possible. Tests that depend on other tests, shared state, or undocumented setup conditions are brittle by design. Refactor the highest-priority tests to be independently runnable with visible setup.
4. Add a test for the test infrastructure. The most important automation reliability metric is whether a new team member can check out the repository and run the full test suite without external help. Test that. Make it a team definition of done.

**The Core Tension**

There is pressure to add coverage. The right answer is to stop adding coverage until what you have is maintainable. A maintainable, smaller suite is more valuable than a large, opaque one that nobody can change.

**Common Mistakes**

- Continuing to add tests to a suite that is already unmaintainable, increasing the debt
- Treating maintainability as a future concern rather than an active quality criterion
- Not capturing the architectural knowledge before the people who hold it leave

---

### Edge Case F — Multiple Parallel Streams (Mergers, Platform Migrations)

**The Setup**

Two products are being merged, or a legacy system is being re-platformed alongside the running production system. Two separate codebases exist simultaneously. Two test suites exist, possibly with different tooling, different conventions, and different coverage. Teams may be running CI/CD pipelines in parallel, with no shared quality gate.

**The Risk Profile**

The primary risk is convergence conflicts — changes in one stream break behaviour in the other, and the disconnect is not caught until integration. The secondary risk is premature rationalisation of the test suites — merging them before the underlying systems are actually converged, which creates a combined test suite that is wrong for both systems.

**The Strategy Decision**

1. Define the target state explicitly and anchor all quality decisions to it. What does the merged or migrated system look like? What is the test architecture for the target state? Every quality decision in the transition period should be evaluated against whether it moves towards or away from that target.
2. Keep the two test suites separate until the underlying systems are converged. Merging the test suites prematurely is technically complex and often counterproductive. The right time to merge is when there is something merged to test.
3. Define an integration verification layer that tests both systems against a shared contract. This is not the full test suite of either system — it is a smaller set of boundary tests that confirms the integration between the two.
4. Be explicit about which system is canonical for each piece of behaviour during the transition. Ambiguity about whether System A or System B is authoritative for a given domain is the source of most quality problems in migration and merger projects.

**The Core Tension**

There is pressure to consolidate quickly. The right answer is to consolidate deliberately, with a clear plan for when each piece merges and a quality gate for each step. Rushing the consolidation typically produces a merged system that has the defects of both originals while preserving the test coverage of neither.

**Common Mistakes**

- Merging test suites before the underlying systems are converged
- Not having an integration verification layer that covers the boundary between the two systems
- Allowing both teams to make assumptions about shared behaviour without a shared contract

---

### Edge Case G — UI-Heavy Legacy + API Modernisation In Flight

**The Setup**

A legacy system has a large, brittle UI automation suite. The team is adding an API layer as a modernisation initiative. The UI automation team and the API automation team are working in parallel, with limited coordination. The risk is that the API layer is used to duplicate the same test coverage that the UI layer already has, rather than to displace it.

**The Risk Profile**

The primary risk is duplication — the same business logic being tested at both the UI and API layers simultaneously. This multiplies maintenance cost without increasing coverage quality. The secondary risk is incoherence — two independently structured test suites that use different data models, different environment assumptions, and different naming conventions, making them practically impossible to consolidate later.

**The Strategy Decision**

1. Define layer ownership before both teams start building. The API layer tests the business logic and the service contracts. The UI layer tests the user journey and the presentation logic. There should be minimal overlap. Any scenario where both layers are testing the same underlying behaviour should be an explicit decision with a justification.
2. Sequence the parallel workstreams to minimise duplication. Where the API layer will eventually carry the confidence for a given behaviour, deprioritise the UI automation for that behaviour — do not build it if the API coverage is coming.
3. Define a convergence plan. At some point, the UI automation suite should be smaller than it is today, because the API layer has displaced its value in the areas where it operates more cheaply and reliably. Name that end-state. Track the transition.
4. Use the API layer to improve the UI test suite indirectly. If the API layer tests the business logic, the UI tests can focus on the user journey without needing to cover every edge case of the business logic. This makes both suites smaller and more targeted.

**The Core Tension**

Two teams building in parallel will default to building independently. Coordination cost is real. But the absence of coordination produces a combined test estate that is larger, more expensive, and less coherent than either team intended. A small amount of architecture alignment early saves a large amount of rationalisation cost later.

**Common Mistakes**

- Building the API test suite as a mirror of the existing UI test suite
- Not establishing layer ownership conventions before both teams are already building
- Treating the two suites as permanently separate rather than as a transition state toward a coherent target

---

### Edge Case H — Incomplete or Contradictory Requirements

**The Setup**

Requirements are incomplete, ambiguous, or actively contradictory. Different stakeholders have different understandings of what the system should do. The source of truth changes frequently. The team is being asked to test a system whose correct behaviour is not agreed.

**The Risk Profile**

The primary risk is building automation against requirements that change, then maintaining the automation rather than delivering coverage. Automation written on unstable requirements is not an investment — it is waste that creates ongoing maintenance cost and may be testing the wrong behaviour.

The secondary risk is producing a test strategy that gives false confidence. A comprehensive test suite for an incompletely specified system may be passing tests that test the wrong thing.

**The Strategy Decision**

1. Automate only what is stable, agreed, and unlikely to change in the near term. Use the automation viability check: is this behaviour stable? Is it agreed by all relevant stakeholders? Is it high-value? If the answer to any of these is no, manual testing is the correct approach until stability arrives.
2. Focus automation investment on the non-negotiable core. There is almost always a subset of the system behaviour that is agreed and stable — the core business transactions, the authentication flow, the regulatory-required processes. Start there.
3. Use exploratory testing and structured review sessions for the contested or unstable areas. These are better suited to rapidly changing, ambiguous requirements than automation is.
4. Make the assumptions in your test strategy visible. Where the strategy depends on a requirement that is contested or incomplete, name it explicitly. This is not a weakness in the strategy; it is honesty that protects the team from being held accountable for coverage of requirements that were not agreed.

**The Core Tension**

There is pressure to show testing progress. Writing new automation is visible progress. The right answer is to resist automating unstable requirements, even when it looks slower, because the maintenance cost will be paid with interest.

**Common Mistakes**

- Automating everything and maintaining a large, constantly-changing suite instead of stable, high-value coverage
- Not documenting which requirements were contested or incomplete when the test strategy was written
- Treating test coverage of an unstable requirement as the same quality signal as coverage of a stable one

**Related Anti-Patterns:** [The Automation First Fallacy](STRATEGY-ANTI-PATTERNS.md#the-automation-first-fallacy)
