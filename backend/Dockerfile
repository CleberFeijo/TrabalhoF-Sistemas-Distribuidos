FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    TZ=America/Sao_Paulo

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

# Usuário sem privilégios para rodar a aplicação.
RUN useradd --create-home --uid 10001 hist
COPY --chown=hist:hist app ./app
USER hist

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8080/health', timeout=4).status == 200 else 1)"

# WEB_CONCURRENCY = número de processos. Com mais de 1, configure REDIS_URL
# para o chat funcionar entre processos.
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port 8080 --workers ${WEB_CONCURRENCY:-1} --proxy-headers --forwarded-allow-ips='*'"]


# Imagem para rodar testes e lint: docker compose --profile test run --rm tests
FROM base AS test
USER root
COPY requirements-dev.txt pyproject.toml ./
RUN pip install -r requirements-dev.txt
COPY --chown=hist:hist tests ./tests
USER hist
CMD ["sh", "-c", "ruff check app tests && pytest"]
