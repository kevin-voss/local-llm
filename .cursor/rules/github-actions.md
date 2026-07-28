---
description: GitHub Actions CI/CD conventions — workflows, caching, deployment
globs:
  - ".github/**"
---

# GitHub Actions

## Workflow structure

- `ci.yml` — runs on PR; reusable builds for frontend (Bun), backend (Java 25), ai-worker (Node 20), infra (`cdk synth`)
- `deploy-dev.yml` / `deploy-prod.yml` — stage-specific deploy workflows via `workflow_dispatch`
- `reusable-build.yml` — shared build logic; compose in stage workflows, don't duplicate

## Jobs

- `ci` — lint, test, typecheck across packages
- `deploy-infra` — CDK deploy (core stacks), Docker build for backend/worker
- `deploy-services` — frontend build + backend/frontend stack deploy
- `e2e` — Playwright E2E with readiness checks before test run

## Conventions

- AWS auth via OIDC (`aws-actions/configure-aws-credentials`) — never store long-lived AWS keys in secrets
- Cache: Bun cache for frontend, Maven cache (`~/.m2`) for backend, npm cache for infra
- Pin action versions to SHA or major tag
- Path filters for conditional jobs — only build what changed
- Node 20 / Java 25 / Bun — match local dev versions
- `STAGE` passed via environment or input; capitalized prefix for stack names
