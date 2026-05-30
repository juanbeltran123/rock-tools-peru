import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from database.conexion import run_query, run_query_in

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
# OBTENER PERIODOS DISPONIBLES (MODIFICADO)
# ============================================================================
try:
    # Obtener periodos de las diferentes fuentes
    df1 = run_query("vw_general_semanal", select="periodo")
    df2 = run_query("vw_cpm_resultado", select="periodo")
    df3 = run_query("vw_venta", select="periodo")
    
    # Combinar y obtener únicos
    todos_periodos = pd.concat([df1, df2, df3], ignore_index=True)
    periodos_disponibles = todos_periodos['periodo'].drop_duplicates().sort_values(ascending=False).tolist()
except Exception as e:
    st.write(f"Error: {e}")
    periodos_disponibles = []

if not periodos_disponibles:
    periodos_disponibles = [datetime.now().strftime("%Y-%m")]

# ============================================================================
# FILTROS
# ============================================================================
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
        periodos_seleccionados = periodos_disponibles.copy()
    
    periodos_originales = periodos_seleccionados.copy()

with col_f2:
    if periodos_seleccionados:
        # Obtener datos de vw_general_semanal para los períodos seleccionados
        df_general = run_query_in("vw_general_semanal", "periodo", periodos_seleccionados)
        
        # Obtener semanas AVANCE
        df_avance = df_general[(df_general['tipo_reporte'] == 'AVANCE') & (df_general['semana'] > 0)]
        semanas_avance = df_avance['semana'].drop_duplicates().sort_values().tolist()
        
        # Verificar períodos con CIERRE
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
        opciones_semanas = ["TODAS"]
    
    semana_seleccionada = st.selectbox(
        "📊 Semana",
        options=opciones_semanas,
        index=0,
        key="dashboard_semana"
    )

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================================
# CONSTRUIR FILTROS
# ============================================================================
if not periodos_seleccionados:
    st.warning("⚠️ No hay períodos seleccionados")
    st.stop()

# Construir filtro de semana según selección
if semana_seleccionada == "CIERRE":
    if periodos_con_cierre:
        periodos_seleccionados = [p for p in periodos_seleccionados if p in periodos_con_cierre]
        if len(periodos_seleccionados) < len(periodos_originales):
            st.info(f"📌 Mostrando solo períodos con CIERRE: {', '.join(periodos_seleccionados)}")
        usar_cierre = True
        semana_valor = None
    else:
        st.error("❌ Ninguno de los períodos seleccionados tiene datos de CIERRE")
        st.stop()
elif semana_seleccionada == "TODAS":
    usar_cierre = False
    semana_valor = None
else:
    semana_valor = int(semana_seleccionada)
    usar_cierre = False
    
    # Verificar qué períodos tienen esta semana AVANCE
    df_avance_filtro = df_general[(df_general['tipo_reporte'] == 'AVANCE') & (df_general['semana'] == semana_valor)]
    periodos_con_semana = df_avance_filtro['periodo'].drop_duplicates().tolist()
    
    if periodos_con_semana:
        periodos_seleccionados = [p for p in periodos_seleccionados if p in periodos_con_semana]
        if len(periodos_seleccionados) < len(periodos_originales):
            st.info(f"📌 Mostrando solo períodos con datos de semana {semana_valor}: {', '.join(periodos_seleccionados)}")
    else:
        st.error(f"❌ Ninguno de los períodos seleccionados tiene datos de semana {semana_valor}")
        st.stop()

# ============================================================================
# FUNCIÓN PARA OBTENER DATOS FILTRADOS
# ============================================================================
def get_datos_filtrados():
    """Obtiene los datos de vw_general_semanal aplicando los filtros"""
    df = run_query_in("vw_general_semanal", "periodo", periodos_seleccionados)
    
    # Aplicar filtro de semana
    if usar_cierre:
        df = df[df['tipo_reporte'] == 'CIERRE']
    elif semana_valor is not None:
        df = df[(df['tipo_reporte'] == 'AVANCE') & (df['semana'] == semana_valor)]
    else:
        df = df[df['tipo_reporte'] == 'AVANCE']
    
    return df

# ============================================================================
# KPIS
# ============================================================================
df_kpis = get_datos_filtrados()

