import streamlit as st
import pandas as pd
from datetime import date
import calendar
import plotly.express as px
from database import criar_tabelas
from financeiro import *
if "tema" not in st.session_state:
    st.session_state.tema = "claro"

# =================================================
# ================= CONFIG PAGE ===================
# =================================================
st.set_page_config(
    page_title="Megatech | Gestão de Serviços",
    page_icon="🛠️",
    layout="wide"
)

# =================================================
# ================= CSS GLOBAL ====================
# =================================================
st.markdown("""
<style>
/* Cards */
div[data-testid="stContainer"] {
    border-radius: 14px;
}

/* Botões */
button {
    border-radius: 10px !important;
    font-weight: 600;
}

/* Inputs */
input, textarea, select {
    border-radius: 8px !important;
}

/* Títulos */
h1, h2, h3 {
    letter-spacing: 0.5px;
}
</style>
""", unsafe_allow_html=True)

if st.session_state.tema == "escuro":
    st.markdown("""
    <style>
    body {
        background-color: #0e1117;
        color: #fafafa;
    }

    section[data-testid="stSidebar"] {
        background-color: #111827;
        border-right: 1px solid #1f2937;
    }

    div[data-testid="stContainer"] {
        background-color: #161b22;
        border-radius: 12px;
    }

    input, textarea, select {
        background-color: #0e1117 !important;
        color: #fafafa !important;
    }

    .stDataFrame {
        background-color: #0e1117;
    }

    </style>
    """, unsafe_allow_html=True)

