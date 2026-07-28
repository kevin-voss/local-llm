---
description: Bruno API testing conventions — smoke tests, environments, assertions
globs:
  - "bruno/**"
---

# Bruno

## Collection

- Deploy smoke tests in `bruno/crew-orbit-deploy-smoke/`
- Collection config: `bruno.json` + `collection.bru` (no auth for public health endpoints)

## Environments

- `environments/dev.bru`, `qa.bru`, `prod.bru` — each sets `apiBase` to the stage URL
- Dev: `https://dev.crew-orbit.com`, QA: `https://qa.crew-orbit.com`, Prod: `https://crew-orbit.com`

## Smoke tests

- Located in `smoke/` subfolder
- Each `.bru` file: `GET {{apiBase}}/endpoint` with `assert { res.status: eq 200 }`
- Required endpoints: `/api/health`, `/actuator/health`, `/api/v1/config`
- Folder-level config in `smoke/folder.bru`

## Running

- Bruno CLI: `bru run --env <dev|qa|prod>` from the collection directory
- Used after deploy to verify endpoints — see `.cursor/commands/deploy.md`
