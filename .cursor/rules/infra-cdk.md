---
description: AWS CDK infrastructure conventions — stacks, naming, config, IAM
globs:
  - "infra/lib/**"
  - "infra/bin/**"
  - "infra/test/**"
---

# Infrastructure (AWS CDK)

## Stack naming

- Pattern: `${Prefix}-CrewOrbit-${StackName}` where prefix = capitalized stage (Dev, Qa, Prod)
- Deploy order defined in `bin/infra.ts`: Base → Data → Auth → Batch → Backend → Frontend → DNS → Monitoring
- Dependencies declared via `stack.node.addDependency()`

## Resource naming

- Pattern: `${stage}-creworbit-${resource}` (lowercase) via `resourcePrefix()` from `shared-props.ts`
- Log groups: `/creworbit/${stage}/${service}`

## Configuration

- Stage config via `config.ts` — `resolveCrewOrbitContext()` reads CDK context
- Valid stages: `dev`, `qa`, `prod` (enforced at synth)
- Domain names from `config/domain-names.json` — validated for FQDN, uniqueness, no cross-stage collision
- Cross-stack values via props interfaces extending `CrewOrbitBaseProps` / `CrewOrbitVpcProps` / `CrewOrbitClusterProps`
- CDK context keys centralized in `CDK_CONTEXT` const

## IAM

- Policies in `iam-policies.ts` — scoped helper functions (e.g., `dynamoDbCrudPolicy`, `s3AttachmentsPolicy`)
- Least privilege: scope to specific table ARNs, bucket ARNs, queue ARNs
- Never use `*` for both actions and resources

## Tags

- Apply via `applyTags(scope, stage, configHash)` — Stage, Project, ManagedBy, ConfigHash

## Testing

- Jest snapshot tests in `infra/test/`
- Run: `cd infra && make synth` to validate
- Update snapshots intentionally when changing stack definitions

## Conventions

- One concern per construct — compose in stacks
- Avoid CloudFormation export locks: use literal names for cross-stack references when ARNs change on update (e.g., Batch job definition name)
- CloudFront certificates must be in `us-east-1`
- `StageBrowserConfig` drives CORS, callback URLs, and deploy verification — built once in `bin/infra.ts`
