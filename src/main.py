import flet as ft
import pymysql
from pymysql.cursors import DictCursor
from datetime import datetime
import pandas as pd

# === CONFIGURACIÓN REMOTA MySQL ===
MYSQL_CONFIG = {
    "host": "crossover.proxy.rlwy.net",
    "port": 54170,
    "user": "root",
    "password": "iSkNWzuVyHqHDLscFCyEMGDvvNxRzCBv",
    "database": "railway",
    "connect_timeout": 30,
    "cursorclass": DictCursor
}

def resumen_y_detalle(desde, hasta):
    try:
        conexion = pymysql.connect(**MYSQL_CONFIG)
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT 
                vt_folio, vt_fechat, vt_totalg, vt_impuesto, vt_sub_total,
                vt_efectivo, vt_tarjeta, vt_credito, vt_abono
            FROM VEARMA01
            WHERE vt_bandera != '1' AND vt_fechat BETWEEN %s AND %s
        """, (desde, hasta))
        datos = cursor.fetchall()
        conexion.close()

        df = pd.DataFrame(datos)
        if df.empty:
            return {}, pd.DataFrame()

        df["credito_real"] = df["vt_credito"] - df["vt_abono"]

        resumen = {
            "efectivo": df["vt_efectivo"].sum(),
            "tarjeta": df["vt_tarjeta"].sum(),
            "credito": df["credito_real"].sum(),
            "total_con_iva": df["vt_totalg"].sum(),
            "total_sin_iva": df["vt_sub_total"].sum(),
            "iva": df["vt_impuesto"].sum()
        }

        return resumen, df
    except Exception as e:
        print("❌ Error resumen:", e)
        return None, None

def main(page: ft.Page):
    page.title = "Resumen de Ventas"
    page.window_width = 640
    page.window_height = 640

    hoy = datetime.now()
    hoy_fmt_db = hoy.strftime("%y%m%d")
    hoy_fmt_txt = hoy.strftime("%d-%m-%Y")

    fecha_desde = ft.TextField(label="Desde", value=hoy_fmt_txt, width=150)
    fecha_hasta = ft.TextField(label="Hasta", value=hoy_fmt_txt, width=150)
    resultado_txt = ft.Text("", size=12)

    tabla_detalle = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Documento")),
            ft.DataColumn(ft.Text("Fecha")),
            ft.DataColumn(ft.Text("Importe")),
            ft.DataColumn(ft.Text("I.V.A")),
            ft.DataColumn(ft.Text("Neto")),
            ft.DataColumn(ft.Text("Efectivo")),
            ft.DataColumn(ft.Text("Tarjeta")),
            ft.DataColumn(ft.Text("Crédito"))
        ],
        rows=[],
        visible=False
    )

    picker_desde = ft.DatePicker(
        on_change=lambda e: setattr(fecha_desde, "value", e.control.value.strftime("%d-%m-%Y"))
    )
    picker_hasta = ft.DatePicker(
        on_change=lambda e: setattr(fecha_hasta, "value", e.control.value.strftime("%d-%m-%Y"))
    )
    page.overlay.extend([picker_desde, picker_hasta])

    def mostrar_resumen(e=None):
        try:
            desde = datetime.strptime(fecha_desde.value, "%d-%m-%Y").strftime("%y%m%d")
            hasta = datetime.strptime(fecha_hasta.value, "%d-%m-%Y").strftime("%y%m%d")
        except:
            resultado_txt.value = "❌ Formato de fecha inválido (dd-mm-aaaa)"
            page.update()
            return

        resumen, df = resumen_y_detalle(desde, hasta)
        if resumen is None:
            resultado_txt.value = "❌ No se pudo obtener el resumen."
            page.update()
            return

        resultado_txt.value = (
            f"🧾 RESUMEN DEL {fecha_desde.value} AL {fecha_hasta.value}\n\n"
            f"Efectivo: ${resumen['efectivo']:,.2f}\n"
            f"Tarjeta:  ${resumen['tarjeta']:,.2f}\n"
            f"Crédito:  ${resumen['credito']:,.2f}\n"
            f"\nTotal sin IVA: ${resumen['total_sin_iva']:,.2f}"
            f"\nIVA: ${resumen['iva']:,.2f}"
            f"\nTotal con IVA: ${resumen['total_con_iva']:,.2f}"
        )

        tabla_detalle.rows.clear()
        for _, row in df.iterrows():
            tabla_detalle.rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(row["vt_folio"]))),
                ft.DataCell(ft.Text(str(row["vt_fechat"]))),
                ft.DataCell(ft.Text(f"${row['vt_totalg']:,.2f}")),
                ft.DataCell(ft.Text(f"${row['vt_impuesto']:,.2f}")),
                ft.DataCell(ft.Text(f"${row['vt_sub_total']:,.2f}")),
                ft.DataCell(ft.Text(f"${row['vt_efectivo']:,.2f}")),
                ft.DataCell(ft.Text(f"${row['vt_tarjeta']:,.2f}")),
                ft.DataCell(ft.Text(f"${row['credito_real']:,.2f}")),
            ]))
        page.update()

    boton = ft.ElevatedButton(
        "🔍 Mostrar Resumen",
        on_click=mostrar_resumen,
        bgcolor=ft.Colors.BLUE,
        color=ft.Colors.WHITE
    )

    page.add(
        ft.Column([
            ft.Text("📊 Resumen de Ventas", size=22, weight=ft.FontWeight.BOLD),
            ft.Row([fecha_desde, ft.IconButton(icon=ft.Icons.CALENDAR_MONTH, on_click=lambda _: picker_desde.pick())]),
            ft.Row([fecha_hasta, ft.IconButton(icon=ft.Icons.CALENDAR_MONTH, on_click=lambda _: picker_hasta.pick())]),
            boton,
            resultado_txt,
            tabla_detalle
        ], spacing=20)
    )

    # Mostrar resumen del día actual automáticamente
    mostrar_resumen()

ft.app(target=main)
