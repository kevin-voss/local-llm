# Command: Plan and refine a feature

Create or refine an implementation-ready feature package for **one agent** running `/implement-feature <feature-slug>` with no planning chat.

```text
/plan-feature <feature seed or idea>
/plan-feature refine features/<feature-slug> <feedback>
/plan-feature finalize features/<feature-slug>
```

Use Agent mode. Do not implement production code.

## Canonical artifact

Exactly **five files** under `features/<feature-slug>/`:

```text
features/<feature-slug>/
├── README.md       # status, summary, reading order, readiness, blockers
├── product.md      # what to build
├── technical.md    # how to build it
├── acceptance.md   # how to verify it
└── implement.md    # ordered STEP-* plan + evidence table
```

Kebab-case slug. Create `features/` when missing.

### File ownership

| File | Contains |
|------|----------|
| `README.md` | Frontmatter (`feature`, `slug`, `status`, `baseline_sha`, dates), one-paragraph summary, reading order, readiness checklist, blockers, handoff line `/implement-feature <feature-slug>` |
| `product.md` | `DEC-*`, problem, actors, scope, goals, business rules, journeys, UX states, mock views |
| `technical.md` | Codebase evidence, **one** final architecture, data model, contracts, security/tenancy, concurrency/idempotency, performance/observability, deletions |
| `acceptance.md` | `EDGE-*`, `AC-*` (Given/When/Then), test traceability matrix |
| `implement.md` | Ordered `STEP-*` sections, dependency notes, docs targets, evidence table |

### Package rules

- **Exactly five files.** If one file exceeds ~400 lines, split that file only (max **seven** total). Never create `spec/`, `implementation/`, coverage ledgers, per-step track files, or a parallel `specs/` tree.
- **Legacy layouts:** If `spec/`, `implementation/`, or `specs/<slug>.md` exist for this slug, **migrate content into the five files and delete the old trees** in the same planning pass. One package only.
- **Single source of truth.** Each `DEC` / `AC` / `EDGE` / `STEP` ID appears once. Other files link by ID only.
- **Self-contained handoff.** `/implement-feature <feature-slug>` must work from this folder alone.
- **One agent, one plan.** All `STEP-*` briefs are sections in `implement.md`.
- **Non-Markdown assets** only when the user explicitly requests them → `features/<feature-slug>/assets/`.

### `README.md` frontmatter

```yaml
---
feature: <Feature name>
slug: <feature-slug>
status: READY
baseline_sha: <git sha>
created: <YYYY-MM-DD>
updated: <YYYY-MM-DD>
---
```

Default create status is **`READY`** (see Auto-finalize). Use `DRAFT` only when the finalization gate fails or the user invoked `refine` without approving.

## One clean design (non-negotiable)

Crew Orbit has no production data to preserve. Plan **one** final architecture.

**Forbid in the package:**

- Migrations, backfills, rollback architecture, dual reads/writes, compatibility shims, legacy fallbacks, phased old/new coexistence
- Multiple provider/model/storage “options” left open for implementers
- Soft blockers (“verify week 1”, “or use fallback profile X”, “optional path if …”)
- Docs or steps about “how to change the embedding/model/store later”
- Parallel package layouts or versioned specs for the same slug

**Require instead:**

- One chosen stack per concern (embedder, transport, storage, queue, UI surface), recorded as a `DEC-*` with rejected alternatives
- Constants / single implementation — not a pluggable multi-backend registry for v1
- Unresolved product choices → write them as hard `DEC-*` with the recommended default from `/reason-feature` (or a documented default); do **not** leave open Q blockers after a normal plan pass
- Breaking storage → update mocks/fixtures; document dev/qa reset/reseed, not migration
- If repo evidence contradicts no-production-data, keep `DRAFT` and list the contradiction in blockers

## Required preparation

1. Read `AGENTS.md`, applicable `.cursor/rules/`, product/technical docs.
2. Inspect current code, tests, APIs, data models, infra, prior art.
3. Record current Git SHA in README `baseline_sha`.
4. Preserve `/reason-feature` decisions; challenge second vendors and multi-version designs.
5. For `refine` / `finalize`, read all five files before editing. Migrate any legacy trees first.

Subagent research consolidates into these five files — no sidecar outputs.

## Status lifecycle

