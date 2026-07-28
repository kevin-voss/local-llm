# Command: Deploy and verify

```text
/deploy <dev|qa|prod>
```

Deploy the requested stage, verify public health, diagnose failures, and fix forward. Deployment is separate from `/implement-feature`.

## Authorization

- `dev` and `qa`: explicit stage in the invocation is sufficient.
- `prod`: require explicit `prod` in the current user request.
- Never infer production deployment.
- Never force-push, rewrite Git history, reset the worktree, or deploy an older revision.

## Greenfield rule

- No data migrations or backfills.
- No rollback architecture.
- No backwards-compatibility or dual-version deployment.
- No legacy fallback.
- Fix failed deployments forward on the final architecture.
- CloudFormation may report automatic rollback states; inspect them as failure evidence, but do not restore obsolete application behavior.

## Preparation

1. Read:
   - `AGENTS.md`
   - `docs/technical/deployment.md`
   - Relevant package deployment docs
   - Root and infra Makefiles
2. Validate stage.
3. Use repository-configured AWS profile and region unless the user overrides them.
4. Inspect branch, HEAD, and `git status`.
5. State whether the deployment includes uncommitted changes.
6. For `prod`, stop if the worktree is dirty or the branch is not pushed.
7. Confirm required credentials and CDK context without printing secrets.

## Deploy

From repository root:

```bash
make deploy STAGE=<stage> AWS_PROFILE=<profile> AWS_REGION=<region>
```

Use lowercase `stage=` only when required by an existing script. Do not invent partial stack deployment unless the user requests it or failure isolation requires a documented scoped retry.

## Verify

Discover the deployed frontend URL:

```bash
cd infra && make print-frontend-urls STAGE=<stage> AWS_PROFILE=<profile> AWS_REGION=<region>
```

Use the real HTTPS application origin when available. Run:

```bash
curl -sS -o /dev/null -w "%{http_code}" "${APP_ORIGIN}/api/health"
curl -sS -o /dev/null -w "%{http_code}" "${APP_ORIGIN}/actuator/health"
curl -sS -o /dev/null -w "%{http_code}" "${APP_ORIGIN}/api/v1/config"
```

Expect HTTP 200.

Bruno smoke collection:

```text
bruno/crew-orbit-deploy-smoke/
```

Run when Bruno CLI is installed:

```bash
cd bruno/crew-orbit-deploy-smoke && bru run --env <stage>
```

Run deeper E2E only when the deployed change affects a critical journey or the user requests it:

```bash
make test-e2e STAGE=<stage> AWS_PROFILE=<profile> AWS_REGION=<region>
```

## Failure diagnosis

Do not stop at the CDK summary. Identify the first causal failure.

### Local build or synth

- Capture the exact failing command.
- Fix the source issue.
- Run the focused build/test.
- Retry deployment.

### CloudFormation

- Inspect failing stack status and recent events.
- Identify the first `FAILED` resource, not later cascading failures.
- Inspect resource state only as needed.
- Fix template or application configuration forward.

### ECS

- Inspect service desired/running/pending counts and events.
- Inspect recent stopped tasks and container exit reasons.
- Read `/creworbit/<stage>/backend` logs.
- Fix health, startup, image, IAM, or configuration cause forward.

### Lambda, SQS, DynamoDB, or S3

- Inspect the named resource and relevant logs/attributes.
- Use keyed reads and narrow time windows.
- Never print secrets or sensitive payloads.

### Stuck CloudFormation rollback state

- Report stack, resource, status, and reason.
- Do not change application design to restore obsolete behavior.
- Perform only the documented AWS recovery action required to unblock a fix-forward deployment.

## Completion gate

Deployment passes only when:

- Deploy command succeeded.
- Stack reached a terminal success state.
- All three public smoke endpoints return 200.
- Bruno/E2E required by the change passed, or an exact environmental blocker is reported.
- No unresolved ECS, Lambda, queue, or alarm failure remains.

## Output

- Stage, region, profile, branch, and commit
- Deploy command and result
- Application URL
- Smoke results
- Bruno/E2E results
- Failure evidence and fix-forward changes, if any
- Remaining blocker or risk
