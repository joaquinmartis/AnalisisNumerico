"""
api/methods/punto_fijo.py
─────────────────────────
Método de Punto Fijo como Blueprint de Flask.

Endpoint:
    POST /api/punto_fijo

Body JSON:
    {
        "funcion":    "cos(x)",   // función g(x) tal que x = g(x)
        "x0":         1.0,        // valor inicial
        "tolerancia": 1e-6,       // criterio de parada (error relativo o absoluto)
        "max_iter":   100         // máximo de iteraciones
    }

Respuesta exitosa:
    {
        "raiz":          0.739085,
        "n_iteraciones": 30,
        "error_final":   8.8e-7,
        "convergido":    true,
        "iteraciones": [
            { "n": 1, "x": 0.5403, "error": 0.4596 },
            ...
        ]
    }
"""

from flask import Blueprint, request, jsonify
import sympy as sp

punto_fijo_bp = Blueprint("punto_fijo", __name__)


def _parsear_funcion(expr_str: str):
    """
    Convierte un string como 'cos(x)' en una función Python callable.
    Usa sympy para parsear de forma segura.
    """
    x = sp.Symbol("x")
    try:
        expr = sp.sympify(expr_str, locals={"x": x})
    except Exception:
        raise ValueError(f"No se pudo parsear la función g(x): '{expr_str}'")
    
    g = sp.lambdify(x, expr, modules=["math"])
    return g, expr


def buscar_raiz_punto_fijo(g, x0: float, tol: float, max_iter: int):
    """
    Implementación del método de Punto Fijo iterando x_{i+1} = g(x_i).
    """
    iteraciones = []
    x = x0

    for i in range(1, max_iter + 1):
        try:
            x_new = g(x)
        except Exception as e:
            raise ValueError(f"Error al evaluar g(x) en x={x}: {e}")

        error = abs(x_new - x)

        iteraciones.append({
            "n": i,
            "x": x_new,
            "error": error
        })

        if error < tol:
            return {
                "raiz": x_new,
                "n_iteraciones": i,
                "error_final": error,
                "convergido": True,
                "iteraciones": iteraciones
            }
            
        # Detección de divergencia rápida (si el valor explota)
        if abs(x_new) > 1e100:
            return {
                "raiz": x_new,
                "n_iteraciones": i,
                "error_final": error,
                "convergido": False,
                "iteraciones": iteraciones,
                "mensaje": "El método divergió."
            }

        x = x_new

    # No convergió
    return {
        "raiz": x,
        "n_iteraciones": max_iter,
        "error_final": error,
        "convergido": False,
        "iteraciones": iteraciones
    }


@punto_fijo_bp.route("/punto_fijo", methods=["POST"])
def endpoint_punto_fijo():
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "Body JSON inválido o vacío."}), 400

    # ── Validar campos requeridos ────────────────────────────────────────────
    requeridos = ["funcion", "x0"]
    for campo in requeridos:
        if campo not in data:
            return jsonify({"error": f"Falta el campo '{campo}'."}), 400

    funcion_str = str(data["funcion"]).strip()

    try:
        x0 = float(data["x0"])
    except (TypeError, ValueError):
        return jsonify({"error": "'x0' debe ser un número flotante."}), 400

    tol = float(data.get("tolerancia", 1e-6))
    max_iter = int(data.get("max_iter", 100))

    if max_iter <= 0:
        return jsonify({"error": "'max_iter' debe ser un entero positivo."}), 400
    if tol <= 0:
        return jsonify({"error": "'tolerancia' debe ser un número positivo."}), 400

    # ── Parsear y ejecutar ───────────────────────────────────────────────────
    try:
        g, _ = _parsear_funcion(funcion_str)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    try:
        resultado = buscar_raiz_punto_fijo(g, x0, tol, max_iter)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    return jsonify(resultado), 200
