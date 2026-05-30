import streamlit as st
import pandas as pd
from datetime import date, datetime
import os
from database.conexion import get_connection

# Configuración de la página
st.set_page_config(
    page_title="Rock Tools Peru - Maestros",
    page_icon="📚",
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

# Función para cargar CSS
def load_css():
    css_file = os.path.join("assets", "css", "style.css")
    if os.path.exists(css_file):
        with open(css_file) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Cargar estilos
load_css()

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
    if st.button("🚪 Salir", key="logout_maes", type="secondary", use_container_width=True):
        st.session_state.clear()
        st.switch_page("app.py")

st.divider()

# ============================================================================
# TÍTULO
# ============================================================================
st.markdown("## 📚 Maestros")
st.markdown("Gestión de tablas maestras y valores por defecto")

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================================
# FUNCIONES COMUNES
# ============================================================================

def cargar_opciones_contrato():
    """Cargar contratos para combos - limpiando números del nombre"""
    df = pd.read_sql("SELECT id, nombre FROM contratos WHERE activo = 1 ORDER BY nombre", conn)
    
    opciones = {}
    for _, row in df.iterrows():
        # Limpiar el nombre: eliminar "1 " o "2 " al inicio
        nombre_limpio = row['nombre']
        # Si el nombre empieza con número y espacio, lo quitamos
        if nombre_limpio and nombre_limpio[0].isdigit() and ' ' in nombre_limpio:
            nombre_limpio = nombre_limpio.split(' ', 1)[1]
        
        opciones[nombre_limpio] = row['id']
    
    return opciones

def cargar_opciones_cliente(id_contrato=None):
    """Cargar clientes para combos filtrando por contrato"""
    
    if id_contrato:
        # Debug
        st.write(f"🔍 Debug - Filtrando clientes por id_contrato = {id_contrato}")
        
        df = pd.read_sql(f"""
            SELECT id, nombre, codigo, id_contrato
            FROM clientes 
            WHERE activo = 1 AND id_contrato = {id_contrato} 
            ORDER BY nombre
        """, conn)
        
        # Debug: mostrar cuántos encontró
        st.write(f"🔍 Debug - Clientes encontrados: {len(df)}")
        if not df.empty:
            st.dataframe(df)
        
    else:
        st.write("🔍 Debug - Cargando TODOS los clientes (sin filtro)")
        df = pd.read_sql("""
            SELECT id, nombre, codigo, id_contrato
            FROM clientes 
            WHERE activo = 1 
            ORDER BY nombre
        """, conn)
        
        st.write(f"🔍 Debug - Clientes encontrados: {len(df)}")
        st.dataframe(df)
    
    return {f"{row['nombre']} ({row['codigo']})": row['id'] for _, row in df.iterrows()} 

def cargar_opciones_tipo_perforacion():
    """Cargar tipos de perforación"""
    df = pd.read_sql("SELECT id, nombre FROM tipo_perforacion WHERE activo = 1 ORDER BY nombre", conn)
    return {row['nombre']: row['id'] for _, row in df.iterrows()}

def cargar_opciones_familia():
    """Cargar familias"""
    df = pd.read_sql("SELECT id, nombre FROM familia ORDER BY nombre", conn)
    return {row['nombre']: row['id'] for _, row in df.iterrows()}

def cargar_opciones_concepto():
    """Cargar conceptos de gastos"""
    df = pd.read_sql("SELECT id, concepto FROM conceptos_gastos WHERE activo = 1 ORDER BY concepto", conn)
    return {row['concepto']: row['id'] for _, row in df.iterrows()}


# ====================================================================
# FUNCIÓN INDEPENDIENTE PARA TARIFAS
# ====================================================================
def render_tarifas():
    """Función independiente para gestionar tarifas"""
    
    st.markdown("### 💰 Gestión de Tarifas")
    
    # Cargar datos directamente
    df_contratos = pd.read_sql("SELECT id, nombre FROM contratos WHERE activo = 1 ORDER BY id", conn)
    contratos_lista = [row['nombre'] for _, row in df_contratos.iterrows()]
    contratos_dict = {row['nombre']: row['id'] for _, row in df_contratos.iterrows()}
    
    # Estado inicial
    if 'tarifa_contrato_seleccionado' not in st.session_state:
        st.session_state.tarifa_contrato_seleccionado = contratos_lista[0] if contratos_lista else None
    
    # Formulario
    with st.form(key="form_tarifas", clear_on_submit=False):
        col1, col2 = st.columns(2)
        
        with col1:
            # Selector de contrato
            contrato = st.selectbox(
                "Contrato *",
                options=contratos_lista,
                index=contratos_lista.index(st.session_state.tarifa_contrato_seleccionado) if st.session_state.tarifa_contrato_seleccionado in contratos_lista else 0,
                key="sel_contrato_tarifa"
            )
            
            # Actualizar estado
            st.session_state.tarifa_contrato_seleccionado = contrato
            
            # Mostrar el ID para debug
            st.caption(f"ID Contrato: {contratos_dict[contrato]}")
            
            # Cargar clientes del contrato seleccionado
            id_contrato = contratos_dict[contrato]
            df_clientes = pd.read_sql(f"""
                SELECT id, nombre, codigo 
                FROM clientes 
                WHERE activo = 1 AND id_contrato = {id_contrato}
                ORDER BY nombre
            """, conn)
            
            clientes_lista = ["(Todos los clientes)"] + [f"{row['nombre']} ({row['codigo']})" for _, row in df_clientes.iterrows()]
            cliente = st.selectbox("Cliente", options=clientes_lista, key="sel_cliente_tarifa")
            
            # Tipo perforación
            df_tipos = pd.read_sql("SELECT id, nombre FROM tipo_perforacion WHERE activo = 1 ORDER BY nombre", conn)
            tipos_lista = [row['nombre'] for _, row in df_tipos.iterrows()]
            tipos_dict = {row['nombre']: row['id'] for _, row in df_tipos.iterrows()}
            
            tipo_perf = st.selectbox("Tipo de Perforación *", options=tipos_lista, key="sel_tipo_tarifa")
        
        with col2:
            tarifa_valor = st.number_input("Tarifa *", min_value=0.0, step=0.01, format="%.2f", key="num_tarifa")
            fecha_desde = st.date_input("Período Desde *", value=date.today(), key="date_desde_tarifa")
            fecha_hasta = st.date_input("Período Hasta (opcional)", value=None, key="date_hasta_tarifa")
        
        observacion = st.text_input("Observación (opcional)", key="text_obs_tarifa")
        
        # Botón submit
        submitted = st.form_submit_button("💾 Guardar Tarifa", use_container_width=True, type="primary")
        
        if submitted:
            if not contrato or not tipo_perf or not tarifa_valor:
                st.error("❌ Los campos marcados con * son obligatorios")
            else:
                try:
                    id_contrato = contratos_dict[contrato]
                    id_tipo = tipos_dict[tipo_perf]
                    id_cliente = None if cliente == "(Todos los clientes)" else df_clientes[df_clientes.apply(lambda r: f"{r['nombre']} ({r['codigo']})" == cliente, axis=1)]['id'].values[0]
                    
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO tarifas 
                        (id_contrato, id_cliente, id_tipo_perforacion, tarifa, periodo_desde, periodo_hasta, observacion)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (id_contrato, id_cliente, id_tipo, tarifa_valor,
                          fecha_desde.strftime('%Y-%m-%d'),
                          fecha_hasta.strftime('%Y-%m-%d') if fecha_hasta else None,
                          observacion if observacion else None))
                    conn.commit()
                    st.success("✅ Tarifa guardada correctamente")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    # Mostrar tarifas existentes
    st.markdown("---")
    st.markdown("#### 💰 Tarifas Registradas")
    
    df_tarifas = pd.read_sql("""
        SELECT t.id,
               co.nombre as contrato,
               cl.nombre as cliente,
               tp.nombre as tipo_perforacion,
               t.tarifa,
               t.periodo_desde,
               t.periodo_hasta
        FROM tarifas t
        JOIN contratos co ON t.id_contrato = co.id
        JOIN tipo_perforacion tp ON t.id_tipo_perforacion = tp.id
        LEFT JOIN clientes cl ON t.id_cliente = cl.id
        ORDER BY t.periodo_desde DESC
        LIMIT 50
    """, conn)
    
    if not df_tarifas.empty:
        df_show = df_tarifas.copy()
        df_show['cliente'] = df_show['cliente'].fillna('(Todos)')
        df_show['tarifa'] = df_show['tarifa'].apply(lambda x: f"S/. {x:,.2f}")
        df_show.columns = ['ID', 'Contrato', 'Cliente', 'Tipo Perf.', 'Tarifa', 'Desde', 'Hasta']
        st.dataframe(df_show, use_container_width=True, hide_index=True)
    else:
        st.info("📌 No hay tarifas registradas")



