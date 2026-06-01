import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from database.conexion import run_query, get_supabase

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
    /* Contenedor de la tabla */
    .stDataFrame {
        
        margin: 0 auto !important;
        border-radius: 16px !important;
        overflow: hidden !important;
        border: 1px solid #E5E7EB !important;
    }
    
    /* Encabezados de tabla */
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
    
    /* Celdas del cuerpo */
    .stDataFrame tbody td,
    div[data-testid="stDataFrame"] tbody tr td {
        text-align: center !important;
        font-size: 0.85rem !important;
        padding: 10px 8px !important;
        border-bottom: 1px solid #E5E7EB !important;
    }
    
    /* Primera columna alineada a la izquierda */
    .stDataFrame tbody td:first-child,
    div[data-testid="stDataFrame"] tbody tr td:first-child {
        text-align: left !important;
        font-weight: 500 !important;
    }
    
    /* Filas pares (zebra) */
    .stDataFrame tbody tr:nth-child(even) td,
    div[data-testid="stDataFrame"] tbody tr:nth-child(even) td {
        background-color: #F8FAFC !important;
    }
    
    /* Filas impares */
    .stDataFrame tbody tr:nth-child(odd) td,
    div[data-testid="stDataFrame"] tbody tr:nth-child(odd) td {
        background-color: #FFFFFF !important;
    }
    
    /* Hover en filas */
    .stDataFrame tbody tr:hover td,
    div[data-testid="stDataFrame"] tbody tr:hover td {
        background-color: #E8EDF2 !important;
    }
    
    /* Dataframe general */
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

# Al inicio del archivo, después de imports y configuración
def estilo_margen(valor):
    """Aplica estilo rojo a márgenes negativos"""
    if isinstance(valor, str) and '-' in valor:
        return 'color: #ef4444; font-weight: bold;'
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

# PESTAÑAS PRINCIPALES
# ============================================================================

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 RESUMEN GLOBAL", 
    "📋 DETALLE POR CONTRATO", 
    "📊 EVOLUCIÓN SEMANAL",
    "📉 ANÁLISIS POR METRO"
])

