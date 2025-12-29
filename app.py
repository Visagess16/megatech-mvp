import streamlit as st
import pandas as pd
from datetime import date
import calendar

from database import criar_tabelas
from financeiro import *

# ================= ESTADO GLOBAL =================
if "agendar_alerta" not in st.session_state:
    st.session_state.agendar_alerta = None

STATUS_CORES = {
    "agendado": "#4CAF50",
    "confirmar agendamento": "#FFC107",
    "concluída": "#2196F3"
}

# ================= INIT =================
criar_tabelas()

st.set_page_config(
    page_title="Megatech - Controle",
    layout="wide"
)

st.title("🛠️ Megatech - Controle de Clientes e Serviços")

abas = st.tabs([
    "👤 Clientes",
    "🛠️ Serviços",
    "💸 Gastos",
    "⏰ Alertas",
    "📊 Dashboard",
    "📅 Agenda",
    "🗓️ Agenda Mensal"
])

# =================================================
# ================= CLIENTES ======================
# =================================================
with abas[0]:
    st.subheader("Cadastro de Clientes")

    nome = st.text_input("Nome")
    tel = st.text_input("Telefone")
    email = st.text_input("Email")
    obs = st.text_area("Observações")

    if st.button("Salvar Cliente"):
        inserir_cliente(nome, tel, email, obs)
        st.success("Cliente cadastrado!")
        st.rerun()

    st.dataframe(listar_clientes(), use_container_width=True)

# =================================================
# ================= SERVIÇOS ======================
# =================================================
with abas[1]:
    st.subheader("Registro de Serviços")

    clientes_df = listar_clientes()

    if clientes_df.empty:
        st.warning("Cadastre um cliente antes.")
    else:
        clientes_dict = {
            f"{row['id']} - {row['nome']}": int(row["id"])
            for _, row in clientes_df.iterrows()
        }

        with st.form("form_servico", clear_on_submit=True):
            cliente_label = st.selectbox("Cliente", list(clientes_dict.keys()))
            cliente_id = clientes_dict[cliente_label]

            descricao = st.text_input("Descrição do serviço")
            valor = st.number_input("Valor (R$)", min_value=0.0)
            data_servico = st.date_input("Data do serviço")

            salvar = st.form_submit_button("Salvar Serviço")

        if salvar:
            inserir_servico(cliente_id, descricao, valor, data_servico)
            st.success("Serviço registrado!")
            st.rerun()

    st.divider()
    st.subheader("Histórico de Serviços Executados")
    st.dataframe(listar_servicos_executados(), use_container_width=True)

# =================================================
# ================= GASTOS ========================
# =================================================
with abas[2]:
    st.subheader("Registro de Gastos")

    with st.form("form_gastos", clear_on_submit=True):
        tipo = st.selectbox("Tipo", ["Fixo", "Variável"])
        descricao = st.text_input("Descrição")
        valor = st.number_input("Valor (R$)", min_value=0.0, step=10.0)
        data_gasto = st.date_input("Data")

        salvar = st.form_submit_button("Salvar Gasto")

    if salvar:
        inserir_despesa(tipo.lower(), descricao, valor, data_gasto)
        st.success("Gasto registrado!")
        st.rerun()

    st.divider()
    st.subheader("Histórico de Gastos")
    st.dataframe(listar_despesas(), use_container_width=True)

# =================================================
# ================= ALERTAS =======================
# =================================================
with abas[3]:
    st.subheader("⏰ Alertas de Manutenção")

    dias = st.slider("Próximos dias", 7, 365, 30)

    vencidas, a_vencer = listar_alertas_manutencao(dias)

    st.subheader("🚨 Manutenções Vencidas")

    if vencidas.empty:
        st.success("Nenhuma manutenção vencida 🎉")
    else:
        for _, row in vencidas.iterrows():
            st.markdown(
                f"""
                **Cliente:** {row['cliente']}  
                **Serviço:** {row['descricao']}  
                **Próxima manutenção:** 🔴 {row['proxima_manutencao']}  
                📞 {row['telefone']}
                """
            )

            if st.button("🗓️ Agendar agora", key=f"ag_{row['id']}"):
                st.session_state.agendar_alerta = {
                    "cliente_id": row["id"],
                    "cliente_nome": row["cliente"],
                    "descricao": row["descricao"]
                }
                st.success("Vá para a aba Agenda para concluir o agendamento.")

            st.divider()

    st.subheader("⏳ A Vencer")
    st.dataframe(a_vencer, use_container_width=True)

