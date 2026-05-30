import sqlite3
import pandas as pd
import re
from datetime import datetime

def conectar_db():
    """Conectar a la base de datos"""
    return sqlite3.connect('RTPERU.db')

def obtener_contrato(conn, nombre_contrato):
    """Obtener ID del contrato - VALIDA que existe"""
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM contratos WHERE nombre = ?", (nombre_contrato,))
    resultado = cursor.fetchone()
    
    if resultado:
        return resultado[0]
    else:
        raise Exception(f"❌ El contrato '{nombre_contrato}' no existe en la base de datos")

def obtener_cliente(conn, nombre_cliente, id_contrato):
    """Obtener ID del cliente - VALIDA que existe para el contrato"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id FROM clientes 
        WHERE nombre = ? AND id_contrato = ?
    """, (nombre_cliente, id_contrato))
    resultado = cursor.fetchone()
    
    if resultado:
        return resultado[0]
    else:
        raise Exception(f"❌ El cliente '{nombre_cliente}' no existe para el contrato ID {id_contrato}")

def obtener_tipo_perforacion(conn, nombre_tipo):
    """Obtener ID del tipo de perforación - VALIDA que existe"""
    if not nombre_tipo or pd.isna(nombre_tipo) or str(nombre_tipo).strip() == '':
        return None
        
    nombre_tipo = str(nombre_tipo).strip()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM tipo_perforacion WHERE nombre = ?", (nombre_tipo,))
    resultado = cursor.fetchone()
    
    if resultado:
        return resultado[0]
    else:
        print(f"  ⚠️ Tipo de perforación '{nombre_tipo}' no existe - fila omitida")
        return None

def detectar_encabezados_cliente(df):
    """
    Detectar automáticamente la fila donde están los encabezados de cliente
    y las columnas de cada cliente
    """
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
                    
                    # Recorrer TODAS las columnas después de DESCRIPCIÓN
                    for col in range(j+1, len(fila)):
                        valor_col = fila[col]
                        if pd.notna(valor_col) and isinstance(valor_col, str):
                            valor_limpio = valor_col.strip().upper()
                            
                            print(f"    Columna {col}: '{valor_col}'")
                            
                            # Detectar P.VENTA (prioridad)
                            if any(x in valor_limpio for x in ['P.VENTA', 'P VENTA', 'PVENTA', 'PRECIO VENTA']):
                                col_pventa = col
                                print(f"      → P.VENTA detectada en columna {col}")
                            
                            # Detectar clientes (excluir TOTAL y encabezados conocidos)
                            elif valor_limpio and 'TOTAL' not in valor_limpio:
                                if not any(x in valor_limpio for x in ['CODIGO', 'FAMILIA', 'DESCRIPCI', 'STOCK', 'INGRESO']):
                                    clientes[valor_col.strip()] = col
                                    print(f"      → CLIENTE: '{valor_col.strip()}'")
                            
                            # TOTAL solo es informativo, no detenemos la búsqueda
                            elif 'TOTAL' in valor_limpio:
                                print(f"      → TOTAL encontrado (continuamos buscando P.VENTA)")
                    
                    print(f"  → Resumen: P.VENTA columna {col_pventa}, Clientes: {list(clientes.keys())}")
                    return i, clientes, col_pventa
    
    print("  ❌ No se encontraron encabezados de clientes")
    return None, {}, None


def encontrar_limite_metros(df):
    """
    Encontrar la primera fila donde columna A contiene 'METROS PERFORADOS'
    Todo lo anterior son aceros, todo lo siguiente son metros
    """
    for i in range(len(df)):
        fila = df.iloc[i]
        if pd.notna(fila.iloc[0]) and isinstance(fila.iloc[0], str):
            if 'METROS PERFORADOS' in fila.iloc[0].upper():
                print(f"  📍 Límite ACEROS/METROS encontrado en fila {i+1}")
                return i
    return len(df)  # Si no encuentra, todo es aceros

