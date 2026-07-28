# Command: Debug and fix an error

```text
/debug <error, stack trace, failing request, or incident description>
```

Run an evidence-first diagnosis, reproduce the defect, fix the root cause, and prove the fix with the smallest relevant test. Do not commit, push, or deploy unless explicitly requested.

## Greenfield rule

- Fix the canonical design directly.
- Do not add compatibility shims, legacy fallbacks, dual paths, data migrations, rollback behavior, or old/new coexistence.
- Delete the superseded defective path when the fix replaces it.
- Fix forward.

## 1. Classify before using tools

Choose the evidence source:

| Error class | First evidence |
|-------------|----------------|
| Local test/build/type error | Local command output and code |
| Browser/UI error | Browser console, network request, frontend state |
| Local API/backend error | Backend logs, request, focused test |
| Deployed AWS incident | CloudWatch, CloudFormation, ECS, Lambda, SQS, DynamoDB, S3 as relevant |
| Unknown | Reproduce locally, then expand |

Do not use AWS merely because the project runs on AWS.

## 2. Evidence

- Preserve the exact error.
- Identify stage, timestamp, request ID, run ID, task ID, or resource when present.
- Find the smallest failing code path.
- Explain how the evidence implicates that path.
- Inspect surrounding tests and recent relevant changes.

For AWS:

- Use the repository-configured profile and region unless the user overrides them.
- Infer the stage from resource names or URLs; ask only when inference is unsafe.
- Start read-only.
- Prefer keyed DynamoDB reads over scans.
- Never expose tokens, secrets, presigned URLs, or decrypted credentials.
- Inspect only relevant CloudWatch groups, stack events, ECS tasks, queues, Lambdas, and S3 keys.

## 3. Reproduce

Add or extend the narrowest regression test.

Required order:

```text
evidence → reproducing test → red → root-cause fix → same test → green
```

If an automated reproduction is genuinely impossible, document why and use deterministic manual evidence.

## 4. Fix

- Address the root cause.
- Keep changes inside the failing feature boundary.
- Remove obsolete behavior and tests.
- Do not mask the error with retries, null defaults, broad exception handling, or fallback behavior unless retry is the canonical contract.
- Preserve unrelated working-tree changes.

## 5. Verify

Use `/verify` routing principles:

- Frontend: focused Bun test, then package typecheck when needed
- Backend: one `test-single`, then `./mvnw test -B` only when integration requires it
- AI worker: focused Vitest, then package typecheck when needed
- Infra: focused test and synth
- Cross-stack: `make build && make test` only when necessary
- E2E/Bruno for changed critical journeys when a target is available

Re-run the exact red test after the fix.

## Output

### Root cause

Specific causal explanation.

### Evidence

Logs, request behavior, failing assertion, and implicated paths.

### Fix

Files changed or deleted and why.

### Verification

Exact commands and red/green outcomes.

### Remaining risk

Only real unverified behavior or environmental blockers.
