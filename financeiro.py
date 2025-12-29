import pandas as pd
from database import conectar
from datetime import datetime
from dateutil.relativedelta import relativedelta
from datetime import date, timedelta

# ================= CLIENTES =================
def inserir_cliente(nome, telefone, email, obs):
    conn = conectar()
    conn.execute(
        """
        INSERT INTO clientes (nome, telefone, email, observacoes)
        VALUES (?, ?, ?, ?)
        """,
        (nome, telefone, email, obs),
    )
    conn.commit()
    conn.close()

def listar_clientes():
    conn = conectar()
    df = pd.read_sql("SELECT * FROM clientes", conn)
    conn.close()
    return df


# ================= SERVIÇOS =================
def inserir_servico(cliente_id, descricao, valor, data_servico):
    data = datetime.strptime(str(data_servico), "%Y-%m-%d")
    proxima = data + relativedelta(months=4)

    conn = conectar()
    conn.execute(
        """
        INSERT INTO servicos
        (cliente_id, descricao, valor, data_servico, proxima_manutencao)
        VALUES (?, ?, ?, ?, ?)
        """,
        (cliente_id, descricao, valor, str(data.date()), str(proxima.date()))
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
        WHERE date(s.data_servico) <= date('now')
        ORDER BY s.data_servico DESC
        """,
        conn
    )
    conn.close()
    return df


def listar_alertas_manutencao(dias):
    from datetime import date, timedelta

    conn = conectar()

    hoje = date.today()
    limite = hoje + timedelta(days=dias)

    # 🔴 VENCIDAS
    vencidas = pd.read_sql(
        """
        SELECT
            s.id,
            c.nome AS cliente,
            c.telefone,
            s.descricao,
            s.data_servico,
            s.proxima_manutencao
        FROM servicos s
        JOIN clientes c ON c.id = s.cliente_id
        WHERE s.proxima_manutencao IS NOT NULL
          AND date(s.proxima_manutencao) < date(?)
        ORDER BY date(s.proxima_manutencao)
        """,
        conn,
        params=(hoje.isoformat(),)
    )

    # 🟡 A VENCER (CORRIGIDO)
    a_vencer = pd.read_sql(
        """
        SELECT
            s.id,
            c.nome AS cliente,
            c.telefone,
            s.descricao,
            s.data_servico,
            s.proxima_manutencao
        FROM servicos s
        JOIN clientes c ON c.id = s.cliente_id
        WHERE s.proxima_manutencao IS NOT NULL
          AND date(s.proxima_manutencao) >= date(?)
          AND date(s.proxima_manutencao) <= date(?)
        ORDER BY date(s.proxima_manutencao)
        """,
        conn,
        params=(hoje.isoformat(), limite.isoformat())
    )

    conn.close()
    return vencidas, a_vencer




# ================= DESPESAS =================
def inserir_despesa(tipo, descricao, valor, data):
    conn = conectar()
    conn.execute(
        """
        INSERT INTO despesas (tipo, descricao, valor, data)
        VALUES (?, ?, ?, ?)
        """,
        (tipo, descricao, valor, str(data))
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
        conn
    )
    conn.close()
    return df

# ================= DASHBOARD =================
def resumo_financeiro():
    conn = conectar()

    df_receita = pd.read_sql(
        "SELECT SUM(valor) AS total_receita FROM servicos",
        conn
    )

    df_despesa = pd.read_sql(
        "SELECT SUM(valor) AS total_despesa FROM despesas",
        conn
    )

    conn.close()

    receita = df_receita["total_receita"].iloc[0] or 0
    despesa = df_despesa["total_despesa"].iloc[0] or 0
    lucro = receita - despesa

    return receita, despesa, lucro

# ================= DASHBOARD POR PERÍODO =================
def resumo_financeiro_periodo(data_inicio, data_fim):
    conn = conectar()

    df_receita = pd.read_sql(
        """
        SELECT SUM(valor) AS total_receita
        FROM servicos
        WHERE data_servico BETWEEN ? AND ?
        """,
        conn,
        params=(str(data_inicio), str(data_fim))
    )

    df_despesa = pd.read_sql(
        """
        SELECT SUM(valor) AS total_despesa
        FROM despesas
        WHERE data BETWEEN ? AND ?
        """,
        conn,
        params=(str(data_inicio), str(data_fim))
    )

    conn.close()

    receita = df_receita["total_receita"].iloc[0] or 0
    despesa = df_despesa["total_despesa"].iloc[0] or 0
    lucro = receita - despesa

    return receita, despesa, lucro

def dados_grafico_periodo(data_inicio, data_fim):
    conn = conectar()

    df_receita = pd.read_sql(
        """
        SELECT data_servico AS data, valor, 'Receita' AS tipo
        FROM servicos
        WHERE data_servico BETWEEN ? AND ?
        """,
        conn,
        params=(str(data_inicio), str(data_fim))
    )

    df_despesa = pd.read_sql(
        """
        SELECT data AS data, valor, 'Despesa' AS tipo
        FROM despesas
        WHERE data BETWEEN ? AND ?
        """,
        conn,
        params=(str(data_inicio), str(data_fim))
    )

    conn.close()

    df = pd.concat([df_receita, df_despesa])
    df["data"] = pd.to_datetime(df["data"])

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
            s.data_servico,
            s.proxima_manutencao
        FROM servicos s
        JOIN clientes c ON c.id = s.cliente_id
        WHERE s.data_servico BETWEEN ? AND ?
        ORDER BY s.data_servico DESC
        """,
        conn,
        params=(str(data_inicio), str(data_fim))
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
        ORDER BY data DESC
        """,
        conn,
        params=(str(data_inicio), str(data_fim))
    )
    conn.close()
    return df

# ================= AGENDA =================
def inserir_agenda(data, horario, cliente_nome, cliente_id, descricao, valor, status):
    conn = conectar()
    conn.execute(
        """
        INSERT INTO agenda
        (data, horario, cliente, cliente_id, descricao, valor, status, convertido)
        VALUES (?, ?, ?, ?, ?, ?, ?, 0)
        """,
        (str(data), horario, cliente_nome, cliente_id, descricao, valor, status)
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
            a.descricao,
            a.valor,
            a.status,
            a.cliente_id,
            c.nome AS cliente,
            c.email,
            c.telefone,
            c.observacoes
        FROM agenda a
        JOIN clientes c ON c.id = a.cliente_id
        ORDER BY a.data, a.horario
        """,
        conn
    )

    conn.close()
    return df