# PESTAÑAS
# ============================================================================
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
    "📋 Contratos", 
    "👥 Clientes", 
    "🔩 Tipo Perforación", 
    "🏷️ Familias", 
    "📝 Conceptos",
    "🎯 Objetivos", 
    "💰 Tarifas",
    "⚙️ Valores por defecto",
    "Valores reales"
])

# ====================================================================
# TAB 1: CONTRATOS
# ====================================================================
with tab1:
    st.markdown("### 📋 Gestión de Contratos")
    
    with st.container(border=True):
        st.markdown("#### ➕ Agregar Nuevo Contrato")
        
        with st.form("form_contrato"):
            col1, col2 = st.columns(2)
            with col1:
                nombre = st.text_input("Nombre del Contrato *")
            with col2:
                tipo = st.selectbox("Tipo de Operación *", ["SUPERFICIAL", "SUBTERRANEA"])
            
            activo = st.checkbox("Activo", value=True)
            
            if st.form_submit_button("Guardar Contrato", use_container_width=True):
                if not nombre or not tipo:
                    st.error("Nombre y tipo son obligatorios")
                else:
                    try:
                        cursor = conn.cursor()
                        cursor.execute('''
                            INSERT INTO contratos (nombre, tipo_operacion, activo)
                            VALUES (?, ?, ?)
                        ''', (nombre, tipo, 1 if activo else 0))
                        conn.commit()
                        st.success("✅ Contrato guardado correctamente")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
    
    st.markdown("#### 📋 Contratos Registrados")
    df_contratos = pd.read_sql("SELECT id, nombre, tipo_operacion, activo FROM contratos ORDER BY nombre", conn)
    
    if not df_contratos.empty:
        df_show = df_contratos.copy()
        df_show['activo'] = df_show['activo'].apply(lambda x: '✅' if x else '❌')
        df_show.columns = ['ID', 'Nombre', 'Tipo', 'Activo']
        st.dataframe(df_show, use_container_width=True, hide_index=True)
    else:
        st.info("No hay contratos registrados")

