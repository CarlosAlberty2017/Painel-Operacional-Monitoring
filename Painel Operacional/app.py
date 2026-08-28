import firebase_admin
from firebase_admin import credentials, db
import plotly.graph_objects as go
import streamlit as st

# Configuração da página
st.set_page_config(
    page_title='Painel Operacional Monitoring', layout='wide'
)

# Conexão com o Firebase
if not firebase_admin._apps:
  firebase_dict = dict(st.secrets['firebase'])
  firebase_dict['private_key'] = firebase_dict['private_key'].replace(
      '\\n', '\n'
  )

  cred = credentials.Certificate(firebase_dict)
  firebase_admin.initialize_app(
      cred, {'databaseURL': st.secrets['firebase']['databaseURL']}
  )


# Funções de leitura e gravação no Firebase
def carregar_dados():
  ref = db.reference('dados_painel')
  dados = ref.get()
  return dados if dados else {}


def salvar_dados(chave_aba, novos_dados):
  ref = db.reference(f'dados_painel/{chave_aba}')
  ref.set(novos_dados)


# Carrega dados do Firebase na primeira inicialização da sessão
dados_firebase = carregar_dados()

if 'dados_cad' not in st.session_state:
  st.session_state.dados_cad = dados_firebase.get(
      'dados_cad',
      [
          {'CLIENTE': 'Airtable', 'QTD': 100, 'REALIZADAS': 100},
          {'CLIENTE': 'SPX', 'QTD': 120, 'REALIZADAS': 110},
          {'CLIENTE': 'Raster', 'QTD': 80, 'REALIZADAS': 70},
          {'CLIENTE': 'KMM', 'QTD': 60, 'REALIZADAS': 55},
          {'CLIENTE': 'Photocheck', 'QTD': 90, 'REALIZADAS': 85},
          {'CLIENTE': 'ELOG', 'QTD': 50, 'REALIZADAS': 48},
          {'CLIENTE': 'AMAZON', 'QTD': 110, 'REALIZADAS': 100},
      ],
  )

if 'dados_risco' not in st.session_state:
  st.session_state.dados_risco = dados_firebase.get(
      'dados_risco',
      [
          {'CLIENTE': 'SM', 'QTD': 50, 'REALIZADAS': 45},
          {'CLIENTE': 'SM Expressa', 'QTD': 30, 'REALIZADAS': 28},
          {'CLIENTE': 'Checklists', 'QTD': 80, 'REALIZADAS': 75},
          {'CLIENTE': 'SM Forçadas', 'QTD': 20, 'REALIZADAS': 15},
          {'CLIENTE': 'Monitoring', 'QTD': 100, 'REALIZADAS': 92},
      ],
  )

