import streamlit as st


# -----------------------------------------------------------------------------
# FUNÇÃO AUXILIAR: Cadastro / Ger. Risco (Aba 1 e 2)
# -----------------------------------------------------------------------------
def render_tab_content(key_session, prefix_key):
    """Renderiza a estrutura padrão para Cadastro e Gerenciamento de Risco."""
    if key_session not in st.session_state:
        st.session_state[key_session] = []

    dados = st.session_state[key_session]

    # Totais
    tot_qtd = sum(item.get("QTD", 0) for item in dados)
    tot_real = sum(item.get("REALIZADAS", 0) for item in dados)
    perf_geral = (tot_real / tot_qtd * 100) if tot_qtd > 0 else 0.0

    # Cards KPI Topo
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">TOTAL AGENDADO</div>
            <div class="kpi-value">{tot_qtd}</div>
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
            <div class="kpi-value-orange">{max(0, tot_qtd - tot_real)}</div>
        </div>
    """,
        unsafe_allow_html=True,
    )

    c4.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">PERFORMANCE</div>
            <div class="kpi-value-green">{perf_geral:.1f}%</div>
        </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown(
        "<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True
    )

    # Tabela de Edição de Dados
    st.markdown('<div class="card-floating">', unsafe_allow_html=True)
    h1, h2, h3, h4 = st.columns([2.5, 1.2, 1.2, 2.0])
    h1.markdown('<div class="th-title">CLIENTE</div>', unsafe_allow_html=True)
    h2.markdown(
        '<div class="th-title" style="text-align:center;">QTD</div>',
        unsafe_allow_html=True,
    )
    h3.markdown(
        '<div class="th-title" style="text-align:center;">REALIZADAS</div>',
        unsafe_allow_html=True,
    )
    h4.markdown('<div class="th-title">% PROGRESSO</div>', unsafe_allow_html=True)

    st.markdown(
        "<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True
    )

    for idx, item in enumerate(dados):
        col_cli, col_qtd, col_real, col_perc = st.columns([2.5, 1.2, 1.2, 2.0])

        qtd = item.get("QTD", 0)
        realizadas = item.get("REALIZADAS", 0)
        perc = (realizadas / qtd * 100) if qtd > 0 else 0.0

        if "get_status_e_cor" in globals():
            _, cor_bar, _ = get_status_e_cor(perc)
        else:
            cor_bar = "#00e676" if perc >= 80 else "#ffeb3b" if perc >= 50 else "#ff5252"

        with col_cli:
            st.markdown(
                f"<div style='padding-top:8px; font-weight:700; font-size:13px;'>{item.get('CLIENTE', '')}</div>",
                unsafe_allow_html=True,
            )

        with col_qtd:
            v_qtd = st.number_input(
                "",
                min_value=0,
                value=qtd,
                key=f"{prefix_key}_qtd_{idx}",
                label_visibility="collapsed",
            )
            if v_qtd != qtd:
                st.session_state[key_session][idx]["QTD"] = v_qtd
                if "salvar_dados" in globals():
                    salvar_dados(key_session, st.session_state[key_session])
                st.rerun()

        with col_real:
            v_real = st.number_input(
                "",
                min_value=0,
                max_value=v_qtd,
                value=min(realizadas, v_qtd),
                key=f"{prefix_key}_real_{idx}",
                label_visibility="collapsed",
            )
            if v_real != realizadas:
                st.session_state[key_session][idx]["REALIZADAS"] = v_real
                if "salvar_dados" in globals():
                    salvar_dados(key_session, st.session_state[key_session])
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

    st.markdown("</div>", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# FUNÇÃO: Aba TORRE MULTI
# -----------------------------------------------------------------------------
def render_torre_multi():
    tot_qtd = sum(
        item.get("QTD", 0) for item in st.session_state.dados_torre
    )
    tot_em_doca = sum(
        item.get("EM_DOCA", 0) for item in st.session_state.dados_torre
    )
    tot_em_transito = sum(
        item.get("EM_TRANSITO", 0) for item in st.session_state.dados_torre
    )
    tot_chegada_cliente = sum(
        item.get("CHEGADA_NO_CLIENTE", 0)
        for item in st.session_state.dados_torre
    )
    tot_finalizado = sum(
        item.get("FINALIZADO", 0) for item in st.session_state.dados_torre
    )

    st.markdown(
        """
        <div class="charts-card">
            <div class="charts-header">
                <div class="charts-title">DISTRIBUIÇÃO TORRE MULTI</div>
                <div class="charts-legend">
                    <span style="color:#00e676;">● EM DOCA</span>
                    <span style="color:#ffeb3b;">● EM TRÂNSITO</span>
                    <span style="color:#ff9800;">● CHEGADA NO CLIENTE</span>
                    <span style="color:#ff5252;">● FINALIZADO</span>
                </div>
            </div>
        """,
        unsafe_allow_html=True,
    )

    if "render_barra_empilhada_torre" in globals():
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

    if "render_mini_barras" in globals():
        render_mini_barras(dados_proc_torre, "torre")

    st.markdown("</div>", unsafe_allow_html=True)

    # Tabela
    st.markdown('<div class="card-floating">', unsafe_allow_html=True)

    h1, h2, h3, h4, h5, h6, h7 = st.columns([2.2, 1.0, 1.0, 1.1, 1.1, 1.0, 2.0])
    h1.markdown('<div class="th-title">CLIENTE</div>', unsafe_allow_html=True)
    h2.markdown('<div class="th-title" style="text-align:center;">QTD</div>', unsafe_allow_html=True)
    h3.markdown('<div class="th-title" style="text-align:center;"><span style="color:#00e676;">●</span> EM DOCA</div>', unsafe_allow_html=True)
    h4.markdown('<div class="th-title" style="text-align:center;"><span style="color:#ffeb3b;">●</span> EM TRANSITO</div>', unsafe_allow_html=True)
    h5.markdown('<div class="th-title" style="text-align:center;"><span style="color:#ff9800;">●</span> CHEGADA NO CLIENTE</div>', unsafe_allow_html=True)
    h6.markdown('<div class="th-title" style="text-align:center;"><span style="color:#ff5252;">●</span> FINALIZADO</div>', unsafe_allow_html=True)
    h7.markdown('<div class="th-title">%</div>', unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

    for idx, item in enumerate(st.session_state.dados_torre):
        col_cli, col_qtd, col_doca, col_trans, col_cheg, col_fin, col_perc = st.columns([2.2, 1.0, 1.0, 1.1, 1.1, 1.0, 2.0])

        qtd = item.get("QTD", 0)
        em_doca = item.get("EM_DOCA", 0)
        em_transito = item.get("EM_TRANSITO", 0)
        chegada_cli = item.get("CHEGADA_NO_CLIENTE", 0)
        finalizado = item.get("FINALIZADO", 0)

        perc = (em_doca / qtd * 100) if qtd > 0 else 0.0
        cor_bar = "#00e676" if perc >= 80 else "#ffeb3b" if perc >= 50 else "#ff5252"

        with col_cli:
            st.markdown(f"<div style='padding-top:8px; font-weight:700; font-size:13px;'>{item.get('CLIENTE', '')}</div>", unsafe_allow_html=True)

        with col_qtd:
            v = st.number_input("", min_value=0, value=qtd, key=f"t_qtd_{idx}", label_visibility="collapsed")
            if v != qtd:
                st.session_state.dados_torre[idx]["QTD"] = v
                if "salvar_dados" in globals(): salvar_dados("dados_torre", st.session_state.dados_torre)
                st.rerun()

        with col_doca:
            v = st.number_input("", min_value=0, max_value=qtd, value=min(em_doca, qtd), key=f"t_doca_{idx}", label_visibility="collapsed")
            if v != em_doca:
                st.session_state.dados_torre[idx]["EM_DOCA"] = v
                if "salvar_dados" in globals(): salvar_dados("dados_torre", st.session_state.dados_torre)
                st.rerun()

        with col_trans:
            v = st.number_input("", min_value=0, value=em_transito, key=f"t_trans_{idx}", label_visibility="collapsed")
            if v != em_transito:
                st.session_state.dados_torre[idx]["EM_TRANSITO"] = v
                if "salvar_dados" in globals(): salvar_dados("dados_torre", st.session_state.dados_torre)
                st.rerun()

        with col_cheg:
            v = st.number_input("", min_value=0, value=chegada_cli, key=f"t_cheg_{idx}", label_visibility="collapsed")
            if v != chegada_cli:
                st.session_state.dados_torre[idx]["CHEGADA_NO_CLIENTE"] = v
                if "salvar_dados" in globals(): salvar_dados("dados_torre", st.session_state.dados_torre)
                st.rerun()

        with col_fin:
            v = st.number_input("", min_value=0, value=finalizado, key=f"t_fin_{idx}", label_visibility="collapsed")
            if v != finalizado:
                st.session_state.dados_torre[idx]["FINALIZADO"] = v
                if "salvar_dados" in globals(): salvar_dados("dados_torre", st.session_state.dados_torre)
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

    st.markdown("</div>", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# FUNÇÃO: Aba TORRE MULTI GERENCIAL
# -----------------------------------------------------------------------------
def render_torre_multi_gerencial():
    tot_qtd = sum(item.get("QTD", 0) for item in st.session_state.dados_torre_gerencial)
    tot_no_prazo = sum(item.get("NO_PRAZO", 0) for item in st.session_state.dados_torre_gerencial)
    tot_atr_orig = sum(item.get("ATR_ORIG", 0) for item in st.session_state.dados_torre_gerencial)
    tot_atr_dest = sum(item.get("ATR_DEST", 0) for item in st.session_state.dados_torre_gerencial)
    tot_no_show = sum(item.get("NO_SHOW", 0) for item in st.session_state.dados_torre_gerencial)

    perf_geral = (tot_no_prazo / tot_qtd * 100) if tot_qtd > 0 else 0.0

    # Cards Resumo Topo
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.markdown(f'<div class="kpi-card"><div class="kpi-title">QTD</div><div class="kpi-value">{tot_qtd}</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="kpi-card"><div class="kpi-title">NO PRAZO</div><div class="kpi-value-green">{tot_no_prazo}</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="kpi-card"><div class="kpi-title">ATR. ORIGEM</div><div class="kpi-value-yellow">{tot_atr_orig}</div></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="kpi-card"><div class="kpi-title">ATR. DESTINO</div><div class="kpi-value-orange">{tot_atr_dest}</div></div>', unsafe_allow_html=True)
    c5.markdown(f'<div class="kpi-card"><div class="kpi-title">NO SHOW</div><div class="kpi-value-red">{tot_no_show}</div></div>', unsafe_allow_html=True)
    c6.markdown(f'<div class="kpi-card"><div class="kpi-title">PERFORMANCE</div><div class="kpi-value-green">{perf_geral:.1f}%</div></div>', unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 16px;'></div>", unsafe_allow_html=True)

    # Gráficos
    st.markdown(
        """
        <div class="charts-card">
            <div class="charts-header">
                <div class="charts-title">DISTRIBUIÇÃO DE STATUS GERENCIAIS</div>
                <div class="charts-legend">
                    <span style="color:#00e676;">● NO PRAZO</span>
                    <span style="color:#ffeb3b;">● ATR. ORIGEM</span>
                    <span style="color:#ff9800;">● ATR. DESTINO</span>
                    <span style="color:#ff5252;">● NO SHOW</span>
                </div>
            </div>
        """,
        unsafe_allow_html=True,
    )

    if "render_barra_empilhada_torre" in globals():
        render_barra_empilhada_torre(
            tot_no_prazo,
            tot_atr_orig,
            tot_atr_dest,
            tot_no_show,
            "stack_bar_torre_gerencial",
        )

    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    dados_proc_torre = []
    for item in st.session_state.dados_torre_gerencial:
        qtd = item.get("QTD", 0)
        no_prazo = item.get("NO_PRAZO", 0)
        perc = (no_prazo / qtd * 100) if qtd > 0 else 0.0
        dados_proc_torre.append({
            "CLIENTE": item.get("CLIENTE", ""),
            "REALIZADAS": no_prazo,
            "PENDENTES": max(0, qtd - no_prazo),
            "%": perc,
        })

    if "render_mini_barras" in globals():
        render_mini_barras(dados_proc_torre, "torre_gerencial")

    st.markdown("</div>", unsafe_allow_html=True)

    # Tabela
    st.markdown('<div class="card-floating">', unsafe_allow_html=True)

    h1, h2, h3, h4, h5, h6, h7 = st.columns([2.2, 1.0, 1.0, 1.1, 1.1, 1.0, 2.0])
    h1.markdown('<div class="th-title">CLIENTE</div>', unsafe_allow_html=True)
    h2.markdown('<div class="th-title" style="text-align:center;">QTD</div>', unsafe_allow_html=True)
    h3.markdown('<div class="th-title" style="text-align:center;"><span style="color:#00e676;">●</span> NO PRAZO</div>', unsafe_allow_html=True)
    h4.markdown('<div class="th-title" style="text-align:center;"><span style="color:#ffeb3b;">●</span> ATR. ORIGEM</div>', unsafe_allow_html=True)
    h5.markdown('<div class="th-title" style="text-align:center;"><span style="color:#ff9800;">●</span> ATR. DESTINO</div>', unsafe_allow_html=True)
    h6.markdown('<div class="th-title" style="text-align:center;"><span style="color:#ff5252;">●</span> NO SHOW</div>', unsafe_allow_html=True)
    h7.markdown('<div class="th-title">%</div>', unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

    for idx, item in enumerate(st.session_state.dados_torre_gerencial):
        col_cli, col_qtd, col_prazo, col_atrorig, col_atrdest, col_noshow, col_perc = st.columns([2.2, 1.0, 1.0, 1.1, 1.1, 1.0, 2.0])

        qtd = item.get("QTD", 0)
        no_prazo = item.get("NO_PRAZO", 0)
        atr_orig = item.get("ATR_ORIG", 0)
        atr_dest = item.get("ATR_DEST", 0)
        no_show = item.get("NO_SHOW", 0)

        perc = (no_prazo / qtd * 100) if qtd > 0 else 0.0
        cor_bar = "#00e676" if perc >= 80 else "#ffeb3b" if perc >= 50 else "#ff5252"

        with col_cli:
            st.markdown(f"<div style='padding-top:8px; font-weight:700; font-size:13px;'>{item.get('CLIENTE', '')}</div>", unsafe_allow_html=True)

        with col_qtd:
            v = st.number_input("", min_value=0, value=qtd, key=f"tg_qtd_{idx}", label_visibility="collapsed")
            if v != qtd:
                st.session_state.dados_torre_gerencial[idx]["QTD"] = v
                if "salvar_dados" in globals(): salvar_dados("dados_torre_gerencial", st.session_state.dados_torre_gerencial)
                st.rerun()

        with col_prazo:
            v = st.number_input("", min_value=0, max_value=qtd, value=min(no_prazo, qtd), key=f"tg_prazo_{idx}", label_visibility="collapsed")
            if v != no_prazo:
                st.session_state.dados_torre_gerencial[idx]["NO_PRAZO"] = v
                if "salvar_dados" in globals(): salvar_dados("dados_torre_gerencial", st.session_state.dados_torre_gerencial)
                st.rerun()

        with col_atrorig:
            v = st.number_input("", min_value=0, value=atr_orig, key=f"tg_atrorig_{idx}", label_visibility="collapsed")
            if v != atr_orig:
                st.session_state.dados_torre_gerencial[idx]["ATR_ORIG"] = v
                if "salvar_dados" in globals(): salvar_dados("dados_torre_gerencial", st.session_state.dados_torre_gerencial)
                st.rerun()

        with col_atrdest:
            v = st.number_input("", min_value=0, value=atr_dest, key=f"tg_atrdest_{idx}", label_visibility="collapsed")
            if v != atr_dest:
                st.session_state.dados_torre_gerencial[idx]["ATR_DEST"] = v
                if "salvar_dados" in globals(): salvar_dados("dados_torre_gerencial", st.session_state.dados_torre_gerencial)
                st.rerun()

        with col_noshow:
            v = st.number_input("", min_value=0, value=no_show, key=f"tg_noshow_{idx}", label_visibility="collapsed")
            if v != no_show:
                st.session_state.dados_torre_gerencial[idx]["NO_SHOW"] = v
                if "salvar_dados" in globals(): salvar_dados("dados_torre_gerencial", st.session_state.dados_torre_gerencial)
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

    st.markdown("</div>", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# ESTRUTURA PRINCIPAL DO APP E ABAS
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div class="header-container">
        <div class="header-left">
            <div class="avatar-icon">CB</div>
            <div>
                <div class="header-title">PAINEL OPERACIONAL MONITORING</div>
                <div class="header-sub">Gestão Operacional e Acompanhamento de Metas</div>
            </div>
        </div>
    </div>
""",
    unsafe_allow_html=True,
)

tab1, tab2, tab3, tab4 = st.tabs(
    ["CADASTRO", "GER. RISCO", "TORRE MULTI", "TORRE MULTI GERENCIAL"]
)

with tab1:
    render_tab_content("dados_cad", "cad")

with tab2:
    render_tab_content("dados_risco", "risco")

with tab3:
    render_torre_multi()

with tab4:
    render_torre_multi_gerencial()
