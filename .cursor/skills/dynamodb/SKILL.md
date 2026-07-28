---
name: dynamodb
displayName: DynamoDB
description: DynamoDB data modeling and operations guidance for keys, indexes, conditional writes, transactions,
  streams, migrations, and cost control.
allowed-tools:
  - Read
  - Grep
  - Bash
metadata:
  creworbit:
    skillSlug: dynamodb
    category: data
    contentHash: 331214c197b71a5be3c72a4cf1f9ea8dcf6a745ce0ea8f05fe2214bbcba7d192
    bodyVersionId: vYk3eRVQJ9kkk1fKDD_zaPoTHaJYK00O
---


# DynamoDB

Use this skill when designing, changing, querying, or operating DynamoDB tables and indexes.

## Core principles

- Design from access patterns first. Do not start with an entity relationship model.
- Choose partition keys that distribute load and avoid hot partitions.
- Use sort keys to model time, hierarchy, status, and queryable groupings.
- Prefer single-table or multi-table design based on the product's access patterns and team familiarity, not ideology.
- Keep items bounded in size. Store large blobs in S3 and references in DynamoDB.
- Make writes idempotent and state transitions conditional.

## Key design

- Define every required query before choosing keys.
- Use composite keys when they make query intent explicit.
- Keep high-cardinality values in partition keys.
- Avoid partition keys based on low-cardinality status values such as `OPEN` or `PENDING`.
- Include deterministic tie-breakers in sort keys for stable pagination.
- Consider write sharding for extremely hot logical partitions.

```text
PK = PROJECT#<projectId>
SK = TASK#<createdAt>#<taskId>

GSI1PK = TASK_STATUS#<projectId>#<status>
GSI1SK = <updatedAt>#<taskId>
```

## Queries and pagination

- Use `Query` when the partition key is known.
- Avoid `Scan` in request paths. Scans are for admin tools, backfills, and controlled migrations.
- Always paginate list operations that can grow.
- Return opaque cursors to clients instead of exposing DynamoDB internals directly.
- Use projection expressions when large attributes are unnecessary.
- Validate filter behavior: filters happen after reading and still consume capacity.

## Conditional writes and idempotency

- Use condition expressions for uniqueness, ownership, and state transitions.
- Use idempotency tokens for retryable create/action endpoints.
- Store request fingerprints when duplicate idempotency keys must detect conflicts.
- Treat conditional check failures as expected business conflicts, not system errors.

```text
Update item only when status = PREPARING:
SET status = READY, updatedAt = :now
ConditionExpression: status = :preparing
```

## Transactions

- Use transactions when multiple items must change atomically.
- Keep transactions small and targeted.
- Expect higher latency and cost than simple writes.
- Include condition checks to protect invariants.
- Make transaction retries safe.

## Indexes

- Add GSIs for real query patterns, not speculative future needs.
- Remember GSIs are eventually consistent.
- Choose projected attributes deliberately to control cost and item size.
- Monitor index backfill and write throttling after adding a new GSI.
- Avoid overloading one GSI with unrelated patterns if it makes code hard to reason about.

## Streams and async workflows

- Use streams for event-driven reactions to data changes, not as a substitute for clear write logic.
- Make stream processors idempotent.
- Handle retries and poison records with DLQs or failure destinations where supported.
- Store enough event context to debug without logging sensitive payloads.
- Understand ordering guarantees: ordering is per partition key, not global.

## Capacity, cost, and limits

- Know whether tables use on-demand or provisioned capacity.
- Monitor throttling, consumed capacity, hot keys, item size, and account limits.
- Watch write amplification from GSIs and streams.
- Use TTL for natural expiration, but do not rely on TTL for immediate deletion.
- Batch operations reduce round trips but do not make writes atomic.

## Local and AWS commands

```bash
aws dynamodb describe-table --table-name <table>
aws dynamodb query --table-name <table> --key-condition-expression "PK = :pk"
aws dynamodb scan --table-name <table> --limit 10
aws dynamodb update-item --table-name <table> --key file://key.json --update-expression "SET #s = :s"
```

Prefer project scripts and repository abstractions for application behavior tests.

## Testing

- Unit test key builders and mappers.
- Test conditional write behavior and conflict mapping.
- Use integration tests for repository queries and transactions.
- Cover pagination, empty results, missing items, duplicate creates, and invalid state transitions.
- Use realistic item shapes and large-enough samples for index queries.

## Risk management

- Before changing keys or GSIs, list every access pattern and caller.
- Before backfills, estimate item count, capacity impact, cost, and rollback.
- Do not remove old attributes until all deployed code can operate without them.
- Check IAM permissions for table, index, and stream access.
- Treat hot partitions, unbounded scans, and non-idempotent retries as production risks.
