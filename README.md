# 🎬 Video Processing API

API assíncrona para processamento de vídeos utilizando arquitetura orientada a eventos.

---

## 🚀 Tecnologias Utilizadas

* **FastAPI** → Framework web moderno e performático
* **SQLAlchemy** → ORM para persistência
* **Alembic** → Controle de migrations
* **PostgreSQL** → Banco de dados relacional
* **AWS SQS (LocalStack)** → Mensageria assíncrona
* **Docker & Docker Compose** → Ambiente isolado
* **Pytest** → Testes automatizados

---

## 🧠 Arquitetura do Projeto

O projeto segue uma arquitetura em camadas:

```
app/
├── api/            → Rotas e handlers HTTP
├── core/           → Configurações e logging
├── db/             → Modelos e sessão do banco
├── repositories/   → Acesso a dados
├── services/       → Regras de negócio
├── messaging/      → Integração com SQS
├── worker/         → Processamento assíncrono
├── schemas/        → DTOs (Pydantic)
```

### 🔄 Fluxo da aplicação

1. Cliente envia requisição de processamento de vídeo
2. API salva requisição no banco
3. Mensagem é enviada para fila (SQS)
4. Worker consome a fila
5. Processamento é executado
6. Resultado é salvo no banco

---

## ⚙️ Como rodar o projeto localmente

> ⚠️ Antes de subir novamente a aplicação, execute `docker-compose down` para evitar problemas de estado com containers e filas do LocalStack.

### 🐳 Usando Docker

```bash
docker-compose up --build
```

Isso irá subir:

* API
* Worker
* PostgreSQL
* LocalStack (SQS)
* Rodar tests

---

## 📄 Documentação da API (Swagger)

Após subir a aplicação:

👉 [http://localhost:8000/docs](http://localhost:8000/docs)

Interface interativa com Swagger UI.

---

## 🧪 Rodando os testes

```bash
docker-compose run --rm test
```

---

## 📦 Estrutura de Testes

```
tests/
├── unit/          → Testes unitários
├── integration/   → Testes de integração
```

---

## 🔁 CI/CD

O projeto possui integração contínua com GitHub Actions que executa:

* Build da aplicação
* Migrations
* Testes automatizados
* Lint

Toda vez que um Pull Request é aberto.
