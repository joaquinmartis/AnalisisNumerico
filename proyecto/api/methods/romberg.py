"""
api/methods/romberg.py
──────────────────────
Método de Integración de Romberg como Blueprint de Flask.

Endpoint:
    POST /api/romberg

Body JSON:
    {
        "funcion":    "sin(x)", // expresión en Python/SymPy
        "a":          0.0,      // límite inferior
        "b":          3.14159,  // límite superior
        "n":          5         // número de niveles de la tabla
    }

Respuesta exitosa:
    {
        "integral":      2.0,
        "n_niveles":     5,
        "tabla": [
            [R(1,1)],
            [R(2,1), R(2,2)],
            [R(3,1), R(3,2), R(3,3)],
            ...
        ]
    }
"""

from flask import Blueprint, request, jsonify
import sympy as sp
import math

romberg_bp = Blueprint("romberg", __name__)


def _parsear_funcion(expr_str: str):
    x = sp.Symbol("x")
    try:
        expr = sp.sympify(expr_str, locals={"x": x})
    except Exception:
        raise ValueError(f"No se pudo parsear la función: '{expr_str}'")
    
    f = sp.lambdify(x, expr, modules=["math"])
    return f, expr


def integracion_romberg(f, a: float, b: float, n: int):
    if n <= 0:
        raise ValueError("El número de niveles 'n' debe ser mayor a 0.")
        
    R = [[0.0] * n for _ in range(n)]
    
    # R(1,1): Trapecio con 1 intervalo
    h = b - a
    R[0][0] = (h / 2.0) * (f(a) + f(b))
    
    for i in range(1, n):
        # Calcular R(i, 1) usando la regla del trapecio con 2^i intervalos
        h = (b - a) / (2**i)
        
        suma = 0.0
        # Solo necesitamos evaluar los puntos intermedios nuevos
        for k in range(1, 2**(i-1) + 1):
            suma += f(a + (2*k - 1) * h)
            
        R[i][0] = 0.5 * R[i-1][0] + h * suma
        
        # Extrapolación de Richardson
        for j in range(1, i + 1):
            R[i][j] = R[i][j-1] + (R[i][j-1] - R[i-1][j-1]) / (4**j - 1)
            
    # Formatear la tabla de salida quitando los ceros extras
    tabla_out = []
    for i in range(n):
        fila = [R[i][j] for j in range(i + 1)]
        tabla_out.append(fila)
        
    return {
        "integral": R[n-1][n-1],
        "n_niveles": n,
        "tabla": tabla_out
    }


@romberg_bp.route("/romberg", methods=["POST"])
def endpoint_romberg():
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "Body JSON inválido o vacío."}), 400

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

    if not (1 <= n <= 15):
        return jsonify({"error": "'n' (niveles) debe estar entre 1 y 15 para evitar tiempos de cómputo excesivos."}), 400

    try:
        f, _ = _parsear_funcion(funcion_str)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    try:
        resultado = integracion_romberg(f, a, b, n)
    except Exception as e:
        return jsonify({"error": f"Error al evaluar la función: {e}"}), 400

    return jsonify(resultado), 200
