import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import json
from pathlib import Path
from datetime import date, datetime


# =========================
# PERSISTÊNCIA / HISTÓRICO T3
# =========================
# Em execução local, o histórico é salvo em JSON ao lado do app.
# Em hospedagens com filesystem efêmero, configure uma fonte persistente
# (ex.: banco/planilha) para retenção definitiva entre reinicializações.
HIST_FILE = Path(__file__).with_name("historico_t3.json")

CAMPOS_T3 = [
    "SM", "SM_EXPRESSA", "CHECKLIST", "MONITORAMENTO", "SM_FORCADA",
    "DEMANDAS", "CONCLUIDAS", "PENDENTES", "CANCELADAS", "DENTRO_SLA",
    "TEMPO_MEDIO", "META_SLA"
]

def carregar_historico_t3():
    if HIST_FILE.exists():
        try:
            dados = json.loads(HIST_FILE.read_text(encoding="utf-8"))
            return dados if isinstance(dados, list) else []
        except Exception:
            return []
    return []

def salvar_historico_t3(registros):
    HIST_FILE.write_text(
        json.dumps(registros, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

def upsert_registro_t3(data_ref, dados):
    historico = carregar_historico_t3()
    data_iso = data_ref.isoformat() if hasattr(data_ref, "isoformat") else str(data_ref)
    registro = {"DATA": data_iso, "ATUALIZADO_EM": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    for campo in CAMPOS_T3:
        registro[campo] = dados.get(campo, 0)

    indice = next((i for i, r in enumerate(historico) if r.get("DATA") == data_iso), None)
    if indice is None:
        historico.append(registro)
    else:
        historico[indice] = registro
    historico.sort(key=lambda x: x.get("DATA", ""))
    salvar_historico_t3(historico)
    return historico

def excluir_registro_t3(data_ref):
    data_iso = data_ref.isoformat() if hasattr(data_ref, "isoformat") else str(data_ref)
    historico = [r for r in carregar_historico_t3() if r.get("DATA") != data_iso]
    salvar_historico_t3(historico)
    return historico


# Configuração da página
st.set_page_config(page_title="Painel Operacional Monitoring", layout="wide")

# Estilização CSS Personalizada
st.markdown("""
    <style>
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
    
    header[data-testid="stHeader"] {
        background-color: rgba(0,0,0,0) !important;
        height: 0px !important;
    }

    .stApp {
        background-color: #08090c;
        color: #ffffff;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    #MainMenu, footer, header {visibility: hidden;}

    .header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 0px !important;
        margin-bottom: 16px !important;
        padding-top: 0px !important;
    }
    .header-left {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .avatar-icon {
        background-color: #1e232d;
        color: #ffffff;
        font-weight: 800;
        font-size: 13px;
        width: 36px;
        height: 36px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 1px solid #2d3545;
    }
    .header-title { font-size: 18px; font-weight: 700; color: #ffffff; margin: 0; line-height: 1.2; }
    .header-sub { font-size: 12px; color: #6e7681; margin-top: 2px; }

    /* Customização das Abas */
    .stTabs [data-baseweb="tab-list"] { 
        gap: 8px; 
        background-color: transparent !important;
        margin-bottom: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #12161f !important;
        border-radius: 8px !important;
        color: #8b949e !important;
        padding: 6px 16px !important;
        font-weight: 700 !important;
        border: 1px solid #1c212c !important;
        font-size: 12px !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #ffffff !important;
        background-color: #1a202c !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #12161f !important;
        color: #ffffff !important;
        border-bottom: 2px solid #00e676 !important;
    }
    .stTabs [data-baseweb="tab-highlight"] {
        background-color: #00e676 !important;
    }

    /* Cards KPI */
    .kpi-card {
        background-color: #10141d;
        border: 1px solid #1c222e;
        border-radius: 12px;
        padding: 16px 20px;
        position: relative;
        overflow: hidden;
    }
    .kpi-title { color: #8b949e; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; }
    .kpi-value { font-size: 32px; font-weight: 800; color: #ffffff; margin-top: 6px; }
    .kpi-value-green { font-size: 32px; font-weight: 800; color: #00e676; margin-top: 6px; }
    .kpi-value-yellow { font-size: 32px; font-weight: 800; color: #ffeb3b; margin-top: 6px; }
    .kpi-value-orange { font-size: 32px; font-weight: 800; color: #ff9800; margin-top: 6px; }
    .kpi-value-red { font-size: 32px; font-weight: 800; color: #ff5252; margin-top: 6px; }

    .kpi-bar-white { position: absolute; bottom: 0; left: 0; right: 0; height: 3px; background-color: #ffffff; }
    .kpi-bar-green { position: absolute; bottom: 0; left: 0; right: 0; height: 3px; background-color: #00e676; }

    /* Card Flutuante dos Gráficos */
    .charts-card {
        background-color: #10141d;
        border: 1px solid #1c222e;
        border-radius: 14px;
        padding: 20px 24px;
        margin-bottom: 20px;
    }
    .charts-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;
    }
    .charts-title {
        font-size: 13px;
        font-weight: 700;
        color: #ffffff;
        letter-spacing: 0.5px;
    }
    .charts-legend {
        display: flex;
        gap: 16px;
        font-size: 11px;
        font-weight: 700;
    }

    /* Card Flutuante da Tabela */
    .card-floating {
        background-color: #10141d;
        border: 1px solid #1c222e;
        border-radius: 14px;
        padding: 20px 24px;
    }

    .th-title {
        color: #8b949e;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }

    /* Input Numérico */
    div[data-baseweb="input"] {
        background-color: #161b26 !important;
        border: 1px solid #232a38 !important;
        border-radius: 10px !important;
    }
    div[data-baseweb="input"]:focus-within {
        border-color: #00e676 !important;
    }
    div[data-baseweb="input"] input {
        color: #ffffff !important;
        text-align: center;
        font-weight: 700;
        font-size: 13px;
    }

    /* Barra de Progresso Customizada */
    .progress-bar-bg {
        background-color: #1c222e;
        border-radius: 10px;
        height: 6px;
        width: 100%;
        overflow: hidden;
    }
    .progress-bar-fill {
        height: 100%;
        border-radius: 10px;
    }

    /* Badges de Status */
    .badge-otimo {
        background-color: rgba(0, 230, 118, 0.08);
        color: #00e676;
        border: 1px solid #00e676;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 700;
        display: inline-block;
    }
    .badge-regular {
        background-color: rgba(255, 179, 0, 0.08);
        color: #ffb300;
        border: 1px solid #ffb300;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 700;
        display: inline-block;
    }
    .badge-baixo {
        background-color: rgba(255, 82, 82, 0.08);
        color: #ff5252;
        border: 1px solid #ff5252;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 700;
        display: inline-block;
    }
    </style>
""", unsafe_allow_html=True)

# Inicialização dos dados da Aba Cadastro
if "dados_cad" not in st.session_state:
    st.session_state.dados_cad = [
        {"CLIENTE": "Airtable", "QTD": 100, "REALIZADAS": 100},
        {"CLIENTE": "SPX", "QTD": 120, "REALIZADAS": 110},
        {"CLIENTE": "Raster", "QTD": 80, "REALIZADAS": 70},
        {"CLIENTE": "KMM", "QTD": 60, "REALIZADAS": 55},
        {"CLIENTE": "Photocheck", "QTD": 90, "REALIZADAS": 85},
        {"CLIENTE": "ELOG", "QTD": 50, "REALIZADAS": 48},
        {"CLIENTE": "AMAZON", "QTD": 110, "REALIZADAS": 100},
    ]

# Inicialização dos dados da Aba Ger. Risco
if "dados_risco" not in st.session_state:
    st.session_state.dados_risco = [
        {"CLIENTE": "SM", "QTD": 50, "REALIZADAS": 45},
        {"CLIENTE": "SM Expressa", "QTD": 30, "REALIZADAS": 28},
        {"CLIENTE": "Checklists", "QTD": 80, "REALIZADAS": 75},
        {"CLIENTE": "SM Forçadas", "QTD": 20, "REALIZADAS": 15},
        {"CLIENTE": "Monitoring", "QTD": 100, "REALIZADAS": 92},
    ]

# Inicialização dos dados da Aba Torre Multi
if "dados_torre" not in st.session_state:
    st.session_state.dados_torre = [
        {"CLIENTE": "Amazon", "QTD": 42, "NO_PRAZO": 40, "ATR_ORIG": 1, "ATR_DEST": 1, "NO_SHOW": 0},
        {"CLIENTE": "Imile", "QTD": 28, "NO_PRAZO": 25, "ATR_ORIG": 2, "ATR_DEST": 1, "NO_SHOW": 0},
        {"CLIENTE": "Decathlon", "QTD": 18, "NO_PRAZO": 18, "ATR_ORIG": 0, "ATR_DEST": 0, "NO_SHOW": 0},
        {"CLIENTE": "Loggi", "QTD": 35, "NO_PRAZO": 31, "ATR_ORIG": 2, "ATR_DEST": 2, "NO_SHOW": 0},
        {"CLIENTE": "Plural", "QTD": 12, "NO_PRAZO": 11, "ATR_ORIG": 0, "ATR_DEST": 1, "NO_SHOW": 0},
        {"CLIENTE": "Brasil Gráfica", "QTD": 9, "NO_PRAZO": 8, "ATR_ORIG": 0, "ATR_DEST": 1, "NO_SHOW": 0},
        {"CLIENTE": "Total Meli", "QTD": 54, "NO_PRAZO": 48, "ATR_ORIG": 3, "ATR_DEST": 2, "NO_SHOW": 1},
        {"CLIENTE": "Carrossel J&T", "QTD": 22, "NO_PRAZO": 20, "ATR_ORIG": 1, "ATR_DEST": 0, "NO_SHOW": 1},
        {"CLIENTE": "ANJUN", "QTD": 15, "NO_PRAZO": 13, "ATR_ORIG": 1, "ATR_DEST": 1, "NO_SHOW": 0},
        {"CLIENTE": "Americanas", "QTD": 31, "NO_PRAZO": 27, "ATR_ORIG": 2, "ATR_DEST": 1, "NO_SHOW": 1},
        {"CLIENTE": "Word Post", "QTD": 11, "NO_PRAZO": 10, "ATR_ORIG": 0, "ATR_DEST": 0, "NO_SHOW": 1},
    ]

# Função para obter cor e status
def get_status_e_cor(perc):
    if perc <= 40.0:
        return "BAIXO", "#ff5252", "badge-baixo"
    elif perc <= 80.0:
        return "REGULAR", "#ffb300", "badge-regular"
    else:
        return "ÓTIMO", "#00e676", "badge-otimo"

# Funções de Renderização dos Gráficos
def render_barra_empilhada(v1, v2, chart_key):
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=['GERAL'], x=[v1], orientation='h', width=0.6,
        text=[f"{v1}"], textposition='inside',
        insidetextanchor='middle',
        textfont=dict(color='#000000', size=13, family='sans-serif'),
        marker=dict(color="#00e676", cornerradius=10)
    ))
    fig.add_trace(go.Bar(
        y=['GERAL'], x=[v2], orientation='h', width=0.6,
        text=[f"{v2}" if v2 > 0 else ""], textposition='inside',
        insidetextanchor='middle',
        textfont=dict(color='#ffffff', size=13, family='sans-serif'),
        marker=dict(color="#ff5252", cornerradius=10)
    ))
    fig.update_layout(
        barmode='stack', height=36,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        xaxis=dict(showgrid=False, visible=False),
        yaxis=dict(showgrid=False, visible=False)
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False}, key=chart_key)

