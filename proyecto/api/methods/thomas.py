from flask import Blueprint, request, jsonify

thomas_bp = Blueprint("thomas", __name__)

def solve_thomas(a, b, c, d):
    """
    a: subdiagonal (n-1) -> la api provee n, empezando por a[1] o lo adaptamos. Usaremos longitudes:
       b: len n (diagonal principal)
       a: len n (a[0] no se usa, o si len es n-1, lo manejamos. Asumimos len(a)=n con a[0]=0)
       c: len n (c[n-1] no se usa)
       d: len n
    """
    n = len(d)
    if len(b) != n:
        raise ValueError("Longitud de 'b' incorrecta.")
    
    # Rellenamos para que tengan longitud n, el usuario puede enviar listas de distintas long.
    if len(a) == n - 1:
        a = [0.0] + a
    elif len(a) != n:
        raise ValueError("Longitud de 'a' (subdiagonal) incorrecta.")
        
    if len(c) == n - 1:
        c = c + [0.0]
    elif len(c) != n:
        raise ValueError("Longitud de 'c' (superdiagonal) incorrecta.")

    # Copiamos para no mutar original
    c_star = [0.0] * n
    d_star = [0.0] * n

    # Forward sweep
    if b[0] == 0:
        raise ValueError("El elemento b[0] es cero, el método falla.")
        
    c_star[0] = c[0] / b[0]
    d_star[0] = d[0] / b[0]

    for i in range(1, n):
        denom = b[i] - a[i] * c_star[i-1]
        if denom == 0:
            raise ValueError(f"División por cero en el paso {i}.")
        if i < n-1:
            c_star[i] = c[i] / denom
        d_star[i] = (d[i] - a[i] * d_star[i-1]) / denom

    # Back substitution
    x = [0.0] * n
    x[-1] = d_star[-1]
    for i in range(n-2, -1, -1):
        x[i] = d_star[i] - c_star[i] * x[i+1]

    return {
        "solucion": x,
        "n": n,
        "c_star": c_star,
        "d_star": d_star
    }

@thomas_bp.route("/thomas", methods=["POST"])
def endpoint_thomas():
    data = request.get_json(force=True, silent=True)
    if not data or any(k not in data for k in ("a", "b", "c", "d")):
        return jsonify({"error": "Faltan 'a', 'b', 'c' o 'd'."}), 400

    try:
        resultado = solve_thomas(data["a"], data["b"], data["c"], data["d"])
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
