"""
api/app.py
──────────
API REST modular para Métodos Numéricos.
Estructura pensada para agregar métodos fácilmente.

Instalación:
    pip install flask flask-cors sympy

Uso:
    python app.py

Agregar un método nuevo:
    1. Crear api/methods/nuevo_metodo.py  (implementar función + schema de validación)
    2. Registrar el blueprint en app.py   (una sola línea)
"""

from flask import Flask
from flask_cors import CORS
from methods.biseccion import biseccion_bp
from methods.gauss import gauss_bp
from methods.gauss_jordan import gauss_jordan_bp
from methods.thomas import thomas_bp
from methods.trapecios import trapecios_bp
from methods.simpson_1_3 import simpson_1_3_bp
from methods.simpson_3_8 import simpson_3_8_bp
from methods.romberg import romberg_bp
from methods.jacobi import jacobi_bp
from methods.condicion import condicion_bp
from methods.falsa_posicion import falsa_posicion_bp
from methods.punto_fijo import punto_fijo_bp
# from methods.newton_raphson import newton_raphson_bp

app = Flask(__name__)
CORS(app)  # permite requests desde el frontend

# ─── Registrar blueprints ───────────────────────────────────────────────────
app.register_blueprint(biseccion_bp,      url_prefix="/api")
app.register_blueprint(gauss_bp,          url_prefix="/api")
app.register_blueprint(gauss_jordan_bp,   url_prefix="/api")
app.register_blueprint(thomas_bp,         url_prefix="/api")
app.register_blueprint(trapecios_bp,      url_prefix="/api")
app.register_blueprint(simpson_1_3_bp,    url_prefix="/api")
app.register_blueprint(simpson_3_8_bp,    url_prefix="/api")
app.register_blueprint(romberg_bp,        url_prefix="/api")
app.register_blueprint(jacobi_bp,         url_prefix="/api")
app.register_blueprint(condicion_bp,      url_prefix="/api")
app.register_blueprint(falsa_posicion_bp, url_prefix="/api")
app.register_blueprint(punto_fijo_bp,     url_prefix="/api")
# app.register_blueprint(newton_raphson_bp, url_prefix="/api")

# ─── Health check ───────────────────────────────────────────────────────────
@app.route("/api/ping")
def ping():
    return {"status": "ok", "metodos_disponibles": ["biseccion"]}

if __name__ == "__main__":
    app.run(debug=True, port=5000)