def render_barra_empilhada_torre(v_np, v_ao, v_ad, v_ns, chart_key):
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=['GERAL'], x=[v_np], orientation='h', width=0.6,
        text=[f"{v_np}" if v_np > 0 else ""], textposition='inside',
        insidetextanchor='middle',
        textfont=dict(color='#000000', size=13, family='sans-serif'),
        marker=dict(color="#00e676", cornerradius=10)
    ))
    fig.add_trace(go.Bar(
        y=['GERAL'], x=[v_ao], orientation='h', width=0.6,
        text=[f"{v_ao}" if v_ao > 0 else ""], textposition='inside',
        insidetextanchor='middle',
        textfont=dict(color='#000000', size=13, family='sans-serif'),
        marker=dict(color="#ffeb3b", cornerradius=10)
    ))
    fig.add_trace(go.Bar(
        y=['GERAL'], x=[v_ad], orientation='h', width=0.6,
        text=[f"{v_ad}" if v_ad > 0 else ""], textposition='inside',
        insidetextanchor='middle',
        textfont=dict(color='#ffffff', size=13, family='sans-serif'),
        marker=dict(color="#ff9800", cornerradius=10)
    ))
    fig.add_trace(go.Bar(
        y=['GERAL'], x=[v_ns], orientation='h', width=0.6,
        text=[f"{v_ns}" if v_ns > 0 else ""], textposition='inside',
        insidetextanchor='middle',
        textfont=dict(color='#ffffff', size=13, family='sans-serif'),
        marker=dict(color="#ff5252", cornerradius=10)
    ))
    fig.update_layout(
        barmode='stack', height=36,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        xaxis=dict(showgrid=False, visible=False),
        yaxis=dict(showgrid=False, visible=False)
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False}, key=chart_key)

