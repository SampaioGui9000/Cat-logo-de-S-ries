import json
import sqlite3
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Catálogo de Séries")

ARQUIVO_JSON = Path("series.json")
ARQUIVO_DB = "series.db"


# ---------------------------------------------------------------- Modelo
class Serie(BaseModel):
    titulo: str = Field(..., min_length=1)
    genero: str = Field(..., min_length=1)
    ano_lancamento: int = Field(..., gt=1900, description="Deve ser maior que 1900")
    temporadas: int = Field(..., gt=0, description="Deve ser positivo")


# ---------------------------------------------------------- Persistência
def ler_series() -> list[dict]:
    """Lê o series.json. Se não existir (ou estiver vazio), retorna []."""
    if not ARQUIVO_JSON.exists():
        return []
    try:
        with open(ARQUIVO_JSON, "r", encoding="utf-8") as f:
            conteudo = f.read().strip()
            return json.loads(conteudo) if conteudo else []
    except (OSError, json.JSONDecodeError) as erro:
        raise HTTPException(status_code=500, detail=f"Erro ao ler o arquivo: {erro}")


def salvar_series(series: list[dict]) -> None:
    try:
        with open(ARQUIVO_JSON, "w", encoding="utf-8") as f:
            json.dump(series, f, ensure_ascii=False, indent=4)
    except OSError as erro:
        raise HTTPException(status_code=500, detail=f"Erro ao gravar o arquivo: {erro}")


def conectar_db() -> sqlite3.Connection:
    conexao = sqlite3.connect(ARQUIVO_DB)
    conexao.row_factory = sqlite3.Row
    return conexao


def criar_tabela() -> None:
    with conectar_db() as conexao:
        conexao.execute(
            """
            CREATE TABLE IF NOT EXISTS series (
                titulo TEXT PRIMARY KEY,
                genero TEXT,
                ano_lancamento INTEGER,
                temporadas INTEGER
            )
            """
        )


def inserir_no_db(serie: Serie) -> None:
    try:
        with conectar_db() as conexao:
            conexao.execute(
                "INSERT INTO series (titulo, genero, ano_lancamento, temporadas) "
                "VALUES (?, ?, ?, ?)",
                (serie.titulo, serie.genero, serie.ano_lancamento, serie.temporadas),
            )
    except sqlite3.Error as erro:
        raise HTTPException(status_code=500, detail=f"Erro no banco de dados: {erro}")


criar_tabela()


# ----------------------------------------------------------------- Rotas
@app.get("/")
def home():
    return {"mensagem": "Catálogo de Séries em construção"}


# Etapa 1 – Cadastro
@app.post("/series", status_code=201)
def cadastrar_serie(serie: Serie):
    series = ler_series()  # lê antes de gravar para não sobrescrever

    if any(s["titulo"].lower() == serie.titulo.lower() for s in series):
        raise HTTPException(status_code=409, detail="Série já cadastrada.")

    series.append(serie.model_dump())  # no Pydantic v1 use serie.dict()
    salvar_series(series)
    inserir_no_db(serie)  # mantém o SQLite sincronizado para a busca (Etapa 3)

    return {"mensagem": "Série cadastrada com sucesso!", "serie": serie}


# Etapa 2 – Listagem
@app.get("/series")
def listar_series():
    return ler_series()


# Etapa 3 – Busca por título (SQLite, case-insensitive)
@app.get("/series/{titulo}")
def buscar_serie(titulo: str):
    # Aceita "Breaking Bad", "breaking bad" e também "breaking-bad"
    with conectar_db() as conexao:
        linha = conexao.execute(
            """
            SELECT * FROM series
            WHERE LOWER(titulo) = LOWER(?)
               OR REPLACE(LOWER(titulo), ' ', '-') = LOWER(?)
            """,
            (titulo, titulo),
        ).fetchone()

    if linha is None:
        raise HTTPException(status_code=404, detail="Série não encontrada.")
    return dict(linha)
