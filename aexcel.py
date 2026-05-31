import sqlite3
import pandas as pd

# Conectar a la base de datos
conn = sqlite3.connect('RTPERU.db')

# Leer la tabla costos
df = pd.read_sql_query("SELECT * FROM costos", conn)

# Exportar a Excel
df.to_excel('costos.xlsx', index=False)

# Cerrar conexión
conn.close()