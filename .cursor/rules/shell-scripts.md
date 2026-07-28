---
description: Shell script conventions — safety, style, shared helpers
globs:
  - "scripts/**"
  - "**/*.sh"
---

# Shell Scripts

## Safety

- Start with `#!/usr/bin/env bash` and `set -euo pipefail`
- Quote all variable expansions: `"${VAR}"` not `$VAR`
- Use `readonly` for constants

## Shared helpers

- Source `scripts/make/lib.sh` for common functions and defaults
- `lib.sh` exports: `ROOT` (repo root), `AWS_PROFILE` (default: `kevin-voss`), `AWS_REGION` (default: `eu-central-1`), `STAGE` (default: `dev`)
- `stage_cap()` — capitalizes stage for CloudFormation stack names

## Style

- Prefer `[[ ]]` over `[ ]` for conditionals
- Log to stderr (`>&2`), output to stdout
- Trap for cleanup: `trap cleanup EXIT`
- Functions: lowercase with underscores (`deploy_stack`, `stage_cap`)

## Per-directory conventions

- `scripts/make/` — orchestration scripts invoked by root `Makefile` (deploy, dev, mock, clean-data)
- `scripts/e2e/` — Cognito user setup/teardown for E2E tests
- `scripts/mocks/` — seed data scripts (TypeScript via Bun)
- `backend/scripts/make/` — backend-specific dev/build helpers
- `infra/scripts/make/` — CDK deploy/synth helpers
