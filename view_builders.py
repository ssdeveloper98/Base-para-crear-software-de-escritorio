import tkinter as GUI
from tkinter import ttk

class CRUDViewBuilder:
    """clase constructora para crear cada componente de la interfaz principal
    peritiendo desacoplar la logica de la interfaz del diseño de la misma"""

    #Constructor
    def __init__(self, frame: ttk.Frame, meta: dict, validaciones:dict, enmascaramiento_cedula):
        """frame: Contenedor donde se agregaran los componentes (main_workplace)
           meta: Diccionario de datos del modulo activo (MODEL_METADATA)
           validaciones: Diccionario para los comandos de validacion pre-registrados
           enmascaramiento_cedula: funcion para enmascarar la cedula en tienpo real"""
        
        self.frame = frame
        self.meta = meta
        self.validaciones = validaciones
        self.enmascaramiento_cedula = enmascaramiento_cedula
    
        #Diccionarios para almecenarar lo construido
        self.form_variables ={}
        self.frame_form = None
        self.frame_grid = None
        self.ultimo_row_idx = 0
    
    def construir_contenedores(self):
        
        #Panel Izquierdo, el formulario es generado dinamicamente
        self.frame_form= ttk.LabelFrame(self.frame, text="Datos de registro", padding=15)
        self.frame_form.grid(row=1, column=0, sticky='nsew', padx=(0,15), pady=(0,15))
        
        #Panel derecho, DataGrid(celdas) para mostrar registros
        self.frame_grid = ttk.LabelFrame(self.frame, text="Registros", padding=10)
        self.frame_grid.grid(row=1, column=1, sticky='nsew')
        
        #Configuracion de propiedades responsive
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=3)
        self.frame.rowconfigure(1, weight=1)
        
        return self

    def construir_formulario(self):
        """Construye dinamicamente cada campo y label del formulario a traves de los metadatos """
        row_idx = 0
        for field_name, props in self.meta["fields"].items():
            label = ttk.Label(self.frame_form, text =f"{props['label']}:")
            label.grid(row=row_idx, column=0, sticky=GUI.W, pady=6, padx=(0,10))

            if props['type'] == "combo":
                var = GUI.StringVar()
                widget = ttk.Combobox(self.frame_form, textvariable=var, values=props['values'], state='readonly',width=25)
                widget.current(0)
                widget.grid(row=row_idx, column=1, sticky=GUI.W, pady=6)
                self.form_variables[field_name] = var
            
            elif props['type'] in ["string", "number", "cedula"]:
                var = GUI.StringVar()
                widget = ttk.Entry(self.frame_form, textvariable=var, width=28)

                #Validaciones de entrada
                valid_type = props.get('valid')
                if valid_type in self.validaciones:
                    widget.config(validate='key', validatecommand=self.validaciones[valid_type])
                elif valid_type == 'cedula':
                    widget.bind('<KeyRelease>', lambda event, v=var : self.enmascaramiento_cedula(v))

                if props.get('readonly_on_create', False):
                    widget.config('disabled')

                widget.grid(row=row_idx, column=1, sticky=GUI.W, pady=6)
                self.form_variables[field_name] = var
            row_idx +=1
        self.ultimo_row_idx = row_idx
        return self
            
    def construir_botones_accion(self):
        """Crea el panel inferior de botones con las acciones: Guardar, Limpiar, Eliminar"""

        #Panel de acciones internas(CRUD)
        frame_acciones = ttk.Frame(self.frame_form)
        frame_acciones.grid(row=self.ultimo_row_idx, column=0, columnspan=2, pady=15, sticky=GUI.EW)
        
        #Boton crear/guardar registro
        btn_crear = ttk.Button(frame_acciones, text="Guardar")
        btn_crear.pack(side=GUI.LEFT, padx=4)
        
        #Boton eliminar registro
        btn_eliminar = ttk.Button(frame_acciones, text="Eliminar", style='Danger.TButton')
        btn_eliminar.pack(side=GUI.RIGHT, padx=4)
        
        #Boton limpiar formulario
        btn_limpiar = ttk.Button(frame_acciones, text="Limpiar campos", style='Action.TButton')
        btn_limpiar.pack(side = GUI.RIGHT, padx=4)

        return btn_crear, btn_limpiar, btn_eliminar

    def panel_busqueda(self):
        panel_busqueda = ttk.Frame(self.frame_grid, width=30, height=4)
        panel_busqueda.pack(side=GUI.TOP, padx=1)
        
        
        campo = GUI.Entry(panel_busqueda, width=20)
        campo.pack(side=GUI.LEFT, padx=4)
        btn_buscar = ttk.Button(panel_busqueda, text="Buscar", style='Action.TButton')
        btn_buscar.pack(side = GUI.RIGHT, padx=4)

        return btn_buscar, campo

    def construir_datagrid(self)->ttk.Treeview:
        """Construccion de las celdas para mostrar los datos con sus barras de desplazamiento"""
        columnas= list(self.meta['fields'].keys())
        grid_datos = ttk.Treeview(self.frame_grid, columns=columnas, show="headings", selectmode='browse')
        

        for col in columnas:
            grid_datos.heading(col, text=self.meta["fields"][col]["label"].upper())
            grid_datos.column(col, width=110, anchor=GUI.CENTER)
        
        grid_datos.pack(side=GUI.LEFT, fill=GUI.BOTH, expand=True)
        
        #Scrollbar Vertical
        scrollbar_vert = ttk.Scrollbar(self.frame_grid, orient=GUI.VERTICAL, command = grid_datos.yview)
        grid_datos.configure(yscrollcommand= scrollbar_vert.set)
        scrollbar_vert.pack(side=GUI.RIGHT, fill=GUI.Y)
        
        #Scrollbar Inferior
        scrollbar_inf = ttk.Scrollbar(grid_datos, orient=GUI.HORIZONTAL, command= grid_datos.xview)
        grid_datos.configure(xscrollcommand=scrollbar_inf.set)
        scrollbar_inf.pack(side=GUI.BOTTOM, fill=GUI.X)

        return grid_datos
    
    def obtener_variables(self)->dict:
        """Retorna un mapa de variables de Tkinter asociadas al formulario"""
        return self.form_variables