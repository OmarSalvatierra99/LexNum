import unicodedata, re, pandas as pd
from num2words import num2words

def normalize(s):
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+", "", s).lower()

def find_num_column(df):
    for c in df.columns:
        if normalize(c) in {"numero", "num"}:
            return c
    return None

def clean_num(value):
    if value in (None, "", " "):
        return None
    s = str(value)
    s = s.replace(",", "").replace("$", "").replace("MXN", "").replace("M.N.", "").replace("MN", "").strip()
    return float(s)

def numero_a_texto(valor):
    try:
        n = clean_num(valor)
        if n is None:
            return ""
        entero = int(n)
        dec = round((n - entero) * 100)
        texto = num2words(entero, lang="es").upper()
        texto = texto.replace(" UNO ", " UN ").replace("UNO ", "UN ").replace(" UNO", " UN")
        sufijo = f"{dec:02d}/100 M.N."
        if entero == 1:
            return f"UN PESO {sufijo}"
        return f"{texto} PESOS {sufijo}"
    except Exception:
        return ""