# ====================================================================
# TAB 2: CLIENTES
# ====================================================================
with tab2:
    st.markdown("### 👥 Gestión de Clientes")
    
    with st.container(border=True):
        st.markdown("#### ➕ Agregar Nuevo Cliente")
        
        with st.form("form_cliente"):
            opciones_contrato = cargar_opciones_contrato()
            
            col1, col2 = st.columns(2)
            with col1:
                contrato_sel = st.selectbox(
                    "Contrato *", 
                    options=list(opciones_contrato.keys())
                )
                nombre = st.text_input("Nombre del Cliente *")
            with col2:
                codigo = st.text_input("Código (siglas) *")
                activo = st.checkbox("Activo", value=True)
            
            if st.form_submit_button("Guardar Cliente", use_container_width=True):
                if not contrato_sel or not nombre or not codigo:
                    st.error("Todos los campos son obligatorios")
                else:
                    try:
                        id_contrato = opciones_contrato[contrato_sel]
                        cursor = conn.cursor()
                        cursor.execute('''
                            INSERT INTO clientes (nombre, codigo, id_contrato, activo)
                            VALUES (?, ?, ?, ?)
                        ''', (nombre, codigo, id_contrato, 1 if activo else 0))
                        conn.commit()
                        st.success("✅ Cliente guardado correctamente")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
    
    st.markdown("#### 👥 Clientes Registrados")
    df_clientes = pd.read_sql("""
        SELECT c.id, c.nombre, c.codigo, co.nombre as contrato, c.activo 
        FROM clientes c
        JOIN contratos co ON c.id_contrato = co.id
        ORDER BY c.nombre
    """, conn)
    
    if not df_clientes.empty:
        df_show = df_clientes.copy()
        df_show['activo'] = df_show['activo'].apply(lambda x: '✅' if x else '❌')
        df_show.columns = ['ID', 'Nombre', 'Código', 'Contrato', 'Activo']
        st.dataframe(df_show, use_container_width=True, hide_index=True)
    else:
        st.info("No hay clientes registrados")

# ====================================================================
# TAB 3: TIPO PERFORACIÓN
# ====================================================================
with tab3:
    st.markdown("### 🔩 Gestión de Tipos de Perforación")
    
    with st.container(border=True):
        st.markdown("#### ➕ Agregar Nuevo Tipo")
        
        with st.form("form_tipo"):
            col1, col2 = st.columns(2)
            with col1:
                nombre = st.text_input("Nombre del Tipo *")
            with col2:
                activo = st.checkbox("Activo", value=True)
            
            descripcion = st.text_area("Descripción (opcional)")
            
            if st.form_submit_button("Guardar Tipo", use_container_width=True):
                if not nombre:
                    st.error("El nombre es obligatorio")
                else:
                    try:
                        cursor = conn.cursor()
                        cursor.execute('''
                            INSERT INTO tipo_perforacion (nombre, descripcion, activo)
                            VALUES (?, ?, ?)
                        ''', (nombre, descripcion if descripcion else None, 1 if activo else 0))
                        conn.commit()
                        st.success("✅ Tipo guardado correctamente")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
    
    st.markdown("#### 🔩 Tipos Registrados")
    df_tipos = pd.read_sql("SELECT id, nombre, descripcion, activo FROM tipo_perforacion ORDER BY nombre", conn)
    
    if not df_tipos.empty:
        df_show = df_tipos.copy()
        df_show['activo'] = df_show['activo'].apply(lambda x: '✅' if x else '❌')
        df_show.columns = ['ID', 'Nombre', 'Descripción', 'Activo']
        st.dataframe(df_show, use_container_width=True, hide_index=True)
    else:
        st.info("No hay tipos registrados")

# ====================================================================
# TAB 4: FAMILIAS
# ====================================================================
with tab4:
    st.markdown("### 🏷️ Gestión de Familias")
    
    with st.container(border=True):
        st.markdown("#### ➕ Agregar Nueva Familia")
        
        with st.form("form_familia"):
            nombre = st.text_input("Nombre de la Familia *")
            descripcion = st.text_area("Descripción (opcional)")
            
            if st.form_submit_button("Guardar Familia", use_container_width=True):
                if not nombre:
                    st.error("El nombre es obligatorio")
                else:
                    try:
                        cursor = conn.cursor()
                        cursor.execute('''
                            INSERT INTO familia (nombre, descripcion)
                            VALUES (?, ?)
                        ''', (nombre, descripcion if descripcion else None))
                        conn.commit()
                        st.success("✅ Familia guardada correctamente")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
    
    st.markdown("#### 🏷️ Familias Registradas")
    df_familias = pd.read_sql("SELECT id, nombre, descripcion FROM familia ORDER BY nombre", conn)
    
    if not df_familias.empty:
        df_show = df_familias.copy()
        df_show.columns = ['ID', 'Nombre', 'Descripción']
        st.dataframe(df_show, use_container_width=True, hide_index=True)
    else:
        st.info("No hay familias registradas")

# ====================================================================
# TAB 5: CONCEPTOS
# ====================================================================
with tab5:
    st.markdown("### 📝 Gestión de Conceptos")
    
    with st.container(border=True):
        st.markdown("#### ➕ Agregar Nuevo Concepto")
        
        with st.form("form_concepto"):
            col1, col2 = st.columns(2)
            with col1:
                concepto = st.text_input("Concepto *")
            with col2:
                activo = st.checkbox("Activo", value=True)
            
            descripcion = st.text_area("Descripción (opcional)")
            
            if st.form_submit_button("Guardar Concepto", use_container_width=True):
                if not concepto:
                    st.error("El concepto es obligatorio")
                else:
                    try:
                        cursor = conn.cursor()
                        cursor.execute('''
                            INSERT INTO conceptos_gastos (concepto, descripcion, activo)
                            VALUES (?, ?, ?)
                        ''', (concepto, descripcion if descripcion else None, 1 if activo else 0))
                        conn.commit()
                        st.success("✅ Concepto guardado correctamente")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
    
    st.markdown("#### 📝 Conceptos Registrados")
    df_conceptos = pd.read_sql("SELECT id, concepto, descripcion, activo FROM conceptos_gastos ORDER BY concepto", conn)
    
    if not df_conceptos.empty:
        df_show = df_conceptos.copy()
        df_show['activo'] = df_show['activo'].apply(lambda x: '✅' if x else '❌')
        df_show.columns = ['ID', 'Concepto', 'Descripción', 'Activo']
        st.dataframe(df_show, use_container_width=True, hide_index=True)
    else:
        st.info("No hay conceptos registrados")

