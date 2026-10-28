import tkinter as GUI
from tkinter import ttk, messagebox
from events import EventManager
from models import*
from view_builders import CRUDViewBuilder

#LISTAS DE OPCIONES PARA LOS COMBOBOX
GENEROS = ["Masculino", "Femenino", "Otro"]
MODALIDAD_TRABAJO = ["Contratado", "Tiempo completo", "Parcial", "Medio Tiempo"]
CARGO = ["Obrero", "Docente", "Administrativo", "Director", "Sub-director"]
TURNOS = ["Mañana", "Tarde"]
DIAS_CLASES = ["Lun-Mar", "Mie-Jue", "Mar-Mie", "Jue-Vie", "Mie a Vie"]
#MAPEO PARA GENERAR FORMULARIOS DINAMICAMENTE

MODEL_METADATA: dict[str, dict[str, object]] = {
    "Bienes": {
        "table_name":"bien",
        "class": Bienes,
        "pk": "codigo",
        "fields": {
            "codigo": {"label": "Código del Bien", "type": "string", "valid": "alphanumeric"},
            "nombre": {"label": "Nombre/Descripción", "type": "string", "valid": "text"},
            "cantidad": {"label": "Cantidad en Inventario", "type": "number", "valid": "integer"},
            "monto_unit": {"label": "Monto Unitario", "type": "number", "valid": "float"}
        }
    },
    "Empleados": {
        "table_name":"empleado",
        "class": Empleados,
        "pk": "cedula",
        "fields": {
            "cedula": {"label": "Cédula de Identidad", "type": "cedula", "valid": "cedula"},
            "nombre": {"label": "Nombre", "type": "string", "valid": "text"},
            "apellido": {"label": "Apellido", "type": "string", "valid": "text"},
            "cargo": {"label": "Cargo Asignado", "type": "combo", "values": CARGO},
            "modalidad_trab": {"label": "Modalidad de Trabajo", "type": "combo", "values": MODALIDAD_TRABAJO}
        }
    },
    "Estudiantes": {
        "table_name":"estudiante",
        "class": Estudiantes,
        "pk": "cedula",
        "fields": {
            "cedula": {"label": "Cédula de Identidad", "type": "cedula", "valid": "cedula"},
            "nombre": {"label": "Nombre", "type": "string", "valid": "text"},
            "apellido": {"label": "Apellido", "type": "string", "valid": "text"},
            "edad": {"label": "Edad", "type": "number", "valid": "integer"},
            "genero": {"label": "Género", "type": "combo", "values": GENEROS}
        }
    },
    "Cursos": {
        "table_name":"curso",
        "class": Cursos,
        "pk": "codigo",
        "fields": {
            "codigo": {"label": "Código del Curso", "type": "string", "valid": "alphanumeric"},
            "empleado_id":{"label":"Docente", "type": "string", "valid":"text"},
            "nombre": {"label": "Nombre del Curso", "type": "string", "valid": "text"},
            "fecha_inicio": {"label": "Fecha Inicio (AAAA-MM-DD)", "type": "string", "valid": "date"},
            "fecha_fin": {"label": "Fecha Fin (AAAA-MM-DD)", "type": "string", "valid": "date"},
            "modalidad": {"label": "Modalidad", "type": "combo", "values": ["Presencial", "Virtual", "Híbrido"]},
            "horario": {"label": "Horario/Turno", "type": "combo", "values": TURNOS},
            "dia": {"label": "Día de Dictado", "type": "combo", "values": DIAS_CLASES}
        }
    },
    "Inscripciones": {
        "table_name":"inscripcion",
        "class": Inscripciones,
        "pk": "id",
        "fields": {
            "id": {"label": "ID Inscripción (Vacío si es Nuevo)", "type": "number", "valid": "integer", "readonly_on_create": True},
            "fecha_inscripcion": {"label": "Fecha Inscripción (AAAA-MM-DD)", "type": "string", "valid": "date"},
            "estudiante": {"label": "Cédula Estudiante", "type": "string", "valid": "alphanumeric"},
            "curso": {"label": "Código del Curso", "type": "string", "valid": "alphanumeric"}
        }
    },
    "Asistencias": {
        "table_name":"asistencia",
        "class": Asistencias,
        "pk": "id",
        "fields": {
            "id": {"label": "ID Asistencia (Vacío si es Nuevo)", "type": "number", "valid": "integer", "readonly_on_create": True},
            "fecha_asistencia": {"label": "Fecha (AAAA-MM-DD)", "type": "string", "valid": "date"},
            "estudiante": {"label": "Cédula Estudiante", "type": "string", "valid": "alphanumeric"},
            "curso": {"label": "Código del Curso", "type": "string", "valid": "alphanumeric"}
        }
    }
}