if 'dados_torre' not in st.session_state:
  st.session_state.dados_torre = dados_firebase.get(
      'dados_torre',
      [
          {
              'CLIENTE': 'Amazon',
              'QTD': 42,
              'NO_PRAZO': 40,
              'ATR_ORIG': 1,
              'ATR_DEST': 1,
              'NO_SHOW': 0,
          },
          {
              'CLIENTE': 'Imile',
              'QTD': 28,
              'NO_PRAZO': 25,
              'ATR_ORIG': 2,
              'ATR_DEST': 1,
              'NO_SHOW': 0,
          },
          {
              'CLIENTE': 'Decathlon',
              'QTD': 18,
              'NO_PRAZO': 18,
              'ATR_ORIG': 0,
              'ATR_DEST': 0,
              'NO_SHOW': 0,
          },
          {
              'CLIENTE': 'Loggi',
              'QTD': 35,
              'NO_PRAZO': 31,
              'ATR_ORIG': 2,
              'ATR_DEST': 2,
              'NO_SHOW': 0,
          },
          {
              'CLIENTE': 'Plural',
              'QTD': 12,
              'NO_PRAZO': 11,
              'ATR_ORIG': 0,
              'ATR_DEST': 1,
              'NO_SHOW': 0,
          },
          {
              'CLIENTE': 'Brasil Gráfica',
              'QTD': 9,
              'NO_PRAZO': 8,
              'ATR_ORIG': 0,
              'ATR_DEST': 1,
              'NO_SHOW': 0,
          },
          {
              'CLIENTE': 'Total Meli',
              'QTD': 54,
              'NO_PRAZO': 48,
              'ATR_ORIG': 3,
              'ATR_DEST': 2,
              'NO_SHOW': 1,
          },
          {
              'CLIENTE': 'Carrossel J&T',
              'QTD': 22,
              'NO_PRAZO': 20,
              'ATR_ORIG': 1,
              'ATR_DEST': 0,
              'NO_SHOW': 1,
          },
          {
              'CLIENTE': 'ANJUN',
              'QTD': 15,
              'NO_PRAZO': 13,
              'ATR_ORIG': 1,
              'ATR_DEST': 1,
              'NO_SHOW': 0,
          },
          {
              'CLIENTE': 'Americanas',
              'QTD': 31,
              'NO_PRAZO': 27,
              'ATR_ORIG': 2,
              'ATR_DEST': 1,
              'NO_SHOW': 1,
          },
          {
              'CLIENTE': 'Word Post',
              'QTD': 11,
              'NO_PRAZO': 10,
              'ATR_ORIG': 0,
              'ATR_DEST': 0,
              'NO_SHOW': 1,
          },
      ],
  )

# Estilização CSS Personalizada
st.markdown(
    """
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
""",
    unsafe_allow_html=True,
)


# Função para obter cor e status
def get_status_e_cor(perc):
  if perc <= 40.0:
    return 'BAIXO', '#ff5252', 'badge-baixo'
  elif perc <= 80.0:
    return 'REGULAR', '#ffb300', 'badge-regular'
  else:
    return 'ÓTIMO', '#00e676', 'badge-otimo'


# Funções de Renderização dos Gráficos
def render_barra_empilhada(v1, v2, chart_key):
  fig = go.Figure()
  fig.add_trace(
      go.Bar(
          y=['GERAL'],
          x=[v1],
          orientation='h',
          width=0.6,
          text=[f'{v1}'],
          textposition='inside',
          insidetextanchor='middle',
          textfont=dict(color='#000000', size=13, family='sans-serif'),
          marker=dict(color='#00e676', cornerradius=10),
      )
  )
  fig.add_trace(
      go.Bar(
          y=['GERAL'],
          x=[v2],
          orientation='h',
          width=0.6,
          text=[f'{v2}' if v2 > 0 else ''],
          textposition='inside',
          insidetextanchor='middle',
          textfont=dict(color='#ffffff', size=13, family='sans-serif'),
          marker=dict(color='#ff5252', cornerradius=10),
      )
  )
  fig.update_layout(
      barmode='stack',
      height=36,
      margin=dict(l=0, r=0, t=0, b=0),
      paper_bgcolor='rgba(0,0,0,0)',
      plot_bgcolor='rgba(0,0,0,0)',
      showlegend=False,
      xaxis=dict(showgrid=False, visible=False),
      yaxis=dict(showgrid=False, visible=False),
  )
  st.plotly_chart(
      fig,
      use_container_width=True,
      config={'displayModeBar': False},
      key=chart_key,
  )