# ====================================================================
# TAB 6: OBJETIVOS
# ====================================================================
with tab6:
    st.markdown("### 🎯 Gestión de Objetivos")
    
    # ================================================================
    # KEY DINÁMICA PARA EVITAR CACHÉ DE STREAMLIT
    # ================================================================
    import time
    import hashlib
    
    # Generar una key única basada en el tiempo
    if 'tab6_init_time' not in st.session_state:
        st.session_state.tab6_init_time = time.time()
    
    # Key dinámica para los selectbox
    dynamic_key = f"tab6_contrato_{hashlib.md5(str(st.session_state.tab6_init_time).encode()).hexdigest()[:8]}"
    
    # ================================================================
    # CARGAR DATOS
    # ================================================================
    @st.cache_data(ttl=60)
    def cargar_contratos_obj():
        return pd.read_sql("SELECT id, nombre FROM contratos WHERE activo = 1 ORDER BY id", conn)
    
    @st.cache_data(ttl=60)
    def cargar_tipos_obj():
        return pd.read_sql("SELECT id, nombre FROM tipo_perforacion WHERE activo = 1 ORDER BY nombre", conn)
    
    @st.cache_data(ttl=60)
    def cargar_familias_obj():
        return pd.read_sql("SELECT id, nombre FROM familia ORDER BY nombre", conn)
    
    df_cont = cargar_contratos_obj()
    df_tipos = cargar_tipos_obj()
    df_familias = cargar_familias_obj()
    
    # Convertir a listas
    lista_contratos = df_cont['nombre'].tolist()
    dict_contratos = dict(zip(df_cont['nombre'], df_cont['id']))
    lista_tipos = df_tipos['nombre'].tolist()
    dict_tipos = dict(zip(df_tipos['nombre'], df_tipos['id']))
    lista_familias = df_familias['nombre'].tolist()
    dict_familias = dict(zip(df_familias['nombre'], df_familias['id']))
    
    # ================================================================
    # SELECTOR DE CONTRATO CON KEY DINÁMICA
    # ================================================================
    contrato_nombre = st.selectbox(
        "Contrato *",
        options=lista_contratos,
        key=dynamic_key
    )
    
    # Obtener ID del contrato
    id_contrato = dict_contratos[contrato_nombre]
    
    # Mostrar feedback visual
    st.success(f"📌 Contrato seleccionado: **{contrato_nombre}** (ID: {id_contrato})")
    
    # ================================================================
    # CARGAR CLIENTES DEL CONTRATO SELECCIONADO
    # ================================================================
    df_clientes = pd.read_sql(f"""
        SELECT id, nombre, codigo 
        FROM clientes 
        WHERE activo = 1 AND id_contrato = {id_contrato}
        ORDER BY nombre
    """, conn)
    
    # Crear diccionario de clientes para búsqueda fácil
    dict_clientes = {}
    for _, row in df_clientes.iterrows():
        dict_clientes[f"{row['nombre']} ({row['codigo']})"] = row['id']
    
    # Mostrar cuántos clientes se encontraron
    if len(df_clientes) > 0:
        st.caption(f"✅ {len(df_clientes)} cliente(s) encontrado(s) para este contrato")
    else:
        st.warning("⚠️ No hay clientes registrados para este contrato")
    
    # ================================================================
    # FORMULARIO PRINCIPAL
    # ================================================================
    with st.form(key=f"tab6_form_{dynamic_key}"):
        col1, col2 = st.columns(2)
        
        with col1:
            # Cliente
            if len(df_clientes) > 0:
                lista_clientes = ["(Todos los clientes)"] + list(dict_clientes.keys())
            else:
                lista_clientes = ["(Todos los clientes)"]
            
            cliente_label = st.selectbox(
                "Cliente",
                options=lista_clientes,
                key=f"tab6_cliente_{dynamic_key}"
            )
            
            # Tipo de Perforación
            tipo_nombre = st.selectbox(
                "Tipo de Perforación *",
                options=lista_tipos,
                key=f"tab6_tipo_{dynamic_key}"
            )
        
        with col2:
            # Familia
            familia_nombre = st.selectbox(
                "Familia *",
                options=lista_familias,
                key=f"tab6_familia_{dynamic_key}"
            )
            
            # Objetivo
            objetivo_valor = st.number_input(
                "Objetivo *",
                min_value=0.0,
                step=0.1,
                format="%.2f",
                key=f"tab6_objetivo_{dynamic_key}"
            )
            
            # Fechas
            fecha_desde = st.date_input(
                "Período Desde *",
                value=date.today(),
                key=f"tab6_desde_{dynamic_key}"
            )
            fecha_hasta = st.date_input(
                "Período Hasta (opcional)",
                value=None,
                key=f"tab6_hasta_{dynamic_key}"
            )
        
        # Observación
        observacion = st.text_input(
            "Observación (opcional)",
            key=f"tab6_obs_{dynamic_key}"
        )
        
        # Botón guardar
        submitted = st.form_submit_button(
            "💾 Guardar Objetivo",
            use_container_width=True,
            type="primary"
        )
        
        if submitted:
            # Validaciones
            if not contrato_nombre or not tipo_nombre or not familia_nombre or not objetivo_valor:
                st.error("❌ Los campos marcados con * son obligatorios")
            else:
                try:
                    # Obtener IDs
                    id_tipo = dict_tipos[tipo_nombre]
                    id_familia = dict_familias[familia_nombre]
                    
                    # Obtener ID del cliente correctamente
                    id_cliente = None
                    if cliente_label != "(Todos los clientes)":
                        if cliente_label in dict_clientes:
                            id_cliente = dict_clientes[cliente_label]
                            st.write(f"🔍 Cliente encontrado: {cliente_label} -> ID: {id_cliente}")
                        else:
                            st.warning(f"⚠️ Cliente '{cliente_label}' no encontrado en el diccionario")
                    
                    # Insertar en BD
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO objetivos 
                        (id_contrato, id_cliente, id_tipo_perforacion, id_familia, objetivo, 
                         periodo_desde, periodo_hasta, observacion)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        id_contrato, 
                        id_cliente, 
                        id_tipo, 
                        id_familia, 
                        objetivo_valor,
                        fecha_desde.strftime('%Y-%m-%d'),
                        fecha_hasta.strftime('%Y-%m-%d') if fecha_hasta else None,
                        observacion if observacion else None
                    ))
                    conn.commit()
                    
                    st.success("✅ Objetivo guardado correctamente")
                    
                    # Recargar la página
                    time.sleep(1)
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error al guardar: {str(e)}")
    
    # ================================================================
    # LISTA DE OBJETIVOS REGISTRADOS
    # ================================================================
    st.markdown("---")
    st.markdown("#### 🎯 Objetivos Registrados")
    
    df_objetivos = pd.read_sql("""
        SELECT o.id,
               co.nombre as contrato,
               cl.nombre as cliente,
               tp.nombre as tipo_perforacion,
               f.nombre as familia,
               o.objetivo,
               o.periodo_desde,
               o.periodo_hasta,
               o.observacion
        FROM objetivos o
        JOIN contratos co ON o.id_contrato = co.id
        JOIN tipo_perforacion tp ON o.id_tipo_perforacion = tp.id
        JOIN familia f ON o.id_familia = f.id
        LEFT JOIN clientes cl ON o.id_cliente = cl.id
        ORDER BY o.periodo_desde DESC
        LIMIT 100
    """, conn)
    
    if not df_objetivos.empty:
        df_show = df_objetivos.copy()
        df_show['cliente'] = df_show['cliente'].fillna('(Todos)')
        df_show.columns = ['ID', 'Contrato', 'Cliente', 'Tipo Perf.', 'Familia', 'Objetivo', 'Desde', 'Hasta', 'Observación']
        st.dataframe(df_show, use_container_width=True, hide_index=True)
        
        # Opción para eliminar objetivos
        with st.expander("🗑️ Eliminar Objetivo"):
            objetivo_id = st.number_input("ID del Objetivo a eliminar", min_value=1, step=1, key="delete_objetivo_id")
            if st.button("Eliminar Objetivo", type="secondary"):
                try:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM objetivos WHERE id = ?", (objetivo_id,))
                    conn.commit()
                    st.success(f"✅ Objetivo ID {objetivo_id} eliminado correctamente")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    else:
        st.info("📌 No hay objetivos registrados. Use el formulario superior para agregar.")




