import os
import re
import json
from datetime import date
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

def ver_alertas():
    alertas = cargar_alertas()

    if not alertas:
        print("No hay alertas registradas.")
        input("Presiona Enter para continuar...")
        return

    print("====== HISTORIAL DE ALERTAS ======")
    
    for a in alertas:
        print(f"\nFecha: {a['fecha']}")
        print(f"Tipo: {a['tipo']}")
        print(f"Categoría: {a['categoria']}")
        print(f"Monto: {a['monto']}")
        print(f"Promedio: {a['promedio']}")
        print(f"Límite: {a['limite']}")
        print(f"Mensaje: {a['mensaje']}")
        print("---------------------------------")

    input("\nPresiona Enter para volver al menú...")


# ======================================
# CARGAR ALERTAS DESDE JSON
# ======================================
def cargar_alertas():
    try:
        with open("alertas.json", "r") as file:
            return json.load(file)
    except:
        return []

# ======================================
# GUARDAR ALERTAS EN JSON
# ======================================
def guardar_alertas(alertas):
    with open("alertas.json", "w") as file:
        json.dump(alertas, file, indent=4)

# ======================================
# REGISTRAR UNA ALERTA NUEVA
# ======================================
def registrar_alerta(tipo, categoria, monto, promedio, limite, mensaje):
    alertas = cargar_alertas()
    nueva_alerta = {
        "fecha": str(date.today()),
        "tipo": tipo,
        "categoria": categoria,
        "monto": monto,
        "promedio": promedio,
        "limite": limite,
        "mensaje": mensaje
    }
    alertas.append(nueva_alerta)
    guardar_alertas(alertas)

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

def cargar_config_alertas():
    path = "config_alertas.json"
    if not os.path.exists(path):
        print("⚠ No existe config_alertas.json. No se aplicarán alertas.")
        return None
    return readFile(path)

def promedio_diario_historico(gastos):
    if not gastos:
        return None
    
    # Agrupar gastos por fecha
    totals = {}
    for g in gastos:
        fecha = g["fecha"]
        totals[fecha] = totals.get(fecha, 0) + g["monto"]
    
    return sum(totals.values()) / len(totals)  # promedio

def promedio_semanal_historico(gastos):
    if not gastos:
        return None

    # Obtener semana ISO YYYY-WW
    totals = {}
    for g in gastos:
        y, m, d = map(int, g["fecha"].split("-"))
        semana = date(y, m, d).isocalendar()[1]
        totals[semana] = totals.get(semana, 0) + g["monto"]

    return sum(totals.values()) / len(totals)

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

    # === SISTEMA DE ALERTAS ===
    config = cargar_config_alertas()
    if not config:
        return  # sin config no hay alertas

    # Calcular totales del día y semana actual
    hoy = date.today()
    total_dia_actual = sum(
        g["monto"] for g in gastos if g["fecha"] == hoy.isoformat()
    )

    semana_actual = hoy.isocalendar()[1]
    total_semana_actual = sum(
        g["monto"]
        for g in gastos
        if date.fromisoformat(g["fecha"]).isocalendar()[1] == semana_actual
    )

    # Promedios históricos
    prom_dia = promedio_diario_historico(gastos)
    prom_sem = promedio_semanal_historico(gastos)

    # Si no hay historial, avisar (no alerta crítica)
    if not prom_dia or not prom_sem:
        print("⚠ No hay historial suficiente para generar alertas.")
        return

       # ALERTA DIARIA
    limite_dia = prom_dia * (config["porcentaje_alerta_diaria"] / 100)
    if total_dia_actual > limite_dia:
        print("🚨 ALERTA DIARIA:")
        print(f"Has superado el {config['porcentaje_alerta_diaria']}% del promedio diario histórico.")
        print(f"Promedio: {prom_dia:.2f} | Hoy: {total_dia_actual:.2f}")

        # === GUARDAR ALERTA ===
        registrar_alerta(
            tipo="Diaria",
            categoria=categoria,
            monto=total_dia_actual,
            promedio=prom_dia,
            limite=limite_dia,
            mensaje="Se superó el límite diario permitido."
        )

    # ALERTA SEMANAL
    limite_sem = prom_sem * (config["porcentaje_alerta_semanal"] / 100)
    if total_semana_actual > limite_sem:
        print("🚨 ALERTA SEMANAL:")
        print(f"Has superado el {config['porcentaje_alerta_semanal']}% del promedio semanal histórico.")
        print(f"Promedio: {prom_sem:.2f} | Semana Actual: {total_semana_actual:.2f}")

        # === GUARDAR ALERTA ===
        registrar_alerta(
            tipo="Semanal",
            categoria=categoria,
            monto=total_semana_actual,
            promedio=prom_sem,
            limite=limite_sem,
            mensaje="Se superó el límite semanal permitido."
        )

    # ALERTAS POR CATEGORÍA
    limites_cat = config.get("limites_categoria", {})
    if categoria in limites_cat:
        limite_cat = prom_dia * (limites_cat[categoria] / 100)
        total_cat_hoy = sum(
            g["monto"]
            for g in gastos
            if g["categoria"] == categoria and g["fecha"] == hoy.isoformat()
        )
        if total_cat_hoy > limite_cat:
            print("🚨 ALERTA POR CATEGORÍA:")
            print(f"Has superado el límite de categoría '{categoria}'.")
            print(f"Límite: {limites_cat[categoria]}% del promedio diario.")
            print(f"Promedio: {prom_dia:.2f} | Hoy en '{categoria}': {total_cat_hoy:.2f}")

            # === GUARDAR ALERTA ===
            registrar_alerta(
                tipo="Categoría",
                categoria=categoria,
                monto=total_cat_hoy,
                promedio=prom_dia,
                limite=limite_cat,
                mensaje=f"Se superó el límite de la categoría '{categoria}'."
            )


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
            ver_alertas()
        elif choice == 8:
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