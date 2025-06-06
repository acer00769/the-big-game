import random
import os
import csv
from datetime import datetime

# Configuración avanzada
CATEGORIAS = {
    'S': {'ratio_min': 1000, 'puntos_base': 1000, 'nombre': 'Extremo'},
    'A': {'ratio_min': 500, 'puntos_base': 800, 'nombre': 'Difícil'},
    'B': {'ratio_min': 200, 'puntos_base': 600, 'nombre': 'Intermedio'},
    'C': {'ratio_min': 50, 'puntos_base': 400, 'nombre': 'Fácil'},
    'D': {'ratio_min': 0, 'puntos_base': 200, 'nombre': 'Principiante'}
}

LOGROS = {
    'legendario': {'condicion': lambda c, iu, it: c == 'S' and iu == 1},
    'eficiente': {'condicion': lambda c, iu, it: iu/it <= 0.2},
    'invicto': {'condicion': lambda c, iu, it: iu == it},
    'maestro': {'condicion': lambda c, iu, it: c in ['S', 'A'] and iu/it <= 0.3},
    'principiante': {'condicion': lambda c, iu, it: c == 'D' and iu <= 2}
}

NIVELES = [
    (0, 'Novato'),
    (1000, 'Aprendiz'),
    (5000, 'Competente'),
    (10000, 'Experto'),
    (25000, 'Maestro'),
    (50000, 'Gran Maestro'),
    (100000, 'Leyenda')
]

def inicializar_archivos():
    for archivo in ['historial.csv', 'logros.csv', 'leaderboard.csv']:
        if not os.path.exists(archivo):
            with open(archivo, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                if archivo == 'historial.csv':
                    writer.writerow(['Fecha', 'Nombre', 'Categoria', 'Rango', 'Intentos', 'Usados', 'Puntaje', 'Resultado'])
                elif archivo == 'logros.csv':
                    writer.writerow(['Fecha', 'Nombre', 'Logro'])
                elif archivo == 'leaderboard.csv':
                    writer.writerow(['Fecha', 'Nombre', 'Puntaje', 'Categoria', 'Intentos'])

def determinar_categoria(max_num, intentos):
    ratio = max_num / intentos
    for cat, valores in CATEGORIAS.items():
        if ratio >= valores['ratio_min']:
            return cat
    return 'D'

def calcular_puntaje(categoria, intentos_usados, intentos_totales):
    eficiencia = (intentos_totales - intentos_usados + 1) / intentos_totales
    return int(CATEGORIAS[categoria]['puntos_base'] * eficiencia)

def guardar_resultado(nombre, max_num, intentos_totales, intentos_usados, gano):
    categoria = determinar_categoria(max_num, intentos_totales)
    puntaje = calcular_puntaje(categoria, intentos_usados, intentos_totales) if gano else 0
    
    with open('historial.csv', 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        resultado = 'Victoria' if gano else 'Derrota'
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            nombre,
            categoria,
            max_num,
            intentos_totales,
            intentos_usados,
            puntaje,
            resultado
        ])
    
    if gano:
        actualizar_leaderboard(nombre, puntaje, categoria, intentos_usados)
        return verificar_logros(nombre, categoria, intentos_usados, intentos_totales)
    return []

def verificar_logros(nombre, categoria, intentos_usados, intentos_totales):
    logros_desbloqueados = []
    for logro, datos in LOGROS.items():
        if datos['condicion'](categoria, intentos_usados, intentos_totales):
            logros_desbloqueados.append(logro)
    
    if logros_desbloqueados:
        with open('logros.csv', 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            for logro in logros_desbloqueados:
                writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M"), nombre, logro])
    
    return logros_desbloqueados

def calcular_nivel(puntaje_total):
    for puntos, nombre in reversed(NIVELES):
        if puntaje_total >= puntos:
            return nombre, puntaje_total - puntos
    return NIVELES[0][1], 0

def actualizar_leaderboard(nombre, puntaje, categoria, intentos):
    with open('leaderboard.csv', 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            nombre,
            puntaje,
            categoria,
            intentos
        ])

