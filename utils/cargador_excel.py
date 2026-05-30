import streamlit as st
import pandas as pd
import re
from datetime import datetime
from database.conexion import get_supabase  # ← CAMBIADO

# ============================================================================
# FUNCIONES DE VALIDACIÓN (NO CAMBIAN)
# ============================================================================

def obtener_contrato(nombre_contrato):
    """Obtener ID del contrato desde Supabase"""
    supabase = get_supabase()
    response = supabase.table("contratos").select("id").eq("nombre", nombre_contrato).execute()
    
    if response.data:
        return response.data[0]['id']
    else:
        raise Exception(f"❌ El contrato '{nombre_contrato}' no existe en la base de datos")

def obtener_cliente(nombre_cliente, id_contrato):
    """Obtener ID del cliente desde Supabase"""
    supabase = get_supabase()
    response = supabase.table("clientes").select("id")\
        .eq("nombre", nombre_cliente)\
        .eq("id_contrato", id_contrato)\
        .execute()
    
    if response.data:
        return response.data[0]['id']
    else:
        raise Exception(f"❌ El cliente '{nombre_cliente}' no existe para el contrato ID {id_contrato}")

def obtener_tipo_perforacion(nombre_tipo):
    """Obtener ID del tipo de perforación desde Supabase"""
    if not nombre_tipo or pd.isna(nombre_tipo) or str(nombre_tipo).strip() == '':
        return None
        
    nombre_tipo = str(nombre_tipo).strip()
    supabase = get_supabase()
    response = supabase.table("tipo_perforacion").select("id").eq("nombre", nombre_tipo).execute()
    
    if response.data:
        return response.data[0]['id']
    else:
        print(f"  ⚠️ Tipo de perforación '{nombre_tipo}' no existe - fila omitida")
        return None

# ============================================================================
# FUNCIONES DE DETECCIÓN (NO CAMBIAN)
# ============================================================================

def detectar_encabezados_cliente(df):
    """Detectar automáticamente la fila donde están los encabezados de cliente"""
    print("\n🔍 Buscando encabezados de clientes...")
    
    for i in range(6, 20):
        if i >= len(df):
            break
            
        fila = df.iloc[i]
        
        for j, valor in enumerate(fila):
            if pd.notna(valor) and isinstance(valor, str):
                if 'DESCRIPCIÓN' in valor.upper() or 'DESCRIPTION' in valor.upper():
                    print(f"  ✅ Encontrada fila de encabezados en fila {i+1}")
                    
                    clientes = {}
                    col_pventa = None
                    
                    for col in range(j+1, len(fila)):
                        valor_col = fila[col]
                        if pd.notna(valor_col) and isinstance(valor_col, str):
                            valor_limpio = valor_col.strip().upper()
                            
                            if any(x in valor_limpio for x in ['P.VENTA', 'P VENTA', 'PVENTA', 'PRECIO VENTA']):
                                col_pventa = col
                                print(f"      → P.VENTA detectada en columna {col}")
                            
                            elif valor_limpio and 'TOTAL' not in valor_limpio:
                                if not any(x in valor_limpio for x in ['CODIGO', 'FAMILIA', 'DESCRIPCI', 'STOCK', 'INGRESO']):
                                    clientes[valor_col.strip()] = col
                                    print(f"      → CLIENTE: '{valor_col.strip()}'")
                    
                    print(f"  → Resumen: P.VENTA columna {col_pventa}, Clientes: {list(clientes.keys())}")
                    return i, clientes, col_pventa
    
    print("  ❌ No se encontraron encabezados de clientes")
    return None, {}, None

def encontrar_limite_metros(df):
    """Encontrar la primera fila donde columna A contiene 'METROS PERFORADOS'"""
    for i in range(len(df)):
        fila = df.iloc[i]
        if pd.notna(fila.iloc[0]) and isinstance(fila.iloc[0], str):
            if 'METROS PERFORADOS' in fila.iloc[0].upper():
                print(f"  📍 Límite ACEROS/METROS encontrado en fila {i+1}")
                return i
    return len(df)

