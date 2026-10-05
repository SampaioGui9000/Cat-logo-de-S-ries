# 📺 Catálogo de Séries

API REST para gerenciar um catálogo de séries de TV, construída com **FastAPI**. Permite cadastrar, listar e buscar séries, evoluindo da persistência em arquivo `.json` até um banco **SQLite**.

Projeto prático do curso de Python da Alura (Checkpoint – Nível 1).

## 🚀 Tecnologias

- Python 3.10+
- [FastAPI](https://fastapi.tiangolo.com/)
- [Pydantic](https://docs.pydantic.dev/) (validação e modelagem de dados)
- [Uvicorn](https://www.uvicorn.org/) (servidor ASGI)
- JSON (`series.json`) e SQLite (`series.db`) para persistência

## ⚙️ Como executar

```bash
# 1. Clone o repositório
git clone <url-do-seu-repositorio>
cd <nome-da-pasta>

# 2. Crie e ative o ambiente virtual
python -m venv venv
source venv/bin/activate      # No Windows: venv\Scripts\activate

# 3. Instale as dependências
pip install fastapi uvicorn pydantic

# 4. Inicie o servidor
uvicorn main:app --reload
```

A API ficará disponível em `http://localhost:8000` e a documentação interativa (Swagger) em `http://localhost:8000/docs`.

## 🧩 Etapas do projeto

### Etapa 1 – Cadastro de séries (`POST /series`)
- Recebe os dados da série em JSON.
- Valida os dados com um modelo `Serie` (Pydantic):
  - `ano_lancamento` deve ser maior que 1900;
  - `temporadas` deve ser um número positivo.
- Lê o `series.json` antes de gravar, para não sobrescrever dados antigos.
- Usa `try/except` para tratar erros de leitura e gravação.
- Impede títulos duplicados (retorna `409`).

### Etapa 2 – Listagem de séries (`GET /series`)
- Lê o `series.json` e retorna todas as séries cadastradas.
- Retorna uma lista vazia `[]` quando não há séries.

### Etapa 3 – Busca por título (`GET /series/{titulo}`)
- Consulta diretamente o banco **SQLite** (`series.db`).
- Busca *case-insensitive*: `Breaking Bad`, `breaking bad` e `BREAKING BAD` funcionam igual (também aceita `breaking-bad`).
- Retorna `404` com mensagem amigável caso a série não exista.

> **Nota:** o `POST /series` grava nos dois lugares (JSON e SQLite), mantendo os dados sincronizados para que a busca da Etapa 3 encontre as séries cadastradas.

## 📡 Endpoints

| Método | Rota                | Descrição                      |
|--------|---------------------|--------------------------------|
| GET    | `/`                 | Mensagem de boas-vindas        |
| POST   | `/series`           | Cadastra uma nova série        |
| GET    | `/series`           | Lista todas as séries          |
| GET    | `/series/{titulo}`  | Busca uma série pelo título    |

## 🧪 Exemplos de uso

### Cadastrar uma série

```bash
curl -X POST http://localhost:8000/series \
  -H "Content-Type: application/json" \
  -d '{
    "titulo": "Breaking Bad",
    "genero": "Drama",
    "ano_lancamento": 2008,
    "temporadas": 5
  }'
```

Resposta (`201`):

```json
{
  "mensagem": "Série cadastrada com sucesso!",
  "serie": {
    "titulo": "Breaking Bad",
    "genero": "Drama",
    "ano_lancamento": 2008,
    "temporadas": 5
  }
}
```

### Listar todas as séries

```bash
curl http://localhost:8000/series
```

```json
[
  {
    "titulo": "Breaking Bad",
    "genero": "Drama",
    "ano_lancamento": 2008,
    "temporadas": 5
  }
]
```

### Buscar por título

```bash
curl http://localhost:8000/series/breaking-bad
```

```json
{
  "titulo": "Breaking Bad",
  "genero": "Drama",
  "ano_lancamento": 2008,
  "temporadas": 5
}
```

Série inexistente (`404`):

```json
{
  "detail": "Série não encontrada."
}
```

## 📁 Estrutura do projeto

```
.
├── main.py          # API (modelo, persistência e rotas)
├── series.json      # Criado automaticamente no primeiro cadastro
├── series.db        # Criado automaticamente ao iniciar a API
└── README.md
```

## 📚 Aprendizados

- Estruturação de rotas HTTP com FastAPI;
- Validação e modelagem de dados com Pydantic;
- Persistência em arquivo JSON e em banco relacional (SQLite);
- Tratamento de erros e códigos de status HTTP;
- Diferenças entre níveis de persistência de dados.

## 🔭 Próximos passos

- [ ] Autenticação de usuários
- [ ] Filtros por gênero e ano de lançamento
- [ ] Interface web consumindo a API
- [ ] Migração para PostgreSQL com SQLAlchemy

## 📄 Licença

Projeto desenvolvido para fins educacionais.
