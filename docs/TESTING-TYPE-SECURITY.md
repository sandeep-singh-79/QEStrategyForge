# Testing Type Deep-Dive: Security Testing in the Pipeline

Last Updated: 2026-04-09

## What This Document Is For

This is a full treatment of security testing as a quality layer — what the distinct types are, where each fits in the delivery pipeline, what each catches, and how to build a security testing strategy that is continuous rather than periodic. Read it when you are designing a strategy for any system that handles sensitive data, operates in a regulated domain, or is exposed to the internet.

---

## Why Security Testing Is a Pipeline Concern, Not a Pen-Test-Once Concern

The traditional model of security testing is: build the system, then bring in a security specialist near release to run a penetration test. This model has several failure modes:

1. **Findings arrive late.** Remediating a security vulnerability discovered two weeks before a release is expensive, stressful, and sometimes causes the release to slip.
2. **The test cadence does not match the delivery cadence.** A annual or quarterly pen test cannot keep up with a team delivering weekly or daily.
3. **The pen test covers the state of the system on a single day.** New vulnerabilities introduced in the following sprint are not covered until the next pen test.
4. **Teams treat passing the pen test as the security posture.** It is not — it is a point-in-time snapshot.

A modern security testing strategy embeds security checks into the delivery pipeline at multiple points, so vulnerabilities are caught as close to their introduction as possible.

---

## The Four Layers of Pipeline Security Testing

### Layer 1 — SAST: Static Application Security Testing

**What it is:** Analysis of source code or compiled artefacts for known vulnerability patterns, without executing the code.

**What it catches:**
- SQL injection and command injection patterns
- Cross-site scripting (XSS) vulnerabilities in web application code
- Hardcoded credentials, API keys, or secrets in source code
- Insecure cryptography usage (e.g. MD5, SHA1 as password hashes)
- Deserialization vulnerabilities
- Path traversal patterns
- OWASP Top 10 patterns that are statically detectable