def render_mini_barras(lista_dados, prefix_key):
    col1, col2, col3 = st.columns(3)
    cols = [col1, col2, col3]
    for i, item in enumerate(lista_dados):
        with cols[i % 3]:
            real = item['REALIZADAS']
            pend = item['PENDENTES']
            perc = item['%']
            _, cor_p, _ = get_status_e_cor(perc)
            
            c_cli, c_bar, c_txt = st.columns([0.25, 0.60, 0.15])
            with c_cli:
                st.markdown(f"<div style='font-size:12px; font-weight:700; color:#ffffff; padding-top:5px; white-space:nowrap;'>{item['CLIENTE']}</div>", unsafe_allow_html=True)
            with c_bar:
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    y=[''], x=[real], orientation='h', width=0.6,
                    text=[f"{real}"], textposition='inside',
                    insidetextanchor='middle',
                    textfont=dict(color='#000000', size=11, family='sans-serif'),
                    marker=dict(color='#00e676', cornerradius=10)
                ))
                fig.add_trace(go.Bar(
                    y=[''], x=[pend], orientation='h', width=0.6,
                    text=[f"{pend}" if pend > 0 else ""], textposition='inside',
                    insidetextanchor='middle',
                    textfont=dict(color='#ffffff', size=11, family='sans-serif'),
                    marker=dict(color='#ff5252', cornerradius=10)
                ))
                fig.update_layout(
                    barmode='stack', height=30,
                    margin=dict(l=0, r=0, t=0, b=0),
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    showlegend=False,
                    xaxis=dict(showgrid=False, visible=False),
                    yaxis=dict(showgrid=False, visible=False)
                )
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False}, key=f"mini_bar_{prefix_key}_{i}")
            with c_txt:
                st.markdown(f"<div style='font-size:12px; font-weight:800; color:{cor_p}; text-align:left; padding-left:4px; padding-top:5px;'>{perc:.0f}%</div>", unsafe_allow_html=True)

