# NO SE SI DEBIA LLEVAR INTERFAZ
import flet as ft
import ast  # Para convertir de forma segura un string a tupla
import io   # Para capturar la salida de print
import contextlib # Para redirigir la salida

# Importamos todo de sld_practice y knowledge_base
import sld_practice
import knowledge_base

def main(page: ft.Page):
    page.title = "Motor de Inferencia SLD"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.window_width = 700
    page.window_height = 600
    page.padding = 20

    # 1. El campo de texto para la consulta
    txt_query = ft.TextField(
        label="Consulta",
        hint_text="Escribe tu consulta como una tupla, ej: ('debe_pagar', 'ana', 'reposicion', 'Costo')",
        autofocus=True,
    )

    # 2. El área de texto para mostrar los resultados
    txt_output = ft.TextField(
        label="Resultado",
        multiline=True,
        read_only=True,
        min_lines=15,
        max_lines=15,
        # Eliminamos 'font_family' para evitar el error de versión
    )

    # 3. La función que se ejecuta al presionar el botón
    def handle_solve(e):
        query_string = txt_query.value
        txt_output.value = "" # Limpiamos salida anterior
        
        if not query_string:
            txt_output.value = "Error: Por favor, introduce una consulta."
            page.update()
            return
            
        try:
            # ast.literal_eval es la forma SEGURA de convertir "('a', 'b')" en ('a', 'b')
            query_tuple = ast.literal_eval(query_string)

            if not isinstance(query_tuple, tuple):
                 raise TypeError("La entrada no es una tupla.")

            # --- ¡AQUÍ OCURRE LA MAGIA! ---
            # 1. Creamos un "archivo" falso en la memoria
            f = io.StringIO()
            
            # 2. Redirigimos TODOS los 'print' a ese archivo falso jijiji
            with contextlib.redirect_stdout(f):
                # 3. Ejecutamos tu función original (la que usa 'print')
                kb = knowledge_base.LICENCIAS
                sld_practice.sld_solve(kb, query_tuple)
            
            # 4. Obtenemos todo lo que se "imprimió" en el archivo falso
            resultado_string = f.getvalue()
            
            # 5. Mostramos el resultado en el campo de texto
            txt_output.value = resultado_string

        except Exception as ex:
            # Capturamos cualquier error (ej. tupla mal escrita)
            txt_output.value = (
                f"Error al procesar la consulta:\n{ex}\n\n"
                "Asegúrate de que la tupla esté bien escrita, "
                "con comillas en los strings.\n"
                "Ej: ('es_ciudadano', 'ana')"
            )
        
        # Actualizamos la página para que se vean los cambios
        page.update()

    # 4. El botón para correrlo
    btn_solve = ft.Button(
        text="Resolver Consulta",
        icon=ft.Icons.PLAY_ARROW,
        on_click=handle_solve,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10))
    )
    
    # 5. Añadimos todos los controles a la página
    page.add(
        ft.Column(
            [
                ft.Text("Motor de Resolución SLD", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                txt_query,
                btn_solve,
                txt_output
            ],
            spacing=15
        )
    )
    
    # Permite que el botón se active al presionar Enter en el campo de texto
    txt_query.on_submit = handle_solve

# --- Ejecución Principal ---
if __name__ == "__main__":
    ft.app(target=main)