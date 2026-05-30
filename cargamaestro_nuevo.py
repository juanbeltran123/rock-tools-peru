import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime

class FormularioDatos:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Gestión - ROCK TOOLS PERÚ")
        self.root.geometry("900x700")
        
        # Conectar a la base de datos
        self.conn = sqlite3.connect('RTPERU.db')
        self.cursor = self.conn.cursor()
        
        # Variable para almacenar el ID insertado
        self.ultimo_id_insertado = None
        
        self.crear_widgets()
        self.cargar_combos()
        
    def crear_widgets(self):
        # Notebook para pestañas
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Pestañas
        self.crear_pestana_contratos()
        self.crear_pestana_clientes()
        self.crear_pestana_tipo_perforacion()
        self.crear_pestana_familia()
        self.crear_pestana_objetivos()
        self.crear_pestana_tarifas()
        self.crear_pestana_consultas()
        
    def crear_pestana_contratos(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Contratos")
        
        # Formulario
        ttk.Label(frame, text="AGREGAR CONTRATO", font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=2, pady=10)
        
        ttk.Label(frame, text="Nombre:").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.contrato_nombre = ttk.Entry(frame, width=40)
        self.contrato_nombre.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(frame, text="Tipo Operación:").grid(row=2, column=0, sticky='e', padx=5, pady=5)
        self.contrato_tipo = ttk.Combobox(frame, values=['SUPERFICIAL', 'SUBTERRANEA'], width=37)
        self.contrato_tipo.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(frame, text="Activo:").grid(row=3, column=0, sticky='e', padx=5, pady=5)
        self.contrato_activo = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame, variable=self.contrato_activo).grid(row=3, column=1, sticky='w')
        
        ttk.Button(frame, text="Guardar Contrato", command=self.guardar_contrato).grid(row=4, column=0, columnspan=2, pady=20)
        
        # Lista de contratos
        ttk.Label(frame, text="CONTRATOS REGISTRADOS", font=('Arial', 10, 'bold')).grid(row=5, column=0, columnspan=2, pady=10)
        
        self.tree_contratos = ttk.Treeview(frame, columns=('ID', 'Nombre', 'Tipo', 'Activo'), show='headings', height=8)
        self.tree_contratos.heading('ID', text='ID')
        self.tree_contratos.heading('Nombre', text='Nombre')
        self.tree_contratos.heading('Tipo', text='Tipo')
        self.tree_contratos.heading('Activo', text='Activo')
        
        self.tree_contratos.column('ID', width=50)
        self.tree_contratos.column('Nombre', width=200)
        self.tree_contratos.column('Tipo', width=100)
        self.tree_contratos.column('Activo', width=50)
        
        self.tree_contratos.grid(row=6, column=0, columnspan=2, padx=10, pady=5)
        
        ttk.Button(frame, text="Refrescar", command=self.cargar_contratos).grid(row=7, column=0, columnspan=2, pady=5)
        
    def crear_pestana_clientes(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Clientes")
        
        ttk.Label(frame, text="AGREGAR CLIENTE", font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=2, pady=10)
        
        ttk.Label(frame, text="Contrato:").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.cliente_contrato = ttk.Combobox(frame, width=37)
        self.cliente_contrato.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(frame, text="Nombre Cliente:").grid(row=2, column=0, sticky='e', padx=5, pady=5)
        self.cliente_nombre = ttk.Entry(frame, width=40)
        self.cliente_nombre.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(frame, text="Código (siglas):").grid(row=3, column=0, sticky='e', padx=5, pady=5)
        self.cliente_codigo = ttk.Entry(frame, width=40)
        self.cliente_codigo.grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Label(frame, text="Activo:").grid(row=4, column=0, sticky='e', padx=5, pady=5)
        self.cliente_activo = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame, variable=self.cliente_activo).grid(row=4, column=1, sticky='w')
        
        ttk.Button(frame, text="Guardar Cliente", command=self.guardar_cliente).grid(row=5, column=0, columnspan=2, pady=20)
        
        # Lista de clientes
        ttk.Label(frame, text="CLIENTES REGISTRADOS", font=('Arial', 10, 'bold')).grid(row=6, column=0, columnspan=2, pady=10)
        
        self.tree_clientes = ttk.Treeview(frame, columns=('ID', 'Nombre', 'Código', 'Contrato', 'Activo'), show='headings', height=8)
        self.tree_clientes.heading('ID', text='ID')
        self.tree_clientes.heading('Nombre', text='Nombre')
        self.tree_clientes.heading('Código', text='Código')
        self.tree_clientes.heading('Contrato', text='Contrato')
        self.tree_clientes.heading('Activo', text='Activo')
        
        self.tree_clientes.column('ID', width=50)
        self.tree_clientes.column('Nombre', width=150)
        self.tree_clientes.column('Código', width=80)
        self.tree_clientes.column('Contrato', width=150)
        self.tree_clientes.column('Activo', width=50)
        
        self.tree_clientes.grid(row=7, column=0, columnspan=2, padx=10, pady=5)
        
        ttk.Button(frame, text="Refrescar", command=self.cargar_clientes).grid(row=8, column=0, columnspan=2, pady=5)
        
    def crear_pestana_tipo_perforacion(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Tipo Perforación")
        
        ttk.Label(frame, text="AGREGAR TIPO DE PERFORACIÓN", font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=2, pady=10)
        
        ttk.Label(frame, text="Nombre:").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.tipo_nombre = ttk.Entry(frame, width=40)
        self.tipo_nombre.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(frame, text="Descripción:").grid(row=2, column=0, sticky='e', padx=5, pady=5)
        self.tipo_descripcion = ttk.Entry(frame, width=40)
        self.tipo_descripcion.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(frame, text="Activo:").grid(row=3, column=0, sticky='e', padx=5, pady=5)
        self.tipo_activo = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame, variable=self.tipo_activo).grid(row=3, column=1, sticky='w')
        
        ttk.Button(frame, text="Guardar Tipo", command=self.guardar_tipo_perforacion).grid(row=4, column=0, columnspan=2, pady=20)
        
        # Lista de tipos
        ttk.Label(frame, text="TIPOS REGISTRADOS", font=('Arial', 10, 'bold')).grid(row=5, column=0, columnspan=2, pady=10)
        
        self.tree_tipos = ttk.Treeview(frame, columns=('ID', 'Nombre', 'Descripción', 'Activo'), show='headings', height=8)
        self.tree_tipos.heading('ID', text='ID')
        self.tree_tipos.heading('Nombre', text='Nombre')
        self.tree_tipos.heading('Descripción', text='Descripción')
        self.tree_tipos.heading('Activo', text='Activo')
        
        self.tree_tipos.column('ID', width=50)
        self.tree_tipos.column('Nombre', width=150)
        self.tree_tipos.column('Descripción', width=250)
        self.tree_tipos.column('Activo', width=50)
        
        self.tree_tipos.grid(row=6, column=0, columnspan=2, padx=10, pady=5)
        
        ttk.Button(frame, text="Refrescar", command=self.cargar_tipos_perforacion).grid(row=7, column=0, columnspan=2, pady=5)
        
    def crear_pestana_familia(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Familias")
        
        ttk.Label(frame, text="AGREGAR FAMILIA", font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=2, pady=10)
        
        ttk.Label(frame, text="Nombre:").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.familia_nombre = ttk.Entry(frame, width=40)
        self.familia_nombre.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(frame, text="Descripción:").grid(row=2, column=0, sticky='e', padx=5, pady=5)
        self.familia_descripcion = ttk.Entry(frame, width=40)
        self.familia_descripcion.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Button(frame, text="Guardar Familia", command=self.guardar_familia).grid(row=3, column=0, columnspan=2, pady=20)
        
        # Lista de familias
        ttk.Label(frame, text="FAMILIAS REGISTRADAS", font=('Arial', 10, 'bold')).grid(row=4, column=0, columnspan=2, pady=10)
        
        self.tree_familias = ttk.Treeview(frame, columns=('ID', 'Nombre', 'Descripción'), show='headings', height=8)
        self.tree_familias.heading('ID', text='ID')
        self.tree_familias.heading('Nombre', text='Nombre')
        self.tree_familias.heading('Descripción', text='Descripción')
        
        self.tree_familias.column('ID', width=50)
        self.tree_familias.column('Nombre', width=150)
        self.tree_familias.column('Descripción', width=250)
        
        self.tree_familias.grid(row=5, column=0, columnspan=2, padx=10, pady=5)
        
        ttk.Button(frame, text="Refrescar", command=self.cargar_familias).grid(row=6, column=0, columnspan=2, pady=5)
        
    def crear_pestana_objetivos(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Objetivos")
        
        ttk.Label(frame, text="AGREGAR OBJETIVO", font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=2, pady=10)
        
        ttk.Label(frame, text="Contrato:").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.objetivo_contrato = ttk.Combobox(frame, width=37)
        self.objetivo_contrato.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(frame, text="Cliente (opcional):").grid(row=2, column=0, sticky='e', padx=5, pady=5)
        self.objetivo_cliente = ttk.Combobox(frame, width=37)
        self.objetivo_cliente.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(frame, text="Tipo Perforación:").grid(row=3, column=0, sticky='e', padx=5, pady=5)
        self.objetivo_tipo = ttk.Combobox(frame, width=37)
        self.objetivo_tipo.grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Label(frame, text="Familia:").grid(row=4, column=0, sticky='e', padx=5, pady=5)
        self.objetivo_familia = ttk.Combobox(frame, width=37)
        self.objetivo_familia.grid(row=4, column=1, padx=5, pady=5)
        
        ttk.Label(frame, text="Objetivo:").grid(row=5, column=0, sticky='e', padx=5, pady=5)
        self.objetivo_valor = ttk.Entry(frame, width=40)
        self.objetivo_valor.grid(row=5, column=1, padx=5, pady=5)
        
        ttk.Label(frame, text="Período Desde (YYYY-MM-DD):").grid(row=6, column=0, sticky='e', padx=5, pady=5)
        self.objetivo_desde = ttk.Entry(frame, width=40)
        self.objetivo_desde.insert(0, datetime.now().strftime('%Y-%m-%d'))
        self.objetivo_desde.grid(row=6, column=1, padx=5, pady=5)
        
        ttk.Label(frame, text="Período Hasta (opcional):").grid(row=7, column=0, sticky='e', padx=5, pady=5)
        self.objetivo_hasta = ttk.Entry(frame, width=40)
        self.objetivo_hasta.grid(row=7, column=1, padx=5, pady=5)
        
        ttk.Label(frame, text="Observación:").grid(row=8, column=0, sticky='e', padx=5, pady=5)
        self.objetivo_obs = ttk.Entry(frame, width=40)
        self.objetivo_obs.grid(row=8, column=1, padx=5, pady=5)
        
        ttk.Button(frame, text="Guardar Objetivo", command=self.guardar_objetivo).grid(row=9, column=0, columnspan=2, pady=20)
        
    def crear_pestana_tarifas(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Tarifas")
        
        ttk.Label(frame, text="AGREGAR TARIFA", font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=2, pady=10)
        
        ttk.Label(frame, text="Contrato:").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.tarifa_contrato = ttk.Combobox(frame, width=37)
        self.tarifa_contrato.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(frame, text="Cliente (opcional):").grid(row=2, column=0, sticky='e', padx=5, pady=5)
        self.tarifa_cliente = ttk.Combobox(frame, width=37)
        self.tarifa_cliente.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(frame, text="Tipo Perforación:").grid(row=3, column=0, sticky='e', padx=5, pady=5)
        self.tarifa_tipo = ttk.Combobox(frame, width=37)
        self.tarifa_tipo.grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Label(frame, text="Tarifa:").grid(row=4, column=0, sticky='e', padx=5, pady=5)
        self.tarifa_valor = ttk.Entry(frame, width=40)
        self.tarifa_valor.grid(row=4, column=1, padx=5, pady=5)
        
        ttk.Label(frame, text="Período Desde (YYYY-MM-DD):").grid(row=5, column=0, sticky='e', padx=5, pady=5)
        self.tarifa_desde = ttk.Entry(frame, width=40)
        self.tarifa_desde.insert(0, datetime.now().strftime('%Y-%m-%d'))
        self.tarifa_desde.grid(row=5, column=1, padx=5, pady=5)
        
        ttk.Label(frame, text="Período Hasta (opcional):").grid(row=6, column=0, sticky='e', padx=5, pady=5)
        self.tarifa_hasta = ttk.Entry(frame, width=40)
        self.tarifa_hasta.grid(row=6, column=1, padx=5, pady=5)
        
        ttk.Label(frame, text="Observación:").grid(row=7, column=0, sticky='e', padx=5, pady=5)
        self.tarifa_obs = ttk.Entry(frame, width=40)
        self.tarifa_obs.grid(row=7, column=1, padx=5, pady=5)
        
        ttk.Button(frame, text="Guardar Tarifa", command=self.guardar_tarifa).grid(row=8, column=0, columnspan=2, pady=20)
        
    def crear_pestana_consultas(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Consultas")
        
        ttk.Label(frame, text="CONSULTAS RÁPIDAS", font=('Arial', 12, 'bold')).pack(pady=10)
        
        # Botones de consulta
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Ver Contratos", command=self.ver_contratos).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Ver Clientes", command=self.ver_clientes).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Ver Tipos Perf.", command=self.ver_tipos).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Ver Familias", command=self.ver_familias).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Ver Objetivos", command=self.ver_objetivos).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Ver Tarifas", command=self.ver_tarifas).pack(side='left', padx=5)
        
        # Área de resultados
        self.resultado_text = scrolledtext.ScrolledText(frame, width=100, height=30)
        self.resultado_text.pack(padx=10, pady=10, fill='both', expand=True)
        
    def cargar_combos(self):
        """Cargar datos en los combobox"""
        # Contratos
        self.cursor.execute("SELECT id, nombre FROM contratos WHERE activo = 1")
        contratos = self.cursor.fetchall()
        contratos_list = [f"{c[0]} - {c[1]}" for c in contratos]
        
        for combo in [self.cliente_contrato, self.objetivo_contrato, self.tarifa_contrato]:
            combo['values'] = contratos_list
        
        # Clientes
        self.cursor.execute("SELECT id, nombre, codigo FROM clientes WHERE activo = 1")
        clientes = self.cursor.fetchall()
        clientes_list = [f"{c[0]} - {c[1]} ({c[2]})" for c in clientes]
        
        for combo in [self.objetivo_cliente, self.tarifa_cliente]:
            combo['values'] = [''] + clientes_list  # Opción vacía al inicio
        
        # Tipos de perforación
        self.cursor.execute("SELECT id, nombre FROM tipo_perforacion WHERE activo = 1")
        tipos = self.cursor.fetchall()
        tipos_list = [f"{t[0]} - {t[1]}" for t in tipos]
        
        for combo in [self.objetivo_tipo, self.tarifa_tipo]:
            combo['values'] = tipos_list
        
        # Familias
        self.cursor.execute("SELECT id, nombre FROM familia")
        familias = self.cursor.fetchall()
        familias_list = [f"{f[0]} - {f[1]}" for f in familias]
        self.objetivo_familia['values'] = familias_list
        
    def cargar_contratos(self):
        """Cargar contratos en el treeview"""
        for row in self.tree_contratos.get_children():
            self.tree_contratos.delete(row)
        
        self.cursor.execute("SELECT id, nombre, tipo_operacion, activo FROM contratos")
        for row in self.cursor.fetchall():
            self.tree_contratos.insert('', 'end', values=row)
    
    def cargar_clientes(self):
        """Cargar clientes en el treeview"""
        for row in self.tree_clientes.get_children():
            self.tree_clientes.delete(row)
        
        self.cursor.execute("""
            SELECT c.id, c.nombre, c.codigo, co.nombre, c.activo 
            FROM clientes c
            JOIN contratos co ON c.id_contrato = co.id
        """)
        for row in self.cursor.fetchall():
            self.tree_clientes.insert('', 'end', values=row)
    
    def cargar_tipos_perforacion(self):
        """Cargar tipos en el treeview"""
        for row in self.tree_tipos.get_children():
            self.tree_tipos.delete(row)
        
        self.cursor.execute("SELECT id, nombre, descripcion, activo FROM tipo_perforacion")
        for row in self.cursor.fetchall():
            self.tree_tipos.insert('', 'end', values=row)
    
    def cargar_familias(self):
        """Cargar familias en el treeview"""
        for row in self.tree_familias.get_children():
            self.tree_familias.delete(row)
        
        self.cursor.execute("SELECT id, nombre, descripcion FROM familia")
        for row in self.cursor.fetchall():
            self.tree_familias.insert('', 'end', values=row)
    
    def guardar_contrato(self):
        nombre = self.contrato_nombre.get()
        tipo = self.contrato_tipo.get()
        activo = 1 if self.contrato_activo.get() else 0
        
        if not nombre or not tipo:
            messagebox.showerror("Error", "Nombre y tipo de operación son obligatorios")
            return
        
        try:
            self.cursor.execute('''
                INSERT INTO contratos (nombre, tipo_operacion, activo)
                VALUES (?, ?, ?)
            ''', (nombre, tipo, activo))
            self.conn.commit()
            
            messagebox.showinfo("Éxito", "Contrato guardado correctamente")
            
            # Limpiar campos
            self.contrato_nombre.delete(0, tk.END)
            self.contrato_tipo.set('')
            
            # Refrescar
            self.cargar_contratos()
            self.cargar_combos()
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar: {str(e)}")
    
    def guardar_cliente(self):
        contrato_sel = self.cliente_contrato.get()
        nombre = self.cliente_nombre.get()
        codigo = self.cliente_codigo.get()
        activo = 1 if self.cliente_activo.get() else 0
        
        if not contrato_sel or not nombre or not codigo:
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return
        
        try:
            id_contrato = int(contrato_sel.split(' - ')[0])
            
            self.cursor.execute('''
                INSERT INTO clientes (nombre, codigo, id_contrato, activo)
                VALUES (?, ?, ?, ?)
            ''', (nombre, codigo, id_contrato, activo))
            self.conn.commit()
            
            messagebox.showinfo("Éxito", "Cliente guardado correctamente")
            
            # Limpiar campos
            self.cliente_contrato.set('')
            self.cliente_nombre.delete(0, tk.END)
            self.cliente_codigo.delete(0, tk.END)
            
            # Refrescar
            self.cargar_clientes()
            self.cargar_combos()
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar: {str(e)}")
    
    def guardar_tipo_perforacion(self):
        nombre = self.tipo_nombre.get()
        descripcion = self.tipo_descripcion.get()
        activo = 1 if self.tipo_activo.get() else 0
        
        if not nombre:
            messagebox.showerror("Error", "El nombre es obligatorio")
            return
        
        try:
            self.cursor.execute('''
                INSERT INTO tipo_perforacion (nombre, descripcion, activo)
                VALUES (?, ?, ?)
            ''', (nombre, descripcion, activo))
            self.conn.commit()
            
            messagebox.showinfo("Éxito", "Tipo de perforación guardado correctamente")
            
            # Limpiar campos
            self.tipo_nombre.delete(0, tk.END)
            self.tipo_descripcion.delete(0, tk.END)
            
            # Refrescar
            self.cargar_tipos_perforacion()
            self.cargar_combos()
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar: {str(e)}")
    
    def guardar_familia(self):
        nombre = self.familia_nombre.get()
        descripcion = self.familia_descripcion.get()
        
        if not nombre:
            messagebox.showerror("Error", "El nombre es obligatorio")
            return
        
        try:
            self.cursor.execute('''
                INSERT INTO familia (nombre, descripcion)
                VALUES (?, ?)
            ''', (nombre, descripcion))
            self.conn.commit()
            
            messagebox.showinfo("Éxito", "Familia guardada correctamente")
            
            # Limpiar campos
            self.familia_nombre.delete(0, tk.END)
            self.familia_descripcion.delete(0, tk.END)
            
            # Refrescar
            self.cargar_familias()
            self.cargar_combos()
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar: {str(e)}")
    
    def guardar_objetivo(self):
        contrato_sel = self.objetivo_contrato.get()
        cliente_sel = self.objetivo_cliente.get()
        tipo_sel = self.objetivo_tipo.get()
        familia_sel = self.objetivo_familia.get()
        objetivo = self.objetivo_valor.get()
        desde = self.objetivo_desde.get()
        hasta = self.objetivo_hasta.get() or None
        obs = self.objetivo_obs.get() or None
        
        if not contrato_sel or not tipo_sel or not familia_sel or not objetivo or not desde:
            messagebox.showerror("Error", "Los campos marcados con * son obligatorios")
            return
        
        try:
            id_contrato = int(contrato_sel.split(' - ')[0])
            id_tipo = int(tipo_sel.split(' - ')[0])
            id_familia = int(familia_sel.split(' - ')[0])
            id_cliente = int(cliente_sel.split(' - ')[0]) if cliente_sel else None
            
            self.cursor.execute('''
                INSERT INTO objetivos 
                (id_contrato, id_cliente, id_tipo_perforacion, id_familia, objetivo, periodo_desde, periodo_hasta, observacion)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (id_contrato, id_cliente, id_tipo, id_familia, float(objetivo), desde, hasta, obs))
            self.conn.commit()
            
            messagebox.showinfo("Éxito", "Objetivo guardado correctamente")
            
            # Limpiar campos
            self.objetivo_contrato.set('')
            self.objetivo_cliente.set('')
            self.objetivo_tipo.set('')
            self.objetivo_familia.set('')
            self.objetivo_valor.delete(0, tk.END)
            self.objetivo_desde.delete(0, tk.END)
            self.objetivo_desde.insert(0, datetime.now().strftime('%Y-%m-%d'))
            self.objetivo_hasta.delete(0, tk.END)
            self.objetivo_obs.delete(0, tk.END)
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar: {str(e)}")
    
    def guardar_tarifa(self):
        contrato_sel = self.tarifa_contrato.get()
        cliente_sel = self.tarifa_cliente.get()
        tipo_sel = self.tarifa_tipo.get()
        tarifa = self.tarifa_valor.get()
        desde = self.tarifa_desde.get()
        hasta = self.tarifa_hasta.get() or None
        obs = self.tarifa_obs.get() or None
        
        if not contrato_sel or not tipo_sel or not tarifa or not desde:
            messagebox.showerror("Error", "Los campos marcados con * son obligatorios")
            return
        
        try:
            id_contrato = int(contrato_sel.split(' - ')[0])
            id_tipo = int(tipo_sel.split(' - ')[0])
            id_cliente = int(cliente_sel.split(' - ')[0]) if cliente_sel else None
            
            self.cursor.execute('''
                INSERT INTO tarifas 
                (id_contrato, id_cliente, id_tipo_perforacion, tarifa, periodo_desde, periodo_hasta, observacion)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (id_contrato, id_cliente, id_tipo, float(tarifa), desde, hasta, obs))
            self.conn.commit()
            
            messagebox.showinfo("Éxito", "Tarifa guardada correctamente")
            
            # Limpiar campos
            self.tarifa_contrato.set('')
            self.tarifa_cliente.set('')
            self.tarifa_tipo.set('')
            self.tarifa_valor.delete(0, tk.END)
            self.tarifa_desde.delete(0, tk.END)
            self.tarifa_desde.insert(0, datetime.now().strftime('%Y-%m-%d'))
            self.tarifa_hasta.delete(0, tk.END)
            self.tarifa_obs.delete(0, tk.END)
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar: {str(e)}")
    
    def ver_contratos(self):
        self.resultado_text.delete(1.0, tk.END)
        self.cursor.execute("SELECT * FROM contratos")
        rows = self.cursor.fetchall()
        
        self.resultado_text.insert(tk.END, "=== CONTRATOS ===\n\n")
        for row in rows:
            self.resultado_text.insert(tk.END, f"ID: {row[0]}\n")
            self.resultado_text.insert(tk.END, f"Nombre: {row[1]}\n")
            self.resultado_text.insert(tk.END, f"Tipo Operación: {row[2]}\n")
            self.resultado_text.insert(tk.END, f"Activo: {row[3]}\n")
            self.resultado_text.insert(tk.END, "-" * 40 + "\n")
    
    def ver_clientes(self):
        self.resultado_text.delete(1.0, tk.END)
        self.cursor.execute("""
            SELECT c.*, co.nombre 
            FROM clientes c
            JOIN contratos co ON c.id_contrato = co.id
        """)
        rows = self.cursor.fetchall()
        
        self.resultado_text.insert(tk.END, "=== CLIENTES ===\n\n")
        for row in rows:
            self.resultado_text.insert(tk.END, f"ID: {row[0]}\n")
            self.resultado_text.insert(tk.END, f"Nombre: {row[1]}\n")
            self.resultado_text.insert(tk.END, f"Código: {row[2]}\n")
            self.resultado_text.insert(tk.END, f"ID Contrato: {row[3]}\n")
            self.resultado_text.insert(tk.END, f"Contrato: {row[5]}\n")
            self.resultado_text.insert(tk.END, f"Activo: {row[4]}\n")
            self.resultado_text.insert(tk.END, "-" * 40 + "\n")
    
    def ver_tipos(self):
        self.resultado_text.delete(1.0, tk.END)
        self.cursor.execute("SELECT * FROM tipo_perforacion")
        rows = self.cursor.fetchall()
        
        self.resultado_text.insert(tk.END, "=== TIPOS DE PERFORACIÓN ===\n\n")
        for row in rows:
            self.resultado_text.insert(tk.END, f"ID: {row[0]}\n")
            self.resultado_text.insert(tk.END, f"Nombre: {row[1]}\n")
            self.resultado_text.insert(tk.END, f"Descripción: {row[2]}\n")
            self.resultado_text.insert(tk.END, f"Activo: {row[3]}\n")
            self.resultado_text.insert(tk.END, "-" * 40 + "\n")
    
    def ver_familias(self):
        self.resultado_text.delete(1.0, tk.END)
        self.cursor.execute("SELECT * FROM familia")
        rows = self.cursor.fetchall()
        
        self.resultado_text.insert(tk.END, "=== FAMILIAS ===\n\n")
        for row in rows:
            self.resultado_text.insert(tk.END, f"ID: {row[0]}\n")
            self.resultado_text.insert(tk.END, f"Nombre: {row[1]}\n")
            self.resultado_text.insert(tk.END, f"Descripción: {row[2]}\n")
            self.resultado_text.insert(tk.END, "-" * 40 + "\n")
    
    def ver_objetivos(self):
        self.resultado_text.delete(1.0, tk.END)
        self.cursor.execute("""
            SELECT o.*, co.nombre, tp.nombre, f.nombre 
            FROM objetivos o
            JOIN contratos co ON o.id_contrato = co.id
            JOIN tipo_perforacion tp ON o.id_tipo_perforacion = tp.id
            JOIN familia f ON o.id_familia = f.id
        """)
        rows = self.cursor.fetchall()
        
        self.resultado_text.insert(tk.END, "=== OBJETIVOS ===\n\n")
        for row in rows:
            self.resultado_text.insert(tk.END, f"ID: {row[0]}\n")
            self.resultado_text.insert(tk.END, f"Contrato: {row[8]}\n")
            self.resultado_text.insert(tk.END, f"Cliente ID: {row[2]}\n")
            self.resultado_text.insert(tk.END, f"Tipo Perf.: {row[9]}\n")
            self.resultado_text.insert(tk.END, f"Familia: {row[10]}\n")
            self.resultado_text.insert(tk.END, f"Objetivo: {row[4]}\n")
            self.resultado_text.insert(tk.END, f"Período: {row[5]} - {row[6]}\n")
            self.resultado_text.insert(tk.END, f"Obs: {row[7]}\n")
            self.resultado_text.insert(tk.END, "-" * 40 + "\n")
    
    def ver_tarifas(self):
        self.resultado_text.delete(1.0, tk.END)
        self.cursor.execute("""
            SELECT t.*, co.nombre, tp.nombre 
            FROM tarifas t
            JOIN contratos co ON t.id_contrato = co.id
            JOIN tipo_perforacion tp ON t.id_tipo_perforacion = tp.id
        """)
        rows = self.cursor.fetchall()
        
        self.resultado_text.insert(tk.END, "=== TARIFAS ===\n\n")
        for row in rows:
            self.resultado_text.insert(tk.END, f"ID: {row[0]}\n")
            self.resultado_text.insert(tk.END, f"Contrato: {row[7]}\n")
            self.resultado_text.insert(tk.END, f"Cliente ID: {row[2]}\n")
            self.resultado_text.insert(tk.END, f"Tipo Perf.: {row[8]}\n")
            self.resultado_text.insert(tk.END, f"Tarifa: {row[4]}\n")
            self.resultado_text.insert(tk.END, f"Período: {row[5]} - {row[6]}\n")
            self.resultado_text.insert(tk.END, f"Obs: {row[7]}\n")
            self.resultado_text.insert(tk.END, "-" * 40 + "\n")
    
    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = FormularioDatos(root)
    
    # Cargar datos iniciales
    app.cargar_contratos()
    app.cargar_clientes()
    app.cargar_tipos_perforacion()
    app.cargar_familias()
    
    root.mainloop()