# ====================================================================
# TAB 7: TARIFAS
# ====================================================================
with tab7:
    st.markdown("### 💰 Gestión de Tarifas")
    
    # ================================================================
    # KEY DINÁMICA PARA EVITAR CACHÉ DE STREAMLIT
    # ================================================================
    import time
    import hashlib
    
    # Generar una key única basada en el tiempo
    if 'tab7_init_time' not in st.session_state:
        st.session_state.tab7_init_time = time.time()
    
    # Key dinámica para el selectbox principal
    dynamic_key = f"tab7_contrato_{hashlib.md5(str(st.session_state.tab7_init_time).encode()).hexdigest()[:8]}"
    
    # ================================================================
    # CARGAR DATOS
    # ================================================================
    @st.cache_data(ttl=60)
    def cargar_contratos_tarifa():
        return pd.read_sql("SELECT id, nombre FROM contratos WHERE activo = 1 ORDER BY id", conn)
    
    @st.cache_data(ttl=60)
    def cargar_tipos_tarifa():
        return pd.read_sql("SELECT id, nombre FROM tipo_perforacion WHERE activo = 1 ORDER BY nombre", conn)
    
    df_cont = cargar_contratos_tarifa()
    df_tipos = cargar_tipos_tarifa()
    
    # Convertir a listas
    lista_contratos = df_cont['nombre'].tolist()
    dict_contratos = dict(zip(df_cont['nombre'], df_cont['id']))
    lista_tipos = df_tipos['nombre'].tolist()
    dict_tipos = dict(zip(df_tipos['nombre'], df_tipos['id']))
    
    # ================================================================
    # SELECTOR DE CONTRATO CON KEY DINÁMICA
    # ================================================================
    contrato_nombre = st.selectbox(
        "Contrato *",
        options=lista_contratos,
        key=dynamic_key
    )
    
    # Obtener ID del contrato
    id_contrato = dict_contratos[contrato_nombre]
    
    # Mostrar feedback visual
    st.success(f"📌 Contrato seleccionado: **{contrato_nombre}** (ID: {id_contrato})")
    
    # ================================================================
    # CARGAR CLIENTES DEL CONTRATO SELECCIONADO
    # ================================================================
    df_clientes = pd.read_sql(f"""
        SELECT id, nombre, codigo 
        FROM clientes 
        WHERE activo = 1 AND id_contrato = {id_contrato}
        ORDER BY nombre
    """, conn)
    
    # Crear diccionario de clientes para búsqueda fácil
    dict_clientes = {}
    for _, row in df_clientes.iterrows():
        dict_clientes[f"{row['nombre']} ({row['codigo']})"] = row['id']
    
    # Mostrar cuántos clientes se encontraron
    if len(df_clientes) > 0:
        st.caption(f"✅ {len(df_clientes)} cliente(s) encontrado(s) para este contrato")
    else:
        st.warning("⚠️ No hay clientes registrados para este contrato")
    
    # ================================================================
    # FORMULARIO PRINCIPAL
    # ================================================================
    with st.form(key=f"tab7_form_{dynamic_key}"):
        col1, col2 = st.columns(2)
        
        with col1:
            # Cliente
            if len(df_clientes) > 0:
                lista_clientes = ["(Todos los clientes)"] + list(dict_clientes.keys())
            else:
                lista_clientes = ["(Todos los clientes)"]
            
            cliente_label = st.selectbox(
                "Cliente",
                options=lista_clientes,
                key=f"tab7_cliente_{dynamic_key}"
            )
            
            # Tipo de Perforación
            tipo_nombre = st.selectbox(
                "Tipo de Perforación *",
                options=lista_tipos,
                key=f"tab7_tipo_{dynamic_key}"
            )
        
        with col2:
            # Tarifa
            tarifa_valor = st.number_input(
                "Tarifa *",
                min_value=0.0,
                step=0.01,
                format="%.2f",
                key=f"tab7_tarifa_{dynamic_key}"
            )
            
            # Fechas
            fecha_desde = st.date_input(
                "Período Desde *",
                value=date.today(),
                key=f"tab7_desde_{dynamic_key}"
            )
            fecha_hasta = st.date_input(
                "Período Hasta (opcional)",
                value=None,
                key=f"tab7_hasta_{dynamic_key}"
            )
        
        # Observación
        observacion = st.text_input(
            "Observación (opcional)",
            key=f"tab7_obs_{dynamic_key}"
        )
        
        # Botón guardar
        submitted = st.form_submit_button(
            "💾 Guardar Tarifa",
            use_container_width=True,
            type="primary"
        )
        
        if submitted:
            # Validaciones
            if not contrato_nombre or not tipo_nombre or not tarifa_valor:
                st.error("❌ Los campos marcados con * son obligatorios")
            else:
                try:
                    # Obtener IDs
                    id_tipo = dict_tipos[tipo_nombre]
                    
                    # Obtener ID del cliente correctamente
                    id_cliente = None
                    if cliente_label != "(Todos los clientes)":
                        if cliente_label in dict_clientes:
                            id_cliente = dict_clientes[cliente_label]
                        else:
                            st.warning(f"⚠️ Cliente '{cliente_label}' no encontrado")
                    
                    # Insertar en BD
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO tarifas 
                        (id_contrato, id_cliente, id_tipo_perforacion, tarifa, 
                         periodo_desde, periodo_hasta, observacion)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        id_contrato, 
                        id_cliente, 
                        id_tipo, 
                        tarifa_valor,
                        fecha_desde.strftime('%Y-%m-%d'),
                        fecha_hasta.strftime('%Y-%m-%d') if fecha_hasta else None,
                        observacion if observacion else None
                    ))
                    conn.commit()
                    
                    st.success("✅ Tarifa guardada correctamente")
                    
                    # Recargar la página
                    time.sleep(1)
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error al guardar: {str(e)}")
    
    # ================================================================
    # LISTA DE TARIFAS REGISTRADAS
    # ================================================================
    st.markdown("---")
    st.markdown("#### 💰 Tarifas Registradas")
    
    df_tarifas = pd.read_sql("""
        SELECT t.id,
               co.nombre as contrato,
               cl.nombre as cliente,
               tp.nombre as tipo_perforacion,
               t.tarifa,
               t.periodo_desde,
               t.periodo_hasta,
               t.observacion
        FROM tarifas t
        JOIN contratos co ON t.id_contrato = co.id
        JOIN tipo_perforacion tp ON t.id_tipo_perforacion = tp.id
        LEFT JOIN clientes cl ON t.id_cliente = cl.id
        ORDER BY t.periodo_desde DESC
        LIMIT 100
    """, conn)
    
    if not df_tarifas.empty:
        df_show = df_tarifas.copy()
        df_show['cliente'] = df_show['cliente'].fillna('(Todos)')
        df_show['tarifa'] = df_show['tarifa'].apply(lambda x: f"S/. {x:,.2f}")
        df_show.columns = ['ID', 'Contrato', 'Cliente', 'Tipo Perf.', 'Tarifa', 'Desde', 'Hasta', 'Observación']
        st.dataframe(df_show, use_container_width=True, hide_index=True)
        
        # Opción para eliminar tarifas
        with st.expander("🗑️ Eliminar Tarifa"):
            tarifa_id = st.number_input("ID de la Tarifa a eliminar", min_value=1, step=1, key="delete_tarifa_id")
            if st.button("Eliminar Tarifa", type="secondary"):
                try:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM tarifas WHERE id = ?", (tarifa_id,))
                    conn.commit()
                    st.success(f"✅ Tarifa ID {tarifa_id} eliminada correctamente")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    else:
        st.info("📌 No hay tarifas registradas. Use el formulario superior para agregar.")

