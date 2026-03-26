# Métodos Numéricos — Guía del proyecto

## Estructura

```
proyecto/
├── index.html              ← Índice de todos los métodos
├── biseccion.html          ← Página del método de bisección
├── [metodo].html           ← Agregar una página por método nuevo
│
└── api/
    ├── app.py              ← Servidor Flask (punto de entrada)
    ├── requirements.txt
    └── methods/
        ├── _template.py    ← Plantilla para métodos nuevos
        ├── biseccion.py    ← Método de bisección
        ├── falsa_posicion.py   (próximamente)
        └── newton_raphson.py   (próximamente)
```

---

## Setup

```bash
cd api
pip install flask flask-cors sympy
python app.py
```

El servidor arranca en `http://localhost:5000`.

---

## Agregar un método nuevo

### 1. Backend (API)

Copiá `api/methods/_template.py` con el nombre del nuevo método:

```bash
cp api/methods/_template.py api/methods/newton_raphson.py
```

Implementá el algoritmo y el endpoint POST `/api/newton_raphson`.

Registrá el blueprint en `api/app.py`:

```python
from methods.newton_raphson import newton_raphson_bp
app.register_blueprint(newton_raphson_bp, url_prefix="/api")
```

### 2. Frontend

Copiá `biseccion.html` como base para la nueva página.
Actualizá el formulario con los campos específicos del método.
Cambiá `API_URL` al nuevo endpoint.

### 3. Índice

En `index.html`, agregá una nueva card en la categoría correspondiente:

```html
<a href="newton_raphson.html" class="method-card">
  <div class="card-top">
    <span class="method-index">#003</span>
    <span class="status-badge ready">Disponible</span>
  </div>
  <div class="method-icon">∂</div>
  <div class="method-name">Newton-Raphson</div>
  <div class="method-desc">...</div>
  <div class="method-tags">
    <span class="tag">derivada</span>
  </div>
</a>
```

---

## Formato de respuesta esperado

Todos los métodos deben retornar JSON con esta estructura:

```json
{
  "raiz":          1.5213797,
  "n_iteraciones": 20,
  "error_final":   4.77e-7,
  "f_raiz":        1.23e-9,
  "convergido":    true,
  "iteraciones": [
    { "n": 1, "a": 1.0, "b": 2.0, "c": 1.5, "fc": -0.125, "error": 0.5 }
  ]
}
```

En caso de error:

```json
{ "error": "descripción del problema" }
```

---

## Ejemplos de uso de la API

```bash
# Bisección: f(x) = x³ - x - 2 en [1, 2]
curl -X POST http://localhost:5000/api/biseccion \
  -H "Content-Type: application/json" \
  -d '{"funcion": "x**3 - x - 2", "a": 1, "b": 2, "tolerancia": 1e-8}'
```

---

## Funciones soportadas en f(x)

Usá sintaxis de Python/SymPy:

| Operación   | Sintaxis        |
|-------------|-----------------|
| Potencia    | `x**2`          |
| Exponencial | `exp(x)`        |
| Logaritmo   | `log(x)`        |
| Raíz        | `sqrt(x)`       |
| Seno/Coseno | `sin(x)`, `cos(x)` |
| Valor abs   | `Abs(x)`        |

## Arrancar api

```bash
cd api
pip install -r requirements.txt
python app.py
```
La api corre en http://localhost:5000/
