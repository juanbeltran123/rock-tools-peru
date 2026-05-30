import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from database.conexion import get_connection

# Configuración de la página
st.set_page_config(
    page_title="Rock Tools Peru - Dashboard",
    page_icon="⛏️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ===== OCULTAR SIDEBAR COMPLETAMENTE =====
st.markdown("""
<style>
    /* Ocultar sidebar */
    [data-testid="stSidebar"] {display: none;}
    [data-testid="collapsedControl"] {display: none;}
    
    /* Ocultar menú de navegación superior */
    #MainMenu {visibility: hidden;}
    
    /* Ocultar footer */
    footer {visibility: hidden;}
    
    /* Ajustar padding del contenido principal */
    .main > .block-container {
        padding-top: 0 !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Verificar autenticación
if 'autenticado' not in st.session_state or not st.session_state['autenticado']:
    st.switch_page("app.py")

# Asegurar que existe la clave 'usuario'
if 'usuario' not in st.session_state:
    st.session_state['usuario'] = 'Admin'

# Conexión a BD
conn = get_connection()

# ============================================================================
# HEADER PROFESIONAL
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
    tabs = st.tabs(["📊 Dashboard", "📄 Contratos", "📤 Cargas", "📈 Resultados", "📚 Maestros", "👥 Admin"])

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
# TÍTULO Y FILTROS
# ============================================================================
# Obtener años disponibles
años = pd.read_sql("""
    SELECT DISTINCT substr(periodo, 1, 4) as año 
    FROM vw_cpm_resultado
    UNION
    SELECT DISTINCT substr(periodo, 1, 4) as año 
    FROM vw_venta
    ORDER BY año DESC
""", conn)['año'].tolist()

title_cols = st.columns([2, 1, 1])

with title_cols[0]:
    st.markdown("## 📊 Panel de Control")
    st.markdown("Resumen global del negocio")

with title_cols[1]:
    año_seleccionado = st.selectbox("Año", años if años else [datetime.now().strftime("%Y")], index=0)

with title_cols[2]:
    # Obtener meses disponibles
    meses = pd.read_sql(f"""
        SELECT DISTINCT periodo 
        FROM vw_cpm_resultado 
        WHERE periodo LIKE '{año_seleccionado}-%'
        ORDER BY periodo
    """, conn)['periodo'].tolist()
    
    opciones_periodo = ["TODOS"] + [m.split('-')[1] for m in meses]
    periodo_seleccionado = st.selectbox("Período", opciones_periodo)

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================================
# CÁLCULOS DE KPIS
# ============================================================================
# Construir filtro de período
if periodo_seleccionado == "TODOS":
    filtro_periodo = f"periodo LIKE '{año_seleccionado}-%'"
else:
    filtro_periodo = f"periodo = '{año_seleccionado}-{periodo_seleccionado}'"

# INGRESOS TOTALES
df_ingresos_cpm = pd.read_sql(f"""
    SELECT COALESCE(SUM(ingresos), 0) as total 
    FROM vw_cpm_resultado 
    WHERE {filtro_periodo}
""", conn)

df_ingresos_venta = pd.read_sql(f"""
    SELECT COALESCE(SUM(ingreso_linea), 0) as total 
    FROM vw_venta 
    WHERE {filtro_periodo}
""", conn)

ingresos_cpm = df_ingresos_cpm['total'].iloc[0]
ingresos_venta = df_ingresos_venta['total'].iloc[0]
ingresos_totales = ingresos_cpm + ingresos_venta

# COSTOS TOTALES
df_costos_cpm = pd.read_sql(f"""
    SELECT 
        COALESCE(SUM(costo_acero), 0) as costo_acero,
        COALESCE(SUM(costo_afiladoras), 0) as costo_afiladoras_cpm
    FROM vw_cpm_resultado
    WHERE {filtro_periodo}
""", conn)

df_costos_venta = pd.read_sql(f"""
    SELECT COALESCE(SUM(costo_linea), 0) as total 
    FROM vw_venta 
    WHERE {filtro_periodo}
""", conn)

df_afiladoras = pd.read_sql(f"""
    SELECT COALESCE(SUM(costo_total), 0) as total 
    FROM vw_afiladoras 
    WHERE {filtro_periodo}
""", conn)

costo_acero_cpm = df_costos_cpm['costo_acero'].iloc[0]
costo_afiladoras_cpm = df_costos_cpm['costo_afiladoras_cpm'].iloc[0]
costo_venta = df_costos_venta['total'].iloc[0]
costo_afiladoras = df_afiladoras['total'].iloc[0]

costos_totales = costo_acero_cpm + costo_afiladoras_cpm + costo_venta + costo_afiladoras
margen_total = ingresos_totales - costos_totales
margen_pct = (1 - costos_totales/ingresos_totales) * 100 if ingresos_totales > 0 else 0

# ============================================================================
# KPIS - TARJETAS DE MÉTRICAS
# ============================================================================
kpi_cols = st.columns(4)

with kpi_cols[0]:
    with st.container(border=True):
        st.markdown("#### 💰 Ingresos")
        st.markdown(f"# ${ingresos_totales:,.0f}")
        st.markdown("📊 Período seleccionado")

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
# GRÁFICO 1: INGRESOS VS COSTOS MENSUAL
# ============================================================================
graf_cols = st.columns(2)

with graf_cols[0]:
    with st.container(border=True):
        st.markdown("### 📈 Ingresos vs Costos - Evolución Mensual")
        
        # Datos mensuales
        df_mensual = pd.read_sql(f"""
            SELECT 
                substr(periodo, 6, 2) as mes,
                SUM(ingresos) as ingresos,
                SUM(costo_acero + costo_afiladoras) as costos_cpm
            FROM vw_cpm_resultado
            WHERE periodo LIKE '{año_seleccionado}-%'
            GROUP BY substr(periodo, 6, 2)
            ORDER BY mes
        """, conn)
        
        if not df_mensual.empty:
            meses_map = {'01': 'Ene', '02': 'Feb', '03': 'Mar', '04': 'Abr', '05': 'May', '06': 'Jun',
                        '07': 'Jul', '08': 'Ago', '09': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dic'}
            
            df_mensual['mes_nombre'] = df_mensual['mes'].map(meses_map)
            
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
                y=df_mensual['costos_cpm'], 
                mode='lines+markers',
                name='Costos', 
                line=dict(color='#ef4444', width=3)
            ))
            
            fig.update_layout(height=350, margin=dict(l=0, r=0, t=20, b=0))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos mensuales para el año seleccionado")

# ============================================================================
# GRÁFICO 2: MÁRGENES POR CONTRATO
# ============================================================================
with graf_cols[1]:
    with st.container(border=True):
        st.markdown("### 📊 Márgenes por Contrato")
        
        # Obtener contratos con margen
        contratos = pd.read_sql("SELECT id, nombre FROM contratos WHERE activo = 1", conn)
        
        datos_contratos = []
        for _, contrato in contratos.iterrows():
            df_ing = pd.read_sql(f"""
                SELECT COALESCE(SUM(ingresos), 0) as ingresos
                FROM vw_cpm_resultado
                WHERE id_contrato = {contrato['id']} AND {filtro_periodo}
            """, conn)
            
            ingresos = df_ing['ingresos'].iloc[0]
            
            if ingresos > 0:
                df_costos = pd.read_sql(f"""
                    SELECT 
                        COALESCE(SUM(costo_acero), 0) as costo_acero,
                        COALESCE(SUM(costo_afiladoras), 0) as costo_afiladoras
                    FROM vw_cpm_resultado
                    WHERE id_contrato = {contrato['id']} AND {filtro_periodo}
                """, conn)
                
                costos = df_costos['costo_acero'].iloc[0] + df_costos['costo_afiladoras'].iloc[0]
                margen = (1 - costos/ingresos) * 100 if ingresos > 0 else 0
                
                datos_contratos.append({
                    'Contrato': contrato['nombre'],
                    'Margen': margen
                })
        
        if datos_contratos:
            df_contratos = pd.DataFrame(datos_contratos)
            df_contratos = df_contratos.sort_values('Margen', ascending=True)
            
            colores = ['#10b981' if m >= 42 else '#f59e0b' if m >= 30 else '#ef4444' 
                      for m in df_contratos['Margen']]
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df_contratos['Margen'],
                y=df_contratos['Contrato'],
                orientation='h',
                marker_color=colores,
                text=df_contratos['Margen'].round(1).astype(str) + '%',
                textposition='outside'
            ))
            fig.add_vline(x=42, line_dash="dash", line_color="green", annotation_text="Objetivo 42%")
            
            fig.update_layout(height=350, margin=dict(l=0, r=0, t=20, b=0))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos de contratos para el período seleccionado")

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================================
# TABLA DE CONTRATOS Y ALERTAS
# ============================================================================
tabla_cols = st.columns([2, 1])

with tabla_cols[0]:
    with st.container(border=True):
        st.markdown("### 📋 Contratos Activos")
        
        # Datos detallados de contratos
        datos_tabla = []
        for _, contrato in contratos.iterrows():
            df_ing = pd.read_sql(f"""
                SELECT 
                    COALESCE(SUM(ingresos), 0) as ingresos,
                    COALESCE(SUM(costo_acero + costo_afiladoras), 0) as costos
                FROM vw_cpm_resultado
                WHERE id_contrato = {contrato['id']} AND {filtro_periodo}
            """, conn)
            
            ingresos = df_ing['ingresos'].iloc[0]
            costos = df_ing['costos'].iloc[0]
            
            if ingresos > 0 or costos > 0:
                margen = (1 - costos/ingresos) * 100 if ingresos > 0 else 0
                
                # Determinar color
                if margen >= 42:
                    estado = "🟢"
                elif margen >= 30:
                    estado = "🟡"
                else:
                    estado = "🔴"
                
                datos_tabla.append({
                    "Contrato": contrato['nombre'],
                    "Ingresos": f"${ingresos:,.0f}",
                    "Margen": f"{margen:.1f}% {estado}"
                })
        
        if datos_tabla:
            df_tabla = pd.DataFrame(datos_tabla)
            st.dataframe(df_tabla, use_container_width=True, hide_index=True)
        else:
            st.info("No hay datos para mostrar")

with tabla_cols[1]:
    with st.container(border=True):
        st.markdown("### ⚠️ Alertas")
        
        # Contratos con margen bajo
        alertas = []
        for _, contrato in contratos.iterrows():
            df_ing = pd.read_sql(f"""
                SELECT 
                    COALESCE(SUM(ingresos), 0) as ingresos,
                    COALESCE(SUM(costo_acero + costo_afiladoras), 0) as costos
                FROM vw_cpm_resultado
                WHERE id_contrato = {contrato['id']} AND {filtro_periodo}
            """, conn)
            
            ingresos = df_ing['ingresos'].iloc[0]
            costos = df_ing['costos'].iloc[0]
            
            if ingresos > 0:
                margen = (1 - costos/ingresos) * 100
                if margen < 30:
                    alertas.append(f"🔴 **{contrato['nombre']}** - Margen: {margen:.1f}%")
                elif margen < 42:
                    alertas.append(f"🟡 **{contrato['nombre']}** - Margen: {margen:.1f}%")
        
        if alertas:
            for alerta in alertas[:5]:  # Mostrar solo 5
                if "🔴" in alerta:
                    st.error(alerta)
                else:
                    st.warning(alerta)
        else:
            st.success("✅ No hay alertas activas")
        
        st.markdown("---")
        st.markdown("### 📤 Últimas Cargas")
        
        # Últimas cargas
        df_ultimas = pd.read_sql("""
            SELECT 
                fecha_carga,
                ct.nombre as contrato,
                tipo_reporte,
                periodo
            FROM control_cargas c
            JOIN contratos ct ON c.id_contrato = ct.id
            ORDER BY fecha_carga DESC
            LIMIT 5
        """, conn)
        
        if not df_ultimas.empty:
            for _, row in df_ultimas.iterrows():
                fecha = pd.to_datetime(row['fecha_carga']).strftime('%d/%m/%Y')
                st.markdown(f"✅ **{row['contrato']}** - {row['tipo_reporte']} {row['periodo']} ({fecha})")
        else:
            st.info("No hay cargas recientes")

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================================
# GRÁFICOS SECUNDARIOS
# ============================================================================
graf2_cols = st.columns(2)

with graf2_cols[0]:
    with st.container(border=True):
        st.markdown("### 📊 Distribución de Ingresos")
        
        # Distribución por tipo
        total_cpm = ingresos_cpm
        total_venta = ingresos_venta
        
        if total_cpm > 0 or total_venta > 0:
            fig = go.Figure(data=[go.Pie(
                labels=['CPM', 'Venta Directa'],
                values=[total_cpm, total_venta],
                hole=0.4,
                marker_colors=['#1152d4', '#f59e0b']
            )])
            fig.update_layout(height=300, margin=dict(l=0, r=0, t=20, b=0))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos de ingresos")

with graf2_cols[1]:
    with st.container(border=True):
        st.markdown("### 📈 Evolución del Margen")
        
        # Evolución mensual del margen
        df_margen_mensual = pd.read_sql(f"""
            SELECT 
                substr(periodo, 6, 2) as mes,
                CASE 
                    WHEN SUM(ingresos) > 0 
                    THEN (1 - SUM(costo_acero + costo_afiladoras)/SUM(ingresos)) * 100
                    ELSE 0
                END as margen
            FROM vw_cpm_resultado
            WHERE periodo LIKE '{año_seleccionado}-%'
            GROUP BY substr(periodo, 6, 2)
            ORDER BY mes
        """, conn)
        
        if not df_margen_mensual.empty:
            meses_map = {'01': 'Ene', '02': 'Feb', '03': 'Mar', '04': 'Abr', '05': 'May', '06': 'Jun',
                        '07': 'Jul', '08': 'Ago', '09': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dic'}
            
            df_margen_mensual['mes_nombre'] = df_margen_mensual['mes'].map(meses_map)
            
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

# ============================================================================
# FOOTER
# ============================================================================
st.divider()
footer_cols = st.columns(3)

with footer_cols[0]:
    st.markdown("© 2024 Rock Tools Peru S.A.")

with footer_cols[1]:
    st.markdown("v2.0.0")

with footer_cols[2]:
    fecha_actual = datetime.now().strftime("%d/%m/%Y")
    st.markdown(f"Última actualización: {fecha_actual}")