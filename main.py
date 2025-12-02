"""
LegalMente - Sistema Experto Legal
===================================
Aplicación de escritorio desarrollada con Flet para gestionar trámites legales
en Ensenada, B.C. El sistema utiliza un motor de inferencia para proporcionar
información personalizada según el perfil del usuario (residente/foráneo).

Autor: Ponchito's Team
Versión: 1.0
Dependencias: flet, logic.sistema, ui.elementos
"""

import flet as ft
from logic import sistema
from ui import elementos

# ============================================================================
# INICIALIZACIÓN DEL BACKEND
# ============================================================================
# Instancia del motor de inferencia que carga automáticamente los hechos
# y reglas del sistema experto
backend = sistema.BackendLegal()


# ============================================================================
# FUNCIÓN PRINCIPAL DE LA APLICACIÓN
# ============================================================================
def main(page: ft.Page):
    """
    Punto de entrada principal de la aplicación.
    
    Configura la ventana, tema visual e inicializa el flujo de navegación
    comenzando con la validación de edad del usuario.
    
    Args:
        page (ft.Page): Objeto página principal de Flet que contiene todos
                        los elementos de la interfaz
    """
    
    # ------------------------------------------------------------------------
    # CONFIGURACIÓN DE LA VENTANA Y TEMA
    # ------------------------------------------------------------------------
    page.title = "LegalMente - Sistema Experto"
    page.window_width = 1100
    page.window_height = 800
    page.theme_mode = "light"
    page.padding = 0
    
    # Intenta aplicar tema con color índigo, maneja excepciones por compatibilidad
    try: 
        page.theme = ft.Theme(color_scheme_seed=ft.Colors.INDIGO)
    except: 
        pass

    # ------------------------------------------------------------------------
    # ESTADO DE LA APLICACIÓN
    # ------------------------------------------------------------------------
    # Diccionario que mantiene el estado global de la sesión
    state = {
        "es_residente": False,          # Indica si el usuario reside en Ensenada
        "tramite_seleccionado": None    # Nombre del trámite actualmente seleccionado
    }

    # ========================================================================
    # COMPONENTES DEL PANEL DERECHO (DASHBOARD)
    # ========================================================================
    
    # Título dinámico que muestra el trámite seleccionado
    lbl_titulo_tramite = ft.Text(
        "Selecciona un trámite", 
        size=24, 
        weight="bold", 
        color=ft.Colors.INDIGO, 
        text_align=ft.TextAlign.CENTER
    )
    
    # Tarjetas de información visual para datos clave del trámite
    card_dependencia = elementos.crear_tarjeta_info(
        "DEPENDENCIA", "-", ft.Icons.ACCOUNT_BALANCE, ft.Colors.BLUE
    )
    card_vigencia = elementos.crear_tarjeta_info(
        "VIGENCIA", "-", ft.Icons.TIMER, ft.Colors.ORANGE
    )
    card_modalidad = elementos.crear_tarjeta_info(
        "MODALIDAD", "-", ft.Icons.LAPTOP_MAC, ft.Colors.PURPLE
    )
    
    # Fila que contiene las tarjetas de resumen (inicialmente oculta)
    row_resumen = ft.Row(
        [card_dependencia, card_vigencia, card_modalidad], 
        spacing=20, 
        visible=False, 
        alignment=ft.MainAxisAlignment.CENTER
    )

    # Contenedor scrolleable para mostrar detalles del trámite
    contenedor_detalles = ft.Column(
        scroll=ft.ScrollMode.AUTO, 
        expand=True, 
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )
    
    # Panel derecho completo que agrupa todos los elementos de visualización
    panel_derecho = ft.Container(
        content=ft.Column([
            ft.Container(height=10),
            lbl_titulo_tramite,
            ft.Divider(color=ft.Colors.TRANSPARENT, height=15),
            row_resumen,
            ft.Divider(),
            ft.Text(
                "Información Detallada", 
                size=12, 
                weight="bold", 
                color=ft.Colors.GREY_400
            ),
            ft.Container(
                content=contenedor_detalles,
                padding=20,
                bgcolor=ft.Colors.GREY_50,
                border_radius=10,
                expand=True,
                alignment=ft.alignment.top_center
            )
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        padding=30, 
        expand=True, 
        bgcolor=ft.Colors.WHITE
    )

    # Grid para mostrar la lista de trámites disponibles (panel izquierdo)
    grid_tramites = ft.GridView(
        expand=True, 
        runs_count=1,           # Una columna
        max_extent=300,         # Ancho máximo de cada elemento
        child_aspect_ratio=4.0, # Relación ancho/alto
        spacing=10, 
        run_spacing=10
    )

    # ========================================================================
    # FUNCIONES DE CONTROL Y LÓGICA
    # ========================================================================

    def actualizar_panel_central(tramite):
        """
        Actualiza el panel derecho con información del trámite seleccionado.
        
        Consulta al motor de inferencia (backend) los datos de dependencia,
        vigencia y modalidad, luego actualiza las tarjetas visuales.
        
        Args:
            tramite (str): Nombre identificador del trámite seleccionado
        """
        row_resumen.visible = True
        
        # Consultas al motor de inferencia para obtener datos del trámite
        raw_dep = backend.consultar_motor_real(tramite, 'dependencia', 'Lugar')
        raw_vig = backend.consultar_motor_real(tramite, 'vigencia', 'Tiempo')
        raw_mod = backend.consultar_motor_real(tramite, 'modalidad_tramite', 'Modo')

        # Limpieza de las respuestas obtenidas del motor
        dep = backend.limpiar_respuesta_motor(raw_dep)
        vig = backend.limpiar_respuesta_motor(raw_vig)
        mod = backend.limpiar_respuesta_motor(raw_mod)

        # Actualización de valores en las tarjetas (con valores por defecto)
        card_dependencia.content.controls[2].value = dep if dep != "N/A" else "No especif."
        card_vigencia.content.controls[2].value = vig if vig != "N/A" else "Variable"
        card_modalidad.content.controls[2].value = mod if mod != "N/A" else "Híbrido"
        
        # Limpia y resetea el contenedor de detalles con mensaje inicial
        contenedor_detalles.controls.clear()
        contenedor_detalles.controls.append(
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.TOUCH_APP, size=40, color=ft.Colors.GREY_300),
                    ft.Text("Consulta Requisitos o Costos abajo", color=ft.Colors.GREY_400)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                alignment=ft.alignment.center, 
                padding=40
            )
        )
        page.update()

    def accion_botones(tipo):
        """
        Maneja las acciones de los botones "Ver Requisitos" y "Ver Costos".
        
        Consulta la información correspondiente al backend y la formatea
        visualmente según el tipo de consulta (requisitos o costos).
        
        Args:
            tipo (str): Tipo de información a consultar ('requiere' o 'costo')
        """
        tramite = state["tramite_seleccionado"]
        if not tramite: 
            return
        
        # Consulta al motor de inferencia
        texto_raw = backend.consultar_motor_real(tramite, tipo)
        contenedor_detalles.controls.clear()
        items_visuales = []
        
        # Formateo especial para costos (tarjetas verdes con ícono de moneda)
        if tipo == 'costo':
            lista_costos = backend.procesar_costos_inteligente(texto_raw)
            for costo in lista_costos:
                items_visuales.append(
                    ft.Container(
                        content=ft.ListTile(
                            leading=ft.Icon(
                                ft.Icons.MONETIZATION_ON, 
                                color=ft.Colors.GREEN_700, 
                                size=24
                            ),
                            title=ft.Text(
                                costo, 
                                size=13, 
                                weight="bold", 
                                color=ft.Colors.BLACK87
                            ),
                        ),
                        bgcolor=ft.Colors.GREEN_50,
                        border_radius=10,
                        padding=5,
                        margin=ft.margin.only(bottom=5)
                    )
                )
        else:
            # Formateo para requisitos (lista con checks)
            texto_limpio = backend.limpiar_respuesta_motor(texto_raw)
            for l in texto_limpio.split('\n'):
                if l.strip() and l != "N/A":
                    items_visuales.append(
                        ft.ListTile(
                            leading=ft.Icon(
                                ft.Icons.CHECK_CIRCLE, 
                                color=ft.Colors.INDIGO, 
                                size=20
                            ),
                            title=ft.Text(l, size=13, weight="w500"),
                            dense=True,
                        )
                    )
        
        # Mensaje por defecto si no hay información disponible
        if not items_visuales: 
            items_visuales.append(
                ft.Text("Información no disponible.", color=ft.Colors.RED_400)
            )
        
        contenedor_detalles.controls.append(ft.Column(items_visuales))
        page.update()

    # Botones de acción (inicialmente deshabilitados hasta seleccionar trámite)
    btn_req = ft.ElevatedButton(
        "Ver Requisitos", 
        icon=ft.Icons.LIST_ALT, 
        on_click=lambda _: accion_botones('requiere'), 
        disabled=True
    )
    btn_cost = ft.ElevatedButton(
        "Ver Costos", 
        icon=ft.Icons.ATTACH_MONEY, 
        on_click=lambda _: accion_botones('costo'), 
        disabled=True
    )

    def seleccionar_tramite(e):
        """
        Maneja la selección de un trámite de la lista.
        
        Actualiza el estado visual (resaltado), habilita los botones de acción
        y carga la información básica del trámite seleccionado.
        
        Args:
            e (ft.ControlEvent): Evento generado por el clic en un trámite
        """
        nombre = e.control.data
        state["tramite_seleccionado"] = nombre
        
        # Actualiza el resaltado visual de los trámites
        for c in grid_tramites.controls:
            c.bgcolor = ft.Colors.WHITE
            c.border = None
            if c.data == nombre:
                c.bgcolor = ft.Colors.INDIGO_50
                c.border = ft.border.all(2, ft.Colors.INDIGO)
        
        # Actualiza el título y habilita botones
        lbl_titulo_tramite.value = nombre.replace("_", " ").upper()
        btn_req.disabled = False
        btn_cost.disabled = False
        
        # Carga información inicial del trámite
        actualizar_panel_central(nombre)

    # ========================================================================
    # FUNCIONES DE NAVEGACIÓN ENTRE PANTALLAS
    # ========================================================================

    def cargar_dashboard():
        """
        Carga la pantalla principal del dashboard.
        
        Muestra el panel izquierdo con la lista de trámites filtrados según
        el tipo de usuario (residente/foráneo) y el panel derecho con detalles.
        """
        page.clean()
        
        # Selecciona la lista de trámites según el perfil del usuario
        lista = (backend.TRAMITES_RESIDENTES if state["es_residente"] 
                 else backend.TRAMITES_NO_RESIDENTES)
        
        grid_tramites.controls.clear()
        
        # Crea tarjetas para cada trámite disponible
        for t in lista:
            grid_tramites.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.DESCRIPTION, color=ft.Colors.INDIGO_300, size=20),
                        ft.Text(
                            t.replace("_", " ").title(), 
                            size=12, 
                            weight="bold", 
                            expand=True
                        )
                    ]),
                    data=t, 
                    on_click=seleccionar_tramite,
                    bgcolor=ft.Colors.WHITE, 
                    padding=12, 
                    border_radius=8, 
                    ink=True,
                    shadow=ft.BoxShadow(blur_radius=2, color=ft.Colors.GREY_200)
                )
            )

        # Layout principal: panel izquierdo (lista) + panel derecho (detalles)
        layout = ft.Row([
            # Panel izquierdo - Lista de trámites
            ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.GAVEL, color=ft.Colors.WHITE), 
                            ft.Text(
                                "LegalMente", 
                                color=ft.Colors.WHITE, 
                                weight="bold", 
                                size=18
                            )
                        ]), 
                        bgcolor=ft.Colors.INDIGO, 
                        padding=20, 
                        border_radius=10
                    ),
                    ft.Divider(),
                    grid_tramites
                ]),
                width=300, 
                bgcolor=ft.Colors.GREY_100, 
                padding=15
            ),
            # Panel derecho - Detalles del trámite
            ft.Container(
                content=ft.Column([
                    panel_derecho,
                    ft.Container(
                        content=ft.Row(
                            [btn_req, btn_cost], 
                            alignment=ft.MainAxisAlignment.CENTER
                        ), 
                        padding=20, 
                        bgcolor=ft.Colors.WHITE
                    )
                ]),
                expand=True
            )
        ], expand=True, spacing=0)
        
        page.add(layout)

    def ir_a_dashboard(residente):
        """
        Transición hacia el dashboard principal.
        
        Actualiza el estado del usuario y configura los hechos en el motor
        de inferencia según si es residente o foráneo.
        
        Args:
            residente (bool): True si el usuario es residente de Ensenada
        """
        state["es_residente"] = residente
        
        # Actualiza los hechos en el motor de inferencia
        if residente:
            backend.HECHOS_SESION = [('reside_en_ensenada', 'usuario_actual')]
        else:
            backend.HECHOS_SESION = []
        
        cargar_dashboard()

    def cargar_pantalla_residencia():
        """
        Carga la pantalla de validación de residencia.
        
        Pregunta al usuario si reside en Ensenada, B.C. para filtrar
        los trámites disponibles.
        """
        page.clean()
        page.add(ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.MAP, size=60, color=ft.Colors.INDIGO),
                ft.Text("Validación de Residencia", size=24, weight="bold"),
                ft.Text(
                    "¿Vives actualmente en Ensenada, B.C.?", 
                    color=ft.Colors.GREY_600
                ),
                ft.Container(height=20),
                ft.Row([
                    ft.ElevatedButton(
                        "Sí, soy residente", 
                        on_click=lambda _: ir_a_dashboard(True)
                    ),
                    ft.OutlinedButton(
                        "No, soy foráneo", 
                        on_click=lambda _: ir_a_dashboard(False)
                    )
                ], alignment=ft.MainAxisAlignment.CENTER)
            ], 
            alignment=ft.MainAxisAlignment.CENTER, 
            horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.alignment.center, 
            expand=True, 
            bgcolor=ft.Colors.INDIGO_50
        ))

    def validar_edad(es_mayor):
        """
        Valida si el usuario es mayor de edad.
        
        Si es mayor, continúa al flujo normal. Si es menor, muestra
        pantalla de acceso restringido.
        
        Args:
            es_mayor (bool): True si el usuario es mayor de 18 años
        """
        if es_mayor:
            cargar_pantalla_residencia()
        else:
            page.clean()
            page.add(ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.BLOCK, size=100, color=ft.Colors.RED),
                    ft.Text(
                        "Acceso Restringido", 
                        size=40, 
                        weight="bold", 
                        color=ft.Colors.RED
                    ),
                    ft.Text(
                        "Este sistema requiere que seas mayor de 18 años.", 
                        size=20
                    ),
                ], 
                alignment=ft.MainAxisAlignment.CENTER, 
                horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                alignment=ft.alignment.center,
                expand=True
            ))

    def cargar_pantalla_edad():
        """
        Carga la pantalla inicial de verificación de edad.
        
        Primera pantalla que ve el usuario al iniciar la aplicación.
        """
        page.clean()
        page.add(ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.VERIFIED_USER, size=60, color=ft.Colors.INDIGO),
                ft.Text("Bienvenido", size=30, weight="bold"),
                ft.Text("Verificación de mayoría de edad", size=16),
                ft.Container(height=20),
                ft.Row([
                    ft.OutlinedButton(
                        "Soy menor", 
                        on_click=lambda _: validar_edad(False)
                    ),
                    ft.ElevatedButton(
                        "Soy mayor de 18", 
                        on_click=lambda _: validar_edad(True)
                    )
                ], alignment=ft.MainAxisAlignment.CENTER)
            ], 
            alignment=ft.MainAxisAlignment.CENTER, 
            horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.alignment.center, 
            expand=True
        ))

    # ========================================================================
    # INICIO DE LA APLICACIÓN
    # ========================================================================
    # Carga la primera pantalla (verificación de edad)
    cargar_pantalla_edad()


# ============================================================================
# PUNTO DE ENTRADA
# ============================================================================
# Ejecuta la aplicación Flet con la función main como target
ft.app(target=main)