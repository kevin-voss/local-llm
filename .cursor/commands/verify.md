# Command: Verify the current change

```text
/verify
/verify <path, package, feature, or acceptance criteria>
```

Inspect the actual diff, select the smallest complete verification scope, run it, and report evidence. Do not commit, push, or deploy.

## Rules

- Read `AGENTS.md` and applicable `.cursor/rules/`.
- Preserve unrelated working-tree changes.
- Never stage files.
- Test behavior, contracts, permissions, regressions, and important edge cases.
- Add or repair focused tests when verification exposes missing coverage or a defect in the current change.
- Do not refactor unrelated code.
- Do not preserve obsolete behavior through compatibility tests.

Crew Orbit is greenfield:

- No migration tests
- No rollback tests
- No backwards-compatibility suite
- No dual-path or legacy-fallback tests
- Remove obsolete tests when their behavior was intentionally replaced

## Process

1. Inspect `git status`, diff, changed packages, shared contracts, and existing tests.
2. Build a verification matrix:
   - Behavior changed
   - Risk
   - Relevant test layer
   - Command
3. Run focused tests first.
4. Fix feature-scoped defects or missing tests.
5. Re-run the exact failing command.
6. Expand scope only when shared contracts or cross-package behavior require it.
7. Run critical E2E or Bruno checks when the environment exists.
8. Record skipped or blocked evidence precisely.

## Scope routing

### Frontend

Focused:

```bash
cd frontend && bun test <test-path>
```

Package gate:

```bash
cd frontend && make test && make typecheck
```

### Backend

Focused:

```bash
cd backend && make test-single TEST=<ClassNameTest>
```

Broader backend integration:

```bash
cd backend && ./mvnw test -B
```

### AI worker

Focused:

```bash
cd ai-worker && npx vitest run <test-path>
```

Package gate:

```bash
cd ai-worker && make test && make typecheck
```

### Infra

```bash
cd infra && make synth
```

Run focused construct tests when applicable.

### Cross-stack or shared contracts

```bash
make build && make test
```

Do not run this for a narrow single-package change.

### E2E

```bash
make test-e2e
```

Run when a critical journey changed and a stable target is available. If unavailable, report:

- Exact blocker
- Command that should run
- Scenarios left unverified
- Residual risk

## Output

### Verdict

`PASS`, `FAIL`, or `BLOCKED`.

### Scope

Changed areas and risks verified.

### Evidence

| Command | Result | Coverage |
|---------|--------|----------|

### Changes made during verification

Tests or fixes added, with paths.

### Unverified areas

Exact blockers and residual risks. Never present “not run” as success.
