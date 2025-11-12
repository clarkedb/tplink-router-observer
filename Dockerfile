FROM python:3.13-slim
COPY --from=ghcr.io/astral-sh/uv:0.9.8 /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml ./
RUN uv sync --no-dev

# create non-root user for security
RUN useradd -m -u 1000 collector && \
    chown -R collector:collector /app

# create data directory
RUN mkdir -p /app/data && chown -R collector:collector /app/data

COPY router_stats_collector/ ./router_stats_collector/

USER collector

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1

VOLUME ["/app/data"]

CMD ["uv", "run", "router-collector"]
