from flask import Flask, render_template, request, jsonify
import math
import random

app = Flask(__name__)

# Diccionario de coordenadas de ciudades
CITIES = {
    'Jiloyork': (19.916012, -99.580580),
    'Toluca': (19.289165, -99.655697),
    'Atlacomulco': (19.799520, -99.873844),
    'Guadalajara': (20.677754, -103.346253),
    'Monterrey': (25.691611, -100.321838),
    'QuintanaRoo': (21.163111, -86.802315),
    'Michoacán': (19.701400, -101.208296),
    'Aguascalientes': (21.876410, -102.264386),
    'CDMX': (19.432713, -99.133183),
    'Querétaro': (20.597194, -100.386670)
}

# Calcular distancia euclidiana entre dos coordenadas
def distancia(coord1, coord2):
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    return math.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2)

# Evaluar una ruta completa
def evalua_ruta(ruta, ciudades):
    total = sum(distancia(ciudades[ruta[i]], ciudades[ruta[i+1]]) for i in range(len(ruta)-1))
    total += distancia(ciudades[ruta[-1]], ciudades[ruta[0]])  # Ruta cíclica
    return total

# Generar vecinos intercambiando dos ciudades
def obtener_vecinos(ruta):
    vecinos = []
    for i in range(1, len(ruta) - 1):  # No mover origen y destino
        for j in range(i + 1, len(ruta) - 1):
            vecino = ruta[:]
            vecino[i], vecino[j] = vecino[j], vecino[i]
            vecinos.append(vecino)
    return vecinos

# Búsqueda Tabú
def busqueda_tabu(ruta_inicial, max_iteraciones=100, tamaño_tabu=10):
    mejor_ruta = ruta_inicial[:]
    ruta_actual = ruta_inicial[:]
    mejor_costo = evalua_ruta(mejor_ruta, CITIES)
    lista_tabu = []

    for _ in range(max_iteraciones):
        vecinos = obtener_vecinos(ruta_actual)
        vecinos = [v for v in vecinos if v not in lista_tabu]

        if not vecinos:
            break

        vecino = min(vecinos, key=lambda r: evalua_ruta(r, CITIES))
        costo_vecino = evalua_ruta(vecino, CITIES)

        if costo_vecino < mejor_costo:
            mejor_ruta = vecino[:]
            mejor_costo = costo_vecino

        lista_tabu.append(vecino)
        if len(lista_tabu) > tamaño_tabu:
            lista_tabu.pop(0)

        ruta_actual = vecino

    return mejor_ruta

@app.route('/')
def index():
    return render_template('index.html', cities=CITIES.keys())

@app.route('/solve', methods=['POST'])
def solve():
    data = request.form
    origin_city = data['origin_city']
    destination_city = data['destination_city']

    intermedias = [c for c in CITIES.keys() if c != origin_city and c != destination_city]
    random.shuffle(intermedias)
    ruta = [origin_city] + intermedias + [destination_city]

    ruta_optima = busqueda_tabu(ruta, max_iteraciones=200, tamaño_tabu=15)
    distancia_total = evalua_ruta(ruta_optima, CITIES)

    return jsonify({'ruta': ruta_optima, 'distancia_total': distancia_total})

if __name__ == '__main__':
    app.run(debug=True)
