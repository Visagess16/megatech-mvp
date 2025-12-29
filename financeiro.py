import pandas as pd
from datetime import date, timedelta
from database import conectar
from datetime import datetime, timedelta, date


# =================================================
# ================= CLIENTES ======================
# =================================================
def inserir_cliente(nome, telefone, email, observacoes):
    conn = conectar()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO clientes (nome, telefone, email, observacoes)
        VALUES (?, ?, ?, ?)
        """,
        (nome, telefone, email, observacoes),
    )
    conn.commit()
    conn.close()


def listar_clientes():
    conn = conectar()
    df = pd.read_sql(
        """
        SELECT
            id,
            nome,
            telefone,
            email,
            observacoes
        FROM clientes
        ORDER BY nome
        """,
        conn,
    )
    conn.close()
    return df


# =================================================
# ================= SERVIÇOS ======================
# =================================================
def inserir_servico(cliente_id, descricao, valor, data_servico):
    """
    Ao inserir um serviço, já calcula automaticamente
    a próxima manutenção (+120 dias).
    """
    proxima_manutencao = data_servico + timedelta(days=120)

    conn = conectar()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO servicos
        (cliente_id, descricao, valor, data_servico, proxima_manutencao)
        VALUES (?, ?, ?, ?, ?)
        """,
        (cliente_id, descricao, valor, data_servico, proxima_manutencao),
    )
    conn.commit()
    conn.close()


def listar_servicos_executados():
    conn = conectar()
    df = pd.read_sql(
        """
        SELECT
            s.id,
            c.nome AS cliente,
            s.descricao,
            s.valor,
            s.data_servico,
            s.proxima_manutencao
        FROM servicos s
        JOIN clientes c ON c.id = s.cliente_id
        ORDER BY s.data_servico DESC
        """,
        conn,
    )
    conn.close()
    return df


def listar_servicos_periodo(data_inicio, data_fim):
    conn = conectar()
    df = pd.read_sql(
        """
        SELECT
            s.id,
            c.nome AS cliente,
            s.descricao,
            s.valor,
            s.data_servico
        FROM servicos s
        JOIN clientes c ON c.id = s.cliente_id
        WHERE s.data_servico BETWEEN ? AND ?
        ORDER BY s.data_servico
        """,
        conn,
        params=(data_inicio, data_fim),
    )
    conn.close()
    return df


# =================================================
# ================= DESPESAS ======================
# =================================================
def inserir_despesa(tipo, descricao, valor, data):
    conn = conectar()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO despesas (tipo, descricao, valor, data)
        VALUES (?, ?, ?, ?)
        """,
        (tipo, descricao, valor, data),
    )
    conn.commit()
    conn.close()


def listar_despesas():
    conn = conectar()
    df = pd.read_sql(
        """
        SELECT
            id,
            tipo,
            descricao,
            valor,
            data
        FROM despesas
        ORDER BY data DESC
        """,
        conn,
    )
    conn.close()
    return df


def listar_despesas_periodo(data_inicio, data_fim):
    conn = conectar()
    df = pd.read_sql(
        """
        SELECT
            id,
            tipo,
            descricao,
            valor,
            data
        FROM despesas
        WHERE data BETWEEN ? AND ?
        ORDER BY data
        """,
        conn,
        params=(data_inicio, data_fim),
    )
    conn.close()
    return df


# =================================================
# ================= AGENDA ========================
# =================================================
def inserir_agenda(data, horario, cliente_nome, cliente_id, descricao, valor, status):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO agenda (
            data,
            horario,
            cliente,
            cliente_id,
            descricao,
            valor,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            str(data),
            horario,
            cliente_nome,
            cliente_id,
            descricao,
            valor,
            status
        )
    )

    conn.commit()
    conn.close()



def listar_agenda():
    conn = conectar()
    df = pd.read_sql(
        """
        SELECT 
            a.id,
            a.data,
            a.horario,
            a.cliente_id,
            c.nome AS cliente,
            a.descricao,
            a.valor,
            a.status,
            c.email,
            c.telefone,
            c.observacoes
        FROM agenda a
        LEFT JOIN clientes c ON c.id = a.cliente_id
        ORDER BY a.data DESC
        """,
        conn
    )
    conn.close()
    return df



def listar_agenda_mes(ano, mes):
    conn = conectar()
    df = pd.read_sql(
        """
        SELECT
            id,
            data,
            cliente,
            descricao,
            valor,
            status
        FROM agenda
        WHERE strftime('%Y', data) = ?
          AND strftime('%m', data) = ?
        """,
        conn,
        params=(str(ano), f"{mes:02d}"),
    )
    conn.close()

    df["data"] = pd.to_datetime(df["data"])
    return df


def atualizar_status_agenda(id_agenda, status):
    conn = conectar()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE agenda
        SET status = ?
        WHERE id = ?
        """,
        (status, id_agenda),
    )
    conn.commit()
    conn.close()


