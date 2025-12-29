# 💻 Megatech – Sistema de Controle Financeiro

Sistema web desenvolvido em **Python + Streamlit** para controle financeiro simples e eficiente, voltado para pequenos negócios, prestadores de serviço e profissionais autônomos.

O sistema permite o gerenciamento de **clientes**, **serviços**, **despesas**, **agenda**, **alertas de manutenção** e **resumo financeiro**, tudo de forma centralizada.

---

## 🚀 Funcionalidades

### 📌 Clientes
- Cadastro de clientes
- Listagem e consulta rápida

### 🛠️ Serviços
- Registro de serviços executados
- Associação do serviço a um cliente
- Controle de valores e datas
- Histórico completo de serviços

### 💸 Despesas
- Registro de despesas operacionais
- Classificação por data e valor
- Visualização organizada

### 📅 Agenda
- Cadastro de agendamentos
- Atualização de status (pendente, concluído, cancelado)
- Visualização mensal
- Controle de compromissos futuros

### ⚠️ Alertas de Manutenção
- Alertas automáticos baseados em períodos
- Apoio ao controle de manutenções recorrentes

### 📊 Resumo Financeiro
- Resumo por período
- Visão clara de entradas, saídas e saldo
- Apoio à tomada de decisão

---

## 🧱 Tecnologias Utilizadas

- **Python 3**
- **Streamlit**
- **Pandas**
- **SQLite** (banco de dados local)
- Estrutura modular (separação por arquivos)

---

## 📂 Estrutura do Projeto

```text
📁 projeto/
│
├── app.py                # Arquivo principal (Streamlit)
├── database.py           # Criação e conexão com o banco
├── financeiro.py         # Regras de negócio e consultas
├── requirements.txt      # Dependências do projeto
└── README.md             # Documentação
