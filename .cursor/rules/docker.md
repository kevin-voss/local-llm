---
description: Dockerfile conventions — multi-stage builds, caching, security
globs:
  - "**/Dockerfile"
---

# Dockerfiles

## Multi-stage builds

- Builder stage for compilation, slim runtime stage for the final image
- Copy dependency manifests first, install deps, then copy source — maximizes layer caching

## Per-service patterns

- **Backend** (`backend/Dockerfile`): `eclipse-temurin:25-jdk` build → `eclipse-temurin:25-jre` runtime; `curl` installed for ECS health checks; JVM flags: `-XX:+UseContainerSupport -XX:MaxRAMPercentage=75.0`
- **AI Worker** (`ai-worker/docker/Dockerfile`): Node multi-stage; installs CLI tools (Cursor, GitHub CLI, etc.) via `PROVIDERS` build arg; runs as non-root `worker` user
- **Lambda** (`infra/lambdas/attachment-optimizer/Dockerfile`): cargo-lambda/cargo-chef for Rust; Alpine asset stage

## Security

- Run as non-root user in runtime stage (`useradd`/`adduser` → `USER`)
- `--no-install-recommends` on apt; `rm -rf /var/lib/apt/lists/*` after install
- No secrets in build args or layers

## Conventions

- Pin base image versions — avoid `latest` tags
- `WORKDIR /app` (or service-appropriate path)
- `EXPOSE` the port the service listens on
- `ENTRYPOINT` for the main process
