FROM python:3.12-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install --no-install-recommends -y \
    curl && rm -rf /var/lib/apt/lists/*

ADD https://astral.sh/uv/install.sh /install.sh
RUN chmod 755 /install.sh && /install.sh && rm /install.sh
# Make uv available system-wide for all users
RUN cp /root/.local/bin/uv /usr/local/bin/uv
ENV PATH="/usr/local/bin:${PATH}"

RUN useradd --create-home --uid 10001 appuser
WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN ln -sf /usr/local/bin/python3.12 /usr/bin/python3.12 && ln -sf /usr/local/bin/python3.12 /usr/bin/python3
RUN uv sync

COPY . .
RUN chown -R appuser:appuser /app

# Set PATH before switching user
ENV PATH="/app/.venv/bin:$PATH"
USER appuser

CMD ["python", "--version"]