# ====================================================================
with tab8:
    st.markdown("### ⚙️ Valores por Defecto")
    st.markdown("Configura los valores que se mostrarán mientras no haya liquidación real")
    
    st.info("""
    **Instrucciones:**
    - Selecciona Contrato, Cliente y Concepto
    - Ingresa el monto que DEBES COBRAR (por defecto)
    - Ingresa el monto que GASTAS (por defecto)
    - Estos valores se usarán en Resultados hasta que cargues la liquidación real
    """)
    
    # Obtener opciones
    opciones_contrato = cargar_opciones_contrato()
    opciones_concepto = cargar_opciones_concepto()
    
    col1, col2 = st.columns(2)
    
    with col1:
        contrato_def = st.selectbox(
            "Contrato *",
            options=list(opciones_contrato.keys()),
            key="def_contrato"
        )
        
        if contrato_def:
            id_contrato_def = opciones_contrato[contrato_def]
            opciones_cliente_def = cargar_opciones_cliente(id_contrato_def)
            cliente_def = st.selectbox(
                "Cliente *",
                options=list(opciones_cliente_def.keys()),
                key="def_cliente"
            )
            id_cliente_def = opciones_cliente_def[cliente_def] if cliente_def else None
        else:
            cliente_def = None
            id_cliente_def = None
    
    with col2:
        concepto_def = st.selectbox(
            "Concepto *",
            options=list(opciones_concepto.keys()),
            key="def_concepto"
        )
        id_concepto_def = opciones_concepto[concepto_def] if concepto_def else None
        
        monto_cobrar = st.number_input(
            "Monto a Cobrar (S/) - Por defecto",
            min_value=0.0,
            step=100.0,
            format="%.2f",
            key="def_cobrar"
        )
        
        monto_gasto = st.number_input(
            "Monto Gasto (S/) - Por defecto",
            min_value=0.0,
            step=100.0,
            format="%.2f",
            key="def_gasto"
        )
    
    # Botón para guardar
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        if st.button("💾 Guardar Valores por Defecto", type="primary", use_container_width=True, key="btn_guardar_def"):
            if not contrato_def or not cliente_def or not concepto_def:
                st.error("Todos los campos son obligatorios")
            else:
                try:
                    cursor = conn.cursor()
                    
                    # Verificar si ya existe
                    cursor.execute("""
                        SELECT id FROM valores_por_defecto 
                        WHERE id_contrato = ? AND id_cliente = ? AND id_concepto = ?
                    """, (id_contrato_def, id_cliente_def, id_concepto_def))
                    
                    existe = cursor.fetchone()
                    
                    if existe:
                        # Actualizar
                        cursor.execute("""
                            UPDATE valores_por_defecto 
                            SET monto_cobrar_default = ?, monto_gasto_default = ?
                            WHERE id_contrato = ? AND id_cliente = ? AND id_concepto = ?
                        """, (monto_cobrar, monto_gasto, id_contrato_def, id_cliente_def, id_concepto_def))
                        st.success("✅ Valores por defecto actualizados")
                    else:
                        # Insertar
                        cursor.execute("""
                            INSERT INTO valores_por_defecto 
                            (id_contrato, id_cliente, id_concepto, monto_cobrar_default, monto_gasto_default)
                            VALUES (?, ?, ?, ?, ?)
                        """, (id_contrato_def, id_cliente_def, id_concepto_def, monto_cobrar, monto_gasto))
                        st.success("✅ Valores por defecto guardados")
                    
                    conn.commit()
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    with col_b2:
        if st.button("🔄 Limpiar", use_container_width=True, key="btn_limpiar_def"):
            st.rerun()
    
    st.markdown("---")
    
    # Lista de valores por defecto registrados
    st.markdown("#### 📋 Valores por Defecto Registrados")
    
    df_defecto = pd.read_sql("""
        SELECT 
            vd.id,
            ct.nombre as contrato,
            cl.nombre as cliente,
            cg.concepto,
            vd.monto_cobrar_default,
            vd.monto_gasto_default
        FROM valores_por_defecto vd
        JOIN contratos ct ON vd.id_contrato = ct.id
        JOIN clientes cl ON vd.id_cliente = cl.id
        JOIN conceptos_gastos cg ON vd.id_concepto = cg.id
        ORDER BY ct.nombre, cl.nombre, cg.concepto
    """, conn)
    
    if not df_defecto.empty:
        df_show = df_defecto.copy()
        df_show['monto_cobrar_default'] = df_show['monto_cobrar_default'].apply(lambda x: f"S/. {x:,.2f}" if x else "-")
        df_show['monto_gasto_default'] = df_show['monto_gasto_default'].apply(lambda x: f"S/. {x:,.2f}" if x else "-")
        df_show.columns = ['ID', 'Contrato', 'Cliente', 'Concepto', 'Debo Cobrar (default)', 'Gasto (default)']
        st.dataframe(df_show, use_container_width=True, hide_index=True)
        
        # Opción para eliminar
        st.markdown("#### 🗑️ Eliminar Valor por Defecto")
        
        opciones_eliminar = {}
        for _, row in df_defecto.iterrows():
            opciones_eliminar[f"{row['id']} - {row['contrato']} | {row['cliente']} | {row['concepto']}"] = row['id']
        
        seleccion_eliminar = st.selectbox(
            "Seleccionar para eliminar",
            options=list(opciones_eliminar.keys()),
            key="select_eliminar_def"
        )
        
        if seleccion_eliminar and st.button("🗑️ Eliminar", use_container_width=True, key="btn_eliminar_def"):
            id_eliminar = opciones_eliminar[seleccion_eliminar]
            try:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM valores_por_defecto WHERE id = ?", (id_eliminar,))
                conn.commit()
                st.success("✅ Valor por defecto eliminado")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {str(e)}")
    else:
        st.info("No hay valores por defecto registrados")


