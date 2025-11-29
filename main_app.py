"""
nota: modificar lo de ensenada en los que son foraneos

NO LE MUEVAN A ESTE CODIGO PIBES
                       uuuuuuuuuuuuuuuuuuuuu.
                   .u$$$$$$$$$$$$$$$$$$$$$$$$$$W.
                 u$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$Wu.
               $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$i
         `    $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
          .$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
         .$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
         #$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
         W$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
$u       #$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$~
$#      `"$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
$i        $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
$$        #$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
$$         $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#$.        $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$#
 $$      $iW$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$!
 $$i      $$$$$$$#"" `"'"#$$$$$$$$$$$$$$$$$#"'"'""#$$$$$$$$$$$$$$$W
 #$$W    `$$$#"            "       !$$$$$`           `"#$$$$$$$$$$#
  $$$     `""                 ! !iuW$$$$$                 #$$$$$$$#
  #$$    $u                  $   $$$$$$$                  $$$$$$$~
   "#    #$$i.               #   $$$$$$$.                 `$$$$$$
          $$$$$i.                "'"#$$$$i.               .$$$$#
          $$$$$$$$!         .   `    $$$$$$$$$i           $$$$$
          `$$$$$  $iWW   .uW`        #$$$$$$$$$W.       .$$$$$$#
            "#$$$$$$$$$$$$#`          $$$$$$$$$$$iWiuuuW$$$$$$$$W
               !#""    ""             `$$$$$$$##$$$$$$$$$$$$$$$$
          i$$$$    .                   !$$$$$$ .$$$$$$$$$$$$$$$#
         $$$$$$$$$$`                    $$$$$$$$$Wi$$$$$$#"#$$`
         #$$$$$$$$$W.                   $$$$$$$$$$$#'  ``
          `$$$$##$$$$!       i$u.  $. .i$$$$$$$$$#"/
             "     `#W       $$$$$$$$$$$$$$$$$$$`      u$#
                            W$$$$$$$$$$$$$$$$$$      $$$$W
                            $$`!$$$##$$$$``$$$$      $$$$!
                           i$" $$$$  $$#"`  ""'     W$$$$
                                                   W$$$$!
                      uW$$  uu  uu.  $$$  $$$Wu#   $$$$$$
                     ~$$$$iu$$iu$$$uW$$! $$$$$$i .W$$$$$$
             ..  !   "#$$$$$$$$$$##$$$$$$$$$$$$$$$$$$$$#"
             $$W  $     "#$$$$$$$iW$$$$$$$$$$$$$$$$$$$$$W
             $#`   `       ""#$$$$$$$$$$$$$$$$$$$$$$$$$$$
                              !$$$$$$$$$$$$$$$$$$$$$#`
                              $$$$$$$$$$$$$$$$$$$$$$!
                            $$$$$$$$$$$$$$$$$$$$$$$`
                             $$$$$$$$$$$$$$$$$$$$

"""
import flet as ft
import io
import contextlib
import sys

# --- IMPORTS REALES ---
try:
    import motor_inferencia as motor
    import knowledge_base as kb
except ImportError:
    print("ERROR CRÍTICO: No se encontraron los archivos 'motor_inferencia.py' o 'knowledge_base.py'.")
    sys.exit(1)

# --- CONFIGURACIÓN BASE ---
KB_BASE = kb.KB_LEGALMENTE.copy()
HECHOS_SESION = []

TRAMITES_RESIDENTES = [
    'acta_nacimiento', 'expedicion_licencia', 'revalidacion_licencia',
    'refrendo_tarjeta_circulacion', 'constancia_antecedentes_penales',
    'reposicion_licencia', 'alta_vehiculo', 'baja_vehiculo',
    'cambio_propietario_vehiculo', 'reposicion_tarjeta_circulacion',
    'reposicion_placas_circulacion', 'permiso_traslado_vehicular',
    'acta_matrimonio', 'acta_defuncion', 'pasaporte'
]

TRAMITES_NO_RESIDENTES = [
    'acta_nacimiento', 
    'constancia_antecedentes_penales', 
    'acta_defuncion', 
    'pasaporte'
]

# --- LÓGICA DE PROCESAMIENTO (BACKEND) ---