# ============================================================================
with tab1:
    st.markdown("### 📊 Resumen Global")
    
    # ===== OBTENER PERIODOS DISPONIBLES =====
    df_periodos1 = run_query("vw_general_semanal", select="periodo")
    df_periodos2 = run_query("vw_cpm_resultado", select="periodo")
    df_periodos3 = run_query("vw_venta", select="periodo")
    
    periodos_set = set()
    if not df_periodos1.empty:
        periodos_set.update(df_periodos1['periodo'].tolist())
    if not df_periodos2.empty:
        periodos_set.update(df_periodos2['periodo'].tolist())
    if not df_periodos3.empty:
        periodos_set.update(df_periodos3['periodo'].tolist())
    
    periodos_disponibles = sorted(list(periodos_set), reverse=True)
    
    # ===== FILTROS: TÍTULO + PERÍODO + SEMANA =====
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
            periodos_seleccionados = periodos_disponibles
        periodos_originales = periodos_seleccionados.copy()        
    
    with col_semana:
        # Construir opciones de semana según períodos seleccionados
        if periodos_seleccionados:
            # Obtener semanas AVANCE disponibles
            df_semanas = run_query("vw_general_semanal", 
                                   select="semana",
                                   filters={"periodo": periodos_seleccionados, "tipo_reporte": "AVANCE"})
            if not df_semanas.empty:
                semanas_avance = df_semanas[df_semanas['semana'] > 0]['semana'].unique().tolist()
                semanas_avance.sort()
            else:
                semanas_avance = []
            
            # Verificar si existen períodos con CIERRE
            df_cierre = run_query("vw_general_semanal", 
                                 select="periodo",
                                 filters={"periodo": periodos_seleccionados, "tipo_reporte": "CIERRE"})
            periodos_con_cierre = df_cierre['periodo'].unique().tolist() if not df_cierre.empty else []
            tiene_cierre = len(periodos_con_cierre) > 0
        else:
            semanas_avance = []
            tiene_cierre = False
            periodos_con_cierre = []
        
        # Construir opciones del selectbox
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
        
        # Validar selección
        if semana_seleccionada == "NO HAY DATOS":
            st.warning("⚠️ No hay datos de semanas disponibles para los períodos seleccionados")
            st.stop()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ===== CONSTRUIR FILTROS =====
    if not periodos_seleccionados:
        st.warning("⚠️ No hay períodos seleccionados")
        st.stop()
    
    # Construir filtro de semana según selección
    if semana_seleccionada == "CIERRE":
        # Filtrar solo períodos que tienen CIERRE
        if periodos_con_cierre:
            periodos_seleccionados = [p for p in periodos_seleccionados if p in periodos_con_cierre]
            if len(periodos_seleccionados) < len(periodos_originales):
                st.info(f"📌 Mostrando solo períodos con CIERRE: {', '.join(periodos_seleccionados)}")
        else:
            st.error("❌ Ninguno de los períodos seleccionados tiene datos de CIERRE")
            st.stop()
        
        filtro_tipo_reporte = "CIERRE"
        filtro_semana_valor = None
    else:
        semana_valor = int(semana_seleccionada)
        # Verificar qué períodos tienen esta semana AVANCE
        df_periodos_con_semana = run_query("vw_general_semanal",
                                           select="periodo",
                                           filters={"periodo": periodos_seleccionados, 
                                                   "tipo_reporte": "AVANCE",
                                                   "semana": semana_valor})
        
        periodos_con_semana = df_periodos_con_semana['periodo'].unique().tolist() if not df_periodos_con_semana.empty else []
        
        if periodos_con_semana:
            periodos_seleccionados = [p for p in periodos_seleccionados if p in periodos_con_semana]
            if len(periodos_seleccionados) < len(periodos_originales):
                st.info(f"📌 Mostrando solo períodos con datos de semana {semana_valor}: {', '.join(periodos_seleccionados)}")
        else:
            st.error(f"❌ Ninguno de los períodos seleccionados tiene datos de semana {semana_valor}")
            st.stop()
        
        filtro_tipo_reporte = "AVANCE"
        filtro_semana_valor = semana_valor
    
    # ===== 1. TOTAL GENERAL (KPI PRINCIPALES) =====
    # Construir filtros base
    filtros_base = {"periodo": periodos_seleccionados, "tipo_reporte": filtro_tipo_reporte}
    if filtro_semana_valor is not None:
        filtros_base["semana"] = filtro_semana_valor
    
    # Ingresos totales
    df_ingresos = run_query("vw_general_semanal", 
                           select="ingresos",
                           filters={**filtros_base, "tipo": ["CPM", "VENTA"]})
    ingresos_totales = df_ingresos['ingresos'].sum() if not df_ingresos.empty else 0
    
    # Costos totales
    df_costos_cpm_venta = run_query("vw_general_semanal",
                                   select="costos",
                                   filters={**filtros_base, "tipo": ["CPM", "VENTA"]})
    df_costos_afiladoras = run_query("vw_general_semanal",
                                    select="otros_costos",
                                    filters={**filtros_base, "tipo": "AFILADORAS"})
    
    costos_cpm_venta = df_costos_cpm_venta['costos'].sum() if not df_costos_cpm_venta.empty else 0
    costos_afiladoras = df_costos_afiladoras['otros_costos'].sum() if not df_costos_afiladoras.empty else 0
    costos_totales = costos_cpm_venta + costos_afiladoras
    
    margen_total = ingresos_totales - costos_totales
    margen_pct = (1 - costos_totales/ingresos_totales) * 100 if ingresos_totales > 0 else 0
    
    # KPIs
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
    
    # ===== 2. TARJETAS POR TIPO DE OPERACIÓN =====
    st.markdown("### ⛏️ Por Tipo de Operación")
    
    # Obtener datos por tipo de operación
    df_general = run_query("vw_general_semanal",
                          select="id_contrato, tipo, ingresos, costos, otros_costos",
                          filters={**filtros_base})
    
    if filtro_semana_valor is not None:
        df_general = df_general[df_general['semana'] == filtro_semana_valor]
    
    # Obtener tipos de operación de contratos
    df_contratos_tipos = run_query("contratos", select="id, tipo_operacion")
    contratos_dict = dict(zip(df_contratos_tipos['id'], df_contratos_tipos['tipo_operacion']))
    
    # Agrupar por tipo de operación
    tipos_datos = {}
    for _, row in df_general.iterrows():
        tipo_op = contratos_dict.get(row['id_contrato'], 'SIN TIPO')
        if tipo_op not in tipos_datos:
            tipos_datos[tipo_op] = {'ingresos': 0, 'costos': 0}
        
        if row['tipo'] in ['CPM', 'VENTA']:
            tipos_datos[tipo_op]['ingresos'] += row['ingresos']
            tipos_datos[tipo_op]['costos'] += row['costos']
        elif row['tipo'] == 'AFILADORAS':
            tipos_datos[tipo_op]['costos'] += row['otros_costos']
    
    if tipos_datos:
        tipo_cols = st.columns(2)
        
        for idx, tipo in enumerate(['SUPERFICIAL', 'SUBTERRANEA']):
            if tipo in tipos_datos:
                ingresos = tipos_datos[tipo]['ingresos']
                costos = tipos_datos[tipo]['costos']
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
                            color = "#10b981" if utilidad > 0 else "#ef4444"
                            st.markdown(f"<div style='text-align: center; font-size: 1.2rem; font-weight: 700; color: {color};'>${utilidad:,.0f}</div>", unsafe_allow_html=True)
                        with col_u2:
                            st.markdown("<div style='text-align: center;'>🎯 Margen %</div>", unsafe_allow_html=True)
                            st.markdown(f"<div style='text-align: center; font-size: 1.2rem; font-weight: 700;'>{margen:.1f}%</div>", unsafe_allow_html=True)
            else:
                with tipo_cols[idx]:
                    with st.container(border=True):
                        st.markdown(f"<h3 style='text-align: center; color: #1152d4;'>{tipo}</h3>", unsafe_allow_html=True)
                        st.markdown("<div style='text-align: center; color: #64748b;'>Sin datos para este tipo</div>", unsafe_allow_html=True)
    else:
        st.info("No hay datos por tipo de operación para los filtros seleccionados")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ===== 3. GRÁFICO DE MÁRGENES POR CONTRATO =====
    st.markdown("### 📊 Margen por Contrato vs Objetivo 42%")
    
    contratos = run_query("contratos", select="id, nombre", filters={"activo": 1})
    
    datos_grafico = []
    for _, contrato in contratos.iterrows():
        df_cont = run_query("vw_general_semanal",
                           select="tipo,ingresos, costos, otros_costos",
                           filters={**filtros_base, "id_contrato": contrato['id'], "tipo": ["CPM", "VENTA", "AFILADORAS"]})
        
        if filtro_semana_valor is not None:
            df_cont = df_cont[df_cont['semana'] == filtro_semana_valor]
        
        if not df_cont.empty:
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
        
        # Colores sobrios y profesionales
        colores = []
        for m in df_grafico['Margen %']:
            if m >= 42:
                colores.append('#2C5F8A')  # Azul sobrio (excelente)
            elif m >= 30:
                colores.append('#F59E0B')  # Ámbar (aceptable)
            else:
                colores.append('#9CA3AF')  # Gris (crítico)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df_grafico['Margen %'],
            y=df_grafico['Contrato'],
            orientation='h',
            marker_color=colores,
            text=df_grafico['Margen %'].round(1).astype(str) + '%',
            textposition='outside',
            textfont=dict(
                size=11,
                color='#1A2A3A',
                weight='bold'
            ),
            hovertemplate='<b>%{y}</b><br>Margen: %{x:.1f}%<extra></extra>'
        ))
        fig.add_vline(
            x=42, 
            line_dash="dash", 
            line_color="#2C5F8A", 
            line_width=2,
            annotation_text="🎯 Objetivo 42%",
            annotation_position="top"
        )
        fig.update_layout(
            height=500, 
            margin=dict(l=0, r=80, t=40, b=0),
            xaxis_title="Margen (%)",
            xaxis=dict(
                gridcolor='#E5E7EB',
                gridwidth=1,
                range=[0, max(df_grafico['Margen %'].max() + 10, 50)]
            ),
            yaxis=dict(
                gridcolor='#E5E7EB',
                gridwidth=1
            ),
            plot_bgcolor='white',
            font=dict(family='Inter, sans-serif')
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay datos para mostrar")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("### 📋 Detalle por Contrato")
    
    datos_contratos_lista = []
    
    for _, contrato in contratos.iterrows():
        df_detalle = run_query("vw_general_semanal",
                              select="tipo,ingresos, costos, otros_costos",
                              filters={**filtros_base, "id_contrato": contrato['id'], "tipo": ["CPM", "VENTA", "AFILADORAS"]})
        
        if filtro_semana_valor is not None:
            df_detalle = df_detalle[df_detalle['semana'] == filtro_semana_valor]
        
        if not df_detalle.empty:
            ingresos = df_detalle[df_detalle['tipo'].isin(['CPM', 'VENTA'])]['ingresos'].sum()
            costos = df_detalle[df_detalle['tipo'].isin(['CPM', 'VENTA'])]['costos'].sum() + df_detalle['otros_costos'].sum()
            
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
        
        # Ordenar por margen de mayor a menor
        df_contratos_lista = df_contratos_lista.sort_values('Margen', ascending=False)
        
        df_display = df_contratos_lista.copy()
        df_display['Ingresos'] = df_display['Ingresos'].apply(lambda x: f"${x:,.0f}")
        df_display['Costos'] = df_display['Costos'].apply(lambda x: f"${x:,.0f}")
        df_display['Utilidad'] = df_display['Utilidad'].apply(lambda x: f"${x:,.0f}")
        df_display['Margen'] = df_display['Margen'].apply(lambda x: f"{x:.1f}%")
        
        # Función para determinar estado y color del margen
        def get_estado_y_color(margen_str):
            valor = float(margen_str.replace('%', ''))
            if valor >= 42:
                return ("Excelente", "#10B981")
            elif valor >= 30:
                return ("Aceptable", "#F59E0B")
            else:
                return ("Crítico", "#EF4444")
        
        # Aplicar estado y color
        df_display['Estado'] = df_display['Margen'].apply(lambda x: get_estado_y_color(x)[0])
        df_display['ColorMargen'] = df_display['Margen'].apply(lambda x: get_estado_y_color(x)[1])
        
        # Generar tabla HTML profesional (sin bordes redondeados, sin sombras intercaladas)
        html_table = """
        <style>
            .pro-table {
                width: 100%;
                max-width: 1200px;
                margin: 0 auto;
                border-collapse: collapse;
                font-family: 'Inter', -apple-system, sans-serif;
                border: 1px solid #D1D5DB;
            }
            .pro-table th {
                background: #1A2A3A;
                color: white;
                font-weight: 600;
                font-size: 0.8rem;
                text-transform: uppercase;
                letter-spacing: 0.8px;
                padding: 14px 12px;
                text-align: center;
                border-bottom: 1px solid #2C3E50;
            }
            .pro-table td {
                padding: 12px 12px;
                font-size: 0.85rem;
                text-align: center;
                border-bottom: 1px solid #E5E7EB;
                background-color: white;
            }
            .pro-table tr:hover td {
                background-color: #F5F7FA;
            }
            .pro-table td:first-child {
                text-align: left;
                font-weight: 500;
                color: #1A2A3A;
            }
            .margen-excelente {
                color: #10B981;
                font-weight: 600;
            }
            .margen-aceptable {
                color: #F59E0B;
                font-weight: 600;
            }
            .margen-critico {
                color: #EF4444;
                font-weight: 600;
            }
            .estado-excelente {
                color: #10B981;
                font-weight: 500;
            }
            .estado-aceptable {
                color: #F59E0B;
                font-weight: 500;
            }
            .estado-critico {
                color: #EF4444;
                font-weight: 500;
            }
        </style>
        <table class="pro-table">
            <thead>
                <tr>
                    <th style="width: 25%;">CONTRATO</th>
                    <th style="width: 15%;">INGRESOS</th>
                    <th style="width: 15%;">COSTOS</th>
                    <th style="width: 15%;">UTILIDAD</th>
                    <th style="width: 15%;">MARGEN %</th>
                    <th style="width: 15%;">ESTADO</th>
                </tr>
            </thead>
            <tbody>
        """
        
        for _, row in df_display.iterrows():
            if row['ColorMargen'] == "#10B981":
                clase_margen = "margen-excelente"
                clase_estado = "estado-excelente"
            elif row['ColorMargen'] == "#F59E0B":
                clase_margen = "margen-aceptable"
                clase_estado = "estado-aceptable"
            else:
                clase_margen = "margen-critico"
                clase_estado = "estado-critico"
            
            html_table += f"""
                <tr>
                    <td style="text-align: left;">{row['Contrato']}</td>
                    <td>{row['Ingresos']}</td>
                    <td>{row['Costos']}</td>
                    <td>{row['Utilidad']}</td>
                    <td class="{clase_margen}">{row['Margen']}</td>
                    <td class="{clase_estado}">{row['Estado']}</td>
                </tr>
            """
        
        html_table += """
            </tbody>
        </table>
        """
        
        st.html(html_table)
        
    else:
        st.info("No hay datos de contratos para los filtros seleccionados")

# [CONTINUARÉ CON LAS SIGUIENTES TABS EN EL SIGUIENTE MENSAJE - TAB2, TAB3, TAB4]

with tab2:
    st.markdown("### 📋 Detalle por Contrato")
    
    # ===== FILTROS COMPACTOS (4 columnas) =====
    periodos_disponibles = run_query("vw_general_semanal", select="periodo")
    periodos_disponibles = periodos_disponibles['periodo'].unique().tolist() if not periodos_disponibles.empty else []
    periodos_disponibles.sort(reverse=True)
    
    if not periodos_disponibles:
        st.warning("⚠️ No hay períodos con datos cargados")
        st.stop()
    
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    
    with col_f1:
        periodo_principal = st.selectbox(
            "📅 Período",
            periodos_disponibles,
            key="detalle_periodo_principal"
        )
    
    contratos_filtrados = run_query("contratos", select="id, nombre", filters={"activo": 1})
    # Filtrar contratos que tienen datos en el período seleccionado
    df_contratos_con_datos = run_query("vw_general_semanal", 
                                       select="id_contrato",
                                       filters={"periodo": periodo_principal})
    ids_con_datos = df_contratos_con_datos['id_contrato'].unique().tolist() if not df_contratos_con_datos.empty else []
    contratos_filtrados = contratos_filtrados[contratos_filtrados['id'].isin(ids_con_datos)] if ids_con_datos else pd.DataFrame()
    
    if contratos_filtrados.empty:
        st.warning(f"⚠️ No hay contratos con datos en el período {periodo_principal}")
        st.stop()
    
    with col_f2:
        contrato_nombre = st.selectbox(
            "📋 Contrato", 
            contratos_filtrados['nombre'].tolist(), 
            key="detalle_contrato"
        )
        id_contrato = contratos_filtrados[contratos_filtrados['nombre'] == contrato_nombre]['id'].iloc[0]
    
    clientes = run_query("clientes", select="id, nombre, codigo", 
                        filters={"id_contrato": id_contrato, "activo": 1})
    
    with col_f3:
        cliente_opciones = {"TODOS": None}
        for _, row in clientes.iterrows():
            cliente_opciones[f"{row['nombre']} ({row['codigo']})"] = row['id']
        cliente_seleccionado = st.selectbox("👤 Cliente", list(cliente_opciones.keys()), key="detalle_cliente")
        id_cliente = cliente_opciones[cliente_seleccionado]
    
    with col_f4:
        filtro_cliente_sql_condition = {"id_cliente": id_cliente} if id_cliente else {}
        
        # Obtener semanas AVANCE
        df_semanas = run_query("vw_general_semanal", 
                              select="semana",
                              filters={**{"id_contrato": id_contrato, "periodo": periodo_principal, 
                                         "tipo_reporte": "AVANCE"}, **filtro_cliente_sql_condition})
        if not df_semanas.empty:
            semanas_avance = df_semanas[df_semanas['semana'] > 0]['semana'].unique().tolist()
            semanas_avance.sort()
        else:
            semanas_avance = []
        
        # Verificar CIERRE
        df_cierre = run_query("vw_general_semanal",
                             select="periodo",
                             filters={**{"id_contrato": id_contrato, "periodo": periodo_principal, 
                                        "tipo_reporte": "CIERRE"}, **filtro_cliente_sql_condition})
        tiene_cierre = not df_cierre.empty
        
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
            key="detalle_semana_unica"
        )
        
        if semana_seleccionada == "NO HAY DATOS":
            st.warning("⚠️ No hay datos de semanas disponibles")
            st.stop()
    
    st.markdown("---")
    
    # ===== CONSTRUIR FILTROS =====
    filtros_detalle = {"id_contrato": id_contrato, "periodo": periodo_principal}
    if id_cliente:
        filtros_detalle["id_cliente"] = id_cliente
    
    if semana_seleccionada == "CIERRE":
        filtros_detalle["tipo_reporte"] = "CIERRE"
    else:
        semana_valor = int(semana_seleccionada)
        filtros_detalle["tipo_reporte"] = "AVANCE"
        filtros_detalle["semana"] = semana_valor
    
    # ===== FUNCIÓN PARA COLOR DE MARGEN =====
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
    
    # ===== FUNCIÓN PARA COLOR DE EFICIENCIA =====
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
    
    # ===== SUBPESTAÑAS =====
    sub_tab1, sub_tab2 = st.tabs(["📊 OPERACIONES", "📈 RENDIMIENTO"])
    
    # ========== SUBPESTAÑA 1: OPERACIONES ==========
    with sub_tab1:
        
        # ----- CPM -----
        st.markdown("#### 💰 CPM")
        
        df_cpm = run_query("vw_general_semanal",
                          select="periodo, semana, id_tipo_perforacion, ingresos, costos",
                          filters={**filtros_detalle, "tipo": "CPM"})
        
        # Obtener nombres de tipo perforacion
        df_tipos_perf = run_query("tipo_perforacion", select="id, nombre")
        tipos_perf_dict = dict(zip(df_tipos_perf['id'], df_tipos_perf['nombre']))
        
        if not df_cpm.empty:
            df_cpm['tipo_perforacion'] = df_cpm['id_tipo_perforacion'].map(tipos_perf_dict).fillna('SIN TIPO')
            df_cpm['utilidad'] = df_cpm['ingresos'] - df_cpm['costos']
            df_cpm['margen_pct'] = df_cpm.apply(lambda row: (row['utilidad'] / row['ingresos'] * 100) if row['ingresos'] > 0 else 0, axis=1)
            
            total_ingresos_cpm = df_cpm['ingresos'].sum()
            total_costos_cpm = df_cpm['costos'].sum()
            total_margen_cpm = total_ingresos_cpm - total_costos_cpm
            margen_pct_cpm = (total_margen_cpm / total_ingresos_cpm * 100) if total_ingresos_cpm > 0 else 0
            
            col_c1, col_c2, col_c3 = st.columns(3)
            with col_c1:
                with st.container(border=True):
                    st.markdown("<div style='text-align: center; font-size: 0.75rem; color: #64748b;'>💰 Ingresos CPM</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='text-align: center; font-size: 1.5rem; font-weight: 700; color: #1152d4;'>${total_ingresos_cpm:,.0f}</div>", unsafe_allow_html=True)
            with col_c2:
                with st.container(border=True):
                    st.markdown("<div style='text-align: center; font-size: 0.75rem; color: #64748b;'>💸 Costos CPM</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='text-align: center; font-size: 1.5rem; font-weight: 700; color: #ef4444;'>${total_costos_cpm:,.0f}</div>", unsafe_allow_html=True)
            with col_c3:
                with st.container(border=True):
                    st.markdown("<div style='text-align: center; font-size: 0.75rem; color: #64748b;'>📊 Margen CPM</div>", unsafe_allow_html=True)
                    color = "#10b981" if total_margen_cpm > 0 else "#ef4444"
                    st.markdown(f"<div style='text-align: center; font-size: 1.5rem; font-weight: 700; color: {color};'>${total_margen_cpm:,.0f}</div>", unsafe_allow_html=True)
                    st.caption(f"{margen_pct_cpm:.1f}% del ingreso")
            
            df_cpm_display = df_cpm[['periodo', 'semana', 'tipo_perforacion', 'ingresos', 'costos', 'utilidad', 'margen_pct']].copy()
            df_cpm_display['ingresos'] = df_cpm_display['ingresos'].apply(lambda x: f"${x:,.0f}")
            df_cpm_display['costos'] = df_cpm_display['costos'].apply(lambda x: f"${x:,.0f}")
            df_cpm_display['utilidad'] = df_cpm_display['utilidad'].apply(lambda x: f"${x:,.0f}")
            df_cpm_display['margen_pct'] = df_cpm_display['margen_pct'].apply(lambda x: f"{x:.1f}%")
            
            df_cpm_display = df_cpm_display.rename(columns={
                'periodo': 'Período',
                'semana': 'Semana',
                'tipo_perforacion': 'Tipo Perforación',
                'ingresos': 'Ingresos',
                'costos': 'Costos',
                'utilidad': 'Utilidad',
                'margen_pct': 'Margen %'
            })
            
            st.dataframe(
                df_cpm_display.style.map(color_margen, subset=['Margen %']).set_properties(**{
                    'text-align': 'center',
                    'padding': '8px'
                }).set_table_styles([
                    {'selector': 'th', 'props': [('text-align', 'center'), ('font-weight', 'bold'), ('background-color', '#f3f4f6'), ('padding', '8px')]},
                    {'selector': 'td', 'props': [('padding', '8px')]}
                ]),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No hay datos CPM para los filtros seleccionados")
        
        st.markdown("---")
        
        # ----- AFILADORAS -----
        st.markdown("#### 💸 Afiladoras")
        
        df_afil = run_query("vw_general_semanal",
                           select="periodo, semana, otros_costos",
                           filters={**filtros_detalle, "tipo": "AFILADORAS"})
        
        if not df_afil.empty:
            total_costo_afil = df_afil['otros_costos'].sum()
            
            col_a1, col_a2 = st.columns(2)
            with col_a1:
                with st.container(border=True):
                    st.markdown("<div style='text-align: center; font-size: 0.75rem; color: #64748b;'>🔧 Total Afiladoras</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='text-align: center; font-size: 1.5rem; font-weight: 700;'>${total_costo_afil:,.0f}</div>", unsafe_allow_html=True)
            with col_a2:
                with st.container(border=True):
                    st.markdown("<div style='text-align: center; font-size: 0.75rem; color: #64748b;'>📦 Registros</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='text-align: center; font-size: 1.5rem; font-weight: 700;'>{len(df_afil)}</div>", unsafe_allow_html=True)
            
            df_afil_display = df_afil[['periodo', 'semana', 'otros_costos']].copy()
            df_afil_display = df_afil_display.rename(columns={
                'periodo': 'Período',
                'semana': 'Semana',
                'otros_costos': 'Costo Total'
            })
            df_afil_display['Costo Total'] = df_afil_display['Costo Total'].apply(lambda x: f"${x:,.0f}")
            
            st.dataframe(
                df_afil_display.style.set_properties(**{
                    'text-align': 'center',
                    'padding': '8px'
                }).set_table_styles([
                    {'selector': 'th', 'props': [('text-align', 'center'), ('font-weight', 'bold'), ('background-color', '#f3f4f6'), ('padding', '8px')]},
                    {'selector': 'td', 'props': [('padding', '8px')]}
                ]),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No hay datos de Afiladoras para los filtros seleccionados")
        
        st.markdown("---")
        
        # ----- VENTA -----
        st.markdown("#### 📦 Venta")
        
        df_venta = run_query("vw_general_semanal",
                            select="periodo, semana, ingresos, costos",
                            filters={**filtros_detalle, "tipo": "VENTA"})
        
        if not df_venta.empty:
            df_venta['utilidad'] = df_venta['ingresos'] - df_venta['costos']
            df_venta['margen_pct'] = df_venta.apply(lambda row: (row['utilidad'] / row['ingresos'] * 100) if row['ingresos'] > 0 else 0, axis=1)
            
            total_ingresos_venta = df_venta['ingresos'].sum()
            total_costos_venta = df_venta['costos'].sum()
            total_margen_venta = total_ingresos_venta - total_costos_venta
            margen_pct_venta = (total_margen_venta / total_ingresos_venta * 100) if total_ingresos_venta > 0 else 0
            
            col_v1, col_v2, col_v3, col_v4 = st.columns(4)
            with col_v1:
                with st.container(border=True):
                    st.markdown("<div style='text-align: center; font-size: 0.7rem; color: #64748b;'>💰 Ingresos Venta</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='text-align: center; font-size: 1.2rem; font-weight: 700;'>${total_ingresos_venta:,.0f}</div>", unsafe_allow_html=True)
            with col_v2:
                with st.container(border=True):
                    st.markdown("<div style='text-align: center; font-size: 0.7rem; color: #64748b;'>💸 Costos Venta</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='text-align: center; font-size: 1.2rem; font-weight: 700;'>${total_costos_venta:,.0f}</div>", unsafe_allow_html=True)
            with col_v3:
                with st.container(border=True):
                    st.markdown("<div style='text-align: center; font-size: 0.7rem; color: #64748b;'>📊 Margen Venta</div>", unsafe_allow_html=True)
                    color = "#10b981" if total_margen_venta > 0 else "#ef4444"
                    st.markdown(f"<div style='text-align: center; font-size: 1.2rem; font-weight: 700; color: {color};'>${total_margen_venta:,.0f}</div>", unsafe_allow_html=True)
            with col_v4:
                with st.container(border=True):
                    st.markdown("<div style='text-align: center; font-size: 0.7rem; color: #64748b;'>🎯 Margen %</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='text-align: center; font-size: 1.2rem; font-weight: 700;'>{margen_pct_venta:.1f}%</div>", unsafe_allow_html=True)
            
            df_venta_display = df_venta[['periodo', 'semana', 'ingresos', 'costos', 'utilidad', 'margen_pct']].copy()
            df_venta_display['ingresos'] = df_venta_display['ingresos'].apply(lambda x: f"${x:,.0f}")
            df_venta_display['costos'] = df_venta_display['costos'].apply(lambda x: f"${x:,.0f}")
            df_venta_display['utilidad'] = df_venta_display['utilidad'].apply(lambda x: f"${x:,.0f}")
            df_venta_display['margen_pct'] = df_venta_display['margen_pct'].apply(lambda x: f"{x:.1f}%")
            
            df_venta_display = df_venta_display.rename(columns={
                'periodo': 'Período',
                'semana': 'Semana',
                'ingresos': 'Ingresos',
                'costos': 'Costos',
                'utilidad': 'Utilidad',
                'margen_pct': 'Margen %'
            })
            
            st.dataframe(
                df_venta_display.style.map(color_margen, subset=['Margen %']).set_properties(**{
                    'text-align': 'center',
                    'padding': '8px'
                }).set_table_styles([
                    {'selector': 'th', 'props': [('text-align', 'center'), ('font-weight', 'bold'), ('background-color', '#f3f4f6'), ('padding', '8px')]},
                    {'selector': 'td', 'props': [('padding', '8px')]}
                ]),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No hay datos de Venta para los filtros seleccionados")
        
        st.markdown("---")
        
        # ----- RESUMEN GENERAL -----
        st.markdown("## 📊 RESUMEN GENERAL DE CONTRATO")
        
        df_resumen = run_query("vw_general_semanal",
                              select="tipo, ingresos, costos, otros_costos",
                              filters=filtros_detalle)
        
        if not df_resumen.empty:
            total_ingresos = df_resumen[df_resumen['tipo'].isin(['CPM', 'VENTA'])]['ingresos'].sum()
            total_costos = df_resumen[df_resumen['tipo'].isin(['CPM', 'VENTA'])]['costos'].sum() + df_resumen['otros_costos'].sum()
            roi_total = total_ingresos - total_costos
            roi_pct = (roi_total / total_ingresos * 100) if total_ingresos > 0 else 0
            
            col_r1, col_r2, col_r3, col_r4 = st.columns(4)
            with col_r1:
                with st.container(border=True):
                    st.markdown("<div style='text-align: center; font-size: 0.75rem; color: #64748b;'>💰 Total Ingresos</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='text-align: center; font-size: 1.5rem; font-weight: 700; color: #1152d4;'>${total_ingresos:,.0f}</div>", unsafe_allow_html=True)
            with col_r2:
                with st.container(border=True):
                    st.markdown("<div style='text-align: center; font-size: 0.75rem; color: #64748b;'>💸 Total Costos</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='text-align: center; font-size: 1.5rem; font-weight: 700; color: #ef4444;'>${total_costos:,.0f}</div>", unsafe_allow_html=True)
            with col_r3:
                with st.container(border=True):
                    st.markdown("<div style='text-align: center; font-size: 0.75rem; color: #64748b;'>📊 Ganancia</div>", unsafe_allow_html=True)
                    color = "#10b981" if roi_total > 0 else "#ef4444"
                    st.markdown(f"<div style='text-align: center; font-size: 1.5rem; font-weight: 700; color: {color};'>${roi_total:,.0f}</div>", unsafe_allow_html=True)
            with col_r4:
                with st.container(border=True):
                    st.markdown("<div style='text-align: center; font-size: 0.75rem; color: #64748b;'>🎯 Margen %</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='text-align: center; font-size: 1.5rem; font-weight: 700;'>{roi_pct:.1f}%</div>", unsafe_allow_html=True)
                    st.progress(min(roi_pct/42, 1.0) if roi_pct > 0 else 0, text="Objetivo: 42%")
        else:
            st.info("No hay datos suficientes para el resumen general")
    
    # ========== SUBPESTAÑA 2: RENDIMIENTO ==========
    with sub_tab2:
        st.markdown("#### 📈 Rendimiento vs Objetivos")
        
        # Construir filtros para rendimiento
        filtros_rend = {"id_contrato": id_contrato, "periodo": periodo_principal}
        if id_cliente:
            filtros_rend["id_cliente"] = id_cliente
        
        if semana_seleccionada == "CIERRE":
            filtros_rend["tipo_reporte"] = "CIERRE"
        else:
            filtros_rend["tipo_reporte"] = "AVANCE"
            filtros_rend["semana"] = semana_valor
        
        # Obtener datos de rendimiento
        df_rend = run_query("vw_rendimiento_detalle",
                           select="tipo_perforacion, familia, periodo, semana, metros_aplicables, total_acero, rendimiento, objetivo",
                           filters={**filtros_rend, "metros_aplicables": ">0"})
        
        # Calcular eficiencia
        if not df_rend.empty:
            df_rend['metros'] = df_rend['metros_aplicables']
            df_rend['cantidad'] = df_rend['total_acero']
            df_rend['objetivo'] = df_rend['objetivo'].fillna(0)
            df_rend['eficiencia'] = df_rend.apply(lambda row: (row['rendimiento'] / row['objetivo'] * 100) if row['objetivo'] > 0 else 0, axis=1)
            
            tipos_perforacion = df_rend['tipo_perforacion'].unique()
            
            for tipo in tipos_perforacion:
                df_tipo = df_rend[df_rend['tipo_perforacion'] == tipo].copy()
                
                st.markdown(f"##### 🔨 {tipo}")
                
                df_tipo = df_tipo.rename(columns={
                    'familia': 'FAMILIA',
                    'periodo': 'PERIODO',
                    'semana': 'SEMANA',
                    'metros': 'METROS',
                    'cantidad': 'CANTIDAD',
                    'rendimiento': 'RENDIMIENTO',
                    'objetivo': 'OBJETIVO',
                    'eficiencia': 'EFICIENCIA'
                })
                
                df_tipo = df_tipo[[
                    'FAMILIA', 'PERIODO', 'SEMANA', 'METROS', 
                    'CANTIDAD', 'RENDIMIENTO', 'OBJETIVO', 'EFICIENCIA'
                ]]
                
                st.dataframe(
                    df_tipo.style.format({
                        'METROS': '{:,.0f}',
                        'CANTIDAD': '{:,.0f}',
                        'RENDIMIENTO': '{:.2f}',
                        'OBJETIVO': '{:.2f}',
                        'EFICIENCIA': '{:.1f}%'
                    }).map(color_eficiencia_val, subset=['EFICIENCIA']).set_properties(**{
                        'text-align': 'center',
                        'padding': '8px'
                    }).set_table_styles([
                        {'selector': 'th', 'props': [('text-align', 'center'), ('font-weight', 'bold'), ('background-color', '#f3f4f6'), ('padding', '8px')]},
                        {'selector': 'td', 'props': [('padding', '8px')]}
                    ]),
                    use_container_width=True,
                    hide_index=True
                )
                st.markdown("<br>", unsafe_allow_html=True)
        else:
            st.info("No hay datos de rendimiento para los filtros seleccionados")

with tab3:
    st.markdown("### 📈 Evolución de Márgenes")
    
    # ========== SUBPESTAÑA 1: SEMANA A SEMANA ==========
    sub_tab1, sub_tab2 = st.tabs(["📊 Semana a Semana", "📈 Mes a Mes"])
    
    with sub_tab1:
        st.markdown("#### Evolución Semanal (Acumulado por período)")
        
        # ===== FILTROS COMPACTOS (3 columnas) =====
        periodos_todos_evo = run_query("vw_general_semanal", select="periodo", filters={"tipo_reporte": "CIERRE"})
        periodos_todos_evo = periodos_todos_evo['periodo'].unique().tolist() if not periodos_todos_evo.empty else []
        periodos_todos_evo.sort(reverse=True)
        
        if not periodos_todos_evo:
            st.warning("⚠️ No hay períodos con datos de CIERRE")
            st.stop()
        
        col_f1, col_f2, col_f3 = st.columns(3)
        
        with col_f1:
            periodo_evo = st.selectbox(
                "📅 Período",
                periodos_todos_evo,
                key="evo_periodo_principal"
            )
        
        # Contratos con datos
        contratos_con_datos_evo = run_query("contratos", select="id, nombre", filters={"activo": 1})
        df_contratos_evo = run_query("vw_general_semanal", 
                                     select="id_contrato",
                                     filters={"periodo": periodo_evo, "tipo_reporte": "CIERRE"})
        ids_con_datos_evo = df_contratos_evo['id_contrato'].unique().tolist() if not df_contratos_evo.empty else []
        contratos_con_datos_evo = contratos_con_datos_evo[contratos_con_datos_evo['id'].isin(ids_con_datos_evo)] if ids_con_datos_evo else pd.DataFrame()
        
        if contratos_con_datos_evo.empty:
            with col_f2:
                st.warning(f"⚠️ No hay contratos con datos en {periodo_evo}")
            st.stop()
        
        with col_f2:
            contrato_nombre = st.selectbox(
                "📋 Contrato",
                contratos_con_datos_evo['nombre'].tolist(),
                key="evo_semanal_contrato"
            )
            id_contrato = contratos_con_datos_evo[contratos_con_datos_evo['nombre'] == contrato_nombre]['id'].iloc[0]
        
        # Clientes
        clientes_evo = run_query("clientes", select="id, nombre, codigo", 
                                filters={"id_contrato": id_contrato, "activo": 1})
        
        with col_f3:
            cliente_opciones = {"TODOS": None}
            for _, row in clientes_evo.iterrows():
                cliente_opciones[f"{row['nombre']} ({row['codigo']})"] = row['id']
            cliente_seleccionado = st.selectbox(
                "👤 Cliente",
                list(cliente_opciones.keys()),
                key="evo_semanal_cliente"
            )
            id_cliente = cliente_opciones[cliente_seleccionado]
        
        st.markdown("---")
        
        # ===== CONSTRUIR FILTROS =====
        filtros_evolucion = {"id_contrato": id_contrato, "periodo": periodo_evo, 
                            "tipo": "CPM", "tipo_reporte": "CIERRE"}
        if id_cliente:
            filtros_evolucion["id_cliente"] = id_cliente
        
        df_evolucion = run_query("vw_general_semanal",
                                select="semana, ingresos, costos, otros_costos",
                                filters=filtros_evolucion)
        
        if not df_evolucion.empty:
            # Calcular márgenes
            df_evolucion['costos_totales'] = df_evolucion['costos'] + df_evolucion['otros_costos']
            df_evolucion['margen'] = df_evolucion['ingresos'] - df_evolucion['costos_totales']
            df_evolucion['margen_pct'] = df_evolucion.apply(
                lambda row: (row['margen'] / row['ingresos'] * 100) if row['ingresos'] > 0 else 0,
                axis=1
            )
            
            # Tarjetas de totales del período
            total_ingresos = df_evolucion['ingresos'].sum()
            total_costos = df_evolucion['costos_totales'].sum()
            total_margen = total_ingresos - total_costos
            margen_pct_total = (total_margen / total_ingresos * 100) if total_ingresos > 0 else 0
            
            col_t1, col_t2, col_t3, col_t4 = st.columns(4)
            with col_t1:
                with st.container(border=True):
                    st.markdown("<div style='text-align: center; font-size: 0.75rem; color: #64748b;'>💰 Ingresos Totales</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='text-align: center; font-size: 1.3rem; font-weight: 700; color: #1152d4;'>${total_ingresos:,.0f}</div>", unsafe_allow_html=True)
            with col_t2:
                with st.container(border=True):
                    st.markdown("<div style='text-align: center; font-size: 0.75rem; color: #64748b;'>💸 Costos Totales</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='text-align: center; font-size: 1.3rem; font-weight: 700; color: #ef4444;'>${total_costos:,.0f}</div>", unsafe_allow_html=True)
            with col_t3:
                with st.container(border=True):
                    st.markdown("<div style='text-align: center; font-size: 0.75rem; color: #64748b;'>📊 Margen Total</div>", unsafe_allow_html=True)
                    color = "#10b981" if total_margen > 0 else "#ef4444"
                    st.markdown(f"<div style='text-align: center; font-size: 1.3rem; font-weight: 700; color: {color};'>${total_margen:,.0f}</div>", unsafe_allow_html=True)
            with col_t4:
                with st.container(border=True):
                    st.markdown("<div style='text-align: center; font-size: 0.75rem; color: #64748b;'>🎯 Margen %</div>", unsafe_allow_html=True)
                    color_margen = "#10b981" if margen_pct_total >= 42 else "#f59e0b" if margen_pct_total >= 30 else "#ef4444"
                    st.markdown(f"<div style='text-align: center; font-size: 1.3rem; font-weight: 700; color: {color_margen};'>{margen_pct_total:.1f}%</div>", unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Gráfico de evolución semanal
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_evolucion['semana'],
                y=df_evolucion['margen_pct'],
                mode='lines+markers',
                name='Margen %',
                line=dict(color='#1152d4', width=3),
                marker=dict(size=10, color='#1152d4', symbol='circle'),
                text=df_evolucion['margen_pct'].round(1).astype(str) + '%',
                textposition='top center',
                textfont=dict(size=10, color='#1A2A3A')
            ))
            fig.add_hline(y=42, line_dash="dash", line_color="#10b981", line_width=2, 
                         annotation_text="🎯 Objetivo 42%", annotation_position="top right")
            fig.update_layout(
                title=dict(text=f"Evolución del Margen - {periodo_evo}", font=dict(size=14, color='#1A2A3A')),
                xaxis_title=dict(text="Semana", font=dict(size=12, color='#64748b')),
                yaxis_title=dict(text="Margen %", font=dict(size=12, color='#64748b')),
                height=450,
                xaxis=dict(tickmode='linear', tick0=1, dtick=1, gridcolor='#E5E7EB'),
                yaxis=dict(gridcolor='#E5E7EB', range=[0, max(df_evolucion['margen_pct'].max() + 10, 50)]),
                plot_bgcolor='white',
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Tabla detallada
            st.markdown("#### 📋 Detalle Semanal")
            
            df_tabla = df_evolucion[['semana', 'ingresos', 'costos_totales', 'margen', 'margen_pct']]
            df_tabla.columns = ['Semana', 'Ingresos', 'Costos', 'Margen', 'Margen %']
            df_tabla['Ingresos'] = df_tabla['Ingresos'].apply(lambda x: f"${x:,.0f}")
            df_tabla['Costos'] = df_tabla['Costos'].apply(lambda x: f"${x:,.0f}")
            df_tabla['Margen'] = df_tabla['Margen'].apply(lambda x: f"${x:,.0f}")
            
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
            
            df_tabla['Margen %'] = df_tabla['Margen %'].apply(lambda x: f"{x:.1f}%")
            
            st.dataframe(
                df_tabla.style.map(color_margen_tabla, subset=['Margen %']).set_properties(**{
                    'text-align': 'center',
                    'padding': '8px'
                }).set_table_styles([
                    {'selector': 'th', 'props': [('text-align', 'center'), ('font-weight', 'bold'), ('background-color', '#F8FAFC'), ('color', '#1A2A3A'), ('padding', '8px')]},
                    {'selector': 'td', 'props': [('padding', '8px'), ('border-bottom', '1px solid #E5E7EB')]}
                ]),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info(f"No hay datos para {periodo_evo} con los filtros seleccionados")
    
    # ========== SUBPESTAÑA 2: MES A MES ==========
    with sub_tab2:
        st.markdown("#### Comparativa Mensual (CIERRE por período)")
        
        # ===== FILTROS COMPACTOS =====
        periodos_disponibles_mensual = run_query("vw_general_semanal", select="periodo", filters={"tipo_reporte": "CIERRE"})
        periodos_disponibles_mensual = periodos_disponibles_mensual['periodo'].unique().tolist() if not periodos_disponibles_mensual.empty else []
        periodos_disponibles_mensual.sort(reverse=True)
        
        
        
        if not periodos_disponibles_mensual:
            st.warning("⚠️ No hay períodos con datos de CIERRE")
            st.stop()
        
        col_m1, col_m2, col_m3 = st.columns(3)
        
        with col_m1:
            opciones_periodos = ["TODOS"] + periodos_disponibles_mensual
            periodos_seleccionados = st.multiselect(
                "📅 Período(s)",
                options=opciones_periodos,
                default=[periodos_disponibles_mensual[0]] if periodos_disponibles_mensual else ["TODOS"],
                key="evo_mensual_periodos"
            )
            
            if "TODOS" in periodos_seleccionados:
                periodos_seleccionados = periodos_disponibles_mensual
        
       
        
        if not periodos_seleccionados:
            st.warning("⚠️ Seleccione al menos un período")
            st.stop()
        
        # Contratos con datos
        df_contratos_mensual = run_query("vw_general_semanal", 
                                        select="id_contrato",
                                        filters={"periodo": periodos_seleccionados, "tipo_reporte": "CIERRE"})
        
        
        
        
        ids_con_datos_mensual = df_contratos_mensual['id_contrato'].unique().tolist() if not df_contratos_mensual.empty else []
        
        df_contratos_nombres = run_query("contratos", select="id, nombre", filters={"activo": 1})
        df_contratos_nombres = df_contratos_nombres[df_contratos_nombres['id'].isin(ids_con_datos_mensual)] if ids_con_datos_mensual else pd.DataFrame()
        
        
        
        if df_contratos_nombres.empty:
            st.warning(f"⚠️ No hay contratos con datos CIERRE en los períodos seleccionados")
            st.stop()
        
        with col_m2:
            contrato_nombre = st.selectbox(
                "📋 Contrato",
                df_contratos_nombres['nombre'].tolist(),
                key="evo_mensual_contrato"
            )
            id_contrato = df_contratos_nombres[df_contratos_nombres['nombre'] == contrato_nombre]['id'].iloc[0]
        
        # Clientes
        clientes_mensual = run_query("clientes", select="id, nombre, codigo", 
                                    filters={"id_contrato": id_contrato, "activo": 1})
        
        with col_m3:
            cliente_opciones = {"TODOS": None}
            for _, row in clientes_mensual.iterrows():
                cliente_opciones[f"{row['nombre']} ({row['codigo']})"] = row['id']
            cliente_seleccionado = st.selectbox(
                "👤 Cliente",
                list(cliente_opciones.keys()),
                key="evo_mensual_cliente"
            )
            id_cliente = cliente_opciones[cliente_seleccionado]
        
        st.markdown("---")
        
        # ===== OBTENER DATOS PARA CADA PERÍODO INDIVIDUALMENTE =====
        df_mensual_lista = []
        
        for periodo in periodos_seleccionados:
            filtros_temp = {
                "id_contrato": id_contrato,
                "periodo": periodo,
                "tipo": "CPM",
                "tipo_reporte": "CIERRE"
            }
            if id_cliente:
                filtros_temp["id_cliente"] = id_cliente
            
            df_temp = run_query("vw_general_semanal",
                               select="periodo, ingresos, costos, otros_costos",
                               filters=filtros_temp)
            
            if not df_temp.empty:
                df_mensual_lista.append(df_temp)
        
        st.write(f"🔍 DEBUG - períodos con datos: {len(df_mensual_lista)}")
        
        if df_mensual_lista:
            df_mensual = pd.concat(df_mensual_lista, ignore_index=True)
        else:
            df_mensual = pd.DataFrame()
        
        if not df_mensual.empty:
            # Calcular márgenes
            df_mensual_grouped = df_mensual.groupby('periodo').agg({
                'ingresos': 'sum',
                'costos': 'sum',
                'otros_costos': 'sum'
            }).reset_index()
            
            df_mensual_grouped['costos_totales'] = df_mensual_grouped['costos'] + df_mensual_grouped['otros_costos']
            df_mensual_grouped['margen'] = df_mensual_grouped['ingresos'] - df_mensual_grouped['costos_totales']
            df_mensual_grouped['margen_pct'] = df_mensual_grouped.apply(
                lambda row: (row['margen'] / row['ingresos'] * 100) if row['ingresos'] > 0 else 0,
                axis=1
            )
            
            # Tarjetas de totales
            total_ingresos = df_mensual_grouped['ingresos'].sum()
            total_costos = df_mensual_grouped['costos_totales'].sum()
            total_margen = total_ingresos - total_costos
            margen_pct_total = (total_margen / total_ingresos * 100) if total_ingresos > 0 else 0
            
            col_t1, col_t2, col_t3, col_t4 = st.columns(4)
            with col_t1:
                with st.container(border=True):
                    st.markdown("<div style='text-align: center; font-size: 0.75rem; color: #64748b;'>💰 Ingresos Totales</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='text-align: center; font-size: 1.3rem; font-weight: 700; color: #1152d4;'>${total_ingresos:,.0f}</div>", unsafe_allow_html=True)
            with col_t2:
                with st.container(border=True):
                    st.markdown("<div style='text-align: center; font-size: 0.75rem; color: #64748b;'>💸 Costos Totales</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='text-align: center; font-size: 1.3rem; font-weight: 700; color: #ef4444;'>${total_costos:,.0f}</div>", unsafe_allow_html=True)
            with col_t3:
                with st.container(border=True):
                    st.markdown("<div style='text-align: center; font-size: 0.75rem; color: #64748b;'>📊 Margen Total</div>", unsafe_allow_html=True)
                    color = "#10b981" if total_margen > 0 else "#ef4444"
                    st.markdown(f"<div style='text-align: center; font-size: 1.3rem; font-weight: 700; color: {color};'>${total_margen:,.0f}</div>", unsafe_allow_html=True)
            with col_t4:
                with st.container(border=True):
                    st.markdown("<div style='text-align: center; font-size: 0.75rem; color: #64748b;'>🎯 Margen % Promedio</div>", unsafe_allow_html=True)
                    color_margen = "#10b981" if margen_pct_total >= 42 else "#f59e0b" if margen_pct_total >= 30 else "#ef4444"
                    st.markdown(f"<div style='text-align: center; font-size: 1.3rem; font-weight: 700; color: {color_margen};'>{margen_pct_total:.1f}%</div>", unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Gráfico de barras comparativo
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df_mensual_grouped['periodo'],
                y=df_mensual_grouped['margen_pct'],
                text=df_mensual_grouped['margen_pct'].round(1).astype(str) + '%',
                textposition='outside',
                textfont=dict(size=11, color='#1A2A3A'),
                marker_color=['#10b981' if m >= 42 else '#f59e0b' if m >= 30 else '#ef4444' for m in df_mensual_grouped['margen_pct']],
                name='Margen %',
                hovertemplate='<b>%{x}</b><br>Margen: %{y:.1f}%<extra></extra>'
            ))
            fig.add_hline(y=42, line_dash="dash", line_color="#10b981", line_width=2,
                         annotation_text="🎯 Objetivo 42%", annotation_position="top right")
            fig.update_layout(
                title=dict(text="Comparativa de Margen por Período", font=dict(size=14, color='#1A2A3A')),
                xaxis_title=dict(text="Período", font=dict(size=12, color='#64748b')),
                yaxis_title=dict(text="Margen %", font=dict(size=12, color='#64748b')),
                height=450,
                xaxis=dict(gridcolor='#E5E7EB'),
                yaxis=dict(gridcolor='#E5E7EB', range=[0, max(df_mensual_grouped['margen_pct'].max() + 10, 50)]),
                plot_bgcolor='white',
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Tabla resumen
            st.markdown("#### 📋 Resumen por Período")
            
            df_tabla = df_mensual_grouped[['periodo', 'ingresos', 'costos_totales', 'margen', 'margen_pct']]
            df_tabla.columns = ['Período', 'Ingresos', 'Costos', 'Margen', 'Margen %']
            df_tabla['Ingresos'] = df_tabla['Ingresos'].apply(lambda x: f"${x:,.0f}")
            df_tabla['Costos'] = df_tabla['Costos'].apply(lambda x: f"${x:,.0f}")
            df_tabla['Margen'] = df_tabla['Margen'].apply(lambda x: f"${x:,.0f}")
            df_tabla['Margen %'] = df_tabla['Margen %'].apply(lambda x: f"{x:.1f}%")
            
            def estado_margen(val):
                if isinstance(val, str):
                    valor = float(val.replace('%', ''))
                    if valor >= 42:
                        return "🟢 Excelente"
                    elif valor >= 30:
                        return "🟡 Aceptable"
                    else:
                        return "🔴 Crítico"
                return "⚪ Sin datos"
            
            df_tabla['Estado'] = df_tabla['Margen %'].apply(estado_margen)
            
            st.dataframe(
                df_tabla.style.map(color_margen_tabla, subset=['Margen %']).set_properties(**{
                    'text-align': 'center',
                    'padding': '8px'
                }).set_table_styles([
                    {'selector': 'th', 'props': [('text-align', 'center'), ('font-weight', 'bold'), ('background-color', '#F8FAFC'), ('color', '#1A2A3A'), ('padding', '8px')]},
                    {'selector': 'td', 'props': [('padding', '8px'), ('border-bottom', '1px solid #E5E7EB')]}
                ]),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No hay datos de CIERRE para los períodos seleccionados")

with tab4:
    st.markdown("### 📉 Análisis: Costo por Metro vs Tarifa")
    st.caption("Comparativa del costo real de perforación vs la tarifa cobrada por metro")
    
    # ===== FILTROS =====
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    
    with col_f1:
        # Contratos
        contratos_analisis = run_query("contratos", select="id, nombre", filters={"activo": 1})
        contrato_analisis = st.selectbox(
            "📋 Contrato",
            contratos_analisis['nombre'].tolist(),
            key="analisis_contrato"
        )
        id_contrato_analisis = contratos_analisis[contratos_analisis['nombre'] == contrato_analisis]['id'].iloc[0]
    
    with col_f2:
        # Clientes del contrato
        clientes_analisis = run_query("clientes", select="id, nombre, codigo", 
                                     filters={"id_contrato": id_contrato_analisis, "activo": 1})
        
        cliente_opciones = {"TODOS": None}
        for _, row in clientes_analisis.iterrows():
            cliente_opciones[f"{row['nombre']} ({row['codigo']})"] = row['id']
        
        cliente_analisis = st.selectbox(
            "👤 Cliente",
            list(cliente_opciones.keys()),
            key="analisis_cliente"
        )
        id_cliente_analisis = cliente_opciones[cliente_analisis]
    
    with col_f3:
        # Períodos disponibles para este contrato
        periodos_analisis = run_query("perforacion_general", select="periodo",
                                     filters={"id_contrato": id_contrato_analisis})
        periodos_analisis = periodos_analisis['periodo'].unique().tolist() if not periodos_analisis.empty else []
        periodos_analisis.sort(reverse=True)
        
        opciones_periodos = ["TODOS"] + periodos_analisis
        periodos_seleccionados = st.multiselect(
            "📅 Período(s)",
            options=opciones_periodos,
            default=[periodos_analisis[0]] if periodos_analisis else ["TODOS"],
            key="analisis_periodos"
        )
        
        if "TODOS" in periodos_seleccionados:
            periodos_seleccionados = periodos_analisis
    
    with col_f4:
        # Semanas disponibles
        if periodos_seleccionados:
            # Semanas AVANCE
            df_semanas = run_query("perforacion_general", select="semana",
                                  filters={"id_contrato": id_contrato_analisis, "periodo": periodos_seleccionados,
                                          "tipo_reporte": "AVANCE"})
            if not df_semanas.empty:
                semanas_avance = df_semanas[df_semanas['semana'] > 0]['semana'].unique().tolist()
                semanas_avance.sort()
            else:
                semanas_avance = []
            
            # Verificar CIERRE
            df_cierre = run_query("perforacion_general", select="periodo",
                                 filters={"id_contrato": id_contrato_analisis, "periodo": periodos_seleccionados,
                                         "tipo_reporte": "CIERRE"})
            tiene_cierre = not df_cierre.empty
        else:
            semanas_avance = []
            tiene_cierre = False
        
        opciones_semanas = []
        if tiene_cierre:
            opciones_semanas.append("CIERRE")
        opciones_semanas.extend([str(s) for s in semanas_avance])
        
        if not opciones_semanas:
            opciones_semanas = ["NO HAY DATOS"]
        
        semana_analisis = st.selectbox(
            "📊 Semana",
            options=opciones_semanas,
            index=0,
            key="analisis_semana"
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ===== CONSTRUIR FILTROS =====
    if not periodos_seleccionados:
        st.warning("⚠️ No hay períodos seleccionados")
        st.stop()
    
    if semana_analisis == "NO HAY DATOS":
        st.warning("⚠️ No hay datos disponibles para los filtros seleccionados")
        st.stop()
    
    if semana_analisis == "CIERRE":
        semana_valor = None
        tipo_reporte = "CIERRE"
    else:
        semana_valor = int(semana_analisis)
        tipo_reporte = "AVANCE"
    

    
    # ===== 1. OBTENER METROS (iterando por período) =====
    df_perforacion_lista = []
    
    for periodo in periodos_seleccionados:
        filtros_temp = {
            "id_contrato": id_contrato_analisis,
            "periodo": periodo,
            "tipo_operacion": "CPM",
            "tipo_reporte": tipo_reporte
        }
        if id_cliente_analisis:
            filtros_temp["id_cliente"] = id_cliente_analisis
        if semana_valor:
            filtros_temp["semana"] = semana_valor
        
        df_temp = run_query("perforacion_general", select="id, id_tipo_perforacion", filters=filtros_temp)
        
        if not df_temp.empty:
            df_perforacion_lista.append(df_temp)
    
    
    if df_perforacion_lista:
        df_perforacion = pd.concat(df_perforacion_lista, ignore_index=True)
        
        
        ids_perforacion = df_perforacion['id'].tolist()
        df_perforacion_detalle = run_query("perforacion_detalle", select="id_perforacion_general, total_mp",
                                          filters={"id_perforacion_general": ids_perforacion})
        
        if not df_perforacion_detalle.empty:
            df_metros = df_perforacion.merge(df_perforacion_detalle, left_on='id', right_on='id_perforacion_general')
            df_metros = df_metros.groupby('id_tipo_perforacion')['total_mp'].sum().reset_index()
            df_metros.columns = ['id_tipo_perforacion', 'metros_totales']
            
        else:
            df_metros = pd.DataFrame()
            st.warning("⚠️ No hay detalles de perforación")
    else:
        df_perforacion = pd.DataFrame()
        df_metros = pd.DataFrame()
        st.warning("⚠️ No se encontraron datos de perforación")
    
    # ===== 2. OBTENER COSTOS CPM (iterando por período) =====
    df_costos_lista = []
    
    for periodo in periodos_seleccionados:
        filtros_temp = {
            "tipo": "CPM",
            "id_contrato": id_contrato_analisis,
            "periodo": periodo,
            "tipo_reporte": tipo_reporte
        }
        if id_cliente_analisis:
            filtros_temp["id_cliente"] = id_cliente_analisis
        if semana_valor:
            filtros_temp["semana"] = semana_valor
        
        df_temp = run_query("vw_general_semanal",
                           select="id_tipo_perforacion, costos",
                           filters=filtros_temp)
        
        if not df_temp.empty:
            df_costos_lista.append(df_temp)
    
    
    
    if df_costos_lista:
        df_costos = pd.concat(df_costos_lista, ignore_index=True)
        df_costos = df_costos.groupby('id_tipo_perforacion')['costos'].sum().reset_index()
        df_costos.columns = ['id_tipo_perforacion', 'costo_total']
        
    else:
        df_costos = pd.DataFrame()
        st.warning("⚠️ No se encontraron datos de costos")
    
    # ===== 3. OBTENER TARIFAS =====
    filtros_tarifas = {"id_contrato": id_contrato_analisis}
    if id_cliente_analisis:
        filtros_tarifas["id_cliente"] = id_cliente_analisis
    
    df_tarifas = run_query("tarifas", select="id_tipo_perforacion, tarifa",
                          filters=filtros_tarifas)
    
    
    
    # Crear diccionarios
    metros_dict = {}
    tipo_nombre_dict = {}
    
    if not df_metros.empty:
        df_tipos = run_query("tipo_perforacion", select="id, nombre")
        tipos_dict = dict(zip(df_tipos['id'], df_tipos['nombre']))
        
        for _, row in df_metros.iterrows():
            metros_dict[row['id_tipo_perforacion']] = row['metros_totales']
            tipo_nombre_dict[row['id_tipo_perforacion']] = tipos_dict.get(row['id_tipo_perforacion'], "SIN TIPO")
    
    costo_dict = {}
    for _, row in df_costos.iterrows():
        costo_dict[row['id_tipo_perforacion']] = row['costo_total']
    
    tarifa_dict = {}
    for _, row in df_tarifas.iterrows():
        tarifa_dict[row['id_tipo_perforacion']] = row['tarifa']
    
    # ===== COMBINAR TODOS LOS TIPOS =====
    todos_los_tipos = set(metros_dict.keys()) | set(costo_dict.keys()) | set(tarifa_dict.keys())
    
    
    
    datos_analisis = []
    
    for id_tipo in todos_los_tipos:
        tipo_nombre = tipo_nombre_dict.get(id_tipo, "SIN TIPO")
        metros = metros_dict.get(id_tipo, 0)
        costo_total = costo_dict.get(id_tipo, 0)
        tarifa = tarifa_dict.get(id_tipo, 0)
        
        if metros > 0:
            costo_por_metro = costo_total / metros
        else:
            costo_por_metro = 0
        
        diferencia = tarifa - costo_por_metro
        margen = (diferencia / tarifa * 100) if tarifa > 0 else 0
        
        # Determinar estado
        if tarifa == 0:
            estado = "⚪ Sin tarifa"
            color_estado = "#64748b"
        elif margen >= 30:
            estado = "🟢 Excelente"
            color_estado = "#10b981"
        elif margen >= 15:
            estado = "🟡 Aceptable"
            color_estado = "#f59e0b"
        elif margen >= 0:
            estado = "🟠 Justo"
            color_estado = "#f97316"
        else:
            estado = "🔴 Pérdida"
            color_estado = "#ef4444"
        
        datos_analisis.append({
            'id_tipo_perforacion': id_tipo,
            'Tipo Perforación': tipo_nombre,
            'Metros (m)': metros,
            'Costo Total': costo_total,
            'Costo por Metro': costo_por_metro,
            'Tarifa por Metro': tarifa,
            'Diferencia': diferencia,
            'Margen %': margen,
            'Estado': estado,
            'color_estado': color_estado
        })
    
    if not datos_analisis:
        st.info("No hay datos de perforación para los filtros seleccionados")
    else:
        df_analisis = pd.DataFrame(datos_analisis)
        
        # ===== TARJETAS DE RESUMEN =====
        st.markdown("#### 📊 Resumen General")
        
        total_metros = df_analisis['Metros (m)'].sum()
        total_costo = df_analisis['Costo Total'].sum()
        costo_promedio_metro = total_costo / total_metros if total_metros > 0 else 0
        
        # Tarifa promedio ponderada por metros
        tarifa_promedio = 0
        if total_metros > 0:
            tarifa_promedio = sum(
                row['Tarifa por Metro'] * row['Metros (m)'] 
                for _, row in df_analisis.iterrows()
            ) / total_metros
        
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
        
        # ===== GRÁFICO 1: Costo por Metro vs Tarifa por Metro =====
        st.markdown("#### 📊 Comparativa: Costo vs Tarifa por Metro")
        
        # Filtrar tipos con datos relevantes para el gráfico
        df_grafico = df_analisis[df_analisis['Metros (m)'] > 0].copy()
        
        if not df_grafico.empty:
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=df_grafico['Tipo Perforación'],
                y=df_grafico['Costo por Metro'],
                name='Costo por Metro',
                marker_color='#ef4444',
                text=df_grafico['Costo por Metro'].round(2).astype(str),
                textposition='outside'
            ))
            
            fig.add_trace(go.Bar(
                x=df_grafico['Tipo Perforación'],
                y=df_grafico['Tarifa por Metro'],
                name='Tarifa por Metro',
                marker_color='#10b981',
                text=df_grafico['Tarifa por Metro'].round(2).astype(str),
                textposition='outside'
            ))
            
            fig.update_layout(
                title="Costo por Metro vs Tarifa por Metro",
                xaxis_title="Tipo de Perforación",
                yaxis_title="Valor por Metro ($)",
                height=450,
                barmode='group'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos con metros para mostrar en el gráfico")
        
        # ===== GRÁFICO 2: Margen por Tipo =====
        st.markdown("#### 📈 Margen por Tipo de Perforación")
        
        df_margen = df_analisis[(df_analisis['Tarifa por Metro'] > 0) & (df_analisis['Metros (m)'] > 0)].copy()
        
        if not df_margen.empty:
            colores_margen = []
            for _, row in df_margen.iterrows():
                if row['Margen %'] >= 30:
                    colores_margen.append('#10b981')
                elif row['Margen %'] >= 15:
                    colores_margen.append('#f59e0b')
                elif row['Margen %'] >= 0:
                    colores_margen.append('#f97316')
                else:
                    colores_margen.append('#ef4444')
            
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(
                x=df_margen['Tipo Perforación'],
                y=df_margen['Margen %'],
                marker_color=colores_margen,
                text=df_margen['Margen %'].round(1).astype(str) + '%',
                textposition='outside'
            ))
            
            fig2.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Excelente (30%)")
            fig2.add_hline(y=15, line_dash="dash", line_color="orange", annotation_text="Aceptable (15%)")
            
            fig2.update_layout(
                title="Margen por Tipo de Perforación",
                xaxis_title="Tipo de Perforación",
                yaxis_title="Margen (%)",
                height=400
            )
            
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No hay datos con tarifa definida para mostrar el margen")
        
        # ===== TABLA DETALLADA =====
        st.markdown("#### 📋 Detalle por Tipo de Perforación")
        
        df_tabla = df_analisis.copy()
        df_tabla = df_tabla[df_tabla['Metros (m)'] > 0]
        
        if not df_tabla.empty:
            df_tabla['Costo Total'] = df_tabla['Costo Total'].apply(lambda x: f"${x:,.0f}")
            df_tabla['Metros (m)'] = df_tabla['Metros (m)'].apply(lambda x: f"{x:,.0f}")
            df_tabla['Costo por Metro'] = df_tabla['Costo por Metro'].apply(lambda x: f"${x:.2f}")
            df_tabla['Tarifa por Metro'] = df_tabla['Tarifa por Metro'].apply(lambda x: f"${x:.2f}" if x > 0 else "-")
            df_tabla['Diferencia'] = df_tabla['Diferencia'].apply(lambda x: f"${x:.2f}")
            df_tabla['Margen %'] = df_tabla['Margen %'].apply(lambda x: f"{x:.1f}%" if x != 0 else "-")
            
            df_tabla = df_tabla[['Tipo Perforación', 'Metros (m)', 'Costo Total', 'Costo por Metro', 
                                 'Tarifa por Metro', 'Diferencia', 'Margen %', 'Estado']]
            
            st.dataframe(
                df_tabla.style.set_properties(**{
                    'text-align': 'center',
                    'border': '1px solid #e5e7eb',
                    'padding': '8px'
                }).set_table_styles([
                    {'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#f3f4f6'), ('color', '#374151'), ('font-weight', '600')]}
                ]),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No hay tipos de perforación con metros registrados")
        
        # ===== ALERTAS =====
        perdidas = df_analisis[(df_analisis['Margen %'] < 0) & (df_analisis['Tarifa por Metro'] > 0)]
        if not perdidas.empty:
            st.warning("⚠️ **Tipos de perforación con pérdida:** " + ", ".join(perdidas['Tipo Perforación'].tolist()))
        
        sin_tarifa = df_analisis[(df_analisis['Tarifa por Metro'] == 0) & (df_analisis['Metros (m)'] > 0)]
        if not sin_tarifa.empty:
            st.info("ℹ️ **Tipos con metros pero sin tarifa definida:** " + ", ".join(sin_tarifa['Tipo Perforación'].tolist()))
        
        cero_metros = df_analisis[(df_analisis['Metros (m)'] == 0) & (df_analisis['Costo Total'] > 0)]
        if not cero_metros.empty:
            st.info("ℹ️ **Tipos con costo pero sin metros registrados:** " + ", ".join(cero_metros['Tipo Perforación'].tolist()))
