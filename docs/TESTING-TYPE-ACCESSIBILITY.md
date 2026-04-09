# Testing Type Deep-Dive: Accessibility Testing

Last Updated: 2026-04-09

## What This Document Is For

This is a full treatment of accessibility testing as a quality layer — what it means, what standards apply, the tools and techniques available, where it fits in the delivery pipeline, and the cost of getting it wrong. Read it when you are designing a strategy for any product with a user interface, particularly products used by the public, products in regulated domains, or products with legal obligations under disability access legislation.

---

## Why Accessibility Is a Quality Concern, Not a Design Concern

Accessibility is frequently treated as a design task — something handled during UX review and visual design, not something tested in the pipeline. This framing is wrong, and it is expensive.

An accessible product is one that can be used by people with a range of abilities — including visual impairments (users who rely on screen readers), motor impairments (users who navigate by keyboard only), cognitive impairments (users who need clear, consistent, simple interactions), and hearing impairments (users who need captions or non-audio alternatives).

Accessibility failures are not cosmetic. They are functional defects that make parts of the product unusable for specific user groups. In many jurisdictions, they also carry legal exposure: the US ADA, the EU European Accessibility Act, the UK Equality Act, and Section 508 of the US Rehabilitation Act all impose accessibility obligations on software products in defined categories.

The most common reason accessibility defects accumulate to a significant remediation problem is that they were not tested continuously. Like security vulnerabilities and performance regressions, accessibility defects introduced in each sprint accumulate until someone looks.

---

## The Applicable Standards: WCAG

The Web Content Accessibility Guidelines (WCAG) are the international reference standard for web accessibility. Published by the W3C, they are referenced by legislation across multiple jurisdictions.

WCAG organises guidelines around four principles, often abbreviated as POUR:

- **Perceivable** — information and UI components must be presentable to users in ways they can perceive. Examples: images have alt text; videos have captions; colour is not the only means of conveying information.
- **Operable** — UI components and navigation must be operable. Examples: all functionality is accessible by keyboard; users have enough time to read content; pages do not contain content that flashes more than three times per second (seizure risk).
- **Understandable** — information and UI operation must be understandable. Examples: text is readable and understandable; pages behave in predictable ways; users are helped to avoid and correct mistakes.
- **Robust** — content must be robust enough that it can be interpreted by assistive technologies. Examples: HTML is valid; ARIA attributes are used correctly; names, roles, and values are programmatically determinable.

WCAG has three conformance levels:

| Level | Meaning |
|---|---|
| **A** | Minimum level. Failing these criteria makes the content inaccessible to some users entirely. |
| **AA** | The standard level referenced by most legislation and most accessibility policies. |
| **AAA** | The most stringent level, not typically required for full-site conformance, but applicable to specific content types. |

Most accessibility strategies target WCAG 2.1 AA as the conformance goal. WCAG 2.2 introduced additional criteria (particularly around mobile and cognitive accessibility) and is increasingly the relevant target.

---

## Types of Accessibility Testing

### Automated Accessibility Scanning

Automated scanners analyse the rendered HTML of a page and report violations of WCAG success criteria that can be detected algorithmically. They are fast, repeat exactly the same checks on every run, and can be integrated into CI/CD pipelines.

**What automated scanning reliably catches:**
- Missing alt text on images
- Form fields without associated labels
- Insufficient colour contrast (foreground/background ratio below 4.5:1 for normal text)
- Missing language declaration in HTML
- Duplicate IDs
- Missing page title
- Improper heading hierarchy
- Links with non-descriptive text ("click here", "read more")
- Missing ARIA labels where they are required
- Role violations (ARIA used incorrectly)

**What automated scanning cannot catch (the "57% problem"):**
Automated scanning catches approximately 30–40% of WCAG 2.1 AA issues. The majority require human judgment:
- Is the alt text meaningful and accurate, or is it just present?
- Is the reading order logical when the visual layout is stripped away?
- Is the error message clear and helpful, or just technically present?
- Does the keyboard navigation follow a logical flow through the page?
- Is the content understandable to a person with a cognitive impairment?

**Key tools:** axe-core (used by Lighthouse, axe DevTools, Jest-axe, Playwright accessibility checks), WAVE, Deque axe, Pa11y.