def mostrar_estadisticas_completas():
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # Calcular nivel
    puntaje_total = 0
    try:
        with open('historial.csv', 'r', encoding='utf-8') as f:
            lector = csv.DictReader(f)
            for fila in lector:
                if fila['Resultado'] == 'Victoria':
                    puntaje_total += int(fila['Puntaje'])
    except FileNotFoundError:
        pass
    
    nivel, progreso = calcular_nivel(puntaje_total)
    
    print("═" * 40)
    print("═ ESTADO DEL JUGADOR ═".center(40))
    print("═" * 40)
    print(f"\nNivel actual: {nivel}")
    print(f"Progreso al siguiente nivel: {progreso} puntos\n")
    
    # Leaderboard
    print("═" * 40)
    print("═ LEADERBOARD GLOBAL ═".center(40))
    print("═" * 40)
    try:
        with open('leaderboard.csv', 'r', encoding='utf-8') as f:
            lector = csv.DictReader(f)
            registros = sorted(lector, key=lambda x: int(x['Puntaje']), reverse=True)[:5]
            
            for i, registro in enumerate(registros, 1):
                print(f"{i}. {registro['Nombre']}: {registro['Puntaje']} pts")
                print(f"   Categoría: {registro['Categoria']}, Intentos: {registro['Intentos']}\n")
    except FileNotFoundError:
        print("\nAún no hay registros en el leaderboard")
    
    # Logros
    print("═" * 40)
    print("═ LOGROS DESBLOQUEADOS ═".center(40))
    print("═" * 40)
    try:
        with open('logros.csv', 'r', encoding='utf-8') as f:
            lector = csv.DictReader(f)
            logros = set()
            for fila in lector:
                logros.add(fila['Logro'])
            
            for logro in logros:
                print(f"- {logro.capitalize()}")
    except FileNotFoundError:
        print("\nAún no has desbloqueado logros")

def jugar():
    inicializar_archivos()
    nombre = input("\n¡Bienvenido al Juego de Adivinar el Número!\n\n¿Cómo te llamas? ").strip()
    
    while True:
        try:
            max_num = int(input("\nElije el número máximo (ej: 100): "))
            intentos = int(input("Elije la cantidad de intentos: "))
            
            if max_num > 0 and intentos > 0:
                break
            print("⚠️ Los valores deben ser mayores que 0")
        except ValueError:
            print("⚠️ Solo se permiten números enteros")
    
    numero_secreto = random.randint(1, max_num)
    categoria = determinar_categoria(max_num, intentos)
    
    print(f"\n¡Dificultad {CATEGORIAS[categoria]['nombre']} detectada!")
    print(f"\nHola {nombre}, he pensado un número entre 1 y {max_num}.")
    print(f"Tienes {intentos} intentos. ¡Buena suerte!")
    
    for intento_actual in range(1, intentos + 1):
        while True:
            try:
                adivinanza = int(input(f"\nIntento {intento_actual}/{intentos} → Ingresa un número: "))
                
                if 1 <= adivinanza <= max_num:
                    break
                print(f"⚠️ El número debe estar entre 1 y {max_num}")
            except ValueError:
                print("⚠️ ¡Solo se permiten números enteros!")
        
        if adivinanza < numero_secreto:
            print("Mi número es más alto")
        elif adivinanza > numero_secreto:
            print("Mi número es más bajo")
        else:
            print(f"\n¡Felicidades {nombre}! 🎉 Adivinaste en {intento_actual} intentos!")
            logros = guardar_resultado(nombre, max_num, intentos, intento_actual, True)
            if logros:
                print("\n¡Logros desbloqueados!")
                for logro in logros:
                    print(f"- {logro.capitalize()}")
            return
    
    print(f"\n¡Agotaste tus intentos! 😢 El número era {numero_secreto}")
    guardar_resultado(nombre, max_num, intentos, intentos, False)

if __name__ == "__main__":
    while True:
        mostrar_estadisticas_completas()
        jugar()
        
        while True:
            opcion = input("\n¿Quieres jugar otra partida? (s/n): ").lower()
            if opcion in ['s', 'n']:
                break
            print("⚠️ Opción inválida. Solo 's' o 'n'")
        
        if opcion != 's':
            print("\n¡Hasta la próxima! 🎮\n")
            break
