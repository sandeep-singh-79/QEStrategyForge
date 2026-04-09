from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable


@dataclass(slots=True)
class GenerationRequest:
    prompt: str
    model: str
    max_tokens: int = 4096


@dataclass(slots=True)
class GenerationResponse:
    text: str
    model: str


@runtime_checkable
class LLMClient(Protocol):
    """Minimal provider-agnostic interface for text generation."""

    def generate(self, request: GenerationRequest) -> GenerationResponse:
        ...


# ---------------------------------------------------------------------------
# Fake client for deterministic testing
# ---------------------------------------------------------------------------

_FAKE_STRATEGY = """\
## Executive Summary
Strategy Confidence: standard
This strategy is tailored for a test engagement with a focus on quality improvement.

## Engagement Context
Project Posture: brownfield
Delivery Model: Agile
System Type: microservices
Critical Business Flows: test flow
Key Constraints: none

## Quality Objectives And Risk Priorities
Primary Quality Goal: regression stability
Business Goal: reduce defect escape rate
Risk Priorities: none
Compliance Focus: none

## Lifecycle Posture
Shift-Left Stance: moderate
Shift-Right Stance: selective where production signals are available
Prevention vs Detection Balance: prevention first where feasible
Lifecycle Checkpoints: requirements -> design -> build -> integration -> release readiness

## Layered Test Strategy
Layering Priority: balanced
System Profile: api_first
Recommended Coverage Layers: unit / component / integration / API / UI / regression

## Test Types And Coverage Focus
Functional Coverage: critical business flows and high-risk integrations
Regression Coverage: risk-based and posture-aware
Exploratory Coverage: targeted around uncertainty and legacy behavior
Non-Functional Priorities: performance, security, accessibility, and resilience

## Automation Strategy
Current Automation State: partial
Target Automation State: phased expansion
Automation Adoption Path: phased expansion
Brownfield Transition Strategy: assess_reuse_stabilize_retire_replace
CI/CD Integration Target: pipeline quality gates scaled to maturity

## CI/CD And Quality Gates
Current CI/CD Maturity: partial
Target CI/CD Posture: progressive_gates
Pipeline Quality Gates: smoke, critical-path, and risk-based checks
Release Decision Guidance: use explicit quality signals

## Test Data Strategy
Test Data Approach: synthetic datasets for non-production environments

## Environment Strategy
Environment Stability: controlled environments with stable configurations

## Defect, Triage, And Reporting Model
Defect Model: risk-based triage with severity classification
Reporting Emphasis: medium

## AI Usage Model
AI Adoption Posture: cautious
Human Review Boundaries: QE lead review required for AI-assisted test outputs
AI Tooling: limited to low-risk test generation assistance

## Assumptions, Gaps, And Open Questions
Missing Information: none
Strategy Confidence Note: based on provided context

## Recommended Next Steps
Recommended Immediate Actions: validate current-state evidence
"""


class FakeLLMClient:
    """Deterministic LLM client for tests. Always returns a structurally valid strategy."""

    def generate(self, request: GenerationRequest) -> GenerationResponse:
        return GenerationResponse(text=_FAKE_STRATEGY, model=request.model)
