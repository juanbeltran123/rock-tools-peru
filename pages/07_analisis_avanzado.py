import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
from database.conexion import get_connection
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_percentage_error, r2_score

# Configuración de la página
st.set_page_config(
    page_title="Rock Tools Peru - Análisis Avanzado",
    page_icon="📊",
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
</style>
""", unsafe_allow_html=True)

# Verificar autenticación
if 'autenticado' not in st.session_state or not st.session_state['autenticado']:
    st.switch_page("app.py")

if 'usuario' not in st.session_state:
    st.session_state['usuario'] = 'Admin'

conn = get_connection()

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
    if st.button("🚪 Salir", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.switch_page("app.py")

st.markdown("---")

# ============================================================================
# CARGA DE DATOS DESDE LA VISTA
# ============================================================================
@st.cache_data(ttl=3600)
def cargar_datos_rentabilidad():
    """Carga datos desde la vista vw_rentabilidad_contrato_tipo"""
    query = """
    SELECT 
        periodo,
        semana,
        tipo_reporte,
        contrato_nombre,
        cliente_nombre,
        tipo_nombre,
        total_metros,
        tarifa,
        ingreso_usd,
        consumo_usd,
        margen_usd,
        margen_porcentual
    FROM vw_rentabilidad_contrato_tipo
    ORDER BY periodo, semana, contrato_nombre, tipo_nombre
    """
    df = pd.read_sql_query(query, conn)
    return df

with st.spinner("Cargando datos..."):
    df = cargar_datos_rentabilidad()

if len(df) == 0:
    st.error("❌ No hay datos disponibles. Verifica que la vista 'vw_rentabilidad_contrato_tipo' esté creada.")
    st.stop()

# Convertir semana a string para filtros
df['semana_str'] = df['semana'].apply(lambda x: f"Semana {int(x)}" if pd.notna(x) and x != 'CIERRE' else str(x) if pd.notna(x) else '')

st.success(f"✅ Datos cargados: {df['periodo'].nunique()} períodos, {df['contrato_nombre'].nunique()} contratos")

# ============================================================================
# PESTAÑAS
# ============================================================================
tab_calor, tab_prediccion = st.tabs(["🔥 Matriz de Calor", "🤖 Predicción de Consumo"])

# ============================================================================
# PESTAÑA 1: MATRIZ DE CALOR (SIN CAMBIOS)
# ============================================================================
with tab_calor:
    st.subheader("🔥 Matriz de Calor: Margen Porcentual (%)")
    
    # Filtros
    col_f1, col_f2, col_f3 = st.columns(3)
    
    with col_f1:
        # Filtro de Semana (igual a otras páginas)
        opciones_semana = ['TODAS'] + sorted([s for s in df['semana_str'].unique() if s != ''])
        # Asegurar que CIERRE esté en las opciones
        if 'CIERRE' not in opciones_semana and 'CIERRE' in df['semana_str'].values:
            opciones_semana.append('CIERRE')
        semana_sel = st.selectbox(
            "📅 Semana",
            opciones_semana,
            index=opciones_semana.index('CIERRE') if 'CIERRE' in opciones_semana else 0
        )
    
    with col_f2:
        # Período (múltiple)
        periodos = sorted(df['periodo'].unique(), reverse=True)
        periodo_sel = st.multiselect(
            "📅 Período",
            periodos,
            default=[periodos[0]] if periodos else []
        )
    
    with col_f3:
        # Contrato (múltiple)
        contratos = sorted(df['contrato_nombre'].unique())
        contrato_sel = st.multiselect(
            "📄 Contrato",
            contratos,
            default=contratos  # Todos por defecto
        )
    
    # Aplicar filtros
    df_filtrado = df.copy()
    
    # Filtro de semana
    if semana_sel != 'TODAS':
        df_filtrado = df_filtrado[df_filtrado['semana_str'] == semana_sel]
    
    # Filtro de período
    if periodo_sel:
        df_filtrado = df_filtrado[df_filtrado['periodo'].isin(periodo_sel)]
    
    # Filtro de contrato
    if contrato_sel:
        df_filtrado = df_filtrado[df_filtrado['contrato_nombre'].isin(contrato_sel)]
    
    if len(df_filtrado) == 0:
        st.warning("⚠️ No hay datos con los filtros seleccionados")
    else:
        # Configuración de colores
        OBJETIVO = 42.0
        
        custom_colorscale = [
            [0.0, "#8B0000"],
            [0.2, "#FF0000"],
            [0.35, "#FF6600"],
            [0.42, "#FFFF00"],
            [0.5, "#90EE90"],
            [0.7, "#32CD32"],
            [1.0, "#006400"]
        ]
        
        # Agrupar por contrato y tipo (promedio)
        df_agrupado = df_filtrado.groupby(['contrato_nombre', 'tipo_nombre'], as_index=False)['margen_porcentual'].mean()
        
        # Crear pivote
        pivot = df_agrupado.pivot_table(
            index='contrato_nombre',
            columns='tipo_nombre',
            values='margen_porcentual',
            aggfunc='mean'
        )
        
        # Matriz de calor
        fig = px.imshow(
            pivot,
            text_auto='.1f',
            color_continuous_scale=custom_colorscale,
            range_color=[0, 80],
            aspect='auto',
            title=None
        )
        
        fig.update_layout(
            height=400 + (len(pivot) * 20),
            width=None,
            xaxis_title='Tipo de Perforación',
            yaxis_title='Contrato',
            coloraxis_colorbar=dict(
                title="Margen (%)",
                tickvals=[0, 20, 35, 42, 50, 70, 80],
                ticktext=["0%", "20%", "35%", "42% (objetivo)", "50%", "70%", "80%"]
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Métricas resumen
        st.subheader("📊 Resumen del Período")
        col_r1, col_r2, col_r3, col_r4, col_r5 = st.columns(5)
        
        with col_r1:
            st.metric("📄 Contratos", df_filtrado['contrato_nombre'].nunique())
        with col_r2:
            st.metric("📏 Total Metros", f"{df_filtrado['total_metros'].sum():,.0f}")
        with col_r3:
            st.metric("💰 Ingreso Total", f"${df_filtrado['ingreso_usd'].sum():,.0f}")
        with col_r4:
            st.metric("🔧 Consumo Total", f"${df_filtrado['consumo_usd'].sum():,.0f}")
        with col_r5:
            margen_prom = df_filtrado['margen_porcentual'].mean()
            st.metric("📊 Margen Promedio", f"{margen_prom:.1f}%")
        
        # Tabla detallada
        with st.expander("📋 Ver datos detallados"):
            st.dataframe(df_filtrado[[
                'periodo', 'semana_str', 'contrato_nombre', 'tipo_nombre',
                'total_metros', 'ingreso_usd', 'consumo_usd', 'margen_usd', 'margen_porcentual'
            ]].head(100), use_container_width=True)

# ============================================================================
# PESTAÑA 2: PREDICCIÓN DE CONSUMO (RESUMEN POR CONTRATO O CLIENTE)
# ============================================================================
with tab_prediccion:
    st.subheader("🤖 Predicción de Metros y Consumo de Acero")
    
    st.markdown("""
    **¿Cómo funciona?**  
    El modelo aprende del historial de cada contrato y tipo de perforación.  
    **Predice cuántos metros perforará** y **cuánto acero consumirá** para CADA tipo.
    
    Luego puedes ver el resumen **por Contrato** o **por Cliente**.
    """)
    
    # Filtrar solo datos CIERRE para el modelo
    df_modelo = df[df['tipo_reporte'] == 'CIERRE'].copy()
    
    if len(df_modelo) < 10:
        st.warning(f"⚠️ Datos insuficientes para entrenar modelo. Solo {len(df_modelo)} registros con CIERRE. Se necesitan al menos 10.")
    else:
        # Botón para entrenar modelo
        if st.button("🚀 Entrenar Modelo de Predicción", type="primary"):
            with st.spinner("Entrenando modelo con datos históricos..."):
                # Preparar datos
                df_feat = df_modelo.copy()
                df_feat = df_feat.sort_values(['contrato_nombre', 'tipo_nombre', 'periodo'])
                
                # Extraer mes del período
                df_feat['mes'] = df_feat['periodo'].str.split('-').str[1].astype(int)
                df_feat['año'] = df_feat['periodo'].str.split('-').str[0].astype(int)
                
                # Features para predecir METROS
                df_feat['metros_lag1'] = df_feat.groupby(['contrato_nombre', 'tipo_nombre'])['total_metros'].shift(1)
                df_feat['metros_lag2'] = df_feat.groupby(['contrato_nombre', 'tipo_nombre'])['total_metros'].shift(2)
                df_feat['metros_prom_3'] = df_feat.groupby(['contrato_nombre', 'tipo_nombre'])['total_metros'].transform(
                    lambda x: x.rolling(3, min_periods=1).mean()
                )
                
                # Features para predecir CONSUMO
                df_feat['consumo_lag1'] = df_feat.groupby(['contrato_nombre', 'tipo_nombre'])['consumo_usd'].shift(1)
                df_feat['consumo_lag2'] = df_feat.groupby(['contrato_nombre', 'tipo_nombre'])['consumo_usd'].shift(2)
                df_feat['consumo_prom_3'] = df_feat.groupby(['contrato_nombre', 'tipo_nombre'])['consumo_usd'].transform(
                    lambda x: x.rolling(3, min_periods=1).mean()
                )
                
                # Features
                features_metros = ['metros_lag1', 'metros_lag2', 'metros_prom_3', 'mes']
                features_consumo = ['total_metros', 'consumo_lag1', 'consumo_lag2', 'consumo_prom_3', 'mes']
                
                # Limpiar datos
                df_clean_metros = df_feat.dropna(subset=features_metros + ['total_metros'])
                df_clean_consumo = df_feat.dropna(subset=features_consumo + ['consumo_usd'])
                
                if len(df_clean_metros) < 5 or len(df_clean_consumo) < 5:
                    st.error(f"Datos insuficientes. Metros: {len(df_clean_metros)} | Consumo: {len(df_clean_consumo)}")
                else:
                    # --- MODELO 1: Predecir METROS ---
                    X_metros = df_clean_metros[features_metros]
                    y_metros = df_clean_metros['total_metros']
                    
                    n_test_metros = max(1, int(len(df_clean_metros) * 0.2))
                    X_train_m, X_test_m = X_metros[:-n_test_metros], X_metros[-n_test_metros:]
                    y_train_m, y_test_m = y_metros[:-n_test_metros], y_metros[-n_test_metros:]
                    
                    modelo_metros = RandomForestRegressor(n_estimators=50, random_state=42)
                    modelo_metros.fit(X_train_m, y_train_m)
                    
                    y_pred_m = modelo_metros.predict(X_test_m)
                    mape_metros = mean_absolute_percentage_error(y_test_m, y_pred_m)
                    r2_metros = r2_score(y_test_m, y_pred_m)
                    
                    # --- MODELO 2: Predecir CONSUMO ---
                    X_consumo = df_clean_consumo[features_consumo]
                    y_consumo = df_clean_consumo['consumo_usd']
                    
                    n_test_consumo = max(1, int(len(df_clean_consumo) * 0.2))
                    X_train_c, X_test_c = X_consumo[:-n_test_consumo], X_consumo[-n_test_consumo:]
                    y_train_c, y_test_c = y_consumo[:-n_test_consumo], y_consumo[-n_test_consumo:]
                    
                    modelo_consumo = RandomForestRegressor(n_estimators=50, random_state=42)
                    modelo_consumo.fit(X_train_c, y_train_c)
                    
                    y_pred_c = modelo_consumo.predict(X_test_c)
                    mape_consumo = mean_absolute_percentage_error(y_test_c, y_pred_c)
                    r2_consumo = r2_score(y_test_c, y_pred_c)
                    
                    # Guardar en sesión
                    st.session_state.modelo_metros = modelo_metros
                    st.session_state.modelo_consumo = modelo_consumo
                    st.session_state.mape_metros = mape_metros
                    st.session_state.mape_consumo = mape_consumo
                    st.session_state.r2_metros = r2_metros
                    st.session_state.r2_consumo = r2_consumo
                    st.session_state.features_metros = features_metros
                    st.session_state.features_consumo = features_consumo
                    st.session_state.df_clean_metros = df_clean_metros
                    st.session_state.df_clean_consumo = df_clean_consumo
                    st.session_state.modelo_entrenado = True
                    
                    # Mostrar resultados
                    st.success("✅ Modelos entrenados correctamente")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("📏 Predicción de Metros", f"MAPE: {mape_metros:.1%} | R²: {r2_metros:.3f}")
                    with col2:
                        st.metric("💰 Predicción de Consumo", f"MAPE: {mape_consumo:.1%} | R²: {r2_consumo:.3f}")
                    
                    # Importancia de features
                    st.subheader("🔍 Factores más importantes")
                    
                    col_imp1, col_imp2 = st.columns(2)
                    
                    importancia_metros = pd.DataFrame({
                        'feature': features_metros,
                        'importancia': modelo_metros.feature_importances_
                    }).sort_values('importancia', ascending=False)
                    
                    importancia_consumo = pd.DataFrame({
                        'feature': features_consumo,
                        'importancia': modelo_consumo.feature_importances_
                    }).sort_values('importancia', ascending=False)
                    
                    with col_imp1:
                        st.caption("Para predecir METROS:")
                        fig_imp_m = px.bar(importancia_metros, x='importancia', y='feature', orientation='h')
                        st.plotly_chart(fig_imp_m, use_container_width=True)
                    
                    with col_imp2:
                        st.caption("Para predecir CONSUMO:")
                        fig_imp_c = px.bar(importancia_consumo, x='importancia', y='feature', orientation='h')
                        st.plotly_chart(fig_imp_c, use_container_width=True)
        
        # Simulador (solo si modelo está entrenado)
        if st.session_state.get('modelo_entrenado', False):
            st.markdown("---")
            st.subheader("🎯 Predicción")
            st.caption("Selecciona si quieres ver el resumen por CONTRATO o por CLIENTE")
            
            # Selector: Ver por Contrato o por Cliente
            tipo_resumen = st.radio(
                "Ver resumen por:",
                ["📄 Contrato", "👥 Cliente"],
                horizontal=True
            )
            
            if tipo_resumen == "📄 Contrato":
                # ============================================================
                # RESUMEN POR CONTRATO
                # ============================================================
                contratos_pred = sorted(df_modelo['contrato_nombre'].unique())
                contrato_pred = st.selectbox("Seleccionar Contrato", contratos_pred)
                
                # Obtener todos los tipos de perforación de este contrato
                tipos_contrato = df_modelo[df_modelo['contrato_nombre'] == contrato_pred]['tipo_nombre'].unique()
                tipos_contrato = sorted(tipos_contrato)
                
                if len(tipos_contrato) == 0:
                    st.warning("⚠️ No hay tipos de perforación para este contrato")
                else:
                    st.info(f"📋 Tipos encontrados: {', '.join(tipos_contrato)}")
                    
                    predicciones_por_tipo = []
                    
                    with st.spinner(f"Prediciendo para {len(tipos_contrato)} tipo(s)..."):
                        for tipo in tipos_contrato:
                            historico = df_modelo[
                                (df_modelo['contrato_nombre'] == contrato_pred) & 
                                (df_modelo['tipo_nombre'] == tipo)
                            ].sort_values('periodo', ascending=False)
                            
                            if len(historico) < 3:
                                st.warning(f"⚠️ {tipo}: Datos insuficientes (solo {len(historico)} meses)")
                                continue
                            
                            ultimo = historico.iloc[0]
                            
                            # Predecir METROS
                            pred_row_metros = {}
                            for f in st.session_state.features_metros:
                                if f == 'metros_lag1':
                                    pred_row_metros[f] = historico.iloc[0]['total_metros'] if len(historico) >= 1 else 0
                                elif f == 'metros_lag2':
                                    pred_row_metros[f] = historico.iloc[1]['total_metros'] if len(historico) >= 2 else historico.iloc[0]['total_metros'] if len(historico) >= 1 else 0
                                elif f == 'metros_prom_3':
                                    pred_row_metros[f] = historico['total_metros'].head(3).mean()
                                elif f == 'mes':
                                    mes_actual = datetime.now().month
                                    pred_row_metros[f] = mes_actual + 1 if mes_actual < 12 else 1
                            
                            X_pred_metros = pd.DataFrame([pred_row_metros])
                            metros_predicho = st.session_state.modelo_metros.predict(X_pred_metros)[0]
                            metros_predicho = max(0, int(metros_predicho))
                            
                            # Predecir CONSUMO
                            pred_row_consumo = {}
                            for f in st.session_state.features_consumo:
                                if f == 'total_metros':
                                    pred_row_consumo[f] = metros_predicho
                                elif f == 'consumo_lag1':
                                    pred_row_consumo[f] = historico.iloc[0]['consumo_usd'] if len(historico) >= 1 else 0
                                elif f == 'consumo_lag2':
                                    pred_row_consumo[f] = historico.iloc[1]['consumo_usd'] if len(historico) >= 2 else historico.iloc[0]['consumo_usd'] if len(historico) >= 1 else 0
                                elif f == 'consumo_prom_3':
                                    pred_row_consumo[f] = historico['consumo_usd'].head(3).mean()
                                elif f == 'mes':
                                    mes_actual = datetime.now().month
                                    pred_row_consumo[f] = mes_actual + 1 if mes_actual < 12 else 1
                            
                            X_pred_consumo = pd.DataFrame([pred_row_consumo])
                            consumo_predicho = st.session_state.modelo_consumo.predict(X_pred_consumo)[0]
                            consumo_predicho = max(0, consumo_predicho)
                            
                            # Calcular ingreso y margen
                            tarifa_actual = ultimo['tarifa']
                            ingreso_estimado = metros_predicho * tarifa_actual
                            margen_estimado = ingreso_estimado - consumo_predicho
                            margen_porcentual = (1 - consumo_predicho / ingreso_estimado) * 100 if ingreso_estimado > 0 else 0
                            
                            predicciones_por_tipo.append({
                                'Tipo': tipo,
                                'Metros': metros_predicho,
                                'Consumo (USD)': consumo_predicho,
                                'Ingreso (USD)': ingreso_estimado,
                                'Margen (USD)': margen_estimado,
                                'Margen %': margen_porcentual
                            })
                    
                    if len(predicciones_por_tipo) > 0:
                        df_predicciones = pd.DataFrame(predicciones_por_tipo)
                        
                        # Totales
                        total_metros = df_predicciones['Metros'].sum()
                        total_consumo = df_predicciones['Consumo (USD)'].sum()
                        total_ingreso = df_predicciones['Ingreso (USD)'].sum()
                        total_margen = df_predicciones['Margen (USD)'].sum()
                        margen_porcentual_total = (total_margen / total_ingreso) * 100 if total_ingreso > 0 else 0
                        
                        # Mostrar tabla
                        st.subheader(f"📊 Predicción por Tipo - {contrato_pred}")
                        df_mostrar = df_predicciones.copy()
                        df_mostrar['Metros'] = df_mostrar['Metros'].apply(lambda x: f"{x:,.0f}")
                        df_mostrar['Consumo (USD)'] = df_mostrar['Consumo (USD)'].apply(lambda x: f"${x:,.0f}")
                        df_mostrar['Ingreso (USD)'] = df_mostrar['Ingreso (USD)'].apply(lambda x: f"${x:,.0f}")
                        df_mostrar['Margen (USD)'] = df_mostrar['Margen (USD)'].apply(lambda x: f"${x:,.0f}")
                        df_mostrar['Margen %'] = df_mostrar['Margen %'].apply(lambda x: f"{x:.1f}%")
                        st.dataframe(df_mostrar, use_container_width=True)
                        
                        # Resumen del contrato
                        st.markdown("---")
                        st.subheader(f"📋 RESUMEN DEL CONTRATO: {contrato_pred}")
                        
                        col_r1, col_r2, col_r3, col_r4, col_r5 = st.columns(5)
                        with col_r1:
                            st.metric("📏 Total Metros", f"{total_metros:,.0f}")
                        with col_r2:
                            st.metric("💰 Consumo Total", f"${total_consumo:,.0f}")
                        with col_r3:
                            st.metric("📈 Ingreso Total", f"${total_ingreso:,.0f}")
                        with col_r4:
                            st.metric("💵 Margen Total", f"${total_margen:,.0f}")
                        with col_r5:
                            st.metric("📊 Margen %", f"{margen_porcentual_total:.1f}%")
                        
                        if margen_porcentual_total >= 42:
                            st.success(f"✅ Margen del {margen_porcentual_total:.1f}% - Supera objetivo del 42%")
                        elif margen_porcentual_total >= 30:
                            st.warning(f"⚠️ Margen del {margen_porcentual_total:.1f}% - Por debajo del objetivo 42%")
                        else:
                            st.error(f"❌ Margen del {margen_porcentual_total:.1f}% - Crítico, requiere revisión")
                    else:
                        st.error("No se pudo predecir para ningún tipo")
            
            else:
                # ============================================================
                # RESUMEN POR CLIENTE (todos sus contratos)
                # ============================================================
                clientes_pred = sorted(df_modelo['cliente_nombre'].unique())
                cliente_pred = st.selectbox("Seleccionar Cliente", clientes_pred)
                
                # Obtener todos los contratos de este cliente
                contratos_cliente = df_modelo[df_modelo['cliente_nombre'] == cliente_pred]['contrato_nombre'].unique()
                contratos_cliente = sorted(contratos_cliente)
                
                if len(contratos_cliente) == 0:
                    st.warning("⚠️ No hay contratos para este cliente")
                else:
                    st.info(f"📋 Contratos encontrados: {', '.join(contratos_cliente)}")
                    
                    todas_predicciones = []  # Lista para acumular todas las predicciones
                    
                    with st.spinner(f"Prediciendo para {len(contratos_cliente)} contrato(s)..."):
                        
                        for contrato in contratos_cliente:
                            # Obtener tipos de este contrato
                            tipos_contrato = df_modelo[
                                (df_modelo['contrato_nombre'] == contrato) & 
                                (df_modelo['cliente_nombre'] == cliente_pred)
                            ]['tipo_nombre'].unique()
                            tipos_contrato = sorted(tipos_contrato)
                            
                            for tipo in tipos_contrato:
                                historico = df_modelo[
                                    (df_modelo['contrato_nombre'] == contrato) & 
                                    (df_modelo['tipo_nombre'] == tipo)
                                ].sort_values('periodo', ascending=False)
                                
                                if len(historico) < 3:
                                    continue
                                
                                ultimo = historico.iloc[0]
                                
                                # Predecir METROS
                                pred_row_metros = {}
                                for f in st.session_state.features_metros:
                                    if f == 'metros_lag1':
                                        pred_row_metros[f] = historico.iloc[0]['total_metros'] if len(historico) >= 1 else 0
                                    elif f == 'metros_lag2':
                                        pred_row_metros[f] = historico.iloc[1]['total_metros'] if len(historico) >= 2 else historico.iloc[0]['total_metros'] if len(historico) >= 1 else 0
                                    elif f == 'metros_prom_3':
                                        pred_row_metros[f] = historico['total_metros'].head(3).mean()
                                    elif f == 'mes':
                                        mes_actual = datetime.now().month
                                        pred_row_metros[f] = mes_actual + 1 if mes_actual < 12 else 1
                                
                                X_pred_metros = pd.DataFrame([pred_row_metros])
                                metros_predicho = st.session_state.modelo_metros.predict(X_pred_metros)[0]
                                metros_predicho = max(0, int(metros_predicho))
                                
                                # Predecir CONSUMO
                                pred_row_consumo = {}
                                for f in st.session_state.features_consumo:
                                    if f == 'total_metros':
                                        pred_row_consumo[f] = metros_predicho
                                    elif f == 'consumo_lag1':
                                        pred_row_consumo[f] = historico.iloc[0]['consumo_usd'] if len(historico) >= 1 else 0
                                    elif f == 'consumo_lag2':
                                        pred_row_consumo[f] = historico.iloc[1]['consumo_usd'] if len(historico) >= 2 else historico.iloc[0]['consumo_usd'] if len(historico) >= 1 else 0
                                    elif f == 'consumo_prom_3':
                                        pred_row_consumo[f] = historico['consumo_usd'].head(3).mean()
                                    elif f == 'mes':
                                        mes_actual = datetime.now().month
                                        pred_row_consumo[f] = mes_actual + 1 if mes_actual < 12 else 1
                                
                                X_pred_consumo = pd.DataFrame([pred_row_consumo])
                                consumo_predicho = st.session_state.modelo_consumo.predict(X_pred_consumo)[0]
                                consumo_predicho = max(0, consumo_predicho)
                                
                                # Calcular ingreso y margen
                                tarifa_actual = ultimo['tarifa']
                                ingreso_estimado = metros_predicho * tarifa_actual
                                margen_estimado = ingreso_estimado - consumo_predicho
                                margen_porcentual = (1 - consumo_predicho / ingreso_estimado) * 100 if ingreso_estimado > 0 else 0
                                
                                todas_predicciones.append({
                                    'Contrato': contrato,
                                    'Tipo': tipo,
                                    'Metros': metros_predicho,
                                    'Consumo (USD)': consumo_predicho,
                                    'Ingreso (USD)': ingreso_estimado,
                                    'Margen (USD)': margen_estimado,
                                    'Margen %': margen_porcentual
                                })
                    
                    if len(todas_predicciones) > 0:
                        df_predicciones = pd.DataFrame(todas_predicciones)
                        
                        # Totales del cliente
                        total_metros = df_predicciones['Metros'].sum()
                        total_consumo = df_predicciones['Consumo (USD)'].sum()
                        total_ingreso = df_predicciones['Ingreso (USD)'].sum()
                        total_margen = df_predicciones['Margen (USD)'].sum()
                        margen_porcentual_total = (total_margen / total_ingreso) * 100 if total_ingreso > 0 else 0
                        
                        # Mostrar tabla detallada
                        st.subheader(f"📊 Predicción Detallada - {cliente_pred}")
                        df_mostrar = df_predicciones.copy()
                        df_mostrar['Metros'] = df_mostrar['Metros'].apply(lambda x: f"{x:,.0f}")
                        df_mostrar['Consumo (USD)'] = df_mostrar['Consumo (USD)'].apply(lambda x: f"${x:,.0f}")
                        df_mostrar['Ingreso (USD)'] = df_mostrar['Ingreso (USD)'].apply(lambda x: f"${x:,.0f}")
                        df_mostrar['Margen (USD)'] = df_mostrar['Margen (USD)'].apply(lambda x: f"${x:,.0f}")
                        df_mostrar['Margen %'] = df_mostrar['Margen %'].apply(lambda x: f"{x:.1f}%")
                        st.dataframe(df_mostrar, use_container_width=True)
                        
                        # Resumen del cliente
                        st.markdown("---")
                        st.subheader(f"📋 RESUMEN DEL CLIENTE: {cliente_pred}")
                        
                        col_r1, col_r2, col_r3, col_r4, col_r5 = st.columns(5)
                        with col_r1:
                            st.metric("📏 Total Metros", f"{total_metros:,.0f}")
                        with col_r2:
                            st.metric("💰 Consumo Total", f"${total_consumo:,.0f}")
                        with col_r3:
                            st.metric("📈 Ingreso Total", f"${total_ingreso:,.0f}")
                        with col_r4:
                            st.metric("💵 Margen Total", f"${total_margen:,.0f}")
                        with col_r5:
                            st.metric("📊 Margen %", f"{margen_porcentual_total:.1f}%")
                        
                        if margen_porcentual_total >= 42:
                            st.success(f"✅ Margen del {margen_porcentual_total:.1f}% - Supera objetivo del 42%")
                        elif margen_porcentual_total >= 30:
                            st.warning(f"⚠️ Margen del {margen_porcentual_total:.1f}% - Por debajo del objetivo 42%")
                        else:
                            st.error(f"❌ Margen del {margen_porcentual_total:.1f}% - Crítico, requiere revisión")
                    else:
                        st.error("No se pudo predecir para ningún contrato/tipo")
        else:
            st.info("👈 Haz clic en 'Entrenar Modelo de Predicción' primero")