import streamlit as st
from supabase import create_client
import pandas as pd
import os
from typing import Optional, Dict, List, Any
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
def run_query(
    table_name: str, 
    select: str = "*", 
    filters: Optional[Dict[str, Any]] = None,
    order_by: Optional[str] = None,
    ascending: bool = True
) -> pd.DataFrame:
    """
    Ejecuta consulta SELECT en Supabase y retorna DataFrame
    
    Args:
        table_name: Nombre de la tabla o vista
        select: Columnas a seleccionar (ej: "*", "id,nombre")
        filters: Diccionario con filtros {columna: valor}
                 Si el valor es una lista, hace IN
                 Si el valor es un string con operador (ej: ">0"), aplica condición
        order_by: Columna para ordenar
        ascending: Orden ascendente o descendente
    """
    supabase = get_supabase()
    
    # Iniciar consulta
    query = supabase.table(table_name).select(select)
    
    # Aplicar filtros
    if filters:
        for col, val in filters.items():
            if isinstance(val, list):
                # Si es lista, usar IN
                if val:
                    query = query.in_(col, val)
            elif isinstance(val, str):
                # Verificar si tiene operador
                if val.startswith('>'):
                    query = query.gt(col, float(val[1:]))
                elif val.startswith('>='):
                    query = query.gte(col, float(val[2:]))
                elif val.startswith('<'):
                    query = query.lt(col, float(val[1:]))
                elif val.startswith('<='):
                    query = query.lte(col, float(val[2:]))
                elif val.startswith('!='):
                    query = query.neq(col, val[2:])
                else:
                    query = query.eq(col, val)
            else:
                query = query.eq(col, val)
    
    # Aplicar ordenamiento
    if order_by:
        query = query.order(order_by, desc=not ascending)
    
    # Ejecutar
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



def run_insert(table_name: str, data: Dict[str, Any]) -> Dict:
    """Inserta un registro en la tabla"""
    supabase = get_supabase()
    response = supabase.table(table_name).insert(data).execute()
    return response.data[0] if response.data else None

def run_delete(table_name: str, filters: Dict[str, Any]) -> bool:
    """Elimina registros que cumplan los filtros"""
    supabase = get_supabase()
    query = supabase.table(table_name).delete()
    
    for col, val in filters.items():
        if isinstance(val, list):
            query = query.in_(col, val)
        else:
            query = query.eq(col, val)
    
    response = query.execute()
    return len(response.data) > 0
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