**Where it fits in the pipeline:** In the unit/component test stage (e.g. using jest-axe for React components) and in the E2E test stage (using Playwright's built-in accessibility checks or axe-playwright). Results should gate the pipeline for serious and critical violations.

### Keyboard-Only Navigation Testing

The tester navigates the entire product using only a keyboard — Tab, Shift+Tab, Enter, Space, arrow keys, Escape. No mouse.

**What it verifies:**
- Every interactive element (links, buttons, form fields, dropdowns, dialogs) is reachable and operable by keyboard
- The focus order is logical and matches the visual layout
- Focus indicators are visible when an element is focused (the outline is not suppressed by CSS)
- Keyboard traps do not exist (a component that captures focus and does not release it)
- Modal dialogs follow the correct focus management pattern (focus moves into the modal; Tab cycles within it; Escape closes it and returns focus to the trigger)

**How to run it:** Open the application. Put the mouse down and do not touch it. Start from the top of the page. Complete the primary user journeys using only the keyboard. Document every point where navigation fails, is illogical, or produces invisible focus.

**Where it fits in the pipeline:** Manual testing activity, run as part of the pre-release quality checklist and after significant UI changes. Can be partially automated using Playwright to simulate Tab navigation and assert focus order.

### Screen Reader Testing

The tester uses a screen reader to navigate and use the product, listening to the audio output and judging whether the product is usable without visual reference.

**What it verifies:**
- The reading order is logical in the accessibility tree (not just visually)
- Images are described correctly by their alt text
- Interactive elements are announced correctly with their role, name, and state ("button", not just the visual label; "expanded" or "collapsed" for accordions)
- Dynamic content updates (e.g. modal content appearing, form validation messages) are announced to the user
- Complex widgets (date pickers, carousels, data tables) expose the correct ARIA roles, states, and properties

**Key tools:** NVDA + Firefox (Windows, free), JAWS + Chrome or IE (Windows, paid), VoiceOver + Safari (macOS/iOS, built-in), TalkBack (Android, built-in).

**Where it fits in the pipeline:** Manual testing activity, run with a real screen reader by someone familiar with screen reader operation. This is not automatable — it requires a human to judge whether the audio output is meaningful and usable. Run before significant releases of any page or component that affects primary user flows.

### Colour Contrast and Visual Review

**What it verifies:**
- Text has sufficient contrast against its background (4.5:1 for normal text, 3:1 for large text and UI components at WCAG AA)
- Information is not conveyed by colour alone (e.g. a form validation error that is only indicated by turning text red, with no other indicator)
- Focus indicators are visible with sufficient contrast

**Key tools:** The browser's built-in developer tools (Lighthouse / axe in Chrome DevTools), TPGi Colour Contrast Analyser, automated scanning (axe-core catches contrast failures automatically).

---

## Where Accessibility Testing Fits in the Delivery Pipeline

```
Component development:
  - Unit-level accessibility checks (jest-axe, storybook-a11y)
  - Gate: fail on critical/serious axe violations

Every PR / CI run:
  - Automated accessibility scan (axe-playwright or pa11y) on key pages
  - Gate: no new serious or critical violations

Pre-release (significant UI changes):
  - Keyboard-only navigation walkthrough of affected flows
  - Colour contrast review of new/changed components

Before major releases or public launches:
  - Full screen reader test of primary user journeys
  - Complete WCAG 2.1 AA audit of the whole application (or affected areas)

Ongoing:
  - Automated scan results tracked over time to detect regression trends
```

---

## Accessibility as a Definition of Done

The most effective way to prevent accessibility debt from accumulating is to include accessibility checks in the team's definition of done for every story or feature that includes a UI change:

> A UI story is done when:
> - Automated accessibility scan shows no new critical or serious violations
> - Keyboard navigation through the new/changed elements is functional
> - New images have meaningful alt text
> - New form fields have labels
> - New interactive elements are reachable and operable by keyboard

This is lightweight to enforce but significant in impact. Most accessibility defects are introduced incrementally, story by story. Catching them at the story level is far cheaper than remediating them in a bulk accessibility audit six months later.

---

## The Cost of Deferred Accessibility

Teams that defer accessibility work until a late-project accessibility audit routinely discover two expensive problems:

1. **Systemic architectural issues** — foundational accessibility problems (e.g. a component library that uses `div` elements for interactive controls instead of semantic HTML) require architectural changes to fix, not just attribute additions.
2. **Volume** — hundreds of individual issues, some affecting every page, that were each individually small to fix but are now a large remediation project.

The pattern of "do a bulk accessibility audit and fix it all at once" is more expensive than "prevent accessibility issues from entering the codebase in the first place". The prevention approach costs almost nothing per story when accessibility checks are part of the routine. The remediation approach always costs more than expected.

---

## Accessibility and Legal Risk

In the following jurisdictions, accessibility obligations are enforceable:

- **United States:** Section 508 (federal agencies and federal contractors), ADA Title III (places of "public accommodation", increasingly interpreted to include websites), WCAG 2.1 AA is widely treated as the applicable standard
- **European Union:** European Accessibility Act (2025+ compliance required for many product categories), EN 301 549 standard
- **United Kingdom:** Equality Act 2010, public sector website accessibility regulations, WCAG 2.1 AA required
- **Australia:** Disability Discrimination Act, WCAG 2.0 AA referenced
- **Canada:** AODA (Ontario), WCAG 2.0 Level AA

The legal risk profile is highest for: public-facing consumer products, financial services, healthcare, government services, employment platforms, and any product used by a significant population of users with disabilities.

---

## Common Mistakes

- Treating a passing automated scan as an accessibility certification. Automated scanning catches 30–40% of WCAG failures.
- Not testing with a real screen reader. Screen reader behaviour is different from what the accessibility tree suggests, and the only way to know is to use one.
- Suppressing the browser default focus outline with `outline: none` in CSS without replacing it with an equivalent visible indicator.
- Writing alt text that is technically present but meaningless (e.g. `alt="image"` or `alt="photo of a thing"`).
- Deferring accessibility to a one-time pre-launch audit rather than catching it continuously.
- Not including accessibility in the definition of done, then discovering that every recently shipped story has introduced violations.

---

## Related Situations

- [Situation 3 — Greenfield Product](SITUATIONS-CATALOGUE.md#situation-3--greenfield-product) — accessibility is cheapest to build correctly from the start
- [Situation 5 — High-Regulation Domain](SITUATIONS-CATALOGUE.md#situation-5--high-regulation-domain) — accessibility may be a legal obligation
- [Anti-Pattern: The Deferred Compliance](STRATEGY-ANTI-PATTERNS.md#the-deferred-compliance)
