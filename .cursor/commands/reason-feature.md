# Command: Reason about a feature

Use in **Ask mode** before creating a specification:

```text
/reason-feature <idea, problem, or feature request>
```

Read-only exploration. Do not create or edit files. Do not implement code.

## Objective

Turn an incomplete idea into a coherent feature direction grounded in the current Crew Orbit product and codebase. Challenge weak assumptions, find missing behavior, and produce a self-contained feature seed for `/plan-feature`.

## Greenfield architecture rule

Crew Orbit has no production data to preserve.

- Choose **one** clean final architecture.
- Do not propose data migrations, backfills, rollback architecture, compatibility shims, dual reads/writes, legacy fallbacks, phased coexistence, or “verify later / fallback provider” designs.
- Do not introduce a second AI vendor, model family, or storage engine when an existing path can own the job.
- Replace and delete superseded designs directly.
- If repository evidence contradicts the no-production-data premise, surface the contradiction instead of inventing compatibility work.

## Process

1. Read `AGENTS.md`, relevant `.cursor/rules/`, product docs, technical docs, and current implementation.
2. Restate the actual user problem. Separate desired outcome from the suggested solution.
3. Identify actors, permissions, frequency, urgency, and workflow context.
4. Describe the current journey and the desired journey.
5. Test product value:
   - Who benefits?
   - What repeated friction disappears?
   - Why does this belong in Crew Orbit?
   - Does it improve execution, collaboration, reliability, or accumulated context value?
6. Generate only meaningful alternatives. Compare user value, system fit, complexity, risk, and operating cost.
7. Recommend one direction. Reject weaker alternatives explicitly — including extra vendors, pluggable backends, and “version 2 later” escape hatches.
8. Inspect codebase feasibility:
   - Existing feature owners and reusable patterns
   - Required frontend, backend, ai-worker, infra, Bruno, and docs areas
   - Contracts and domain invariants likely affected
   - Existing behavior that should be replaced or deleted
9. Cover UX:
   - Happy path
   - Loading, empty, error, permission, and unavailable states
   - Responsive and accessibility implications
   - Low-fidelity view or flow when visual structure matters
10. Cover high-value edge cases:
    - Authorization and tenant isolation
    - Concurrency and idempotency
    - Partial failure and retries
    - Stale UI or background state changes
    - Cost, quotas, abuse, and observability
11. Separate decisions already made from questions that still need user input. Every open question gets a recommended default that `/plan-feature` **auto-finalizes** into a hard `DEC-*` (no separate finalize step after a normal reason→plan flow).

Do not force a fixed number of ideas or recommendations.

## Output

### Verdict

One of:

- `READY TO PLAN`
- `NEEDS PRODUCT DECISIONS`
- `DO NOT BUILD`

Explain why in a short paragraph.

### Refined feature request

A concise description of the recommended feature.

### User problem and outcome

- Actors
- Current pain
- Desired outcome
- Success signals

### Before → after

Show the end-to-end workflow change.

### Scope

- In scope
- Non-goals
- Existing behavior to replace or delete

### Recommended solution

Describe product behavior and key system touchpoints. Include a small Mermaid flow or Markdown wireframe when useful. Name the **single** choice for each contested concern (embedder, transport, store, etc.).

### Alternatives rejected

Short decision table: option, advantage, problem, rejection reason.

### Technical feasibility

List likely owning areas, existing patterns, contracts, and major constraints. Do not write a full technical plan.

### Edge cases and risks

Prioritized. Avoid trivia.

### Decisions needed

For every unresolved decision, give a recommended default and consequence. Prefer defaults that remove vendors and dual paths.

### Feature seed

End with a compact, copy-ready block containing everything `/plan-feature` needs. The seed must not depend on hidden conversation context. It must describe one architecture with no fallback stacks. Expect `/plan-feature` to promote all recommended defaults to `DEC-*` and set `status: READY` in the same turn.