class AppGui:
    def __init__(self, root: GUI.Tk, container):
        self.root = root
        self.event_manager = container.obtener("eventos")
        self.validadores = container.obtener("validadores")


        #Eventos operativos (Servicios)
        self.event_manager.suscribir("on_nomina_calculada", self.mostrar_resultado_nomina)
        self.event_manager.suscribir("on_inventario_calculado", self.mostrar_resultado_inventario)
        self.event_manager.suscribir("on_asistencia_calculada", self.mostrar_resultado_asistencia)
        self.event_manager.suscribir("on_dashboard_stats_loaded", self.renderizar_dashboard)

        #CONFIGURACION DE LA VENTANA PRINCIPAL
        self.configurar_ventana_principal()
        self.aplicar_estilos()
        self.crear_arq_paneles()
        self.construir_menu_desplegable()

    #implementar los metodos de configuracion de la ventana, estilos, paneles y menu desplegable
    def configurar_ventana_principal(self):
        self.root.title("Sistema de Gestión CDC")
        self.root.geometry("1000x500")
        self.root.minsize(950, 400)
    
    def aplicar_estilos(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        #paleta de colores
        self.COLOR_PRIMARY = "#2c3e50"
        self.COLOR_SECONDARY = "#18bc9c"
        self.COLOR_BG = "#f8f9fa"
        self.COLOR_TEXT = "#2d3e50"

        self.root.configure(bg=self.COLOR_BG)

        self.style.configure('TFrame', background=self.COLOR_BG)
        self.style.configure('Sidebar.TFrame', background=self.COLOR_PRIMARY)
        self.style.configure('Header.TFrame', background=self.COLOR_PRIMARY)
        
        self.style.configure('TLabel', background = self.COLOR_BG, foreground=self.COLOR_TEXT, font=('Arial', 10))
        self.style.configure('Header.TLabel', background=self.COLOR_PRIMARY, foreground='white', font=('Arial', 12, 'bold'))
        self.style.configure('Title.TLabel', background = self.COLOR_BG, foreground= self.COLOR_PRIMARY, font = ('Arial', 14, 'bold'))
        #Configuracion de botones
        self.style.configure('TButton', background=self.COLOR_SECONDARY, foreground='white', font=('Arial', 10), borderwidth=0)
        self.style.map('TButton', background=[('active', '#128F76')])

        self.style.configure('Action.TButton', font=('Arial', 10, 'bold'), background="#34495E", foreground = 'white')
        self.style.configure('Danger.TButton', font=('Arial', 10, 'bold'), background="#E74C3C", foreground = 'white')
        self.style.configure('Danger.TButton', background=[('active', '#C0392B')])

        #Configuracion de data grids
        self.style.configure('Treeview', background='white', rowheight=25, fieldbackground='white', font=('Arial', 10))
        self.style.configure('Treeview.Heading', background='#EAECEE', foreground=self.COLOR_TEXT, font=('Arial', 10, 'bold'))

    def crear_arq_paneles(self):
        #Panel superior
        self.header_panel = ttk.Frame(self.root, style = 'Header.TFrame', height=50)
        self.header_panel.pack(side=GUI.TOP, fill=GUI.X)
        self.header_panel.pack_propagate(False)

        label_title = ttk.Label(self.header_panel, text="Sistema de Gestión CDC", style='Header.TLabel')
        label_title.pack(side=GUI.LEFT, padx=20, pady=10)
        #Espacio de trabajo dinamico
        self.main_workplace = ttk.Frame(self.root, style='TFrame')
        self.main_workplace.pack(side=GUI.TOP, fill=GUI.BOTH, expand=True, padx=20,pady=20)
        self.cargar_modulo_dashboard()
    
    def construir_menu_desplegable(self):
        barra_menus = GUI.Menu(self.root)

        #Menu de opciones para CRUD
        menu_modulos = GUI.Menu(barra_menus, tearoff=0)
        for mod in MODEL_METADATA.keys():
            menu_modulos.add_command(label = f'Gestion de {mod}', command= lambda m=mod: self.cargar_modulo_crud(m))
        barra_menus.add_cascade(label='Módulos de registro', menu=menu_modulos)

        #Menu de operaciones
        menu_operaciones = GUI.Menu(barra_menus, tearoff=0)
        menu_operaciones.add_command(label="Calculo de Nomina", command=self.ejecutar_operacion_nomina)
        menu_operaciones.add_command(label="Valoracion de invetario", command=self.ejecutar_operacion_inventario)
        menu_operaciones.add_command(label="Metricas de asistencia", command=self.ejecutar_operacion_asistencia)
        barra_menus.add_cascade(label='Procesos Operativos',menu=menu_operaciones)

        #Menu del Sistema
        menu_sistema = GUI.Menu(barra_menus, tearoff=0)
        menu_sistema.add_command(label = 'Inicio', command=self.cargar_modulo_dashboard)
        menu_sistema.add_separator()
        menu_sistema.add_command(label='Salir', command=self.root.quit)
        barra_menus.add_cascade(label='Sistema', menu=menu_sistema)

        self.root.config(menu=barra_menus)
    
    def limpiar_area_trabajo(self):
        for widget in self.main_workplace.winfo_children():
            widget.destroy()
        
    def cargar_modulo_dashboard(self):
        self.limpiar_area_trabajo()
        label_dashboard = ttk.Label(self.main_workplace, text="Dashboard del Sistema de Gestión CDC", style='Title.TLabel')
        label_dashboard.pack(anchor=GUI.W,pady=(0,10))

        self.event_manager.emitir("request_dashboard_stats")

    def renderizar_dashboard(self, stats:dict):
        """El Callback  es llamado cuando el controlador responde."""
        contenedor_target = GUI.Frame(self.main_workplace)
        contenedor_target.pack(fill=GUI.X, pady=10)

        for idx, (nombre_mod, total) in enumerate(stats.items()):
            target = GUI.Frame(contenedor_target, bg='white', highlightbackground='#BDC3C7', highlightthickness=1,bd=0)
            target.grid(row=idx // 3, column=idx % 3, padx=15, pady=15, sticky='nsew')

            label_tittle = GUI.Label(target, text=nombre_mod.upper(), font=('Arial', 12, 'bold'), fg=self.COLOR_PRIMARY, bg='white')
            label_tittle.pack(pady=(15,5), padx=20)

            label_count = GUI.Label(target, text=str(total), font=('Arial', 20, 'bold'), fg=self.COLOR_SECONDARY, bg='white')
            label_count.pack(pady=(0,15))
            
        for i in range(3):
            contenedor_target.columnconfigure(i, weight=1)
        
    #Aplicacion de patron factory para crear formularios dinamicos para cada modulo
    
        
    
    def cargar_modulo_crud(self, nombre_modulo:str):
        self.limpiar_area_trabajo()
        meta = MODEL_METADATA[nombre_modulo]
        tabla = meta['table_name']
        
        #Funcion que permite capturar el msg de respuesta que emite el controlador
        def manejar_msg_crud(msg:str):
            self.mostrar_msg_exito(msg)
            self.event_manager.emitir(f"request_read_all_{tabla}",{})

        #Inicializamos los eventos registrados para evitar que al realizar alguna
        #acción esta de error al buscar en eventos viejos

        self.event_manager.listeners[f'on_error_{tabla}']=[]
        self.event_manager.listeners[f'on_success_save_{tabla}']=[]
        self.event_manager.listeners[f'on_success_update_{tabla}']=[]
        self.event_manager.listeners[f'on_success_delete_{tabla}']=[]
        self.event_manager.listeners[f'on_data_loaded_{tabla}']=[]
        self.event_manager.listeners[f'data_changed_{tabla}']=[]
        #Suscripcion de eventos (Nota: los nombres los coloca el programador,
        #usar nombres de eventos descriptivos para que el codigo sea )
        self.event_manager.suscribir(f"on_error_{tabla}", self.mostrar_msg_error)
        self.event_manager.suscribir(f"on_success_save_{tabla}", manejar_msg_crud)
        self.event_manager.suscribir(f"on_success_update_{tabla}",manejar_msg_crud)
        self.event_manager.suscribir(f"on_success_delete_{tabla}", manejar_msg_crud)
        
        #Titulo del modulo activo
        label_modulo = ttk.Label(self.main_workplace, text=f"Gestión de {nombre_modulo}", style='Title.TLabel')
        label_modulo.grid(row=0, column=0, columnspan=2, sticky=GUI.W, pady=(0,15))
     
        #Validaciones a nivel de pulsaciones de teclas para los campos del formulario
        validaciones={
            "integer":(self.root.register(self.validadores["integer"].validar), '%P'),
            "float" :(self.root.register(self.validadores["float"].validar), '%P'),
            "text":(self.root.register(self.validadores["text"].validar), '%P')
        }
        
        builder = CRUDViewBuilder(self.main_workplace, meta, validaciones, self.aplicar_mascara_cedula)

        builder.construir_contenedores()
        builder.construir_formulario()
        btn_crear,btn_limpiar,btn_eliminar= builder.construir_botones_accion()
        btn_buscar, campo = builder.panel_busqueda()
        grid_datos = builder.construir_datagrid()
        form_variables = builder.obtener_variables()
        
        #Enlace de la logica de la interfaz principal con los componentes Builder
        btn_crear.config(command= lambda : self.ejecutar_guardado_dinamico(nombre_modulo, form_variables, grid_datos))
        btn_eliminar.config(command= lambda: self.ejecutar_eliminacion_dinamica(nombre_modulo, form_variables, grid_datos))
        btn_limpiar.config(command= lambda: self.limpiar_formulario(form_variables, meta, grid_datos))
        btn_buscar.config(command=lambda: self.ejecutar_busqueda_dinamica(nombre_modulo, campo))
        #Enlace para pasar los datos de la tabla a el formulario para actualizar los datos
        grid_datos.bind('<<TreeviewSelect>>', lambda event: self.transferir_grid_a_formulario(nombre_modulo, grid_datos, form_variables))
        
        self.event_manager.suscribir(f"data_changed_{tabla}",lambda registro: self.llenar_grid_datos(nombre_modulo, grid_datos, registro))
        self.event_manager.suscribir(f"on_data_loaded_{tabla}", lambda registros: self.llenar_grid_datos(nombre_modulo,grid_datos, registros))
        self.event_manager.emitir(f"request_read_all_{tabla}",{})
        
    def llenar_grid_datos(self, nombre_modulo:str, grid:ttk.Treeview, registros:list[dict]):
        """Callback que inyecta los datos en el grid una vez el controlador responde"""
        for item in grid.get_children():
            grid.delete(item)
        
        meta = MODEL_METADATA[nombre_modulo]
        if len(registros) > 1:
            for reg in registros:
                valores = []
                for field in meta['fields'].keys():
                    val = reg.get(field, "")
                    #Si el campo es una cedula mostrarlo formateado
                    if meta['fields'][field].get('valid') == "cedula" and val:
                        try:
                            val = f"{int(val):,}".replace(",",".")
                        except ValueError:
                            pass
                    valores.append(val)
                grid.insert("", GUI.END, values=valores)
    #Control de datos dinamicos y procesamiento de CRUD interno
    
    def transferir_grid_a_formulario(self, nombre_modulo: str, grid: ttk.Treeview, form_vars: dict):
        seleccion = grid.selection()
        if not seleccion:
            return
        
        valores_fila = grid.item(seleccion[0], 'values')
        meta = MODEL_METADATA[nombre_modulo]
        for idx, field in enumerate(meta['fields'].keys()):
            if idx < len(valores_fila):
                #Se reactiva el campo momentaneamente para permitir la asignacion de valores
                if meta['fields'][field].get('readonly_on_create', False):
                    for widget in self.main_workplace.focus_get().master.winfo_children():
                        if isinstance(widget, ttk.Entry) and meta['fields'][field]['label'] in widget.master.winfo_children():
                            widget.config(state='normal')
                form_vars[field].set(str(valores_fila[idx]))
    
    
    def limpiar_formulario(self, form_vars:dict, meta:dict, grid: ttk.Treeview):
        for field, var in form_vars.items():
            if meta['fields'][field].get('readonly_on_create', False):
                continue
            var.set("")
        if grid:
            grid.selection_remove(grid.selection())

    def ejecutar_busqueda_dinamica(self, nombre_modulo:str,campo:GUI.Entry):
        meta = MODEL_METADATA[nombre_modulo]
        tabla = meta['table_name']
        pk = campo.get().strip()

        if pk:
            self.event_manager.emitir(f"request_read_{tabla}",pk)
        else:
            messagebox.showwarning("Dato invalido", "El dato ingresado no coincide con ningun registro")


    def ejecutar_guardado_dinamico(self, nombre_modulo:str, form_vars: dict, grid: ttk.Treeview):
        meta = MODEL_METADATA[nombre_modulo]
        tabla = meta["table_name"]
        pk_field = meta['pk']
        payload={}
        
        for field, var in form_vars.items():
            val_string = var.get().strip()
            #Validación estricta
            if not val_string and not meta['fields'][field].get('readonly_on_create', False):
                messagebox.showwarning("Validación de campo", f'El campo "{meta["fields"][field]["label"]}" no puede estar vacío.')
                return
            #Limpieza de cedula
            if meta['fields'][field].get('valid') == "cedula":
                pure_cd = self.purificar_cedula(val_string)
                #Valdación de longitud de cédula requerida entre 6-8
                if not (6 <= len(pure_cd) <=8):
                    messagebox.showwarning("Validación de cédula", f'La cédula "{pure_cd}" debe tener entre 6 y 8 dígitos.')
                    return
                payload[field] = pure_cd
            else:
                #Conversion de tipos
                if meta['fields'][field]['type'] == "number":
                    if meta['fields'][field]['valid'] == "integer":
                        payload[field] = int(val_string) if val_string else None
                    else:
                        payload[field] = float(val_string) if val_string else None
                else:
                    payload[field] = val_string
        
        #Verificamos si es una trasaccion insert o update
        select = grid.selection()
        if select:
            values_reg = grid.item(select[0], 'values')
            columnas = list(meta['fields'].keys())
            pk_index = columnas.index(pk_field)
            pk_value = values_reg[pk_index]

            if meta['fields'][pk_field].get('valid') == "cedula":
                pk_value  = self.purificar_cedula(pk_value)
            
            payload_update ={
                "id":pk_value,
                "data":payload
            }
            self.event_manager.emitir(f"request_update_{tabla}", payload_update)
        else:
            self.event_manager.emitir(f"request_save_{tabla}", payload)
        
        self.limpiar_formulario(form_vars, meta, grid)       
    
    def ejecutar_eliminacion_dinamica(self, nombre_modulo:str, form_vars:dict, grid:ttk.Treeview)->None:
        meta = MODEL_METADATA[nombre_modulo]
        tabla = meta['table_name']
        pk_field = meta['pk']
        pk_value = form_vars[pk_field].get().strip()

        if meta['fields'][pk_field].get('valid') == "cedula":
            pk_value = self.purificar_cedula(pk_value)

        if not pk_value:
            messagebox.showwarning("Validación de campo", f'El campo "{meta["fields"][pk_field]["label"]}" debe ser valido.')
            return
        #Confirmacion de la eliminación del registro
        confirmacion = messagebox.askyesno("Confirmar Eliminación", f"¿Está seguro de eliminar el registro?")
        if confirmacion:
            self.event_manager.emitir(f"request_delete_{tabla}",pk_value)
            self.limpiar_formulario(form_vars, meta, grid)

    #Logica de negocio para los procesos operativos.
    def ejecutar_operacion_inventario(self)->None:
        self.event_manager.emitir("request_calculo_inventario")
    
    def mostrar_resultado_inventario(self, data:dict):
        self.limpiar_area_trabajo()
        lbl_titulo = ttk.Label(self.main_workplace, text="Valoración Patrimonial Total - Bienes e Inmuebles", style="Title.TLabel")
        lbl_titulo.pack(anchor=GUI.W, pady=(0, 15))
        
        frame_resumen = ttk.LabelFrame(self.main_workplace, text="Métricas Consolidadas", padding=20)
        frame_resumen.pack(fill=GUI.BOTH, expand=True)
            
        ttk.Label(frame_resumen, text=f"Total de Ítems Registrados: {data['total_items']}", font=("Segoe UI", 12)).pack(anchor=GUI.W, pady=10)
        ttk.Label(frame_resumen, text=f"Valoración Financiera: {data['capital_total']}", font=("Segoe UI", 14, "bold"), foreground=self.COLOR_SECONDARY).pack(anchor=GUI.W, pady=10)

    def ejecutar_operacion_nomina(self):
        self.event_manager.emitir("request_calculo_nomina")
    
    def mostrar_resultado_nomina(self, data:dict):
        self.limpiar_area_trabajo()
        lbl_titulo = ttk.Label(self.main_workplace, text="Simulación de Nómina Presupuestaria Institucional", style="Title.TLabel")
        lbl_titulo.pack(anchor=GUI.W, pady=(0, 15))
        
        frame_resumen = ttk.LabelFrame(self.main_workplace, text="Proyección Presupuestaria Mensual", padding=20)
        frame_resumen.pack(fill=GUI.BOTH, expand=True)
            
        ttk.Label(frame_resumen, text=f"Personal Activo Evaluado: {data['total_items']} empleados", font=("Segoe UI", 12)).pack(anchor=GUI.W, pady=10)
        ttk.Label(frame_resumen, text=f"Costo Total Estimado de Nómina: {data['total_nomina']:,.2f} $M".replace(",", "X").replace(".", ",").replace("X", "."), font=("Segoe UI", 14, "bold"), foreground="#E74C3C").pack(anchor=GUI.W, pady=10)
        
    def ejecutar_operacion_asistencia(self)->None:
        self.event_manager.emitir("request_operacion_asistencia")
    
    def mostrar_resultado_asistencia(self, data:dict)->None:
        self.limpiar_area_trabajo()
        lbl_titulo = ttk.Label(self.main_workplace, text="Estadísticas Avanzadas de Asistencia Escolar", style="Title.TLabel")
        lbl_titulo.pack(anchor=GUI.W, pady=(0, 15))
        
        frame_resumen = ttk.LabelFrame(self.main_workplace, text="Métricas de Participación Académica", padding=20)
        frame_resumen.pack(fill=GUI.BOTH, expand=True)
            
        ttk.Label(frame_resumen, text=f"Total de asistencias: {data['total_asistencias']}", font=("Segoe UI", 12)).pack(anchor=GUI.W, pady=10)
        ttk.Label(frame_resumen, text=f"Porcentaje asistencial: {data['porcentaje_asistencia']}", font=("Segoe UI", 14, "bold"), foreground=self.COLOR_PRIMARY).pack(anchor=GUI.W, pady=10)

    def mostrar_msg_exito(self, msg:str=""):
        messagebox.showinfo("Operacion exitosa", msg)
    
    def mostrar_msg_error(self, msg: str = ""):
        messagebox.showerror("Error", msg)
    
        #Validaciones y enmascaramiento en tiempo real.
    
    def validar_entero(self, texto : str) -> bool:
        if texto == "":
            return True
        return texto.isdigit()
        
    def validar_flotante(self, texto: str) -> bool:
        if texto == "":
            return True
        try:
            float(texto)
            return True
        except ValueError:
            return False
    
    def validar_texto(self, texto : str) -> bool:
        if texto == "":
            return True
        
        #Permite letras, espacios y caracteres especiales comunes en nombres
        return all(c.isalpha() or c.isspace() for c in texto)
    
    def aplicar_mascara_cedula(self, var: GUI.StringVar):
        #Filtra para dejar exclusivamente digitos numéricos y purificados
        raw_digits = "".join([c for c in var.get() if c.isdigit()])
        #Se restringe la cedula a un maximo de 8 digitos
        if len(raw_digits)>8:
            raw_digits = raw_digits[:8]
        
        if not raw_digits:
            var.set("")
            return
        
        #Algoritmo de enmascaramiento para cédula por .
        valor_int = int(raw_digits)
        formatted = f"{valor_int:,}".replace(",",".")
        var.set(formatted)
    
    def purificar_cedula(self, cedula: str) -> str:
        return cedula.replace(".", "").strip()
