import streamlit as st
import re
from datetime import datetime
import pandas as pd
import plotly.express as px
import difflib
import random

# ==========================================
# 1. CONFIGURAÇÃO E DESIGN MODO ESCURO
# ==========================================
st.set_page_config(page_title="Organizé", page_icon="💸", layout="wide", initial_sidebar_state="expanded")

st.markdown('''
<style>
    .stApp { background-color: #0E1117; }
    
    /* Barra lateral */
    [data-testid="stSidebar"] {
        background-color: #050505;
        border-right: 1px solid #1C2621;
    }
    
    /* Novo Design dos Botões de Navegação */
    [data-testid="stSidebar"] button {
        border-radius: 8px !important;
        padding: 15px !important;
        border: none !important;
        display: flex !important;
        justify-content: flex-start !important;
        transition: background-color 0.3s !important;
    }
    
    [data-testid="stSidebar"] button p {
        font-size: 1.25rem !important;
        margin: 0 !important;
    }

    [data-testid="stSidebar"] button[kind="secondary"] {
        background-color: transparent !important;
        color: #e2e8f0 !important;
    }
    
    [data-testid="stSidebar"] button[kind="secondary"]:hover {
        background-color: #121619 !important;
        color: #00C853 !important;
    }

    [data-testid="stSidebar"] button[kind="primary"] {
        background-color: #00C853 !important;
        color: #050505 !important;
        font-weight: 600 !important;
    }

    h1, h2, h3 { color: #00C853 !important; }
</style>
''', unsafe_allow_html=True)

# ==========================================
# 2. DADOS E MEMÓRIA
# ==========================================
categorias_map = {
    "Alimentação": ("mercado", "lanche", "ifood", "pizza", "restaurante", "comida", "padaria", "cantina"),
    "Transporte": ("uber", "ônibus", "gasolina", "posto", "passagem", "pedágio", "99"),
    "Lazer": ("cinema", "festa", "jogo", "bar", "show", "ingresso", "futebol", "esporte"),
    "Moradia": ("aluguel", "luz", "água", "internet", "condomínio", "conta")
}

dicas_financeiras = [
    "Evite compras por impulso: espere 24h antes de comprar algo não essencial.",
    "Pague-se primeiro: reserve uma parte do seu dinheiro logo que receber.",
    "Pequenos gastos diários (como o cafézinho) somam grandes valores no final do mês.",
    "Construa uma reserva de emergência equivalente a 6 meses dos seus custos fixos.",
    "Não use o cartão de crédito como extensão do seu salário."
]

if "transacoes" not in st.session_state:
    st.session_state.transacoes = []
    
if "mensagens_chat" not in st.session_state:
    st.session_state.mensagens_chat = [
        {"role": "assistant", "content": "Olá! Pode mandar os seus gastos e ganhos aqui (ex: 'Gastei 50 no ifood')."}
    ]

if "menu_navegacao" not in st.session_state:
    st.session_state.menu_navegacao = "💬 Chat de Lançamentos"

if "mudar_pagina" not in st.session_state:
    st.session_state.mudar_pagina = None

if st.session_state.mudar_pagina:
    st.session_state.menu_navegacao = st.session_state.mudar_pagina
    st.session_state.mudar_pagina = None

if "dica_atual" not in st.session_state:
    st.session_state.dica_atual = random.choice(dicas_financeiras)

# ==========================================
# 3. BARRA LATERAL (MENU DE NAVEGAÇÃO)
# ==========================================
st.sidebar.markdown("<h1 style='text-align: center; margin-bottom: 30px;'>💸 Organizé</h1>", unsafe_allow_html=True)

if st.sidebar.button(
    "💬 Chat de Lançamentos", 
    use_container_width=True, 
    type="primary" if st.session_state.menu_navegacao == "💬 Chat de Lançamentos" else "secondary"
):
    st.session_state.mudar_pagina = "💬 Chat de Lançamentos"
    st.rerun()

if st.sidebar.button(
    "📊 Dashboard e Relatórios", 
    use_container_width=True, 
    type="primary" if st.session_state.menu_navegacao == "📊 Dashboard e Relatórios" else "secondary"
):
    st.session_state.mudar_pagina = "📊 Dashboard e Relatórios"
    st.rerun()

st.sidebar.divider()

total_entradas_geral = sum(t["Valor"] for t in st.session_state.transacoes if t["Tipo"] == "Entrada")
total_saidas_geral = sum(t["Valor"] for t in st.session_state.transacoes if t["Tipo"] == "Saída")
saldo_geral = total_entradas_geral - total_saidas_geral
cor_saldo = "#00C853" if saldo_geral >= 0 else "#FF5252"

