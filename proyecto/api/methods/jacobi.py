"""
api/methods/jacobi.py
──────────────────────
Método de Jacobi como Blueprint de Flask para resolver Sistemas de Ecuaciones Lineales.

Endpoint:
    POST /api/jacobi

Body JSON:
    {
        "A": [[4, -1, 0, 0],
              [-1, 4, -1, 0],
              [0, -1, 4, -1],
              [0, 0, -1, 3]],
        "b": [15, 10, 10, 10],
        "x0": [0, 0, 0, 0],     // opcional, por defecto vector nulo
        "tolerancia": 1e-6,     // opcional, por defecto 1e-6
        "max_iter": 100         // opcional, por defecto 100
    }

Respuesta exitosa:
    {
        "solucion": [x1, x2, x3, x4],
        "n_iteraciones": 14,
        "error_final": 4.5e-7,
        "convergido": true,
        "iteraciones": [
            {"iter": 1, "x": [...], "error": 1.5},
            ...
        ]
    }
"""

from flask import Blueprint, request, jsonify

jacobi_bp = Blueprint("jacobi", __name__)


def solve_jacobi(A, b, x0=None, tolerancia=1e-6, max_iter=100):
    n = len(A)
    # Validations
    if len(b) != n:
        raise ValueError("La dimensión de A y b no coincide.")
    for i, row in enumerate(A):
        if len(row) != n:
            raise ValueError("La matriz A no es cuadrada.")
        if abs(row[i]) < 1e-15:
            raise ValueError(f"El elemento diagonal A[{i}][{i}] es casi nulo. El método de Jacobi requiere diagonales no nulas.")

    # Condición suficiente de convergencia (diagonalmente dominante)
    # No la exigimos estrictamente, pero es buena práctica saberlo, aunque el método
    # lo dejamos correr igual hasta max_iter.

    if x0 is None or len(x0) != n:
        x0 = [0.0] * n

    x = x0[:]
    x_new = [0.0] * n
    iteraciones = []
    convergido = False
    error = float('inf')

    # Guardar iteración 0
    iteraciones.append({
        "iter": 0,
        "x": [round(val, 8) for val in x],
        "error": None
    })

    for k in range(1, max_iter + 1):
        for i in range(n):
            suma = 0.0
            for j in range(n):
                if i != j:
                    suma += A[i][j] * x[j]
            x_new[i] = (b[i] - suma) / A[i][i]

        # Calcular error (norma infinita)
        error = max(abs(x_new[i] - x[i]) for i in range(n))
        
        # Actualizar x para la siguiente iteración
        x = x_new[:]

        iteraciones.append({
            "iter": k,
            "x": [round(val, 8) for val in x],
            "error": error
        })

        if error < tolerancia:
            convergido = True
            break

    return {
        "solucion": x,
        "n_iteraciones": k,
        "error_final": error,
        "convergido": convergido,
        "iteraciones": iteraciones
    }


@jacobi_bp.route("/jacobi", methods=["POST"])
def endpoint_jacobi():
    data = request.get_json(force=True, silent=True)
    if not data or "A" not in data or "b" not in data:
        return jsonify({"error": "Faltan 'A' y 'b'."}), 400

    A, b = data["A"], data["b"]
    x0 = data.get("x0", None)
    tolerancia = float(data.get("tolerancia", 1e-6))
    max_iter = int(data.get("max_iter", 100))

    try:
        resultado = solve_jacobi(A, b, x0, tolerancia, max_iter)
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
