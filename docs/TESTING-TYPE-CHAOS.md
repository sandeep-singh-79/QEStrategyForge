# Testing Type Deep-Dive: Chaos and Resilience Testing

Last Updated: 2026-04-09

## What This Document Is For

This is a full treatment of chaos and resilience testing — what it is, why it matters, the maturity prerequisites for using it responsibly, the techniques and tools involved, and where it fits relative to other testing types. Read it when you are designing a strategy for distributed systems, cloud-native platforms, or any system with high availability requirements where failure of individual components is plausible and expected.

---

## What Chaos and Resilience Testing Is

Chaos testing is the practice of deliberately injecting failures, faults, and unexpected conditions into a system — and observing whether it behaves as intended under those conditions.

The core premise is that failures in production are not edge cases. In any sufficiently large or complex system, individual components will fail — network calls will time out, instances will crash, dependencies will become unavailable, CPUs will spike. The question is not whether these failures will occur. The question is: when they do, how does the system behave?

Resilience testing is the broader category. Chaos testing is one technique within it. Resilience testing encompasses all testing that validates the system's behaviour under adverse conditions — not just injected failures, but also degraded dependencies, resource constraints, network partitions, and latency introduction.

---

## Why This Matters Strategically

Traditional testing verifies what the system does when everything works correctly. Resilience testing verifies what the system does when things go wrong.

In a monolithic application, failures are often binary: the application is up or it is down. In a distributed system, failures are partial: one of twelve services is slow, or intermittently unavailable, or returning malformed responses. The distributed system must be designed to tolerate these partial failures gracefully — to degrade rather than collapse, to recover rather than require manual intervention.

The business risk is: a distributed system that has not been tested for resilience may appear healthy in CI/CD but have undetected failure modes that produce cascading outages, silent data corruption, or customer-facing errors under real-world conditions.

---

## Prerequisites: When Chaos Testing Is Appropriate

Chaos testing is not appropriate for all teams and all systems. Before introducing chaos testing, the following conditions should hold:

### Prerequisite 1: The System Has Baseline Observability

Chaos testing produces value only if you can observe the system's behaviour during the experiment. Without metrics, structured logging, distributed tracing, and alerting, you are running experiments that produce no visible results. The prerequisite is not advanced observability — it is basic visibility into health, errors, and latency.

### Prerequisite 2: The Steady State Is Defined and Measurable

Before injecting failures, you must be able to describe what "normal" looks like — what the system's expected error rate, latency, throughput, and health indicators are under normal load. Chaos experiments test deviation from this steady state. Without a defined steady state, you have no baseline to compare against.

### Prerequisite 3: The Team Has a Hypothesis

A chaos experiment without a hypothesis is not an experiment — it is random fault injection. Every experiment should be preceded by a statement of the form: "We believe that if [fault condition], the system will [expected behaviour]. We will measure [observable indicator] to verify this."

### Prerequisite 4: Blast Radius Is Limited and Recoverable

Chaos experiments should begin in isolated, non-production environments. When run in production, they should be carefully scoped to limit the impact to a small percentage of traffic, and they should be immediately reversible.

Teams that do not yet have the observability, defined steady state, or recovery mechanisms to run experiments safely should not run chaos experiments in production. Start in staging.

---

## The Kinds of Faults Worth Injecting

### Resource Faults
- **CPU spike**: simulate a process competing for CPU, causing the application to slow
- **Memory pressure**: simulate high memory utilisation or a memory leak condition
- **Disk fill**: simulate storage capacity exhaustion

### Network Faults
- **Network latency**: add artificial latency to a service dependency (e.g. 200ms added to all calls to the payment service)
- **Packet loss**: drop a percentage of packets between services
- **Network partition**: completely block network access between two services
- **DNS failure**: make a service's DNS resolution fail intermittently

### Service Faults
- **Instance termination**: kill one or more instances of a service
- **Container crash**: crash a container without warning
- **Process hang**: make a service unresponsive (accepting connections but not processing them — the socket stays open but no response comes)
- **Dependency unavailability**: make a downstream service return 503 or time out entirely

### Data Faults
- **Malformed response injection**: make a dependency return a structurally incorrect response (wrong schema, missing fields, wrong content type)
- **Slow response injection**: make a dependency respond very slowly (not time out — just very slow)
- **Partial failure injection**: make a percentage of calls to a dependency fail while others succeed

---

## What Resilience Testing Validates

For each fault type, you are validating specific resilience properties:

| Fault | Resilience Property Being Validated |
|---|---|
| Instance termination | Does the system reroute traffic correctly? Do replicas absorb the load? Does autoscaling add capacity? |
| Dependency latency | Does the timeout fire correctly? Does the fallback or circuit breaker activate? Does the caller fail fast or wait indefinitely? |
| Dependency unavailability | Does the circuit breaker open and prevent cascading load? Does the system degrade gracefully (serve cached data, reduce functionality) rather than failing completely? |
| Malformed response | Does the parsing layer handle unexpected shapes without crashing? Are appropriate errors returned to the caller? |
| Network partition | Can the system partition correctly, maintaining availability for independent concerns while unavailable for the partitioned concern? |
| Memory pressure | Does the system remain stable or does it degrade? Do GC pauses affect latency significantly? |

