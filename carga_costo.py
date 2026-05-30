import sqlite3
import pandas as pd
import re

# ============================================
# CONFIGURACIÓN
# ============================================
archivo_excel = "COSTOS.xlsx"
base_datos = "BD_central.db"
periodo = "2026-02"

# ============================================
# 1. LEER EXCEL
# ============================================
print(f"📂 Leyendo archivo: {archivo_excel}")
df = pd.read_excel(archivo_excel)

print(f"✅ Columnas originales: {list(df.columns)}")

# ============================================
# 2. LIMPIAR NOMBRES DE COLUMNAS
# ============================================
def limpiar_nombre(col):
    # Convertir a minúsculas
    nombre = col.lower()
    # Reemplazar espacios y caracteres especiales con guiones bajos
    nombre = re.sub(r'[^a-z0-9]', '_', nombre)
    # Eliminar guiones bajos múltiples
    nombre = re.sub(r'_+', '_', nombre)
    # Quitar guiones bajos al inicio y final
    nombre = nombre.strip('_')
    return nombre

df.columns = [limpiar_nombre(col) for col in df.columns]
print(f"✅ Columnas limpias: {list(df.columns)}")

# ============================================
# 3. AGREGAR PERIODO
# ============================================
df['periodo'] = periodo

# ============================================
# 4. CONECTAR Y CREAR TABLA
# ============================================
conn = sqlite3.connect(base_datos)
cursor = conn.cursor()

# Crear tabla con nombres limpios
columnas_sql = []
for col in df.columns:
    if col == 'id':
        continue
    if 'precio' in col or 'price' in col or 'unit' in col:
        tipo = 'REAL'
    else:
        tipo = 'TEXT'
    columnas_sql.append(f'"{col}" {tipo}')

create_sql = f"""
CREATE TABLE IF NOT EXISTS costos (
    id INTEGER PRIMARY KEY,
    {', '.join(columnas_sql)}
)
"""
cursor.execute(create_sql)
print("✅ Tabla 'costos' creada/verificada")

# ============================================
# 5. INSERTAR DATOS
# ============================================
print(f"📤 Insertando {len(df)} filas...")
df.to_sql('costos', conn, if_exists='append', index=False)

# ============================================
# 6. VERIFICAR
# ============================================
cursor.execute("SELECT COUNT(*) FROM costos WHERE periodo = ?", (periodo,))
count = cursor.fetchone()[0]
print(f"✅ Filas insertadas: {count}")

conn.close()
print("🎯 Proceso completado")