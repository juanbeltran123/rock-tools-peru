import streamlit as st
import pandas as pd
import os
import tempfile
import re
from datetime import datetime
from database.conexion import run_query, get_supabase, run_delete, run_insert
from utils.cargador_excel import cargar_excel, obtener_contrato, obtener_cliente, detectar_encabezados_cliente

# Configuración de la página
st.set_page_config(
    page_title="Rock Tools Peru - Cargas",
    page_icon="📤",
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
        max-width: 1400px;
        margin: 0 auto;
    }
    
    /* Estilos para tablas */
    .stDataFrame thead tr th {
        text-align: center !important;
        font-weight: bold !important;
        background-color: #F8FAFC !important;
        color: #1A2A3A !important;
        padding: 10px 8px !important;
    }
    
    .stDataFrame tbody tr td {
        text-align: center !important;
        padding: 8px !important;
        border-bottom: 1px solid #E5E7EB !important;
    }
    
    .stDataFrame tbody tr td:first-child {
        text-align: left !important;
    }
</style>
""", unsafe_allow_html=True)

# Verificar autenticación
if 'autenticado' not in st.session_state or not st.session_state['autenticado']:
    st.switch_page("app.py")

if 'usuario' not in st.session_state:
    st.session_state['usuario'] = 'Admin'

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
    if st.button("🚪 Salir", key="logout_cargas", type="secondary", use_container_width=True):
        st.session_state.clear()
        st.switch_page("app.py")

st.divider()

# ============================================================================
# TÍTULO
# ============================================================================
st.markdown("## 📤 Gestión de Cargas")
st.markdown("Carga de reportes, costos y control de archivos")

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================================
# OBTENER PERÍODOS DISPONIBLES PARA FILTROS
# ============================================================================
df_periodos = run_query("control_cargas", select="periodo")
periodos_disponibles = df_periodos['periodo'].unique().tolist() if not df_periodos.empty else []
periodos_disponibles.sort(reverse=True)

if not periodos_disponibles:
    periodos_disponibles = [datetime.now().strftime("%Y-%m")]

# ============================================================================
# PESTAÑAS PRINCIPALES
# ============================================================================
tab1, tab2 = st.tabs([
    "📤 CARGAR REPORTES", 
    "💰 CARGAR COSTOS"
])

# ===== PESTAÑA 1: CARGAR REPORTES =====
with tab1:
    col_upload, col_filters = st.columns([2, 1])
    
    with col_upload:
        st.markdown("#### 📤 Subir Reporte")
        
        st.info("""
        **Instrucciones:**
        - Selecciona el archivo Excel de reporte (avance semanal o cierre mensual)
        - El sistema detectará automáticamente: contrato, período, semana y tipo
        - Los datos existentes serán reemplazados
        """)
        
        archivo_reporte = st.file_uploader(
            "Seleccionar archivo Excel", 
            type=['xlsx', 'xls'],
            key="upload_reporte"
        )
        
        if archivo_reporte:
            nombre_archivo = archivo_reporte.name.upper()
            
            col1, col2, col3 = st.columns(3)
            
            if "CIERRE" in nombre_archivo:
                tipo_reporte = "CIERRE"
                meses = {
                    'ENERO': '01', 'FEBRERO': '02', 'MARZO': '03', 'ABRIL': '04',
                    'MAYO': '05', 'JUNIO': '06', 'JULIO': '07', 'AGOSTO': '08',
                    'SEPTIEMBRE': '09', 'OCTUBRE': '10', 'NOVIEMBRE': '11', 'DICIEMBRE': '12'
                }
                
                periodo_detectado = None
                año_actual = datetime.now().strftime("%Y")
                for mes_nombre, mes_num in meses.items():
                    if mes_nombre in nombre_archivo:
                        periodo_detectado = f"{año_actual}-{mes_num}"
                        break
                
                with col1:
                    st.metric("Tipo", "CIERRE")
                with col2:
                    st.metric("Período detectado", periodo_detectado or "No detectado")
                with col3:
                    st.metric("Semana", "-")
                
                semana_detectada = 0
                
            else:
                tipo_reporte = "AVANCE"
                
                semana_detectada = 1
                match = re.search(r'SEMANA\s*(\d+)', nombre_archivo, re.IGNORECASE)
                if match:
                    semana_detectada = int(match.group(1))
                
                meses = {
                    'ENERO': '01', 'FEBRERO': '02', 'MARZO': '03', 'ABRIL': '04',
                    'MAYO': '05', 'JUNIO': '06', 'JULIO': '07', 'AGOSTO': '08',
                    'SEPTIEMBRE': '09', 'OCTUBRE': '10', 'NOVIEMBRE': '11', 'DICIEMBRE': '12'
                }
                
                periodo_detectado = None
                año_actual = datetime.now().strftime("%Y")
                for mes_nombre, mes_num in meses.items():
                    if mes_nombre in nombre_archivo:
                        periodo_detectado = f"{año_actual}-{mes_num}"
                        break
                
                with col1:
                    st.metric("Tipo", "AVANCE")
                with col2:
                    st.metric("Período detectado", periodo_detectado or "No detectado")
                with col3:
                    st.metric("Semana detectada", semana_detectada)
            
            if st.button("📤 Procesar Reporte", type="primary", use_container_width=True, key="btn_procesar_reporte"):
                with st.spinner("Procesando archivo..."):
                    try:
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
                            tmp_file.write(archivo_reporte.getbuffer())
                            ruta_temporal = tmp_file.name
                        
                        resumen = cargar_excel(
                            ruta_temporal,
                            periodo_detectado,
                            semana_detectada if tipo_reporte == "AVANCE" else 0,
                            tipo_reporte
                        )
                        
                        st.success("✅ Archivo procesado correctamente")
                        
                        with st.expander("📊 Ver resumen de carga"):
                            st.json(resumen)
                        
                        os.unlink(ruta_temporal)
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                        try:
                            os.unlink(ruta_temporal)
                        except:
                            pass
    
    with col_filters:
        st.markdown("#### 🔍 Reportes Cargados")
        
        periodo_filtro = st.selectbox(
            "📅 Período",
            periodos_disponibles,
            key="reportes_periodo"
        )
        
        if st.button("🔄 Actualizar", use_container_width=True, key="btn_actualizar_reportes"):
            st.rerun()
    
    st.markdown("---")
    
    # Tabla de reportes cargados por período
    st.markdown(f"#### 📋 Reportes Cargados - Período: {periodo_filtro}")
    
    # Obtener reportes del período
    df_reportes = run_query("control_cargas", 
                           select="fecha_carga, id_contrato, id_cliente, semana, tipo_reporte, archivo_original",
                           filters={"periodo": periodo_filtro})
    
    if not df_reportes.empty:
        # Obtener nombres de contratos
        df_contratos = run_query("contratos", select="id, nombre")
        contratos_dict = dict(zip(df_contratos['id'], df_contratos['nombre']))
        
        # Obtener nombres de clientes
        df_clientes = run_query("clientes", select="id, nombre")
        clientes_dict = dict(zip(df_clientes['id'], df_clientes['nombre']))
        
        df_reportes['contrato'] = df_reportes['id_contrato'].map(contratos_dict)
        df_reportes['cliente'] = df_reportes['id_cliente'].map(clientes_dict)
        df_reportes['fecha_carga'] = pd.to_datetime(df_reportes['fecha_carga']).dt.strftime('%Y-%m-%d %H:%M')
        df_reportes['semana'] = df_reportes['semana'].apply(lambda x: f"S{int(x)}" if x and x > 0 else "-")
        df_reportes = df_reportes.rename(columns={
            'fecha_carga': 'Fecha Carga',
            'contrato': 'Contrato',
            'cliente': 'Cliente',
            'semana': 'Semana',
            'tipo_reporte': 'Tipo',
            'archivo_original': 'Archivo'
        })
        
        st.dataframe(
            df_reportes[['Fecha Carga', 'Contrato', 'Cliente', 'Semana', 'Tipo', 'Archivo']],
            use_container_width=True,
            hide_index=True,
            column_config={
                "Fecha Carga": st.column_config.TextColumn("Fecha Carga", width="small"),
                "Contrato": st.column_config.TextColumn("Contrato", width="medium"),
                "Cliente": st.column_config.TextColumn("Cliente", width="medium"),
                "Semana": st.column_config.TextColumn("Semana", width="small"),
                "Tipo": st.column_config.TextColumn("Tipo", width="small"),
                "Archivo": st.column_config.TextColumn("Archivo", width="large")
            }
        )
    else:
        st.info(f"No hay reportes cargados para el período {periodo_filtro}")

# ===== PESTAÑA 2: CARGAR COSTOS =====
with tab2:
    col_upload_costos, col_lista = st.columns([1, 1])
    
    with col_upload_costos:
        st.markdown("#### 💰 Subir Costos")
        
        st.info("""
        **Instrucciones:**
        - Selecciona el archivo Excel de costos
        - Indica el período correspondiente (YYYY-MM)
        - Los datos del período serán reemplazados
        """)
        
        archivo_costos = st.file_uploader(
            "Seleccionar archivo Excel de Costos", 
            type=['xlsx', 'xls'],
            key="upload_costos"
        )
        
        periodo_costos = st.text_input(
            "Período (YYYY-MM)", 
            value=datetime.now().strftime("%Y-%m"),
            key="periodo_costos_input"
        )
        
        if archivo_costos and periodo_costos:
            if not re.match(r'^\d{4}-\d{2}$', periodo_costos):
                st.error("❌ Período inválido. Use formato YYYY-MM")
            else:
                if st.button("📤 Procesar Costos", type="primary", use_container_width=True, key="btn_procesar_costos"):
                    with st.spinner("Procesando archivo de costos..."):
                        try:
                            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
                                tmp_file.write(archivo_costos.getbuffer())
                                ruta_temporal = tmp_file.name
                            
                            df = pd.read_excel(ruta_temporal)
                            
                            def limpiar_nombre(col):
                                nombre = str(col).lower()
                                nombre = re.sub(r'[^a-z0-9]', '_', nombre)
                                nombre = re.sub(r'_+', '_', nombre)
                                return nombre.strip('_')
                            
                            df.columns = [limpiar_nombre(col) for col in df.columns]
                            
                            if 'codigo' in df.columns:
                                df['codigo'] = df['codigo'].astype(str)
                                df['codigo'] = df['codigo'].str.replace(r'\.0$', '', regex=True)
                                df['codigo'] = df['codigo'].str.strip()
                            
                            df['periodo'] = periodo_costos
                            
                            columnas_precios = ['unit_price_usd', 'precio_rtperu']
                            nulos_antes = 0
                            for col in columnas_precios:
                                if col in df.columns:
                                    nulos_antes += df[col].isna().sum()
                            
                            for col in columnas_precios:
                                if col in df.columns:
                                    df[col] = df[col].fillna(0)
                            
                            if nulos_antes > 0:
                                st.info(f"ℹ️ Se rellenaron {nulos_antes} celdas vacías con 0 en las columnas de precios")
                            
                            # Obtener cliente de Supabase para verificar columnas
                            supabase = get_supabase()
                            
                            # Eliminar registros existentes del período
                            result_delete = supabase.table('costos').delete().eq('periodo', periodo_costos).execute()
                            registros_eliminados = len(result_delete.data) if result_delete.data else 0
                            
                            # Insertar nuevos registros
                            registros_insertados = 0
                            for _, row in df.iterrows():
                                # Filtrar solo las columnas que existen en la tabla
                                data_row = row.to_dict()
                                # Remover NaN y None
                                data_row = {k: (v if pd.notna(v) else None) for k, v in data_row.items()}
                                result_insert = supabase.table('costos').insert(data_row).execute()
                                if result_insert.data:
                                    registros_insertados += 1
                            
                            st.success(f"✅ Período {periodo_costos}: {registros_eliminados} registros reemplazados por {registros_insertados} nuevos")
                            
                            os.unlink(ruta_temporal)
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
                            try:
                                os.unlink(ruta_temporal)
                            except:
                                pass
    
    with col_lista:
        st.markdown("#### 📋 Períodos Cargados")
        
        # Obtener períodos de costos
        df_costos = run_query("costos", select="periodo")
        
        if not df_costos.empty:
            df_periodos = df_costos.groupby('periodo').size().reset_index(name='registros')
            df_periodos = df_periodos.sort_values('periodo', ascending=False)
            df_periodos = df_periodos.rename(columns={
                'periodo': 'Período',
                'registros': 'Registros'
            })
            st.dataframe(
                df_periodos,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Período": st.column_config.TextColumn("Período", width="small"),
                    "Registros": st.column_config.NumberColumn("Registros", width="small")
                }
            )
        else:
            st.info("No hay costos cargados")

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