# Testing Type Deep-Dive: Contract Testing

Last Updated: 2026-04-09

## What This Document Is For

This is a full treatment of contract testing as a strategy layer — what it is, when it is necessary, how it differs from integration testing, how to implement it, and the tradeoffs it carries. Read it when you are designing a strategy for a distributed system, a microservices architecture, or any system where service boundaries cross team ownership lines.

---

## What Contract Testing Is

A contract is an agreement about the interface between two systems: what the producer will provide, and what the consumer expects to receive. A contract test verifies that this agreement is being honoured.

Contract testing is not integration testing. This distinction matters.

| | Contract Testing | Integration Testing |
|---|---|---|
| **What it tests** | The interface agreement between two systems | The combined behaviour of the integrated systems |
| **Where it runs** | In each system's own pipeline, independently | In a shared integration environment |
| **What it requires** | No live dependencies | Both (or all) systems running together |
| **Feedback speed** | Fast — part of the unit-test layer | Slow — requires environment coordination |
| **What it catches** | Breaking interface changes | Combined runtime failures |
| **Who owns it** | Consumer and provider teams, independently | Usually a shared or platform QE function |

Both have a role. They are not substitutes for each other. Contract testing catches interface regressions early and cheaply. Integration testing catches runtime interactions that contract tests cannot simulate.

---

## Two Models for Contract Testing

### Consumer-Driven Contract Testing

In consumer-driven contract testing, the consumer defines what it needs from the producer. This definition — the contract — is published as a formal artefact. The producer's pipeline verifies that it satisfies every contract published by every consumer.

The canonical tool for this model is [Pact](https://pact.io). The consumer writes a test that records what it calls from the provider and what response it expects. Pact generates a contract file. The provider runs a verification against that file in its own test suite.

**When to use it:** When different teams own the consumer and the producer, and you need a formal mechanism to catch breaking changes before they reach shared environments. When providers change their APIs and consumers need to be confident they will not be broken without notice.

**Key properties:**
- The consumer defines the contract: this puts the contract closest to the party who cares about it
- The provider verifies independently: no shared environment needed for this check
- Contract changes produce explicit negotiation between teams: the consumer must update the contract, the provider must re-verify

**What it does not catch:** Runtime integration failures, environment-specific behaviour, authentication and authorisation flows that only exist in a live deployment, performance under real load.

### Provider-Side Schema Validation

Where consumer-driven contracts are impractical (e.g. public APIs with many consumers), schema validation is the practical alternative. The provider publishes an OpenAPI or JSON Schema specification. Consumer pipelines validate their actual request and response parsing against that schema. Provider pipelines validate that actual responses conform to the schema.

**When to use it:** For public or widely-consumed APIs where consumer-driven contract negotiation is not practical. When the provider has an existing OpenAPI spec and the goal is to prevent schema drift.

---

## What Contract Testing Catches

A contract test answers the question: "If I call the provider in the way I currently do, will it respond in the way I currently expect?"

It catches:
- Fields removed from a response that the consumer depends on
- Fields renamed or moved to a different nesting level
- Data type changes (e.g. a numeric ID becoming a string)
- Required request fields added by the provider
- Status code changes for known request patterns
- Enum values removed or renamed

It does not catch:
- Business logic errors inside the provider
- Failures caused by real data the contract test did not simulate
- Performance regressions
- Authentication expiry or token format changes (unless explicitly included in the contract)
- Side effects — a provider that accepts a request correctly but writes wrong data to its database

---

## The Most Common Failure Mode

Teams treat contract testing as optional, rely on integration testing to catch interface regressions, and then discover that:

1. Integration tests are too slow to run on every commit
2. Integration environments are unstable and cannot be relied upon for fast feedback
3. A provider team changes their API, the change is not caught in the provider's pipeline, and it reaches production where it breaks consumers

The cost of this pattern compounds as the number of service boundaries grows. In a system with ten services and thirty integration points, the probability that one of those points is broken at any given moment approaches certainty without a contract layer.

---

## Where Contract Tests Fit In The Pipeline

```
Developer commits code
     |
     v
Unit tests (< 2 min)
     |
     v
Contract tests — consumer-side: regenerate Pact contracts (< 2 min)
     |
     v
Contract tests — provider-side: verify all known consumer contracts (< 3 min)
     |
     v
[Contracts published to Pact Broker or equivalent]
     |
     v
Integration tests (shared environment, slower cadence)
```

The key property is that contract verification runs inside each service's own pipeline, against its own dependencies, without a shared running environment. This is why it is fast, reliable, and scalable.

---

## What Good Looks Like

- Every service that consumes another service has a published contract
- Provider pipelines verify all consumer contracts before merging to their main branch
- Contract changes are an explicit PR — not a silent deployment
- When a provider needs to make a breaking change, the workflow is: notify consumers, negotiate, consumers update their contracts and verify with the new version, provider merges
- The Pact Broker (or equivalent) shows the compatibility matrix across all services at a glance

---

## What Bad Looks Like

- Contracts exist for some service pairs but not others — leaving the uncovered boundaries as silent regression risk
- Provider teams do not run contract verification in their pipeline — contracts become stale and trust in them erodes
- Contracts cover only the happy path — error response shapes are undocumented and break silently
- Teams add integration tests to cover what contract tests should cover, then complain that integration tests are too slow

---

## When Contract Testing Is Not The Right Answer

- Small systems with a single consumer of every service: the overhead of consumer-driven contracts is not justified if you are the only consumer. Schema validation is sufficient.
- Teams that share a codebase or deployment unit: if two services are always deployed together and owned by the same team, the value of a formal contract between them is low.
- Early-stage products where service interfaces are changing weekly: contract testing is most valuable when interfaces are relatively stable. In a very early product, the contract maintenance overhead may exceed the value.

---

## Key Vocabulary

| Term | Meaning |
|---|---|
| **Consumer** | The service that calls another service and depends on its response |
| **Provider** | The service that receives requests and returns responses |
| **Contract** | A formal description of what the consumer requests and what it expects in response |
| **Pact file** | A JSON file generated by a Pact consumer test, describing the recorded interaction |
| **Pact Broker** | A shared server that stores contracts and tracks provider verification status |
| **Provider verification** | The provider running its own test against a consumer's Pact file to confirm it satisfies the contract |
| **Consumer-driven** | The consumer defines the contract; the provider's obligation is to satisfy it |

---

## Related Situations

- [Situation 6 — Microservices / Distributed System](SITUATIONS-CATALOGUE.md#situation-6--microservices--distributed-system)
- [Situation 10 — Third-Party Integration Heavy](SITUATIONS-CATALOGUE.md#situation-10--third-party-integration-heavy)