def inserir_servico(cliente_id, descricao, valor, data_servico):
    conn = conectar()

    # 🔹 garante que a data é date
    if isinstance(data_servico, str):
        data_servico = datetime.strptime(data_servico, "%Y-%m-%d").date()

    proxima_manutencao = data_servico + timedelta(days=120)

    conn.execute(
        """
        INSERT INTO servicos (
            cliente_id,
            descricao,
            valor,
            data_servico,
            proxima_manutencao
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            cliente_id,
            descricao,
            valor,
            data_servico,
            proxima_manutencao
        )
    )

    conn.commit()
    conn.close()



def servico_existe(cliente_id, descricao, data_servico):
    conn = conectar()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT 1
        FROM servicos
        WHERE cliente_id = ?
          AND descricao = ?
          AND data_servico = ?
        LIMIT 1
        """,
        (cliente_id, descricao, str(data_servico))
    )

    existe = cur.fetchone() is not None
    conn.close()
    return existe




# =================================================
# ================= ALERTAS =======================
# =================================================
def listar_alertas_manutencao(dias):
    hoje = date.today()
    limite = hoje + timedelta(days=dias)

    conn = conectar()
    df = pd.read_sql(
        """
        SELECT
            s.id,
            c.id AS cliente_id,
            c.nome AS cliente,
            c.telefone,
            s.descricao,
            s.proxima_manutencao
        FROM servicos s
        JOIN clientes c ON c.id = s.cliente_id
        WHERE s.proxima_manutencao IS NOT NULL
        """,
        conn,
    )
    conn.close()

    df["proxima_manutencao"] = pd.to_datetime(df["proxima_manutencao"]).dt.date

    vencidas = df[df["proxima_manutencao"] < hoje]
    a_vencer = df[
        (df["proxima_manutencao"] >= hoje)
        & (df["proxima_manutencao"] <= limite)
    ]

    return vencidas, a_vencer


# =================================================
# ================= DASHBOARD =====================
# =================================================
def resumo_financeiro_periodo(data_inicio, data_fim):
    conn = conectar()

    receita = pd.read_sql(
        """
        SELECT COALESCE(SUM(valor), 0) AS total
        FROM servicos
        WHERE data_servico BETWEEN ? AND ?
        """,
        conn,
        params=(data_inicio, data_fim),
    )["total"][0]

    despesa = pd.read_sql(
        """
        SELECT COALESCE(SUM(valor), 0) AS total
        FROM despesas
        WHERE data BETWEEN ? AND ?
        """,
        conn,
        params=(data_inicio, data_fim),
    )["total"][0]

    conn.close()

    lucro = receita - despesa
    return receita, despesa, lucro


def dados_grafico_periodo(data_inicio, data_fim):
    conn = conectar()

    df_receita = pd.read_sql(
        """
        SELECT
            data_servico AS data,
            valor,
            'Receita' AS tipo
        FROM servicos
        WHERE data_servico BETWEEN ? AND ?
        """,
        conn,
        params=(data_inicio, data_fim),
    )

    df_despesa = pd.read_sql(
        """
        SELECT
            data AS data,
            valor,
            'Despesa' AS tipo
        FROM despesas
        WHERE data BETWEEN ? AND ?
        """,
        conn,
        params=(data_inicio, data_fim),
    )

    conn.close()

    return pd.concat([df_receita, df_despesa], ignore_index=True)