```text
DRAFT → READY → IMPLEMENTING → VERIFIED
```

- **`/plan-feature <seed>` (create):** write the five files and **auto-finalize to `READY` in the same turn** (see Auto-finalize). Normal path after `/reason-feature` — no separate finalize step.
- **`refine`:** apply feedback; leave `DRAFT` only if new unresolved blockers remain; otherwise re-finalize to `READY` in the same turn.
- **`finalize`:** explicit freeze for packages still `DRAFT`, or re-confirm after refine when the user asks. Same gate as auto-finalize.
- `/implement-feature` owns `IMPLEMENTING` and `VERIFIED`.

## Auto-finalize (default)

`/reason-feature` already separates locked decisions from open questions **with recommended defaults**. Therefore a normal `/plan-feature` create **must**:

1. Promote every seed default into a hard `DEC-*` (or accept it as an existing `DEC-*`).
2. Clear README blockers (`None.`).
3. Fill **Accepted defaults (finalize)** in README.
4. Check readiness including user/seed approval of behavior.
5. Set `status: READY` and print the `/implement-feature <slug>` handoff.

**Do not** end a successful create on `DRAFT` waiting for a later `/plan-feature finalize`.

Stay `DRAFT` and report blockers **only** when the finalization gate fails (true contradictions, missing architecture, dual paths, or user override that re-opens a decision without a replacement).

## Planning process

Write once into the five files:

1. **Product intent** → `product.md`
2. **Current system** → `technical.md` § Current system (reuse / extend / delete)
3. **Final design** → `technical.md` (one architecture; no alternate live paths)
4. **Testability** → `acceptance.md`
5. **Execution** → `implement.md` (sequential `STEP-*` for one agent)
6. **Adversarial pass** → close gaps; promote remaining defaults to `DEC-*`
7. **Auto-finalize** → `READY` unless gate fails

Before READY: no ambiguity, contracts consistent, P0/P1 edges covered, every AC testable, steps ordered with clear path ownership, no hidden dependencies, no fallback architectures.

## Content rules

### Decisions (`DEC-*`)

In `product.md`. Decision + rationale + rejected alternative. No “maybe” / “consider” / “optional provider”. Decide or exclude. Seed defaults from `/reason-feature` become `DEC-*` during the plan pass — not lingering README Q rows.

### Mock views

In `product.md` when user-facing: primary, loading, empty, error, permission denied, unavailable dependency, responsive, a11y.

### Edge cases (`EDGE-*`)

In `acceptance.md`. P0 = security/tenant/data/state; P1 = races/retries/partial failure; P2 = UX friction.

### Acceptance criteria (`AC-*`)

In `acceptance.md`. Observable Given/When/Then. Matrix:

| AC | Test layer | Test target | Evidence command or method |
|----|------------|-------------|----------------------------|

### Steps (`STEP-*`)

Numbered sections in `implement.md`. Each step:

- Outcome
- Paths to create / edit / delete
- Depends on (prior steps)
- Requirements + linked `AC-*` / `EDGE-*`
- Tests and commands
- Docs updates

**Default: sequential for one agent.** Mark `[parallel-safe]` only for disjoint paths. Target **5–12 steps**. If the plan needs 15+, cut scope or merge steps — do not invent a multi-track DAG of micro-briefs.

### Evidence table

Bottom of `implement.md` (filled during `/implement-feature`):

| Step / AC | Status | Files or evidence | Tests | Commit |
|-----------|--------|-------------------|-------|--------|

## Finalization gate

Auto-finalize (create/refine) or `/plan-feature finalize features/<feature-slug>` sets `READY` only when:

- Product behavior and scope approved via `/reason-feature` seed defaults and/or explicit user acceptance in this turn.
- README has **zero** blocking decisions; every former open Q is a `DEC-*` written into `product.md`.
- Package is the five-file layout only (legacy trees deleted).
- `technical.md` matches codebase evidence and describes **one** architecture.
- Superseded paths listed for deletion; no dual paths kept “just in case”.
- Contracts consistent; P0/P1 edges have behavior; every AC mapped in `acceptance.md`.
- `implement.md` steps are ordered, owned, and completable by one agent (≤12 unless user approved a larger cut).
- No migration / rollback / compatibility / multi-version work.

Otherwise stay `DRAFT`; report remaining blockers only.
