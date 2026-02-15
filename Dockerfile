FROM python:3.13-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-editable

COPY src/ ./src/
RUN uv sync --frozen --no-dev

FROM python:3.13-slim AS runtime

WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src

ENV PATH="/app/.venv/bin:$PATH"
ENV FAKTUROID_TRANSPORT=streamable-http
ENV FAKTUROID_HOST=0.0.0.0
ENV FAKTUROID_PORT=8000

EXPOSE 8000

CMD ["python", "-m", "fakturoid_mcp"]
