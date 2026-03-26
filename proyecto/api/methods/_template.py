"""
api/methods/_template.py
────────────────────────
Plantilla para agregar un método numérico nuevo.

Pasos:
  1. Copiá este archivo y renombralo: ej. newton_raphson.py
  2. Completá los TODO: implementá el algoritmo y el endpoint.
  3. En app.py, importá el blueprint y registralo con:
       app.register_blueprint(nuevo_bp, url_prefix="/api")

Convenio de nombres:
  - Blueprint : <nombre>_bp
  - Endpoint  : /api/<nombre>   (POST)
  - Función   : def <nombre>(...)
"""

from flask import Blueprint, request, jsonify
import sympy as sp

# TODO: cambiar "template" por el nombre real del método
template_bp = Blueprint("template", __name__)


def _parsear_funcion(expr_str: str):
    """Reutilizá o importá esta utilidad desde un módulo compartido."""
    x = sp.Symbol("x")
    expr = sp.sympify(expr_str, locals={"x": x})
    return sp.lambdify(x, expr, modules=["math"]), expr


def mi_metodo(f, *args, **kwargs):
    """
    TODO: Implementar el algoritmo.
    
    Parámetros
    ----------
    f : callable
    ...

    Retorna
    -------
    dict con: raiz, n_iteraciones, error_final, f_raiz, convergido, iteraciones
    """
    raise NotImplementedError("Implementá el método aquí.")


@template_bp.route("/template", methods=["POST"])  # TODO: cambiar ruta
def endpoint_template():
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "Body JSON inválido."}), 400

    # TODO: validar los campos necesarios para tu método
    funcion_str = str(data.get("funcion", "")).strip()
    if not funcion_str:
        return jsonify({"error": "Falta el campo 'funcion'."}), 400

    try:
        f, _ = _parsear_funcion(funcion_str)
        resultado = mi_metodo(f)  # TODO: pasar los parámetros correctos
    except NotImplementedError:
        return jsonify({"error": "Método no implementado aún."}), 501
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    return jsonify(resultado), 200