def procesar_estado_acero(conn, df, inicio_fila, fin_fila, estado, periodo, semana, 
                          id_contrato, tipo_reporte, clientes_columnas, col_pventa):
    """
    Procesar un estado específico dentro de aceros (CPM, AFILADORAS, VENTA)
    """
    cursor = conn.cursor()
    fila_actual = inicio_fila
    tipo_perforacion_actual = None
    registros_generales_por_cliente = {}
    total_detalles = 0
    errores = 0
    
    # Determinar si usamos P.VENTA (solo para VENTA)
    usar_pventa = 'VENTA' in estado.upper()
    
    print(f"\n  📊 Procesando ESTADO:{estado} (filas {inicio_fila+1} a {fin_fila+1})")
    print(f"     Usar P.VENTA: {usar_pventa}")
    if usar_pventa:
        print(f"     Columna P.VENTA: {col_pventa}")
    
    while fila_actual <= fin_fila:
        fila = df.iloc[fila_actual]
        
        # Detectar tipo de perforación (columna A)
        if pd.notna(fila.iloc[0]) and isinstance(fila.iloc[0], str):
            tipo_texto = fila.iloc[0].strip()
            # Solo actualizar si no es un estado y no es un código numérico
            if tipo_texto and not re.match(r'^\d+', tipo_texto) and 'ESTADO:' not in tipo_texto.upper():
                tipo_perforacion_actual = tipo_texto
                print(f"    📍 Tipo perforación: {tipo_perforacion_actual}")
        
        # Procesar fila con código (columna B)
        if pd.notna(fila.iloc[1]) and str(fila.iloc[1]).strip():
            codigo = str(fila.iloc[1]).strip()
            familia = fila.iloc[2] if pd.notna(fila.iloc[2]) else None
            descripcion = fila.iloc[3] if pd.notna(fila.iloc[3]) else None
            
            # ========== DEPURACIÓN P.VENTA ==========
            if usar_pventa:
                print(f"\n      🔍 VENTA - Código: {codigo}")
                print(f"      🔍 col_pventa: {col_pventa}")
                print(f"      🔍 len(fila): {len(fila)}")
                
                if col_pventa is not None:
                    if col_pventa < len(fila):
                        valor_pventa = fila.iloc[col_pventa]
                        print(f"      🔍 valor en columna {col_pventa}: '{valor_pventa}'")
                        print(f"      🔍 tipo: {type(valor_pventa)}")
                        print(f"      🔍 pd.notna: {pd.notna(valor_pventa)}")
                        
                        if pd.notna(valor_pventa):
                            str_valor = str(valor_pventa).strip()
                            print(f"      🔍 str.strip: '{str_valor}'")
                            print(f"      🔍 vacío?: {str_valor == ''}")
                    else:
                        print(f"      🔍 ERROR: col_pventa {col_pventa} >= len(fila) {len(fila)}")
                else:
                    print(f"      🔍 ERROR: col_pventa es None")
            # ========================================
            
            # Validar tipo de perforación
            id_tipo_perf = None
            if tipo_perforacion_actual:
                id_tipo_perf = obtener_tipo_perforacion(conn, tipo_perforacion_actual)
                if id_tipo_perf is None:
                    print(f"      ⚠️ Código {codigo} omitido por tipo perforación inválido")
                    errores += 1
                    fila_actual += 1
                    continue
            
            # Obtener P.VENTA solo si es estado VENTA
            p_venta = 0
            if usar_pventa and col_pventa is not None and col_pventa < len(fila):
                valor_pventa = fila.iloc[col_pventa]
                if pd.notna(valor_pventa) and str(valor_pventa).strip() != '':
                    try:
                        if isinstance(valor_pventa, str):
                            # Limpiar formato peruano
                            valor_limpio = valor_pventa.replace('.', '').replace(',', '.')
                            numeros = re.findall(r"[\d.]+", valor_limpio)
                            if numeros:
                                p_venta = float(numeros[0])
                                print(f"      ✅ P.VENTA convertido: {p_venta}")
                        else:
                            p_venta = float(valor_pventa)
                            print(f"      ✅ P.VENTA numérico: {p_venta}")
                    except Exception as e:
                        print(f"      ⚠️ Error convirtiendo P.VENTA: {e}")
                        p_venta = 0
            
            # Procesar cada cliente
            for cliente_nombre, col_idx in clientes_columnas.items():
                if col_idx >= len(fila):
                    continue
                    
                valor_celda = fila.iloc[col_idx]
                
                # Convertir cantidad
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
                        # Validar cliente
                        id_cliente = obtener_cliente(conn, cliente_nombre, id_contrato)
                        
                        # Clave para el general
                        key = (id_cliente, tipo_perforacion_actual)
                        
                        # Buscar o crear acero_general
                        if key not in registros_generales_por_cliente:
                            cursor.execute('''
                                SELECT id FROM acero_general 
                                WHERE periodo = ? AND semana = ? 
                                  AND id_contrato = ? AND id_cliente = ?
                                  AND tipo_operacion = ? 
                                  AND (id_tipo_perforacion = ? OR (id_tipo_perforacion IS NULL AND ? IS NULL))
                            ''', (periodo, semana, id_contrato, id_cliente, 
                                  estado, id_tipo_perf, id_tipo_perf))
                            
                            resultado = cursor.fetchone()
                            
                            if resultado:
                                id_acero_general = resultado[0]
                                print(f"      📌 Usando acero_general ID: {id_acero_general} para {cliente_nombre}")
                            else:
                                cursor.execute('''
                                    INSERT INTO acero_general 
                                    (periodo, semana, id_contrato, id_cliente, id_tipo_perforacion, 
                                     tipo_operacion, tipo_reporte, observacion)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                ''', (periodo, semana, id_contrato, id_cliente, id_tipo_perf,
                                      estado, tipo_reporte, None))
                                id_acero_general = cursor.lastrowid
                                print(f"      📌 Creado NUEVO acero_general ID: {id_acero_general} para {cliente_nombre}")
                            
                            registros_generales_por_cliente[key] = id_acero_general
                        else:
                            id_acero_general = registros_generales_por_cliente[key]
                        
                        # Insertar detalle
                        cursor.execute('''
                            INSERT INTO acero_detalle 
                            (id_acero_general, codigo, cantidad, p_venta, descripcion)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (id_acero_general, codigo, cantidad, p_venta, 
                              str(descripcion) if pd.notna(descripcion) else None))
                        
                        total_detalles += 1
                        
                        # Mostrar cada 20 detalles
                        if total_detalles % 20 == 0:
                            print(f"        ... {total_detalles} detalles en {estado}")
                        
                    except Exception as e:
                        print(f"      ❌ Error: {e}")
                        errores += 1
        
        fila_actual += 1
    
    print(f"  ✅ ESTADO:{estado}: {total_detalles} detalles, {errores} errores")
    if usar_pventa and total_detalles > 0:
        print(f"     💰 P.VENTA aplicado a {total_detalles} detalles")
    
    return total_detalles


def procesar_metros_perforados(conn, df, inicio_fila, fin_fila, periodo, semana, id_contrato, tipo_reporte):
    """
    Procesar la sección de metros perforados (después del límite)
    """
    cursor = conn.cursor()
    print(f"\n  📏 Procesando METROS PERFORADOS (filas {inicio_fila+1} a {fin_fila+1})")
    
    fila_actual = inicio_fila
    cliente_actual = None
    en_tabla = False
    total_registros = 0
    errores = 0
    
    while fila_actual <= fin_fila:
        fila = df.iloc[fila_actual]
        
        valor_colA = fila.iloc[0] if len(fila) > 0 else None
        valor_colB = fila.iloc[1] if len(fila) > 1 else None
        valor_colD = fila.iloc[3] if len(fila) > 3 else None
        valor_colE = fila.iloc[4] if len(fila) > 4 else None
        
        # Detectar cliente (columna A)
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
                # Validar tipo de perforación
                id_tipo_perf = obtener_tipo_perforacion(conn, tipo_perf)
                
                if id_tipo_perf:
                    try:
                        # Validar cliente
                        id_cliente = obtener_cliente(conn, cliente_actual, id_contrato)
                        
                        # Procesar metros
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
                        
                        # Procesar rimado
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
                            cursor.execute('''
                                INSERT INTO perforacion_general 
                                (periodo, semana, fecha, id_contrato, id_cliente, id_tipo_perforacion,
                                 tipo_operacion, tipo_reporte, observacion)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (periodo, semana, None, id_contrato, id_cliente, id_tipo_perf,
                                  'PERFORACION', tipo_reporte, None))
                            
                            id_perforacion_general = cursor.lastrowid
                            
                            # Crear detalle
                            cursor.execute('''
                                INSERT INTO perforacion_detalle 
                                (id_perforacion_general, total_mp, mp_rimado, observacion)
                                VALUES (?, ?, ?, ?)
                            ''', (id_perforacion_general, metros, rimado, None))
                            
                            total_registros += 1
                            print(f"      ✅ {cliente_actual} - {tipo_perf}: {metros} m (rimado: {rimado})")
                    
                    except Exception as e:
                        print(f"      ❌ Error: {e}")
                        errores += 1
                else:
                    print(f"      ⚠️ Tipo perforación '{tipo_perf}' inválido - omitido")
                    errores += 1
        
        fila_actual += 1
    
    print(f"  ✅ Metros perforados: {total_registros} registros, {errores} errores")

