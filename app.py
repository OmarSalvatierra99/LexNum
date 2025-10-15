from flask import Flask, render_template, request, send_file, jsonify
import pandas as pd
from num2words import num2words
from io import BytesIO
import unicodedata, re

app = Flask(__name__)

def _normalize_text(s: str) -> str:
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower().strip()
    s = re.sub(r"\s+", "", s)
    return s

def _find_num_col(df: pd.DataFrame) -> str | None:
    allowed = {"numero", "num"}
    for col in df.columns:
        if _normalize_text(col) in allowed:
            return col
    return None

def _clean_number(value) -> float:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        raise ValueError("valor vacío")
    s = str(value).strip()
    s = s.replace(",", "")
    s = s.replace("$", "")
    s = s.replace("MXN", "").replace("M.N.", "").replace("MN", "")
    return float(s)

def numero_a_texto(valor):
    try:
        n = _clean_number(valor)
    except Exception:
        return ""
    parte_entera = int(n)
    parte_decimal = round((n - parte_entera) * 100)
    texto_entero = num2words(parte_entera, lang="es").upper()
    texto_entero = (texto_entero
                    .replace(" UNO ", " UN ")
                    .replace("UNO ", "UN ")
                    .replace(" UNO", " UN"))
    texto_decimal = f"{parte_decimal:02d}/100 M.N."
    if parte_entera == 1:
        return f"UN PESO {texto_decimal}"
    return f"{texto_entero} PESOS {texto_decimal}"

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

    col = _find_num_col(df)
    if not col:
        return jsonify({
            "error": "La columna de números no se encontró. "
                     "Use una columna llamada: Número, Numero, numero, NUMERO, Num, num."
        }), 400

    df["Texto"] = df[col].apply(numero_a_texto)

    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    buf.seek(0)

    return send_file(
        buf,
        as_attachment=True,
        download_name="resultado_lexnum.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4055, debug=True)

