"""
api/methods/condicion.py
────────────────────────
Módulo para calcular el número de condición de una matriz y analizar la sensibilidad
de la solución de un sistema Ax = b ante perturbaciones en b.

Endpoint:
    POST /api/condicion

Body JSON:
    {
        "A": [[1, 1], [1, 1.0001]],
        "b": [2, 2.0001],
        "delta_b": [0.0001, -0.0001]
    }

Respuesta exitosa:
    {
        "norma_A": ...,
        "norma_A_inv": ...,
        "condicion": ...,
        "x": [...],
        "x_pert": [...],
        "delta_x": [...],
        "error_relativo_b": ...,
        "error_relativo_x": ...
    }
"""

from flask import Blueprint, request, jsonify

condicion_bp = Blueprint("condicion", __name__)


def norma_infinita_matriz(A):
    """Calcula la norma infinita de una matriz (máxima suma absoluta por filas)."""
    return max(sum(abs(x) for x in fila) for fila in A)


def norma_infinita_vector(v):
    """Calcula la norma infinita de un vector (máximo valor absoluto)."""
    return max(abs(x) for x in v)


def invertir_matriz(A):
    """
    Invierte una matriz cuadrada A utilizando eliminación de Gauss-Jordan con pivoteo parcial.
    Retorna A^{-1} o lanza ValueError si la matriz es singular.
    """
    n = len(A)
    # Crear matriz ampliada [A | I]
    M = []
    for i in range(n):
        fila = A[i][:] + [1.0 if i == j else 0.0 for j in range(n)]
        M.append(fila)

    for k in range(n):
        # Pivoteo parcial
        max_piv = k
        for i in range(k + 1, n):
            if abs(M[i][k]) > abs(M[max_piv][k]):
                max_piv = i
        
        if max_piv != k:
            M[k], M[max_piv] = M[max_piv], M[k]
            
        pivote = M[k][k]
        if abs(pivote) < 1e-12:
            raise ValueError("La matriz es singular o está demasiado mal condicionada para ser invertida con precisión estándar.")

        # Dividir la fila pivot por el pivote
        for j in range(k, 2 * n):
            M[k][j] /= pivote

        # Hacer ceros en el resto de la columna
        for i in range(n):
            if i != k:
                factor = M[i][k]
                for j in range(k, 2 * n):
                    M[i][j] -= factor * M[k][j]

    # Extraer la inversa de la parte derecha de la matriz ampliada
    A_inv = [fila[n:] for fila in M]
    return A_inv


def multiplicar_matriz_vector(M, v):
    """Multiplica una matriz M por un vector v."""
    n = len(M)
    resultado = [0.0] * n
    for i in range(n):
        resultado[i] = sum(M[i][j] * v[j] for j in range(len(v)))
    return resultado


def sumar_vectores(v1, v2):
    return [x + y for x, y in zip(v1, v2)]


def restar_vectores(v1, v2):
    return [x - y for x, y in zip(v1, v2)]


def analizar_condicion(A, b, delta_b=None):
    n = len(A)
    if len(b) != n:
        raise ValueError("La dimensión de A y b no coincide.")
        
    if delta_b is None or len(delta_b) != n:
        delta_b = [0.0] * n

    try:
        A_inv = invertir_matriz(A)
    except ValueError as e:
        raise ValueError(f"No se puede calcular el número de condición. {e}")

    norma_A = norma_infinita_matriz(A)
    norma_A_inv = norma_infinita_matriz(A_inv)
    condicion = norma_A * norma_A_inv

    # Calcular solución exacta (x = A^-1 * b)
    x = multiplicar_matriz_vector(A_inv, b)
    
    # Calcular solución perturbada
    b_pert = sumar_vectores(b, delta_b)
    x_pert = multiplicar_matriz_vector(A_inv, b_pert)
    
    # Vector diferencia de x
    delta_x = restar_vectores(x_pert, x)
    
    # Errores relativos
    norma_b = norma_infinita_vector(b)
    norma_x = norma_infinita_vector(x)
    
    err_rel_b = norma_infinita_vector(delta_b) / norma_b if norma_b != 0 else 0
    err_rel_x = norma_infinita_vector(delta_x) / norma_x if norma_x != 0 else 0

    return {
        "norma_A": norma_A,
        "norma_A_inv": norma_A_inv,
        "condicion": condicion,
        "x": x,
        "x_pert": x_pert,
        "delta_x": delta_x,
        "error_relativo_b": err_rel_b,
        "error_relativo_x": err_rel_x
    }


@condicion_bp.route("/condicion", methods=["POST"])
def endpoint_condicion():
    data = request.get_json(force=True, silent=True)
    if not data or "A" not in data or "b" not in data:
        return jsonify({"error": "Faltan 'A' y 'b'."}), 400

    A = data["A"]
    b = data["b"]
    delta_b = data.get("delta_b", None)

    try:
        resultado = analizar_condicion(A, b, delta_b)
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
