# API do Hist — referência para o app

Base: `https://<host>/v1`. A referência interativa completa (schemas, exemplos)
fica em `/docs` (Swagger). Este documento resume o que o app precisa.

## Convenções

- **Autenticação:** `Authorization: Bearer <access_token>` em todas as rotas,
  exceto `POST /auth/register`, `POST /auth/login` e `GET /health`.
- **Ids** são strings (ObjectId do MongoDB).
- **Datas** em ISO 8601 com fuso (UTC).
- **Coordenadas** sempre como `latitude`/`longitude` (ou `lat`/`lon` em query).
- **Paginação:** `?page=1&page_size=20` (máx. 100) → `{"items": [...], "total", "page", "page_size"}`.
- **Erros** sempre no formato:

```json
{"error": {"code": "not_found", "message": "Ponto histórico não encontrado.", "details": []}}
```

| HTTP | `code` mais comuns |
|---|---|
| 401 | `unauthorized`, `invalid_credentials`, `session_revoked`, `invalid_password` |
| 403 | `forbidden`, `premium_required` |
| 404 | `not_found`, `feature_disabled` |
| 409 | `email_taken`, `conflict` |
| 422 | `validation_error` (`details` traz `field` e `message`) |
| 500 | `internal_error` (sem detalhes técnicos) |

Ao receber `401`, o app deve descartar o token e voltar para o login.

## Autenticação

| Método | Rota | Corpo | Resposta |
|---|---|---|---|
| POST | `/auth/register` | JSON `{name, last_name, email, password}` (senha 8–72) | `201` TokenResponse |
| POST | `/auth/login` | **form-urlencoded** `username=<email>&password=...` | `200` TokenResponse |
| POST | `/auth/logout` | — | encerra todas as sessões do usuário |

TokenResponse:

```json
{"access_token": "...", "token_type": "bearer", "expires_in": 604800,
 "user": {"id": "...", "name": "Ana", "last_name": "Souza", "email": "ana@ex.com",
          "roles": ["user"], "plan": "free", "is_active": true, "created_at": "..."}}
```

## Conta

| Método | Rota | Observação |
|---|---|---|
| GET | `/users/me` | perfil |
| PATCH | `/users/me` | `{name?, last_name?, email?, current_password?}` — trocar email exige a senha |
| POST | `/users/me/password` | `{current_password, new_password}` → TokenResponse novo (os outros tokens deixam de valer) |
| DELETE | `/users/me` | corpo `{password}` → `204`. Exigência da Play Store. Conteúdo aprovado fica anônimo; o restante é apagado |
| GET | `/users/me/curiosities?status=` | minhas curiosidades (inclui `rejection_reason`) |
| GET | `/users/me/landmarks?status=` | pontos que sugeri |

> Retrofit: `DELETE` com corpo exige `@HTTP(method = "DELETE", path = "users/me", hasBody = true)`.

## Pontos históricos

| Método | Rota | Observação |
|---|---|---|
| GET | `/landmarks/nearby?lat=&lon=&radius=&limit=` | aprovados, do mais próximo ao mais distante. `radius` padrão 200 m, máx. 50 km |
| GET | `/landmarks/{id}` | detalhe |
| GET | `/landmarks/{id}/curiosities` | curiosidades aprovadas, paginadas, mais recentes primeiro |
| POST | `/landmarks` | sugerir ponto: `{name, latitude, longitude, description?, category?, address?, city?, state?, image_url?, curiosity?}` |
| POST | `/landmarks/{id}/curiosities` | `{text}` (10–2000) → `pending` |
| PATCH | `/landmarks/{id}` | moderador |
| DELETE | `/landmarks/{id}` | admin, ou o autor enquanto não aprovado |

Item de `/nearby`:

```json
{"id": "...", "name": "Igreja Matriz", "description": "...", "latitude": -22.52, "longitude": -41.94,
 "category": "igreja", "city": "Rio das Ostras", "state": "RJ", "country": "BR",
 "image_url": "https://...", "source": {"name": "wikidata", "url": "...", "license": "CC0", "external_id": "Q123"},
 "status": "approved", "curiosity_count": 3, "distance_m": 87.4, "chat_available": true, ...}
```

Curiosidade:

```json
{"id": "...", "landmark_id": "...", "landmark_name": "Igreja Matriz", "text": "...",
 "author": {"id": "...", "name": "Ana Souza"}, "source": null,
 "status": "approved", "rejection_reason": null, "created_at": "..."}
```