---

## The Experiment Structure

Every chaos experiment should follow this structure:

### 1. Define the steady state

What does normal look like? Name the specific metrics and their acceptable ranges:
- p95 response time < 150ms
- Error rate < 0.1%
- All health checks returning 200
- No alerts firing

### 2. State the hypothesis

"We believe that if we terminate one of three application instances, the load balancer will reroute traffic within 10 seconds, p95 latency will remain under 250ms during the rerouting period, and the error rate will not exceed 0.5% for longer than 15 seconds."

### 3. Define the blast radius and rollback procedure

Which services or components will the fault be injected into? What percentage of traffic will be affected? How is the fault reversed immediately if needed?

### 4. Run the experiment

Inject the fault. Observe the system through the defined metrics. Record what happens — both what was expected and what was not.

### 5. Restore and debrief

Remove the fault. Observe recovery. Document: did the hypothesis hold? What was observed that was unexpected? What follow-up experiments or fixes are warranted?

---

## Game Days

A game day is a planned, team-wide resilience exercise — a structured event where the team runs a set of pre-planned chaos experiments together, observing and responding as if it were a real incident.

Game days serve multiple purposes:
- They surface failure modes that individual experiments might not because they combine multiple fault types
- They test the team's incident response procedures, communication, and tooling under controlled conditions
- They build team familiarity with failure modes before they occur in production

A game day proceeds from a scenario definition: "Today we are simulating the loss of our primary database region." The team runs the defined fault injections, observes the system, and exercises their runbooks. The debrief identifies what worked, what did not, and what needs to change.

---

## Chaos in CI/CD vs. Chaos in Production

### Chaos in Lower Environments (CI/CD, Staging)

This should be the starting point. Inject faults into staging or integration environments as part of the release pipeline. A resilience gate before promotion to production verifies that key failure scenarios are handled correctly.

Examples of resilience checks that can run in CI/CD:
- Kill one instance during a load test and verify traffic reroutes within the SLA
- Introduce 500ms latency on a downstream service and verify circuit breaker activates
- Return 503 from a dependency and verify fallback behaviour

### Chaos in Production (Controlled, Limited)

For mature teams with strong observability and blast-radius controls, controlled production chaos experiments provide the highest confidence — because they are testing the real system under real traffic. The key controls are: start with low-blast-radius experiments, always have a clear rollback procedure, always run during business hours with the on-call team present, and stop the experiment immediately if the system behaves unexpectedly.

**Key tooling for production chaos:** Chaos Monkey (Netflix), AWS Fault Injection Simulator, Azure Chaos Studio, LitmusChaos (Kubernetes), Gremlin.

---

## Common Mistakes

- Running chaos experiments without confirming the steady state first. Without a baseline, you cannot interpret the results.
- Running experiments without a hypothesis. Random fault injection tells you what happened; a hypothesis tells you whether what happened was expected.
- Starting in production before establishing the pattern in staging. Always run the experiment in a lower environment first.
- Not having a clear rollback procedure. If an experiment causes unexpected behaviour, you must be able to stop it and restore the system immediately.
- Treating a passed chaos experiment as a permanent assurance. The system changes with every deployment. Chaos experiments should be repeated regularly, not treated as one-time validations.
- Conflating chaos testing with stress testing. Stress testing pushes load to the limit. Chaos testing injects specific, realistic failure conditions at normal or moderate load.

---

## What Good Looks Like

- Resilience experiments run in staging as part of the release pipeline
- A library of experiments with recorded results that grows over time
- Game days conducted before significant production changes
- Production chaos experiments run with blast-radius controls and monitoring
- Every production incident that reveals a new failure mode triggers a new chaos experiment to prevent future recurrence
- The team can describe, from a defined catalogue, which failure modes the system is known to handle correctly

---

## What Bad Looks Like

- No resilience testing at all — the first discovery of how the system behaves under failure conditions is a production incident
- Chaos experiments run by one person, results not shared, insights not acted on
- Chaos testing undertaken at a team's request but without the observability infrastructure to interpret results
- Chaos experiments run without a hypothesis, producing observations with no quality gate

---

## Related Situations

- [Situation 6 — Microservices / Distributed System](SITUATIONS-CATALOGUE.md#situation-6--microservices--distributed-system)
- [Situation 7 — High-Frequency Release Cadence](SITUATIONS-CATALOGUE.md#situation-7--high-frequency-release-cadence-cicd-native)
- [Situation 12 — Performance-Critical System](SITUATIONS-CATALOGUE.md#situation-12--performance-critical-system-trading-real-time-high-volume)
- [Edge Case D — Mature Automation, No Observability](SITUATIONS-CATALOGUE.md#edge-case-d--mature-automation-no-observability)
