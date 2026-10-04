import sys
import re

lineas = sys.stdin.read().splitlines()
idx = 0


def siguiente_linea():
    global idx
    linea = lineas[idx]
    idx += 1
    return linea


def parsear_conjunto(token):
    """Convierte '{1 5}' -> frozenset({1,5}); '0' -> frozenset() (vacio)."""
    token = token.strip()
    if token == "0":
        return frozenset()
    interior = token[1:-1].strip()  # quita las llaves { }
    if interior == "":
        return frozenset()
    return frozenset(int(x) for x in interior.split())


def leer_caso():
    n = int(siguiente_linea())
    S = set(map(int, siguiente_linea().split()))
    simbolos = siguiente_linea().split()
    finales = set(map(int, siguiente_linea().split()))

    Delta = {}  # Delta[(estado, simbolo)] = frozenset de estados destino
    for _ in range(n):
        tokens = re.findall(r'\{[^}]*\}|\S+', siguiente_linea())
        q = int(tokens[0])
        for simbolo, conjunto_txt in zip(simbolos, tokens[1:]):
            Delta[(q, simbolo)] = parsear_conjunto(conjunto_txt)

    return n, S, simbolos, finales, Delta


def subset_construction(S, simbolos, finales_N, Delta):
    """Kozen Lecture 6: construye el DFA M a partir del NFA N, de forma
    perezosa (solo subconjuntos alcanzables desde el estado inicial S)."""
    inicial = frozenset(S)
    visitados = {inicial}
    orden = [inicial]          # orden de descubrimiento (para numerar los estados)
    cola = [inicial]
    delta_M = {}

    while cola:
        A = cola.pop(0)
        for a in simbolos:
            destino = frozenset()
            for q in A:
                destino |= Delta.get((q, a), frozenset())
            delta_M[(A, a)] = destino
            if destino not in visitados:
                visitados.add(destino)
                orden.append(destino)
                cola.append(destino)

    finales_M = {A for A in orden if A & finales_N}
    return orden, delta_M, inicial, finales_M


def imprimir_tabla(numero_caso, orden, delta_M, inicial, finales_M, simbolos):
    nombre = {A: i for i, A in enumerate(orden)}

    print(f"Case {numero_caso}:")
    print(f"Initial state of M: {nombre[inicial]}")
    ids_finales = sorted(nombre[A] for A in finales_M)
    print(f"Final states of M: {{{', '.join(map(str, ids_finales))}}}")
    print()
    print("   " + " ".join(simbolos))
    for A in orden:
        marca = ("-> " if A == inicial else "   ") + ("(F)" if A in finales_M else "   ")
        fila_destinos = " ".join(str(nombre[delta_M[(A, a)]]) for a in simbolos)
        contenido = "{" + ",".join(map(str, sorted(A))) + "}" if A else "{}"
        print(f"{marca} {nombre[A]:<3} {fila_destinos:<10} ; {nombre[A]} = {contenido}")


def dibujar_diagrama(ax, orden, delta_M, inicial, finales_M, simbolos, titulo):
    """Dibuja el DFA resultante (M) sobre un eje de matplotlib, usando solo
    circulos y flechas -- no requiere ningun programa externo ni genera
    ningun archivo en disco."""
    nombre = {A: i for i, A in enumerate(orden)}
    n = len(orden)

    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(titulo, fontsize=11)

    radio_layout = 3.0
    radio_estado = 0.4
    if n == 1:
        posiciones = {0: (0, 0)}
    else:
        posiciones = {
            i: (radio_layout * math.cos(2 * math.pi * i / n + math.pi / 2),
                radio_layout * math.sin(2 * math.pi * i / n + math.pi / 2))
            for i in range(n)
        }

    x0, y0 = posiciones[nombre[inicial]]
    ax.annotate("", xy=(x0 - radio_estado, y0), xytext=(x0 - radio_estado - 0.8, y0),
                arrowprops=dict(arrowstyle="-|>", lw=1.5, color="black"))

    for A in orden:
        i = nombre[A]
        x, y = posiciones[i]
        ax.add_patch(Circle((x, y), radio_estado, fill=False, lw=1.5, color="black"))
        if A in finales_M:
            ax.add_patch(Circle((x, y), radio_estado - 0.08, fill=False, lw=1.5, color="black"))
        ax.text(x, y, str(i), ha="center", va="center", fontsize=11)

    agrupado = {}
    for A in orden:
        for a in simbolos:
            destino = nombre[delta_M[(A, a)]]
            agrupado.setdefault((nombre[A], destino), []).append(a)

    for (origen, destino), etiquetas in agrupado.items():
        etiqueta = ",".join(etiquetas)
        xo, yo = posiciones[origen]
        xd, yd = posiciones[destino]
        if origen == destino:
            flecha = FancyArrowPatch(
                (xo + 0.15, yo + radio_estado), (xo - 0.15, yo + radio_estado),
                connectionstyle="arc3,rad=2.2", arrowstyle="-|>",
                mutation_scale=12, lw=1.1, color="black")
            ax.add_patch(flecha)
            ax.text(xo, yo + radio_estado + 0.9, etiqueta, ha="center", fontsize=9)
        else:
            dx, dy = xd - xo, yd - yo
            dist = math.hypot(dx, dy)
            ux, uy = dx / dist, dy / dist
            inicio = (xo + ux * radio_estado, yo + uy * radio_estado)
            fin = (xd - ux * radio_estado, yd - uy * radio_estado)
            flecha = FancyArrowPatch(
                inicio, fin, connectionstyle="arc3,rad=0.15", arrowstyle="-|>",
                mutation_scale=12, lw=1.1, color="black")
            ax.add_patch(flecha)
            mx, my = (inicio[0] + fin[0]) / 2, (inicio[1] + fin[1]) / 2
            nx, ny = -uy, ux
            ax.text(mx + nx * 0.35, my + ny * 0.35, etiqueta, ha="center", fontsize=9)

    margen = radio_layout + 1.5
    ax.set_xlim(-margen, margen)
    ax.set_ylim(-margen, margen)


c = int(siguiente_linea())
resultados = []
for i in range(c):
    n, S, simbolos, finales, Delta = leer_caso()
    orden, delta_M, inicial, finales_M = subset_construction(S, simbolos, finales, Delta)
    imprimir_tabla(i + 1, orden, delta_M, inicial, finales_M, simbolos)
    if i < c - 1:
        print()
    resultados.append((orden, delta_M, inicial, finales_M, simbolos))

# Diagrama automatico del DFA resultante de cada caso, en una sola ventana.
# No se guarda ningun archivo; solo se muestra en pantalla.
try:
    import math
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle, FancyArrowPatch

    columnas = min(3, c)
    filas = math.ceil(c / columnas)
    fig, ejes = plt.subplots(filas, columnas, figsize=(5 * columnas, 5 * filas))
    ejes = [ejes] if c == 1 else ejes.flatten()

    for i, (orden, delta_M, inicial, finales_M, simbolos) in enumerate(resultados):
        dibujar_diagrama(ejes[i], orden, delta_M, inicial, finales_M, simbolos,
                          titulo=f"Caso {i + 1}: DFA M")
    for j in range(len(resultados), len(ejes)):
        ejes[j].axis("off")

    fig.tight_layout()
    plt.show()
except ImportError:
    print("[diagram] matplotlib no esta instalado, se omite el diagrama "
          "(pip install matplotlib)", file=sys.stderr)