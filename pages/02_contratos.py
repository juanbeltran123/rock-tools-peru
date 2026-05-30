import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from database.conexion import run_query, run_query_in

# Configuración de la página
st.set_page_config(
    page_title="Rock Tools Peru - Contratos",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Ocultar sidebar y estilos profesionales
st.markdown("""
<style>
    [data-testid="stSidebar"] {display: none;}
    [data-testid="collapsedControl"] {display: none;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .main > .block-container {
        padding-top: 0 !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 100%;
    }
    
    /* === ESTILOS PROFESIONALES PARA TABLAS === */
    .stDataFrame {
        margin: 0 auto !important;
        border-radius: 16px !important;
        overflow: hidden !important;
        border: 1px solid #E5E7EB !important;
    }
    
    .stDataFrame thead th,
    .stDataFrame thead tr th,
    div[data-testid="stDataFrame"] thead tr th {
        background: #1E3A5F !important;
        color: white !important;
        font-weight: 700 !important;
        font-size: 0.8rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        text-align: center !important;
        padding: 12px 8px !important;
        border-bottom: 2px solid #2C5F8A !important;
    }
    
    .stDataFrame tbody td,
    div[data-testid="stDataFrame"] tbody tr td {
        text-align: center !important;
        font-size: 0.85rem !important;
        padding: 10px 8px !important;
        border-bottom: 1px solid #E5E7EB !important;
    }
    
    .stDataFrame tbody td:first-child,
    div[data-testid="stDataFrame"] tbody tr td:first-child {
        text-align: left !important;
        font-weight: 500 !important;
    }
    
    .stDataFrame tbody tr:nth-child(even) td,
    div[data-testid="stDataFrame"] tbody tr:nth-child(even) td {
        background-color: #F8FAFC !important;
    }
    
    .stDataFrame tbody tr:nth-child(odd) td,
    div[data-testid="stDataFrame"] tbody tr:nth-child(odd) td {
        background-color: #FFFFFF !important;
    }
    
    .stDataFrame tbody tr:hover td,
    div[data-testid="stDataFrame"] tbody tr:hover td {
        background-color: #E8EDF2 !important;
    }
    
    .dataframe {
        font-size: 0.85rem !important;
    }
    
    .positive-margin {
        color: #10b981;
        font-weight: 600;
    }
    .negative-margin {
        color: #ef4444;
        font-weight: 600;
    }
    .warning-margin {
        color: #f59e0b;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Verificar autenticación
if 'autenticado' not in st.session_state or not st.session_state['autenticado']:
    st.switch_page("app.py")

if 'usuario' not in st.session_state:
    st.session_state['usuario'] = 'Admin'

# ============================================================================
# FUNCIÓN PARA COLOR DE MARGEN
# ============================================================================
def color_margen(val):
    try:
        if isinstance(val, str):
            val = val.replace('%', '')
        num = float(val)
        if num >= 42:
            return 'color: #10b981; font-weight: bold;'
        elif num >= 30:
            return 'color: #f59e0b; font-weight: bold;'
        else:
            return 'color: #ef4444; font-weight: bold;'
    except:
        return ''

def color_eficiencia_val(val):
    try:
        if isinstance(val, str):
            val = val.replace('%', '')
        num = float(val)
        if num >= 100:
            return 'color: #10b981; font-weight: bold;'
        elif num >= 90:
            return 'color: #f59e0b; font-weight: bold;'
        else:
            return 'color: #ef4444; font-weight: bold;'
    except:
        return ''

def color_margen_tabla(val):
    try:
        if isinstance(val, str):
            val = val.replace('%', '')
        num = float(val)
        if num >= 42:
            return 'color: #10b981; font-weight: bold;'
        elif num >= 30:
            return 'color: #f59e0b; font-weight: bold;'
        else:
            return 'color: #ef4444; font-weight: bold;'
    except:
        return ''

# ============================================================================
# HEADER CON NAVEGACIÓN
# ============================================================================
header_cols = st.columns([1, 3, 1, 1])

with header_cols[0]:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px;">
        <div style="background: #1152d4; color: white; width: 40px; height: 40px; 
                    border-radius: 8px; display: flex; align-items: center; 
                    justify-content: center; font-weight: bold; font-size: 20px;">
            R
        </div>
        <div>
            <div style="font-weight: 600; color: #1e293b;">ROCK TOOLS</div>
            <div style="font-size: 12px; color: #64748b;">PERU</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with header_cols[1]:
    nav_cols = st.columns(7)
    with nav_cols[0]:
        if st.button("📊 Dashboard", key="nav_dash", use_container_width=True):
            st.switch_page("pages/01_dashboard.py")
    with nav_cols[1]:
        if st.button("📄 Contratos", key="nav_cont", use_container_width=True):
            st.switch_page("pages/02_contratos.py")
    with nav_cols[2]:
        if st.button("📈 Resultados", key="nav_res", use_container_width=True):
            st.switch_page("pages/04_resultados_proyecciones.py")
    with nav_cols[3]:
        if st.button("📊 Análisis", use_container_width=True):
            st.switch_page("pages/07_analisis_avanzado.py")
    with nav_cols[4]:
        if st.button("📤 Cargas", key="nav_carg", use_container_width=True):
            st.switch_page("pages/03_cargas.py")    
    with nav_cols[5]:
        if st.button("📚 Maestros", key="nav_maes", use_container_width=True):
            st.switch_page("pages/05_maestros.py")

with header_cols[2]:
    usuario = st.session_state.get('usuario', 'Usuario')
    st.markdown(f"""
    <div style="text-align: right;">
        <div style="font-weight: 500; color: #1e293b;">{usuario}</div>
        <div style="font-size: 12px; color: #64748b;">Administrador</div>
    </div>
    """, unsafe_allow_html=True)

with header_cols[3]:
    if st.button("🚪 Salir", type="secondary", use_container_width=True):
        st.session_state.clear()
        st.switch_page("app.py")

st.divider()

# ============================================================================
# FUNCIÓN AUXILIAR PARA OBTENER DATOS DE VISTAS
# ============================================================================
def get_general_data(periodos=None, id_contrato=None, id_cliente=None, semana=None, tipo_reporte=None):
    """Obtiene datos de vw_general_semanal con filtros"""
    supabase = get_supabase()
    query = supabase.table("vw_general_semanal").select("*")
    
    if periodos:
        query = query.in_("periodo", periodos)
    if id_contrato:
        query = query.eq("id_contrato", id_contrato)
    if id_cliente:
        query = query.eq("id_cliente", id_cliente)
    if semana and semana != "CIERRE":
        query = query.eq("semana", int(semana)).eq("tipo_reporte", "AVANCE")
    if tipo_reporte == "CIERRE":
        query = query.eq("tipo_reporte", "CIERRE")
    
    response = query.execute()
    return pd.DataFrame(response.data) if response.data else pd.DataFrame()

# Nota: get_supabase debe estar importada
from database.conexion import get_supabase, run_query, run_query_in

# ============================================================================
# TABS PRINCIPALES
# ============================================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 RESUMEN GLOBAL", 
    "📋 DETALLE POR CONTRATO", 
    "📊 EVOLUCIÓN SEMANAL",
    "📉 ANÁLISIS POR METRO"
])

# ============================================================================
# TAB 1: RESUMEN GLOBAL
# ============================================================================
with tab1:
    st.markdown("### 📊 Resumen Global")
    
    # ===== OBTENER PERIODOS DISPONIBLES =====
    df1 = run_query("vw_general_semanal", select="periodo")
    df2 = run_query("vw_cpm_resultado", select="periodo")
    df3 = run_query("vw_venta", select="periodo")
    
    todos_periodos = pd.concat([df1, df2, df3], ignore_index=True)
    periodos_disponibles = todos_periodos['periodo'].drop_duplicates().sort_values(ascending=False).tolist() if not todos_periodos.empty else []
    
    # ===== FILTROS =====
    col_titulo, col_periodo, col_semana = st.columns([1, 2, 2])
    
    with col_titulo:
        st.markdown("#### 📊 Resumen Global")
    
    with col_periodo:
        opciones_periodos = ["TODOS"] + periodos_disponibles
        periodos_seleccionados = st.multiselect(
            "📅 Período(s)",
            options=opciones_periodos,
            default=[periodos_disponibles[0]] if periodos_disponibles else ["TODOS"],
            key="filtro_periodos_tab1"
        )
        
        if "TODOS" in periodos_seleccionados:
            periodos_seleccionados = periodos_disponibles.copy() if periodos_disponibles else []
        periodos_originales = periodos_seleccionados.copy() if periodos_seleccionados else []
    
    with col_semana:
        if periodos_seleccionados:
            df_general = run_query_in("vw_general_semanal", "periodo", periodos_seleccionados)
            
            df_avance = df_general[(df_general['tipo_reporte'] == 'AVANCE') & (df_general['semana'] > 0)]
            semanas_avance = df_avance['semana'].drop_duplicates().sort_values().tolist()
            
            df_cierre = df_general[df_general['tipo_reporte'] == 'CIERRE']
            periodos_con_cierre = df_cierre['periodo'].drop_duplicates().tolist()
            tiene_cierre = len(periodos_con_cierre) > 0
        else:
            semanas_avance = []
            tiene_cierre = False
            periodos_con_cierre = []
        
        opciones_semanas = []
        if tiene_cierre:
            opciones_semanas.append("CIERRE")
        opciones_semanas.extend([str(s) for s in semanas_avance])
        
        if not opciones_semanas:
            opciones_semanas = ["NO HAY DATOS"]
        
        semana_seleccionada = st.selectbox(
            "📊 Semana",
            options=opciones_semanas,
            index=0,
            key="filtro_semana_tab1"
        )
        
        if semana_seleccionada == "NO HAY DATOS":
            st.warning("⚠️ No hay datos de semanas disponibles para los períodos seleccionados")
            st.stop()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ===== APLICAR FILTROS =====
    if not periodos_seleccionados:
        st.warning("⚠️ No hay períodos seleccionados")
        st.stop()
    
    # Aplicar filtros de semana
    usar_cierre = (semana_seleccionada == "CIERRE")
    semana_valor = None if usar_cierre else int(semana_seleccionada)
    
    df_filtrado = run_query_in("vw_general_semanal", "periodo", periodos_seleccionados)
    
    if usar_cierre:
        df_filtrado = df_filtrado[df_filtrado['tipo_reporte'] == 'CIERRE']
    elif semana_valor:
        df_filtrado = df_filtrado[(df_filtrado['tipo_reporte'] == 'AVANCE') & (df_filtrado['semana'] == semana_valor)]
    else:
        df_filtrado = df_filtrado[df_filtrado['tipo_reporte'] == 'AVANCE']
    
    # ===== KPI PRINCIPALES =====
    ingresos_totales = df_filtrado[df_filtrado['tipo'].isin(['CPM', 'VENTA'])]['ingresos'].sum()
    costos_totales = df_filtrado[df_filtrado['tipo'].isin(['CPM', 'VENTA'])]['costos'].sum() + df_filtrado['otros_costos'].sum()
    margen_total = ingresos_totales - costos_totales
    margen_pct = (1 - costos_totales/ingresos_totales) * 100 if ingresos_totales > 0 else 0
    
    kpi_cols = st.columns(4)
    
    with kpi_cols[0]:
        with st.container(border=True):
            st.markdown("<div style='text-align: center;'>💰 Ingresos Totales</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='text-align: center; font-size: 1.5rem; font-weight: 700; color: #1152d4;'>${ingresos_totales:,.0f}</div>", unsafe_allow_html=True)
    
    with kpi_cols[1]:
        with st.container(border=True):
            st.markdown("<div style='text-align: center;'>💸 Costos Totales</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='text-align: center; font-size: 1.5rem; font-weight: 700; color: #ef4444;'>${costos_totales:,.0f}</div>", unsafe_allow_html=True)
    
    with kpi_cols[2]:
        with st.container(border=True):
            st.markdown("<div style='text-align: center;'>📊 Margen Total</div>", unsafe_allow_html=True)
            color = "#10b981" if margen_total > 0 else "#ef4444"
            st.markdown(f"<div style='text-align: center; font-size: 1.5rem; font-weight: 700; color: {color};'>${margen_total:,.0f}</div>", unsafe_allow_html=True)
    
    with kpi_cols[3]:
        with st.container(border=True):
            st.markdown("<div style='text-align: center;'>🎯 Margen %</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='text-align: center; font-size: 1.5rem; font-weight: 700;'>{margen_pct:.1f}%</div>", unsafe_allow_html=True)
            objetivo = 42
            progreso = min(margen_pct / objetivo, 1.0) if margen_pct > 0 else 0
            st.progress(progreso, text=f"Objetivo: {objetivo}%")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ===== POR TIPO DE OPERACIÓN =====
    st.markdown("### ⛏️ Por Tipo de Operación")
    
    # Obtener contratos con sus tipos
    df_contratos_tipos = run_query("contratos", select="id, nombre, tipo_operacion")
    
    tipo_cols = st.columns(2)
    
    for idx, tipo in enumerate(['SUPERFICIAL', 'SUBTERRANEA']):
        contratos_tipo = df_contratos_tipos[df_contratos_tipos['tipo_operacion'] == tipo]['id'].tolist()
        
        if contratos_tipo:
            df_tipo = df_filtrado[df_filtrado['id_contrato'].isin(contratos_tipo)]
            ingresos = df_tipo[df_tipo['tipo'].isin(['CPM', 'VENTA'])]['ingresos'].sum()
            costos = df_tipo[df_tipo['tipo'].isin(['CPM', 'VENTA'])]['costos'].sum() + df_tipo['otros_costos'].sum()
            utilidad = ingresos - costos
            margen = (utilidad / ingresos * 100) if ingresos > 0 else 0
            
            with tipo_cols[idx]:
                with st.container(border=True):
                    st.markdown(f"<h3 style='text-align: center; color: #1152d4;'>{tipo}</h3>", unsafe_allow_html=True)
                    
                    col_i1, col_i2 = st.columns(2)
                    with col_i1:
                        st.markdown("<div style='text-align: center;'>💰 Ingresos</div>", unsafe_allow_html=True)
                        st.markdown(f"<div style='text-align: center; font-size: 1.2rem; font-weight: 700;'>${ingresos:,.0f}</div>", unsafe_allow_html=True)
                    with col_i2:
                        st.markdown("<div style='text-align: center;'>💸 Costos</div>", unsafe_allow_html=True)
                        st.markdown(f"<div style='text-align: center; font-size: 1.2rem; font-weight: 700;'>${costos:,.0f}</div>", unsafe_allow_html=True)
                    
                    st.markdown("---")
                    
                    col_u1, col_u2 = st.columns(2)
                    with col_u1:
                        st.markdown("<div style='text-align: center;'>📊 Utilidad</div>", unsafe_allow_html=True)
                        color_u = "#10b981" if utilidad > 0 else "#ef4444"
                        st.markdown(f"<div style='text-align: center; font-size: 1.2rem; font-weight: 700; color: {color_u};'>${utilidad:,.0f}</div>", unsafe_allow_html=True)
                    with col_u2:
                        st.markdown("<div style='text-align: center;'>🎯 Margen %</div>", unsafe_allow_html=True)
                        st.markdown(f"<div style='text-align: center; font-size: 1.2rem; font-weight: 700;'>{margen:.1f}%</div>", unsafe_allow_html=True)
        else:
            with tipo_cols[idx]:
                with st.container(border=True):
                    st.markdown(f"<h3 style='text-align: center; color: #1152d4;'>{tipo}</h3>", unsafe_allow_html=True)
                    st.markdown("<div style='text-align: center; color: #64748b;'>Sin datos para este tipo</div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ===== GRÁFICO DE MÁRGENES POR CONTRATO =====
    st.markdown("### 📊 Margen por Contrato vs Objetivo 42%")
    
    contratos = run_query("contratos", select="id, nombre", filters={"activo": 1})
    
    datos_grafico = []
    for _, contrato in contratos.iterrows():
        df_cont = df_filtrado[df_filtrado['id_contrato'] == contrato['id']]
        ingresos = df_cont[df_cont['tipo'].isin(['CPM', 'VENTA'])]['ingresos'].sum()
        costos = df_cont[df_cont['tipo'].isin(['CPM', 'VENTA'])]['costos'].sum() + df_cont['otros_costos'].sum()
        
        if ingresos > 0:
            margen = (1 - costos/ingresos) * 100
            datos_grafico.append({
                'Contrato': contrato['nombre'],
                'Margen %': margen
            })
    
    if datos_grafico:
        df_grafico = pd.DataFrame(datos_grafico)
        df_grafico = df_grafico.sort_values('Margen %', ascending=True)
        
        colores = []
        for m in df_grafico['Margen %']:
            if m >= 42:
                colores.append('#2C5F8A')
            elif m >= 30:
                colores.append('#F59E0B')
            else:
                colores.append('#9CA3AF')
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df_grafico['Margen %'],
            y=df_grafico['Contrato'],
            orientation='h',
            marker_color=colores,
            text=df_grafico['Margen %'].round(1).astype(str) + '%',
            textposition='outside'
        ))
        fig.add_vline(x=42, line_dash="dash", line_color="#2C5F8A", line_width=2,
                     annotation_text="🎯 Objetivo 42%", annotation_position="top")
        fig.update_layout(height=500, margin=dict(l=0, r=80, t=40, b=0))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay datos para mostrar")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ===== TABLA DE CONTRATOS =====
    st.markdown("### 📋 Detalle por Contrato")
    
    datos_contratos_lista = []
    for _, contrato in contratos.iterrows():
        df_cont = df_filtrado[df_filtrado['id_contrato'] == contrato['id']]
        ingresos = df_cont[df_cont['tipo'].isin(['CPM', 'VENTA'])]['ingresos'].sum()
        costos = df_cont[df_cont['tipo'].isin(['CPM', 'VENTA'])]['costos'].sum() + df_cont['otros_costos'].sum()
        
        if ingresos > 0 or costos > 0:
            margen = (1 - costos/ingresos) * 100 if ingresos > 0 else 0
            datos_contratos_lista.append({
                'Contrato': contrato['nombre'],
                'Ingresos': ingresos,
                'Costos': costos,
                'Margen': margen,
                'Utilidad': ingresos - costos
            })
    
    if datos_contratos_lista:
        df_contratos_lista = pd.DataFrame(datos_contratos_lista)
        df_contratos_lista = df_contratos_lista.sort_values('Margen', ascending=False)
        
        html_table = """
        <style>
            .pro-table { width: 100%; max-width: 1200px; margin: 0 auto; border-collapse: collapse; font-family: 'Inter', sans-serif; border: 1px solid #D1D5DB; }
            .pro-table th { background: #1A2A3A; color: white; font-weight: 600; font-size: 0.8rem; text-transform: uppercase; padding: 14px 12px; text-align: center; }
            .pro-table td { padding: 12px 12px; font-size: 0.85rem; text-align: center; border-bottom: 1px solid #E5E7EB; background-color: white; }
            .pro-table tr:hover td { background-color: #F5F7FA; }
            .pro-table td:first-child { text-align: left; font-weight: 500; }
            .margen-excelente { color: #10B981; font-weight: 600; }
            .margen-aceptable { color: #F59E0B; font-weight: 600; }
            .margen-critico { color: #EF4444; font-weight: 600; }
        </style>
        <table class="pro-table">
            <thead><tr><th>CONTRATO</th><th>INGRESOS</th><th>COSTOS</th><th>UTILIDAD</th><th>MARGEN %</th><th>ESTADO</th></tr></thead>
            <tbody>
        """
        
        for _, row in df_contratos_lista.iterrows():
            if row['Margen'] >= 42:
                clase_margen = "margen-excelente"
                estado = "Excelente"
            elif row['Margen'] >= 30:
                clase_margen = "margen-aceptable"
                estado = "Aceptable"
            else:
                clase_margen = "margen-critico"
                estado = "Crítico"
            
            html_table += f"""
                <tr>
                    <td style="text-align: left;">{row['Contrato']}</td>
                    <td>${row['Ingresos']:,.0f}</td>
                    <td>${row['Costos']:,.0f}</td>
                    <td>${row['Utilidad']:,.0f}</td>
                    <td class="{clase_margen}">{row['Margen']:.1f}%</td>
                    <td>{estado}</td>
                </tr>
            """
        
        html_table += "</tbody></table>"
        st.html(html_table)
    else:
        st.info("No hay datos de contratos para los filtros seleccionados")

# ============================================================================
# TAB 2: DETALLE POR CONTRATO
# ============================================================================
with tab2:
    st.markdown("### 📋 Detalle por Contrato")
    
    # ===== OBTENER PERIODOS =====
    periodos_disponibles = run_query("vw_general_semanal", select="periodo")['periodo'].drop_duplicates().sort_values(ascending=False).tolist()
    
    if not periodos_disponibles:
        st.warning("⚠️ No hay períodos con datos cargados")
        st.stop()
    
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    
    with col_f1:
        periodo_principal = st.selectbox("📅 Período", periodos_disponibles, key="detalle_periodo_principal")
    
    # Contratos con datos en el período
    df_contratos_filtrados = run_query_in("vw_general_semanal", "periodo", [periodo_principal], select="id_contrato")
    ids_contratos = df_contratos_filtrados['id_contrato'].drop_duplicates().tolist()
    
    contratos_filtrados = run_query("contratos", select="id, nombre", filters={"activo": 1})
    contratos_filtrados = contratos_filtrados[contratos_filtrados['id'].isin(ids_contratos)]
    
    if contratos_filtrados.empty:
        st.warning(f"⚠️ No hay contratos con datos en el período {periodo_principal}")
        st.stop()
    
    with col_f2:
        contrato_nombre = st.selectbox("📋 Contrato", contratos_filtrados['nombre'].tolist(), key="detalle_contrato")
        id_contrato = contratos_filtrados[contratos_filtrados['nombre'] == contrato_nombre]['id'].iloc[0]
    
    clientes = run_query("clientes", select="id, nombre, codigo", filters={"id_contrato": id_contrato, "activo": 1})
    
    with col_f3:
        cliente_opciones = {"TODOS": None}
        for _, row in clientes.iterrows():
            cliente_opciones[f"{row['nombre']} ({row['codigo']})"] = row['id']
        cliente_seleccionado = st.selectbox("👤 Cliente", list(cliente_opciones.keys()), key="detalle_cliente")
        id_cliente = cliente_opciones[cliente_seleccionado]
    
    with col_f4:
        df_semanas = run_query_in("vw_general_semanal", "periodo", [periodo_principal], select="semana, tipo_reporte")
        df_semanas = df_semanas[(df_semanas['tipo_reporte'] == 'AVANCE') & (df_semanas['semana'] > 0)]
        semanas_avance = df_semanas['semana'].drop_duplicates().sort_values().tolist()
        
        df_cierre = run_query_in("vw_general_semanal", "periodo", [periodo_principal], select="periodo")
        df_cierre = df_cierre[df_cierre['tipo_reporte'] == 'CIERRE']
        tiene_cierre = len(df_cierre) > 0
        
        opciones_semanas = []
        if tiene_cierre:
            opciones_semanas.append("CIERRE")
        opciones_semanas.extend([str(s) for s in semanas_avance])
        
        if not opciones_semanas:
            opciones_semanas = ["NO HAY DATOS"]
        
        semana_seleccionada = st.selectbox("📊 Semana", options=opciones_semanas, index=0, key="detalle_semana_unica")
        
        if semana_seleccionada == "NO HAY DATOS":
            st.warning("⚠️ No hay datos de semanas disponibles")
            st.stop()
    
    st.markdown("---")
    
    # ===== APLICAR FILTROS =====
    usar_cierre = (semana_seleccionada == "CIERRE")
    semana_valor = None if usar_cierre else int(semana_seleccionada)
    
    df_general = run_query_in("vw_general_semanal", "periodo", [periodo_principal])
    df_general = df_general[df_general['id_contrato'] == id_contrato]
    
    if id_cliente:
        df_general = df_general[df_general['id_cliente'] == id_cliente]
    
    if usar_cierre:
        df_general = df_general[df_general['tipo_reporte'] == 'CIERRE']
    elif semana_valor:
        df_general = df_general[(df_general['tipo_reporte'] == 'AVANCE') & (df_general['semana'] == semana_valor)]
    
    # ===== SUBPESTAÑAS =====
    sub_tab1, sub_tab2 = st.tabs(["📊 OPERACIONES", "📈 RENDIMIENTO"])
    
    with sub_tab1:
        # ----- CPM -----
        st.markdown("#### 💰 CPM")
        
        df_cpm = df_general[df_general['tipo'] == 'CPM'].copy()
        
        if not df_cpm.empty:
            total_ingresos_cpm = df_cpm['ingresos'].sum()
            total_costos_cpm = df_cpm['costos'].sum()
            total_margen_cpm = total_ingresos_cpm - total_costos_cpm
            margen_pct_cpm = (total_margen_cpm / total_ingresos_cpm * 100) if total_ingresos_cpm > 0 else 0
            
            col_c1, col_c2, col_c3 = st.columns(3)
            with col_c1:
                with st.container(border=True):
                    st.markdown("<div style='text-align: center; font-size: 0.75rem;'>💰 Ingresos CPM</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='text-align: center; font-size: 1.5rem; font-weight: 700; color: #1152d4;'>${total_ingresos_cpm:,.0f}</div>", unsafe_allow_html=True)
            with col_c2:
                with st.container(border=True):
                    st.markdown("<div style='text-align: center; font-size: 0.75rem;'>💸 Costos CPM</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='text-align: center; font-size: 1.5rem; font-weight: 700; color: #ef4444;'>${total_costos_cpm:,.0f}</div>", unsafe_allow_html=True)
            with col_c3:
                with st.container(border=True):
                    st.markdown("<div style='text-align: center; font-size: 0.75rem;'>📊 Margen CPM</div>", unsafe_allow_html=True)
                    color = "#10b981" if total_margen_cpm > 0 else "#ef4444"
                    st.markdown(f"<div style='text-align: center; font-size: 1.5rem; font-weight: 700; color: {color};'>${total_margen_cpm:,.0f}</div>", unsafe_allow_html=True)
                    st.caption(f"{margen_pct_cpm:.1f}% del ingreso")
            
            df_cpm_display = df_cpm[['periodo', 'semana', 'id_tipo_perforacion', 'ingresos', 'costos']].copy()
            df_cpm_display['utilidad'] = df_cpm_display['ingresos'] - df_cpm_display['costos']
            df_cpm_display['margen_pct'] = (df_cpm_display['utilidad'] / df_cpm_display['ingresos'] * 100).fillna(0)
            
            df_cpm_display['ingresos'] = df_cpm_display['ingresos'].apply(lambda x: f"${x:,.0f}")
            df_cpm_display['costos'] = df_cpm_display['costos'].apply(lambda x: f"${x:,.0f}")
            df_cpm_display['utilidad'] = df_cpm_display['utilidad'].apply(lambda x: f"${x:,.0f}")
            df_cpm_display['margen_pct'] = df_cpm_display['margen_pct'].apply(lambda x: f"{x:.1f}%")
            
            df_cpm_display = df_cpm_display.rename(columns={
                'periodo': 'Período', 'semana': 'Semana', 'id_tipo_perforacion': 'Tipo Perforación',
                'ingresos': 'Ingresos', 'costos': 'Costos', 'utilidad': 'Utilidad', 'margen_pct': 'Margen %'
            })
            
            st.dataframe(df_cpm_display.style.applymap(color_margen, subset=['Margen %']), use_container_width=True, hide_index=True)
        else:
            st.info("No hay datos CPM para los filtros seleccionados")
        
        st.markdown("---")
        
        # ----- AFILADORAS -----
        st.markdown("#### 💸 Afiladoras")
        
        df_afil = df_general[df_general['tipo'] == 'AFILADORAS'].copy()
        
        if not df_afil.empty:
            total_costo_afil = df_afil['otros_costos'].sum()
            
            col_a1, col_a2 = st.columns(2)
            with col_a1:
                with st.container(border=True):
                    st.markdown("<div style='text-align: center; font-size: 0.75rem;'>🔧 Total Afiladoras</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='text-align: center; font-size: 1.5rem; font-weight: 700;'>${total_costo_afil:,.0f}</div>", unsafe_allow_html=True)
            with col_a2:
                with st.container(border=True):
                    st.markdown("<div style='text-align: center; font-size: 0.75rem;'>📦 Registros</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='text-align: center; font-size: 1.5rem; font-weight: 700;'>{len(df_afil)}</div>", unsafe_allow_html=True)
            
            df_afil_display = df_afil[['periodo', 'semana', 'otros_costos']].copy()
            df_afil_display['costo_total'] = df_afil_display['otros_costos'].apply(lambda x: f"${x:,.0f}")
            df_afil_display = df_afil_display.rename(columns={'periodo': 'Período', 'semana': 'Semana', 'costo_total': 'Costo Total'})
            st.dataframe(df_afil_display, use_container_width=True, hide_index=True)
        else:
            st.info("No hay datos de Afiladoras para los filtros seleccionados")
        
        st.markdown("---")
        
        # ----- VENTA -----
        st.markdown("#### 📦 Venta")
        
        df_venta = df_general[df_general['tipo'] == 'VENTA'].copy()
        
        if not df_venta.empty:
            total_ingresos_venta = df_venta['ingresos'].sum()
            total_costos_venta = df_venta['costos'].sum()
            total_margen_venta = total_ingresos_venta - total_costos_venta
            margen_pct_venta = (total_margen_venta / total_ingresos_venta * 100) if total_ingresos_venta > 0 else 0
            
            col_v1, col_v2, col_v3, col_v4 = st.columns(4)
            with col_v1:
                with st.container(border=True):
                    st.markdown("<div style='text-align: center; font-size: 0.7rem;'>💰 Ingresos Venta</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='text-align: center; font-size: 1.2rem; font-weight: 700;'>${total_ingresos_venta:,.0f}</div>", unsafe_allow_html=True)
            with col_v2:
                with st.container(border=True):
                    st.markdown("<div style='text-align: center; font-size: 0.7rem;'>💸 Costos Venta</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='text-align: center; font-size: 1.2rem; font-weight: 700;'>${total_costos_venta:,.0f}</div>", unsafe_allow_html=True)
            with col_v3:
                with st.container(border=True):
                    st.markdown("<div style='text-align: center; font-size: 0.7rem;'>📊 Margen Venta</div>", unsafe_allow_html=True)
                    color = "#10b981" if total_margen_venta > 0 else "#ef4444"
                    st.markdown(f"<div style='text-align: center; font-size: 1.2rem; font-weight: 700; color: {color};'>${total_margen_venta:,.0f}</div>", unsafe_allow_html=True)
            with col_v4:
                with st.container(border=True):
                    st.markdown("<div style='text-align: center; font-size: 0.7rem;'>🎯 Margen %</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='text-align: center; font-size: 1.2rem; font-weight: 700;'>{margen_pct_venta:.1f}%</div>", unsafe_allow_html=True)
            
            df_venta_display = df_venta[['periodo', 'semana', 'ingresos', 'costos']].copy()
            df_venta_display['utilidad'] = df_venta_display['ingresos'] - df_venta_display['costos']
            df_venta_display['margen_pct'] = (df_venta_display['utilidad'] / df_venta_display['ingresos'] * 100).fillna(0)
            
            df_venta_display['ingresos'] = df_venta_display['ingresos'].apply(lambda x: f"${x:,.0f}")
            df_venta_display['costos'] = df_venta_display['costos'].apply(lambda x: f"${x:,.0f}")
            df_venta_display['utilidad'] = df_venta_display['utilidad'].apply(lambda x: f"${x:,.0f}")
            df_venta_display['margen_pct'] = df_venta_display['margen_pct'].apply(lambda x: f"{x:.1f}%")
            
            df_venta_display = df_venta_display.rename(columns={
                'periodo': 'Período', 'semana': 'Semana', 'ingresos': 'Ingresos',
                'costos': 'Costos', 'utilidad': 'Utilidad', 'margen_pct': 'Margen %'
            })
            
            st.dataframe(df_venta_display.style.applymap(color_margen, subset=['Margen %']), use_container_width=True, hide_index=True)
        else:
            st.info("No hay datos de Venta para los filtros seleccionados")
        
        st.markdown("---")
        
        # ----- RESUMEN GENERAL -----
        st.markdown("## 📊 RESUMEN GENERAL DE CONTRATO")
        
        total_ingresos = df_general[df_general['tipo'].isin(['CPM', 'VENTA'])]['ingresos'].sum()
        total_costos = df_general[df_general['tipo'].isin(['CPM', 'VENTA'])]['costos'].sum() + df_general['otros_costos'].sum()
        roi_total = total_ingresos - total_costos
        roi_pct = (roi_total / total_ingresos * 100) if total_ingresos > 0 else 0
        
        col_r1, col_r2, col_r3, col_r4 = st.columns(4)
        with col_r1:
            with st.container(border=True):
                st.markdown("<div style='text-align: center;'>💰 Total Ingresos</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='text-align: center; font-size: 1.5rem; font-weight: 700;'>${total_ingresos:,.0f}</div>", unsafe_allow_html=True)
        with col_r2:
            with st.container(border=True):
                st.markdown("<div style='text-align: center;'>💸 Total Costos</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='text-align: center; font-size: 1.5rem; font-weight: 700;'>${total_costos:,.0f}</div>", unsafe_allow_html=True)
        with col_r3:
            with st.container(border=True):
                st.markdown("<div style='text-align: center;'>📊 Ganancia</div>", unsafe_allow_html=True)
                color = "#10b981" if roi_total > 0 else "#ef4444"
                st.markdown(f"<div style='text-align: center; font-size: 1.5rem; font-weight: 700; color: {color};'>${roi_total:,.0f}</div>", unsafe_allow_html=True)
        with col_r4:
            with st.container(border=True):
                st.markdown("<div style='text-align: center;'>🎯 Margen %</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='text-align: center; font-size: 1.5rem; font-weight: 700;'>{roi_pct:.1f}%</div>", unsafe_allow_html=True)
                st.progress(min(roi_pct/42, 1.0) if roi_pct > 0 else 0, text="Objetivo: 42%")
    
    with sub_tab2:
        st.markdown("#### 📈 Rendimiento vs Objetivos")
        
        # Obtener datos de rendimiento
        df_rend = run_query_in("vw_rendimiento_detalle", "periodo", [periodo_principal])
        df_rend = df_rend[df_rend['id_contrato'] == id_contrato]
        
        if id_cliente:
            df_rend = df_rend[df_rend['id_cliente'] == id_cliente]
        
        if usar_cierre:
            df_rend = df_rend[df_rend['tipo_reporte'] == 'CIERRE']
        elif semana_valor:
            df_rend = df_rend[(df_rend['tipo_reporte'] == 'AVANCE') & (df_rend['semana'] == semana_valor)]
        
        if not df_rend.empty:
            tipos_perforacion = df_rend['tipo_perforacion'].unique()
            
            for tipo in tipos_perforacion:
                df_tipo = df_rend[df_rend['tipo_perforacion'] == tipo].copy()
                st.markdown(f"##### 🔨 {tipo}")
                
                df_tipo = df_tipo[['familia', 'periodo', 'semana', 'metros_aplicables', 'total_acero', 'rendimiento', 'rendimiento_objetivo', 'eficiencia_porcentaje']].copy()
                df_tipo.columns = ['FAMILIA', 'PERIODO', 'SEMANA', 'METROS', 'CANTIDAD', 'RENDIMIENTO', 'OBJETIVO', 'EFICIENCIA']
                
                df_tipo['METROS'] = df_tipo['METROS'].fillna(0).round(0).astype(int)
                df_tipo['CANTIDAD'] = df_tipo['CANTIDAD'].fillna(0).round(0).astype(int)
                df_tipo['RENDIMIENTO'] = df_tipo['RENDIMIENTO'].fillna(0).round(2)
                df_tipo['OBJETIVO'] = df_tipo['OBJETIVO'].fillna(0).round(2)
                df_tipo['EFICIENCIA'] = df_tipo['EFICIENCIA'].fillna(0).round(1).astype(str) + '%'
                
                st.dataframe(df_tipo.style.applymap(color_eficiencia_val, subset=['EFICIENCIA']), use_container_width=True, hide_index=True)
                st.markdown("<br>", unsafe_allow_html=True)
        else:
            st.info("No hay datos de rendimiento para los filtros seleccionados")

# ============================================================================
# TAB 3: EVOLUCIÓN SEMANAL
# ============================================================================
with tab3:
    st.markdown("### 📈 Evolución de Márgenes")
    
    sub_tab1, sub_tab2 = st.tabs(["📊 Semana a Semana", "📈 Mes a Mes"])
    
    with sub_tab1:
        st.markdown("#### Evolución Semanal (Acumulado por período)")
        
        periodos_todos_evo = run_query("vw_general_semanal", select="periodo")
        periodos_todos_evo = periodos_todos_evo[periodos_todos_evo['tipo_reporte'] == 'AVANCE']['periodo'].drop_duplicates().sort_values(ascending=False).tolist()
        
        if not periodos_todos_evo:
            st.warning("⚠️ No hay períodos con datos de AVANCE")
            st.stop()
        
        col_f1, col_f2, col_f3 = st.columns(3)
        
        with col_f1:
            periodo_evo = st.selectbox("📅 Período", periodos_todos_evo, key="evo_periodo_principal")
        
        # Contratos con datos
        df_contratos_evo = run_query_in("vw_general_semanal", "periodo", [periodo_evo], select="id_contrato")
        ids_contratos_evo = df_contratos_evo['id_contrato'].drop_duplicates().tolist()
        contratos_con_datos_evo = run_query("contratos", select="id, nombre", filters={"activo": 1})
        contratos_con_datos_evo = contratos_con_datos_evo[contratos_con_datos_evo['id'].isin(ids_contratos_evo)]
        
        if contratos_con_datos_evo.empty:
            with col_f2:
                st.warning(f"⚠️ No hay contratos con datos en {periodo_evo}")
            st.stop()
        
        with col_f2:
            contrato_nombre = st.selectbox("📋 Contrato", contratos_con_datos_evo['nombre'].tolist(), key="evo_semanal_contrato")
            id_contrato = contratos_con_datos_evo[contratos_con_datos_evo['nombre'] == contrato_nombre]['id'].iloc[0]
        
        clientes_evo = run_query("clientes", select="id, nombre, codigo", filters={"id_contrato": id_contrato, "activo": 1})
        
        with col_f3:
            cliente_opciones = {"TODOS": None}
            for _, row in clientes_evo.iterrows():
                cliente_opciones[f"{row['nombre']} ({row['codigo']})"] = row['id']
            cliente_seleccionado = st.selectbox("👤 Cliente", list(cliente_opciones.keys()), key="evo_semanal_cliente")
            id_cliente = cliente_opciones[cliente_seleccionado]
        
        st.markdown("---")
        
        # Obtener datos
        df_evolucion = run_query_in("vw_general_semanal", "periodo", [periodo_evo])
        df_evolucion = df_evolucion[df_evolucion['id_contrato'] == id_contrato]
        df_evolucion = df_evolucion[df_evolucion['tipo'] == 'CPM']
        df_evolucion = df_evolucion[df_evolucion['tipo_reporte'] == 'AVANCE']
        
        if id_cliente:
            df_evolucion = df_evolucion[df_evolucion['id_cliente'] == id_cliente]
        
        if not df_evolucion.empty:
            # Agrupar por semana
            df_evolucion_group = df_evolucion.groupby('semana').agg({
                'ingresos': 'sum',
                'costos': 'sum',
                'otros_costos': 'sum'
            }).reset_index()
            
            df_evolucion_group['costos_totales'] = df_evolucion_group['costos'] + df_evolucion_group['otros_costos']
            df_evolucion_group['margen'] = df_evolucion_group['ingresos'] - df_evolucion_group['costos_totales']
            df_evolucion_group['margen_pct'] = (df_evolucion_group['margen'] / df_evolucion_group['ingresos'] * 100).fillna(0)
            df_evolucion_group = df_evolucion_group.sort_values('semana')
            
            # Tarjetas de totales
            total_ingresos = df_evolucion_group['ingresos'].sum()
            total_costos = df_evolucion_group['costos_totales'].sum()
            total_margen = total_ingresos - total_costos
            margen_pct_total = (total_margen / total_ingresos * 100) if total_ingresos > 0 else 0
            
            col_t1, col_t2, col_t3, col_t4 = st.columns(4)
            with col_t1:
                with st.container(border=True):
                    st.markdown("<div style='text-align: center;'>💰 Ingresos Totales</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='text-align: center; font-size: 1.3rem; font-weight: 700;'>${total_ingresos:,.0f}</div>", unsafe_allow_html=True)
            with col_t2:
                with st.container(border=True):
                    st.markdown("<div style='text-align: center;'>💸 Costos Totales</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='text-align: center; font-size: 1.3rem; font-weight: 700;'>${total_costos:,.0f}</div>", unsafe_allow_html=True)
            with col_t3:
                with st.container(border=True):
                    st.markdown("<div style='text-align: center;'>📊 Margen Total</div>", unsafe_allow_html=True)
                    color = "#10b981" if total_margen > 0 else "#ef4444"
                    st.markdown(f"<div style='text-align: center; font-size: 1.3rem; font-weight: 700; color: {color};'>${total_margen:,.0f}</div>", unsafe_allow_html=True)
            with col_t4:
                with st.container(border=True):
                    st.markdown("<div style='text-align: center;'>🎯 Margen %</div>", unsafe_allow_html=True)
                    color_m = "#10b981" if margen_pct_total >= 42 else "#f59e0b" if margen_pct_total >= 30 else "#ef4444"
                    st.markdown(f"<div style='text-align: center; font-size: 1.3rem; font-weight: 700; color: {color_m};'>{margen_pct_total:.1f}%</div>", unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Gráfico
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_evolucion_group['semana'],
                y=df_evolucion_group['margen_pct'],
                mode='lines+markers',
                name='Margen %',
                line=dict(color='#1152d4', width=3),
                marker=dict(size=10, color='#1152d4'),
                text=df_evolucion_group['margen_pct'].round(1).astype(str) + '%',
                textposition='top center'
            ))
            fig.add_hline(y=42, line_dash="dash", line_color="#10b981", line_width=2,
                         annotation_text="🎯 Objetivo 42%", annotation_position="top right")
            fig.update_layout(title=f"Evolución del Margen - {periodo_evo}", height=450)
            st.plotly_chart(fig, use_container_width=True)
            
            # Tabla
            st.markdown("#### 📋 Detalle Semanal")
            df_tabla = df_evolucion_group[['semana', 'ingresos', 'costos_totales', 'margen', 'margen_pct']].copy()
            df_tabla.columns = ['Semana', 'Ingresos', 'Costos', 'Margen', 'Margen %']
            df_tabla['Ingresos'] = df_tabla['Ingresos'].apply(lambda x: f"${x:,.0f}")
            df_tabla['Costos'] = df_tabla['Costos'].apply(lambda x: f"${x:,.0f}")
            df_tabla['Margen'] = df_tabla['Margen'].apply(lambda x: f"${x:,.0f}")
            df_tabla['Margen %'] = df_tabla['Margen %'].apply(lambda x: f"{x:.1f}%")
            
            st.dataframe(df_tabla.style.applymap(color_margen_tabla, subset=['Margen %']), use_container_width=True, hide_index=True)
        else:
            st.info(f"No hay datos para {periodo_evo} con los filtros seleccionados")
    
    with sub_tab2:
        st.markdown("#### Comparativa Mensual (CIERRE por período)")
        
        periodos_disponibles_mensual = run_query("vw_general_semanal", select="periodo")
        periodos_disponibles_mensual = periodos_disponibles_mensual[periodos_disponibles_mensual['tipo_reporte'] == 'CIERRE']['periodo'].drop_duplicates().sort_values(ascending=False).tolist()
        
        if not periodos_disponibles_mensual:
            st.warning("⚠️ No hay períodos con datos de CIERRE")
            st.stop()
        
        col_m1, col_m2, col_m3 = st.columns(3)
        
        with col_m1:
            opciones_periodos = ["TODOS"] + periodos_disponibles_mensual
            periodos_seleccionados = st.multiselect("📅 Período(s)", options=opciones_periodos,
                default=[periodos_disponibles_mensual[0]] if periodos_disponibles_mensual else ["TODOS"],
                key="evo_mensual_periodos")
            
            if "TODOS" in periodos_seleccionados:
                periodos_seleccionados = periodos_disponibles_mensual
        
        if not periodos_seleccionados:
            st.warning("⚠️ Seleccione al menos un período")
            st.stop()
        
        # Contratos con datos
        df_contratos_mensual = run_query_in("vw_general_semanal", "periodo", periodos_seleccionados, select="id_contrato")
        ids_contratos_mensual = df_contratos_mensual['id_contrato'].drop_duplicates().tolist()
        contratos_mensual = run_query("contratos", select="id, nombre", filters={"activo": 1})
        contratos_mensual = contratos_mensual[contratos_mensual['id'].isin(ids_contratos_mensual)]
        
        if contratos_mensual.empty:
            st.warning("⚠️ No hay contratos con datos CIERRE en los períodos seleccionados")
            st.stop()
        
        with col_m2:
            contrato_nombre = st.selectbox("📋 Contrato", contratos_mensual['nombre'].tolist(), key="evo_mensual_contrato")
            id_contrato = contratos_mensual[contratos_mensual['nombre'] == contrato_nombre]['id'].iloc[0]
        
        clientes_mensual = run_query("clientes", select="id, nombre, codigo", filters={"id_contrato": id_contrato, "activo": 1})
        
        with col_m3:
            cliente_opciones = {"TODOS": None}
            for _, row in clientes_mensual.iterrows():
                cliente_opciones[f"{row['nombre']} ({row['codigo']})"] = row['id']
            cliente_seleccionado = st.selectbox("👤 Cliente", list(cliente_opciones.keys()), key="evo_mensual_cliente")
            id_cliente = cliente_opciones[cliente_seleccionado]
        
        st.markdown("---")
        
        df_mensual = run_query_in("vw_general_semanal", "periodo", periodos_seleccionados)
        df_mensual = df_mensual[df_mensual['id_contrato'] == id_contrato]
        df_mensual = df_mensual[df_mensual['tipo'] == 'CPM']
        df_mensual = df_mensual[df_mensual['tipo_reporte'] == 'CIERRE']
        
        if id_cliente:
            df_mensual = df_mensual[df_mensual['id_cliente'] == id_cliente]
        
        if not df_mensual.empty:
            df_mensual_group = df_mensual.groupby('periodo').agg({
                'ingresos': 'sum',
                'costos': 'sum',
                'otros_costos': 'sum'
            }).reset_index()
            
            df_mensual_group['costos_totales'] = df_mensual_group['costos'] + df_mensual_group['otros_costos']
            df_mensual_group['margen'] = df_mensual_group['ingresos'] - df_mensual_group['costos_totales']
            df_mensual_group['margen_pct'] = (df_mensual_group['margen'] / df_mensual_group['ingresos'] * 100).fillna(0)
            df_mensual_group = df_mensual_group.sort_values('periodo')
            
            total_ingresos = df_mensual_group['ingresos'].sum()
            total_costos = df_mensual_group['costos_totales'].sum()
            total_margen = total_ingresos - total_costos
            margen_pct_total = (total_margen / total_ingresos * 100) if total_ingresos > 0 else 0
            
            col_t1, col_t2, col_t3, col_t4 = st.columns(4)
            with col_t1:
                with st.container(border=True):
                    st.markdown("<div style='text-align: center;'>💰 Ingresos Totales</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='text-align: center; font-size: 1.3rem; font-weight: 700;'>${total_ingresos:,.0f}</div>", unsafe_allow_html=True)
            with col_t2:
                with st.container(border=True):
                    st.markdown("<div style='text-align: center;'>💸 Costos Totales</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='text-align: center; font-size: 1.3rem; font-weight: 700;'>${total_costos:,.0f}</div>", unsafe_allow_html=True)
            with col_t3:
                with st.container(border=True):
                    st.markdown("<div style='text-align: center;'>📊 Margen Total</div>", unsafe_allow_html=True)
                    color = "#10b981" if total_margen > 0 else "#ef4444"
                    st.markdown(f"<div style='text-align: center; font-size: 1.3rem; font-weight: 700; color: {color};'>${total_margen:,.0f}</div>", unsafe_allow_html=True)
            with col_t4:
                with st.container(border=True):
                    st.markdown("<div style='text-align: center;'>🎯 Margen % Promedio</div>", unsafe_allow_html=True)
                    color_m = "#10b981" if margen_pct_total >= 42 else "#f59e0b" if margen_pct_total >= 30 else "#ef4444"
                    st.markdown(f"<div style='text-align: center; font-size: 1.3rem; font-weight: 700; color: {color_m};'>{margen_pct_total:.1f}%</div>", unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df_mensual_group['periodo'],
                y=df_mensual_group['margen_pct'],
                text=df_mensual_group['margen_pct'].round(1).astype(str) + '%',
                textposition='outside',
                marker_color=['#10b981' if m >= 42 else '#f59e0b' if m >= 30 else '#ef4444' for m in df_mensual_group['margen_pct']]
            ))
            fig.add_hline(y=42, line_dash="dash", line_color="#10b981", line_width=2,
                         annotation_text="🎯 Objetivo 42%", annotation_position="top right")
            fig.update_layout(title="Comparativa de Margen por Período", height=450)
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("#### 📋 Resumen por Período")
            df_tabla = df_mensual_group[['periodo', 'ingresos', 'costos_totales', 'margen', 'margen_pct']].copy()
            df_tabla.columns = ['Período', 'Ingresos', 'Costos', 'Margen', 'Margen %']
            df_tabla['Ingresos'] = df_tabla['Ingresos'].apply(lambda x: f"${x:,.0f}")
            df_tabla['Costos'] = df_tabla['Costos'].apply(lambda x: f"${x:,.0f}")
            df_tabla['Margen'] = df_tabla['Margen'].apply(lambda x: f"${x:,.0f}")
            df_tabla['Margen %'] = df_tabla['Margen %'].apply(lambda x: f"{x:.1f}%")
            df_tabla['Estado'] = df_tabla['Margen %'].apply(lambda x: "🟢 Excelente" if float(x.replace('%','')) >= 42 else "🟡 Aceptable" if float(x.replace('%','')) >= 30 else "🔴 Crítico")
            
            st.dataframe(df_tabla.style.applymap(color_margen_tabla, subset=['Margen %']), use_container_width=True, hide_index=True)
        else:
            st.info("No hay datos de CIERRE para los períodos seleccionados")

# ============================================================================
# TAB 4: ANÁLISIS POR METRO
# ============================================================================
with tab4:
    st.markdown("### 📉 Análisis: Costo por Metro vs Tarifa")
    st.caption("Comparativa del costo real de perforación vs la tarifa cobrada por metro")
    
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    
    with col_f1:
        contratos_analisis = run_query("contratos", select="id, nombre", filters={"activo": 1})
        if contratos_analisis.empty:
            st.warning("⚠️ No hay contratos activos")
            st.stop()
        
        contrato_analisis = st.selectbox("📋 Contrato", contratos_analisis['nombre'].tolist(), key="analisis_contrato")
        id_contrato_analisis = contratos_analisis[contratos_analisis['nombre'] == contrato_analisis]['id'].iloc[0]
    
    with col_f2:
        clientes_analisis = run_query("clientes", select="id, nombre, codigo", filters={"id_contrato": id_contrato_analisis, "activo": 1})
        cliente_opciones = {"TODOS": None}
        for _, row in clientes_analisis.iterrows():
            cliente_opciones[f"{row['nombre']} ({row['codigo']})"] = row['id']
        cliente_analisis = st.selectbox("👤 Cliente", list(cliente_opciones.keys()), key="analisis_cliente")
        id_cliente_analisis = cliente_opciones[cliente_analisis]
    
    with col_f3:
        periodos_analisis = run_query_in("perforacion_general", "id_contrato", [id_contrato_analisis], select="periodo")
        periodos_analisis = periodos_analisis['periodo'].drop_duplicates().sort_values(ascending=False).tolist()
        
        if not periodos_analisis:
            st.warning("⚠️ No hay períodos disponibles")
            st.stop()
        
        opciones_periodos = ["TODOS"] + periodos_analisis
        periodos_seleccionados_analisis = st.multiselect("📅 Período(s)", options=opciones_periodos,
            default=[periodos_analisis[0]] if periodos_analisis else ["TODOS"],
            key="analisis_periodos")
        
        if "TODOS" in periodos_seleccionados_analisis:
            periodos_seleccionados_analisis = periodos_analisis
    
    with col_f4:
        if periodos_seleccionados_analisis:
            df_semanas_analisis = run_query_in("perforacion_general", "periodo", periodos_seleccionados_analisis, select="semana, tipo_reporte")
            df_semanas_analisis = df_semanas_analisis[(df_semanas_analisis['tipo_reporte'] == 'AVANCE') & (df_semanas_analisis['semana'] > 0)]
            semanas_avance_analisis = df_semanas_analisis['semana'].drop_duplicates().sort_values().tolist()
            
            df_cierre_analisis = run_query_in("perforacion_general", "periodo", periodos_seleccionados_analisis, select="periodo")
            df_cierre_analisis = df_cierre_analisis[df_cierre_analisis['tipo_reporte'] == 'CIERRE']
            tiene_cierre_analisis = len(df_cierre_analisis) > 0
        else:
            semanas_avance_analisis = []
            tiene_cierre_analisis = False
        
        opciones_semanas_analisis = []
        if tiene_cierre_analisis:
            opciones_semanas_analisis.append("CIERRE")
        opciones_semanas_analisis.extend([str(s) for s in semanas_avance_analisis])
        
        if not opciones_semanas_analisis:
            opciones_semanas_analisis = ["NO HAY DATOS"]
        
        semana_analisis = st.selectbox("📊 Semana", options=opciones_semanas_analisis, index=0, key="analisis_semana")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if semana_analisis == "NO HAY DATOS" or not periodos_seleccionados_analisis:
        st.warning("⚠️ No hay datos disponibles para los filtros seleccionados")
        st.stop()
    
    # Obtener metros perforados
    usar_cierre_analisis = (semana_analisis == "CIERRE")
    semana_valor_analisis = None if usar_cierre_analisis else int(semana_analisis)
    
    df_perforacion = run_query_in("perforacion_general", "periodo", periodos_seleccionados_analisis)
    df_perforacion = df_perforacion[df_perforacion['id_contrato'] == id_contrato_analisis]
    df_perforacion = df_perforacion[df_perforacion['tipo_operacion'] == 'CPM']
    
    if id_cliente_analisis:
        df_perforacion = df_perforacion[df_perforacion['id_cliente'] == id_cliente_analisis]
    
    if usar_cierre_analisis:
        df_perforacion = df_perforacion[df_perforacion['tipo_reporte'] == 'CIERRE']
    elif semana_valor_analisis:
        df_perforacion = df_perforacion[(df_perforacion['tipo_reporte'] == 'AVANCE') & (df_perforacion['semana'] == semana_valor_analisis)]
    
    # Obtener detalles de metros
    if not df_perforacion.empty:
        df_metros_analisis = run_query_in("perforacion_detalle", "id_perforacion_general", df_perforacion['id'].tolist())
        
        df_metros = df_metros_analisis.groupby('id_perforacion_general').agg({'total_mp': 'sum'}).reset_index()
        df_metros = df_metros.merge(df_perforacion[['id', 'id_tipo_perforacion']], left_on='id_perforacion_general', right_on='id', how='left')
        
        metros_por_tipo = df_metros.groupby('id_tipo_perforacion')['total_mp'].sum().to_dict()
    else:
        metros_por_tipo = {}
    
    # Obtener costos CPM
    df_costos_analisis = run_query_in("vw_general_semanal", "periodo", periodos_seleccionados_analisis)
    df_costos_analisis = df_costos_analisis[df_costos_analisis['id_contrato'] == id_contrato_analisis]
    df_costos_analisis = df_costos_analisis[df_costos_analisis['tipo'] == 'CPM']
    
    if id_cliente_analisis:
        df_costos_analisis = df_costos_analisis[df_costos_analisis['id_cliente'] == id_cliente_analisis]
    
    if usar_cierre_analisis:
        df_costos_analisis = df_costos_analisis[df_costos_analisis['tipo_reporte'] == 'CIERRE']
    elif semana_valor_analisis:
        df_costos_analisis = df_costos_analisis[(df_costos_analisis['tipo_reporte'] == 'AVANCE') & (df_costos_analisis['semana'] == semana_valor_analisis)]
    
    costos_por_tipo = df_costos_analisis.groupby('id_tipo_perforacion')['costos'].sum().to_dict()
    
    # Obtener tarifas
    df_tarifas_analisis = run_query("tarifas", select="id_tipo_perforacion, tarifa")
    df_tarifas_analisis = df_tarifas_analisis[df_tarifas_analisis['id_contrato'] == id_contrato_analisis]
    if id_cliente_analisis:
        df_tarifas_analisis = df_tarifas_analisis[df_tarifas_analisis['id_cliente'] == id_cliente_analisis]
    
    tarifas_por_tipo = df_tarifas_analisis.groupby('id_tipo_perforacion')['tarifa'].first().to_dict()
    
    # Obtener nombres de tipos
    df_tipos_nombres = run_query("tipo_perforacion", select="id, nombre")
    tipo_nombre_dict = dict(zip(df_tipos_nombres['id'], df_tipos_nombres['nombre']))
    
    # Combinar datos
    todos_los_tipos = set(metros_por_tipo.keys()) | set(costos_por_tipo.keys()) | set(tarifas_por_tipo.keys())
    
    datos_analisis = []
    for id_tipo in todos_los_tipos:
        tipo_nombre = tipo_nombre_dict.get(id_tipo, "SIN TIPO")
        metros = metros_por_tipo.get(id_tipo, 0)
        costo_total = costos_por_tipo.get(id_tipo, 0)
        tarifa = tarifas_por_tipo.get(id_tipo, 0)
        
        costo_por_metro = costo_total / metros if metros > 0 else 0
        diferencia = tarifa - costo_por_metro
        margen = (diferencia / tarifa * 100) if tarifa > 0 else 0
        
        if tarifa == 0:
            estado = "⚪ Sin tarifa"
        elif margen >= 30:
            estado = "🟢 Excelente"
        elif margen >= 15:
            estado = "🟡 Aceptable"
        elif margen >= 0:
            estado = "🟠 Justo"
        else:
            estado = "🔴 Pérdida"
        
        datos_analisis.append({
            'Tipo Perforación': tipo_nombre,
            'Metros (m)': metros,
            'Costo Total': costo_total,
            'Costo por Metro': costo_por_metro,
            'Tarifa por Metro': tarifa,
            'Diferencia': diferencia,
            'Margen %': margen,
            'Estado': estado
        })
    
    if datos_analisis:
        df_analisis = pd.DataFrame(datos_analisis)
        df_analisis = df_analisis[df_analisis['Metros (m)'] > 0]
        
        if df_analisis.empty:
            st.info("No hay tipos de perforación con metros registrados")
        else:
            # Resumen general
            total_metros = df_analisis['Metros (m)'].sum()
            total_costo = df_analisis['Costo Total'].sum()
            costo_promedio_metro = total_costo / total_metros if total_metros > 0 else 0
            tarifa_promedio = sum(df_analisis['Tarifa por Metro'] * df_analisis['Metros (m)']) / total_metros if total_metros > 0 else 0
            diferencia_promedio = tarifa_promedio - costo_promedio_metro
            margen_promedio = (diferencia_promedio / tarifa_promedio * 100) if tarifa_promedio > 0 else 0
            
            col_r1, col_r2, col_r3, col_r4, col_r5 = st.columns(5)
            
            with col_r1:
                with st.container(border=True):
                    st.markdown("<div style='text-align: center;'>📏 Total Metros</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='text-align: center; font-size: 1.3rem; font-weight: 700;'>{total_metros:,.0f} m</div>", unsafe_allow_html=True)
            with col_r2:
                with st.container(border=True):
                    st.markdown("<div style='text-align: center;'>💰 Costo Promedio/m</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='text-align: center; font-size: 1.3rem; font-weight: 700;'>${costo_promedio_metro:.2f}</div>", unsafe_allow_html=True)
            with col_r3:
                with st.container(border=True):
                    st.markdown("<div style='text-align: center;'>💵 Tarifa Promedio/m</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='text-align: center; font-size: 1.3rem; font-weight: 700;'>${tarifa_promedio:.2f}</div>", unsafe_allow_html=True)
            with col_r4:
                with st.container(border=True):
                    st.markdown("<div style='text-align: center;'>📊 Diferencia Promedio</div>", unsafe_allow_html=True)
                    color = "#10b981" if diferencia_promedio >= 0 else "#ef4444"
                    st.markdown(f"<div style='text-align: center; font-size: 1.3rem; font-weight: 700; color: {color};'>${diferencia_promedio:.2f}</div>", unsafe_allow_html=True)
            with col_r5:
                with st.container(border=True):
                    st.markdown("<div style='text-align: center;'>🎯 Margen Promedio</div>", unsafe_allow_html=True)
                    color = "#10b981" if margen_promedio >= 30 else "#f59e0b" if margen_promedio >= 15 else "#ef4444"
                    st.markdown(f"<div style='text-align: center; font-size: 1.3rem; font-weight: 700; color: {color};'>{margen_promedio:.1f}%</div>", unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Gráfico Costo vs Tarifa
            st.markdown("#### 📊 Comparativa: Costo vs Tarifa por Metro")
            df_grafico = df_analisis[df_analisis['Metros (m)'] > 0].copy()
            
            if not df_grafico.empty:
                fig = go.Figure()
                fig.add_trace(go.Bar(x=df_grafico['Tipo Perforación'], y=df_grafico['Costo por Metro'], name='Costo por Metro', marker_color='#ef4444', text=df_grafico['Costo por Metro'].round(2).astype(str), textposition='outside'))
                fig.add_trace(go.Bar(x=df_grafico['Tipo Perforación'], y=df_grafico['Tarifa por Metro'], name='Tarifa por Metro', marker_color='#10b981', text=df_grafico['Tarifa por Metro'].round(2).astype(str), textposition='outside'))
                fig.update_layout(title="Costo por Metro vs Tarifa por Metro", height=450, barmode='group')
                st.plotly_chart(fig, use_container_width=True)
            
            # Gráfico Margen
            st.markdown("#### 📈 Margen por Tipo de Perforación")
            df_margen = df_analisis[(df_analisis['Tarifa por Metro'] > 0) & (df_analisis['Metros (m)'] > 0)].copy()
            
            if not df_margen.empty:
                colores_margen = ['#10b981' if m >= 30 else '#f59e0b' if m >= 15 else '#f97316' if m >= 0 else '#ef4444' for m in df_margen['Margen %']]
                fig2 = go.Figure()
                fig2.add_trace(go.Bar(x=df_margen['Tipo Perforación'], y=df_margen['Margen %'], marker_color=colores_margen, text=df_margen['Margen %'].round(1).astype(str) + '%', textposition='outside'))
                fig2.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Excelente (30%)")
                fig2.add_hline(y=15, line_dash="dash", line_color="orange", annotation_text="Aceptable (15%)")
                fig2.update_layout(title="Margen por Tipo de Perforación", height=400)
                st.plotly_chart(fig2, use_container_width=True)
            
            # Tabla detallada
            st.markdown("#### 📋 Detalle por Tipo de Perforación")
            df_tabla = df_analisis.copy()
            df_tabla['Costo Total'] = df_tabla['Costo Total'].apply(lambda x: f"${x:,.0f}")
            df_tabla['Costo por Metro'] = df_tabla['Costo por Metro'].apply(lambda x: f"${x:.2f}")
            df_tabla['Tarifa por Metro'] = df_tabla['Tarifa por Metro'].apply(lambda x: f"${x:.2f}" if x > 0 else "-")
            df_tabla['Diferencia'] = df_tabla['Diferencia'].apply(lambda x: f"${x:.2f}")
            df_tabla['Margen %'] = df_tabla['Margen %'].apply(lambda x: f"{x:.1f}%" if x != 0 else "-")
            
            st.dataframe(df_tabla, use_container_width=True, hide_index=True)
            
            # Alertas
            perdidas = df_analisis[(df_analisis['Margen %'] < 0) & (df_analisis['Tarifa por Metro'] > 0)]
            if not perdidas.empty:
                st.warning(f"⚠️ **Tipos de perforación con pérdida:** {', '.join(perdidas['Tipo Perforación'].tolist())}")
            
            sin_tarifa = df_analisis[(df_analisis['Tarifa por Metro'] == 0) & (df_analisis['Metros (m)'] > 0)]
            if not sin_tarifa.empty:
                st.info(f"ℹ️ **Tipos con metros pero sin tarifa definida:** {', '.join(sin_tarifa['Tipo Perforación'].tolist())}")
    else:
        st.info("No hay datos de perforación para los filtros seleccionados")