# TAB 9: LIQUIDACIÓN DE GASTOS (Valores Reales)
# ====================================================================
with tab9:
    st.markdown("### 📋 Liquidación de Gastos")
    st.markdown("Valores REALES de Personal, EPS, Asistencia Técnica, etc. (CIERRE DE MES)")
    
    st.info("""
    **Instrucciones:**
    - Selecciona Contrato, Cliente, Concepto y Período (YYYY-MM)
    - Ingresa los valores REALES del mes
    - Estos valores reemplazarán a los valores por defecto en Resultados
    - Puedes editar o eliminar liquidaciones existentes desde la tabla
    """)
    
    # Obtener opciones
    opciones_contrato = cargar_opciones_contrato()
    opciones_concepto = cargar_opciones_concepto()
    
    col1, col2 = st.columns(2)
    
    with col1:
        contrato_liq = st.selectbox(
            "Contrato *",
            options=list(opciones_contrato.keys()),
            key="liq_contrato"
        )
        
        if contrato_liq:
            id_contrato_liq = opciones_contrato[contrato_liq]
            opciones_cliente_liq = cargar_opciones_cliente(id_contrato_liq)
            cliente_liq = st.selectbox(
                "Cliente *",
                options=list(opciones_cliente_liq.keys()),
                key="liq_cliente"
            )
            id_cliente_liq = opciones_cliente_liq[cliente_liq] if cliente_liq else None
        else:
            cliente_liq = None
            id_cliente_liq = None
        
        periodo_liq = st.text_input(
            "Período (YYYY-MM) *",
            value=datetime.now().strftime("%Y-%m"),
            key="liq_periodo"
        )
    
    with col2:
        concepto_liq = st.selectbox(
            "Concepto *",
            options=list(opciones_concepto.keys()),
            key="liq_concepto"
        )
        id_concepto_liq = opciones_concepto[concepto_liq] if concepto_liq else None
        
        monto_cobrado = st.number_input(
            "Monto a Cobrar (S/)",
            min_value=0.0,
            step=100.0,
            format="%.2f",
            key="liq_cobrado"
        )
        
        monto_real = st.number_input(
            "Monto Real (S/)",
            min_value=0.0,
            step=100.0,
            format="%.2f",
            key="liq_real"
        )
    
    # Botón para guardar
    col_b1, col_b2, col_b3 = st.columns(3)
    with col_b1:
        if st.button("💾 Guardar Liquidación", type="primary", use_container_width=True, key="btn_guardar_liq"):
            if not contrato_liq or not cliente_liq or not concepto_liq or not periodo_liq:
                st.error("Todos los campos son obligatorios")
            else:
                try:
                    cursor = conn.cursor()
                    
                    # Verificar si ya existe
                    cursor.execute("""
                        SELECT id FROM liquidacion_gastos 
                        WHERE id_contrato = ? AND id_cliente = ? 
                          AND id_concepto = ? AND periodo = ?
                    """, (id_contrato_liq, id_cliente_liq, id_concepto_liq, periodo_liq))
                    
                    existe = cursor.fetchone()
                    
                    if existe:
                        # Actualizar
                        cursor.execute("""
                            UPDATE liquidacion_gastos 
                            SET monto_cobrado = ?, monto_real = ?
                            WHERE id_contrato = ? AND id_cliente = ? 
                              AND id_concepto = ? AND periodo = ?
                        """, (monto_cobrado, monto_real, id_contrato_liq, id_cliente_liq, id_concepto_liq, periodo_liq))
                        st.success(f"✅ Liquidación actualizada para {periodo_liq}")
                    else:
                        # Insertar
                        cursor.execute("""
                            INSERT INTO liquidacion_gastos 
                            (id_contrato, id_cliente, id_concepto, periodo, monto_cobrado, monto_real)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (id_contrato_liq, id_cliente_liq, id_concepto_liq, periodo_liq, monto_cobrado, monto_real))
                        st.success(f"✅ Liquidación guardada para {periodo_liq}")
                    
                    conn.commit()
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    with col_b2:
        if st.button("🔄 Limpiar Formulario", use_container_width=True, key="btn_limpiar_liq"):
            st.rerun()
    
    st.markdown("---")
    
    # ===== LISTA DE LIQUIDACIONES REGISTRADAS =====
    st.markdown("#### 📋 Liquidaciones Registradas")
    
    df_liquidaciones = pd.read_sql("""
        SELECT 
            lg.id,
            ct.nombre as contrato,
            cl.nombre as cliente,
            cg.concepto,
            lg.periodo,
            lg.monto_cobrado,
            lg.monto_real,
            (lg.monto_cobrado - lg.monto_real) as diferencia
        FROM liquidacion_gastos lg
        JOIN contratos ct ON lg.id_contrato = ct.id
        JOIN clientes cl ON lg.id_cliente = cl.id
        JOIN conceptos_gastos cg ON lg.id_concepto = cg.id
        ORDER BY lg.periodo DESC, ct.nombre, cl.nombre
        LIMIT 100
    """, conn)
    
    if not df_liquidaciones.empty:
        # Mostrar tabla
        df_show = df_liquidaciones.copy()
        df_show['monto_cobrado'] = df_show['monto_cobrado'].apply(lambda x: f"S/. {x:,.2f}" if x else "-")
        df_show['monto_real'] = df_show['monto_real'].apply(lambda x: f"S/. {x:,.2f}" if x else "-")
        df_show['diferencia'] = df_show['diferencia'].apply(lambda x: f"S/. {x:,.2f}" if x else "-")
        df_show.columns = ['ID', 'Contrato', 'Cliente', 'Concepto', 'Período', 'Monto Cobrar', 'Monto Real', 'Diferencia']
        
        st.dataframe(df_show, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.markdown("#### ✏️ Editar / Eliminar Liquidación")
        
        # Selector para elegir qué liquidación editar
        opciones_editar = {}
        for _, row in df_liquidaciones.iterrows():
            opciones_editar[f"{row['id']} - {row['contrato']} | {row['cliente']} | {row['concepto']} | {row['periodo']}"] = row['id']
        
        seleccion_editar = st.selectbox(
            "Seleccionar Liquidación para Editar",
            options=list(opciones_editar.keys()),
            key="select_editar_liq"
        )
        
        if seleccion_editar:
            id_seleccionado = opciones_editar[seleccion_editar]
            row_seleccionado = df_liquidaciones[df_liquidaciones['id'] == id_seleccionado].iloc[0]
            
            col_e1, col_e2 = st.columns(2)
            
            with col_e1:
                nuevo_cobrado = st.number_input(
                    "Monto a Cobrar (S/)",
                    value=float(row_seleccionado['monto_cobrado']) if row_seleccionado['monto_cobrado'] else 0.0,
                    step=100.0,
                    format="%.2f",
                    key="edit_cobrado"
                )
            
            with col_e2:
                nuevo_real = st.number_input(
                    "Monto Real (S/)",
                    value=float(row_seleccionado['monto_real']) if row_seleccionado['monto_real'] else 0.0,
                    step=100.0,
                    format="%.2f",
                    key="edit_real"
                )
            
            col_edit1, col_edit2 = st.columns(2)
            with col_edit1:
                if st.button("💾 Actualizar", use_container_width=True, key="btn_actualizar_liq"):
                    try:
                        cursor = conn.cursor()
                        cursor.execute("""
                            UPDATE liquidacion_gastos 
                            SET monto_cobrado = ?, monto_real = ?
                            WHERE id = ?
                        """, (nuevo_cobrado, nuevo_real, id_seleccionado))
                        conn.commit()
                        st.success("✅ Liquidación actualizada correctamente")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            
            with col_edit2:
                if st.button("🗑️ Eliminar", use_container_width=True, key="btn_eliminar_liq"):
                    try:
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM liquidacion_gastos WHERE id = ?", (id_seleccionado,))
                        conn.commit()
                        st.success("✅ Liquidación eliminada correctamente")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
    else:
        st.info("No hay liquidaciones registradas")
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
    fecha_actual = date.today().strftime("%d/%m/%Y")
    st.markdown(f"Última actualización: {fecha_actual}")