import streamlit as st
import pandas as pd
from datetime import datetime, date
from database.conexion import get_connection
import calendar
import plotly.express as px
import plotly.graph_objects as go

# Configuración de la página
st.set_page_config(
    page_title="Rock Tools Peru - Resultados",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Ocultar sidebar
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
    
    /* Estilos para tablas */
    .dataframe {
        font-size: 0.9rem;
    }
    .positive-margin {
        color: #10b981;
        font-weight: 600;
    }
    .negative-margin {
        color: #ef4444;
        font-weight: 600;
    }
            
    .stNumberInput input {
    text-align: center !important;
    }
</style>
""", unsafe_allow_html=True)

# Verificar autenticación
if 'autenticado' not in st.session_state or not st.session_state['autenticado']:
    st.switch_page("app.py")

if 'usuario' not in st.session_state:
    st.session_state['usuario'] = 'Admin'

conn = get_connection()

# Obtener conceptos de gastos
df_conceptos = pd.read_sql("""
    SELECT id, concepto 
    FROM conceptos_gastos 
    WHERE activo = 1 
    ORDER BY concepto
""", conn)
conceptos_lista = df_conceptos.to_dict('records')

# Obtener contratos para usar en tab3 (Liquidación)
contratos_global = pd.read_sql("SELECT id, nombre FROM contratos WHERE activo = 1 ORDER BY nombre", conn)
contrato_opciones = {"TODOS": None}
for _, c in contratos_global.iterrows():
    contrato_opciones[c['nombre']] = c['id']

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
    if st.button("🚪 Salir", key="logout_res", type="secondary", use_container_width=True):
        st.session_state.clear()
        st.switch_page("app.py")

st.divider()

# ============================================================================
# TÍTULO
# ============================================================================
st.markdown("## 📈 Resultados y Proyecciones")
st.markdown("Análisis financiero - Pasado, presente y futuro")

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================================
# PESTAÑAS PRINCIPALES
# ============================================================================

tab1, tab2, tab3 = st.tabs(["📊 ESTADO DE RESULTADOS", "📈 PROYECCIONES", "💵 LIQUIDACIÓN"])


with tab1:
    st.markdown("### 📊 Estado de Resultados (Solo CIERRE)")
    st.caption("Los datos mostrados corresponden únicamente a CIERRE de cada período - valores finales")
    
    # ===== FILTROS =====
    col_f1, col_f2, col_f3 = st.columns(3)
    
    with col_f1:
        años = pd.read_sql("""
            SELECT DISTINCT substr(periodo, 1, 4) as año 
            FROM vw_general_semanal
            WHERE tipo_reporte = 'CIERRE'
            ORDER BY año DESC
        """, conn)['año'].tolist()
        
        año_seleccionado = st.selectbox(
            "📅 Año",
            años if años else [datetime.now().strftime("%Y")],
            key="res_año"
        )
    
    with col_f2:
        periodos_disponibles = pd.read_sql(f"""
            SELECT DISTINCT periodo 
            FROM vw_general_semanal
            WHERE periodo LIKE '{año_seleccionado}-%'
              AND tipo_reporte = 'CIERRE'
            ORDER BY periodo
        """, conn)['periodo'].tolist()
        
        opciones_periodos = ["TODOS"] + periodos_disponibles
        periodos_seleccionados = st.multiselect(
            "📅 Período(s)",
            options=opciones_periodos,
            default=["TODOS"],
            key="res_periodos"
        )
        
        if "TODOS" in periodos_seleccionados:
            periodos_seleccionados = periodos_disponibles
        
        if not periodos_seleccionados:
            st.warning("⚠️ Seleccione al menos un período")
            st.stop()
    
    periodos_str_filtro = "', '".join(periodos_seleccionados)
    
    contratos_con_datos = pd.read_sql(f"""
        SELECT DISTINCT c.id, c.nombre
        FROM contratos c
        INNER JOIN vw_general_semanal v ON c.id = v.id_contrato
        WHERE v.periodo IN ('{periodos_str_filtro}')
          AND v.tipo_reporte = 'CIERRE'
          AND c.activo = 1
        ORDER BY c.nombre
    """, conn)
    
    contrato_opciones_filtradas = {"TODOS": None}
    for _, c in contratos_con_datos.iterrows():
        contrato_opciones_filtradas[c['nombre']] = c['id']
    
    with col_f3:
        contrato_seleccionado = st.selectbox(
            "📋 Contrato",
            list(contrato_opciones_filtradas.keys()),
            key="res_contrato"
        )
        id_contrato = contrato_opciones_filtradas[contrato_seleccionado]
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    periodos_str = "', '".join(periodos_seleccionados)
    filtro_periodo = f"AND periodo IN ('{periodos_str}') AND tipo_reporte = 'CIERRE'"
    
    if id_contrato is None:
        # ===== TODOS LOS CONTRATOS =====
        st.markdown("#### 📊 Resumen General de Todos los Contratos")
        
        datos_generales = []
        total_ingresos_gral = 0
        total_egresos_gral = 0
        
        for _, contrato in contratos_con_datos.iterrows():
            id_contrato_tmp = contrato['id']
            nombre_contrato = contrato['nombre']
            
            clientes_tmp = pd.read_sql(f"""
                SELECT id, nombre, codigo 
                FROM clientes 
                WHERE id_contrato = {id_contrato_tmp} AND activo = 1
            """, conn)
            
            for _, cliente in clientes_tmp.iterrows():
                id_cliente = cliente['id']
                nombre_cliente = cliente['nombre']
                codigo_cliente = cliente['codigo']
                
                df_liq = pd.read_sql(f"""
                    SELECT 
                        SUM(CASE WHEN id_concepto = -1 THEN monto_cobrar ELSE 0 END) as cpm_debo,
                        SUM(CASE WHEN id_concepto = -1 THEN monto_gasto ELSE 0 END) as cpm_gasto,
                        SUM(CASE WHEN id_concepto = -2 THEN monto_cobrar ELSE 0 END) as venta_debo,
                        SUM(CASE WHEN id_concepto = -2 THEN monto_gasto ELSE 0 END) as venta_gasto,
                        SUM(CASE WHEN id_concepto NOT IN (-1, -2) THEN monto_cobrar ELSE 0 END) as conceptos_debo,
                        SUM(CASE WHEN id_concepto NOT IN (-1, -2) THEN monto_gasto ELSE 0 END) as conceptos_gasto,
                        SUM(CASE WHEN id_concepto = -3 THEN monto_gasto ELSE 0 END) as afiladoras_gasto
                    FROM liquidacion_real
                    WHERE id_contrato = {id_contrato_tmp} 
                      AND id_cliente = {id_cliente}
                      AND periodo IN ('{periodos_str}')
                """, conn)
                
                if not df_liq.empty and (df_liq.iloc[0].sum() > 0):
                    cpm_debo = df_liq['cpm_debo'].iloc[0]
                    cpm_gasto = df_liq['cpm_gasto'].iloc[0]
                    venta_debo = df_liq['venta_debo'].iloc[0]
                    venta_gasto = df_liq['venta_gasto'].iloc[0]
                    conceptos_debo = df_liq['conceptos_debo'].iloc[0]
                    conceptos_gasto = df_liq['conceptos_gasto'].iloc[0]
                    afiladoras_gasto = df_liq['afiladoras_gasto'].iloc[0]
                    
                    total_ingresos = cpm_debo + venta_debo + conceptos_debo
                    total_egresos = cpm_gasto + venta_gasto + conceptos_gasto + afiladoras_gasto
                    
                else:
                    df_cpm = pd.read_sql(f"""
                        SELECT COALESCE(SUM(ingresos), 0) as ingresos, COALESCE(SUM(costos), 0) as costos
                        FROM vw_general_semanal
                        WHERE tipo = 'CPM' AND id_contrato = {id_contrato_tmp} AND id_cliente = {id_cliente} {filtro_periodo}
                    """, conn)
                    
                    df_venta = pd.read_sql(f"""
                        SELECT COALESCE(SUM(ingresos), 0) as ingresos, COALESCE(SUM(costos), 0) as costos
                        FROM vw_general_semanal
                        WHERE tipo = 'VENTA' AND id_contrato = {id_contrato_tmp} AND id_cliente = {id_cliente} {filtro_periodo}
                    """, conn)
                    
                    df_afil = pd.read_sql(f"""
                        SELECT COALESCE(SUM(otros_costos), 0) as total
                        FROM vw_general_semanal
                        WHERE tipo = 'AFILADORAS' AND id_contrato = {id_contrato_tmp} AND id_cliente = {id_cliente} {filtro_periodo}
                    """, conn)
                    
                    df_conceptos = pd.read_sql(f"""
                        SELECT 
                            COALESCE(SUM(vd.monto_cobrar_default), 0) as debo,
                            COALESCE(SUM(vd.monto_gasto_default), 0) as gasto
                        FROM conceptos_gastos cg
                        LEFT JOIN valores_por_defecto vd ON vd.id_concepto = cg.id 
                            AND vd.id_contrato = {id_contrato_tmp} 
                            AND vd.id_cliente = {id_cliente}
                        WHERE cg.activo = 1
                    """, conn)
                    
                    total_ingresos = df_cpm['ingresos'].iloc[0] + df_venta['ingresos'].iloc[0] + df_conceptos['debo'].iloc[0]
                    total_egresos = df_cpm['costos'].iloc[0] + df_venta['costos'].iloc[0] + df_afil['total'].iloc[0] + df_conceptos['gasto'].iloc[0]
                
                if total_ingresos > 0 or total_egresos > 0:
                    utilidad = total_ingresos - total_egresos
                    margen = (utilidad / total_ingresos * 100) if total_ingresos > 0 else 0
                    
                    datos_generales.append({
                        'Contrato': nombre_contrato,
                        'Cliente': f"{nombre_cliente} ({codigo_cliente})",
                        'Ingresos': total_ingresos,
                        'Egresos': total_egresos,
                        'Utilidad': utilidad,
                        'Margen %': margen
                    })
                    
                    total_ingresos_gral += total_ingresos
                    total_egresos_gral += total_egresos
        
        utilidad_gral = total_ingresos_gral - total_egresos_gral
        margen_gral = (utilidad_gral / total_ingresos_gral * 100) if total_ingresos_gral > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            with st.container(border=True):
                st.markdown("<div style='text-align: center; font-size: 0.75rem; color: #64748b;'>💰 Total Ingresos</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='text-align: center; font-size: 1.5rem; font-weight: 700; color: #1152d4;'>${total_ingresos_gral:,.0f}</div>", unsafe_allow_html=True)
        with col2:
            with st.container(border=True):
                st.markdown("<div style='text-align: center; font-size: 0.75rem; color: #64748b;'>💸 Total Egresos</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='text-align: center; font-size: 1.5rem; font-weight: 700; color: #ef4444;'>${total_egresos_gral:,.0f}</div>", unsafe_allow_html=True)
        with col3:
            with st.container(border=True):
                st.markdown("<div style='text-align: center; font-size: 0.75rem; color: #64748b;'>📊 Utilidad Neta</div>", unsafe_allow_html=True)
                color = "#10b981" if utilidad_gral > 0 else "#ef4444"
                st.markdown(f"<div style='text-align: center; font-size: 1.5rem; font-weight: 700; color: {color};'>${utilidad_gral:,.0f}</div>", unsafe_allow_html=True)
        with col4:
            with st.container(border=True):
                st.markdown("<div style='text-align: center; font-size: 0.75rem; color: #64748b;'>🎯 Margen %</div>", unsafe_allow_html=True)
                color_m = "#10b981" if margen_gral >= 42 else "#f59e0b" if margen_gral >= 30 else "#ef4444"
                st.markdown(f"<div style='text-align: center; font-size: 1.5rem; font-weight: 700; color: {color_m};'>{margen_gral:.1f}%</div>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if datos_generales:
            st.markdown("#### 📋 Resumen por Cliente")
            df_resumen = pd.DataFrame(datos_generales)
            df_show = df_resumen.copy()
            df_show['Ingresos'] = df_show['Ingresos'].apply(lambda x: f"${x:,.0f}")
            df_show['Egresos'] = df_show['Egresos'].apply(lambda x: f"${x:,.0f}")
            df_show['Utilidad'] = df_show['Utilidad'].apply(lambda x: f"${x:,.0f}")
            df_show['Margen %'] = df_show['Margen %'].apply(lambda x: f"{x:.1f}%")
            
            st.dataframe(df_show, use_container_width=True, hide_index=True)
            
            st.markdown("#### 📈 Márgenes por Contrato")
            df_contratos = df_resumen.groupby('Contrato').agg({
                'Ingresos': 'sum',
                'Egresos': 'sum',
                'Utilidad': 'sum'
            }).reset_index()
            df_contratos['Margen %'] = (df_contratos['Utilidad'] / df_contratos['Ingresos'] * 100).round(1)
            
            fig = px.bar(df_contratos, x='Contrato', y='Margen %', 
                        color='Margen %',
                        color_continuous_scale=['#ef4444', '#f59e0b', '#10b981'],
                        range_color=[0, 50])
            fig.add_hline(y=42, line_dash="dash", line_color="#10b981", annotation_text="Objetivo 42%")
            fig.update_layout(height=400, plot_bgcolor='white', xaxis_title="Contrato", yaxis_title="Margen %")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos para los filtros seleccionados")
    
    else:
        # ===== CONTRATO ESPECÍFICO =====
        info_contrato = pd.read_sql(f"SELECT nombre, tipo_operacion FROM contratos WHERE id = {id_contrato}", conn).iloc[0]
        st.markdown(f"#### 📌 {info_contrato['nombre']} - {info_contrato['tipo_operacion']}")
        
        clientes = pd.read_sql(f"""
            SELECT id, nombre, codigo 
            FROM clientes 
            WHERE id_contrato = {id_contrato} AND activo = 1
            ORDER BY nombre
        """, conn)
        
        if clientes.empty:
            st.warning("No hay clientes para este contrato")
        else:
            total_ingresos_contrato = 0
            total_egresos_contrato = 0
            
            for _, cliente in clientes.iterrows():
                id_cliente = cliente['id']
                nombre_cliente = cliente['nombre']
                codigo_cliente = cliente['codigo']
                
                # ===== VERIFICAR SI EXISTEN VALORES GUARDADOS =====
                df_liq_check = pd.read_sql(f"""
                    SELECT COUNT(*) as total
                    FROM liquidacion_real
                    WHERE id_contrato = {id_contrato} 
                      AND id_cliente = {id_cliente}
                      AND periodo IN ('{periodos_str}')
                """, conn)
                
                tiene_liquidacion = df_liq_check['total'].iloc[0] > 0
                
                if tiene_liquidacion:
                    df_liq = pd.read_sql(f"""
                        SELECT id_concepto, monto_cobrar, monto_gasto
                        FROM liquidacion_real
                        WHERE id_contrato = {id_contrato} 
                          AND id_cliente = {id_cliente}
                          AND periodo IN ('{periodos_str}')
                    """, conn)
                    
                    cobrar_dict = {}
                    gasto_dict = {}
                    for _, row in df_liq.iterrows():
                        cobrar_dict[row['id_concepto']] = row['monto_cobrar']
                        gasto_dict[row['id_concepto']] = row['monto_gasto']
                else:
                    cobrar_dict = {}
                    gasto_dict = {}
                
                # ===== VALORES POR DEFECTO =====
                df_valores_defecto = pd.read_sql(f"""
                    SELECT 
                        cg.id as id_concepto,
                        cg.concepto,
                        COALESCE(vd.monto_cobrar_default, 0) as monto_cobrar_default,
                        COALESCE(vd.monto_gasto_default, 0) as monto_gasto_default
                    FROM conceptos_gastos cg
                    LEFT JOIN valores_por_defecto vd ON vd.id_concepto = cg.id 
                        AND vd.id_contrato = {id_contrato} 
                        AND vd.id_cliente = {id_cliente}
                    WHERE cg.activo = 1
                    ORDER BY cg.concepto
                """, conn)
                
                # ===== CPM, VENTA, AFILADORAS =====
                df_cpm = pd.read_sql(f"""
                    SELECT COALESCE(SUM(ingresos), 0) as ingresos, COALESCE(SUM(costos), 0) as costos
                    FROM vw_general_semanal
                    WHERE tipo = 'CPM' AND id_contrato = {id_contrato} AND id_cliente = {id_cliente} {filtro_periodo}
                """, conn)
                cpm_debo = df_cpm['ingresos'].iloc[0]
                cpm_gasto = df_cpm['costos'].iloc[0]
                
                df_venta = pd.read_sql(f"""
                    SELECT COALESCE(SUM(ingresos), 0) as ingresos, COALESCE(SUM(costos), 0) as costos
                    FROM vw_general_semanal
                    WHERE tipo = 'VENTA' AND id_contrato = {id_contrato} AND id_cliente = {id_cliente} {filtro_periodo}
                """, conn)
                venta_debo = df_venta['ingresos'].iloc[0]
                venta_gasto = df_venta['costos'].iloc[0]
                
                df_afil = pd.read_sql(f"""
                    SELECT COALESCE(SUM(otros_costos), 0) as total
                    FROM vw_general_semanal
                    WHERE tipo = 'AFILADORAS' AND id_contrato = {id_contrato} AND id_cliente = {id_cliente} {filtro_periodo}
                """, conn)
                afiladoras_gasto = df_afil['total'].iloc[0]
                
                with st.expander(f"👤 {nombre_cliente} ({codigo_cliente})", expanded=False):
                    
                    st.markdown("#### 📊 Ingresos vs Gastos")
                    
                    rows_tabla = []
                    
                    # ===== CPM - NO EDITABLE (solo si > 0) =====
                    if cpm_debo > 0 or cpm_gasto > 0:
                        rows_tabla.append({
                            'Concepto': 'CPM',
                            'Debo Cobrar': cpm_debo,
                            'Gasto': cpm_gasto,
                            'es_editable': False,
                            'id_concepto': -1
                        })
                    
                    # ===== VENTA - NO EDITABLE (solo si > 0) =====
                    if venta_debo > 0 or venta_gasto > 0:
                        rows_tabla.append({
                            'Concepto': 'Venta Directa',
                            'Debo Cobrar': venta_debo,
                            'Gasto': venta_gasto,
                            'es_editable': False,
                            'id_concepto': -2
                        })
                    
                    # ===== AFILADORAS - NO EDITABLE (solo si > 0) =====
                    if afiladoras_gasto > 0:
                        rows_tabla.append({
                            'Concepto': 'Afiladoras',
                            'Debo Cobrar': 0,
                            'Gasto': afiladoras_gasto,
                            'es_editable': False,
                            'id_concepto': -3
                        })
                    
                    # ===== OTROS CONCEPTOS - EDITABLES (solo si > 0) =====
                    for _, row in df_valores_defecto.iterrows():
                        id_concepto = row['id_concepto']
                        concepto = row['concepto']
                        
                        debo = cobrar_dict.get(id_concepto, row['monto_cobrar_default'])
                        gasto = gasto_dict.get(id_concepto, row['monto_gasto_default'])
                        
                        if debo > 0 or gasto > 0:
                            rows_tabla.append({
                                'Concepto': concepto,
                                'Debo Cobrar': debo,
                                'Gasto': gasto,
                                'es_editable': True,
                                'id_concepto': id_concepto
                            })
                    
                    if not rows_tabla:
                        st.info("No hay conceptos con valores para este cliente")
                    else:
                        
                        # ===== MOSTRAR TABLA (interfaz mejorada - centrada) =====
                        # Encabezados
                        col1, col2, col3, col4 = st.columns([2, 1.5, 1.5, 1.5])
                        with col1:
                            st.markdown("<div style='text-align: center; font-weight: bold;'>CONCEPTO</div>", unsafe_allow_html=True)
                        with col2:
                            st.markdown("<div style='text-align: center; font-weight: bold;'>INGRESOS</div>", unsafe_allow_html=True)
                        with col3:
                            st.markdown("<div style='text-align: center; font-weight: bold;'>GASTOS</div>", unsafe_allow_html=True)
                        with col4:
                            st.markdown("<div style='text-align: center; font-weight: bold;'>DIFERENCIA</div>", unsafe_allow_html=True)
                        
                        st.markdown("---")
                        
                        for idx, row_item in enumerate(rows_tabla):
                            col1, col2, col3, col4 = st.columns([2, 1.5, 1.5, 1.5])
                            
                            with col1:
                                st.markdown(f"<div style='text-align: center; font-weight: 500;'>{row_item['Concepto'].upper()}</div>", unsafe_allow_html=True)
                            
                            with col2:
                                if row_item['es_editable']:
                                    nuevo_debo = st.number_input(
                                        "Ingresos",
                                        value=float(row_item['Debo Cobrar']),
                                        step=100.0,
                                        format="%.2f",
                                        key=f"res_deb_{row_item['id_concepto']}_{id_cliente}_{str(periodos_seleccionados)}_{idx}",
                                        label_visibility="collapsed"
                                    )
                                    rows_tabla[idx]['Debo Cobrar'] = nuevo_debo
                                else:
                                    st.markdown(f"<div style='text-align: center; font-weight: 500;'>${row_item['Debo Cobrar']:,.0f}</div>", unsafe_allow_html=True)
                            
                            with col3:
                                if row_item['es_editable']:
                                    nuevo_gasto = st.number_input(
                                        "Gastos",
                                        value=float(row_item['Gasto']),
                                        step=100.0,
                                        format="%.2f",
                                        key=f"res_gas_{row_item['id_concepto']}_{id_cliente}_{str(periodos_seleccionados)}_{idx}",
                                        label_visibility="collapsed"
                                    )
                                    rows_tabla[idx]['Gasto'] = nuevo_gasto
                                else:
                                    st.markdown(f"<div style='text-align: center; font-weight: 500;'>${row_item['Gasto']:,.0f}</div>", unsafe_allow_html=True)
                            
                            with col4:
                                diferencia = row_item['Debo Cobrar'] - row_item['Gasto']
                                color = "#10b981" if diferencia >= 0 else "#ef4444"
                                st.markdown(f"<div style='text-align: center; font-weight: bold; color: {color};'>${diferencia:,.0f}</div>", unsafe_allow_html=True)
                        
                        # ===== TOTALES =====
                        total_debo = sum(r['Debo Cobrar'] for r in rows_tabla)
                        total_gasto = sum(r['Gasto'] for r in rows_tabla)
                        total_diferencia = total_debo - total_gasto
                        
                        st.markdown("---")
                        col_t1, col_t2, col_t3 = st.columns(3)
                        with col_t1:
                            with st.container(border=True):
                                st.markdown("<div style='text-align: center; font-size: 0.7rem; color: #64748b;'>💰 TOTAL DEBO COBRAR</div>", unsafe_allow_html=True)
                                st.markdown(f"<div style='text-align: center; font-size: 1.2rem; font-weight: 700;'>${total_debo:,.0f}</div>", unsafe_allow_html=True)
                        with col_t2:
                            with st.container(border=True):
                                st.markdown("<div style='text-align: center; font-size: 0.7rem; color: #64748b;'>💸 TOTAL GASTO</div>", unsafe_allow_html=True)
                                st.markdown(f"<div style='text-align: center; font-size: 1.2rem; font-weight: 700;'>${total_gasto:,.0f}</div>", unsafe_allow_html=True)
                        with col_t3:
                            with st.container(border=True):
                                st.markdown("<div style='text-align: center; font-size: 0.7rem; color: #64748b;'>📊 DIFERENCIA</div>", unsafe_allow_html=True)
                                color = "#10b981" if total_diferencia >= 0 else "#ef4444"
                                st.markdown(f"<div style='text-align: center; font-size: 1.2rem; font-weight: 700; color: {color};'>${total_diferencia:,.0f}</div>", unsafe_allow_html=True)
                        
                        # ===== GUARDAR (solo conceptos editables) =====
                        if any(r['es_editable'] for r in rows_tabla):
                            if st.button("💾 Guardar Cambios", key=f"res_guardar_{id_cliente}_{str(periodos_seleccionados)}"):
                                try:
                                    cursor = conn.cursor()
                                    for row_item in rows_tabla:
                                        if row_item['es_editable']:
                                            id_concepto = row_item['id_concepto']
                                            nuevo_debo = row_item['Debo Cobrar']
                                            nuevo_gasto = row_item['Gasto']
                                            
                                            for periodo in periodos_seleccionados:
                                                cursor.execute("""
                                                    SELECT id FROM liquidacion_real 
                                                    WHERE id_contrato = ? AND id_cliente = ? 
                                                    AND id_concepto = ? AND periodo = ?
                                                """, (id_contrato, id_cliente, id_concepto, periodo))
                                                
                                                existe = cursor.fetchone()
                                                
                                                if existe:
                                                    cursor.execute("""
                                                        UPDATE liquidacion_real 
                                                        SET monto_cobrar = ?, monto_gasto = ?
                                                        WHERE id_contrato = ? AND id_cliente = ? 
                                                        AND id_concepto = ? AND periodo = ?
                                                    """, (nuevo_debo, nuevo_gasto, id_contrato, id_cliente, id_concepto, periodo))
                                                else:
                                                    cursor.execute("""
                                                        INSERT INTO liquidacion_real 
                                                        (id_contrato, id_cliente, id_concepto, periodo, monto_cobrar, monto_gasto)
                                                        VALUES (?, ?, ?, ?, ?, ?)
                                                    """, (id_contrato, id_cliente, id_concepto, periodo, nuevo_debo, nuevo_gasto))
                                    
                                    conn.commit()
                                    st.success(f"✅ Cambios guardados correctamente para {len(periodos_seleccionados)} período(s)")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error al guardar: {str(e)}")
                        
                        total_ingresos_contrato += total_debo
                        total_egresos_contrato += total_gasto
            
            # ===== TOTALES DEL CONTRATO =====
            if total_ingresos_contrato > 0 or total_egresos_contrato > 0:
                st.markdown("#### 📊 Totales del Contrato")
                utilidad_contrato = total_ingresos_contrato - total_egresos_contrato
                margen_contrato = (utilidad_contrato / total_ingresos_contrato * 100) if total_ingresos_contrato > 0 else 0
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    with st.container(border=True):
                        st.markdown("<div style='text-align: center; font-size: 0.75rem; color: #64748b;'>💰 Total Ingresos</div>", unsafe_allow_html=True)
                        st.markdown(f"<div style='text-align: center; font-size: 1.3rem; font-weight: 700; color: #1152d4;'>${total_ingresos_contrato:,.0f}</div>", unsafe_allow_html=True)
                with col2:
                    with st.container(border=True):
                        st.markdown("<div style='text-align: center; font-size: 0.75rem; color: #64748b;'>💸 Total Egresos</div>", unsafe_allow_html=True)
                        st.markdown(f"<div style='text-align: center; font-size: 1.3rem; font-weight: 700; color: #ef4444;'>${total_egresos_contrato:,.0f}</div>", unsafe_allow_html=True)
                with col3:
                    with st.container(border=True):
                        st.markdown("<div style='text-align: center; font-size: 0.75rem; color: #64748b;'>📊 Utilidad</div>", unsafe_allow_html=True)
                        color = "#10b981" if utilidad_contrato > 0 else "#ef4444"
                        st.markdown(f"<div style='text-align: center; font-size: 1.3rem; font-weight: 700; color: {color};'>${utilidad_contrato:,.0f}</div>", unsafe_allow_html=True)
                with col4:
                    with st.container(border=True):
                        st.markdown("<div style='text-align: center; font-size: 0.75rem; color: #64748b;'>🎯 Margen %</div>", unsafe_allow_html=True)
                        color_m = "#10b981" if margen_contrato >= 42 else "#f59e0b" if margen_contrato >= 30 else "#ef4444"
                        st.markdown(f"<div style='text-align: center; font-size: 1.3rem; font-weight: 700; color: {color_m};'>{margen_contrato:.1f}%</div>", unsafe_allow_html=True)

with tab2:
    st.markdown("### 📈 Proyecciones por Contrato (Solo CPM)")
    st.caption("Proyección basada en datos AVANCE del período seleccionado")
    
    # ===== PASO 1: PRIMERO SELECCIONAR PERÍODO =====
    col_p1, col_p2 = st.columns(2)
    
    with col_p1:
        # Obtener períodos disponibles (solo AVANCE)
        periodos_proy = pd.read_sql("""
            SELECT DISTINCT periodo 
            FROM vw_general_semanal
            WHERE tipo = 'CPM'
              AND tipo_reporte = 'AVANCE'
            ORDER BY periodo DESC
        """, conn)['periodo'].tolist()
        
        if not periodos_proy:
            periodos_proy = [datetime.now().strftime("%Y-%m")]
        
        periodo_proy = st.selectbox(
            "📅 Período (AVANCE)",
            periodos_proy,
            key="proy_periodo"
        )
    
    # ===== PASO 2: CONTRATOS QUE TIENEN DATOS EN ESE PERÍODO =====
    if periodo_proy:
        contratos_con_datos_proy = pd.read_sql(f"""
            SELECT DISTINCT c.id, c.nombre
            FROM contratos c
            INNER JOIN vw_general_semanal v ON c.id = v.id_contrato
            WHERE v.periodo = '{periodo_proy}'
              AND v.tipo = 'CPM'
              AND v.tipo_reporte = 'AVANCE'
              AND c.activo = 1
            ORDER BY c.nombre
        """, conn)
        
        contratos_proy_opciones = [c['nombre'] for c in contratos_con_datos_proy.to_dict('records')]
        
        if not contratos_proy_opciones:
            st.warning(f"⚠️ No hay contratos con datos AVANCE en {periodo_proy}")
            st.stop()
    
    with col_p2:
        proy_contrato = st.selectbox(
            "📋 Contrato",
            contratos_proy_opciones,
            key="proy_contrato"
        )
        id_proy_contrato = contratos_con_datos_proy[contratos_con_datos_proy['nombre'] == proy_contrato]['id'].iloc[0]
    
    # ===== CLIENTES =====
    proy_clientes = pd.read_sql(f"""
        SELECT id, nombre, codigo 
        FROM clientes 
        WHERE id_contrato = {id_proy_contrato} AND activo = 1
        ORDER BY nombre
    """, conn)
    
    col_c1, col_c2 = st.columns(2)
    
    with col_c1:
        proy_cliente_opciones = {"TODOS": None}
        for _, row in proy_clientes.iterrows():
            proy_cliente_opciones[f"{row['nombre']} ({row['codigo']})"] = row['id']
        
        proy_cliente = st.selectbox(
            "👤 Cliente",
            list(proy_cliente_opciones.keys()),
            key="proy_cliente"
        )
        id_proy_cliente = proy_cliente_opciones[proy_cliente]
    
    with col_c2:
        st.info(f"📅 Período seleccionado: **{periodo_proy}** | Contrato: **{proy_contrato}**")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Verificar que hay período seleccionado
    if not periodo_proy:
        st.warning("⚠️ Seleccione un período")
        st.stop()
    
    try:
        año, mes = map(int, periodo_proy.split('-'))
        dias_totales_mes = calendar.monthrange(año, mes)[1]
    except:
        st.error("Período inválido")
        st.stop()
    
    # ===== CONSTRUIR FILTROS =====
    filtro_cliente = f"AND id_cliente = {id_proy_cliente}" if id_proy_cliente else ""
    filtro_periodo = f"AND periodo = '{periodo_proy}' AND tipo_reporte = 'AVANCE'"
    
    # ===== OBTENER DATOS DE PERFORACIÓN (metros) =====
    query_perforacion = f"""
        SELECT 
            semana,
            SUM(total_mp) as metros
        FROM perforacion_general pg
        JOIN perforacion_detalle pd ON pg.id = pd.id_perforacion_general
        WHERE pg.id_contrato = {id_proy_contrato}
          AND pg.periodo = '{periodo_proy}'
          AND pg.tipo_operacion = 'CPM'
          AND pg.tipo_reporte = 'AVANCE'
          {filtro_cliente}
        GROUP BY pg.semana
        ORDER BY pg.semana
    """
    
    df_perf = pd.read_sql(query_perforacion, conn)
    
    if df_perf.empty:
        st.warning(f"No hay datos de AVANCE para {periodo_proy}")
        st.info("Para proyectar se necesitan datos de AVANCE con fechas")
    else:
        # ===== OBTENER COSTOS DE ACERO =====
        query_costos = f"""
            SELECT 
                ag.semana,
                SUM(ad.cantidad * ca.precio_rtperu) as costo_total
            FROM acero_general ag
            JOIN acero_detalle ad ON ag.id = ad.id_acero_general
            LEFT JOIN costos ca ON ad.codigo = ca.codigo
            WHERE ag.id_contrato = {id_proy_contrato}
              AND ag.periodo = '{periodo_proy}'
              AND ag.tipo_operacion = 'CPM'
              AND ag.tipo_reporte = 'AVANCE'
              {filtro_cliente}
            GROUP BY ag.semana
            ORDER BY ag.semana
        """
        
        df_costos = pd.read_sql(query_costos, conn)
        
        # ===== OBTENER TARIFA POR METRO =====
        try:
            query_tarifa = f"""
                SELECT tarifa
                FROM tarifas
                WHERE id_contrato = {id_proy_contrato}
                  AND (id_cliente = {id_proy_cliente if id_proy_cliente else 'NULL'} OR id_cliente IS NULL)
                  AND periodo_desde <= '{periodo_proy}'
                  AND (periodo_hasta >= '{periodo_proy}' OR periodo_hasta IS NULL)
                ORDER BY id_cliente DESC
                LIMIT 1
            """
            df_tarifa = pd.read_sql(query_tarifa, conn)
            tarifa_por_metro = df_tarifa['tarifa'].iloc[0] if not df_tarifa.empty else 0
        except:
            tarifa_por_metro = 0
        
        # ===== OBTENER FECHAS POR SEMANA =====
        query_fechas = f"""
            SELECT 
                semana,
                MIN(fecha_inicio) as fecha_inicio,
                MAX(fecha_fin) as fecha_fin
            FROM perforacion_general
            WHERE id_contrato = {id_proy_contrato}
              AND periodo = '{periodo_proy}'
              AND tipo_operacion = 'CPM'
              AND tipo_reporte = 'AVANCE'
              AND fecha_inicio IS NOT NULL
              AND fecha_fin IS NOT NULL
              {filtro_cliente}
            GROUP BY semana
            ORDER BY semana
        """
        df_fechas = pd.read_sql(query_fechas, conn)
        
        # ===== CREAR DICCIONARIOS =====
        metros_dict = {}
        for _, row in df_perf.iterrows():
            metros_dict[row['semana']] = row['metros']
        
        costos_dict = {}
        for _, row in df_costos.iterrows():
            costos_dict[row['semana']] = row['costo_total']
        
        fechas_dict = {}
        for _, row in df_fechas.iterrows():
            fechas_dict[row['semana']] = {
                'inicio': pd.to_datetime(row['fecha_inicio']).date(),
                'fin': pd.to_datetime(row['fecha_fin']).date()
            }
        
        # ===== OBTENER SEMANAS DISPONIBLES =====
        semanas_disponibles = sorted(set(metros_dict.keys()) | set(costos_dict.keys()))
        
        if not semanas_disponibles:
            st.warning("No hay datos disponibles para la proyección")
        else:
            # ===== CALCULAR PROYECCIÓN =====
            datos_semanales = []
            metros_acum = 0
            costo_acum = 0
            dias_acum = 0
            ultima_fecha_fin = None
            
            for semana in sorted(semanas_disponibles):
                metros_semana = metros_dict.get(semana, 0)
                costo_semana = costos_dict.get(semana, 0)
                
                # Obtener fechas de la semana
                if semana in fechas_dict:
                    fecha_inicio = fechas_dict[semana]['inicio']
                    fecha_fin = fechas_dict[semana]['fin']
                    
                    if ultima_fecha_fin is None:
                        dias_semana = (fecha_fin - fecha_inicio).days + 1
                        dias_acum = dias_semana
                    else:
                        dias_semana = (fecha_fin - ultima_fecha_fin).days
                        dias_acum += dias_semana
                    
                    ultima_fecha_fin = fecha_fin
                else:
                    dias_semana = 7
                    dias_acum += dias_semana
                
                metros_acum += metros_semana
                costo_acum += costo_semana
                ingreso_acum = metros_acum * tarifa_por_metro
                ganancia_acum = ingreso_acum - costo_acum
                margen_acum = (ganancia_acum / ingreso_acum * 100) if ingreso_acum > 0 else 0
                
                dias_restantes = dias_totales_mes - dias_acum
                
                if dias_acum > 0 and dias_restantes > 0:
                    rendimiento_diario = metros_acum / dias_acum
                    costo_diario = costo_acum / dias_acum
                    
                    metros_proy = metros_acum + (rendimiento_diario * dias_restantes)
                    costo_proy = costo_acum + (costo_diario * dias_restantes)
                    ingreso_proy = metros_proy * tarifa_por_metro
                    ganancia_proy = ingreso_proy - costo_proy
                    margen_proy = (ganancia_proy / ingreso_proy * 100) if ingreso_proy > 0 else 0
                else:
                    metros_proy = metros_acum
                    costo_proy = costo_acum
                    ingreso_proy = ingreso_acum
                    ganancia_proy = ganancia_acum
                    margen_proy = margen_acum
                
                datos_semanales.append({
                    'Semana': semana,
                    'Metros': metros_acum,
                    'Ingresos': ingreso_acum,
                    'Costos': costo_acum,
                    'Ganancia': ganancia_acum,
                    'Margen %': margen_acum,
                    'Metros_Proy': metros_proy,
                    'Ingresos_Proy': ingreso_proy,
                    'Costos_Proy': costo_proy,
                    'Ganancia_Proy': ganancia_proy,
                    'Margen_Proy_%': margen_proy
                })
            
            # ===== MOSTRAR TABLA =====
            st.markdown("#### 📋 Proyección por Semana")
            
            df_show = pd.DataFrame(datos_semanales)
            
            df_formateado = df_show[['Semana', 'Ingresos', 'Costos', 'Ganancia', 'Margen %', 
                                      'Ingresos_Proy', 'Costos_Proy', 'Ganancia_Proy', 'Margen_Proy_%']].copy()
            
            for col in ['Ingresos', 'Costos', 'Ganancia', 'Ingresos_Proy', 'Costos_Proy', 'Ganancia_Proy']:
                df_formateado[col] = df_formateado[col].apply(lambda x: f"${x:,.0f}")
            
            df_formateado['Margen %'] = df_formateado['Margen %'].apply(lambda x: f"{x:.1f}%")
            df_formateado['Margen_Proy_%'] = df_formateado['Margen_Proy_%'].apply(lambda x: f"{x:.1f}%")
            
            df_formateado.columns = ['Sem', 'Ingresos', 'Costos', 'Ganancia', 'Margen',
                                      'Ingresos Proy', 'Costos Proy', 'Ganancia Proy', 'Margen Proy']
            
            st.dataframe(
                df_formateado.style.set_properties(**{
                    'text-align': 'center',
                    'border': '1px solid #e5e7eb',
                    'padding': '8px'
                }).set_table_styles([
                    {'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#f3f4f6'), ('color', '#374151'), ('font-weight', '600')]}
                ]),
                use_container_width=True,
                hide_index=True
            )
            
            # ===== GRÁFICO DE EVOLUCIÓN =====
            st.markdown("#### 📊 Evolución: Actual vs Proyectado")
            
            semanas_labels = [f"S{int(s)}" for s in df_show['Semana']]
            semanas_labels.append('Proy')
            
            ingresos_vals = list(df_show['Ingresos']) + [df_show['Ingresos_Proy'].iloc[-1]]
            costos_vals = list(df_show['Costos']) + [df_show['Costos_Proy'].iloc[-1]]
            ganancia_vals = list(df_show['Ganancia']) + [df_show['Ganancia_Proy'].iloc[-1]]
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=semanas_labels,
                y=ingresos_vals,
                mode='lines+markers',
                name='Ingresos',
                line=dict(color='#1152d4', width=3),
                marker=dict(size=8)
            ))
            
            fig.add_trace(go.Scatter(
                x=semanas_labels,
                y=costos_vals,
                mode='lines+markers',
                name='Costos',
                line=dict(color='#ef4444', width=3),
                marker=dict(size=8)
            ))
            
            fig.add_trace(go.Scatter(
                x=semanas_labels,
                y=ganancia_vals,
                mode='lines+markers',
                name='Ganancia',
                line=dict(color='#10b981', width=3),
                marker=dict(size=8)
            ))
            
            fig.update_layout(
                title=f"Proyección {periodo_proy} - {proy_contrato}",
                xaxis_title="Semana",
                yaxis_title="Monto ($)",
                height=450,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # ===== RESUMEN FINAL =====
            st.markdown("#### 🎯 Resumen Proyectado a Fin de Mes")
            
            ultimo = datos_semanales[-1]
            
            col_r1, col_r2, col_r3, col_r4 = st.columns(4)
            with col_r1:
                with st.container(border=True):
                    st.markdown("<div style='text-align: center;'>💰 Ingresos</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='text-align: center; font-size: 1.3rem; font-weight: 700;'>${ultimo['Ingresos_Proy']:,.0f}</div>", unsafe_allow_html=True)
            with col_r2:
                with st.container(border=True):
                    st.markdown("<div style='text-align: center;'>💸 Costos</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='text-align: center; font-size: 1.3rem; font-weight: 700;'>${ultimo['Costos_Proy']:,.0f}</div>", unsafe_allow_html=True)
            with col_r3:
                with st.container(border=True):
                    st.markdown("<div style='text-align: center;'>📊 Ganancia</div>", unsafe_allow_html=True)
                    color = "#10b981" if ultimo['Ganancia_Proy'] > 0 else "#ef4444"
                    st.markdown(f"<div style='text-align: center; font-size: 1.3rem; font-weight: 700; color: {color};'>${ultimo['Ganancia_Proy']:,.0f}</div>", unsafe_allow_html=True)
            with col_r4:
                with st.container(border=True):
                    st.markdown("<div style='text-align: center;'>🎯 Margen</div>", unsafe_allow_html=True)
                    color = "#10b981" if ultimo['Margen_Proy_%'] >= 42 else "#f59e0b" if ultimo['Margen_Proy_%'] >= 30 else "#ef4444"
                    st.markdown(f"<div style='text-align: center; font-size: 1.3rem; font-weight: 700; color: {color};'>{ultimo['Margen_Proy_%']:.1f}%</div>", unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            with col_m1:
                st.metric("Metros Proyectados", f"{ultimo['Metros_Proy']:,.0f} m")
            with col_m2:
                st.metric("Tarifa por Metro", f"${tarifa_por_metro:,.2f}")
            with col_m3:
                st.metric("Días Restantes", f"{dias_restantes} días")
            with col_m4:
                st.metric("Rendimiento Diario", f"{rendimiento_diario:.1f} m/día")


with tab3:
    st.markdown("### 💵 Liquidación")
    st.markdown("Control de cobros: Lo que VALORIZA la mina vs lo que HES/LIQUIDA (Solo datos de CIERRE)")
    
    # ===== FILTROS COMPACTOS =====
    col_l1, col_l2, col_l3, col_l4 = st.columns([2, 2, 2, 1])
    
    with col_l1:
        años = pd.read_sql("""
            SELECT DISTINCT substr(periodo, 1, 4) as año 
            FROM vw_general_semanal
            WHERE tipo_reporte = 'CIERRE'
            ORDER BY año DESC
        """, conn)['año'].tolist()
        
        año_liquidacion = st.selectbox(
            "📅 Año",
            años if años else [datetime.now().strftime("%Y")],
            key="liq_año"
        )
    
    with col_l2:
        periodos_liq = pd.read_sql(f"""
            SELECT DISTINCT periodo 
            FROM vw_general_semanal
            WHERE periodo LIKE '{año_liquidacion}-%'
              AND tipo_reporte = 'CIERRE'
            ORDER BY periodo
        """, conn)['periodo'].tolist()
        
        opciones_periodo_liq = ["TODOS"] + periodos_liq
        periodo_liq = st.selectbox("📅 Período", opciones_periodo_liq, key="liq_periodo")
        periodo_liq = None if periodo_liq == "TODOS" else periodo_liq
    
    with col_l3:
        contrato_liq = st.selectbox(
            "📋 Contrato",
            list(contrato_opciones.keys()),
            key="liq_contrato"
        )
        id_contrato_liq = contrato_opciones[contrato_liq] if contrato_liq != "TODOS" else None
    
    with col_l4:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Actualizar", key="btn_actualizar_liq", use_container_width=True):
            st.rerun()
    
    st.markdown("---")
    
    # ===== VALIDACIÓN =====
    if periodo_liq is None:
        st.warning("⚠️ **Selecciona un período específico** (no 'TODOS') para ver la liquidación")
        st.info("La liquidación requiere un período concreto para poder editar los montos pagados.")
        st.stop()
    
    if id_contrato_liq is None:
        st.warning("⚠️ **Selecciona un contrato específico** (no 'TODOS') para ver la liquidación")
        st.info("La liquidación requiere un contrato específico para poder editar los montos pagados.")
        st.stop()
    
    # ===== CONSTRUIR FILTROS =====
    filtro_periodo_liq = f"AND periodo = '{periodo_liq}' AND tipo_reporte = 'CIERRE'"
    
    # ===== INFORMACIÓN DEL CONTRATO =====
    info_contrato_liq = pd.read_sql(f"SELECT nombre FROM contratos WHERE id = {id_contrato_liq}", conn).iloc[0]
    st.markdown(f"#### 📌 {info_contrato_liq['nombre']} - Período: {periodo_liq}")
    
    # ===== CLIENTES =====
    clientes_liq = pd.read_sql(f"""
        SELECT id, nombre, codigo 
        FROM clientes 
        WHERE id_contrato = {id_contrato_liq} AND activo = 1
        ORDER BY nombre
    """, conn)
    
    if clientes_liq.empty:
        st.warning("No hay clientes para este contrato")
        st.stop()
    
    # ===== INICIALIZAR TOTALES GENERALES =====
    total_general_valorizacion = 0
    total_general_hes = 0
    total_general_diferencia = 0
    
    for _, cliente in clientes_liq.iterrows():
        id_cliente = cliente['id']
        nombre_cliente = cliente['nombre']
        codigo_cliente = cliente['codigo']
        
        with st.expander(f"👤 {nombre_cliente} ({codigo_cliente})", expanded=False):
            
            # ===== OBTENER VALORIZACIÓN MINA (de vw_general_semanal) =====
            df_cpm_liq = pd.read_sql(f"""
                SELECT COALESCE(SUM(ingresos), 0) as total
                FROM vw_general_semanal
                WHERE tipo = 'CPM'
                  AND id_contrato = {id_contrato_liq}
                  AND id_cliente = {id_cliente}
                  {filtro_periodo_liq}
            """, conn)
            debo_cpm = df_cpm_liq['total'].iloc[0]
            
            df_venta_liq = pd.read_sql(f"""
                SELECT COALESCE(SUM(ingresos), 0) as total
                FROM vw_general_semanal
                WHERE tipo = 'VENTA'
                  AND id_contrato = {id_contrato_liq}
                  AND id_cliente = {id_cliente}
                  {filtro_periodo_liq}
            """, conn)
            debo_venta = df_venta_liq['total'].iloc[0]
            
            # ===== VALORES POR DEFECTO DE CONCEPTOS (solo los que tienen valor > 0) =====
            df_conceptos_liq = pd.read_sql(f"""
                SELECT 
                    cg.id as id_concepto,
                    cg.concepto,
                    COALESCE(vd.monto_cobrar_default, 0) as debo_default
                FROM conceptos_gastos cg
                LEFT JOIN valores_por_defecto vd ON vd.id_concepto = cg.id 
                    AND vd.id_contrato = {id_contrato_liq} 
                    AND vd.id_cliente = {id_cliente}
                WHERE cg.activo = 1
                  AND COALESCE(vd.monto_cobrar_default, 0) > 0
                ORDER BY cg.concepto
            """, conn)
            
            # ===== VALORES REALES PAGADOS (HES/LIQUIDACIÓN) =====
            df_pagado_real = pd.read_sql(f"""
                SELECT id_concepto, monto_cobrado
                FROM liquidacion_real
                WHERE id_contrato = {id_contrato_liq} 
                  AND id_cliente = {id_cliente}
                  AND periodo = '{periodo_liq}'
            """, conn)
            
            pagado_dict = {}
            for _, row in df_pagado_real.iterrows():
                pagado_dict[row['id_concepto']] = row['monto_cobrado']
            
            # ===== CONSTRUIR TABLA (solo conceptos con Valorización Mina > 0) =====
            rows_liq = []
            
            # CPM
            if debo_cpm > 0:
                rows_liq.append({
                    'Concepto': 'CPM',
                    'Valorizacion Mina': debo_cpm,
                    'HES/Liquidacion': pagado_dict.get(-1, 0),
                    'id_concepto': -1
                })
            
            # Venta Directa
            if debo_venta > 0:
                rows_liq.append({
                    'Concepto': 'Venta Directa',
                    'Valorizacion Mina': debo_venta,
                    'HES/Liquidacion': pagado_dict.get(-2, 0),
                    'id_concepto': -2
                })
            
            # Conceptos dinámicos
            for _, row in df_conceptos_liq.iterrows():
                id_concepto = row['id_concepto']
                debo = row['debo_default']
                
                if debo > 0:
                    rows_liq.append({
                        'Concepto': row['concepto'].upper(),
                        'Valorizacion Mina': debo,
                        'HES/Liquidacion': pagado_dict.get(id_concepto, 0),
                        'id_concepto': id_concepto
                    })
            
            if not rows_liq:
                st.info("No hay conceptos con valores para este cliente")
                continue
            
            # ===== MOSTRAR TABLA =====
            st.markdown("#### 💵 Liquidación por Concepto")
            
            # Encabezados
            col1, col2, col3, col4, col5 = st.columns([2, 1.8, 1.8, 1.5, 1.5])
            with col1:
                st.markdown("<div style='text-align: center; font-weight: bold;'>CONCEPTO</div>", unsafe_allow_html=True)
            with col2:
                st.markdown("<div style='text-align: center; font-weight: bold;'>VALORIZACIÓN MINA</div>", unsafe_allow_html=True)
            with col3:
                st.markdown("<div style='text-align: center; font-weight: bold;'>HES/LIQUIDACIÓN</div>", unsafe_allow_html=True)
            with col4:
                st.markdown("<div style='text-align: center; font-weight: bold;'>DIFERENCIA</div>", unsafe_allow_html=True)
            with col5:
                st.markdown("<div style='text-align: center; font-weight: bold;'>ESTADO</div>", unsafe_allow_html=True)
            
            st.markdown("---")
            
            for idx, row_item in enumerate(rows_liq):
                col1, col2, col3, col4, col5 = st.columns([2, 1.8, 1.8, 1.5, 1.5])
                
                with col1:
                    st.markdown(f"<div style='text-align: center;'>{row_item['Concepto']}</div>", unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"<div style='text-align: right; font-weight: 500;'>${row_item['Valorizacion Mina']:,.0f}</div>", unsafe_allow_html=True)
                
                with col3:
                    nuevo_pagaron = st.number_input(
                        "HES/Liquidacion",
                        value=float(row_item['HES/Liquidacion']),
                        step=100.0,
                        format="%.2f",
                        key=f"liq_pag_{row_item['id_concepto']}_{id_cliente}_{periodo_liq}_{idx}",
                        label_visibility="collapsed"
                    )
                    rows_liq[idx]['HES/Liquidacion'] = nuevo_pagaron
                    diferencia = row_item['Valorizacion Mina'] - nuevo_pagaron
                    rows_liq[idx]['Diferencia'] = diferencia
                
                with col4:
                    diferencia = rows_liq[idx]['Diferencia']
                    if abs(diferencia) <= 5:
                        color = "#10b981"
                    elif diferencia < 0:
                        color = "#f59e0b"
                    else:
                        color = "#ef4444"
                    st.markdown(f"<div style='text-align: right; font-weight: bold; color: {color};'>${diferencia:,.0f}</div>", unsafe_allow_html=True)
                
                with col5:
                    diferencia = rows_liq[idx]['Diferencia']
                    if abs(diferencia) <= 5:
                        st.markdown("<div style='text-align: center; color: #10b981; font-weight: bold;'>✅ CONFORME</div>", unsafe_allow_html=True)
                    elif diferencia < 0:
                        st.markdown("<div style='text-align: center; color: #f59e0b; font-weight: bold;'>⚠️ EXCESO</div>", unsafe_allow_html=True)
                    else:
                        st.markdown("<div style='text-align: center; color: #ef4444; font-weight: bold;'>🔴 PENDIENTE</div>", unsafe_allow_html=True)
            
            # ===== SUBTOTALES Y TOTALES CON IGV =====
            subtotal_valorizacion = sum(r['Valorizacion Mina'] for r in rows_liq)
            subtotal_hes = sum(r['HES/Liquidacion'] for r in rows_liq)
            diferencia_subtotal = subtotal_valorizacion - subtotal_hes
            
            igv_valorizacion = subtotal_valorizacion * 0.18
            igv_hes = subtotal_hes * 0.18
            
            total_valorizacion = subtotal_valorizacion + igv_valorizacion
            total_hes = subtotal_hes + igv_hes
            diferencia_total = total_valorizacion - total_hes
            
            st.markdown("---")
            
            # Fila de SUBTOTAL
            col_s1, col_s2, col_s3, col_s4 = st.columns([2, 1.8, 1.8, 1.5])
            with col_s1:
                st.markdown("<div style='text-align: center; font-weight: bold;'>SUBTOTAL</div>", unsafe_allow_html=True)
            with col_s2:
                st.markdown(f"<div style='text-align: right; font-weight: bold;'>${subtotal_valorizacion:,.0f}</div>", unsafe_allow_html=True)
            with col_s3:
                st.markdown(f"<div style='text-align: right; font-weight: bold;'>${subtotal_hes:,.0f}</div>", unsafe_allow_html=True)
            with col_s4:
                diferencia_color = "#10b981" if diferencia_subtotal >= 0 else "#ef4444"
                st.markdown(f"<div style='text-align: right; font-weight: bold; color: {diferencia_color};'>${diferencia_subtotal:,.0f}</div>", unsafe_allow_html=True)
            
            # Fila de IGV
            col_i1, col_i2, col_i3, col_i4 = st.columns([2, 1.8, 1.8, 1.5])
            with col_i1:
                st.markdown("<div style='text-align: center; font-weight: bold;'>IGV (18%)</div>", unsafe_allow_html=True)
            with col_i2:
                st.markdown(f"<div style='text-align: right; font-weight: bold;'>${igv_valorizacion:,.0f}</div>", unsafe_allow_html=True)
            with col_i3:
                st.markdown(f"<div style='text-align: right; font-weight: bold;'>${igv_hes:,.0f}</div>", unsafe_allow_html=True)
            with col_i4:
                st.markdown("", unsafe_allow_html=True)
            
            # Fila de TOTAL
            col_t1, col_t2, col_t3, col_t4 = st.columns([2, 1.8, 1.8, 1.5])
            with col_t1:
                st.markdown("<div style='text-align: center; font-weight: bold;'>TOTAL</div>", unsafe_allow_html=True)
            with col_t2:
                st.markdown(f"<div style='text-align: right; font-weight: bold;'>${total_valorizacion:,.0f}</div>", unsafe_allow_html=True)
            with col_t3:
                st.markdown(f"<div style='text-align: right; font-weight: bold;'>${total_hes:,.0f}</div>", unsafe_allow_html=True)
            with col_t4:
                diferencia_total_color = "#10b981" if diferencia_total >= 0 else "#ef4444"
                st.markdown(f"<div style='text-align: right; font-weight: bold; color: {diferencia_total_color};'>${diferencia_total:,.0f}</div>", unsafe_allow_html=True)
            
            # Estado final
            st.markdown("---")
            if abs(diferencia_total) <= 5:
                st.markdown("<div style='text-align: center; color: #10b981; font-weight: bold; font-size: 1.2rem;'>✅ TOTAL CONFORME - DIFERENCIA ACEPTABLE</div>", unsafe_allow_html=True)
            elif diferencia_total < 0:
                st.markdown("<div style='text-align: center; color: #f59e0b; font-weight: bold; font-size: 1.2rem;'>⚠️ EXCESO EN PAGO - REVISAR</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div style='text-align: center; color: #ef4444; font-weight: bold; font-size: 1.2rem;'>🔴 PENDIENTE DE PAGO</div>", unsafe_allow_html=True)
            
            # ===== BOTONES =====
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                if st.button("💾 Guardar Liquidación", key=f"guardar_liq_{id_cliente}_{periodo_liq}", use_container_width=True):
                    try:
                        cursor = conn.cursor()
                        guardados = 0
                        
                        for row_item in rows_liq:
                            id_concepto = row_item['id_concepto']
                            hes = row_item['HES/Liquidacion']
                            
                            cursor.execute("""
                                SELECT id FROM liquidacion_real 
                                WHERE id_contrato = ? AND id_cliente = ? 
                                  AND id_concepto = ? AND periodo = ?
                            """, (id_contrato_liq, id_cliente, id_concepto, periodo_liq))
                            
                            existe = cursor.fetchone()
                            
                            if existe:
                                cursor.execute("""
                                    UPDATE liquidacion_real 
                                    SET monto_cobrado = ?
                                    WHERE id_contrato = ? AND id_cliente = ? 
                                      AND id_concepto = ? AND periodo = ?
                                """, (hes, id_contrato_liq, id_cliente, id_concepto, periodo_liq))
                            else:
                                cursor.execute("""
                                    INSERT INTO liquidacion_real 
                                    (id_contrato, id_cliente, id_concepto, periodo, monto_cobrado)
                                    VALUES (?, ?, ?, ?, ?)
                                """, (id_contrato_liq, id_cliente, id_concepto, periodo_liq, hes))
                            guardados += 1
                        
                        conn.commit()
                        st.success(f"✅ {guardados} registros guardados correctamente")
                        st.balloons()
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error al guardar: {str(e)}")
            
            with col_btn2:
                if st.button("🔄 Recargar", key=f"recargar_liq_{id_cliente}_{periodo_liq}", use_container_width=True):
                    st.rerun()
            
            # Acumular totales generales (usando totales con IGV)
            total_general_valorizacion += total_valorizacion
            total_general_hes += total_hes
            total_general_diferencia += diferencia_total
    
    # ===== TOTALES GENERALES DEL CONTRATO =====
    if total_general_valorizacion > 0 or total_general_hes > 0:
        st.markdown("---")
        st.markdown("#### 📊 Totales Generales del Contrato")
        
        col_g1, col_g2, col_g3 = st.columns(3)
        with col_g1:
            with st.container(border=True):
                st.markdown("<div style='text-align: center; font-size: 0.75rem; color: #64748b;'>💰 TOTAL VALORIZACIÓN (Con IGV)</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='text-align: center; font-size: 1.5rem; font-weight: 700; color: #1152d4;'>${total_general_valorizacion:,.0f}</div>", unsafe_allow_html=True)
        with col_g2:
            with st.container(border=True):
                st.markdown("<div style='text-align: center; font-size: 0.75rem; color: #64748b;'>💸 TOTAL HES (Con IGV)</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='text-align: center; font-size: 1.5rem; font-weight: 700; color: #ef4444;'>${total_general_hes:,.0f}</div>", unsafe_allow_html=True)
        with col_g3:
            with st.container(border=True):
                st.markdown("<div style='text-align: center; font-size: 0.75rem; color: #64748b;'>📊 DIFERENCIA TOTAL</div>", unsafe_allow_html=True)
                if abs(total_general_diferencia) <= 5:
                    color = "#10b981"
                    emoji = "✅"
                elif total_general_diferencia < 0:
                    color = "#f59e0b"
                    emoji = "⚠️"
                else:
                    color = "#ef4444"
                    emoji = "🔴"
                st.markdown(f"<div style='text-align: center; font-size: 1.5rem; font-weight: 700; color: {color};'>${total_general_diferencia:,.0f} {emoji}</div>", unsafe_allow_html=True)
        
        col_g4, col_g5, col_g6 = st.columns(3)
        with col_g4:
            with st.container(border=True):
                st.markdown("<div style='text-align: center; font-size: 0.75rem; color: #64748b;'>📊 IGV VALORIZACIÓN</div>", unsafe_allow_html=True)
                igv_general_v = (total_general_valorizacion / 1.18) * 0.18 if total_general_valorizacion > 0 else 0
                st.markdown(f"<div style='text-align: center; font-size: 1.2rem; font-weight: 700;'>${igv_general_v:,.0f}</div>", unsafe_allow_html=True)
        with col_g5:
            with st.container(border=True):
                st.markdown("<div style='text-align: center; font-size: 0.75rem; color: #64748b;'>📊 IGV HES</div>", unsafe_allow_html=True)
                igv_general_h = (total_general_hes / 1.18) * 0.18 if total_general_hes > 0 else 0
                st.markdown(f"<div style='text-align: center; font-size: 1.2rem; font-weight: 700;'>${igv_general_h:,.0f}</div>", unsafe_allow_html=True)
        with col_g6:
            with st.container(border=True):
                st.markdown("<div style='text-align: center; font-size: 0.75rem; color: #64748b;'>🎯 % COBRO</div>", unsafe_allow_html=True)
                porcentaje_general = (total_general_hes / total_general_valorizacion * 100) if total_general_valorizacion > 0 else 0
                if porcentaje_general >= 99:
                    color = "#10b981"
                elif porcentaje_general >= 90:
                    color = "#f59e0b"
                else:
                    color = "#ef4444"
                st.markdown(f"<div style='text-align: center; font-size: 1.5rem; font-weight: 700; color: {color};'>{porcentaje_general:.1f}%</div>", unsafe_allow_html=True)

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