def concluir_agenda(id_agenda, conn=None):
    fechar_conn = False
    if conn is None:
        conn = conectar()
        fechar_conn = True

    # Verifica se já foi convertido
    df_check = pd.read_sql(
        "SELECT convertido FROM agenda WHERE id = ?",
        conn,
        params=(id_agenda,)
    )

    if df_check.empty or df_check.loc[0, "convertido"] == 1:
        if fechar_conn:
            conn.close()
        return

    # Busca dados completos da agenda
    df = pd.read_sql(
        """
        SELECT
            a.data,
            a.descricao,
            a.valor,
            a.cliente_id
        FROM agenda a
        WHERE a.id = ?
        """,
        conn,
        params=(id_agenda,)
    )

    if df.empty:
        if fechar_conn:
            conn.close()
        return

    # Insere em serviços
    conn.execute(
        """
        INSERT INTO servicos
        (cliente_id, descricao, valor, data_servico, proxima_manutencao)
        VALUES (?, ?, ?, ?, date(?, '+120 day'))
        """,
        (
            int(df.loc[0, "cliente_id"]),
            df.loc[0, "descricao"],
            df.loc[0, "valor"] or 0,
            df.loc[0, "data"],
            df.loc[0, "data"]
        )
    )

    # Marca como convertido
    conn.execute(
        "UPDATE agenda SET convertido = 1 WHERE id = ?",
        (id_agenda,)
    )

    if fechar_conn:
        conn.commit()
        conn.close()


def atualizar_status_agenda(id_agenda, novo_status):
    conn = conectar()

    # Atualiza status
    conn.execute(
        "UPDATE agenda SET status = ? WHERE id = ?",
        (novo_status, id_agenda)
    )

    # Se concluiu, converte em serviço
    if novo_status == "concluída":
        concluir_agenda(id_agenda, conn)

    conn.commit()
    conn.close()

def listar_agenda_mes(ano, mes):
    conn = conectar()

    df = pd.read_sql(
        """
        SELECT
            a.id,
            a.data,
            a.descricao,
            a.valor,
            a.status,
            c.nome AS cliente
        FROM agenda a
        JOIN clientes c ON c.id = a.cliente_id
        WHERE strftime('%Y', a.data) = ?
          AND strftime('%m', a.data) = ?
        ORDER BY a.data
        """,
        conn,
        params=(str(ano), f"{mes:02d}")
    )

    conn.close()
    df["data"] = pd.to_datetime(df["data"])
    return df


def marcar_alerta_resolvido(id_agenda):
    conn = conectar()
    conn.execute(
        "UPDATE agenda SET alerta_resolvido = 1 WHERE id = ?",
        (id_agenda,)
    )
    conn.commit()
    conn.close()


def buscar_cliente_por_servico(servico_id):
    import pandas as pd
    import sqlite3

    conn = sqlite3.connect("megatech.db")

    query = """
    SELECT c.id, c.nome
    FROM servicos s
    JOIN clientes c ON c.id = s.cliente_id
    WHERE s.id = ?
    """

    df = pd.read_sql(query, conn, params=(servico_id,))
    conn.close()
    return df
