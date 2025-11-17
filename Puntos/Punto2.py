import random
from collections import deque


class TipoSuciedad:
    """Definición de niveles de suciedad con puntaje"""
    NIVEL1 = {"nombre": "baja", "valor": 1, "simbolo": "🟡"}
    NIVEL2 = {"nombre": "media", "valor": 2, "simbolo": "🟠"}
    NIVEL3 = {"nombre": "alta", "valor": 3, "simbolo": "🔴"}
    TODOS = (NIVEL1, NIVEL2, NIVEL3)


class AgenteLimpiador:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.suciedad_limpiada = 0
        self.valor_total_limpiado = 0
        self.suciedades_limpiadas = []
        self.lugares_visitados = set()
        self.lugares_visitados.add((x, y))
        self.movimientos = 0

    # Percibe si hay suciedad en su posición actual
    def percibir(self, entorno):
        return entorno.hay_suciedad(self.x, self.y)

    # Obtiene las celdas adyacentes válidas
    def obtener_celdas_adyacentes(self, entorno):
        celdas = []
        direcciones = [
            ("arriba", 0, -1),
            ("abajo", 0, 1),
            ("izquierda", -1, 0),
            ("derecha", 1, 0)
        ]

        for nombre, dx, dy in direcciones:
            nx, ny = self.x + dx, self.y + dy
            if 0 <= nx < entorno.ancho and 0 <= ny < entorno.alto:
                celdas.append((nombre, nx, ny))

        return celdas

    def decidir_movimiento(self, entorno):
        celdas_adyacentes = self.obtener_celdas_adyacentes(entorno)

        celdas_sucias_adyacentes = []
        for nombre, x, y in celdas_adyacentes:
            if entorno.hay_suciedad(x, y):
                tipo = entorno.obtener_tipo_suciedad(x, y)
                celdas_sucias_adyacentes.append((nombre, x, y, tipo["valor"]))

        if celdas_sucias_adyacentes:
            # Buscar el máximo valor
            max_valor = max(c[3] for c in celdas_sucias_adyacentes)
            # Quedarse con todas las celdas que tengan ese valor máximo
            mejores = [c for c in celdas_sucias_adyacentes if c[3] == max_valor]
            # Elegir una al azar entre las mejores (por si hay varias)
            nombre, _, _, _ = random.choice(mejores)
            return nombre

        # Filtrar celdas no visitadas
        celdas_no_visitadas = [
            (nombre, x, y) for nombre, x, y in celdas_adyacentes
            if (x, y) not in self.lugares_visitados
        ]

        # Priorizar celdas no visitadas
        if celdas_no_visitadas:
            direccion, _, _ = random.choice(celdas_no_visitadas)
            return direccion

        # Si todas están visitadas, elegir cualquiera
        if celdas_adyacentes:
            direccion, _, _ = random.choice(celdas_adyacentes)
            return direccion

        return None

    # Lógica: SI hay suciedad ENTONCES limpiar, SINO explorar inteligentemente
    def decidir_y_actuar(self, percepcion, entorno):
        if percepcion:
            return "limpiar"
        else:
            return self.decidir_movimiento(entorno)

    # Actualiza posición y registra en memoria
    def actualizar_posicion(self, nueva_x, nueva_y):
        self.x = nueva_x
        self.y = nueva_y
        self.lugares_visitados.add((nueva_x, nueva_y))
        self.movimientos += 1

    # Retorna estadísticas de rendimiento
    def obtener_estadisticas(self, entorno):
        total_celdas = entorno.ancho * entorno.alto
        celdas_exploradas = len(self.lugares_visitados)
        porcentaje_exploracion = (celdas_exploradas / total_celdas) * 100

        return {
            'suciedad_limpiada': self.suciedad_limpiada,
            'valor_total_limpiado': self.valor_total_limpiado,
            'movimientos': self.movimientos,
            'celdas_exploradas': celdas_exploradas,
            'total_celdas': total_celdas,
            'porcentaje_exploracion': porcentaje_exploracion
        }


