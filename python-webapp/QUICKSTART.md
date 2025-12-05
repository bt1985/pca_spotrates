# Quick Start Guide

## 🚀 Lokale Entwicklung (5 Minuten)

### 1. Prerequisites installieren
```bash
# Python 3.9+ erforderlich
python3 --version

# Git (falls noch nicht vorhanden)
git --version
```

### 2. Repository klonen
```bash
git clone https://github.com/bt1985/pca_spotrates.git
cd pca_spotrates/python-webapp
```

### 3. Virtual Environment erstellen
```bash
python3 -m venv venv

# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 4. Dependencies installieren
```bash
pip install -r requirements.txt
```

### 5. App starten
```bash
python app.py
```

✅ Öffnen Sie http://localhost:5000 im Browser!

---

## 🌐 Netcup Deployment (10 Minuten)

### Variante A: Automatisch mit Script

**Linux/Mac:**
```bash
./create_deployment_package.sh
```

**Windows:**
```bash
create_deployment_package.bat
```

Dies erstellt `pca-app-netcup-deployment.zip`

### Variante B: Manuell

1. **Dependencies installieren:**
```bash
pip install --target vendor -r requirements.txt
```

2. **Dateien hochladen:**
   - Alle Python-Dateien
   - `vendor/` Ordner
   - `templates/` Ordner
   - `static/` Ordner
   - `services/` Ordner

3. **Netcup WCP konfigurieren:**
   - Dashboard → Python
   - App Root: `pca-app`
   - Startup: `passenger_wsgi.py`
   - Python Version: 3.9+
   - "Konfiguration neu schreiben"
   - "Anwendung Neuladen"

✅ Ihre App läuft jetzt auf `https://ihre-domain.de`!

---

## 🧪 Testen

### Lokale Tests
```bash
python test_app.py
```

### Manueller Test
1. Öffnen Sie die App im Browser
2. Start Date: `2020-01-01`
3. End Date: Heute
4. Klick auf "Generate Stress Scenarios"
5. Prüfen Sie die 5 Visualisierungen

---

## 🐛 Troubleshooting

### Import Error
```bash
# Fehlende Dependencies
pip install -r requirements.txt
```

### Port bereits belegt
```bash
# Ändern Sie in app.py:
app.run(port=5001)  # Statt 5000
```

### ECB API Fehler
- Prüfen Sie Internetverbindung
- ECB API evtl. temporär down
- Versuchen Sie kürzeren Zeitraum

---

## 📚 Weitere Dokumentation

- **Vollständige Deployment-Anleitung**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **Projekt-Übersicht**: [README.md](README.md)
- **Original R-Code**: [../README.md](../README.md)

---

## 💡 Tipps

### Entwicklung mit Auto-Reload
```bash
# Flask Debug Mode
export FLASK_ENV=development  # Linux/Mac
set FLASK_ENV=development     # Windows
python app.py
```

### Performance verbessern
- Caching aktivieren (siehe DEPLOYMENT.md)
- Kürzere Zeiträume verwenden
- ECB-Daten lokal cachen

### Produktions-Setup
- SECRET_KEY ändern in `config.py`
- Modus auf "Produktiv" in Netcup WCP
- HTTPS aktivieren (automatisch bei Netcup)

---

**Viel Erfolg! 🎉**

Bei Problemen: Siehe [DEPLOYMENT.md](DEPLOYMENT.md) oder öffnen Sie ein GitHub Issue.
