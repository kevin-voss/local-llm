# Cursor config in this repo

High-level map for **Crew Orbit** — details and architecture live in root [`AGENTS.md`](../AGENTS.md).

## Where to look

| Need | Start here |
|------|------------|
| Project + stack + AI workflow rules | [`AGENTS.md`](../AGENTS.md) |
| Human doc hub (product → technical) | [`docs/README.md`](../docs/README.md), [`docs/ai/`](../docs/ai/README.md) (link index) |
| Research notes / ADRs | [`plan/`](../plan/) |
| Canonical pre-code feature packages | `features/<feature-slug>/` (five files from `/plan-feature`) |
| Package runbooks | `frontend/docs/`, `backend/docs/`, `ai-worker/docs/`, `infra/docs/` |
| Marketing decks, demos, carousels | [`docs/assets/`](../docs/assets/) |
| Cinematic ad HTML | [`content/ads/`](../content/ads/README.md) |
| Contributor layout (other root dirs) | [`README.md`](../README.md) “Other top-level directories” |

## Commands (slash)

| Invoke | File | Purpose (short) |
|--------|------|-----------------|
| `/reason-feature` | [`commands/reason-feature.md`](commands/reason-feature.md) | Read-only product and feasibility reasoning |
| `/plan-feature` | [`commands/plan-feature.md`](commands/plan-feature.md) | Create/refine feature package; auto-finalize `READY` after `/reason-feature` |
| `/implement-feature` | [`commands/implement-feature.md`](commands/implement-feature.md) | Orchestrate implementation, reviews, verification, commit, and push |
| `/debug` | [`commands/debug.md`](commands/debug.md) | Evidence-first diagnosis and red/green fix |
| `/verify` | [`commands/verify.md`](commands/verify.md) | Diff-aware tests and acceptance evidence |
| `/deploy` | [`commands/deploy.md`](commands/deploy.md) | Deploy one explicit stage and verify it |

### Feature workflow

1. Ask mode: `/reason-feature <idea>` (decisions + defaults in seed).
2. Agent mode: `/plan-feature <feature seed>` → `features/<slug>/` five files and **auto-finalize to `READY`** (promotes seed defaults to `DEC-*`; no separate finalize step).
3. Optional refine: `/plan-feature refine features/<slug> <feedback>` → re-finalize to `READY` unless new true blockers.
4. Explicit `/plan-feature finalize` only if a package is still `DRAFT`.
5. New Agent chat: `/implement-feature <slug>`.

One package layout, one architecture per feature — no `spec/` + `implementation/` trees, no parallel `specs/<slug>.md`. Commands never hardcode model names; `/implement-feature` may choose subagent capability at dispatch when the runtime supports it.

## Rules (`rules/*.md`)

Rules use **Markdown + YAML frontmatter** (`description`, and optionally `alwaysApply: true` or `globs:`). Scope is stack- or topic-based (frontend, backend, ai-worker, infra-cdk, lambdas, GitHub Actions, Docker, Bruno, shell scripts, security).

**Always-on:** [`rules/common-security.md`](rules/common-security.md), [`rules/common-caveman.md`](rules/common-caveman.md) (default terse communication).

## Skills (`.cursor/skills/`)

| Skill | Path | Notes |
|-------|------|--------|
| Caveman | [`skills/caveman/SKILL.md`](skills/caveman/SKILL.md) | Matches product seed `backend/.../skills/seed/caveman.md`; commits, reviews, doc compression |
| DynamoDB | [`skills/dynamodb/SKILL.md`](skills/dynamodb/SKILL.md) | Keys, GSIs, conditional writes/transactions, streams, cost |

**Note:** `.gitignore` may reference optional local AWS snippets (e.g. `aws-cli.local.mdc`); filenames may use `.mdc` for local-only copies — committed rules here are `.md`.
