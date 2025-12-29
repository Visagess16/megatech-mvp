import os
import sqlite3

# =================================================
# ================= CONFIG DB =====================
# =================================================

# Caminho absoluto do banco (funciona local e cloud)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "megatech.db")


def conectar():
    """
    Retorna conexão SQLite segura para Streamlit Cloud
    """
    return sqlite3.connect(
        DB_PATH,
        check_same_thread=False
    )


# =================================================
# ================= TABELAS =======================
# =================================================
def criar_tabelas():
    """
    Cria todas as tabelas necessárias.
    Executa de forma segura em qualquer ambiente.
    """
    conn = conectar()
    cur = conn.cursor()

    cur.executescript("""
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        telefone TEXT,
        email TEXT,
        observacoes TEXT
    );

    CREATE TABLE IF NOT EXISTS servicos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER NOT NULL,
        descricao TEXT NOT NULL,
        valor REAL NOT NULL,
        data_servico DATE NOT NULL,
        proxima_manutencao DATE,
        FOREIGN KEY (cliente_id) REFERENCES clientes(id)
    );

    CREATE TABLE IF NOT EXISTS despesas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo TEXT NOT NULL,
        descricao TEXT NOT NULL,
        valor REAL NOT NULL,
        data DATE NOT NULL
    );

    CREATE TABLE IF NOT EXISTS agenda (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data DATE NOT NULL,
        horario TEXT,
        cliente TEXT NOT NULL,
        cliente_id INTEGER,
        descricao TEXT,
        valor REAL,
        status TEXT NOT NULL,
        FOREIGN KEY (cliente_id) REFERENCES clientes(id)
    );
    """)

    conn.commit()
    conn.close()