def cargar_excel_a_sqlite(archivo_excel):
    """Función principal para cargar Excel a SQLite"""
    
    print("="*60)
    print("CARGADOR DE EXCEL A SQLITE - RTPERU.db")
    print("="*60)
    print(f"Archivo: {archivo_excel}")
    
    try:
        # Leer Excel
        print(f"\n📖 Leyendo archivo...")
        df = pd.read_excel(archivo_excel, sheet_name=0, header=None)
        print(f"  Total filas: {len(df)}")
        
        # Extraer metadatos
        print("\n🔍 Extrayendo metadatos...")
        
        # Contrato (columna F, fila 2)
        try:
            celda_contrato = df.iloc[1, 5]
            if pd.notna(celda_contrato):
                texto_contrato = str(celda_contrato)
                if '–' in texto_contrato:
                    nombre_contrato = texto_contrato.split('–')[0].strip()
                else:
                    nombre_contrato = texto_contrato.strip()
            else:
                raise Exception("No se encontró el contrato")
        except:
            raise Exception("No se pudo leer el contrato de la fila 2, columna F")
        
        print(f"  Contrato: {nombre_contrato}")
        
        # Detectar clientes
        fila_encabezados, clientes_acero, col_pventa = detectar_encabezados_cliente(df)
        if not clientes_acero:
            raise Exception("No se encontraron clientes en el archivo")
        print(f"  Clientes: {list(clientes_acero.keys())}")
        
        # Período
        periodo = None
        for i in range(5):
            fila = df.iloc[i]
            for j, val in enumerate(fila):
                if pd.notna(val) and 'MES' in str(val):
                    if j+1 < len(fila) and pd.notna(fila[j+1]):
                        try:
                            fecha = pd.to_datetime(fila[j+1])
                            periodo = fecha.strftime('%Y-%m')
                            break
                        except:
                            pass
            if periodo:
                break
        
        if not periodo:
            raise Exception("No se pudo determinar el período")
        print(f"  Período: {periodo}")
        
        # Semana
        semana = 2
        if 'SEMANA' in archivo_excel.upper():
            match = re.search(r'SEMANA\s*(\d+)', archivo_excel, re.IGNORECASE)
            if match:
                semana = int(match.group(1))
        print(f"  Semana: {semana}")
        
        tipo_reporte = "AVANCE"
        print(f"  Tipo reporte: {tipo_reporte}")
        
        # Conectar BD
        conn = conectar_db()
        
        # Validar contrato
        id_contrato = obtener_contrato(conn, nombre_contrato)
        print(f"  ID Contrato: {id_contrato}")
        
        # Validar clientes
        for cliente in clientes_acero.keys():
            try:
                obtener_cliente(conn, cliente, id_contrato)
                print(f"  ✅ Cliente válido: {cliente}")
            except Exception as e:
                print(f"  {e}")
                raise Exception(f"Cliente '{cliente}' no existe en base de datos")
        
        # Encontrar límite entre aceros y metros
        fila_limite_metros = encontrar_limite_metros(df)
        print(f"\n🔪 Límite ACEROS/METROS: fila {fila_limite_metros+1}")
        
        print("\n" + "="*60)
        print("PROCESANDO ACEROS (antes del límite)...")
        print("="*60)
        
        # Procesar aceros (todo antes del límite)
        fila_actual = 0
        estados_procesados = set()
        
        while fila_actual < fila_limite_metros:
            fila = df.iloc[fila_actual]
            
            if pd.notna(fila.iloc[0]) and isinstance(fila.iloc[0], str):
                texto = fila.iloc[0].upper()
                
                # Buscar estados
                if 'ESTADO:CPM' in texto and 'CPM' not in estados_procesados:
                    # Encontrar fin del estado (próximo ESTADO o límite)
                    fin_estado = fila_limite_metros - 1
                    for j in range(fila_actual + 1, fila_limite_metros):
                        if pd.notna(df.iloc[j, 0]) and isinstance(df.iloc[j, 0], str):
                            if 'ESTADO:' in df.iloc[j, 0].upper():
                                fin_estado = j - 1
                                break
                    
                    procesar_estado_acero(
                        conn, df, fila_actual + 1, fin_estado, 'CPM', 
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
                        conn, df, fila_actual + 1, fin_estado, 'AFILADORAS', 
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
                        conn, df, fila_actual + 1, fin_estado, 'VENTA', 
                        periodo, semana, id_contrato, tipo_reporte, 
                        clientes_acero, col_pventa
                    )
                    estados_procesados.add('VENTA')
                    fila_actual = fin_estado
            
            fila_actual += 1
        
        print("\n" + "="*60)
        print("PROCESANDO METROS PERFORADOS (después del límite)...")
        print("="*60)
        
        # Procesar metros (después del límite)
        if fila_limite_metros < len(df):
            procesar_metros_perforados(
                conn, df, fila_limite_metros, len(df) - 1, 
                periodo, semana, id_contrato, tipo_reporte
            )
        
        # Confirmar cambios
        conn.commit()
        
        print("\n" + "="*60)
        print("✅ PROCESO COMPLETADO")
        print("="*60)
        
        # Resumen final
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM acero_general WHERE periodo=? AND semana=?", (periodo, semana))
        acero_general = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM acero_detalle")
        acero_detalle = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM perforacion_general WHERE periodo=? AND semana=?", (periodo, semana))
        perf_general = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM perforacion_detalle")
        perf_detalle = cursor.fetchone()[0]
        
        print(f"\n📊 RESUMEN FINAL:")
        print(f"  Acero General: {acero_general} registros")
        print(f"  Acero Detalle: {acero_detalle} registros")
        print(f"  Perforación General: {perf_general} registros")
        print(f"  Perforación Detalle: {perf_detalle} registros")
        
        conn.close()
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        if 'conn' in locals():
            conn.rollback()
            conn.close()

def main():
    archivo = "AVANCE SEMANAL FEBRERO - SEMANA 02 ANDAYCHAGUA.xlsx"
    cargar_excel_a_sqlite(archivo)

if __name__ == "__main__":
    main()