**What it does not catch:**
- Vulnerabilities that only exist at runtime (e.g. a privilege escalation that depends on the user's current token)
- Business logic flaws (e.g. a pricing logic error that allows negative orders)
- Infrastructure configuration issues
- Vulnerabilities introduced by runtime behaviour of dependencies

**Where it fits in the pipeline:** Build stage. On every commit. SAST results should gate the build for high-severity findings. Medium findings should produce warnings that are tracked and resolved within a defined timeframe.

**Key tools:** Semgrep, SonarQube, Checkmarx, CodeQL (GitHub Actions), Bandit (Python), SpotBugs (Java).

**Common mistake:** Running SAST weekly or as a gate only on main branch. By the time a finding reaches main, it may have been in the codebase for days. Run on every commit to every branch.

---

### Layer 2 — SCA: Software Composition Analysis

**What it is:** Analysis of third-party dependencies (libraries, packages, containers) for known vulnerabilities listed in public CVE databases.

**What it catches:**
- Known CVEs in direct dependencies (packages you explicitly depend on)
- Known CVEs in transitive dependencies (packages your packages depend on)
- License compliance issues (dependencies with licences incompatible with the project's licence)
- Outdated packages with known security patches available

**What it does not catch:**
- Zero-day vulnerabilities not yet in the CVE database
- Vulnerabilities in your own code
- Runtime configuration vulnerabilities

**Where it fits in the pipeline:** On every dependency change (package update PR or lock file change). Also runs on a scheduled basis (weekly at minimum) to catch newly-disclosed CVEs in existing dependencies that were clean when first added.

**Key tools:** Dependabot (GitHub), Snyk, OWASP Dependency-Check, Trivy (for container images), pip-audit (Python).

**Common mistake:** Only running SCA when dependencies are updated. A package that was clean when added can accumulate CVEs months later as new vulnerabilities are disclosed. Scheduled scanning is necessary.

**On dependency scanning and the security invariant:** Dependencies with critical or high CVEs should block release. This is a security invariant — not a preference. The only acceptable exception is a documented, time-limited risk acceptance with a named remediation plan.

---

### Layer 3 — DAST: Dynamic Application Security Testing

**What it is:** Testing the running application by sending malicious or unexpected inputs and observing how it responds. Unlike SAST, DAST tests the application from the outside, as an attacker would.

**What it catches:**
- Injection vulnerabilities (SQL, command, LDAP, XPath) that are exploitable in the running application
- Authentication and session management weaknesses
- Security misconfigurations (exposed debug endpoints, verbose error messages, directory listing)
- SSL/TLS configuration weaknesses
- Broken access controls (endpoints accessible without proper authentication)
- Sensitive data exposure in responses, headers, or error messages

**What it does not catch:**
- Vulnerabilities in code paths that DAST's automated scan does not exercise
- Business logic flaws (DAST is not aware of the application's intended business behaviour)
- Client-side only vulnerabilities (some DAST tools have limited JavaScript rendering)

**Where it fits in the pipeline:** Not on every commit — DAST is heavier and requires a deployed, running environment. Run DAST against the staging environment on every significant release, and on a scheduled weekly basis against staging.

**Key tools:** OWASP ZAP, Burp Suite (manual and automated), Nikto, Nessus.

**Common mistake:** Running DAST only as a manual tool operated by a security specialist. DAST can be automated — ZAP, for example, has a CI/CD pipeline mode. Baseline automated DAST scans should be a routine pipeline step, not an occasional manual exercise.

---

### Layer 4 — Manual Penetration Testing

**What it is:** A human security specialist attempts to exploit the application using the same techniques and mindset as an attacker. This includes automated tooling, but the value is in the specialist's judgment, creativity, and domain expertise.

**What it catches:**
- Business logic vulnerabilities that automated tools cannot detect because they require understanding the application's intent
- Chained exploits: sequences of individually low-severity findings that combine to produce high-severity impact
- Authentication and authorisation bypasses that require understanding the user access model
- Application-specific attack vectors unique to the domain (e.g. financial fraud patterns in a payment system)
- Social engineering vectors and procedural weaknesses

**What it does not catch:** Everything that was introduced after the test date. Pen testing is a point-in-time activity, not a continuous one.

**Where it fits in the pipeline:** Before significant releases (major version, new module). At least annually for systems handling highly sensitive data. After significant architecture changes.

**On pen test findings:** Every pen test finding should produce two outputs: a remediation in the code, and a regression test that would have caught the finding. This is how the automated security test estate grows from real-world findings rather than theoretical templates.

---

## Security Testing in the Functional Test Suite

SAST, SCA, DAST, and pen testing are not a substitute for security test cases in the functional test suite. The functional suite should include:

**Authentication boundary tests:**
- Unauthenticated requests to authenticated endpoints return 401
- Requests with expired tokens return 401
- Requests with valid tokens for the wrong scope or role return 403
- Token reuse after logout is rejected

**Authorisation matrix tests:**
- User A cannot access User B's data
- A user with role X cannot perform actions restricted to role Y
- Cross-tenant data access is blocked

**Input validation tests:**
- Malformed inputs (too long, wrong type, boundary values) are rejected with the correct status code and do not produce stack traces
- SQL metacharacters in input fields do not cause database errors
- Script tags in text input fields are not reflected unescaped in responses

**Sensitive data tests:**
- Payment card numbers, SSNs, health record identifiers are not logged in plain text
- Sensitive fields are absent from responses to roles that should not see them
- Error responses do not include stack traces, internal paths, or version information

---

## The Security Testing Matrix

| Layer | What It Tests | Pipeline Position | Cadence |
|---|---|---|---|
| SAST | Source code patterns | Build stage | Every commit |
| SCA | Dependency CVEs | PR stage + scheduled | Every dependency change + weekly |
| Functional security tests | Auth/authz/validation | Test stage | Every commit |
| DAST | Running application | Staging deployment | Every significant release + weekly |
| Pen test | Business logic + chained exploits | Pre-release | Major releases + annual |

---

## What a Mature Security Testing Strategy Looks Like

- SAST gates the build for high-severity findings on every commit
- SCA gates dependency update PRs for critical/high CVEs
- Security scenarios (auth, authz, input validation, sensitive data) are in the main test suite, not a separate repository
- DAST runs against staging on every release and on a weekly schedule
- Pen test findings are converted into automated regression tests after remediation
- The security test estate grows over time, driven by actual findings

---

## What a Weak Security Testing Strategy Looks Like

- Annual pen test is the primary security assurance mechanism
- SAST runs as a reporting tool only — findings are noted but do not gate anything
- No security test cases in the functional test suite
- SCA is not running; vulnerable dependencies are discovered through CVE notifications or production incidents
- Pen test findings are remediated but not converted into regression tests

---

## Key Vocabulary

| Term | Meaning |
|---|---|
| **CVE** | Common Vulnerabilities and Exposures — a public database of known security vulnerabilities |
| **OWASP Top 10** | A regularly-updated list of the ten most critical web application security risks |
| **Attack surface** | The set of interfaces, endpoints, and entry points through which an attacker could attempt to compromise the system |
| **Threat modelling** | A structured exercise to identify what can go wrong from a security perspective before testing begins |
| **Security invariant** | A security property that must always hold — an API key never in a config file, a CVE above a threshold always blocking release |
| **HITL** | Human in the loop — a person reviews or approves before an action is taken |

---

## Related Situations

- [Situation 5 — High-Regulation Domain](SITUATIONS-CATALOGUE.md#situation-5--high-regulation-domain)
- [Situation 11 — Security-First Domain](SITUATIONS-CATALOGUE.md#situation-11--security-first-domain-fintech-healthtech-deftech)