ingresos_cpm = df_kpis[df_kpis['tipo'] == 'CPM']['ingresos'].sum() if 'ingresos' in df_kpis.columns else 0
ingresos_venta = df_kpis[df_kpis['tipo'] == 'VENTA']['ingresos'].sum() if 'ingresos' in df_kpis.columns else 0
costos_cpm = df_kpis[df_kpis['tipo'] == 'CPM']['costos'].sum() if 'costos' in df_kpis.columns else 0
costos_venta = df_kpis[df_kpis['tipo'] == 'VENTA']['costos'].sum() if 'costos' in df_kpis.columns else 0
costos_afiladoras = df_kpis[df_kpis['tipo'] == 'AFILADORAS']['otros_costos'].sum() if 'otros_costos' in df_kpis.columns else 0

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
    
    # Crear columna de mes a partir del periodo
    df_evolucion = df_kpis.copy()
    if not df_evolucion.empty:
        df_evolucion['mes'] = df_evolucion['periodo'].str[5:7]
        
        # Agrupar por mes
        df_mensual = df_evolucion.groupby('mes').agg({
            'ingresos': 'sum',
            'costos': 'sum'
        }).reset_index()
        
        # Agregar otros_costos
        df_otros = df_evolucion.groupby('mes')['otros_costos'].sum().reset_index()
        df_mensual = df_mensual.merge(df_otros, on='mes', how='left')
        df_mensual['costos'] = df_mensual['costos'] + df_mensual['otros_costos'].fillna(0)
        
        if not df_mensual.empty:
            meses_map = {'01': 'Ene', '02': 'Feb', '03': 'Mar', '04': 'Abr', '05': 'May', '06': 'Jun',
                        '07': 'Jul', '08': 'Ago', '09': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dic'}
            
            df_mensual['mes_nombre'] = df_mensual['mes'].map(meses_map)
            df_mensual = df_mensual.sort_values('mes')
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_mensual['mes_nombre'], 
                y=df_mensual['ingresos'], 
                mode='lines+markers',
                name='Ingresos', 
                line=dict(color='#1152d4', width=3)
            ))
            fig.add_trace(go.Scatter(
                x=df_mensual['mes_nombre'], 
                y=df_mensual['costos'], 
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
    df_contratos = df_kpis.groupby('id_contrato').agg({
        'ingresos': 'sum',
        'costos': 'sum'
    }).reset_index()
    
    # Agregar otros_costos
    df_otros_contratos = df_kpis.groupby('id_contrato')['otros_costos'].sum().reset_index()
    df_contratos = df_contratos.merge(df_otros_contratos, on='id_contrato', how='left')
    df_contratos['costos'] = df_contratos['costos'] + df_contratos['otros_costos'].fillna(0)
    
    # Obtener nombres de contratos
    df_contratos_nombres = run_query("contratos", select="id, nombre")
    df_contratos = df_contratos.merge(df_contratos_nombres, left_on='id_contrato', right_on='id', how='left')
    
    df_contratos = df_contratos[df_contratos['ingresos'] > 0]
    
    if not df_contratos.empty:
        df_contratos['margen'] = (1 - df_contratos['costos'] / df_contratos['ingresos']) * 100
        df_contratos = df_contratos.sort_values('margen', ascending=True)
        
        colores = ['#10b981' if m >= 42 else '#f59e0b' if m >= 30 else '#ef4444' for m in df_contratos['margen']]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df_contratos['margen'],
            y=df_contratos['nombre'],
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

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================================
# TABLA DE CONTRATOS Y ALERTAS
# ============================================================================
col_tabla, col_alertas = st.columns([2, 1])

with col_tabla:
    with st.container(border=True):
        st.markdown("### 📋 Contratos Activos")
        
        df_tabla = df_contratos.copy()
        
        if not df_tabla.empty:
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
            df_tabla = df_tabla[['nombre', 'ingresos', 'margen']]
            df_tabla.columns = ['Contrato', 'Ingresos', 'Margen']
            
            st.dataframe(df_tabla, use_container_width=True, hide_index=True)
        else:
            st.info("No hay datos para mostrar")

with col_alertas:
    with st.container(border=True):
        st.markdown("### ⚠️ Alertas")
        
        if not df_contratos.empty:
            alertas = []
            
            for _, row in df_contratos.iterrows():
                if row['margen'] < 30:
                    alertas.append(f"🔴 **{row['nombre']}** - Margen: {row['margen']:.1f}%")
                elif row['margen'] < 42:
                    alertas.append(f"🟡 **{row['nombre']}** - Margen: {row['margen']:.1f}%")
            
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
        
        df_margen_mensual = df_evolucion.copy()
        if not df_margen_mensual.empty:
            df_margen_mensual['mes'] = df_margen_mensual['periodo'].str[5:7]
            
            # Agrupar por mes
            df_margen_group = df_margen_mensual.groupby('mes').agg({
                'ingresos': 'sum',
                'costos': 'sum'
            }).reset_index()
            
            df_otros_group = df_margen_mensual.groupby('mes')['otros_costos'].sum().reset_index()
            df_margen_group = df_margen_group.merge(df_otros_group, on='mes', how='left')
            df_margen_group['costos'] = df_margen_group['costos'] + df_margen_group['otros_costos'].fillna(0)
            
            df_margen_group['margen'] = (1 - df_margen_group['costos'] / df_margen_group['ingresos']) * 100
            df_margen_group['margen'] = df_margen_group['margen'].fillna(0)
            
            meses_map = {'01': 'Ene', '02': 'Feb', '03': 'Mar', '04': 'Abr', '05': 'May', '06': 'Jun',
                        '07': 'Jul', '08': 'Ago', '09': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dic'}
            
            df_margen_group['mes_nombre'] = df_margen_group['mes'].map(meses_map)
            df_margen_group = df_margen_group.sort_values('mes')
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_margen_group['mes_nombre'],
                y=df_margen_group['margen'],
                mode='lines+markers',
                line=dict(color='#10b981', width=3),
                fill='tozeroy'
            ))
            fig.add_hline(y=42, line_dash="dash", line_color="gray", annotation_text="Objetivo 42%")
            
            fig.update_layout(height=300, margin=dict(l=0, r=0, t=20, b=0))
            st.plotly_chart(fig, use_container_width=True)
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