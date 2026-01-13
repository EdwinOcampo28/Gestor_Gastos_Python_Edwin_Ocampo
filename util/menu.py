def clear_console():
    import os
    os.system("cls" if os.name=="nt" else "clear")

def main_menu() -> int:
    print("=== SIMULADOR / GESTOR DE GASTOS ===")
    print("1. Registrar nuevo gasto")
    print("2. Listar todos los gastos")
    print("3. Listar gastos por categoría")
    print("4. Calcular totales")
    print("5. Reportes")
    print("6. Guardar reporte JSON")
    print("7. Ver historial de alertas de gastos")
    print("8. Ver panel de promedios y límites")
    print("9. Salir")
    try:
        return int(input("Seleccione > ") or 0)
    except:
        return 0

def pause():
    input("\nPresione ENTER para continuar...")

#==Edwin Ocampo==#