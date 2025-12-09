import os
import re
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
    gastos_diarios,
    gastos_ultimo_dias,
    gastos_mes,
)

# ============================================================
# FUNCIÓN UNIVERSAL PARA MOSTRAR TABLAS
# ============================================================
def imprimir_tabla(gastos):
    if not gastos:
        print("No hay datos para mostrar.")
        return

    headers = ["ID", "MONTO", "CATEGORÍA", "DESCRIPCIÓN", "FECHA"]

    rows = []
    for g in gastos:
        rows.append([
            str(g["id"]),
            f"{g['monto']:.2f}",
            g["categoria"],
            g["descripcion"],
            g["fecha"]
        ])

    col_widths = []
    for i in range(len(headers)):
        max_len = max(len(headers[i]), max(len(row[i]) for row in rows))
        col_widths.append(max_len)

    def format_row(row):
        return "│ " + " │ ".join(row[i].ljust(col_widths[i]) for i in range(len(row))) + " │"

    print("┌" + "┬".join("─" * (col_widths[i] + 2) for i in range(len(headers))) + "┐")
    print(format_row(headers))
    print("├" + "┼".join("─" * (col_widths[i] + 2) for i in range(len(headers))) + "┤")

    for row in rows:
        print(format_row(row))

    print("└" + "┴".join("─" * (col_widths[i] + 2) for i in range(len(headers))) + "┘")

# ============================================================
# BASE DE DATOS
# ============================================================
DB_FILE = os.path.join("database", "gastos.json")

def ensure_db_exists():
    if not os.path.exists(os.path.dirname(DB_FILE)):
        os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    if not os.path.exists(DB_FILE):
        saveFile(DB_FILE, [])

# ============================================================
# MOSTRAR CATEGORÍAS
# ============================================================
def mostrar_categorias():
    print("Categorías disponibles:")
    for i, c in enumerate(CATEGORIES, start=1):
        print(f"{i}. {c}")

# ============================================================
# REGISTRAR GASTO
# ============================================================
def registrar_gasto(gastos):
    print("Registrar nuevo gasto ---")

    # --- Validación de monto ---
    while True:
        try:
            monto = float(input("Monto (solo números, mayor a 0) > ") or 0)
            if monto > 0:
                break
            print("El monto debe ser mayor a 0.")
        except ValueError:
            print("Debe ingresar un número válido.")

    # --- Validación de categoría ---
    while True:
        mostrar_categorias()
        try:
            cat_idx = int(input("Seleccione número de categoría > "))
            if 1 <= cat_idx <= len(CATEGORIES):
                categoria = CATEGORIES[cat_idx - 1]
                break
            print("Selección inválida.")
        except ValueError:
            print("Debe ingresar un número.")

    # --- Validación de descripción (solo texto) ---
    while True:
        descripcion = input("Descripción (solo texto) > ").strip()
        if re.fullmatch(r"[A-Za-zÁÉÍÓÚáéíóúÑñ\s]+", descripcion):
            break
        print("La descripción solo puede contener letras y espacios.")

    # --- Fecha ---
    fecha_in = input(f"Fecha (ENTER = hoy {date.today().isoformat()}) > ").strip()
    if fecha_in == "":
        fecha = date.today().isoformat()
    else:
        d = parse_date(fecha_in)
        fecha = d.isoformat() if d else date.today().isoformat()

    # Crear el gasto
    nuevo = {
        "id": next_id(gastos),
        "monto": monto,
        "categoria": categoria,
        "descripcion": descripcion,
        "fecha": fecha
    }

    gastos.append(nuevo)
    if saveFile(DB_FILE, gastos):
        print("✔ Gasto registrado correctamente.")
    else:
        print("Error al guardar.")

# ============================================================
# LISTAR TODOS
# ============================================================
def listar_todos(gastos):
    print("=== LISTA DE GASTOS ===")
    if not gastos:
        print("No hay gastos registrados.")
        return

    imprimir_tabla(gastos)
    print(f"Total: {total_gastos(gastos):.2f}")

# ============================================================
# LISTAR POR CATEGORÍA
# ============================================================
def listar_por_categoria(gastos):
    mostrar_categorias()
    try:
        cat_idx = int(input("Seleccione número de categoría > "))
    except ValueError:
        cat_idx = 0

    if 1 <= cat_idx <= len(CATEGORIES):
        categoria = CATEGORIES[cat_idx - 1]
    else:
        categoria = input("Escribe la categoría manualmente > ").strip() or "Otros"

    filtrados = filter_by_category(gastos, categoria)

    print(f"Gastos de la categoría '{categoria}'")

    if not filtrados:
        print("No hay registros.")
        return

    imprimir_tabla(filtrados)
    print(f"Subtotal {categoria}: {total_gastos(filtrados):.2f}")

# ============================================================
# MOSTRAR TOTALES
# ============================================================
def mostrar_totales(gastos):
    print("=== TOTALES ===")
    total = total_gastos(gastos)
    por_cat = gastos_por_categoria(gastos)

    print(f"Total general: {total:.2f}")
    print("Totales por categoría:")
    for cat, s in por_cat.items():
        print(f" - {cat}: {s:.2f}")

# ============================================================
# REPORTES
# ============================================================
def reportes(gastos):
    print("=== REPORTES ===")
    print("1. Diario")
    print("2. Semanal")
    print("3. Mensual")

    try:
        opt = int(input("Seleccione > ") or 0)
    except:
        opt = 0

    if opt == 1:
        t = date.today()
        items = gastos_diarios(gastos, t)
        title = f"Reporte diario {t}"
    elif opt == 2:
        items = gastos_ultimo_dias(gastos, 7)
        title = "Reporte semanal"
    elif opt == 3:
        today = date.today()
        items = gastos_mes(gastos, today.year, today.month)
        title = f"Reporte mensual {today.year}-{today.month:02d}"
    else:
        print("Opción inválida.")
        return

    print(title)

    if not items:
        print("No hay registros en este periodo.")
        return

    imprimir_tabla(items)
    print(f"Total periodo: {total_gastos(items):.2f}")

# ============================================================
# GUARDAR REPORTE JSON
# ============================================================
def guardar_reporte_json(gastos):
    print("=== GUARDAR REPORTE A JSON ===")
    print("Puedes generar el mismo tipo de reportes.")
    print("1. Diario")
    print("2. Semanal")
    print("3. Mensual")

    try:
        opt = int(input("Seleccione > ") or 0)
    except:
        opt = 0

    if opt not in (1,2,3):
        print("Opción inválida.")
        return

    if opt == 1:
        items = gastos_diarios(gastos, date.today())
        name = f"reporte_diario_{date.today()}.json"
    elif opt == 2:
        items = gastos_ultimo_dias(gastos, 7)
        name = f"reporte_semanal_{date.today()}.json"
    else:
        t = date.today()
        items = gastos_mes(gastos, t.year, t.month)
        name = f"reporte_mensual_{t.year}_{t.month}.json"

    out_folder = "reports"
    if not os.path.exists(out_folder):
        os.makedirs(out_folder)

    out_path = os.path.join(out_folder, name)

    if saveFile(out_path, items):
        print(f"✔ Reporte guardado en {out_path} (elementos: {len(items)})")
    else:
        print("Error guardando el reporte.")

# ============================================================
# MAIN
# ============================================================
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
            print("Bye!")
            break
        else:
            print("Opción inválida.")
            pause()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSaliendo...")
# === Edwin Ocampo === #