# Renderização genérica para CADASTRO e GER. RISCO
def render_tab_content(state_key, prefix_key):
    tot_qtd, tot_real = 0, 0
    dados_processados = []
    
    for item in st.session_state[state_key]:
        qtd = item['QTD']
        real = min(item['REALIZADAS'], qtd)
        pend = 0 if real >= qtd else (qtd - real)
        perc = 100.0 if (qtd > 0 and real >= qtd) else (round((real / qtd * 100), 1) if qtd > 0 else 0.0)
        
        tot_qtd += qtd
        tot_real += real
        dados_processados.append({
            "CLIENTE": item['CLIENTE'],
            "QTD": qtd,
            "REALIZADAS": real,
            "PENDENTES": pend,
            "%": perc
        })
    
    tot_pend = max(0, tot_qtd - tot_real)
    perf_geral = 100.0 if (tot_qtd > 0 and tot_real >= tot_qtd) else (round((tot_real / tot_qtd * 100), 1) if tot_qtd > 0 else 0.0)

    # Cards Resumo Topo
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f'''
        <div class="kpi-card">
            <div class="kpi-title">QTD TOTAL</div>
            <div class="kpi-value">{tot_qtd}</div>
            <div class="kpi-bar-white"></div>
        </div>
    ''', unsafe_allow_html=True)
    
    c2.markdown(f'''
        <div class="kpi-card">
            <div class="kpi-title">REALIZADAS</div>
            <div class="kpi-value-green">{tot_real}</div>
        </div>
    ''', unsafe_allow_html=True)
    
    c3.markdown(f'''
        <div class="kpi-card">
            <div class="kpi-title">PENDENTES</div>
            <div class="kpi-value-red">{tot_pend}</div>
        </div>
    ''', unsafe_allow_html=True)
    
    c4.markdown(f'''
        <div class="kpi-card">
            <div class="kpi-title">PERFORMANCE</div>
            <div class="kpi-value-green">{perf_geral:.1f}%</div>
            <div class="kpi-bar-green"></div>
        </div>
    ''', unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 16px;'></div>", unsafe_allow_html=True)

    # Gráficos
    st.markdown("""
        <div class="charts-card">
            <div class="charts-header">
                <div class="charts-title">REALIZADAS vs PENDENTES</div>
                <div class="charts-legend">
                    <span style="color:#00e676;">● REALIZADAS</span>
                    <span style="color:#ff5252;">● PENDENTES</span>
                </div>
            </div>
    """, unsafe_allow_html=True)

    render_barra_empilhada(tot_real, tot_pend, f"stack_bar_{prefix_key}")
    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
    render_mini_barras(dados_processados, prefix_key)
    st.markdown("</div>", unsafe_allow_html=True)

    # Tabela
    st.markdown('<div class="card-floating">', unsafe_allow_html=True)
    
    h1, h2, h3, h4, h5, h6 = st.columns([2.5, 1.2, 1.2, 1.2, 2.5, 1.5])
    h1.markdown('<div class="th-title">CLIENTE / TIPO</div>', unsafe_allow_html=True)
    h2.markdown('<div class="th-title" style="text-align:center;">QTD</div>', unsafe_allow_html=True)
    h3.markdown('<div class="th-title" style="text-align:center;">REALIZADAS</div>', unsafe_allow_html=True)
    h4.markdown('<div class="th-title" style="text-align:center;">PENDENTES</div>', unsafe_allow_html=True)
    h5.markdown('<div class="th-title">%</div>', unsafe_allow_html=True)
    h6.markdown('<div class="th-title" style="text-align:center;">STATUS</div>', unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

    for idx, r in enumerate(dados_processados):
        col_cli, col_qtd, col_real, col_pend, col_perc, col_stat = st.columns([2.5, 1.2, 1.2, 1.2, 2.5, 1.5])
        status_txt, cor_bar, badge_class = get_status_e_cor(r['%'])
        
        with col_cli:
            st.markdown(f"<div style='padding-top:8px; font-weight:700; font-size:13px;'>{r['CLIENTE']}</div>", unsafe_allow_html=True)
        
        with col_qtd:
            n_qtd = st.number_input("", min_value=0, value=r['QTD'], key=f"{prefix_key}_q_{idx}", label_visibility="collapsed")
            if n_qtd != st.session_state[state_key][idx]['QTD']:
                st.session_state[state_key][idx]['QTD'] = n_qtd
                st.rerun()
            
        with col_real:
            n_real = st.number_input("", min_value=0, max_value=n_qtd, value=min(r['REALIZADAS'], n_qtd), key=f"{prefix_key}_r_{idx}", label_visibility="collapsed")
            if n_real != st.session_state[state_key][idx]['REALIZADAS']:
                st.session_state[state_key][idx]['REALIZADAS'] = n_real
                st.rerun()

        with col_pend:
            st.markdown(f"<div style='padding-top:8px; font-weight:700; color:#8b949e; text-align:center; font-size:13px;'>{r['PENDENTES']}</div>", unsafe_allow_html=True)

        with col_perc:
            st.markdown(f"""
                <div style="padding-top:8px; display:flex; align-items:center; gap:12px;">
                    <div class="progress-bar-bg">
                        <div class="progress-bar-fill" style="width:{r['%']}%; background-color:{cor_bar};"></div>
                    </div>
                    <span style="font-size:12px; font-weight:800; color:{cor_bar}; min-width:42px;">{r['%']:.1f}%</span>
                </div>
            """, unsafe_allow_html=True)

        with col_stat:
            st.markdown(f"<div style='padding-top:4px; text-align:center;'><span class='{badge_class}'>● {status_txt}</span></div>", unsafe_allow_html=True)

        st.markdown("<div style='margin-bottom: 8px;'></div>", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# Renderização da Aba TORRE MULTI
def render_torre_multi():
    tot_qtd = sum(item['QTD'] for item in st.session_state.dados_torre)
    tot_no_prazo = sum(item['NO_PRAZO'] for item in st.session_state.dados_torre)
    tot_atr_orig = sum(item['ATR_ORIG'] for item in st.session_state.dados_torre)
    tot_atr_dest = sum(item['ATR_DEST'] for item in st.session_state.dados_torre)
    tot_no_show = sum(item['NO_SHOW'] for item in st.session_state.dados_torre)
    
    perf_geral = (tot_no_prazo / tot_qtd * 100) if tot_qtd > 0 else 0.0

    # Cards Resumo Topo
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.markdown(f'''
        <div class="kpi-card">
            <div class="kpi-title">QTD</div>
            <div class="kpi-value">{tot_qtd}</div>
            <div class="kpi-bar-white"></div>
        </div>
    ''', unsafe_allow_html=True)
    
    c2.markdown(f'''
        <div class="kpi-card">
            <div class="kpi-title">NO PRAZO</div>
            <div class="kpi-value-green">{tot_no_prazo}</div>
        </div>
    ''', unsafe_allow_html=True)
    
    c3.markdown(f'''
        <div class="kpi-card">
            <div class="kpi-title">ATR ORIG</div>
            <div class="kpi-value-yellow">{tot_atr_orig}</div>
        </div>
    ''', unsafe_allow_html=True)

    c4.markdown(f'''
        <div class="kpi-card">
            <div class="kpi-title">ATR DEST</div>
            <div class="kpi-value-orange">{tot_atr_dest}</div>
        </div>
    ''', unsafe_allow_html=True)

    c5.markdown(f'''
        <div class="kpi-card">
            <div class="kpi-title">NO SHOW</div>
            <div class="kpi-value-red">{tot_no_show}</div>
        </div>
    ''', unsafe_allow_html=True)
    
    c6.markdown(f'''
        <div class="kpi-card">
            <div class="kpi-title">PERFORMANCE</div>
            <div class="kpi-value-green">{perf_geral:.1f}%</div>
            <div class="kpi-bar-green"></div>
        </div>
    ''', unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 16px;'></div>", unsafe_allow_html=True)

    # Gráficos
    st.markdown("""
        <div class="charts-card">
            <div class="charts-header">
                <div class="charts-title">DISTRIBUIÇÃO DE OCORRÊNCIAS POR STATUS</div>
                <div class="charts-legend">
                    <span style="color:#00e676;">● NO PRAZO</span>
                    <span style="color:#ffeb3b;">● ATRASO ORIGEM</span>
                    <span style="color:#ff9800;">● ATRASO DESTINO</span>
                    <span style="color:#ff5252;">● NO SHOW</span>
                </div>
            </div>
    """, unsafe_allow_html=True)

    render_barra_empilhada_torre(tot_no_prazo, tot_atr_orig, tot_atr_dest, tot_no_show, "stack_bar_torre")
    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
    
    dados_proc_torre = []
    for item in st.session_state.dados_torre:
        perc = (item['NO_PRAZO'] / item['QTD'] * 100) if item['QTD'] > 0 else 0.0
        dados_proc_torre.append({
            "CLIENTE": item['CLIENTE'],
            "REALIZADAS": item['NO_PRAZO'],
            "PENDENTES": max(0, item['QTD'] - item['NO_PRAZO']),
            "%": perc
        })
        
    render_mini_barras(dados_proc_torre, "torre")
    st.markdown("</div>", unsafe_allow_html=True)

    # Tabela
    st.markdown('<div class="card-floating">', unsafe_allow_html=True)
    
    h1, h2, h3, h4, h5, h6, h7 = st.columns([2.2, 1.0, 1.0, 1.1, 1.1, 1.0, 2.0])
    h1.markdown('<div class="th-title">CLIENTE</div>', unsafe_allow_html=True)
    h2.markdown('<div class="th-title" style="text-align:center;">QTD</div>', unsafe_allow_html=True)
    h3.markdown('<div class="th-title" style="text-align:center;"><span style="color:#00e676;">●</span> NO PRAZO</div>', unsafe_allow_html=True)
    h4.markdown('<div class="th-title" style="text-align:center;"><span style="color:#ffeb3b;">●</span> ATRASO ORIGEM</div>', unsafe_allow_html=True)
    h5.markdown('<div class="th-title" style="text-align:center;"><span style="color:#ff9800;">●</span> ATRASO DESTINO</div>', unsafe_allow_html=True)
    h6.markdown('<div class="th-title" style="text-align:center;"><span style="color:#ff5252;">●</span> NO SHOW</div>', unsafe_allow_html=True)
    h7.markdown('<div class="th-title">%</div>', unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

    for idx, item in enumerate(st.session_state.dados_torre):
        col_cli, col_qtd, col_np, col_ao, col_ad, col_ns, col_perc = st.columns([2.2, 1.0, 1.0, 1.1, 1.1, 1.0, 2.0])
        
        perc = (item['NO_PRAZO'] / item['QTD'] * 100) if item['QTD'] > 0 else 0.0
        _, cor_bar, _ = get_status_e_cor(perc)

        with col_cli:
            st.markdown(f"<div style='padding-top:8px; font-weight:700; font-size:13px;'>{item['CLIENTE']}</div>", unsafe_allow_html=True)
        
        with col_qtd:
            v = st.number_input("", min_value=0, value=item['QTD'], key=f"t_qtd_{idx}", label_visibility="collapsed")
            if v != item['QTD']:
                st.session_state.dados_torre[idx]['QTD'] = v
                st.rerun()

        with col_np:
            v = st.number_input("", min_value=0, max_value=item['QTD'], value=min(item['NO_PRAZO'], item['QTD']), key=f"t_np_{idx}", label_visibility="collapsed")
            if v != item['NO_PRAZO']:
                st.session_state.dados_torre[idx]['NO_PRAZO'] = v
                st.rerun()

        with col_ao:
            v = st.number_input("", min_value=0, value=item['ATR_ORIG'], key=f"t_ao_{idx}", label_visibility="collapsed")
            if v != item['ATR_ORIG']:
                st.session_state.dados_torre[idx]['ATR_ORIG'] = v
                st.rerun()

        with col_ad:
            v = st.number_input("", min_value=0, value=item['ATR_DEST'], key=f"t_ad_{idx}", label_visibility="collapsed")
            if v != item['ATR_DEST']:
                st.session_state.dados_torre[idx]['ATR_DEST'] = v
                st.rerun()

        with col_ns:
            v = st.number_input("", min_value=0, value=item['NO_SHOW'], key=f"t_ns_{idx}", label_visibility="collapsed")
            if v != item['NO_SHOW']:
                st.session_state.dados_torre[idx]['NO_SHOW'] = v
                st.rerun()

        with col_perc:
            st.markdown(f"""
                <div style="padding-top:8px; display:flex; align-items:center; gap:12px;">
                    <div class="progress-bar-bg">
                        <div class="progress-bar-fill" style="width:{perc}%; background-color:{cor_bar};"></div>
                    </div>
                    <span style="font-size:12px; font-weight:800; color:{cor_bar}; min-width:42px;">{perc:.1f}%</span>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='margin-bottom: 8px;'></div>", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# Header Principal
st.markdown("""
    <div class="header-container">
        <div class="header-left">
            <div class="avatar-icon">AN</div>
            <div>
                <div class="header-title">Painel Operacional Monitoring</div>
                <div class="header-sub">Operacional • QTD vs Realizadas • Edição local</div>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)



# =========================
# T3 GERENCIAL / GER. RISCO
# =========================
def render_t3_gerencial():
    st.markdown("""
        <div style="margin:4px 0 16px 0;">
            <div style="font-size:20px;font-weight:800;color:#fff;">T3 • GERENCIAMENTO DE RISCO</div>
            <div style="font-size:12px;color:#8b949e;">Histórico diário • produtividade • SLA • evolução mensal</div>
        </div>
    """, unsafe_allow_html=True)

    if "t3_gerencial" not in st.session_state:
        st.session_state.t3_gerencial = {
            "SM": 0, "SM_EXPRESSA": 0, "CHECKLIST": 0, "MONITORAMENTO": 0,
            "SM_FORCADA": 0, "DEMANDAS": 0, "CONCLUIDAS": 0,
            "PENDENTES": 0, "CANCELADAS": 0, "DENTRO_SLA": 0,
            "TEMPO_MEDIO": 0.0, "META_SLA": 95.0
        }

    d = st.session_state.t3_gerencial
    historico = carregar_historico_t3()

    # Controle do período / data
    fc1, fc2, fc3 = st.columns([1.4, 1.4, 3.2])
    data_ref = fc1.date_input("DATA DO RESULTADO", value=date.today(), key="t3_data_ref")
    meses = ["Todos","Janeiro","Fevereiro","Março","Abril","Maio","Junho",
             "Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"]
    mes_filtro = fc2.selectbox("VISÃO", meses, index=date.today().month, key="t3_mes_filtro")
    fc3.markdown(
        "<div style='padding-top:30px;color:#8b949e;font-size:12px;'>"
        "Um registro por dia. Salvar novamente a mesma data atualiza o dia sem duplicar.</div>",
        unsafe_allow_html=True
    )

    # Se já houver registro da data escolhida, botão para carregá-lo para edição
    reg_data = next((r for r in historico if r.get("DATA") == data_ref.isoformat()), None)
    if reg_data:
        st.info(f"Já existe resultado salvo para {data_ref.strftime('%d/%m/%Y')}. Você pode carregá-lo, editar e salvar novamente.")
        if st.button("CARREGAR DIA PARA EDIÇÃO", key="carregar_t3"):
            for campo in CAMPOS_T3:
                if campo in reg_data:
                    d[campo] = reg_data[campo]
            st.rerun()

    with st.expander("ALIMENTAR RESULTADO DO DIA", expanded=True):
        c1,c2,c3,c4,c5 = st.columns(5)
        d["SM"] = c1.number_input("SM criadas", min_value=0, value=int(d["SM"]), key="g_sm")
        d["SM_EXPRESSA"] = c2.number_input("SM Expressas", min_value=0, value=int(d["SM_EXPRESSA"]), key="g_sme")
        d["CHECKLIST"] = c3.number_input("Checklists", min_value=0, value=int(d["CHECKLIST"]), key="g_chk")
        d["MONITORAMENTO"] = c4.number_input("Monitoramentos", min_value=0, value=int(d["MONITORAMENTO"]), key="g_mon")
        d["SM_FORCADA"] = c5.number_input("SM Forçadas", min_value=0, value=int(d["SM_FORCADA"]), key="g_smf")

        c1,c2,c3,c4,c5,c6 = st.columns(6)
        d["DEMANDAS"] = c1.number_input("Demandas recebidas", min_value=0, value=int(d["DEMANDAS"]), key="g_dem")
        d["CONCLUIDAS"] = c2.number_input("Concluídas", min_value=0, value=int(d["CONCLUIDAS"]), key="g_con")
        d["PENDENTES"] = c3.number_input("Pendentes", min_value=0, value=int(d["PENDENTES"]), key="g_pen")
        d["CANCELADAS"] = c4.number_input("Canceladas", min_value=0, value=int(d["CANCELADAS"]), key="g_can")
        d["DENTRO_SLA"] = c5.number_input("Dentro do SLA", min_value=0, value=int(d["DENTRO_SLA"]), key="g_sla")
        d["TEMPO_MEDIO"] = c6.number_input("Tempo médio (min)", min_value=0.0, value=float(d["TEMPO_MEDIO"]), step=0.1, key="g_tm")

        b1,b2,b3 = st.columns([1.2,1.2,4])
        if b1.button("💾 SALVAR / ATUALIZAR DIA", use_container_width=True, type="primary"):
            upsert_registro_t3(data_ref, d)
            st.success(f"Resultado de {data_ref.strftime('%d/%m/%Y')} gravado no histórico.")
            st.rerun()
        if reg_data and b2.button("EXCLUIR DIA", use_container_width=True):
            excluir_registro_t3(data_ref)
            st.success("Registro excluído.")
            st.rerun()

    # Histórico filtrado
    historico = carregar_historico_t3()
    df = pd.DataFrame(historico)
    if not df.empty:
        df["DATA"] = pd.to_datetime(df["DATA"], errors="coerce")
        df = df.dropna(subset=["DATA"]).sort_values("DATA")
        if mes_filtro != "Todos":
            numero_mes = meses.index(mes_filtro)
            df_vis = df[df["DATA"].dt.month == numero_mes].copy()
        else:
            df_vis = df.copy()
    else:
        df_vis = pd.DataFrame()

    # KPIs acumulados do filtro
    if not df_vis.empty:
        demandas = int(df_vis["DEMANDAS"].sum())
        concluidas = int(df_vis["CONCLUIDAS"].sum())
        canceladas = int(df_vis["CANCELADAS"].sum())
        pendentes = int(df_vis["PENDENTES"].iloc[-1])
        dentro_sla = int(df_vis["DENTRO_SLA"].sum())
        producao = int(df_vis[["SM","SM_EXPRESSA","CHECKLIST","MONITORAMENTO","SM_FORCADA"]].sum().sum())
        base_valida = max(0, demandas - canceladas)
        atendimento = (concluidas / base_valida * 100) if base_valida else 0
        sla = (dentro_sla / concluidas * 100) if concluidas else 0
        tempo_medio = float(df_vis["TEMPO_MEDIO"].mean())
    else:
        demandas=concluidas=canceladas=pendentes=dentro_sla=producao=0
        atendimento=sla=tempo_medio=0.0

    cols = st.columns(7)
    cards = [
        ("DEMANDAS", demandas, "#ffffff"),
        ("ENTREGAS T3", producao, "#00e676"),
        ("CONCLUÍDAS", concluidas, "#00e676"),
        ("BACKLOG", pendentes, "#ff5252" if pendentes else "#00e676"),
        ("ATENDIMENTO", f"{atendimento:.1f}%", "#00e676" if atendimento >= 95 else "#ffb300"),
        ("SLA", f"{sla:.1f}%", "#00e676" if sla >= 95 else "#ff5252"),
        ("TEMPO MÉDIO", f"{tempo_medio:.1f}m", "#ffffff"),
    ]
    for col,(title,value,color) in zip(cols,cards):
        col.markdown(f"""<div class="kpi-card"><div class="kpi-title">{title}</div>
        <div style="font-size:27px;font-weight:800;color:{color};margin-top:6px;">{value}</div></div>""",
        unsafe_allow_html=True)

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    if df_vis.empty:
        st.warning("Ainda não há histórico para o período selecionado. Alimente o resultado do dia e clique em SALVAR / ATUALIZAR DIA.")
        return

    # Comparativo com dia anterior
    df_vis["BASE_VALIDA"] = (df_vis["DEMANDAS"] - df_vis["CANCELADAS"]).clip(lower=0)
    df_vis["ATENDIMENTO_%"] = (df_vis["CONCLUIDAS"] / df_vis["BASE_VALIDA"].replace(0, pd.NA) * 100).fillna(0)
    df_vis["SLA_%"] = (df_vis["DENTRO_SLA"] / df_vis["CONCLUIDAS"].replace(0, pd.NA) * 100).fillna(0)
    df_vis["PRODUCAO"] = df_vis[["SM","SM_EXPRESSA","CHECKLIST","MONITORAMENTO","SM_FORCADA"]].sum(axis=1)

    ultimo = df_vis.iloc[-1]
    anterior = df_vis.iloc[-2] if len(df_vis) > 1 else None
    delta_prod = int(ultimo["PRODUCAO"] - anterior["PRODUCAO"]) if anterior is not None else 0

    st.markdown(f"""
    <div class="charts-card">
      <div class="charts-title">LEITURA EXECUTIVA • {mes_filtro.upper()}</div>
      <div style="margin-top:12px;color:#c9d1d9;font-size:13px;line-height:1.7;">
        No período selecionado, o T3 recebeu <b>{demandas}</b> demandas e registrou
        <b style="color:#00e676">{concluidas}</b> conclusões, com <b>{atendimento:.1f}%</b> de atendimento.
        A operação contabilizou <b style="color:#00e676">{producao}</b> entregas de Gerenciamento de Risco.
        O SLA acumulado está em <b>{sla:.1f}%</b>, com tempo médio de <b>{tempo_medio:.1f} min</b>.
        O último dia registrado teve <b>{int(ultimo["PRODUCAO"])}</b> entregas
        ({delta_prod:+d} versus o registro anterior).
        Cancelamentos permanecem separados da produtividade.
      </div>
    </div>""", unsafe_allow_html=True)

    # Evolução diária
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_vis["DATA"], y=df_vis["PRODUCAO"], mode="lines+markers+text",
        name="Entregas T3", text=df_vis["PRODUCAO"], textposition="top center",
        line=dict(color="#00e676", width=3)
    ))
    fig.add_trace(go.Scatter(
        x=df_vis["DATA"], y=df_vis["DEMANDAS"], mode="lines+markers",
        name="Demandas", line=dict(color="#ffffff", width=2, dash="dot")
    ))
    fig.update_layout(
        title=dict(text="EVOLUÇÃO DIÁRIA • DEMANDAS x ENTREGAS T3", font=dict(size=13,color="#fff")),
        height=330, paper_bgcolor="#10141d", plot_bgcolor="#10141d",
        font=dict(color="#8b949e"), margin=dict(l=20,r=20,t=55,b=20),
        legend=dict(orientation="h", y=1.12),
        xaxis=dict(showgrid=False), yaxis=dict(gridcolor="#1c222e", zeroline=False)
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False}, key="hist_evolucao")

    # SLA e atendimento por dia
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=df_vis["DATA"], y=df_vis["ATENDIMENTO_%"],
                              mode="lines+markers", name="Atendimento %", line=dict(color="#00e676",width=3)))
    fig2.add_trace(go.Scatter(x=df_vis["DATA"], y=df_vis["SLA_%"],
                              mode="lines+markers", name="SLA %", line=dict(color="#ffb300",width=3)))
    fig2.add_hline(y=95, line_dash="dash", line_color="#ff5252", annotation_text="Meta 95%")
    fig2.update_layout(
        title=dict(text="PERFORMANCE DIÁRIA • ATENDIMENTO x SLA", font=dict(size=13,color="#fff")),
        height=320, paper_bgcolor="#10141d", plot_bgcolor="#10141d",
        font=dict(color="#8b949e"), margin=dict(l=20,r=20,t=55,b=20),
        yaxis=dict(range=[0,105], ticksuffix="%", gridcolor="#1c222e"),
        xaxis=dict(showgrid=False), legend=dict(orientation="h", y=1.12)
    )
    st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar":False}, key="hist_perf")

    # Mix de produção acumulado
    totais = [
        int(df_vis["SM"].sum()), int(df_vis["SM_EXPRESSA"].sum()),
        int(df_vis["CHECKLIST"].sum()), int(df_vis["MONITORAMENTO"].sum()),
        int(df_vis["SM_FORCADA"].sum())
    ]
    nomes = ["SM","SM Expressa","Checklists","Monitoramento","SM Forçada"]
    fig3 = go.Figure(go.Bar(x=nomes,y=totais,text=totais,textposition="outside",
                            marker=dict(color="#00e676",cornerradius=8)))
    fig3.update_layout(
        title=dict(text="PRODUÇÃO ACUMULADA POR ATIVIDADE",font=dict(size=13,color="#fff")),
        height=310,paper_bgcolor="#10141d",plot_bgcolor="#10141d",
        font=dict(color="#8b949e"),margin=dict(l=20,r=20,t=55,b=20),
        xaxis=dict(showgrid=False),yaxis=dict(gridcolor="#1c222e"),showlegend=False
    )
    st.plotly_chart(fig3,use_container_width=True,config={"displayModeBar":False},key="hist_mix")

    # Base histórica auditável + exportação
    st.markdown("### HISTÓRICO GRAVADO")
    tabela = df_vis.copy()
    tabela["DATA"] = tabela["DATA"].dt.strftime("%d/%m/%Y")
    cols_show = ["DATA","DEMANDAS","CONCLUIDAS","PENDENTES","CANCELADAS",
                 "SM","SM_EXPRESSA","CHECKLIST","MONITORAMENTO","SM_FORCADA",
                 "ATENDIMENTO_%","SLA_%","TEMPO_MEDIO"]
    st.dataframe(tabela[cols_show], use_container_width=True, hide_index=True)

    csv = tabela[cols_show].to_csv(index=False, sep=";", decimal=",").encode("utf-8-sig")
    st.download_button("BAIXAR HISTÓRICO CSV", data=csv,
                       file_name="historico_t3.csv", mime="text/csv", key="baixar_hist")

tab1, tab2, tab3, tab4 = st.tabs(["CADASTRO", "GER. RISCO", "TORRE MULTI", "T3 GERENCIAL"])

with tab1:
    render_tab_content("dados_cad", "cad")

with tab2:
    render_tab_content("dados_risco", "risco")


with tab3:
    render_torre_multi()

with tab4:
    render_t3_gerencial()
