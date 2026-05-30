import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from database.conexion import run_query, get_supabase

# Configuración
st.set_page_config(
    page_title="Rock Tools Peru - Dashboard",
    page_icon="⛏️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ESTILOS MEJORADOS (NUEVO)
st.markdown("""
<style>
    /* Ocultar sidebar */
    [data-testid="stSidebar"] {display: none !important;}
    [data-testid="collapsedControl"] {display: none !important;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Contenedor principal */
    .main > .block-container {
        padding-top: 1rem !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
        max-width: 1400px;
        margin: 0 auto;
    }
    
    /* === REDUCIR ANCHO DE FILTROS === */
    div[data-testid="column"]:has(div:has(label:contains("Período"))) {
        max-width: 300px !important;
    }
    
    div[data-testid="column"]:has(div:has(label:contains("Semana"))) {
        max-width: 250px !important;
    }
    
    /* Mejorar espaciado entre elementos */
    .stSelectbox, .stMultiSelect {
        margin-bottom: 0.5rem;
    }
    
    /* Tarjetas más compactas en móvil */
    @media (max-width: 768px) {
        .main > .block-container {
            padding-left: 0.75rem !important;
            padding-right: 0.75rem !important;
        }
        
        /* KPIs en móvil: 2 columnas */
        div[data-testid="column"]:has(div[data-testid="stVerticalBlock"]) {
            min-width: 150px !important;
        }
        
        /* Reducir tamaños de texto en móvil */
        .stMarkdown h1 {
            font-size: 1.5rem !important;
        }
        
        .stMarkdown h2 {
            font-size: 1.2rem !important;
        }
        
        /* Navegación responsive - permitir scroll horizontal */
        div[data-testid="stHorizontalBlock"] {
            overflow-x: auto !important;
            flex-wrap: nowrap !important;
        }
        
        div[data-testid="stHorizontalBlock"] > div {
            min-width: auto !important;
            flex-shrink: 0 !important;
        }
    }
    
    /* Mejoras generales de diseño */
    div[data-testid="stContainer"][border="true"] {
        border-radius: 12px;
        background: white;
        transition: box-shadow 0.2s;
    }
    
    div[data-testid="stContainer"][border="true"]:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    }
    
    /* Botones de navegación más elegantes */
    .stButton button {
        border-radius: 8px !important;
        transition: all 0.2s;
    }
    
    .stButton button:hover {
        transform: translateY(-1px);
    }
</style>
""", unsafe_allow_html=True)

# Verificar autenticación
if 'autenticado' not in st.session_state or not st.session_state['autenticado']:
    st.switch_page("app.py")

if 'usuario' not in st.session_state:
    st.session_state['usuario'] = 'Admin'

# ============================================================================
# HEADER
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
    if st.button("🚪 Salir", key="logout", type="secondary", use_container_width=True):
        st.session_state.clear()
        st.switch_page("app.py")

st.divider()

# ============================================================================
# TÍTULO
# ============================================================================
st.markdown("## 📊 Panel de Control")
st.markdown("Resumen global del negocio")
st.markdown("<br>", unsafe_allow_html=True)

# ============================================================================
# OBTENER PERIODOS DISPONIBLES
# ============================================================================
try:
    # Obtener periodos de las tres vistas
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
except:
    periodos_disponibles = []

if not periodos_disponibles:
    periodos_disponibles = [datetime.now().strftime("%Y-%m")]

# ============================================================================
# FILTROS (con lógica similar a contratos) - MODIFICADO: ahora más compactos
# ============================================================================
# Usar columns con proporciones más pequeñas para los filtros
col_f1, col_f2, col_spacer = st.columns([1, 1, 3])

with col_f1:
    opciones_periodos = ["TODOS"] + periodos_disponibles
    periodos_seleccionados = st.multiselect(
        "📅 Período(s)",
        options=opciones_periodos,
        default=[periodos_disponibles[0]] if periodos_disponibles else ["TODOS"],
        key="dashboard_periodos"
    )
    
    if "TODOS" in periodos_seleccionados:
        periodos_seleccionados = periodos_disponibles
    
    # Guardar copia original para comparar después
    periodos_originales = periodos_seleccionados.copy()

with col_f2:
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
        opciones_semanas = ["TODAS"]
    
    semana_seleccionada = st.selectbox(
        "📊 Semana",
        options=opciones_semanas,
        index=0,
        key="dashboard_semana"
    )

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================================
# CONSTRUIR FILTROS (misma lógica que contratos)
# ============================================================================
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
elif semana_seleccionada == "TODAS":
    # Mostrar todos los datos sin filtrar por semana específica
    filtro_tipo_reporte = "AVANCE"
    filtro_semana_valor = None
else:
    semana_valor = int(semana_seleccionada)
    # Verificar qué períodos tienen esta semana AVANCE
    df_periodos_con_semana = run_query("vw_general_semanal",
                                       select="periodo",
                                       filters={"periodo": periodos_originales, 
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

# ============================================================================
# FUNCIÓN PARA CONSULTAS SEGURAS
# ============================================================================
def safe_query_dataframe(df, default=0):
    try:
        if df.empty:
            return default
        val = df.iloc[0, 0]
        return val if val is not None else default
    except Exception as e:
        print(f"Error en query: {e}")
        return default

# ============================================================================
# KPIS - Usando vw_general_semanal
# ============================================================================
# Construir filtros base
filtros_base = {"periodo": periodos_seleccionados, "tipo_reporte": filtro_tipo_reporte}
if filtro_semana_valor is not None:
    filtros_base["semana"] = filtro_semana_valor

# Ingresos CPM
filtros_cpm = filtros_base.copy()
filtros_cpm["tipo"] = "CPM"
df_ingresos_cpm = run_query("vw_general_semanal", select="ingresos", filters=filtros_cpm)
ingresos_cpm = df_ingresos_cpm['ingresos'].sum() if not df_ingresos_cpm.empty else 0

# Ingresos VENTA
filtros_venta = filtros_base.copy()
filtros_venta["tipo"] = "VENTA"
df_ingresos_venta = run_query("vw_general_semanal", select="ingresos", filters=filtros_venta)
ingresos_venta = df_ingresos_venta['ingresos'].sum() if not df_ingresos_venta.empty else 0

# Costos CPM
df_costos_cpm = run_query("vw_general_semanal", select="costos", filters=filtros_cpm)
costos_cpm = df_costos_cpm['costos'].sum() if not df_costos_cpm.empty else 0

# Costos VENTA
df_costos_venta = run_query("vw_general_semanal", select="costos", filters=filtros_venta)
costos_venta = df_costos_venta['costos'].sum() if not df_costos_venta.empty else 0

# Costos AFILADORAS
filtros_afiladoras = filtros_base.copy()
filtros_afiladoras["tipo"] = "AFILADORAS"
df_afiladoras = run_query("vw_general_semanal", select="otros_costos", filters=filtros_afiladoras)
costos_afiladoras = df_afiladoras['otros_costos'].sum() if not df_afiladoras.empty else 0

# Totales
ingresos_totales = ingresos_cpm + ingresos_venta
costos_totales = costos_cpm + costos_venta + costos_afiladoras
margen_total = ingresos_totales - costos_totales
margen_pct = (1 - costos_totales/ingresos_totales) * 100 if ingresos_totales > 0 else 0

# Mostrar KPIs
kpi_cols = st.columns(4)

with kpi_cols[0]:
    with st.container(border=True):
        st.markdown("#### 💰 Ingresos")
        st.markdown(f"# ${ingresos_totales:,.0f}")

with kpi_cols[1]:
    with st.container(border=True):
        st.markdown("#### 💸 Costos")
        st.markdown(f"# ${costos_totales:,.0f}")

with kpi_cols[2]:
    with st.container(border=True):
        st.markdown("#### 📊 Margen")
        st.markdown(f"# ${margen_total:,.0f}")

with kpi_cols[3]:
    with st.container(border=True):
        st.markdown("#### 🎯 Margen %")
        st.markdown(f"# {margen_pct:.1f}%")
        objetivo = 42
        progreso = min(margen_pct / objetivo, 1.0) if margen_pct > 0 else 0
        st.progress(progreso, text=f"Objetivo: {objetivo}%")

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================================
# GRÁFICO DE EVOLUCIÓN MENSUAL
# ============================================================================
with st.container(border=True):
    st.markdown("### 📈 Ingresos vs Costos - Evolución Mensual")
    
    # Extraer mes de los períodos seleccionados
    periodos_para_evolucion = periodos_seleccionados
    
    # Obtener datos de evolución
    df_evolucion = run_query("vw_general_semanal",
                             select="periodo, tipo, ingresos, costos, otros_costos",
                             filters={"periodo": periodos_para_evolucion})
    
    # Aplicar filtro de semana si existe
    if filtro_semana_valor is not None:
        df_evolucion = df_evolucion[df_evolucion['tipo_reporte'] == filtro_tipo_reporte]
        df_evolucion = df_evolucion[df_evolucion['semana'] == filtro_semana_valor]
    else:
        df_evolucion = df_evolucion[df_evolucion['tipo_reporte'] == filtro_tipo_reporte]
    
    if not df_evolucion.empty:
        # Agrupar por mes
        df_evolucion['mes'] = df_evolucion['periodo'].str[5:7]
        
        # Calcular ingresos y costos por mes
        df_ingresos = df_evolucion[df_evolucion['tipo'].isin(['CPM', 'VENTA'])].groupby('mes')['ingresos'].sum().reset_index()
        df_costos_total = df_evolucion.groupby('mes').apply(
            lambda x: x[x['tipo'].isin(['CPM', 'VENTA'])]['costos'].sum() + x['otros_costos'].sum()
        ).reset_index(name='costos')
        
        df_evolucion_mes = df_ingresos.merge(df_costos_total, on='mes')
        df_evolucion_mes.columns = ['mes', 'ingresos', 'costos']
        
        if not df_evolucion_mes.empty:
            meses_map = {'01': 'Ene', '02': 'Feb', '03': 'Mar', '04': 'Abr', '05': 'May', '06': 'Jun',
                        '07': 'Jul', '08': 'Ago', '09': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dic'}
            
            df_evolucion_mes['mes_nombre'] = df_evolucion_mes['mes'].map(meses_map)
            df_evolucion_mes = df_evolucion_mes.sort_values('mes')
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_evolucion_mes['mes_nombre'], 
                y=df_evolucion_mes['ingresos'], 
                mode='lines+markers',
                name='Ingresos', 
                line=dict(color='#1152d4', width=3)
            ))
            fig.add_trace(go.Scatter(
                x=df_evolucion_mes['mes_nombre'], 
                y=df_evolucion_mes['costos'], 
                mode='lines+markers',
                name='Costos', 
                line=dict(color='#ef4444', width=3)
            ))
            
            fig.update_layout(height=400, margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos mensuales para los períodos seleccionados")
    else:
        st.info("No hay datos disponibles")

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================================
# GRÁFICO DE MÁRGENES POR CONTRATO
# ============================================================================
with st.container(border=True):
    st.markdown("### 📊 Márgenes por Contrato")
    
    # Obtener datos de contratos
    df_contratos_raw = run_query("vw_general_semanal",
                                 select="id_contrato, tipo, ingresos, costos, otros_costos",
                                 filters={"periodo": periodos_seleccionados, "tipo_reporte": filtro_tipo_reporte})
    
    if filtro_semana_valor is not None:
        df_contratos_raw = df_contratos_raw[df_contratos_raw['semana'] == filtro_semana_valor]
    
    if not df_contratos_raw.empty:
        # Obtener nombres de contratos
        df_contratos_nombres = run_query("contratos", select="id, nombre")
        contratos_dict = dict(zip(df_contratos_nombres['id'], df_contratos_nombres['nombre']))
        
        # Agrupar por contrato
        df_contratos_agg = []
        for contrato_id in df_contratos_raw['id_contrato'].unique():
            df_cont = df_contratos_raw[df_contratos_raw['id_contrato'] == contrato_id]
            ingresos = df_cont[df_cont['tipo'].isin(['CPM', 'VENTA'])]['ingresos'].sum()
            costos = df_cont[df_cont['tipo'].isin(['CPM', 'VENTA'])]['costos'].sum() + df_cont['otros_costos'].sum()
            if ingresos > 0:
                df_contratos_agg.append({
                    'contrato': contratos_dict.get(contrato_id, f"ID:{contrato_id}"),
                    'ingresos': ingresos,
                    'costos': costos
                })
        
        df_contratos = pd.DataFrame(df_contratos_agg)
        
        if not df_contratos.empty:
            df_contratos['margen'] = (1 - df_contratos['costos'] / df_contratos['ingresos']) * 100
            df_contratos = df_contratos.sort_values('margen', ascending=True)
            
            colores = ['#10b981' if m >= 42 else '#f59e0b' if m >= 30 else '#ef4444' for m in df_contratos['margen']]
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df_contratos['margen'],
                y=df_contratos['contrato'],
                orientation='h',
                marker_color=colores,
                text=df_contratos['margen'].round(1).astype(str) + '%',
                textposition='outside'
            ))
            fig.add_vline(x=42, line_dash="dash", line_color="green", annotation_text="Objetivo 42%")
            
            fig.update_layout(height=400, margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos de contratos para los filtros seleccionados")
    else:
        st.info("No hay datos disponibles")

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================================
# TABLA DE CONTRATOS Y ALERTAS (ELIMINADO "Últimas Cargas")
# ============================================================================
col_tabla, col_alertas = st.columns([2, 1])

with col_tabla:
    with st.container(border=True):
        st.markdown("### 📋 Contratos Activos")
        
        # Usar los mismos datos ya obtenidos
        if 'df_contratos' in locals() and not df_contratos.empty:
            df_tabla = df_contratos.copy()
            df_tabla['ingresos'] = df_tabla['ingresos'].apply(lambda x: f"${x:,.0f}")
            
            def formato_margen(row):
                m = row['margen']
                if m >= 42:
                    return f"{m:.1f}% 🟢"
                elif m >= 30:
                    return f"{m:.1f}% 🟡"
                else:
                    return f"{m:.1f}% 🔴"
            
            df_tabla['margen'] = df_tabla.apply(formato_margen, axis=1)
            df_tabla = df_tabla[['contrato', 'ingresos', 'margen']]
            df_tabla.columns = ['Contrato', 'Ingresos', 'Margen']
            
            st.dataframe(df_tabla, use_container_width=True, hide_index=True)
        else:
            st.info("No hay datos para mostrar")

with col_alertas:
    with st.container(border=True):
        st.markdown("### ⚠️ Alertas")
        
        # Usar los mismos datos ya obtenidos
        if 'df_contratos' in locals() and not df_contratos.empty:
            alertas = []
            
            for _, row in df_contratos.iterrows():
                if row['margen'] < 30:
                    alertas.append(f"🔴 **{row['contrato']}** - Margen: {row['margen']:.1f}%")
                elif row['margen'] < 42:
                    alertas.append(f"🟡 **{row['contrato']}** - Margen: {row['margen']:.1f}%")
            
            if alertas:
                for alerta in alertas[:5]:
                    if "🔴" in alerta:
                        st.error(alerta)
                    else:
                        st.warning(alerta)
            else:
                st.success("✅ No hay alertas activas")
        else:
            st.success("✅ No hay alertas activas")

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================================
# GRÁFICOS SECUNDARIOS
# ============================================================================
col_pie, col_margen = st.columns(2)

with col_pie:
    with st.container(border=True):
        st.markdown("### 📊 Distribución de Ingresos")
        
        if ingresos_cpm > 0 or ingresos_venta > 0:
            fig = go.Figure(data=[go.Pie(
                labels=['CPM', 'Venta Directa'],
                values=[ingresos_cpm, ingresos_venta],
                hole=0.4,
                marker_colors=['#1152d4', '#f59e0b']
            )])
            fig.update_layout(height=300, margin=dict(l=0, r=0, t=20, b=0))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos de ingresos")

with col_margen:
    with st.container(border=True):
        st.markdown("### 📈 Evolución del Margen")
        
        # Calcular margen mensual
        df_margen_mensual_raw = run_query("vw_general_semanal",
                                         select="periodo, tipo, ingresos, costos, otros_costos",
                                         filters={"periodo": periodos_seleccionados})
        
        if filtro_semana_valor is not None:
            df_margen_mensual_raw = df_margen_mensual_raw[df_margen_mensual_raw['tipo_reporte'] == filtro_tipo_reporte]
            df_margen_mensual_raw = df_margen_mensual_raw[df_margen_mensual_raw['semana'] == filtro_semana_valor]
        else:
            df_margen_mensual_raw = df_margen_mensual_raw[df_margen_mensual_raw['tipo_reporte'] == filtro_tipo_reporte]
        
        if not df_margen_mensual_raw.empty:
            df_margen_mensual_raw['mes'] = df_margen_mensual_raw['periodo'].str[5:7]
            
            # Calcular margen por mes
            df_margen_mensual = []
            for mes in df_margen_mensual_raw['mes'].unique():
                df_mes = df_margen_mensual_raw[df_margen_mensual_raw['mes'] == mes]
                ingresos = df_mes[df_mes['tipo'].isin(['CPM', 'VENTA'])]['ingresos'].sum()
                costos = df_mes[df_mes['tipo'].isin(['CPM', 'VENTA'])]['costos'].sum() + df_mes['otros_costos'].sum()
                if ingresos > 0:
                    margen = (1 - costos/ingresos) * 100
                    df_margen_mensual.append({'mes': mes, 'margen': margen})
            
            df_margen_mensual = pd.DataFrame(df_margen_mensual)
            
            if not df_margen_mensual.empty:
                meses_map = {'01': 'Ene', '02': 'Feb', '03': 'Mar', '04': 'Abr', '05': 'May', '06': 'Jun',
                            '07': 'Jul', '08': 'Ago', '09': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dic'}
                
                df_margen_mensual['mes_nombre'] = df_margen_mensual['mes'].map(meses_map)
                df_margen_mensual = df_margen_mensual.sort_values('mes')
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df_margen_mensual['mes_nombre'],
                    y=df_margen_mensual['margen'],
                    mode='lines+markers',
                    line=dict(color='#10b981', width=3),
                    fill='tozeroy'
                ))
                fig.add_hline(y=42, line_dash="dash", line_color="gray", annotation_text="Objetivo 42%")
                
                fig.update_layout(height=300, margin=dict(l=0, r=0, t=20, b=0))
                st.plotly_chart(fig, use_container_width=True)
            else:   
                st.info("No hay datos de evolución mensual")
        else:
            st.info("No hay datos de evolución mensual")

# ============================================================================
# FOOTER
# ============================================================================
st.divider()
footer_cols = st.columns(3)

with footer_cols[0]:
    st.markdown("© 2026 Rock Tools Peru S.A.")

with footer_cols[1]:
    st.markdown("v2.0.0")

with footer_cols[2]:
    fecha_actual = datetime.now().strftime("%d/%m/%Y")
    st.markdown(f"Última actualización: {fecha_actual}")