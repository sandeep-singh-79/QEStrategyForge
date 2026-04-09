# Testing Type Deep-Dive: Performance Testing

Last Updated: 2026-04-09

## What This Document Is For

This is a full treatment of performance testing as a strategy layer — the distinct test types, what each one answers, when each is necessary, how they are structured, and the common mistakes teams make by conflating them. Read it when you are designing a strategy for any system with explicit SLAs, high-transaction-volume requirements, or stability obligations.

---

## Why Performance Testing Types Must Be Differentiated

Most teams use the term "performance testing" or "load testing" as a single category. In practice, there are at least five distinct test types, each answering a different question:

| Test Type | Core Question | Time Scale |
|---|---|---|
| **Load testing** | Does the system meet its SLAs at normal expected load? | Minutes to hours |
| **Stress testing** | At what load does the system break, and how does it fail? | Minutes to hours |
| **Spike testing** | How does the system respond to sudden, sharp increases in traffic? | Minutes |
| **Soak / Endurance testing** | Does the system remain stable over a sustained period? | Hours to days |
| **Scalability testing** | Does performance scale linearly (or better) as resources are added? | Variable |

Using only one of these — typically a load test — and calling it "performance testing" answers one of five questions while leaving the others unasked. A strategy that only runs load tests may never discover that the system has a memory leak (soak), degrades ungracefully under overload (stress), or falls over during a marketing campaign traffic spike (spike).

---

## Load Testing

### What It Is

A load test simulates the expected normal production load on the system — the number of concurrent users, the transaction rate, or the request volume that the system is designed to handle — and measures whether the system meets its performance SLAs under that load.

### What It Answers

- Does the system meet its p95 response time target at N concurrent users?
- Does the system's throughput meet its target at normal production volume?
- Are there any performance bottlenecks that are only visible under realistic concurrent usage?

### When It Is Necessary

Every production system with an explicit response time or throughput SLA. If no SLA exists, load testing cannot produce a pass/fail result — it can only produce measurements. Define the SLA first, then the load test.

### How To Run It

1. Define the user scenarios. Which flows will be exercised? In what proportions? A realistic load test mixes multiple transaction types in the proportions they occur in production — not just a single endpoint hit repeatedly.
2. Define the load profile. Ramp-up period (gradually increasing to target load), steady-state period (running at target load for long enough to observe stable behaviour), and ramp-down.
3. Define the pass/fail criteria before running the test. p95 response time, p99 response time, error rate, throughput. The results are only meaningful relative to a stated expectation.
4. Run the test in an environment that is representative of production in terms of hardware, configuration, and data volume. A load test against an under-provisioned staging environment is measuring the staging environment, not the production system.

### Common Mistakes

- Measuring average response time instead of percentiles. Averages hide the tail latency that affects real users. p95 and p99 are more meaningful.
- Running the test before defining the pass/fail criteria. This turns a validation test into a benchmarking exercise, which cannot produce a quality gate.
- Using a single-endpoint hit loop as the load profile. This does not simulate realistic concurrent usage patterns.
- Running against an environment that does not represent production and drawing production conclusions from the results.

---

## Stress Testing

### What It Is

A stress test pushes the system beyond its designed load — to the point of failure or degradation — to understand where the breaking point is and how the system behaves when it breaks.

### What It Answers

- At what load does the system stop meeting its SLAs?
- Does the system fail gracefully (predictable degradation, clear error messages, queue buildup) or catastrophically (crashes, data corruption, cascading failures)?
- After overload is removed, does the system recover on its own?

### When It Is Necessary

Any system where overload is possible and the consequences of catastrophic failure are significant. Financial systems, e-commerce platforms during peak events, booking systems. If you do not know where the breaking point is, you cannot reason meaningfully about capacity planning or incident response.

### How To Run It

Continue increasing load beyond the SLA target until the system degrades or breaks. The breaking point is defined as when the system fails to meet its SLAs, not when it crashes — it may degrade gracefully well before it crashes.

Observe: where does latency start climbing? Where does the error rate increase? Is the failure mode graceful (throttling, queuing) or catastrophic (process crash, data corruption)? After returning to normal load, how long does recovery take?

### Common Mistakes

- Running stress tests in production environments. The test is designed to break the system.
- Not observing the recovery behaviour after overload — recovery failure is a separate risk from the overload itself.
- Treating the breaking point as a fixed property. It changes with every significant code or infrastructure change.

---

## Spike Testing

### What It Is

A spike test subjects the system to a sudden, sharp increase in load — not a gradual ramp — and observes how the system responds to the instant change.

### What It Answers

- Can the system handle a sudden traffic surge (e.g. a marketing email blast, a news mention, a social media event)?
- Does the system recover to normal performance after the spike subsides?
- Are there failure modes that only appear at the transition point (the spike) rather than under sustained load?

### When It Is Necessary

Any system with variable traffic patterns where sudden spikes are plausible — consumer products, event-driven platforms, API-heavy systems where consumers retry aggressively after failures.

### How To Run It