def limpiar_respuesta_motor(texto_crudo):
    lineas = texto_crudo.split('\n')
    lineas_limpias = []
    palabras_prohibidas = ["Iniciando", "Solución", "Derivación", "derivación", "paso a paso", "-----", "Sustituciones", "Query:", "Resultado:", "Unifica", "Aplica", "HECHO:", "REGLA:"]

    for l in lineas:
        l = l.strip()
        if not l: continue
        if any(x in l for x in palabras_prohibidas): continue
        if "=" in l:
            partes = l.split("=")
            if len(partes) > 1: l = partes[1].strip()
        l = l.replace("_", " ").capitalize()
        if lineas_limpias and lineas_limpias[-1] == l: continue
        lineas_limpias.append(l)

    return "\n".join(lineas_limpias) if lineas_limpias else "N/A"

def procesar_costos_inteligente(texto_crudo):
    lineas = texto_crudo.split('\n')
    items_formateados = []
    temp_desc = None
    temp_monto = None
    
    for l in lineas:
        l = l.strip()
        if not l: continue
        if "Descripcion =" in l:
            temp_desc = l.split("=")[1].strip().replace("_", " ").capitalize()
        elif "Monto =" in l:
            temp_monto = l.split("=")[1].strip()
        if temp_desc and temp_monto:
            items_formateados.append(f"{temp_desc}: ${temp_monto} MXN")
            temp_desc = None
            temp_monto = None
            
    if not items_formateados:
        return [limpiar_respuesta_motor(texto_crudo)]
    return items_formateados

def consultar_motor_real(tramite, predicado, variable_buscada='Dato'):
    kb_actual = KB_BASE.copy()
    kb_actual['hechos'] = KB_BASE['hechos'] + HECHOS_SESION
    
    if predicado == 'costo': query = ('costo', tramite, 'Descripcion', 'Monto')
    elif predicado == 'requiere': query = ('requiere', tramite, 'Requisito')
    else: query = (predicado, tramite, variable_buscada)

    f = io.StringIO()
    try:
        with contextlib.redirect_stdout(f): motor.sld_solve(kb_actual, query)
        raw = f.getvalue()
    except: raw = ""
    return raw

# --- COMPONENTES UI ---

def crear_tarjeta_info(titulo, valor, icono, color_icono):
    return ft.Container(
        content=ft.Column([
            ft.Icon(icono, color=color_icono, size=28),
            ft.Text(titulo, size=10, color=ft.Colors.GREY_600, weight="bold"),
            ft.Text(valor, size=12, weight="w600", color=ft.Colors.BLACK87, text_align=ft.TextAlign.CENTER)
        ], spacing=5, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        padding=10,
        bgcolor=ft.Colors.WHITE,
        border_radius=12,
        border=ft.border.all(1, ft.Colors.GREY_200),
        width=140,
        height=120,
        alignment=ft.alignment.center,
        shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.GREY_100)
    )

# --- APP PRINCIPAL ---