`author` é `null` em conteúdo importado (ver `source`) ou de conta excluída.

## Curiosidades

| Método | Rota | Observação |
|---|---|---|
| GET | `/curiosities/{id}` | aprovadas, ou próprias/moderador |
| DELETE | `/curiosities/{id}` | autor ou moderador |

## Moderação (moderator/admin)

| Método | Rota |
|---|---|
| GET | `/moderation/landmarks?status=pending` (fila em ordem de chegada) |
| POST | `/moderation/landmarks/{id}/approve` |
| POST | `/moderation/landmarks/{id}/reject` — `{reason}` (3–500) |
| GET | `/moderation/curiosities?status=pending` |
| POST | `/moderation/curiosities/{id}/approve` |
| POST | `/moderation/curiosities/{id}/reject` — `{reason}` |

## Usuários (admin)

`GET /users?q=`, `GET /users/{id}`, `PATCH /users/{id}` (`{roles?, plan?, is_active?}`), `DELETE /users/{id}`.
Não é possível remover o último administrador ativo.

## Chat (WebSocket)

Uma sala por ponto histórico. Mensagens são efêmeras (não são salvas).

```
wss://<host>/v1/chat/{landmark_id}?token=<access_token>&lat=<lat>&lon=<lon>
```

O token também pode ir no header `Authorization: Bearer ...` (OkHttp permite).

**Regras do servidor**

- o ponto precisa estar aprovado;
- para entrar, o usuário precisa estar a até **200 m** (`CHAT_JOIN_RADIUS_M`);
- se o app informar posição a mais de **300 m** (`CHAT_LEAVE_RADIUS_M`), a conexão é encerrada;
- mensagens de 1 a 1000 caracteres, no máximo 10 a cada 10 s.

**App → servidor**

```json
{"type": "message", "text": "Alguém sabe quando abre?"}
{"type": "location", "lat": -22.52, "lon": -41.94}
{"type": "ping"}
```

Envie `location` sempre que o GPS atualizar de forma relevante, e `ping` a cada ~30 s para manter a conexão.

**Servidor → app**

```json
{"type": "welcome", "room": "<landmark_id>", "landmark": {"id": "...", "name": "..."},
 "user": {"id": "...", "name": "Ana Souza"}, "join_radius_m": 200, "leave_radius_m": 300,
 "max_message_length": 1000, "history_enabled": false}
{"type": "message", "id": "<uuid>", "room": "...", "user": {"id": "...", "name": "..."}, "text": "...", "sent_at": "..."}
{"type": "presence", "event": "join", "room": "...", "user": {...}, "sent_at": "..."}
{"type": "presence", "event": "leave", "room": "...", "user": {...}, "sent_at": "..."}
{"type": "error", "code": "rate_limited", "message": "..."}
{"type": "pong"}
```

A identidade do remetente vem sempre do token; o app não envia nome de usuário.

**Fechamento da conexão** (antes de fechar, o servidor envia um `error` explicando o motivo):

| Código | `error.code` | Significado |
|---|---|---|
| 4400 | `invalid_location` | `lat`/`lon` ausentes ou inválidos |
| 4401 | `unauthorized`, `session_revoked` | token ausente, inválido ou revogado |
| 4403 | `out_of_range` | longe demais do ponto |
| 4404 | `not_found` | ponto inexistente ou não aprovado |

Erros que **não** fecham a conexão: `invalid_payload`, `invalid_message`, `message_too_long`, `rate_limited`, `unknown_type`, `invalid_location` (em `location`).

### Histórico (plano premium — desativado)

`GET /chat/{landmark_id}/messages?limit=50&before=<iso>` responde hoje `404 feature_disabled`.
Quando `CHAT_PERSISTENCE_ENABLED=true`, as mensagens passam a ser gravadas (com expiração
de `CHAT_HISTORY_RETENTION_DAYS`) e a rota devolve o histórico para usuários com `plan = premium`
(caso contrário, `403 premium_required`). O campo `history_enabled` do `welcome` indica ao app se
deve oferecer o histórico.

## Limitações conhecidas

- A localização é informada pelo próprio app; um GPS falsificado (mock location) consegue burlar
  o raio do chat. O app pode detectar e bloquear mock locations no Android, mas não há como
  garantir no servidor.
