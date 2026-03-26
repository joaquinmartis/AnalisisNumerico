"""
api/methods/biseccion.py
────────────────────────
Método de Bisección como Blueprint de Flask.

Endpoint:
    POST /api/biseccion

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
            { "n": 1, "a": 1.0, "b": 2.0, "c": 1.5, "fc": -0.125, "error": 0.5 },
            ...
        ]
    }

Error:
    { "error": "descripción del problema" }
"""

from flask import Blueprint, request, jsonify
import sympy as sp

biseccion_bp = Blueprint("biseccion", __name__)


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


def biseccion(f, a: float, b: float, tolerancia: float = 1e-6, max_iter: int = 100):
    """
    Implementación del método de bisección.
    
    Parámetros
    ----------
    f          : callable — función continua
    a, b       : float    — extremos del intervalo (f(a)*f(b) < 0)
    tolerancia : float    — ancho mínimo del intervalo para detener
    max_iter   : int      — máximo de iteraciones

    Retorna
    -------
    dict con raíz, iteraciones, error, etc.
    """
    fa = f(a)
    fb = f(b)

    if fa * fb > 0:
        raise ValueError(
            f"f(a) y f(b) tienen el mismo signo: "
            f"f({a}) = {fa:.6g}, f({b}) = {fb:.6g}. "
            "No se puede garantizar una raíz en el intervalo."
        )

    iteraciones = []
    convergido = False

    for n in range(1, max_iter + 1):
        c  = (a + b) / 2.0
        fc = f(c)
        error = (b - a) / 2.0

        iteraciones.append({
            "n":     n,
            "a":     round(a,  12),
            "b":     round(b,  12),
            "c":     round(c,  12),
            "fc":    fc,
            "error": error,
        })

        # Criterio de parada
        if abs(fc) < 1e-15 or error < tolerancia:
            convergido = True
            break

        # Actualizar intervalo
        if fa * fc < 0:
            b  = c
            fb = fc
        else:
            a  = c
            fa = fc

    return {
        "raiz":          c,
        "n_iteraciones": n,
        "error_final":   error,
        "f_raiz":        fc,
        "convergido":    convergido,
        "iteraciones":   iteraciones,
    }


@biseccion_bp.route("/biseccion", methods=["POST"])
def endpoint_biseccion():
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "Body JSON inválido o vacío."}), 400

    # ── Validar campos requeridos ────────────────────────────────────────────
    requeridos = ["funcion", "a", "b"]
    for campo in requeridos:
        if campo not in data:
            return jsonify({"error": f"Falta el campo '{campo}'."}), 400

    funcion_str = str(data["funcion"]).strip()
    tolerancia  = float(data.get("tolerancia", 1e-6))
    max_iter    = int(data.get("max_iter", 100))

    try:
        a = float(data["a"])
        b = float(data["b"])
    except (TypeError, ValueError):
        return jsonify({"error": "'a' y 'b' deben ser números."}), 400

    if a >= b:
        return jsonify({"error": "'a' debe ser estrictamente menor que 'b'."}), 400

    if tolerancia <= 0:
        return jsonify({"error": "La tolerancia debe ser un número positivo."}), 400

    if not (1 <= max_iter <= 10000):
        return jsonify({"error": "max_iter debe estar entre 1 y 10000."}), 400

    # ── Parsear y ejecutar ───────────────────────────────────────────────────
    try:
        f, _ = _parsear_funcion(funcion_str)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    try:
        resultado = biseccion(f, a, b, tolerancia, max_iter)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except ZeroDivisionError:
        return jsonify({"error": "División por cero al evaluar f(x)."}), 400
    except Exception as e:
        return jsonify({"error": f"Error al evaluar la función: {e}"}), 400

    return jsonify(resultado), 200