else:
    st.markdown("""
    <style>
    body {
        background-color: #ffffff;
        color: #000000;
    }

    section[data-testid="stSidebar"] {
        background-color: #fafafa;
        border-right: 1px solid #e0e0e0;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("""
<style>
.badge {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 600;
    margin-top: 6px;
}

.badge-agendado {
    background-color: #22c55e;
    color: white;
}

.badge-confirmar {
    background-color: #facc15;
    color: #1f2937;
}

.badge-concluida {
    background-color: #3b82f6;
    color: white;
}
</style>
""", unsafe_allow_html=True)


# =================================================


def badge_status(status):
    mapa = {
        "agendado": ("Agendado", "badge-agendado"),
        "confirmar agendamento": ("Confirmar Agendamento", "badge-confirmar"),
        "concluída": ("Concluída", "badge-concluida"),
    }

    texto, classe = mapa.get(status, (status, "badge-agendado"))

    return f"<span class='badge {classe}'>{texto}</span>"



# ================= INIT ==========================
# =================================================
criar_tabelas()

if "agendar_alerta" not in st.session_state:
    st.session_state.agendar_alerta = None

STATUS_CORES = {
    "agendado": "#4CAF50",
    "confirmar agendamento": "#FFC107",
    "concluída": "#2196F3"
}

# =================================================
# ================= CABEÇALHO =====================
# =================================================
st.title("🛠️ Megatech")
st.caption("Sistema profissional de controle de clientes, serviços, agenda e financeiro")
st.divider()

with st.sidebar:
    st.markdown("## 🛠️ Megatech")
    st.caption("Gestão de serviços")

    menu = st.radio(
        "Navegação",
        [
            "👤 Clientes",
            "🛠️ Serviços",
            "💸 Gastos",
            "⏰ Alertas",
            "📊 Painel de Controle",
            "📅 Agenda",
            "🗓️ Agenda Mensal"
        ],
        label_visibility="collapsed"
    )

    st.divider()
    st.caption("© Megatech")

st.divider()
modo_escuro = st.toggle("🌙 Modo escuro", value=st.session_state.tema == "escuro")

if modo_escuro:
    st.session_state.tema = "escuro"
else:
    st.session_state.tema = "claro"


if st.session_state.tema == "escuro":
    st.markdown("""
    <style>
    body {
        background-color: #0e1117;
        color: #fafafa;
    }

    section[data-testid="stSidebar"] {
        background-color: #111827;
        border-right: 1px solid #1f2937;
    }

    div[data-testid="stContainer"] {
        background-color: #161b22;
        border-radius: 12px;
    }

    input, textarea, select {
        background-color: #0e1117 !important;
        color: #fafafa !important;
    }

    .stDataFrame {
        background-color: #0e1117;
    }

    </style>
    """, unsafe_allow_html=True)

else:
    st.markdown("""
    <style>
    body {
        background-color: #ffffff;
        color: #000000;
    }

    section[data-testid="stSidebar"] {
        background-color: #fafafa;
        border-right: 1px solid #e0e0e0;
    }
    </style>
    """, unsafe_allow_html=True)


# =================================================
# ================= CLIENTES ======================
# =================================================
if menu == "👤 Clientes":
    st.caption("Cadastro e visualização dos clientes")
    st.divider()

    col_form, col_lista = st.columns([1, 2], gap="large")

    with col_form:
        with st.container(border=True):
            st.markdown("### ➕ Novo Cliente")
            nome = st.text_input("👤 Nome")
            tel = st.text_input("📞 Telefone")
            email = st.text_input("📧 Email")
            obs = st.text_area("📝 Observações")

            if st.button("💾 Salvar Cliente", use_container_width=True):
                inserir_cliente(nome, tel, email, obs)
                st.success("Cliente cadastrado!")
                st.rerun()

    with col_lista:
        st.markdown("### 📋 Clientes Cadastrados")
        st.dataframe(listar_clientes(), use_container_width=True, hide_index=True)

# =================================================
# ================= SERVIÇOS ======================
# =================================================
if menu == "🛠️ Serviços":
    st.subheader("🛠️ Registro de Serviços")
    st.caption("Cadastro e histórico de serviços")
    st.divider()

    clientes_df = listar_clientes()

    if clientes_df.empty:
        st.warning("Cadastre um cliente antes.")
    else:
        col_form, col_lista = st.columns([1, 2], gap="large")

        clientes_dict = {
            f"{row['id']} - {row['nome']}": int(row["id"])
            for _, row in clientes_df.iterrows()
        }

        with col_form:
            with st.container(border=True):
                with st.form("form_servico", clear_on_submit=True):
                    cliente_label = st.selectbox("Cliente", list(clientes_dict.keys()))
                    cliente_id = clientes_dict[cliente_label]

                    descricao = st.text_input("Descrição")
                    valor = st.number_input("Valor (R$)", min_value=0.0)
                    data_servico = st.date_input("Data", value=date.today())

                    salvar = st.form_submit_button("💾 Salvar Serviço")

                if salvar:
                    inserir_servico(cliente_id, descricao, valor, data_servico)
                    st.success("Serviço registrado!")
                    st.rerun()

        with col_lista:
            st.markdown("### 📑 Histórico de Serviços")
            st.dataframe(listar_servicos_executados(), use_container_width=True, hide_index=True)

# =================================================
# ================= GASTOS ========================
# =================================================
if menu == "💸 Gastos":
    st.subheader("💸 Controle de Gastos")
    st.caption("Despesas fixas e variáveis")
    st.divider()

    col_form, col_lista = st.columns([1, 2], gap="large")

    with col_form:
        with st.container(border=True):
            with st.form("form_gastos", clear_on_submit=True):
                tipo = st.selectbox("Tipo", ["Fixo", "Variável"])
                descricao = st.text_input("Descrição")
                valor = st.number_input("Valor (R$)", min_value=0.0, step=10.0)
                data_gasto = st.date_input("Data", value=date.today())

                salvar = st.form_submit_button("💾 Salvar Gasto")

            if salvar:
                inserir_despesa(tipo.lower(), descricao, valor, data_gasto)
                st.success("Gasto registrado!")
                st.rerun()

    with col_lista:
        st.markdown("### 📑 Histórico de Gastos")
        st.dataframe(listar_despesas(), use_container_width=True, hide_index=True)

# =================================================
# ================= ALERTAS =======================
# =================================================
if menu == "⏰ Alertas":
    st.subheader("⏰ Alertas de Manutenção")
    st.caption("Manutenções vencidas e a vencer")
    st.divider()

    dias = st.slider("Próximos dias", 7, 365, 30)

    vencidas, a_vencer = listar_alertas_manutencao(dias)

    st.markdown("### 🚨 Vencidas")
    if vencidas.empty:
        st.success("Nenhuma vencida 🎉")
    else:
        for _, row in vencidas.iterrows():
            with st.container(border=True):
                st.markdown(f"""
                **Cliente:** {row['cliente']}  
                **Serviço:** {row['descricao']}  
                🔴 **Próxima manutenção:** {row['proxima_manutencao']}  
                📞 {row['telefone']}
                """)

                if st.button("🗓️ Agendar agora", key=f"ag_{row['id']}"):
                    st.session_state.agendar_alerta = row
                    st.success("Vá para a aba Agenda.")

    st.divider()
    st.markdown("### ⏳ A vencer")
    st.dataframe(a_vencer, use_container_width=True, hide_index=True)

# =================================================
# ================= DASHBOARD =====================
# =================================================
if menu == "📊 Painel de Controle":
    st.subheader("📊 Painel de Controle")
    st.caption("Análise financeira e operacional do período")
    st.divider()

    # ================= FILTRO =================
    with st.form("filtro_dashboard"):
        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            inicio = st.date_input(
                "Data inicial",
                value=st.session_state.get("dt_inicio", date.today().replace(day=1))
            )

        with col2:
            fim = st.date_input(
                "Data final",
                value=st.session_state.get("dt_fim", date.today())
            )

        with col3:
            aplicar = st.form_submit_button("🔎 Aplicar")

    if aplicar:
        st.session_state.dt_inicio = inicio
        st.session_state.dt_fim = fim
    else:
        inicio = st.session_state.get("dt_inicio", inicio)
        fim = st.session_state.get("dt_fim", fim)

    if inicio > fim:
        st.warning("Data inicial não pode ser maior que a final.")
        st.stop()

    # ================= RESUMO =================
    receita, despesa, lucro = resumo_financeiro_periodo(inicio, fim)

    c1, c2, c3 = st.columns(3)
    c1.metric("💰 Receita", f"R$ {receita:,.2f}")
    c2.metric("💸 Despesas", f"R$ {despesa:,.2f}")
    c3.metric("📈 Lucro", f"R$ {lucro:,.2f}")

    st.divider()

    # ================= GRÁFICOS =================
    col_g1, col_g2 = st.columns(2, gap="large")

    # -------- PIZZA: RECEITA X DESPESA --------
    with col_g1:
        st.markdown("### 🥧 Receita x Despesas")

        df_pizza = pd.DataFrame({
            "Tipo": ["Receita", "Despesas"],
            "Valor": [receita, despesa]
        })

        st.plotly_chart(
            px.pie(
                df_pizza,
                names="Tipo",
                values="Valor",
                hole=0.4
            ),
            use_container_width=True
        )

    # -------- BARRAS: SERVIÇOS MAIS EXECUTADOS --------
    with col_g2:
        st.markdown("### 🛠️ Serviços mais executados")

        df_serv = listar_servicos_periodo(inicio, fim)

        if df_serv.empty:
            st.info("Nenhum serviço no período.")
        else:
            servicos_top = (
                df_serv
                .groupby("descricao")
                .size()
                .reset_index(name="quantidade")
                .sort_values("quantidade", ascending=False)
                .head(10)
            )

            st.plotly_chart(
                px.bar(
                    servicos_top,
                    x="descricao",
                    y="quantidade",
                    text="quantidade"
                ),
                use_container_width=True
            )

    st.divider()

    # ================= CLIENTES MAIS REPRESENTATIVOS =================
    st.markdown("### 👥 Clientes mais representativos")

    df_clientes = listar_servicos_periodo(inicio, fim)

    if df_clientes.empty:
        st.info("Sem dados para análise.")
    else:
        clientes_top = (
            df_clientes
            .groupby("cliente")
            .agg(
                total_faturado=("valor", "sum"),
                qtd_servicos=("valor", "count")
            )
            .reset_index()
            .sort_values("total_faturado", ascending=False)
            .head(10)
        )

        col_tabela, col_graf = st.columns([1, 1.2], gap="large")

        with col_tabela:
            st.dataframe(
                clientes_top,
                use_container_width=True,
                hide_index=True
            )

        with col_graf:
            st.plotly_chart(
                px.bar(
                    clientes_top,
                    x="cliente",
                    y="total_faturado",
                    text_auto=".2s"
                ),
                use_container_width=True
            )

# =================================================
# ================= AGENDA ========================
# =================================================
elif menu == "📅 Agenda":
    st.subheader("📋 Agendamentos")
    st.caption("Agendamento, acompanhamento e atualização de status")
    st.divider()

    clientes_df = listar_clientes()
    if clientes_df.empty:
        st.warning("Cadastre clientes antes de utilizar a agenda.")
        st.stop()

    # Mapa de clientes
    clientes_map = {
        int(row["id"]): row
        for _, row in clientes_df.iterrows()
    }

    clientes_dict = {
        f"{row['id']} - {row['nome']}": int(row["id"])
        for _, row in clientes_df.iterrows()
    }

    col_form, col_cards = st.columns([1, 2], gap="large")

    # ================= FORMULÁRIO =================
    with col_form:
        with st.container(border=True):
            st.markdown("### ➕ Novo Agendamento")

            with st.form("form_agenda", clear_on_submit=True):
                data = st.date_input("📅 Data", value=date.today())
                horario = st.text_input("⏰ Horário")

                cliente_label = st.selectbox("👤 Cliente", list(clientes_dict.keys()))
                cliente_id = clientes_dict[cliente_label]
                cliente_nome = clientes_map[cliente_id]["nome"]

                descricao = st.text_input("📝 Descrição do serviço")
                valor = st.number_input("💰 Valor (R$)", min_value=0.0, step=10.0)

                status = st.selectbox(
                    "📌 Status",
                    ["Agendado", "Confirmar Agendamento", "Concluída"]
                )

                salvar = st.form_submit_button("💾 Salvar Agendamento")

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
                st.success("Agendamento salvo com sucesso!")
                st.rerun()

    # ================= CARDS =================
    with col_cards:
        st.markdown("### 📋 Agendamentos Cadastrados")

        df_agenda = listar_agenda()

        if df_agenda.empty:
            st.info("Nenhum agendamento cadastrado.")
        else:
            for _, row in df_agenda.iterrows():
                cliente = clientes_map.get(row["cliente_id"], {})

                with st.container(border=True):
                    st.markdown(f"### 👤 {row['cliente']}")
                    st.markdown(f"**🛠 Serviço:** {row['descricao']}")

                    st.markdown(
                        f"📅 **Data:** {row['data']} &nbsp;&nbsp; ⏰ **Horário:** {row['horario']}"
                    )

                    st.markdown(f"💰 **Valor:** R$ {row['valor']:,.2f}")
                    st.markdown(f"📞 **Telefone:** {cliente.get('telefone', '-')}")
                    st.markdown(f"📧 **E-mail:** {cliente.get('email', '-')}")

                    if cliente.get("observacoes"):
                        st.info(f"📝 {cliente['observacoes']}")

                    st.markdown(
                         f"📌 Status:&nbsp; {badge_status(row['status'])}",
                         unsafe_allow_html=True
)


                    # -------- ATUALIZAR STATUS --------
                    with st.form(f"status_{row['id']}"):
                        novo_status = st.selectbox(
                            "Atualizar status",
                            ["Agendado", "Confirmar Agendamento", "Concluída"],
                            index=["agendado", "confirmar agendamento", "concluída"].index(row["status"]),
                            label_visibility="collapsed"
                        )

                        atualizar = st.form_submit_button("🔄 Atualizar status")

                        if atualizar:
                            atualizar_status_agenda(row["id"], novo_status.lower())

                            if novo_status.lower() == "concluída":
                                if not servico_existe(
                                    row["cliente_id"],
                                    row["descricao"],
                                    row["data"]
                                ):
                                    inserir_servico(
                                        row["cliente_id"],
                                        row["descricao"],
                                        row["valor"],
                                        row["data"]
                                    )

                            st.success("Status atualizado com sucesso!")
                            st.rerun()

# ================= AGENDA MENSAL =================
# =================================================
if menu == "🗓️ Agenda Mensal":
    st.subheader("🗓️ Agenda Mensal")
    st.caption("Visão mensal dos atendimentos")
    st.divider()

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
                    if dia.month == mes:
                        st.markdown(f"**{dia.day}**")
                        eventos = df[df["data"].dt.date == dia]
                        for _, ev in eventos.iterrows():
                            cor = STATUS_CORES.get(ev["status"], "#E0E0E0")
                            st.markdown(
                                f"<div style='background:{cor};padding:6px;border-radius:6px;font-size:12px;'>"
                                f"<b>{ev['cliente']}</b><br>{ev['descricao']}</div>",
                                unsafe_allow_html=True
                            )
