import os
from datetime import date, datetime
from util.jsonfileHandler import readFile, saveFile
from util.menu import main_menu, clear_console, pause
from util.listas import (
    CATEGORIES,
    next_id,
    gastos_por_categoria,
    total_gastos,
    filter_by_category,
    parse_date,
    filter_by_date_range,
    gastos_diarios,
    gastos_ultimo_dias,
    gastos_mes,
    pretty_gasto,
)
#===Definicion De Funciones===#
DB_FILE = os.path.join("database", "gastos.json")

def ensure_db_exists():
    if not os.path.exists(os.path.dirname(DB_FILE)):
        os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    if not os.path.exists(DB_FILE):
        saveFile(DB_FILE, [])

def mostrar_categorias():
    print("Categorías disponibles:")
    for i, c in enumerate(CATEGORIES, start=1):
        print(f"{i}. {c}")

def registrar_gasto(gastos):
    print("Registrar nuevo gasto ---")
    try:
        monto = float(input("Monto (solo números) > ") or 0)
    except ValueError:
        print("Monto inválido.")
        return
#===Seleccionar categoria===#
    mostrar_categorias()
    try:
        cat_idx = int(input("Seleccione número de categoría > ") or 0)
    except ValueError:
        cat_idx = 0

    if 1 <= cat_idx <= len(CATEGORIES):
        categoria = CATEGORIES[cat_idx-1]
    else:
        categoria = "Otros"

    descripcion = input("Descripción (opcional) > ").strip()
#===Fecha del gasto===#
    fecha_in = input(f"Fecha (enter = hoy {date.today().isoformat()}) [YYYY-MM-DD o DD/MM/YYYY] > ").strip()
    if fecha_in == "":
        fecha = date.today().isoformat()
    else:
        d = parse_date(fecha_in)
        if not d:
            print("Formato de fecha inválido. Se toma la fecha de hoy.")
            fecha = date.today().isoformat()
        else:
            fecha = d.isoformat()

    nuevo = {
        "id": next_id(gastos),
        "monto": monto,
        "categoria": categoria,
        "descripcion": descripcion,
        "fecha": fecha
    }
    gastos.append(nuevo)
    saved = saveFile(DB_FILE, gastos)
    if saved:
        print("Gasto registrado correctamente.")
    else:
        print("Hubo un error guardando el gasto.")

def listar_todos(gastos):
    print("=== LISTA DE GASTOS ===")
    if not gastos:
        print("No hay gastos registrados.")
        return
    for g in gastos:
        print(pretty_gasto(g))
    print(f"Total: {total_gastos(gastos):.2f}")
#===Listar por categoria===#
def listar_por_categoria(gastos):
    mostrar_categorias()
    try:
        cat_idx = int(input("Seleccione número de categoría > ") or 0)
    except ValueError:
        cat_idx = 0
    if 1 <= cat_idx <= len(CATEGORIES):
        categoria = CATEGORIES[cat_idx-1]
    else:
        categoria = input("Escribe la categoría manualmente > ").strip() or "Otros"
    filtrados = filter_by_category(gastos, categoria)
    print(f"Gastos en categoría: {categoria} (total {len(filtrados)})")
    if not filtrados:
        print("No hay registros.")
        return
    for g in filtrados:
        print(pretty_gasto(g))
    print(f"Subtotal {categoria}: {total_gastos(filtrados):.2f}")
#===Mostrar totales===#
def mostrar_totales(gastos):
    print("=== TOTALES ===")
    total = total_gastos(gastos)
    por_cat = gastos_por_categoria(gastos)
    print(f"Total general: {total:.2f}")
    print("Totales por categoría:")
    for cat, s in por_cat.items():
        print(f"  {cat:<15}: {s:.2f}")
#===Reportes===#
def reportes(gastos):
    print("=== REPORTES ===")
    print("1. Reporte diario (hoy)")
    print("2. Reporte semanal (últimos 7 días)")
    print("3. Reporte mensual (mes actual)")
    try:
        opt = int(input("Seleccione > ") or 0)
    except ValueError:
        opt = 0
#===Generar el reporte===#
    if opt == 1:
        t = date.today()
        items = gastos_diarios(gastos, t)
        title = f"Reporte diario {t.isoformat()}"
    elif opt == 2:
        items = gastos_ultimo_dias(gastos, 7)
        title = "Reporte últimos 7 días"
    elif opt == 3:
        today = date.today()
        items = gastos_mes(gastos, today.year, today.month)
        title = f"Reporte mes {today.year}-{today.month:02d}"
    else:
        print("Opción inválida.")
        return

    print(f"{title}")
    if not items:
        print("No hay gastos en este periodo.")
        return
    for g in items:
        print(pretty_gasto(g))
    print(f"Total periodo: {total_gastos(items):.2f}")
#===Guardar reporte JSON===#
def guardar_reporte_json(gastos):
    print("=== GUARDAR REPORTE A JSON ===")
    print("Puedes generar el mismo tipo de reportes.")
    print("1. Diario  2. Semanal  3. Mensual")
    try:
        opt = int(input("Seleccione > ") or 0)
    except ValueError:
        opt = 0
    if opt not in (1,2,3):
        print("Opción inválida.")
        return
#===Generar el reporte===#
    if opt == 1:
        items = gastos_diarios(gastos, date.today())
        name = f"reporte_diario_{date.today().isoformat()}.json"
    elif opt == 2:
        items = gastos_ultimo_dias(gastos, 7)
        name = f"reporte_semanal_{date.today().isoformat()}.json"
    else:
        t = date.today()
        items = gastos_mes(gastos, t.year, t.month)
        name = f"reporte_mensual_{t.year}_{t.month:02d}.json"
#===Guardar el archivo===#
    out_folder = "reports"
    if not os.path.exists(out_folder):
        os.makedirs(out_folder, exist_ok=True)
    out_path = os.path.join(out_folder, name)
    success = saveFile(out_path, items)
    if success:
        print(f"Reporte guardado en {out_path} (elementos: {len(items)})")
    else:
        print("Error guardando el reporte.")
#===Bucle Principal===#
def main():
    ensure_db_exists()
    gastos = readFile(DB_FILE) or []

    while True:
        clear_console()
        choice = main_menu()
        if choice == 1:
            registrar_gasto(gastos)
            pause()
        elif choice == 2:
            listar_todos(gastos)
            pause()
        elif choice == 3:
            listar_por_categoria(gastos)
            pause()
        elif choice == 4:
            mostrar_totales(gastos)
            pause()
        elif choice == 5:
            reportes(gastos)
            pause()
        elif choice == 6:
            guardar_reporte_json(gastos)
            pause()
        elif choice == 7:
            print("Bye!!!")
            break
        else:
            print("Opción inválida. Intenta otra vez.")
            pause()

if __name__ == "__main__":
    main()

#===Edwin Ocampo===#