---
description: Rust Lambda conventions — attachment optimizer, DynamoDB idempotency, error handling
globs:
  - "infra/lambdas/attachment-optimizer/**"
---

# Rust Lambda (Attachment Optimizer)

## Architecture

- SQS-driven: receives `SqsEvent`, processes records, returns `SqsBatchResponse` with partial failures
- Entry: `main.rs` → `lambda_runtime::run(service_fn(handle))`
- Handler: `handler.rs` → `handle()` iterates records, calls `process_one()` per attachment
- Modules: `dynamo.rs` (DynamoDB ops), `s3.rs` (S3 get/put), `callback.rs` (POST to backend), `mime.rs`

## Idempotency

- DynamoDB conditional write for RAW → PROCESSING (Lambda owns this transition, not backend)
- If conditional write fails → record was already claimed → skip (not a failure)
- After extraction: update DynamoDB to OPTIMIZED or FAILED
- Callback: `maybe_send_callback()` POSTs to backend when all task attachments are done

## Error handling

- Use `Result<T, E>` with descriptive error types throughout
- Never `unwrap()` in production paths — use `?` or match
- Partial batch failures: push `BatchItemFailure` for failed records; succeeded records are not retried
- Empty extraction (e.g., scanned PDFs) → mark as FAILED, not silent success

## Environment

- Required env vars: `S3_ATTACHMENTS_BUCKET`, `ATTACHMENTS_TABLE_NAME`
- Tracing: `tracing_subscriber` with `attachment_optimizer=info` default
- Structured logging via `tracing::info!`, `error!` with event/field annotations

## Build

- Docker build targeting `x86_64-unknown-linux-musl` (or ARM via cargo-lambda)
- Multi-stage: cargo-chef for dependency caching, then build, then minimal runtime
- Test fixtures in `fixtures/`
