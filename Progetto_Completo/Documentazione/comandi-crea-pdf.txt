# 1. Crea l'ambiente virtuale (es. chiamato .venv)
python3 -m venv .venv

# 2. Attiva l'ambiente virtuale
source .venv/bin/activate

# 3. Installa le librerie richieste al suo interno
pip install reportlab Pillow

# 4. Esegui lo script
python3 generate_documentation_pdf.py

# 5. (Opzionale) Disattiva l'ambiente virtuale al termine
deactivate