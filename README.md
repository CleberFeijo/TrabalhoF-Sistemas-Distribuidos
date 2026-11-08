# Hist

Aplicativo Android para descoberta do patrimônio histórico urbano por
geolocalização: o usuário vê os pontos históricos ao redor, lê curiosidades,
contribui com novas (sujeitas a moderação) e conversa em um chat efêmero com
quem está fisicamente no mesmo lugar.

Projeto de TCC — Ciência da Computação, UFF (Rio das Ostras).

## Estrutura

| Pasta | Conteúdo |
|---|---|
| `backend/` | API (FastAPI + MongoDB + Redis), worker Celery e testes |
| `docs/` | Referência da API e do protocolo do chat para o app |
| `android/` | App Kotlin/Jetpack Compose *(em construção)* |

## Rodando localmente

Pré-requisito: Docker com Docker Compose.

```bash
cp .env.example .env
# preencha JWT_SECRET, MONGO_ROOT_PASSWORD, REDIS_PASSWORD e (opcional) ADMIN_EMAIL/ADMIN_PASSWORD
docker compose up -d --build
```

- API: http://localhost:8080
- Swagger: http://localhost:8080/docs
- Saúde: http://localhost:8080/health

O administrador inicial é criado no primeiro boot a partir de `ADMIN_EMAIL` e
`ADMIN_PASSWORD`. Para criar/promover outro depois:

```bash
docker compose exec api python -m app.scripts.create_admin pessoa@exemplo.com --name Nome
```

Worker Celery (usado pelo crawler) e RabbitMQ ficam no perfil `worker`:

```bash
docker compose --profile worker up -d
```

## Testes

Os testes usam MongoDB e Redis reais (as consultas geográficas não funcionam
com mocks):

```bash
docker compose --profile test run --rm --build tests
```

Ou fora do Docker, com Mongo/Redis acessíveis:

```bash
cd backend
pip install -r requirements-dev.txt
MONGO_URI=mongodb://localhost:27017 REDIS_URL_TEST=redis://localhost:6379/0 pytest
ruff check app tests
```

O GitHub Actions roda lint, testes e build da imagem a cada push em `backend/`.

## Papéis e moderação

| Papel | Pode |
|---|---|
| `user` | ver pontos e curiosidades aprovados, sugerir pontos e curiosidades (entram como **pendentes**), conversar no chat, gerenciar/excluir a própria conta |
| `moderator` | tudo de `user` + aprovar/rejeitar conteúdo, editar pontos; o que publica já entra aprovado |
| `admin` | tudo de `moderator` + gerenciar usuários e excluir pontos |

Conteúdo importado pelo crawler entra aprovado, com a fonte (`source`) registrada.

Detalhes dos endpoints e do protocolo do chat: [`docs/api.md`](docs/api.md).
