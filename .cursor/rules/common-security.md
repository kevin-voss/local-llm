---
description: Security rules for all code — secrets, credentials, logging
alwaysApply: true
---

# Security

- Never hardcode secrets, API keys, tokens, or PEM keys — use environment variables or AWS Secrets Manager
- Never log credentials, decrypted payloads, bearer tokens, or service tokens
- Use placeholders (`<REPLACE>`, `${ENV_VAR}`) in plan files, commit messages, and code comments
- `.env` files are gitignored — never commit them
- Reference `WORKER_SERVICE_TOKEN` by name only; never embed its value in source
- Backend credential encryption uses KMS (`credentialsKeyArn`) — never bypass or expose the plaintext
- S3 presigned URLs are short-lived; never persist or log them
- Cognito JWTs: validate issuer and audience on every protected endpoint
- Rate limiting is configured per-tenant (`MultiTenancyRateLimitProperties`) — do not disable it
- IAM policies: scope to specific resources and actions; never use `*` on both
