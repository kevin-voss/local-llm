---
description: TypeScript Lambda conventions — alert routing, SNS events, minimal handler
globs:
  - "infra/lambdas/alert-to-pagerduty/**"
---

# TypeScript Lambda (Alert to PagerDuty)

## Structure

- Single file: `src/index.ts` — exports `handler: SNSHandler`
- No framework — pure Lambda handler function
- Typed event input from `aws-lambda` types (`SNSEvent`, `SNSEventRecord`)

## Pattern

- Parse CloudWatch alarm JSON from `record.Sns.Message`
- Filter: only process `ALARM` state with HIGH severity (name contains `-High-` or `-HIGH-`)
- Route to PagerDuty Events API v2 (`/v2/enqueue`)
- Non-HIGH alarms are logged and skipped — not an error

## Error handling

- Missing `PAGERDUTY_INTEGRATION_KEY` → warn and return (not a crash)
- PagerDuty API failure → log and rethrow for Lambda retry
- Non-alarm SNS messages → skip silently

## Conventions

- AWS SDK v3: import only needed clients/commands
- `console.info` / `console.warn` / `console.error` for CloudWatch Logs
- `fetch()` for HTTP calls (Node 18+ built-in)
