from flask import Blueprint, request, jsonify

gauss_bp = Blueprint("gauss", __name__)

def solve_gauss(A, b, pivoteo=False):
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

        if abs(M[k][k]) == 0:
            raise ValueError(f"Pivote nulo en la fila {k+1}. El método de Gauss simple falla sin pivoteo.")

        for i in range(k+1, n):
            factor = M[i][k] / M[k][k]
            for j in range(k, n+1):
                M[i][j] -= factor * M[k][j]

        # Save step
        pasos.append({"etapa": f"Eliminación columna {k+1}", "matriz": [row[:] for row in M]})

    # Sustitución hacia atrás
    x = [0.0] * n
    for i in range(n-1, -1, -1):
        s = sum(M[i][j] * x[j] for j in range(i+1, n))
        x[i] = (M[i][n] - s) / M[i][i]

    return {
        "solucion": x,
        "pasos": pasos,
        "n": n
    }

@gauss_bp.route("/gauss", methods=["POST"])
def endpoint_gauss():
    data = request.get_json(force=True, silent=True)
    if not data or "A" not in data or "b" not in data:
        return jsonify({"error": "Faltan 'A' y 'b'."}), 400

    A, b = data["A"], data["b"]
    pivoteo = data.get("pivoteo", False)
    try:
        resultado = solve_gauss(A, b, pivoteo)
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