# ============================================================================
# FUNCIONES DE PROCESAMIENTO (CAMBIAN)
# ============================================================================

def procesar_estado_acero(df, inicio_fila, fin_fila, estado, periodo, semana, 
                          id_contrato, tipo_reporte, clientes_columnas, col_pventa):
    """
    Procesar un estado específico dentro de aceros (CPM, AFILADORAS, VENTA)
    """
    supabase = get_supabase()
    fila_actual = inicio_fila
    tipo_perforacion_actual = None
    registros_generales_por_cliente = {}  # Guarda ids de acero_general
    total_detalles = 0
    errores = 0
    
    usar_pventa = 'VENTA' in estado.upper()
    
    print(f"\n  📊 Procesando ESTADO:{estado} (filas {inicio_fila+1} a {fin_fila+1})")
    
    while fila_actual <= fin_fila:
        fila = df.iloc[fila_actual]
        
        # Detectar tipo de perforación
        if pd.notna(fila.iloc[0]) and isinstance(fila.iloc[0], str):
            tipo_texto = fila.iloc[0].strip()
            if tipo_texto and not re.match(r'^\d+', tipo_texto) and 'ESTADO:' not in tipo_texto.upper():
                tipo_perforacion_actual = tipo_texto
                print(f"    📍 Tipo perforación: {tipo_perforacion_actual}")
        
        # Procesar fila con código
        if pd.notna(fila.iloc[1]) and str(fila.iloc[1]).strip():
            codigo = str(fila.iloc[1]).strip()
            familia = fila.iloc[2] if pd.notna(fila.iloc[2]) else None
            descripcion = fila.iloc[3] if pd.notna(fila.iloc[3]) else None
            
            # Validar tipo de perforación
            id_tipo_perf = None
            if tipo_perforacion_actual:
                id_tipo_perf = obtener_tipo_perforacion(tipo_perforacion_actual)
                if id_tipo_perf is None:
                    errores += 1
                    fila_actual += 1
                    continue
            
            # Obtener P.VENTA
            p_venta = 0
            if usar_pventa and col_pventa is not None and col_pventa < len(fila):
                valor_pventa = fila.iloc[col_pventa]
                if pd.notna(valor_pventa) and str(valor_pventa).strip() != '':
                    try:
                        if isinstance(valor_pventa, str):
                            valor_limpio = valor_pventa.replace('.', '').replace(',', '.')
                            numeros = re.findall(r"[\d.]+", valor_limpio)
                            if numeros:
                                p_venta = float(numeros[0])
                        else:
                            p_venta = float(valor_pventa)
                    except:
                        p_venta = 0
            
            # Procesar cada cliente
            for cliente_nombre, col_idx in clientes_columnas.items():
                if col_idx >= len(fila):
                    continue
                    
                valor_celda = fila.iloc[col_idx]
                
                cantidad = 0
                if pd.notna(valor_celda) and str(valor_celda).strip() != '':
                    try:
                        if isinstance(valor_celda, str):
                            valor_limpio = valor_celda.replace('.', '').replace(',', '.')
                            cantidad = float(valor_limpio)
                        else:
                            cantidad = float(valor_celda)
                    except:
                        cantidad = 0
                
                if cantidad > 0:
                    try:
                        id_cliente = obtener_cliente(cliente_nombre, id_contrato)
                        key = (id_cliente, tipo_perforacion_actual)
                        
                        # Buscar o crear acero_general
                        if key not in registros_generales_por_cliente:
                            # Buscar si ya existe
                            response = supabase.table("acero_general").select("id")\
                                .eq("periodo", periodo)\
                                .eq("semana", semana)\
                                .eq("id_contrato", id_contrato)\
                                .eq("id_cliente", id_cliente)\
                                .eq("tipo_operacion", estado)\
                                .eq("id_tipo_perforacion", id_tipo_perf if id_tipo_perf else None)\
                                .execute()
                            
                            if response.data:
                                id_acero_general = response.data[0]['id']
                            else:
                                # Crear nuevo
                                new_response = supabase.table("acero_general").insert({
                                    "periodo": periodo,
                                    "semana": semana,
                                    "id_contrato": id_contrato,
                                    "id_cliente": id_cliente,
                                    "id_tipo_perforacion": id_tipo_perf,
                                    "tipo_operacion": estado,
                                    "tipo_reporte": tipo_reporte,
                                    "observacion": None
                                }).execute()
                                id_acero_general = new_response.data[0]['id']
                            
                            registros_generales_por_cliente[key] = id_acero_general
                        else:
                            id_acero_general = registros_generales_por_cliente[key]
                        
                        # Insertar detalle
                        supabase.table("acero_detalle").insert({
                            "id_acero_general": id_acero_general,
                            "codigo": codigo,
                            "cantidad": cantidad,
                            "p_venta": p_venta,
                            "descripcion": str(descripcion) if pd.notna(descripcion) else None
                        }).execute()
                        
                        total_detalles += 1
                        
                        if total_detalles % 20 == 0:
                            print(f"        ... {total_detalles} detalles en {estado}")
                        
                    except Exception as e:
                        print(f"      ❌ Error: {e}")
                        errores += 1
        
        fila_actual += 1
    
    print(f"  ✅ ESTADO:{estado}: {total_detalles} detalles, {errores} errores")
    return total_detalles

