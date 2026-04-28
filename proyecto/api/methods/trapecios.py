"""
api/methods/trapecios.py
────────────────────────
Método de Trapecios como Blueprint de Flask.

Endpoint:
    POST /api/trapecios

Body JSON:
    {
        "funcion":    "sin(x)", // expresión en Python/SymPy
        "a":          0.0,      // límite inferior de integración
        "b":          3.14159,  // límite superior de integración
        "n":          10        // número de trapecios / subintervalos
    }

Respuesta exitosa:
    {
        "integral":      2.0,
        "n_intervalos":  10,
        "h":             0.314159,
        "puntos": [
            { "i": 0, "x": 0.0, "fx": 0.0 },
            ...
        ]
    }

Error:
    { "error": "descripción del problema" }
"""

from flask import Blueprint, request, jsonify
import sympy as sp

trapecios_bp = Blueprint("trapecios", __name__)


def _parsear_funcion(expr_str: str):
    """
    Convierte un string como 'sin(x)' en una función Python callable.
    Usa sympy para parsear de forma segura.
    """
    x = sp.Symbol("x")
    try:
        expr = sp.sympify(expr_str, locals={"x": x})
    except Exception:
        raise ValueError(f"No se pudo parsear la función: '{expr_str}'")
    
    f = sp.lambdify(x, expr, modules=["math"])
    return f, expr


def regla_trapecios(f, a: float, b: float, n: int):
    """
    Implementación del método de los trapecios compuesto.
    
    Parámetros
    ----------
    f : callable — función a integrar
    a : float    — límite inferior
    b : float    — límite superior
    n : int      — número de subintervalos
    
    Retorna
    -------
    dict con el valor de la integral, h, y los puntos evaluados.
    """
    if n <= 0:
        raise ValueError("El número de intervalos 'n' debe ser mayor a 0.")
        
    h = (b - a) / n
    suma = 0.0
    puntos = []
    
    # Evaluar en los extremos
    fa = f(a)
    fb = f(b)
    
    puntos.append({"i": 0, "x": a, "fx": fa})
    
    # Evaluar los puntos intermedios
    for i in range(1, n):
        xi = a + i * h
        fxi = f(xi)
        suma += fxi
        puntos.append({"i": i, "x": xi, "fx": fxi})
        
    puntos.append({"i": n, "x": b, "fx": fb})
    
    integral = (h / 2.0) * (fa + 2 * suma + fb)
    
    return {
        "integral": integral,
        "n_intervalos": n,
        "h": h,
        "puntos": puntos
    }


@trapecios_bp.route("/trapecios", methods=["POST"])
def endpoint_trapecios():
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "Body JSON inválido o vacío."}), 400

    # ── Validar campos requeridos ────────────────────────────────────────────
    requeridos = ["funcion", "a", "b", "n"]
    for campo in requeridos:
        if campo not in data:
            return jsonify({"error": f"Falta el campo '{campo}'."}), 400

    funcion_str = str(data["funcion"]).strip()

    try:
        a = float(data["a"])
        b = float(data["b"])
        n = int(data["n"])
    except (TypeError, ValueError):
        return jsonify({"error": "'a' y 'b' deben ser números flotantes, 'n' debe ser un entero."}), 400

    if a >= b:
        return jsonify({"error": "'a' (límite inferior) debe ser estrictamente menor que 'b' (límite superior)."}), 400

    if n <= 0:
        return jsonify({"error": "'n' debe ser un número entero mayor a 0."}), 400

    # ── Parsear y ejecutar ───────────────────────────────────────────────────
    try:
        f, _ = _parsear_funcion(funcion_str)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    try:
        resultado = regla_trapecios(f, a, b, n)
    except Exception as e:
        return jsonify({"error": f"Error al evaluar la función: {e}"}), 400

    return jsonify(resultado), 200
