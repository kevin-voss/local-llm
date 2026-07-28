# Command: Implement a planned feature

Run in a new high-capability Agent chat:

```text
/implement-feature <feature-slug>
```

Resolves to `features/<feature-slug>/`. The five-file package is the complete handoff — no planning chat required.

Invocation authorizes:

- Feature-scoped code and documentation changes
- Subagent delegation when helpful (optional — default is **you implement the feature**)
- Relevant tests, builds, typechecks, Bruno, and E2E
- Conventional Commits
- Push of the **current** branch (no new branch creation)

Invocation does not authorize deployment, force-push, destructive history changes, creating a feature branch, or unrelated working-tree changes.

## Role

You are the **feature implementer**. One agent owns the feature end-to-end.

- Read the full package, then execute `implement.md` steps in order.
- Implement directly unless a step is large enough to delegate safely to a subagent.
- Inspect every delegated result; you remain accountable.
- Only you may edit the feature package (status, evidence), stage, commit, and push.

## Package layout

```text
features/<feature-slug>/
├── README.md       # status, baseline_sha, blockers
├── product.md      # what to build
├── technical.md    # how to build it
├── acceptance.md   # AC-*, EDGE-*, tests
└── implement.md    # STEP-* execution plan + evidence table
```

Read in that order (skip re-read of README after first pass unless status/blockers matter).

## Greenfield architecture rule

Crew Orbit has no production data to preserve.

- Implement the clean final architecture directly.
- No migrations, backfills, compatibility shims, dual reads/writes, legacy fallbacks, or phased coexistence.
- Delete superseded code, schemas, contracts, flags, tests, mocks, and docs in the same feature.
- Breaking storage → update mocks/fixtures; document dev/qa reset/reseed.
- If implementation contradicts no-production-data, stop and report.

## Preflight

1. Read `AGENTS.md`, applicable `.cursor/rules/`, and all five package files.
2. Require `status: READY` in README. Otherwise stop; list failed readiness gates.
3. Inspect current branch, `git status`, `baseline_sha`, unrelated user changes.
4. Preserve unrelated changes — never stage, revert, or overwrite them.
5. **Stay on the current branch.** Do not create `feature/<slug>` or any other branch.
6. Reconcile planning baseline drift; update package if contracts/decisions changed, then re-check readiness.
7. Set README status to `IMPLEMENTING`.

## Execution

### Default mode: single agent

1. Walk `implement.md` **STEP-01 → STEP-N** sequentially.
2. After each step: run listed tests; tick AC/edge coverage mentally against `acceptance.md`.
3. Update the evidence table in `implement.md` as you go.
4. Do not skip deletions or docs listed in a step.

### Optional delegation

Delegate a step only when it is clearly bounded and paths do not overlap your active work. Task packet must include: feature slug, `STEP-*`, `AC-*`/`EDGE-*`, owned paths, requirements, tests. Subagents do not commit, push, or edit the package.

Parallelize only steps explicitly marked `[parallel-safe]` with disjoint paths.

### Spec discoveries

- Never silently diverge from the package.
- Factual fixes → update the relevant file when product behavior is unchanged.
- Product/contract/security/AC changes → pause, update package, confirm still implementable, resume.

## Review (proportionate)

Before completion, self-review against:

- `product.md` — journeys, UX states, scope
- `technical.md` — architecture, contracts, deletions, security/tenancy
- `acceptance.md` — every `AC-*` and P0/P1 `EDGE-*`

For high-risk features (auth, tenancy, billing, new infra), dispatch one read-only review subagent. Small/medium features: thorough self-review is enough.

P0/P1 findings block completion until fixed.

## Verification

Run smallest relevant tests during each step. At end, run what the diff requires:

| Area | Command |
|------|---------|
| Frontend | `cd frontend && make test && make typecheck` |
| Backend | `cd backend && ./mvnw test -B` (or `make test-single TEST=…` during steps) |
| AI worker | `cd ai-worker && make test && make typecheck` |
| Infra | `cd infra && make synth` |
| Cross-stack | `make build && make test` |

Bruno for changed HTTP contracts. E2E when environment supports it. Every `AC-*` needs automated evidence or explicit blocked/manual note in evidence table.

## Documentation gate

Update stable docs that own shipped behavior (`docs/product/features/`, `docs/technical/`, Bruno, package READMEs). Remove docs for deleted behavior. Do not copy the planning package into `docs/`.

## Git gate

1. Review `git status` and full feature diff.
2. No secrets, junk, or unrelated files.
3. P0/P1 findings resolved.
4. Evidence table complete except final commit SHAs.
5. Stage feature-owned changes explicitly.
6. One or more logical Conventional Commits.
7. Record commit SHAs in evidence table; set README `status: VERIFIED`; commit package update.
8. Push the current branch without force. Do not create a branch. Do not deploy.

## Completion gate

Report complete only when:

- Every `STEP-*` done or explicitly removed in `implement.md`
- Every `AC-*` has evidence
- Code, deletions, tests, mocks, Bruno, docs done
- Verification passed
- Implementation commits + package verification commit pushed

## Final response

Report: outcome, current branch, commits, push result, steps done, AC evidence, tests run, E2E/Bruno, deletions, residual risk.

Do not claim complete if any gate failed.