def main(page: ft.Page):
    page.title = "LegalMente - Sistema Experto"
    page.window_width = 1100
    page.window_height = 800
    page.theme_mode = "light"
    page.padding = 0
    try: page.theme = ft.Theme(color_scheme_seed=ft.Colors.INDIGO)
    except: pass

    state = {"es_residente": False, "tramite_seleccionado": None}

    # --- PANEL DERECHO (DASHBOARD) ---
    lbl_titulo_tramite = ft.Text("Selecciona un trámite", size=24, weight="bold", color=ft.Colors.INDIGO, text_align=ft.TextAlign.CENTER)
    
    card_dependencia = crear_tarjeta_info("DEPENDENCIA", "-", ft.Icons.ACCOUNT_BALANCE, ft.Colors.BLUE)
    card_vigencia = crear_tarjeta_info("VIGENCIA", "-", ft.Icons.TIMER, ft.Colors.ORANGE)
    card_modalidad = crear_tarjeta_info("MODALIDAD", "-", ft.Icons.LAPTOP_MAC, ft.Colors.PURPLE)
    
    row_resumen = ft.Row(
        [card_dependencia, card_vigencia, card_modalidad], 
        spacing=20, visible=False, alignment=ft.MainAxisAlignment.CENTER
    )

    contenedor_detalles = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    
    panel_derecho = ft.Container(
        content=ft.Column([
            ft.Container(height=10),
            lbl_titulo_tramite,
            ft.Divider(color=ft.Colors.TRANSPARENT, height=15),
            row_resumen,
            ft.Divider(),
            ft.Text("Información Detallada", size=12, weight="bold", color=ft.Colors.GREY_400),
            ft.Container(
                content=contenedor_detalles,
                padding=20,
                bgcolor=ft.Colors.GREY_50,
                border_radius=10,
                expand=True,
                alignment=ft.alignment.top_center
            )
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        padding=30, expand=True, bgcolor=ft.Colors.WHITE
    )

    grid_tramites = ft.GridView(expand=True, runs_count=1, max_extent=300, child_aspect_ratio=4.0, spacing=10, run_spacing=10)

    # --- FUNCIONES DE CONTROL ---

    def actualizar_panel_central(tramite):
        row_resumen.visible = True
        
        raw_dep = consultar_motor_real(tramite, 'dependencia', 'Lugar')
        raw_vig = consultar_motor_real(tramite, 'vigencia', 'Tiempo')
        raw_mod = consultar_motor_real(tramite, 'modalidad_tramite', 'Modo')

        dep = limpiar_respuesta_motor(raw_dep)
        vig = limpiar_respuesta_motor(raw_vig)
        mod = limpiar_respuesta_motor(raw_mod)

        card_dependencia.content.controls[2].value = dep if dep != "N/A" else "No especif."
        card_vigencia.content.controls[2].value = vig if vig != "N/A" else "Variable"
        card_modalidad.content.controls[2].value = mod if mod != "N/A" else "Híbrido"
        
        contenedor_detalles.controls.clear()
        contenedor_detalles.controls.append(
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.TOUCH_APP, size=40, color=ft.Colors.GREY_300),
                    ft.Text("Consulta Requisitos o Costos abajo", color=ft.Colors.GREY_400)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                alignment=ft.alignment.center, padding=40
            )
        )
        page.update()

    def accion_botones(tipo):
        tramite = state["tramite_seleccionado"]
        if not tramite: return
        
        texto_raw = consultar_motor_real(tramite, tipo)
        contenedor_detalles.controls.clear()
        items_visuales = []
        
        if tipo == 'costo':
            lista_costos = procesar_costos_inteligente(texto_raw)
            for costo in lista_costos:
                items_visuales.append(
                    ft.Container(
                        content=ft.ListTile(
                            leading=ft.Icon(ft.Icons.MONETIZATION_ON, color=ft.Colors.GREEN_700, size=24),
                            title=ft.Text(costo, size=13, weight="bold", color=ft.Colors.BLACK87),
                        ),
                        bgcolor=ft.Colors.GREEN_50,
                        border_radius=10,
                        padding=5,
                        margin=ft.margin.only(bottom=5)
                    )
                )
        else:
            texto_limpio = limpiar_respuesta_motor(texto_raw)
            for l in texto_limpio.split('\n'):
                if l.strip() and l != "N/A":
                    items_visuales.append(
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.INDIGO, size=20),
                            title=ft.Text(l, size=13, weight="w500"),
                            dense=True,
                        )
                    )
        
        if not items_visuales: 
            items_visuales.append(ft.Text("Información no disponible.", color=ft.Colors.RED_400))
        
        contenedor_detalles.controls.append(ft.Column(items_visuales))
        page.update()

    btn_req = ft.ElevatedButton("Ver Requisitos", icon=ft.Icons.LIST_ALT, on_click=lambda _: accion_botones('requiere'), disabled=True)
    btn_cost = ft.ElevatedButton("Ver Costos", icon=ft.Icons.ATTACH_MONEY, on_click=lambda _: accion_botones('costo'), disabled=True)

    def seleccionar_tramite(e):
        nombre = e.control.data
        state["tramite_seleccionado"] = nombre
        for c in grid_tramites.controls:
            c.bgcolor = ft.Colors.WHITE
            c.border = None
            if c.data == nombre:
                c.bgcolor = ft.Colors.INDIGO_50
                c.border = ft.border.all(2, ft.Colors.INDIGO)
        
        lbl_titulo_tramite.value = nombre.replace("_", " ").upper()
        btn_req.disabled = False
        btn_cost.disabled = False
        actualizar_panel_central(nombre)

    # --- PANTALLAS (VISTAS) ---

    def cargar_dashboard():
        page.clean()
        lista = TRAMITES_RESIDENTES if state["es_residente"] else TRAMITES_NO_RESIDENTES
        grid_tramites.controls.clear()
        for t in lista:
            grid_tramites.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.DESCRIPTION, color=ft.Colors.INDIGO_300, size=20),
                        ft.Text(t.replace("_", " ").title(), size=12, weight="bold", expand=True)
                    ]),
                    data=t, on_click=seleccionar_tramite,
                    bgcolor=ft.Colors.WHITE, padding=12, border_radius=8, ink=True,
                    shadow=ft.BoxShadow(blur_radius=2, color=ft.Colors.GREY_200)
                )
            )

        layout = ft.Row([
            ft.Container(
                content=ft.Column([
                    ft.Container(content=ft.Row([ft.Icon(ft.Icons.GAVEL, color=ft.Colors.WHITE), ft.Text("LegalMente", color=ft.Colors.WHITE, weight="bold", size=18)]), bgcolor=ft.Colors.INDIGO, padding=20, border_radius=10),
                    ft.Divider(),
                    grid_tramites
                ]),
                width=300, bgcolor=ft.Colors.GREY_100, padding=15
            ),
            ft.Container(
                content=ft.Column([
                    panel_derecho,
                    ft.Container(content=ft.Row([btn_req, btn_cost], alignment=ft.MainAxisAlignment.CENTER), padding=20, bgcolor=ft.Colors.WHITE)
                ]),
                expand=True
            )
        ], expand=True, spacing=0)
        page.add(layout)

    def ir_a_dashboard(residente):
        state["es_residente"] = residente
        global HECHOS_SESION
        HECHOS_SESION = [('reside_en_ensenada', 'usuario_actual')] if residente else []
        cargar_dashboard()

    def cargar_pantalla_residencia():
        page.clean()
        page.add(ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.MAP, size=60, color=ft.Colors.INDIGO),
                ft.Text("Validación de Residencia", size=24, weight="bold"),
                ft.Text("¿Vives actualmente en Ensenada, B.C.?", color=ft.Colors.GREY_600),
                ft.Container(height=20),
                ft.Row([
                    ft.ElevatedButton("Sí, soy residente", on_click=lambda _: ir_a_dashboard(True)),
                    ft.OutlinedButton("No, soy foráneo", on_click=lambda _: ir_a_dashboard(False))
                ], alignment=ft.MainAxisAlignment.CENTER)
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.alignment.center, expand=True, bgcolor=ft.Colors.INDIGO_50
        ))

    # Lógica de validación de edad antigua y segura (yo digo)
    def validar_edad(es_mayor):
        if es_mayor:
            cargar_pantalla_residencia()
        else:
            # En lugar de cerrar la ventana, mostramos la pantalla de bloqueo
            page.clean()
            page.add(ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.BLOCK, size=100, color=ft.Colors.RED),
                    ft.Text("Acceso Restringido", size=40, weight="bold", color=ft.Colors.RED),
                    ft.Text("Este sistema requiere que seas mayor de 18 años.", size=20),
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                alignment=ft.alignment.center,
                expand=True
            ))

    def cargar_pantalla_edad():
        page.clean()
        page.add(ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.VERIFIED_USER, size=60, color=ft.Colors.INDIGO),
                ft.Text("Bienvenido", size=30, weight="bold"),
                ft.Text("Verificación de mayoría de edad", size=16),
                ft.Container(height=20),
                ft.Row([
                    # Llamamos a validar_edad(False) en lugar de intentar cerrar la ventana
                    ft.OutlinedButton("Soy menor", on_click=lambda _: validar_edad(False)),
                    ft.ElevatedButton("Soy mayor de 18", on_click=lambda _: validar_edad(True))
                ], alignment=ft.MainAxisAlignment.CENTER)
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.alignment.center, expand=True
        ))

    cargar_pantalla_edad()

ft.app(target=main)