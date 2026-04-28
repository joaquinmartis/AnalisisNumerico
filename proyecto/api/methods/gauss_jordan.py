from flask import Blueprint, request, jsonify

gauss_jordan_bp = Blueprint("gauss_jordan", __name__)

def solve_gauss_jordan(A, b, pivoteo=False):
    n = len(A)
    # Validations
    if len(b) != n:
        raise ValueError("La dimensión de A y b no coincide.")
    for row in A:
        if len(row) != n:
            raise ValueError("La matriz A no es cuadrada.")

    M = [row[:] + [b[i]] for i, row in enumerate(A)]
    pasos = []

    # Save initial state
    pasos.append({"etapa": "Inicial", "matriz": [row[:] for row in M]})

    for k in range(n):
        if pivoteo:
            max_piv = k
            for i in range(k+1, n):
                if abs(M[i][k]) > abs(M[max_piv][k]):
                    max_piv = i
            if max_piv != k:
                M[k], M[max_piv] = M[max_piv], M[k]
                pasos.append({"etapa": f"Pivoteo Parcial (Fila {k+1} ↔ Fila {max_piv+1})", "matriz": [row[:] for row in M]})

        if abs(M[k][k]) < 1e-12:
            raise ValueError(f"Pivote nulo en la fila {k+1}. El método de Gauss-Jordan simple falla sin pivoteo.")
        
        # Normalizar fila pivote
        pivote = M[k][k]
        for j in range(k, n+1):
            M[k][j] /= pivote
            
        # Eliminar resto de filas
        for i in range(n):
            if i != k:
                factor = M[i][k]
                for j in range(k, n+1):
                    M[i][j] -= factor * M[k][j]

        # Save step
        pasos.append({"etapa": f"Eliminación pivote {k+1}", "matriz": [row[:] for row in M]})

    x = [M[i][n] for i in range(n)]

    return {
        "solucion": x,
        "pasos": pasos,
        "n": n
    }

@gauss_jordan_bp.route("/gauss_jordan", methods=["POST"])
def endpoint_gauss_jordan():
    data = request.get_json(force=True, silent=True)
    if not data or "A" not in data or "b" not in data:
        return jsonify({"error": "Faltan 'A' y 'b'."}), 400

    A, b = data["A"], data["b"]
    pivoteo = data.get("pivoteo", False)
    try:
        resultado = solve_gauss_jordan(A, b, pivoteo)
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