class EntornoGrid:
    """Entorno: Grid 2D con suciedad"""

    def __init__(self, ancho, alto, num_suciedad):
        self.ancho = ancho
        self.alto = alto
        self.suciedad = {}
        self._generar_suciedad(num_suciedad)
        self.suciedad_inicial = len(self.suciedad)
        self.valor_total_inicial = sum(t["valor"]
                                       for t in self.suciedad.values())

    def _generar_suciedad(self, num_suciedad):
        while len(self.suciedad) < num_suciedad:
            x = random.randint(0, self.ancho - 1)
            y = random.randint(0, self.alto - 1)
            if (x, y) not in self.suciedad:
                tipo = random.choice(TipoSuciedad.TODOS)
                self.suciedad[(x, y)] = tipo

    # Verifica si hay suciedad en la posición
    def hay_suciedad(self, x, y):
        return (x, y) in self.suciedad

    # Devuelve el tipo de suciedad en una posición
    def obtener_tipo_suciedad(self, x, y):
        return self.suciedad.get((x, y))

    # Limpia la suciedad en la posición y devuelve el tipo
    def limpiar(self, x, y):
        if (x, y) in self.suciedad:
            tipo = self.suciedad[(x, y)]
            del self.suciedad[(x, y)]
            return tipo
        return None

    # Mueve el agente en la dirección especificada
    def mover_agente(self, agente, direccion):
        nueva_x, nueva_y = agente.x, agente.y

        if direccion == "arriba" and agente.y > 0:
            nueva_y -= 1
        elif direccion == "abajo" and agente.y < self.alto - 1:
            nueva_y += 1
        elif direccion == "izquierda" and agente.x > 0:
            nueva_x -= 1
        elif direccion == "derecha" and agente.x < self.ancho - 1:
            nueva_x += 1

        agente.actualizar_posicion(nueva_x, nueva_y)

    # Visualización del entorno con indicador de celdas visitadas
    def mostrar(self, agente):
        print("  ", end="")
        for x in range(self.ancho):
            print(f"{x} ", end="")
        print()

        for y in range(self.alto):
            print(f"{y} ", end="")
            for x in range(self.ancho):
                if x == agente.x and y == agente.y:
                    print("🤖", end=" ")
                elif (x, y) in self.suciedad:
                    tipo = self.suciedad[(x, y)]
                    print(tipo["simbolo"], end=" ")
                elif (x, y) in agente.lugares_visitados:
                    print("✓ ", end=" ")
                else:
                    print("⬜", end=" ")
            print()
        print()


def simular_limpieza_con_memoria(ancho=5, alto=5, num_suciedad=12, pasos=50):

    entorno = EntornoGrid(ancho, alto, num_suciedad)
    agente = AgenteLimpiador(ancho // 2, alto // 2)

    print("=" * 50)
    print("AGENTE LIMPIADOR")
    print("=" * 50)
    print(f"Configuración:")
    print(f"  - Tamaño del grid: {ancho}x{alto} ({ancho*alto} celdas)")
    print(f"  - Suciedad inicial: {num_suciedad}")
    print(f"  - Pasos máximos: {pasos}")
    print("\nNiveles de suciedad:")
    print("  🟡 Baja  (valor 1)")
    print("  🟠 Media (valor 2)")
    print("  🔴 Alta  (valor 3)")

    print("\nEstado inicial:")
    entorno.mostrar(agente)

    for paso in range(pasos):
        percepcion = agente.percibir(entorno)
        accion = agente.decidir_y_actuar(percepcion, entorno)

        if accion == "limpiar":
            tipo = entorno.limpiar(agente.x, agente.y)
            if tipo is not None:
                agente.suciedad_limpiada += 1
                agente.valor_total_limpiado += tipo["valor"]
                agente.suciedades_limpiadas.append(tipo["nombre"])
                print(
                    f"Paso {paso + 1}: 🧹 Limpiando suciedad {tipo['nombre']} "
                    f"{tipo['simbolo']} en ({agente.x}, {agente.y}) "
                    f"[+{tipo['valor']} pts]"
                )
        elif accion:
            entorno.mover_agente(agente, accion)
            print(
                f"Paso {paso + 1} Moviéndose {accion} a ({agente.x}, {agente.y})")

        # Mostrar estado cada 10 pasos
        if (paso + 1) % 10 == 0:
            print(f"\n--- Estado en paso {paso + 1} ---")
            entorno.mostrar(agente)
            stats = agente.obtener_estadisticas(entorno)
            print(f"Exploración: {stats['porcentaje_exploracion']:.1f}% | "
                  f"Limpieza: {stats['suciedad_limpiada']}/{entorno.suciedad_inicial} | "
                  f"Valor: {stats['valor_total_limpiado']}/{entorno.valor_total_inicial}")

        # Condición de terminación
        if len(entorno.suciedad) == 0:
            print(
                f"\n✅ ¡Toda la suciedad ha sido limpiada en {paso + 1} pasos!")
            break

    # Estadísticas finales
    print("\n" + "=" * 50)
    print("ESTADÍSTICAS FINALES")
    print("=" * 50)
    stats = agente.obtener_estadisticas(entorno)

    print(f"\nRendimiento:")
    print(
        f"  ✓ Suciedad limpiada: {stats['suciedad_limpiada']}/{entorno.suciedad_inicial}")
    print(
        f"  ✓ Valor total limpiado: {stats['valor_total_limpiado']}/{entorno.valor_total_inicial} puntos")
    print(f"  ✓ Movimientos totales: {stats['movimientos']}")

    print(f"Exploración:")
    print(
        f"  ✓ Celdas exploradas: {stats['celdas_exploradas']}/{stats['total_celdas']}")
    print(
        f"  ✓ Porcentaje de cobertura: {stats['porcentaje_exploracion']:.1f}%")

    print(f"\nEstado final:")
    entorno.mostrar(agente)

    if len(entorno.suciedad) > 0:
        print(f"⚠️  Suciedad restante: {len(entorno.suciedad)} ubicaciones")
        print(f"   Posiciones sin limpiar: {list(entorno.suciedad.keys())}")


# Ejecutar simulación
if __name__ == "__main__":
    simular_limpieza_con_memoria()
