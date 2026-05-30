import streamlit as st
import pandas as pd
from datetime import datetime, date
from database.conexion import run_query, get_supabase
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

# Obtener conceptos de gastos
df_conceptos = run_query("conceptos_gastos", select="id, concepto", filters={"activo": 1})
conceptos_lista = df_conceptos.to_dict('records') if not df_conceptos.empty else []

# Obtener contratos para usar en tab3 (Liquidación)
contratos_global = run_query("contratos", select="id, nombre", filters={"activo": 1})
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
        df_años = run_query("vw_general_semanal", select="periodo", filters={"tipo_reporte": "CIERRE"})
        if not df_años.empty:
            df_años['año'] = df_años['periodo'].str[:4]
            años = sorted(df_años['año'].unique(), reverse=True)
        else:
            años = [datetime.now().strftime("%Y")]
        
        año_seleccionado = st.selectbox(
            "📅 Año",
            años if años else [datetime.now().strftime("%Y")],
            key="res_año"
        )
    
    with col_f2:
        df_periodos = run_query("vw_general_semanal", 
                               select="periodo",
                               filters={"periodo": f"{año_seleccionado}-%", "tipo_reporte": "CIERRE"})
        periodos_disponibles = df_periodos['periodo'].unique().tolist() if not df_periodos.empty else []
        periodos_disponibles.sort()
        
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
    
    # Contratos con datos
    df_contratos_con_datos = run_query("vw_general_semanal",
                                       select="id_contrato",
                                       filters={"periodo": periodos_seleccionados, "tipo_reporte": "CIERRE"})
    ids_con_datos = df_contratos_con_datos['id_contrato'].unique().tolist() if not df_contratos_con_datos.empty else []
    
    df_contratos_nombres = run_query("contratos", select="id, nombre", filters={"activo": 1})
    df_contratos_nombres = df_contratos_nombres[df_contratos_nombres['id'].isin(ids_con_datos)] if ids_con_datos else pd.DataFrame()
    
    contrato_opciones_filtradas = {"TODOS": None}
    for _, c in df_contratos_nombres.iterrows():
        contrato_opciones_filtradas[c['nombre']] = c['id']
    
    with col_f3:
        contrato_seleccionado = st.selectbox(
            "📋 Contrato",
            list(contrato_opciones_filtradas.keys()),
            key="res_contrato"
        )
        id_contrato = contrato_opciones_filtradas[contrato_seleccionado]
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if id_contrato is None:
        # ===== TODOS LOS CONTRATOS =====
        st.markdown("#### 📊 Resumen General de Todos los Contratos")
        
        datos_generales = []
        total_ingresos_gral = 0
        total_egresos_gral = 0
        
        for _, contrato in df_contratos_nombres.iterrows():
            id_contrato_tmp = contrato['id']
            nombre_contrato = contrato['nombre']
            
            clientes_tmp = run_query("clientes", select="id, nombre, codigo",
                                    filters={"id_contrato": id_contrato_tmp, "activo": 1})
            
            for _, cliente in clientes_tmp.iterrows():
                id_cliente = cliente['id']
                nombre_cliente = cliente['nombre']
                codigo_cliente = cliente['codigo']
                
                # Verificar si existe liquidación real
                df_liq_check = run_query("liquidacion_real",
                                        select="id",
                                        filters={"id_contrato": id_contrato_tmp, "id_cliente": id_cliente,
                                                "periodo": periodos_seleccionados})
                tiene_liquidacion = not df_liq_check.empty
                
                if tiene_liquidacion:
                    df_liq = run_query("liquidacion_real",
                                      select="id_concepto, monto_cobrar, monto_gasto",
                                      filters={"id_contrato": id_contrato_tmp, "id_cliente": id_cliente,
                                              "periodo": periodos_seleccionados})
                    
                    cpm_debo = df_liq[df_liq['id_concepto'] == -1]['monto_cobrar'].sum() if -1 in df_liq['id_concepto'].values else 0
                    cpm_gasto = df_liq[df_liq['id_concepto'] == -1]['monto_gasto'].sum() if -1 in df_liq['id_concepto'].values else 0
                    venta_debo = df_liq[df_liq['id_concepto'] == -2]['monto_cobrar'].sum() if -2 in df_liq['id_concepto'].values else 0
                    venta_gasto = df_liq[df_liq['id_concepto'] == -2]['monto_gasto'].sum() if -2 in df_liq['id_concepto'].values else 0
                    conceptos_debo = df_liq[(df_liq['id_concepto'] != -1) & (df_liq['id_concepto'] != -2) & (df_liq['id_concepto'] != -3)]['monto_cobrar'].sum()
                    conceptos_gasto = df_liq[(df_liq['id_concepto'] != -1) & (df_liq['id_concepto'] != -2) & (df_liq['id_concepto'] != -3)]['monto_gasto'].sum()
                    afiladoras_gasto = df_liq[df_liq['id_concepto'] == -3]['monto_gasto'].sum() if -3 in df_liq['id_concepto'].values else 0
                    
                    total_ingresos = cpm_debo + venta_debo + conceptos_debo
                    total_egresos = cpm_gasto + venta_gasto + conceptos_gasto + afiladoras_gasto
                    
                else:
                    df_cpm = run_query("vw_general_semanal",
                                      select="ingresos, costos",
                                      filters={"tipo": "CPM", "id_contrato": id_contrato_tmp, "id_cliente": id_cliente,
                                              "periodo": periodos_seleccionados, "tipo_reporte": "CIERRE"})
                    
                    df_venta = run_query("vw_general_semanal",
                                        select="ingresos, costos",
                                        filters={"tipo": "VENTA", "id_contrato": id_contrato_tmp, "id_cliente": id_cliente,
                                                "periodo": periodos_seleccionados, "tipo_reporte": "CIERRE"})
                    
                    df_afil = run_query("vw_general_semanal",
                                       select="otros_costos",
                                       filters={"tipo": "AFILADORAS", "id_contrato": id_contrato_tmp, "id_cliente": id_cliente,
                                               "periodo": periodos_seleccionados, "tipo_reporte": "CIERRE"})
                    
                    df_conceptos_def = run_query("valores_por_defecto",
                                                select="monto_cobrar_default, monto_gasto_default",
                                                filters={"id_contrato": id_contrato_tmp, "id_cliente": id_cliente})
                    
                    total_ingresos = (df_cpm['ingresos'].sum() if not df_cpm.empty else 0) + \
                                    (df_venta['ingresos'].sum() if not df_venta.empty else 0) + \
                                    (df_conceptos_def['monto_cobrar_default'].sum() if not df_conceptos_def.empty else 0)
                    
                    total_egresos = (df_cpm['costos'].sum() if not df_cpm.empty else 0) + \
                                   (df_venta['costos'].sum() if not df_venta.empty else 0) + \
                                   (df_afil['otros_costos'].sum() if not df_afil.empty else 0) + \
                                   (df_conceptos_def['monto_gasto_default'].sum() if not df_conceptos_def.empty else 0)
                
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
        info_contrato = run_query("contratos", select="nombre, tipo_operacion", filters={"id": id_contrato})
        if not info_contrato.empty:
            info_contrato = info_contrato.iloc[0]
            st.markdown(f"#### 📌 {info_contrato['nombre']} - {info_contrato['tipo_operacion']}")
        
        clientes = run_query("clientes", select="id, nombre, codigo",
                            filters={"id_contrato": id_contrato, "activo": 1})
        
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
                df_liq_check = run_query("liquidacion_real",
                                        select="id",
                                        filters={"id_contrato": id_contrato, "id_cliente": id_cliente,
                                                "periodo": periodos_seleccionados})
                
                tiene_liquidacion = not df_liq_check.empty
                
                if tiene_liquidacion:
                    df_liq = run_query("liquidacion_real",
                                      select="id_concepto, monto_cobrar, monto_gasto",
                                      filters={"id_contrato": id_contrato, "id_cliente": id_cliente,
                                              "periodo": periodos_seleccionados})
                    
                    cobrar_dict = {}
                    gasto_dict = {}
                    for _, row in df_liq.iterrows():
                        cobrar_dict[row['id_concepto']] = row['monto_cobrar']
                        gasto_dict[row['id_concepto']] = row['monto_gasto']
                else:
                    cobrar_dict = {}
                    gasto_dict = {}
                
                # ===== VALORES POR DEFECTO =====
                df_valores_defecto = run_query("conceptos_gastos", select="id, concepto", filters={"activo": 1})
                df_valores_defecto = df_valores_defecto.sort_values('concepto')
                
                # Agregar valores por defecto
                for idx, row in df_valores_defecto.iterrows():
                    df_valores_def = run_query("valores_por_defecto",
                                              select="monto_cobrar_default, monto_gasto_default",
                                              filters={"id_contrato": id_contrato, "id_cliente": id_cliente,
                                                      "id_concepto": row['id']})
                    if not df_valores_def.empty:
                        df_valores_defecto.loc[idx, 'monto_cobrar_default'] = df_valores_def['monto_cobrar_default'].iloc[0]
                        df_valores_defecto.loc[idx, 'monto_gasto_default'] = df_valores_def['monto_gasto_default'].iloc[0]
                    else:
                        df_valores_defecto.loc[idx, 'monto_cobrar_default'] = 0
                        df_valores_defecto.loc[idx, 'monto_gasto_default'] = 0
                
                # ===== CPM, VENTA, AFILADORAS =====
                df_cpm = run_query("vw_general_semanal",
                                  select="ingresos, costos",
                                  filters={"tipo": "CPM", "id_contrato": id_contrato, "id_cliente": id_cliente,
                                          "periodo": periodos_seleccionados, "tipo_reporte": "CIERRE"})
                cpm_debo = df_cpm['ingresos'].sum() if not df_cpm.empty else 0
                cpm_gasto = df_cpm['costos'].sum() if not df_cpm.empty else 0
                
                df_venta = run_query("vw_general_semanal",
                                    select="ingresos, costos",
                                    filters={"tipo": "VENTA", "id_contrato": id_contrato, "id_cliente": id_cliente,
                                            "periodo": periodos_seleccionados, "tipo_reporte": "CIERRE"})
                venta_debo = df_venta['ingresos'].sum() if not df_venta.empty else 0
                venta_gasto = df_venta['costos'].sum() if not df_venta.empty else 0
                
                df_afil = run_query("vw_general_semanal",
                                   select="otros_costos",
                                   filters={"tipo": "AFILADORAS", "id_contrato": id_contrato, "id_cliente": id_cliente,
                                           "periodo": periodos_seleccionados, "tipo_reporte": "CIERRE"})
                afiladoras_gasto = df_afil['otros_costos'].sum() if not df_afil.empty else 0
                
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
                        id_concepto = row['id']
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
                                    supabase = get_supabase()
                                    for row_item in rows_tabla:
                                        if row_item['es_editable']:
                                            id_concepto = row_item['id_concepto']
                                            nuevo_debo = row_item['Debo Cobrar']
                                            nuevo_gasto = row_item['Gasto']
                                            
                                            for periodo in periodos_seleccionados:
                                                existing = supabase.table('liquidacion_real').select('id').eq('id_contrato', id_contrato).eq('id_cliente', id_cliente).eq('id_concepto', id_concepto).eq('periodo', periodo).execute()
                                                
                                                if existing.data:
                                                    supabase.table('liquidacion_real').update({
                                                        'monto_cobrar': nuevo_debo,
                                                        'monto_gasto': nuevo_gasto
                                                    }).eq('id_contrato', id_contrato).eq('id_cliente', id_cliente).eq('id_concepto', id_concepto).eq('periodo', periodo).execute()
                                                else:
                                                    data = {
                                                        'id_contrato': id_contrato,
                                                        'id_cliente': id_cliente,
                                                        'id_concepto': id_concepto,
                                                        'periodo': periodo,
                                                        'monto_cobrar': nuevo_debo,
                                                        'monto_gasto': nuevo_gasto
                                                    }
                                                    supabase.table('liquidacion_real').insert(data).execute()
                                    
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
        df_periodos_proy = run_query("vw_general_semanal",
                                    select="periodo",
                                    filters={"tipo": "CPM", "tipo_reporte": "AVANCE"})
        periodos_proy = df_periodos_proy['periodo'].unique().tolist() if not df_periodos_proy.empty else []
        periodos_proy.sort(reverse=True)
        
        if not periodos_proy:
            periodos_proy = [datetime.now().strftime("%Y-%m")]
        
        periodo_proy = st.selectbox(
            "📅 Período (AVANCE)",
            periodos_proy,
            key="proy_periodo"
        )
    
    # ===== PASO 2: CONTRATOS QUE TIENEN DATOS EN ESE PERÍODO =====
    if periodo_proy:
        df_contratos_proy = run_query("vw_general_semanal",
                                     select="id_contrato",
                                     filters={"periodo": periodo_proy, "tipo": "CPM", "tipo_reporte": "AVANCE"})
        ids_contratos_proy = df_contratos_proy['id_contrato'].unique().tolist() if not df_contratos_proy.empty else []
        
        df_contratos_nombres_proy = run_query("contratos", select="id, nombre", filters={"activo": 1})
        df_contratos_nombres_proy = df_contratos_nombres_proy[df_contratos_nombres_proy['id'].isin(ids_contratos_proy)] if ids_contratos_proy else pd.DataFrame()
        
        contratos_proy_opciones = df_contratos_nombres_proy['nombre'].tolist()
        
        if not contratos_proy_opciones:
            st.warning(f"⚠️ No hay contratos con datos AVANCE en {periodo_proy}")
            st.stop()
    
    with col_p2:
        proy_contrato = st.selectbox(
            "📋 Contrato",
            contratos_proy_opciones,
            key="proy_contrato"
        )
        id_proy_contrato = df_contratos_nombres_proy[df_contratos_nombres_proy['nombre'] == proy_contrato]['id'].iloc[0]
    
    # ===== CLIENTES =====
    proy_clientes = run_query("clientes", select="id, nombre, codigo",
                             filters={"id_contrato": id_proy_contrato, "activo": 1})
    
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
    
    # ===== OBTENER DATOS DE PERFORACIÓN (metros) =====
    filtros_perf = {
        "id_contrato": id_proy_contrato,
        "periodo": periodo_proy,
        "tipo_operacion": "CPM",
        "tipo_reporte": "AVANCE"
    }
    if id_proy_cliente:
        filtros_perf["id_cliente"] = id_proy_cliente
    
    df_perforacion = run_query("perforacion_general", select="id, semana", filters=filtros_perf)
    
    if not df_perforacion.empty:
        ids_perforacion = df_perforacion['id'].tolist()
        df_perf_detalle = run_query("perforacion_detalle", select="id_perforacion_general, total_mp",
                                    filters={"id_perforacion_general": ids_perforacion})
        
        df_perf = df_perforacion.merge(df_perf_detalle, left_on='id', right_on='id_perforacion_general')
        df_perf = df_perf.groupby('semana')['total_mp'].sum().reset_index()
        df_perf.columns = ['semana', 'metros']
    else:
        df_perf = pd.DataFrame()
    
    # ===== OBTENER COSTOS DE ACERO =====
    filtros_acero = {
        "id_contrato": id_proy_contrato,
        "periodo": periodo_proy,
        "tipo_operacion": "CPM",
        "tipo_reporte": "AVANCE"
    }
    if id_proy_cliente:
        filtros_acero["id_cliente"] = id_proy_cliente
    
    df_acero = run_query("acero_general", select="id, semana", filters=filtros_acero)
    
    if not df_acero.empty:
        ids_acero = df_acero['id'].tolist()
        df_acero_detalle = run_query("acero_detalle", select="id_acero_general, codigo, cantidad",
                                     filters={"id_acero_general": ids_acero})
        
        # Obtener precios de costos
        df_costos = run_query("costos", select="codigo, precio_rtperu")
        costos_dict = dict(zip(df_costos['codigo'], df_costos['precio_rtperu'])) if not df_costos.empty else {}
        
        df_acero_detalle['costo_total'] = df_acero_detalle.apply(
            lambda row: row['cantidad'] * costos_dict.get(row['codigo'], 0), axis=1
        )
        
        df_costos_agg = df_acero_detalle.groupby('id_acero_general')['costo_total'].sum().reset_index()
        df_costos_agg = df_costos_agg.merge(df_acero[['id', 'semana']], left_on='id_acero_general', right_on='id')
        
        df_costos_agg = df_costos_agg.groupby('semana')['costo_total'].sum().reset_index()
        df_costos_agg.columns = ['semana', 'costo_total']
        df_costos = df_costos_agg
    else:
        df_costos = pd.DataFrame()
    
    # ===== OBTENER TARIFA POR METRO =====
    try:
        filtros_tarifa = {
            "id_contrato": id_proy_contrato,
            "periodo_desde": {"lte": periodo_proy}
        }
        if id_proy_cliente:
            filtros_tarifa["id_cliente"] = id_proy_cliente
        
        df_tarifa = run_query("tarifas", select="tarifa", filters=filtros_tarifa)
        
        # Filtrar por periodo_hasta
        if not df_tarifa.empty:
            df_tarifa = df_tarifa[df_tarifa['periodo_hasta'].isna() | (df_tarifa['periodo_hasta'] >= periodo_proy)]
        
        tarifa_por_metro = df_tarifa['tarifa'].iloc[0] if not df_tarifa.empty else 0
    except:
        tarifa_por_metro = 0
    
    # ===== OBTENER FECHAS POR SEMANA =====
    filtros_fechas = {
        "id_contrato": id_proy_contrato,
        "periodo": periodo_proy,
        "tipo_operacion": "CPM",
        "tipo_reporte": "AVANCE"
    }
    if id_proy_cliente:
        filtros_fechas["id_cliente"] = id_proy_cliente
    
    df_fechas = run_query("perforacion_general", select="semana, fecha_inicio, fecha_fin", filters=filtros_fechas)
    if not df_fechas.empty:
        df_fechas = df_fechas.dropna(subset=['fecha_inicio', 'fecha_fin'])
        df_fechas = df_fechas.groupby('semana').agg({
            'fecha_inicio': 'min',
            'fecha_fin': 'max'
        }).reset_index()
    
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
            'inicio': pd.to_datetime(row['fecha_inicio']).date() if row['fecha_inicio'] else None,
            'fin': pd.to_datetime(row['fecha_fin']).date() if row['fecha_fin'] else None
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
            if semana in fechas_dict and fechas_dict[semana]['inicio'] and fechas_dict[semana]['fin']:
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
        dias_restantes = dias_totales_mes - dias_acum if 'dias_acum' in locals() else 0
        rendimiento_diario = (metros_acum / dias_acum) if 'dias_acum' in locals() and dias_acum > 0 else 0
        
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
        df_años = run_query("vw_general_semanal", select="periodo", filters={"tipo_reporte": "CIERRE"})
        if not df_años.empty:
            df_años['año'] = df_años['periodo'].str[:4]
            años = sorted(df_años['año'].unique(), reverse=True)
        else:
            años = [datetime.now().strftime("%Y")]
        
        año_liquidacion = st.selectbox(
            "📅 Año",
            años if años else [datetime.now().strftime("%Y")],
            key="liq_año"
        )
    
    with col_l2:
        df_periodos_liq = run_query("vw_general_semanal",
                                    select="periodo",
                                    filters={"periodo": f"{año_liquidacion}-%", "tipo_reporte": "CIERRE"})
        periodos_liq = df_periodos_liq['periodo'].unique().tolist() if not df_periodos_liq.empty else []
        periodos_liq.sort()
        
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
    
    # ===== INFORMACIÓN DEL CONTRATO =====
    info_contrato_liq = run_query("contratos", select="nombre", filters={"id": id_contrato_liq})
    if not info_contrato_liq.empty:
        st.markdown(f"#### 📌 {info_contrato_liq['nombre'].iloc[0]} - Período: {periodo_liq}")
    
    # ===== CLIENTES =====
    clientes_liq = run_query("clientes", select="id, nombre, codigo",
                            filters={"id_contrato": id_contrato_liq, "activo": 1})
    
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
            df_cpm_liq = run_query("vw_general_semanal",
                                  select="ingresos",
                                  filters={"tipo": "CPM", "id_contrato": id_contrato_liq,
                                          "id_cliente": id_cliente, "periodo": periodo_liq,
                                          "tipo_reporte": "CIERRE"})
            debo_cpm = df_cpm_liq['ingresos'].sum() if not df_cpm_liq.empty else 0
            
            df_venta_liq = run_query("vw_general_semanal",
                                    select="ingresos",
                                    filters={"tipo": "VENTA", "id_contrato": id_contrato_liq,
                                            "id_cliente": id_cliente, "periodo": periodo_liq,
                                            "tipo_reporte": "CIERRE"})
            debo_venta = df_venta_liq['ingresos'].sum() if not df_venta_liq.empty else 0
            
            # ===== VALORES POR DEFECTO DE CONCEPTOS (solo los que tienen valor > 0) =====
            df_conceptos_liq = run_query("conceptos_gastos", select="id, concepto", filters={"activo": 1})
            
            # Agregar valores por defecto
            conceptos_con_valor = []
            for _, row in df_conceptos_liq.iterrows():
                df_valores_def = run_query("valores_por_defecto",
                                          select="monto_cobrar_default",
                                          filters={"id_contrato": id_contrato_liq, "id_cliente": id_cliente,
                                                  "id_concepto": row['id']})
                debo_default = df_valores_def['monto_cobrar_default'].iloc[0] if not df_valores_def.empty else 0
                
                if debo_default > 0:
                    conceptos_con_valor.append({
                        'id_concepto': row['id'],
                        'concepto': row['concepto'],
                        'debo_default': debo_default
                    })
            
            # ===== VALORES REALES PAGADOS (HES/LIQUIDACIÓN) =====
            df_pagado_real = run_query("liquidacion_real",
                                      select="id_concepto, monto_cobrado",
                                      filters={"id_contrato": id_contrato_liq, "id_cliente": id_cliente,
                                              "periodo": periodo_liq})
            
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
            for concepto in conceptos_con_valor:
                rows_liq.append({
                    'Concepto': concepto['concepto'].upper(),
                    'Valorizacion Mina': concepto['debo_default'],
                    'HES/Liquidacion': pagado_dict.get(concepto['id_concepto'], 0),
                    'id_concepto': concepto['id_concepto']
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
                        supabase = get_supabase()
                        guardados = 0
                        
                        for row_item in rows_liq:
                            id_concepto = row_item['id_concepto']
                            hes = row_item['HES/Liquidacion']
                            
                            existing = supabase.table('liquidacion_real').select('id').eq('id_contrato', id_contrato_liq).eq('id_cliente', id_cliente).eq('id_concepto', id_concepto).eq('periodo', periodo_liq).execute()
                            
                            if existing.data:
                                supabase.table('liquidacion_real').update({
                                    'monto_cobrado': hes
                                }).eq('id_contrato', id_contrato_liq).eq('id_cliente', id_cliente).eq('id_concepto', id_concepto).eq('periodo', periodo_liq).execute()
                            else:
                                data = {
                                    'id_contrato': id_contrato_liq,
                                    'id_cliente': id_cliente,
                                    'id_concepto': id_concepto,
                                    'periodo': periodo_liq,
                                    'monto_cobrado': hes
                                }
                                supabase.table('liquidacion_real').insert(data).execute()
                            guardados += 1
                        
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