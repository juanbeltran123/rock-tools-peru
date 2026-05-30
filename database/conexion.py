import streamlit as st
from supabase import create_client
import pandas as pd
import os
# ============================================================================
# CONEXIÓN A SUPABASE
# ============================================================================

@st.cache_resource
def get_supabase():
    """
    Conexión a Supabase.
    En local: lee desde st.secrets (archivo .streamlit/secrets.toml)
    En producción (Render): lee desde os.environ (variables de entorno)
    """
    # Intentar leer desde st.secrets primero (local)
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
    except:
        # Si falla, leer desde variables de entorno (Render)
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
    
    return create_client(url, key)

# ============================================================================
# CONSULTAS GENÉRICAS
# ============================================================================

@st.cache_data(ttl=600)
def run_query(table, select="*", filters=None, limit=None, order_by=None):
    """
    Consulta genérica a Supabase.
    
    Parámetros:
    - table: nombre de la tabla o vista (ej: "costos", "vw_venta")
    - select: columnas a seleccionar (ej: "*", "id,nombre")
    - filters: diccionario con filtros (ej: {"id_contrato": 1})
    - limit: número máximo de registros (ej: 100)
    - order_by: columna para ordenar (ej: "periodo.desc")
    
    Retorna:
    - pandas.DataFrame con los datos
    """
    supabase = get_supabase()
    query = supabase.table(table).select(select)
    
    # Aplicar filtros
    if filters:
        for key, value in filters.items():
            query = query.eq(key, value)
    
    # Aplicar ordenamiento
    if order_by:
        query = query.order(order_by)
    
    # Aplicar límite
    if limit:
        query = query.limit(limit)
    
    response = query.execute()
    
    if response.data:
        return pd.DataFrame(response.data)
    else:
        return pd.DataFrame()


@st.cache_data(ttl=600)
def run_query_in(table, column, values, select="*", limit=None):
    """
    Consulta con filtro IN (ej: periodo IN ('2026-01', '2026-02'))
    
    Parámetros:
    - table: nombre de la tabla o vista
    - column: nombre de la columna para el filtro
    - values: lista de valores (ej: ["2026-01", "2026-02"])
    - select: columnas a seleccionar
    - limit: límite de registros
    """
    supabase = get_supabase()
    query = supabase.table(table).select(select).in_(column, values)
    
    if limit:
        query = query.limit(limit)
    
    response = query.execute()
    
    if response.data:
        return pd.DataFrame(response.data)
    else:
        return pd.DataFrame()


@st.cache_data(ttl=600)
def run_query_raw(table, select="*"):
    """
    Consulta sin caché (para datos que cambian frecuentemente).
    """
    supabase = get_supabase()
    response = supabase.table(table).select(select).execute()
    
    if response.data:
        return pd.DataFrame(response.data)
    else:
        return pd.DataFrame()


# ============================================================================
# FUNCIONES AUXILIARES PARA FILTROS COMUNES
# ============================================================================

@st.cache_data(ttl=3600)
def get_periodos_disponibles():
    """Obtiene lista de períodos únicos ordenados descendente"""
    supabase = get_supabase()
    response = supabase.table("vw_general_semanal").select("periodo").execute()
    
    if response.data:
        df = pd.DataFrame(response.data)
        periodos = df['periodo'].drop_duplicates().sort_values(ascending=False).tolist()
        return periodos
    return []


@st.cache_data(ttl=3600)
def get_contratos_activos():
    """Obtiene lista de contratos activos"""
    supabase = get_supabase()
    response = supabase.table("contratos").select("id, nombre").eq("activo", 1).execute()
    
    if response.data:
        return pd.DataFrame(response.data)
    return pd.DataFrame()


@st.cache_data(ttl=3600)
def get_clientes_por_contrato(id_contrato):
    """Obtiene clientes de un contrato específico"""
    supabase = get_supabase()
    response = supabase.table("clientes").select("id, nombre").eq("id_contrato", id_contrato).eq("activo", 1).execute()
    
    if response.data:
        return pd.DataFrame(response.data)
    return pd.DataFrame()


# ============================================================================
# EJECUCIÓN DE SQL DIRECTO (USAR CON CUIDADO)
# ============================================================================

def run_sql(sql_query):
    """
    Ejecuta SQL directo en Supabase.
    IMPORTANTE: Solo funciona si tienes habilitada la extensión 'pg_net' o usas RPC.
    
    Alternativa: Usa las funciones de arriba (run_query, run_query_in) que son más seguras.
    """
    supabase = get_supabase()
    # Supabase no permite SQL directo por seguridad.
    # Esta función está como placeholder.
    # Para consultas complejas, crea una vista en Supabase y consúltala con run_query()
    raise NotImplementedError("Usa run_query() con vistas creadas en Supabase")