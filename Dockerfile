# syntax=docker/dockerfile:1

FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

COPY pyproject.toml uv.lock readme.md ./
RUN uv sync --frozen --no-dev --no-install-project

COPY docs ./docs
COPY overrides ./overrides
COPY scripts ./scripts
COPY zensical.toml ./

ARG BPAYD_OPENAPI_SOURCE=https://services.bmspay.com/swagger/docs/v1

RUN uv run --no-sync scripts/generate_api_reference.py --source "$BPAYD_OPENAPI_SOURCE" \
    && uv run --no-sync zensical build --strict

FROM caddy:2-alpine

COPY Caddyfile /etc/caddy/Caddyfile
COPY --from=builder /app/site /srv

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD wget -q -O /dev/null http://127.0.0.1:8080/healthz || exit 1