def render_barra_empilhada_torre(v_np, v_ao, v_ad, v_ns, chart_key):
  fig = go.Figure()
  fig.add_trace(
      go.Bar(
          y=['GERAL'],
          x=[v_np],
          orientation='h',
          width=0.6,
          text=[f'{v_np}' if v_np > 0 else ''],
          textposition='inside',
          insidetextanchor='middle',
          textfont=dict(color='#000000', size=13, family='sans-serif'),
          marker=dict(color='#00e676', cornerradius=10),
      )
  )
  fig.add_trace(
      go.Bar(
          y=['GERAL'],
          x=[v_ao],
          orientation='h',
          width=0.6,
          text=[f'{v_ao}' if v_ao > 0 else ''],
          textposition='inside',
          insidetextanchor='middle',
          textfont=dict(color='#000000', size=13, family='sans-serif'),
          marker=dict(color='#ffeb3b', cornerradius=10),
      )
  )
  fig.add_trace(
      go.Bar(
          y=['GERAL'],
          x=[v_ad],
          orientation='h',
          width=0.6,
          text=[f'{v_ad}' if v_ad > 0 else ''],
          textposition='inside',
          insidetextanchor='middle',
          textfont=dict(color='#ffffff', size=13, family='sans-serif'),
          marker=dict(color='#ff9800', cornerradius=10),
      )
  )
  fig.add_trace(
      go.Bar(
          y=['GERAL'],
          x=[v_ns],
          orientation='h',
          width=0.6,
          text=[f'{v_ns}' if v_ns > 0 else ''],
          textposition='inside',
          insidetextanchor='middle',
          textfont=dict(color='#ffffff', size=13, family='sans-serif'),
          marker=dict(color='#ff5252', cornerradius=10),
      )
  )
  fig.update_layout(
      barmode='stack',
      height=36,
      margin=dict(l=0, r=0, t=0, b=0),
      paper_bgcolor='rgba(0,0,0,0)',
      plot_bgcolor='rgba(0,0,0,0)',
      showlegend=False,
      xaxis=dict(showgrid=False, visible=False),
      yaxis=dict(showgrid=False, visible=False),
  )
  st.plotly_chart(
      fig,
      use_container_width=True,
      config={'displayModeBar': False},
      key=chart_key,
  )


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
        st.markdown(
            f"<div style='font-size:12px; font-weight:700; color:#ffffff;"
            f" padding-top:5px; white-space:nowrap;'>{item['CLIENTE']}</div>",
            unsafe_allow_html=True,
        )
      with c_bar:
        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                y=[''],
                x=[real],
                orientation='h',
                width=0.6,
                text=[f'{real}'],
                textposition='inside',
                insidetextanchor='middle',
                textfont=dict(color='#000000', size=11, family='sans-serif'),
                marker=dict(color='#00e676', cornerradius=10),
            )
        )
        fig.add_trace(
            go.Bar(
                y=[''],
                x=[pend],
                orientation='h',
                width=0.6,
                text=[f'{pend}' if pend > 0 else ''],
                textposition='inside',
                insidetextanchor='middle',
                textfont=dict(color='#ffffff', size=11, family='sans-serif'),
                marker=dict(color='#ff5252', cornerradius=10),
            )
        )
        fig.update_layout(
            barmode='stack',
            height=30,
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False,
            xaxis=dict(showgrid=False, visible=False),
            yaxis=dict(showgrid=False, visible=False),
        )
        st.plotly_chart(
            fig,
            use_container_width=True,
            config={'displayModeBar': False},
            key=f'mini_bar_{prefix_key}_{i}',
        )
      with c_txt:
        st.markdown(
            f"<div style='font-size:12px; font-weight:800; color:{cor_p};"
            f" text-align:left; padding-left:4px; padding-top:5px;'>{perc:.0f}%</div>",
            unsafe_allow_html=True,
        )