# =================================================
# ================= DASHBOARD =====================
# =================================================
with abas[4]:
    st.subheader("📊 Dashboard Financeiro")

    with st.form("filtro_dashboard"):
        col1, col2 = st.columns(2)
        with col1:
            inicio = st.date_input("Data inicial", value=date(date.today().year, date.today().month, 1))
        with col2:
            fim = st.date_input("Data final", value=date.today())

        aplicar = st.form_submit_button("Aplicar")

    if aplicar and inicio <= fim:
        receita, despesa, lucro = resumo_financeiro_periodo(inicio, fim)

        c1, c2, c3 = st.columns(3)
        c1.metric("💰 Receita", f"R$ {receita:,.2f}")
        c2.metric("💸 Despesas", f"R$ {despesa:,.2f}")
        c3.metric("📈 Lucro", f"R$ {lucro:,.2f}")

        st.divider()
        st.dataframe(dados_grafico_periodo(inicio, fim), use_container_width=True)

# =================================================
# ================= AGENDA ========================
# =================================================
with abas[5]:
    st.subheader("📅 Agenda de Manutenções")

    clientes_df = listar_clientes()
    if clientes_df.empty:
        st.warning("Cadastre clientes primeiro.")
        st.stop()

    # ---------- CLIENTES ----------
    clientes_dict = {
        f"{row['id']} - {row['nome']}": int(row["id"])
        for _, row in clientes_df.iterrows()
    }

    # ---------- DADOS VINDOS DO ALERTA ----------
    dados = st.session_state.get("agendar_alerta")

    cliente_padrao = None
    descricao_padrao = ""

    if isinstance(dados, dict):
        cliente_id_alerta = dados.get("cliente_id")
        cliente_nome_alerta = dados.get("cliente_nome")

        if cliente_id_alerta and cliente_nome_alerta:
            cliente_padrao = f"{cliente_id_alerta} - {cliente_nome_alerta}"

        descricao_padrao = dados.get("descricao", "")

    lista_clientes = list(clientes_dict.keys())
    index_cliente = (
        lista_clientes.index(cliente_padrao)
        if cliente_padrao in lista_clientes
        else 0
    )

    # ---------- FORMULÁRIO ----------
    with st.form("form_agenda", clear_on_submit=True):
        data = st.date_input("Data", value=date.today())
        horario = st.text_input("Horário")

        cliente_label = st.selectbox(
            "Cliente",
            lista_clientes,
            index=index_cliente
        )

        cliente_id = clientes_dict[cliente_label]
        cliente_nome = cliente_label.split(" - ", 1)[1]

        descricao = st.text_input(
            "Descrição",
            value=descricao_padrao
        )

        valor = st.number_input(
            "Valor (R$)",
            min_value=0.0,
            step=10.0
        )

        status = st.selectbox(
            "Status",
            ["Agendado", "Confirmar Agendamento", "Concluída"]
        )

        salvar = st.form_submit_button("Salvar")

    # ---------- SALVAR ----------
    if salvar:
        inserir_agenda(
            data,
            horario,
            cliente_nome,
            cliente_id,
            descricao,
            valor,
            status.lower()
        )

        # limpa o estado do alerta
        st.session_state.agendar_alerta = None

        st.success("Agendamento salvo!")
        st.rerun()

    # ---------- LISTAGEM ----------
    st.divider()
    st.subheader("📋 Agenda Cadastrada")
    st.dataframe(listar_agenda(), use_container_width=True)

# =================================================
# ================= AGENDA MENSAL =================
# =================================================
with abas[6]:
    st.subheader("🗓️ Agenda Mensal")

    col1, col2 = st.columns(2)
    with col1:
        mes = st.selectbox("Mês", list(range(1, 13)), index=date.today().month - 1)
    with col2:
        ano = st.number_input("Ano", 2023, 2035, date.today().year)

    df = listar_agenda_mes(ano, mes)

    if df.empty:
        st.info("Nenhum agendamento.")
    else:
        cal = calendar.Calendar()
        for semana in cal.monthdatescalendar(ano, mes):
            cols = st.columns(7)
            for i, dia in enumerate(semana):
                with cols[i]:
                    if dia.month != mes:
                        st.write("")
                    else:
                        st.markdown(f"**{dia.day}**")
                        eventos = df[df["data"].dt.date == dia]
                        for _, ev in eventos.iterrows():
                            cor = STATUS_CORES.get(ev["status"], "#E0E0E0")
                            st.markdown(
                                f"""
                                <div style="
                                    background:{cor};
                                    padding:6px;
                                    border-radius:6px;
                                    font-size:12px;
                                ">
                                <b>{ev['cliente']}</b><br>
                                {ev['descricao']}
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
