"""
api/methods/simpson_1_3.py
──────────────────────────
Método de Simpson 1/3 como Blueprint de Flask.

Endpoint:
    POST /api/simpson_1_3

Body JSON:
    {
        "funcion":    "sin(x)", // expresión en Python/SymPy
        "a":          0.0,      // límite inferior de integración
        "b":          3.14159,  // límite superior de integración
        "n":          10        // número de subintervalos (debe ser par)
    }

Respuesta exitosa:
    {
        "integral":      2.0,
        "n_intervalos":  10,
        "h":             0.314159,
        "puntos": [
            { "i": 0, "x": 0.0, "fx": 0.0, "coef": 1 },
            ...
        ]
    }

Error:
    { "error": "descripción del problema" }
"""

from flask import Blueprint, request, jsonify
import sympy as sp

simpson_1_3_bp = Blueprint("simpson_1_3", __name__)


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


def regla_simpson_1_3(f, a: float, b: float, n: int):
    """
    Implementación del método de Simpson 1/3 compuesto.
    
    Parámetros
    ----------
    f : callable — función a integrar
    a : float    — límite inferior
    b : float    — límite superior
    n : int      — número de subintervalos (debe ser par)
    
    Retorna
    -------
    dict con el valor de la integral, h, y los puntos evaluados.
    """
    if n <= 0 or n % 2 != 0:
        raise ValueError("El número de intervalos 'n' debe ser mayor a 0 y ser un número par.")
        
    h = (b - a) / n
    puntos = []
    
    fa = f(a)
    fb = f(b)
    
    puntos.append({"i": 0, "x": a, "fx": fa, "coef": 1})
    
    suma_impares = 0.0
    suma_pares = 0.0
    
    for i in range(1, n):
        xi = a + i * h
        fxi = f(xi)
        if i % 2 == 1:
            suma_impares += fxi
            puntos.append({"i": i, "x": xi, "fx": fxi, "coef": 4})
        else:
            suma_pares += fxi
            puntos.append({"i": i, "x": xi, "fx": fxi, "coef": 2})
            
    puntos.append({"i": n, "x": b, "fx": fb, "coef": 1})
    
    integral = (h / 3.0) * (fa + 4 * suma_impares + 2 * suma_pares + fb)
    
    return {
        "integral": integral,
        "n_intervalos": n,
        "h": h,
        "puntos": puntos
    }


@simpson_1_3_bp.route("/simpson_1_3", methods=["POST"])
def endpoint_simpson_1_3():
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

    if n <= 0 or n % 2 != 0:
        return jsonify({"error": "'n' debe ser un número entero par mayor a 0."}), 400

    # ── Parsear y ejecutar ───────────────────────────────────────────────────
    try:
        f, _ = _parsear_funcion(funcion_str)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    try:
        resultado = regla_simpson_1_3(f, a, b, n)
    except Exception as e:
        return jsonify({"error": f"Error al evaluar la función: {e}"}), 400

    return jsonify(resultado), 200