def procesar_metros_perforados(df, inicio_fila, fin_fila, periodo, semana, id_contrato, tipo_reporte):
    """Procesar la sección de metros perforados"""
    supabase = get_supabase()
    fila_actual = inicio_fila
    cliente_actual = None
    en_tabla = False
    total_registros = 0
    errores = 0
    
    print(f"\n  📏 Procesando METROS PERFORADOS (filas {inicio_fila+1} a {fin_fila+1})")
    
    while fila_actual <= fin_fila:
        fila = df.iloc[fila_actual]
        
        valor_colA = fila.iloc[0] if len(fila) > 0 else None
        valor_colB = fila.iloc[1] if len(fila) > 1 else None
        valor_colD = fila.iloc[3] if len(fila) > 3 else None
        valor_colE = fila.iloc[4] if len(fila) > 4 else None
        
        # Detectar cliente
        if pd.notna(valor_colA) and isinstance(valor_colA, str):
            nombre_cliente = valor_colA.strip()
            if nombre_cliente and len(nombre_cliente) > 2 and not re.match(r'^\d+', nombre_cliente):
                if 'METROS' not in nombre_cliente.upper() and 'TIPO' not in nombre_cliente.upper():
                    cliente_actual = nombre_cliente
                    en_tabla = True
                    print(f"    👤 Cliente: {cliente_actual}")
                    fila_actual += 1
                    continue
        
        # Procesar datos de metros
        if en_tabla and cliente_actual and pd.notna(valor_colB):
            tipo_perf = str(valor_colB).strip() if isinstance(valor_colB, str) else None
            
            if tipo_perf and 'TOTAL' in tipo_perf.upper():
                en_tabla = False
                cliente_actual = None
                fila_actual += 1
                continue
            
            if tipo_perf and tipo_perf.strip():
                id_tipo_perf = obtener_tipo_perforacion(tipo_perf)
                
                if id_tipo_perf:
                    try:
                        id_cliente = obtener_cliente(cliente_actual, id_contrato)
                        
                        metros = 0
                        if pd.notna(valor_colD):
                            try:
                                if isinstance(valor_colD, str):
                                    val = valor_colD.replace('.', '').replace(',', '.')
                                    metros = float(val) if val else 0
                                else:
                                    metros = float(valor_colD) if valor_colD else 0
                            except:
                                metros = 0
                        
                        rimado = 0
                        if pd.notna(valor_colE):
                            try:
                                if isinstance(valor_colE, str):
                                    val = valor_colE.replace('.', '').replace(',', '.')
                                    rimado = float(val) if val else 0
                                else:
                                    rimado = float(valor_colE) if valor_colE else 0
                            except:
                                rimado = 0
                        
                        if metros > 0:
                            # Crear perforacion_general
                            new_response = supabase.table("perforacion_general").insert({
                                "periodo": periodo,
                                "semana": semana,
                                "fecha": None,
                                "id_contrato": id_contrato,
                                "id_cliente": id_cliente,
                                "id_tipo_perforacion": id_tipo_perf,
                                "tipo_operacion": 'CPM',
                                "tipo_reporte": tipo_reporte,
                                "observacion": None
                            }).execute()
                            
                            id_perforacion_general = new_response.data[0]['id']
                            
                            # Crear detalle
                            supabase.table("perforacion_detalle").insert({
                                "id_perforacion_general": id_perforacion_general,
                                "total_mp": metros,
                                "mp_rimado": rimado,
                                "observacion": None
                            }).execute()
                            
                            total_registros += 1
                            print(f"      ✅ {cliente_actual} - {tipo_perf}: {metros} m (rimado: {rimado})")
                    
                    except Exception as e:
                        print(f"      ❌ Error: {e}")
                        errores += 1
                else:
                    errores += 1
        
        fila_actual += 1
    
    print(f"  ✅ Metros perforados: {total_registros} registros, {errores} errores")

