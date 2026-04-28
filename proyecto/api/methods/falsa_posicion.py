"""
api/methods/falsa_posicion.py
─────────────────────────────
Método de Falsa Posición (Regula Falsi) como Blueprint de Flask.

Endpoint:
    POST /api/falsa_posicion

Body JSON:
    {
        "funcion":    "x**3 - x - 2",   // expresión en Python/SymPy
        "a":          1.0,               // extremo izquierdo del intervalo
        "b":          2.0,               // extremo derecho del intervalo
        "tolerancia": 1e-6,              // criterio de parada
        "max_iter":   100                // máximo de iteraciones
    }

Respuesta exitosa:
    {
        "raiz":          1.5213797...,
        "n_iteraciones": 20,
        "error_final":   4.77e-7,
        "f_raiz":        1.23e-9,
        "convergido":    true,
        "iteraciones": [
            { "n": 1, "a": 1.0, "b": 2.0, "c": 1.5, "fc": -0.125, "error": null },
            ...
        ]
    }
"""

from flask import Blueprint, request, jsonify
import sympy as sp

falsa_posicion_bp = Blueprint("falsa_posicion", __name__)


def _parsear_funcion(expr_str: str):
    """
    Convierte un string como 'x**3 - x - 2' en una función Python callable.
    Usa sympy para parsear de forma segura.
    """
    x = sp.Symbol("x")
    try:
        expr = sp.sympify(expr_str, locals={"x": x})
    except Exception:
        raise ValueError(f"No se pudo parsear la función: '{expr_str}'")
    
    f = sp.lambdify(x, expr, modules=["math"])
    return f, expr


def buscar_raiz_falsa_posicion(f, a: float, b: float, tol: float, max_iter: int):
    """
    Implementación del método de la Falsa Posición (Regula Falsi).
    """
    if a >= b:
        raise ValueError("El valor de 'a' debe ser estrictamente menor que 'b'.")

    fa = f(a)
    fb = f(b)

    if fa * fb > 0:
        raise ValueError(f"La función no cambia de signo en el intervalo [{a}, {b}]. f(a)={fa:.4f}, f(b)={fb:.4f}")

    if fa == 0:
        return {"raiz": a, "n_iteraciones": 0, "error_final": 0, "f_raiz": 0, "convergido": True, "iteraciones": []}
    if fb == 0:
        return {"raiz": b, "n_iteraciones": 0, "error_final": 0, "f_raiz": 0, "convergido": True, "iteraciones": []}

    iteraciones = []
    c_prev = None
    c = a

    for i in range(1, max_iter + 1):
        # Fórmula de falsa posición
        c = b - (fb * (a - b)) / (fa - fb)
        fc = f(c)

        # Calcular error relativo o absoluto según convenga.
        # Aquí usamos la diferencia entre el 'c' actual y el anterior.
        error = abs(c - c_prev) if c_prev is not None else None

        iteraciones.append({
            "n": i,
            "a": a,
            "b": b,
            "c": c,
            "fc": fc,
            "error": error
        })

        if fc == 0 or (error is not None and error < tol):
            return {
                "raiz": c,
                "n_iteraciones": i,
                "error_final": error if error is not None else 0,
                "f_raiz": fc,
                "convergido": True,
                "iteraciones": iteraciones
            }

        # Actualizar intervalo
        if fa * fc < 0:
            b = c
            fb = fc
        else:
            a = c
            fa = fc

        c_prev = c

    # Si llega acá, no convergió en el máximo de iteraciones
    error_final = abs(c - c_prev) if c_prev is not None else float('inf')
    return {
        "raiz": c,
        "n_iteraciones": max_iter,
        "error_final": error_final,
        "f_raiz": f(c),
        "convergido": False,
        "iteraciones": iteraciones
    }


@falsa_posicion_bp.route("/falsa_posicion", methods=["POST"])
def endpoint_falsa_posicion():
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "Body JSON inválido o vacío."}), 400

    # ── Validar campos requeridos ────────────────────────────────────────────
    requeridos = ["funcion", "a", "b"]
    for campo in requeridos:
        if campo not in data:
            return jsonify({"error": f"Falta el campo '{campo}'."}), 400

    funcion_str = str(data["funcion"]).strip()

    try:
        a = float(data["a"])
        b = float(data["b"])
    except (TypeError, ValueError):
        return jsonify({"error": "'a' y 'b' deben ser números flotantes."}), 400

    tol = float(data.get("tolerancia", 1e-6))
    max_iter = int(data.get("max_iter", 100))

    if max_iter <= 0:
        return jsonify({"error": "'max_iter' debe ser un entero positivo."}), 400
    if tol <= 0:
        return jsonify({"error": "'tolerancia' debe ser un número positivo."}), 400

    # ── Parsear y ejecutar ───────────────────────────────────────────────────
    try:
        f, _ = _parsear_funcion(funcion_str)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    try:
        resultado = buscar_raiz_falsa_posicion(f, a, b, tol, max_iter)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    return jsonify(resultado), 200
