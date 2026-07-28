---
description: React/TypeScript/Bun frontend conventions — components, hooks, services, routing, styling
globs:
  - "frontend/src/**"
---

# Frontend

## Structure

- Feature folders: `features/{name}/components/`, `hooks/`, `services/`, `utils/`, `constants/`, `types.ts`, `index.ts`
- Export everything through barrel `index.ts` per feature
- Shared code in `shared/` — hooks, lib, types, utils, constants, contracts
- Path alias `@/*` → `src/*`; also `@/lib/*`, `@/hooks/*`, `@/types/*`

## Components

- Functional components only with typed props interfaces (not `React.FC`)
- Naming: PascalCase components, kebab-case folders
- Import UI primitives from `@/components/ui/` (shadcn, new-york style)
- Use `cn()` from `@/lib/utils` for conditional Tailwind classes
- Tailwind for all styling — no CSS modules, no styled-components
- Icons from `lucide-react`

## Hooks

- Prefix with `use`, one hook per folder: `hooks/{useName}/index.ts`
- Data fetching via TanStack Query: `useQuery` with `queryKeys` from `@/lib/query-keys`
- Mutations via `useMutation` with `onSuccess` cache invalidation using `useQueryClient`
- Keep hooks focused — one concern per hook

## Services

- Thin wrappers around `apiClient` (`@/lib/api-client`) — no business logic
- Type inputs and outputs explicitly; use shared types from `@/types`
- URL construction: helper functions like `const base = (orgId, projectId) => \`/orgs/${orgId}/projects/${projectId}/...\``

## Routing

- TanStack Router with file-based routes under `src/routes/`
- Router created via `createRouter({ routeTree })` in `router.tsx`
- Preloading: `defaultPreload: "intent"`
- Breadcrumbs via `StaticDataRouteOption`

## Permissions

- Use `resolveProjectPermissions()` and the `can.*` helpers from `@/shared/utils/permissions`
- Owner bypass: `roleId === 'owner'` — never hardcode permission sets for owners elsewhere

## Testing

- `bun test` for unit tests, Playwright for E2E (`frontend/e2e/`)
- TypeScript strict mode enabled with `noUncheckedIndexedAccess`