# Renderização genérica para CADASTRO e GER. RISCO
def render_tab_content(state_key, prefix_key):
  tot_qtd, tot_real = 0, 0
  dados_processados = []

  for item in st.session_state[state_key]:
    qtd = item['QTD']
    real = min(item['REALIZADAS'], qtd)
    pend = 0 if real >= qtd else (qtd - real)
    perc = (
        100.0
        if (qtd > 0 and real >= qtd)
        else (round((real / qtd * 100), 1) if qtd > 0 else 0.0)
    )

    tot_qtd += qtd
    tot_real += real
    dados_processados.append({
        'CLIENTE': item['CLIENTE'],
        'QTD': qtd,
        'REALIZADAS': real,
        'PENDENTES': pend,
        '%': perc,
    })

  tot_pend = max(0, tot_qtd - tot_real)
  perf_geral = (
      100.0
      if (tot_qtd > 0 and tot_real >= tot_qtd)
      else (round((tot_real / tot_qtd * 100), 1) if tot_qtd > 0 else 0.0)
  )

  # Cards Resumo Topo
  c1, c2, c3, c4 = st.columns(4)
  c1.markdown(
      f"""
        <div class="kpi-card">
            <div class="kpi-title">QTD TOTAL</div>
            <div class="kpi-value">{tot_qtd}</div>
            <div class="kpi-bar-white"></div>
        </div>
    """,
      unsafe_allow_html=True,
  )

  c2.markdown(
      f"""
        <div class="kpi-card">
            <div class="kpi-title">REALIZADAS</div>
            <div class="kpi-value-green">{tot_real}</div>
        </div>
    """,
      unsafe_allow_html=True,
  )

  c3.markdown(
      f"""
        <div class="kpi-card">
            <div class="kpi-title">PENDENTES</div>
            <div class="kpi-value-red">{tot_pend}</div>
        </div>
    """,
      unsafe_allow_html=True,
  )

  c4.markdown(
      f"""
        <div class="kpi-card">
            <div class="kpi-title">PERFORMANCE</div>
            <div class="kpi-value-green">{perf_geral:.1f}%</div>
            <div class="kpi-bar-green"></div>
        </div>
    """,
      unsafe_allow_html=True,
  )

  st.markdown(
      "<div style='margin-bottom: 16px;'></div>", unsafe_allow_html=True
  )

  # Gráficos
  st.markdown(
      """
        <div class="charts-card">
            <div class="charts-header">
                <div class="charts-title">REALIZADAS vs PENDENTES</div>
                <div class="charts-legend">
                    <span style="color:#00e676;">● REALIZADAS</span>
                    <span style="color:#ff5252;">● PENDENTES</span>
                </div>
            </div>
    """,
      unsafe_allow_html=True,
  )

  render_barra_empilhada(tot_real, tot_pend, f'stack_bar_{prefix_key}')
  st.markdown(
      "<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True
  )
  render_mini_barras(dados_processados, prefix_key)
  st.markdown('</div>', unsafe_allow_html=True)

  # Tabela
  st.markdown('<div class="card-floating">', unsafe_allow_html=True)

  h1, h2, h3, h4, h5, h6 = st.columns([2.5, 1.2, 1.2, 1.2, 2.5, 1.5])
  h1.markdown(
      '<div class="th-title">CLIENTE / TIPO</div>', unsafe_allow_html=True
  )
  h2.markdown(
      '<div class="th-title" style="text-align:center;">QTD</div>',
      unsafe_allow_html=True,
  )
  h3.markdown(
      '<div class="th-title" style="text-align:center;">REALIZADAS</div>',
      unsafe_allow_html=True,
  )
  h4.markdown(
      '<div class="th-title" style="text-align:center;">PENDENTES</div>',
      unsafe_allow_html=True,
  )
  h5.markdown('<div class="th-title">%</div>', unsafe_allow_html=True)
  h6.markdown(
      '<div class="th-title" style="text-align:center;">STATUS</div>',
      unsafe_allow_html=True,
  )

  st.markdown(
      "<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True
  )

  for idx, r in enumerate(dados_processados):
    col_cli, col_qtd, col_real, col_pend, col_perc, col_stat = st.columns(
        [2.5, 1.2, 1.2, 1.2, 2.5, 1.5]
    )
    status_txt, cor_bar, badge_class = get_status_e_cor(r['%'])

    with col_cli:
      st.markdown(
          "<div style='padding-top:8px; font-weight:700;"
          f" font-size:13px;'>{r['CLIENTE']}</div>",
          unsafe_allow_html=True,
      )

    with col_qtd:
      n_qtd = st.number_input(
          '',
          min_value=0,
          value=r['QTD'],
          key=f'{prefix_key}_q_{idx}',
          label_visibility='collapsed',
      )
      if n_qtd != st.session_state[state_key][idx]['QTD']:
        st.session_state[state_key][idx]['QTD'] = n_qtd
        salvar_dados(state_key, st.session_state[state_key])
        st.rerun()

    with col_real:
      n_real = st.number_input(
          '',
          min_value=0,
          max_value=n_qtd,
          value=min(r['REALIZADAS'], n_qtd),
          key=f'{prefix_key}_r_{idx}',
          label_visibility='collapsed',
      )
      if n_real != st.session_state[state_key][idx]['REALIZADAS']:
        st.session_state[state_key][idx]['REALIZADAS'] = n_real
        salvar_dados(state_key, st.session_state[state_key])
        st.rerun()

    with col_pend:
      st.markdown(
          "<div style='padding-top:8px; font-weight:700; color:#8b949e;"
          f" text-align:center; font-size:13px;'>{r['PENDENTES']}</div>",
          unsafe_allow_html=True,
      )

    with col_perc:
      st.markdown(
          f"""
                <div style="padding-top:8px; display:flex; align-items:center; gap:12px;">
                    <div class="progress-bar-bg">
                        <div class="progress-bar-fill" style="width:{r['%']}%; background-color:{cor_bar};"></div>
                    </div>
                    <span style="font-size:12px; font-weight:800; color:{cor_bar}; min-width:42px;">{r['%']:.1f}%</span>
                </div>
            """,
          unsafe_allow_html=True,
      )

    with col_stat:
      st.markdown(
          "<div style='padding-top:4px; text-align:center;'><span"
          f" class='{badge_class}'>● {status_txt}</span></div>",
          unsafe_allow_html=True,
      )

    st.markdown(
        "<div style='margin-bottom: 8px;'></div>", unsafe_allow_html=True
    )

  st.markdown('</div>', unsafe_allow_html=True)


