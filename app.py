from flask import Flask, render_template, request, send_file, jsonify
from io import BytesIO
import pandas as pd
from utils import numero_a_texto, find_num_column

app = Flask(__name__)
app.secret_key = "lexnum-ofs-tlaxcala"
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB

# =========================================================
# Rutas principales
# =========================================================
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/convertir_texto", methods=["POST"])
def convertir_texto():
    data = request.get_json(silent=True) or {}
    numero = data.get("numero", "")
    return jsonify({"texto": numero_a_texto(numero)})

@app.route("/convertir_excel", methods=["POST"])
def convertir_excel():
    archivo = request.files.get("archivo")
    if not archivo:
        return jsonify({"error": "No se subió archivo."}), 400

    try:
        df = pd.read_excel(archivo)
    except Exception:
        return jsonify({"error": "No se pudo leer el Excel. Use .xlsx válido."}), 400

    col = find_num_column(df)
    if not col:
        return jsonify({
            "error": "Columna no encontrada. Use: Número, Numero, numero, NUMERO o Num."
        }), 400

    df["Texto"] = df[col].apply(numero_a_texto)

    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    buf.seek(0)

    # Entregar directamente el archivo al navegador
    return send_file(
        buf,
        as_attachment=True,
        download_name="resultado_lexnum.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@app.after_request
def add_headers(response):
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4055, debug=True)