Apply a step-change in load rather than a gradual ramp. The exact profile depends on the realistic spike shape for the system. Observe: does the system throttle, queue, or drop requests? How does latency behave during and after the spike? Does it recover fully?

### Common Mistakes

- Assuming load test results imply spike resilience. A system can perform well under gradually increasing load and fail under a sharp spike because of instantaneous connection pool exhaustion, autoscaler lag, or load balancer warm-up time.

---

## Soak / Endurance Testing

### What It Is

A soak test runs the system at a realistic (not extreme) load for an extended period — hours or days — to detect problems that only emerge over time: memory leaks, connection pool exhaustion, log file bloat, cache growth, thread accumulation, gradual response time degradation.

### What It Answers

- Is there a memory leak that manifests over hours of operation?
- Does performance degrade gradually with time even at normal load?
- Are there resource exhaustion issues that only appear after sustained operation?
- Does the system need to be restarted regularly to maintain normal performance?

### When It Is Necessary

Any system where memory management is non-trivial, connection pooling is used, caching is significant, or background processes accumulate state. In practice: most non-trivial production systems benefit from at least an occasional soak test, particularly after significant changes to the resource management layer.

### How To Run It

Run at 50–70% of the SLA load target for four to twenty-four hours. Monitor: heap memory growth, thread count, connection pool utilisation, response time trends, error rate. Any metric that trends upward over time rather than stabilising is a signal of a resource leak or accumulation problem.

### Common Mistakes

- Not running soak tests at all because they take too long and there is no dedicated environment. Memory leaks in production are the cost.
- Running soak tests for too short a duration. Some memory leaks only become visible after three or four hours of operation.
- Not establishing a stable baseline before the soak test. Without a baseline, there is no way to know whether the trends observed are expected or anomalous.

---

## Scalability Testing

### What It Is

A scalability test measures how performance changes when resources (instances, nodes, CPU, memory) are added or removed. It verifies that the system scales horizontally or vertically as intended, and identifies where the scale-limiting bottleneck is.

### What It Answers

- Does doubling the number of application instances double (or nearly double) the throughput?
- Where is the bottleneck that prevents linear scaling — the database, a shared cache, a synchronous integration?
- What is the most cost-effective resource configuration for a given SLA target?

### When It Is Necessary

Cloud-native systems where autoscaling is used. Systems that must handle variable load by adding resources dynamically. Cost optimisation exercises.

### Common Mistakes

- Assuming the system scales linearly without testing it. Amdahl's Law predicts that most systems have a fixed serial component that limits horizontal scale. The question is where the limit is.
- Testing scalability without a representative data set. Scalability bottlenecks often live in the database, and a small test data set will not reveal them.

---

## Performance Testing in the Pipeline

Performance tests are more expensive to run than functional tests. The strategy must balance coverage against pipeline speed:

```
Every commit (fast gate, < 5 min):
  - Baseline performance smoke: single-user, p95 response time assertion
    on the most critical API endpoints

Every merge to main (medium gate, 15-20 min):
  - Lightweight load test: 10-20% of SLA target load, duration 5-10 min
  - Assert: no regression vs. previous baseline

Every release to staging (full gate, hours):
  - Full load test at SLA target
  - Stress test to find breaking point
  - Spike test for traffic-variable systems
  - Results compared to previous release baseline

Weekly or release-cadence:
  - Soak test (4-24 hours)
  - Scalability test (when infrastructure changes are made)
```

---

## Defining Performance SLAs

Performance testing without SLAs cannot produce pass/fail results. Before writing a single performance test, define:

- **Concurrent user target:** how many simultaneous users must the system support?
- **Throughput target:** how many transactions per second (TPS) or requests per minute (RPM)?
- **Latency target:** what is the acceptable p95 response time? p99?
- **Error rate target:** what is the acceptable error rate under load (e.g. < 0.1%)?
- **Availability target:** what uptime is required? What is the error budget?

These targets are not technical decisions — they are business decisions about what is acceptable to users. They should be defined by the product and business stakeholders, validated against user research or competitive benchmarks, and agreed before performance testing begins.

---

## Key Vocabulary

| Term | Meaning |
|---|---|
| **p95 / p99** | The 95th / 99th percentile of response times — i.e. 95% / 99% of requests are faster than this value |
| **Throughput** | The rate at which the system processes requests, typically measured in RPS (requests per second) or TPS (transactions per second) |
| **Concurrent users** | The number of users simultaneously interacting with the system |
| **Think time** | Simulated pause between user actions, used to produce a realistic rather than a maximum-stress load profile |
| **Ramp-up** | The period at the start of a test during which load increases gradually to the target level |
| **Error budget** | The acceptable fraction of requests that may fail, often expressed as an SLO (Service Level Objective) |
| **Saturation point** | The load level at which the system's performance starts to degrade |

---

## Related Situations

- [Situation 12 — Performance-Critical System](SITUATIONS-CATALOGUE.md#situation-12--performance-critical-system-trading-real-time-high-volume)
- [Situation 7 — High-Frequency Release Cadence](SITUATIONS-CATALOGUE.md#situation-7--high-frequency-release-cadence-cicd-native)
