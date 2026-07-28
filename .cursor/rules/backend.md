---
description: Java Spring Boot backend conventions — layering, DTOs, DynamoDB, testing
globs:
  - "backend/src/**"
---

# Backend

## Layering

- Strict: controller → service → repository — no repository calls from controllers
- Service interfaces with `*Impl` implementations (e.g., `ProjectService` / `ProjectServiceImpl`)
- Constructor injection only — never `@Autowired` on fields

## Feature packages

```
features/{name}/
  controller/     # @RestController, @RequestMapping, validation
  dto/            # request/ and response/ records
  model/          # domain entities
  repository/     # interface + DynamoDB impl (@Profile("dev")) + in-memory (@Profile("test"))
  service/        # interface + impl
  infrastructure/ # internal wiring if needed
```

## DTOs

- Records for request/response DTOs (e.g., `CreateProjectRequest`)
- Jakarta validation annotations: `@NotBlank`, `@Size`, etc.
- OpenAPI annotations: `@Schema`, `@Operation`, `@Tag`
- Never expose domain models directly in API responses

## Shared

- Exceptions in `shared/exception/` — reuse `ResourceNotFoundException`, `ForbiddenException`, `QuotaExceededException`, etc.
- Pagination via `PageResponse`, `PageResult`, `PaginationParams`, `CursorTokenUtil`
- Security: `SecurityUtils.resolveUserId()`, `ProjectPermissionGuard.requirePermission()`
- API responses wrapped in `ApiResponse<T>`

## DynamoDB

- Deeper modeling guidance: `.cursor/skills/dynamodb/SKILL.md`
- Conditional writes for idempotency; `TransactWriteItems` for multi-entity consistency
- `@Profile("dev")` for `Dynamo*Repository`; `@Profile("test")` for `InMemory*Repository`
- Helper utilities in `shared/util/DynamoHelper`

## Testing

- Use `./mvnw` — never bare `mvn`
- Test base: `ControllerTestBase` for MockMvc tests
- Prefer `make test-single TEST=ClassNameTest` for one class (~10-30s)
- `./mvnw test -B` for incremental package coverage; `make test` for clean CI parity plus container smoke

## Conventions

- Logging: SLF4J via `LoggerFactory.getLogger(ClassName.class)`
- `project.touch()` on updates to bump `updatedAt`
- Metrics: `MetricsService.recordXxx()` for business events
