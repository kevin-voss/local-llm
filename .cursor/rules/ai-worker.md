---
description: AI worker conventions — engine, steps, providers, prompts, reporting
globs:
  - "ai-worker/src/**"
---

# AI Worker

## Architecture

- Entry: `main.ts` → `runMain()` orchestrates the full lifecycle
- Engine: `engine.ts` → `executeDynamicWorkflow()` runs steps in sequence
- Steps: `steps/` — each step self-registers (imported in `main.ts`); atomic and independently testable
- Providers: `providers/` — abstract AI model differences (Claude, OpenAI, etc.) via `getProvider()`
- Prompts: `prompts/roles/`, `prompts/steps/`, `prompts/shared/`

## Step lifecycle

- Steps are typed via `StepType` enum (aligned with backend)
- Each step produces a `StepResult` with `id`, `status`, `output`
- Step status reported to backend via `reporter.reportStepStatus()`
- Role completion reported via `reporter.reportRoleComplete()` with handoff data

## Configuration

- `WorkerConfig` loaded from `TASK_MESSAGE` env var (JSON) or CLI args
- S3 key context: `{ orgId, projectId, taskId, runId }` for artifact uploads
- Backend URL from `BACKEND_URL` env var; auth via `WORKER_SERVICE_TOKEN`

## Reporting

- `createReporter()` for backend-connected mode; `createNoopReporter()` for local/CLI
- Heartbeat every 30s via `reporter.startHeartbeat()`
- Role transitions: `next`, `loop_back`, `await_feedback`, `done`, `abort`, `callback_abort`
- Always report `reportRunComplete()` on exit — even on errors (best-effort)

## Context & Caching

- Workbench pattern: S3 → local `context-cache/` directory
- Attachments hydrated from optimized S3 keys into `context-cache/attachments/`
- Role outputs uploaded to S3 and cached locally between roles
- `pruneOldCycles()` keeps cache clean

## Conventions

- TypeScript strict mode — no `any`, explicit return types on public functions
- Error categorization via `categorizeError()` — produces `{ category, exitCode, message }`
- Graceful shutdown: SIGTERM/SIGINT handlers report failure before exit
- Logging: Pino logger with structured fields (`taskId`, `runId`)
- Testing: Vitest (`vitest.config.ts`)