st.sidebar.markdown(f"""
<div style='background-color: #121619; padding: 15px; border-radius: 10px; border-left: 5px solid {cor_saldo}; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);'>
    <p style='color: #8c8c8c; margin-bottom: 5px; font-size: 0.9rem; font-weight: bold;'>SALDO GERAL</p>
    <h3 style='margin: 0; color: {cor_saldo} !important;'>R$ {saldo_geral:.2f}</h3>
</div>
""", unsafe_allow_html=True)

st.sidebar.info(f"💡 **Dica do Dia:**\n\n{st.session_state.dica_atual}")

# ==========================================
# 4. PÁGINA 1: O CHAT DA IA
# ==========================================
if st.session_state.menu_navegacao == "💬 Chat de Lançamentos":
    
    st.markdown("""
        <div style='text-align: center; padding: 1rem 0 2rem 0;'>
            <h1 style='color: #00C853; font-size: 2.5rem; margin-bottom: 0.2rem;'>Organizé</h1>
            <p style='color: #A0AEC0; font-size: 1rem;'>O que vamos registar hoje?</p>
        </div>
    """, unsafe_allow_html=True)
    
    mensagens_para_exibir = [st.session_state.mensagens_chat[0]]
    if len(st.session_state.mensagens_chat) > 1:
        mensagens_para_exibir.extend(st.session_state.mensagens_chat[-2:])
        
    for msg in mensagens_para_exibir:
        if msg["role"] == "user":
            # Aumentámos o max-width para 85% para ficar melhor no telemóvel
            st.markdown(f"""
            <div style='display: flex; justify-content: flex-end; margin-bottom: 25px;'>
                <div style='background: linear-gradient(135deg, #2D3748, #1A202C); color: white; padding: 12px 18px; border-radius: 20px 20px 0px 20px; max-width: 85%; font-size: 1rem; box-shadow: 0 4px 15px rgba(0,0,0,0.3); border: 1px solid #4A5568;'>
                    👤 <strong>Você:</strong><br><span style='color: #E2E8F0;'>{msg["content"]}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style='display: flex; justify-content: flex-start; margin-bottom: 25px;'>
                <div style='background: linear-gradient(135deg, #0A3D18, #05240D); border: 1px solid #00C853; color: white; padding: 12px 18px; border-radius: 20px 20px 20px 0px; max-width: 85%; font-size: 1rem; box-shadow: 0 4px 15px rgba(0, 200, 83, 0.12);'>
                    🤖 <strong>Organizé:</strong><br><span style='color: #E2E8F0;'>{msg["content"]}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Espaçamento vazio no fundo para o teclado do telemóvel não tapar as mensagens
    st.markdown("<div style='height: 80px;'></div>", unsafe_allow_html=True)

    if prompt := st.chat_input("Digite a sua movimentação (ou diga 'organizé')..."):
        st.session_state.mensagens_chat.append({"role": "user", "content": prompt})
        mensagem_lower = prompt.lower()
        
        if 'organizé' in mensagem_lower or 'organize' in mensagem_lower:
            st.session_state.mensagens_chat.append({"role": "assistant", "content": "📊 **Tudo pronto!** A gerar o dashboard..."})
            st.session_state.mudar_pagina = "📊 Dashboard e Relatórios"
            st.session_state.dica_atual = random.choice(dicas_financeiras) 
            st.rerun()
            
        else:
            numeros = re.findall(r'\d+[.,]?\d*', mensagem_lower)
            if not numeros:
                resposta = "Ops, não encontrei o valor. Pode repetir incluindo quanto foi?"
            else:
                valor = float(numeros[0].replace(',', '.'))
                tipo = "Saída"
                categoria = "Outros"
                palavras_entrada = ("recebi", "ganhei", "salário", "salario", "pix", "devolveram", "vendi", "lucro")
                
                for p in palavras_entrada:
                    if p in mensagem_lower:
                        tipo = "Entrada"
                        categoria = "Renda"
                        break
                
                if tipo == "Saída":
                    palavras_digitadas = mensagem_lower.split()
                    for cat, palavras_chave in categorias_map.items():
                        for palavra_digitada in palavras_digitadas:
                            match_parcial = any(palavra_digitada in p or p in palavra_digitada for p in palavras_chave)
                            if match_parcial:
                                categoria = cat
                                break
                            
                            correspondencia = difflib.get_close_matches(palavra_digitada, palavras_chave, n=1, cutoff=0.6)
                            if correspondencia:
                                categoria = cat
                                break 
                        if categoria != "Outros":
                            break 
                
                st.session_state.transacoes.append({
                    "Data": datetime.now().strftime("%d/%m/%Y"),
                    "Tipo": tipo,
                    "Categoria": categoria,
                    "Valor": valor,
                    "Descrição original": prompt
                })
                
                if tipo == "Entrada":
                    resposta = f"💰 Sucesso! R$ {valor:.2f} adicionado como {categoria}."
                else:
                    resposta = f"💸 Anotado. Gasto de R$ {valor:.2f} classificado em [{categoria}]."
        
            st.session_state.mensagens_chat.append({"role": "assistant", "content": resposta})
            st.rerun()

# ==========================================
# 5. PÁGINA 2: DASHBOARD E RELATÓRIOS
# ==========================================
elif st.session_state.menu_navegacao == "📊 Dashboard e Relatórios":
    st.title("Resumo Financeiro")
    
    if len(st.session_state.transacoes) == 0:
        st.info("Nenhuma movimentação registada ainda. Vá ao menu Chat e digite um gasto para ativar o dashboard!")
    else:
        df = pd.DataFrame(st.session_state.transacoes)
        df["Data_Obj"] = pd.to_datetime(df["Data"], format="%d/%m/%Y")
        df["Mês/Ano"] = df["Data_Obj"].dt.strftime("%m/%Y")
        
        st.sidebar.subheader("Opções de Filtro")
        lista_meses = ["Todos"] + list(df["Mês/Ano"].unique())
        mes_selecionado = st.sidebar.selectbox("📅 Mês:", lista_meses)
        
        lista_categorias = ["Todas"] + list(df["Categoria"].unique())
        categoria_selecionada = st.sidebar.selectbox("🏷️ Categoria:", lista_categorias)

        df_filtrado = df.copy()
        if mes_selecionado != "Todos":
            df_filtrado = df_filtrado[df_filtrado["Mês/Ano"] == mes_selecionado]
        if categoria_selecionada != "Todas":
            df_filtrado = df_filtrado[df_filtrado["Categoria"] == categoria_selecionada]
            
        if df_filtrado.empty:
            st.warning("Nenhum dado encontrado para estes filtros.")
        else:
            total_entradas = df_filtrado[df_filtrado["Tipo"] == "Entrada"]["Valor"].sum()
            total_saidas = df_filtrado[df_filtrado["Tipo"] == "Saída"]["Valor"].sum()
            saldo = total_entradas - total_saidas
            cor_saldo_dashboard = "#00C853" if saldo >= 0 else "#FF5252"
            
            # CSS Grid para manter os 3 cartões lado a lado no telemóvel
            st.markdown(f"""
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-bottom: 30px;">
                <div style="background-color: #121619; border: 1px solid #1f2924; border-top: 3px solid #00C853; padding: 10px; border-radius: 8px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
                    <p style="color: #8c8c8c; font-size: 0.75rem; margin: 0; padding-bottom: 5px; font-weight: bold;">RECEITAS</p>
                    <h4 style="color: #00C853; margin: 0; font-size: 1rem;">R$ {total_entradas:.0f}</h4>
                </div>
                <div style="background-color: #121619; border: 1px solid #1f2924; border-top: 3px solid #FF5252; padding: 10px; border-radius: 8px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
                    <p style="color: #8c8c8c; font-size: 0.75rem; margin: 0; padding-bottom: 5px; font-weight: bold;">DESPESAS</p>
                    <h4 style="color: #FF5252; margin: 0; font-size: 1rem;">R$ {total_saidas:.0f}</h4>
                </div>
                <div style="background-color: #121619; border: 1px solid #1f2924; border-top: 3px solid {cor_saldo_dashboard}; padding: 10px; border-radius: 8px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
                    <p style="color: #8c8c8c; font-size: 0.75rem; margin: 0; padding-bottom: 5px; font-weight: bold;">SALDO</p>
                    <h4 style="color: {cor_saldo_dashboard}; margin: 0; font-size: 1rem;">R$ {saldo:.0f}</h4>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            df_saidas = df_filtrado[df_filtrado["Tipo"] == "Saída"]
            
            if not df_saidas.empty:
                gastos_agrupados = df_saidas.groupby("Categoria")["Valor"].sum().reset_index()
                paleta_contraste = ['#00E676', '#0A3D18', '#B9F6CA', '#198754', '#E0F2F1', '#042812']
                
                # Remoção de colunas limitadoras para que o gráfico utilize 100% do ecrã do telemóvel
                fig = px.pie(
                    gastos_agrupados, 
                    values='Valor', 
                    names='Categoria', 
                    title='Distribuição de Gastos',
                    hole=0.4,
                    color_discrete_sequence=paleta_contraste
                )
                
                # A legenda foi movida para a base do gráfico (horizontal) e as margens foram removidas
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)', 
                    paper_bgcolor='rgba(0,0,0,0)', 
                    font_color='#FAFAFA',
                    legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="center", x=0.5),
                    margin=dict(t=40, b=0, l=0, r=0)
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.write("Sem saídas registadas para exibir no gráfico.")
                
            st.divider()
            
            st.subheader("Histórico Filtrado")
            df_mostrar = df_filtrado.drop(columns=["Data_Obj", "Mês/Ano"])
            st.dataframe(df_mostrar, use_container_width=True)