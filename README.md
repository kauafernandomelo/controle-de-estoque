# Inventory Control API

API profissional de controle de estoque construída com Python, FastAPI, PostgreSQL, SQLAlchemy 2.0, Alembic e autenticação JWT. O projeto foi estruturado como portfólio para demonstrar práticas reais de back-end: separação em camadas, regras de negócio em services, repositories, migrations, testes automatizados, Docker e CI.

## Funcionalidades

- Cadastro e login de usuários com JWT e refresh token.
- Perfis de acesso: `ADMINISTRADOR` e `OPERADOR`.
- CRUD de produtos com SKU único.
- Movimentações de estoque: `ENTRADA`, `SAIDA` e `AJUSTE`.
- Bloqueio de estoque negativo.
- Histórico completo de movimentações.
- Bloqueio de exclusão de produtos com movimentações.
- Relatórios de estoque mínimo, mais movimentados, entradas, saídas e totais.

## Arquitetura

```text
src/
  api/            Rotas HTTP, dependências e permissões
  core/           Configurações, segurança, logs e exceções globais
  database/       Engine, sessão e base declarativa SQLAlchemy
  models/         Modelos ORM e enums do domínio
  repositories/   Acesso a dados e consultas persistentes
  services/       Regras de negócio e casos de uso
  schemas/        Schemas Pydantic de entrada e saída
tests/            Testes automatizados com Pytest
alembic/          Migrations do banco de dados
```

## Tecnologias

- Python 3.12+
- FastAPI
- PostgreSQL
- SQLAlchemy 2.0
- Pydantic v2
- Alembic
- JWT com `python-jose`
- Bcrypt com `passlib`
- Pytest e coverage mínimo de 80%
- Docker e Docker Compose
- GitHub Actions

## Variáveis de Ambiente

Crie um arquivo `.env` baseado em `.env.example`:

```env
APP_NAME="Inventory Control API"
APP_ENV=development
DEBUG=true
DATABASE_URL=postgresql+psycopg://inventory:inventory@localhost:5432/inventory_db
SECRET_KEY=change-this-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]
```

Para produção no Neon, use a URL PostgreSQL fornecida pela plataforma em `DATABASE_URL`.

## Executando Localmente

```bash
python -m venv .venv
source .venv/bin/activate
pip install ".[dev]"
cp .env.example .env
alembic upgrade head
uvicorn src.main:app --reload
```

No Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install ".[dev]"
Copy-Item .env.example .env
alembic upgrade head
uvicorn src.main:app --reload
```

## Executando com Docker

```bash
cp .env.example .env
docker compose up --build
```

A API ficará disponível em `http://localhost:8000` e a documentação em `http://localhost:8000/docs`.

## Testes

```bash
pytest
```

O projeto exige cobertura mínima de 80% configurada no `pyproject.toml`.

## Fluxo de Autenticação

1. Cadastre o primeiro usuário em `POST /api/v1/auth/register`. Ele será administrador automaticamente.
2. Faça login em `POST /api/v1/auth/login` usando `username` como email e `password` como senha.
3. Envie o token no header `Authorization: Bearer <access_token>`.
4. Renove o token em `POST /api/v1/auth/refresh`.

## Deploy no Render

1. Crie um serviço Web no Render conectado ao repositório GitHub.
2. Configure o build command: `pip install .`.
3. Configure o start command: `alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port $PORT`.
4. Adicione as variáveis de ambiente, incluindo `DATABASE_URL` do Neon e um `SECRET_KEY` forte.

Link do deploy: `https://seu-app.onrender.com`

## Principais Decisões Técnicas

- A API usa schemas com aliases em português para alinhar contrato HTTP aos requisitos, enquanto o código interno mantém nomes técnicos em inglês.
- Services concentram regras de negócio como SKU único, estoque negativo e bloqueio de exclusão com histórico.
- Repositories isolam consultas SQLAlchemy e facilitam testes e manutenção.
- Alembic versiona o schema para refletir práticas reais de produção.
- O primeiro usuário cadastrado vira administrador para facilitar bootstrap seguro do projeto.
