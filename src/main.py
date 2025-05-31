import flet as ft
import requests

API_URL = "https://api-refaccionaria-production-d753.up.railway.app/producto/"

def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.RED)
    page.title = "Consulta de Producto"
    page.padding = 10

    

    logo = ft.Image(
    src="https://i.ibb.co/8LxBQKh2/images.png", 
    width=60,
    height=60,
    fit=ft.ImageFit.CONTAIN
    )

    titulo_empresa = ft.Text(
        "DANIELA CAMPOS",
        size=26,
        weight=ft.FontWeight.BOLD,
        color=ft.colors.WHITE
    )
    titulo = ft.Text("Buscar Producto por Código", size=28, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE)
    codigo_input = ft.TextField(label="Código del producto", width=1000, color=ft.colors.WHITE, border_color=ft.colors.WHITE, cursor_color=ft.colors.WHITE)
    nombre_input = ft.TextField(label="Nombre del producto", width=400)

    encabezado = ft.Container(
        content=ft.Column([
            ft.Row([
                logo,
                titulo_empresa
            ]),
            titulo,
            codigo_input
        ]),
        padding=20,
        bgcolor="#e9423a",
        border_radius=ft.BorderRadius(top_left=0, top_right=0, bottom_left= 20, bottom_right= 20),  # Esquinas inferiores redondeadas
    )
    resultado_card = ft.Container(
        ft.Row([
            ft.Image(
            src="https://i.ibb.co/8LxBQKh2/images.png", 
            width=250,
            height=250,
            fit=ft.ImageFit.CONTAIN
            )
        ], alignment=ft.MainAxisAlignment.CENTER))

    def formatear_fecha(fecha_str):
        if not fecha_str or len(fecha_str) != 6:
            return "Fecha no válida"
        try:
            anio = int(fecha_str[:2])
            mes = int(fecha_str[2:4])
            dia = int(fecha_str[4:])
            anio += 2000
            return f"{dia:02d}/{mes:02d}/{anio}"
        except:
            return "Fecha inválida"


    def buscar_producto(codigo):
        
        if not codigo:
            resultado_card.content = ft.Text("⚠️ Por favor, introduce un código válido.", size=16)
            page.update()
            return

        try:
            res = requests.get(API_URL + codigo)
            if res.status_code == 200:
                data = res.json()
                resultado_card.content = ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text(f"🛠 Nombre: {data['nombre']}", size=20, weight=ft.FontWeight.BOLD),
                            ft.Text(f"🔢 Código: {data['codigo']}"),
                            ft.Text(f"📚 Grupo: {data['grupo']}"),
                            ft.Text(f"🔼 Máximo: {data['maximo']}"),
                            ft.Text(f"🔽 Mínimo: {data['minimo']}"),
                            ft.Text(f"💲 Precio: ${data['precio']:.2f}"),
                            ft.Text(f"📦 Existencia: {data['existencia']}"),
                            ft.Text(f"🧾 Último costo: ${data['ultimo_costo']:.2f}"),
                            ft.Text(f"📅 Última venta: {formatear_fecha(data['ultima_venta'])}"),
                            ft.Text(f"📅 Última compra: {formatear_fecha(data['ultima_compra'])}"),
                            ft.Text(f"🏭 Proveedor: {data['proveedor']}"),
                        ]),
                        padding=20,
                    ),
                    elevation=4,
                )
            else:
                resultado_card.content = ft.Text("❌ Producto no encontrado.", size=16)
                confirmacion = ft.AlertDialog(title=ft.Text("Código no encontrado"), 
                                              content=ft.Column([
                                                  ft.Text("¿Desea buscar por nombre?"),
                                                  ft.Row([
                                                    ft.ElevatedButton("Si", width=150, height=40, on_click= lambda e: buscar_por_nombre(codigo, confirmacion)),
                                                    ft.ElevatedButton("No", width=150, height=40, on_click= lambda e: page.close(confirmacion))
                                                ], alignment=ft.MainAxisAlignment.CENTER)  
                                              ], height=80),
                                              )
                page.open(confirmacion)

        except Exception as ex:
            resultado_card.content = ft.Text(f"🚫 Error al conectar con la API: {str(ex)}", size=16)

        page.update()
    

    def copiar_al_portapapeles(codigo):
        page.set_clipboard(codigo)
        snack_bar = ft.SnackBar(
        content=ft.Text("✅ Código copiado al portapapeles."),
        bgcolor=ft.colors.GREEN
        )
        page.open(snack_bar)
        page.update()

    def buscar_por_nombre_inmediato(nombre):
        if not nombre.strip():
            resultado_card.content = ft.Text("⚠️ Por favor, introduce un nombre válido.", size=16)
            return

        try:
            res = requests.get(API_URL + f"nombre/{nombre}")
            if res.status_code == 200:
                data = res.json()

                if isinstance(data, dict):
                    data = [data]

                columnas = []
                for producto in data:
                    columnas.append(
                        ft.Container(
                            content=ft.Column([
                                ft.Text(f"🛠 Nombre: {producto['nombre']}", size=18, weight=ft.FontWeight.BOLD),
                                ft.Text(f"🔢 Código: {producto['codigo']}"),
                                
                                ft.ElevatedButton(
                                    "Seleccionar producto",
                                    icon=ft.icons.SELECT_ALL,
                                    icon_color=ft.colors.WHITE,
                                    width=400,
                                    height=40,
                                    bgcolor=ft.colors.GREEN,
                                    color=ft.colors.WHITE,
                                    on_click=lambda e, c=producto['codigo']: buscar_producto(c)
                                )
                            ]),
                            padding=10,
                            margin=5,
                            bgcolor=ft.colors.GREY_200,
                            border_radius=10
                        )
                    )

                resultado_card.content = ft.Column(columnas, scroll=ft.ScrollMode.AUTO)
            else:
                resultado_card.content = ft.Text("❌ Producto no encontrado por nombre.", size=16)
        except Exception as ex:
            resultado_card.content = ft.Text(f"🚫 Error al conectar con la API: {str(ex)}", size=16)

        page.update()

    def buscar_por_nombre(nombre, dialog):
        if not nombre.strip():
            resultado_card.content = ft.Text("⚠️ Por favor, introduce un nombre válido.", size=16)
            cerrar_dialogo(dialog)
            page.update()
            return

        try:
            res = requests.get(API_URL + f"nombre/{nombre}")
            if res.status_code == 200:
                data = res.json()

                if isinstance(data, dict):
                    data = [data]

                columnas = []
                for producto in data:
                    columnas.append(
                        ft.Container(
                            content=ft.Column([
                                ft.Text(f"🛠 Nombre: {producto['nombre']}", size=18, weight=ft.FontWeight.BOLD),
                                ft.Text(f"🔢 Código: {producto['codigo']}"),
                                ft.ElevatedButton(
                                    "Seleccionar producto",
                                    icon=ft.icons.SELECT_ALL,
                                    icon_color=ft.colors.WHITE,
                                    width=400,
                                    height=40,
                                    bgcolor=ft.colors.GREEN,
                                    color=ft.colors.WHITE,
                                    on_click=lambda e, c=producto['codigo']: buscar_producto(c)
                                )
                            ]),
                            padding=10,
                            margin=5,
                            bgcolor=ft.colors.GREY_200,
                            border_radius=10
                        )
                    )

                resultado_card.content = ft.Column(columnas, scroll=ft.ScrollMode.AUTO)
            else:
                resultado_card.content = ft.Text("❌ Producto no encontrado por nombre.", size=16)
        except Exception as ex:
            resultado_card.content = ft.Text(f"🚫 Error al conectar con la API: {str(ex)}", size=16)

        page.close(dialog)
        nombre_input.value = ""
        cerrar_dialogo(dialog)
        page.update()


    def abrir_dialogo(e):
        page.open(dialogo_busqueda)
        page.update()

    def cerrar_dialogo(dialog):
        page.close(dialog)
        page.update()

    botones = ft.Row([
        ft.ElevatedButton("Buscar", on_click=lambda e: buscar_producto(codigo_input.value.strip()), width=180, height=40, icon=ft.icons.SEARCH),
        ft.ElevatedButton("Buscar por nombre", on_click=lambda e: buscar_por_nombre_inmediato(codigo_input.value), width=180, height=40, icon=ft.icons.SEARCH)
    ], alignment=ft.MainAxisAlignment.CENTER)
    dialogo_busqueda = ft.AlertDialog(
        modal=True,
        title=ft.Text("Buscar por nombre"),
        content=ft.Column([
            nombre_input,
            ft.ElevatedButton("Buscar", width=500, height=40, on_click=lambda e: buscar_por_nombre(nombre_input.value, dialogo_busqueda), icon=ft.icons.SEARCH)
        ], tight=True),
        actions=[ft.TextButton("Cerrar", on_click=lambda e: cerrar_dialogo(dialogo_busqueda))],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.add(
        ft.Column([
            encabezado,
            botones,
            ft.Column([
                resultado_card
            ], scroll=ft.ScrollMode.AUTO, height=400)
        ], spacing=20)
    )

ft.app(target=main)
