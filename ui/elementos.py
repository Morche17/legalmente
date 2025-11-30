import flet as ft

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