# Renderização da Aba TORRE MULTI
def render_torre_multi():
  # Cálculo dos totais
  tot_qtd = sum(item.get("QTD", 0) for item in st.session_state.dados_torre)
  tot_em_doca = sum(
      item.get("EM_DOCA", 0) for item in st.session_state.dados_torre
  )
  tot_em_transito = sum(
      item.get("EM_TRANSITO", 0) for item in st.session_state.dados_torre
  )
  tot_chegada_cliente = sum(
      item.get("CHEGADA_NO_CLIENTE", 0) for item in st.session_state.dados_torre
  )
  tot_finalizado = sum(
      item.get("FINALIZADO", 0) for item in st.session_state.dados_torre
  )

  perf_geral = (tot_em_doca / tot_qtd * 100) if tot_qtd > 0 else 0.0

  # Cards Resumo Topo
  c1, c2, c3, c4, c5, c6 = st.columns(6)
  c1.markdown(
      f"""
        <div class="kpi-card">
            <div class="kpi-title">QTD</div>
            <div class="kpi-value">{tot_qtd}</div>
            <div class="kpi-bar-white"></div>
        </div>
    """,
      unsafe_allow_html=True,
  )

  c2.markdown(
      f"""
        <div class="kpi-card">
            <div class="kpi-title">EM DOCA</div>
            <div class="kpi-value-green">{tot_em_doca}</div>
        </div>
    """,
      unsafe_allow_html=True,
  )

  c3.markdown(
      f"""
        <div class="kpi-card">
            <div class="kpi-title">EM TRANSITO</div>
            <div class="kpi-value-yellow">{tot_em_transito}</div>
        </div>
    """,
      unsafe_allow_html=True,
  )

  c4.markdown(
      f"""
        <div class="kpi-card">
            <div class="kpi-title">CHEGADA NO CLIENTE</div>
            <div class="kpi-value-orange">{tot_chegada_cliente}</div>
        </div>
    """,
      unsafe_allow_html=True,
  )

  c5.markdown(
      f"""
        <div class="kpi-card">
            <div class="kpi-title">FINALIZADO</div>
            <div class="kpi-value-red">{tot_finalizado}</div>
        </div>
    """,
      unsafe_allow_html=True,
  )

  c6.markdown(
      f"""
        <div class="kpi-card">
            <div class="kpi-title">PERFORMANCE</div>
            <div class="kpi-value-green">{perf_geral:.1f}%</div>
            <div class="kpi-bar-green"></div>
        </div>
    """,
      unsafe_allow_html=True,
  )

  st.markdown(
      "<div style='margin-bottom: 16px;'></div>", unsafe_allow_html=True
  )

  # Gráficos
  st.markdown(
      """
        <div class="charts-card">
            <div class="charts-header">
                <div class="charts-title">DISTRIBUIÇÃO DE OCORRÊNCIAS POR STATUS</div>
                <div class="charts-legend">
                    <span style="color:#00e676;">● EM DOCA</span>
                    <span style="color:#ffeb3b;">● EM TRANSITO</span>
                    <span style="color:#ff9800;">● CHEGADA NO CLIENTE</span>
                    <span style="color:#ff5252;">● FINALIZADO</span>
                </div>
            </div>
    """,
      unsafe_allow_html=True,
  )

  render_barra_empilhada_torre(
      tot_em_doca,
      tot_em_transito,
      tot_chegada_cliente,
      tot_finalizado,
      "stack_bar_torre",
  )
  st.markdown(
      "<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True
  )

  dados_proc_torre = []
  for item in st.session_state.dados_torre:
    qtd = item.get("QTD", 0)
    em_doca = item.get("EM_DOCA", 0)
    perc = (em_doca / qtd * 100) if qtd > 0 else 0.0
    dados_proc_torre.append({
        "CLIENTE": item.get("CLIENTE", ""),
        "REALIZADAS": em_doca,
        "PENDENTES": max(0, qtd - em_doca),
        "%": perc,
    })

  render_mini_barras(dados_proc_torre, "torre")
  st.markdown("</div>", unsafe_allow_html=True)

  # Tabela
  st.markdown('<div class="card-floating">', unsafe_allow_html=True)

  h1, h2, h3, h4, h5, h6, h7 = st.columns([2.2, 1.0, 1.0, 1.1, 1.1, 1.0, 2.0])
  h1.markdown('<div class="th-title">CLIENTE</div>', unsafe_allow_html=True)
  h2.markdown(
      '<div class="th-title" style="text-align:center;">QTD</div>',
      unsafe_allow_html=True,
  )
  h3.markdown(
      '<div class="th-title" style="text-align:center;"><span'
      ' style="color:#00e676;">●</span> EM DOCA</div>',
      unsafe_allow_html=True,
  )
  h4.markdown(
      '<div class="th-title" style="text-align:center;"><span'
      ' style="color:#ffeb3b;">●</span> EM TRANSITO</div>',
      unsafe_allow_html=True,
  )
  h5.markdown(
      '<div class="th-title" style="text-align:center;"><span'
      ' style="color:#ff9800;">●</span> CHEGADA NO CLIENTE</div>',
      unsafe_allow_html=True,
  )
  h6.markdown(
      '<div class="th-title" style="text-align:center;"><span'
      ' style="color:#ff5252;">●</span> FINALIZADO</div>',
      unsafe_allow_html=True,
  )
  h7.markdown('<div class="th-title">%</div>', unsafe_allow_html=True)

  st.markdown(
      "<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True
  )

  for idx, item in enumerate(st.session_state.dados_torre):
    col_cli, col_qtd, col_doca, col_trans, col_cheg, col_fin, col_perc = (
        st.columns([2.2, 1.0, 1.0, 1.1, 1.1, 1.0, 2.0])
    )

    qtd = item.get("QTD", 0)
    em_doca = item.get("EM_DOCA", 0)
    em_transito = item.get("EM_TRANSITO", 0)
    chegada_cli = item.get("CHEGADA_NO_CLIENTE", 0)
    finalizado = item.get("FINALIZADO", 0)

    perc = (em_doca / qtd * 100) if qtd > 0 else 0.0
    _, cor_bar, _ = get_status_e_cor(perc)

    with col_cli:
      st.markdown(
          "<div style='padding-top:8px; font-weight:700;"
          f" font-size:13px;'>{item.get('CLIENTE', '')}</div>",
          unsafe_allow_html=True,
      )

    with col_qtd:
      v = st.number_input(
          "",
          min_value=0,
          value=qtd,
          key=f"t_qtd_{idx}",
          label_visibility="collapsed",
      )
      if v != qtd:
        st.session_state.dados_torre[idx]["QTD"] = v
        salvar_dados("dados_torre", st.session_state.dados_torre)
        st.rerun()

    with col_doca:
      v = st.number_input(
          "",
          min_value=0,
          max_value=qtd,
          value=min(em_doca, qtd),
          key=f"t_doca_{idx}",
          label_visibility="collapsed",
      )
      if v != em_doca:
        st.session_state.dados_torre[idx]["EM_DOCA"] = v
        salvar_dados("dados_torre", st.session_state.dados_torre)
        st.rerun()

    with col_trans:
      v = st.number_input(
          "",
          min_value=0,
          value=em_transito,
          key=f"t_trans_{idx}",
          label_visibility="collapsed",
      )
      if v != em_transito:
        st.session_state.dados_torre[idx]["EM_TRANSITO"] = v
        salvar_dados("dados_torre", st.session_state.dados_torre)
        st.rerun()

    with col_cheg:
      v = st.number_input(
          "",
          min_value=0,
          value=chegada_cli,
          key=f"t_cheg_{idx}",
          label_visibility="collapsed",
      )
      if v != chegada_cli:
        st.session_state.dados_torre[idx]["CHEGADA_NO_CLIENTE"] = v
        salvar_dados("dados_torre", st.session_state.dados_torre)
        st.rerun()

    with col_fin:
      v = st.number_input(
          "",
          min_value=0,
          value=finalizado,
          key=f"t_fin_{idx}",
          label_visibility="collapsed",
      )
      if v != finalizado:
        st.session_state.dados_torre[idx]["FINALIZADO"] = v
        salvar_dados("dados_torre", st.session_state.dados_torre)
        st.rerun()

    with col_perc:
      st.markdown(
          f"""
                <div style="padding-top:8px; display:flex; align-items:center; gap:12px;">
                    <div class="progress-bar-bg">
                        <div class="progress-bar-fill" style="width:{perc}%; background-color:{cor_bar};"></div>
                    </div>
                    <span style="font-size:12px; font-weight:800; color:{cor_bar}; min-width:42px;">{perc:.1f}%</span>
                </div>
            """,
          unsafe_allow_html=True,
      )

    st.markdown(
        "<div style='margin-bottom: 8px;'></div>", unsafe_allow_html=True
    )

  st.markdown("</div>", unsafe_allow_html=True)


# Header Principal
st.markdown(
    """
    <div class="header-container">
        <div class="header-left">
            <div class="avatar-icon">AN</div>
            <div>
                <div class="header-title">Painel Operacional Monitoring</div>
                <div class="header-sub">Operacional • QTD vs Realizadas • Sincronizado via Firebase</div>
            </div>
        </div>
    </div>
""",
    unsafe_allow_html=True,
)

tab1, tab2, tab3 = st.tabs(["CADASTRO", "GER. RISCO", "TORRE MULTI"])

with tab1:
  render_tab_content("dados_cad", "cad")

with tab2:
  render_tab_content("dados_risco", "risco")

with tab3:
  render_torre_multi()