def limpiar_datos_existentes(periodo, semana, id_contrato):
    """Eliminar datos existentes para el período, semana y contrato específicos"""
    supabase = get_supabase()
    
    # 1. Obtener ids de acero_general
    response = supabase.table("acero_general").select("id")\
        .eq("periodo", periodo)\
        .eq("semana", semana)\
        .eq("id_contrato", id_contrato)\
        .execute()
    
    ids_acero = [row['id'] for row in response.data] if response.data else []
    
    # 2. Eliminar detalles de acero
    if ids_acero:
        for id_acero in ids_acero:
            supabase.table("acero_detalle").delete().eq("id_acero_general", id_acero).execute()
    
    # 3. Eliminar acero_general
    supabase.table("acero_general").delete()\
        .eq("periodo", periodo)\
        .eq("semana", semana)\
        .eq("id_contrato", id_contrato)\
        .execute()
    
    # 4. Obtener ids de perforacion_general
    response2 = supabase.table("perforacion_general").select("id")\
        .eq("periodo", periodo)\
        .eq("semana", semana)\
        .eq("id_contrato", id_contrato)\
        .execute()
    
    ids_perf = [row['id'] for row in response2.data] if response2.data else []
    
    # 5. Eliminar detalles de perforación
    if ids_perf:
        for id_perf in ids_perf:
            supabase.table("perforacion_detalle").delete().eq("id_perforacion_general", id_perf).execute()
    
    # 6. Eliminar perforacion_general
    supabase.table("perforacion_general").delete()\
        .eq("periodo", periodo)\
        .eq("semana", semana)\
        .eq("id_contrato", id_contrato)\
        .execute()
    
    print(f"\n🗑️ LIMPIEZA PREVIA completada")

# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def cargar_excel(archivo_excel, periodo, semana, tipo_reporte):
    """
    Función principal para cargar Excel a Supabase
    """
    print("="*60)
    print("CARGADOR DE EXCEL A SUPABASE")
    print("="*60)
    print(f"Archivo: {archivo_excel}")
    print(f"Período: {periodo}, Semana: {semana}, Tipo: {tipo_reporte}")
    
    try:
        df = pd.read_excel(archivo_excel, sheet_name=0, header=None)
        print(f"  Total filas: {len(df)}")
        
        # Extraer contrato
        celda_contrato = df.iloc[1, 5]
        if pd.notna(celda_contrato):
            texto_contrato = str(celda_contrato)
            if '–' in texto_contrato:
                nombre_contrato = texto_contrato.split('–')[0].strip()
            else:
                nombre_contrato = texto_contrato.strip()
        else:
            raise Exception("No se encontró el contrato")
        
        print(f"  Contrato: {nombre_contrato}")
        
        # Detectar clientes
        fila_encabezados, clientes_acero, col_pventa = detectar_encabezados_cliente(df)
        if not clientes_acero:
            raise Exception("No se encontraron clientes en el archivo")
        
        print(f"  Clientes: {list(clientes_acero.keys())}")
        
        # Validar contrato
        id_contrato = obtener_contrato(nombre_contrato)
        print(f"  ID Contrato: {id_contrato}")
        
        # Validar clientes
        for cliente in clientes_acero.keys():
            obtener_cliente(cliente, id_contrato)
            print(f"  ✅ Cliente válido: {cliente}")
        
        # Limpiar datos existentes
        limpiar_datos_existentes(periodo, semana, id_contrato)
        
        # Encontrar límite
        fila_limite_metros = encontrar_limite_metros(df)
        print(f"\n🔪 Límite ACEROS/METROS: fila {fila_limite_metros+1}")
        
        # Procesar aceros
        print("\n" + "="*60)
        print("PROCESANDO ACEROS...")
        print("="*60)
        
        fila_actual = 0
        estados_procesados = set()
        
        while fila_actual < fila_limite_metros:
            fila = df.iloc[fila_actual]
            
            if pd.notna(fila.iloc[0]) and isinstance(fila.iloc[0], str):
                texto = fila.iloc[0].upper()
                
                if 'ESTADO:CPM' in texto and 'CPM' not in estados_procesados:
                    fin_estado = fila_limite_metros - 1
                    for j in range(fila_actual + 1, fila_limite_metros):
                        if pd.notna(df.iloc[j, 0]) and isinstance(df.iloc[j, 0], str):
                            if 'ESTADO:' in df.iloc[j, 0].upper():
                                fin_estado = j - 1
                                break
                    
                    procesar_estado_acero(
                        df, fila_actual + 1, fin_estado, 'CPM', 
                        periodo, semana, id_contrato, tipo_reporte, 
                        clientes_acero, col_pventa
                    )
                    estados_procesados.add('CPM')
                    fila_actual = fin_estado
                    
                elif 'ESTADO:AFILADORAS' in texto and 'AFILADORAS' not in estados_procesados:
                    fin_estado = fila_limite_metros - 1
                    for j in range(fila_actual + 1, fila_limite_metros):
                        if pd.notna(df.iloc[j, 0]) and isinstance(df.iloc[j, 0], str):
                            if 'ESTADO:' in df.iloc[j, 0].upper():
                                fin_estado = j - 1
                                break
                    
                    procesar_estado_acero(
                        df, fila_actual + 1, fin_estado, 'AFILADORAS', 
                        periodo, semana, id_contrato, tipo_reporte, 
                        clientes_acero, col_pventa
                    )
                    estados_procesados.add('AFILADORAS')
                    fila_actual = fin_estado
                    
                elif 'ESTADO:VENTA' in texto and 'VENTA' not in estados_procesados:
                    fin_estado = fila_limite_metros - 1
                    for j in range(fila_actual + 1, fila_limite_metros):
                        if pd.notna(df.iloc[j, 0]) and isinstance(df.iloc[j, 0], str):
                            if 'ESTADO:' in df.iloc[j, 0].upper():
                                fin_estado = j - 1
                                break
                    
                    procesar_estado_acero(
                        df, fila_actual + 1, fin_estado, 'VENTA', 
                        periodo, semana, id_contrato, tipo_reporte, 
                        clientes_acero, col_pventa
                    )
                    estados_procesados.add('VENTA')
                    fila_actual = fin_estado
            
            fila_actual += 1
        
        # Procesar metros
        print("\n" + "="*60)
        print("PROCESANDO METROS PERFORADOS...")
        print("="*60)
        
        if fila_limite_metros < len(df):
            procesar_metros_perforados(
                df, fila_limite_metros, len(df) - 1, 
                periodo, semana, id_contrato, tipo_reporte
            )
        
        print("\n" + "="*60)
        print("✅ PROCESO COMPLETADO")
        print("="*60)
        
        return {"mensaje": "Carga completada exitosamente"}
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        raise e