# LexNum — Institutional Numeric Converter

LexNum is a minimal, reliable web tool built for the **Superior Audit Office of Tlaxcala (OFS)** to convert numeric values into their official Spanish currency representation, individually or in bulk from Excel files. It ensures standardized financial text for institutional use.

🔗 **Live:** [https://lexnum.omar-xyz.shop](https://lexnum.omar-xyz.shop)

---

## Features
- Real-time numeric-to-text conversion (e.g., `1523.45` → `MIL QUINIENTOS VEINTITRÉS PESOS 45/100 M.N.`)
- Excel batch conversion with automatic column detection (`Número`, `Numero`, `Num`)
- Simple, responsive interface using pure HTML, CSS, and JavaScript
- Backend built with Flask, Pandas, and OpenPyXL
- Easy to deploy via Gunicorn and systemd

---

## Installation
```bash
git clone https://github.com/OmarSalvatierra99/lexnum.git
cd lexnum
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

---

## Example
```bash
Input:  1320
Output: MIL TRESCIENTOS VEINTE PESOS 00/100 M.N.
```

---

© 2025 **Omar Gabriel Salvatierra Garcia** — Institutional Software, OFS Tlaxcala

