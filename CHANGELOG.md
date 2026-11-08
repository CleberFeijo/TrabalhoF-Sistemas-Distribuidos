# Changelog

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/).

## [Unreleased]

## [1.0.0] — 2026-11-08

Reescrita do backend herdado do trabalho de Sistemas Distribuídos para o TCC.

### Adicionado
- Modelo separado de **pontos históricos** (`landmarks`) e **curiosidades** (`curiosities`), com fonte (`source`) para conteúdo importado pelo crawler.
- **Moderação**: conteúdo de usuários entra como `pending`; moderadores aprovam/rejeitam com motivo.
- Papéis `user`, `moderator` e `admin`.
- **Cadastro público** (`POST /v1/auth/register`) e exclusão da própria conta (exigência da Play Store).
- Busca de pontos próximos com distância (`$geoNear`) e contagem de curiosidades aprovadas.
- Chat por ponto com autenticação JWT, verificação de raio de 200 m no servidor, protocolo JSON, anti-flood e distribuição entre processos via Redis pub/sub.
- Estrutura de histórico do chat para o futuro plano premium (desativada por `CHAT_PERSISTENCE_ENABLED`).
- Logout real (invalidação de tokens via `token_version`), troca de senha com rotação de token.
- Administrador inicial por variáveis de ambiente e script `create_admin`.
- `GET /health`, testes automatizados com MongoDB/Redis reais, GitHub Actions.

### Corrigido
- Qualquer usuário conseguia alterar papéis ou excluir outros usuários.
- `DELETE` de curiosidade não exigia autenticação.
- Banco era repopulado (duplicado) a cada inicialização.
- Emails duplicados eram aceitos (agora há índice único, sem diferenciar maiúsculas).
- Autor das curiosidades vinha do corpo da requisição e a listagem atribuía todas ao usuário atual.
- Listagem quebrava quando o autor não existia.
- Erros de autenticação e de entrada retornavam 500 com traceback.
- `GET /user/{id}` sem o parâmetro do id; rota de roles nunca registrada.
- Chat sem autenticação, com nome de usuário livre, mensagem de entrada nunca enviada e `----Fim----` derrubando a sala inteira.

### Removido
- Segredos, senhas e hashes versionados (`.env.template`, README, seeds).
- Template genérico não utilizado (API keys, tasks de exemplo, `extra_hosts` externos, flake8 no startup).
- Portas de MongoDB/Redis/RabbitMQ expostas para fora da máquina.
