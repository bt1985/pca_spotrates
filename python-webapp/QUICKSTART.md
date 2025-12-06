# Quick Start Guide - PCA Yield Curve Tool

Schritt-für-Schritt-Anleitung zum lokalen Ausführen der Anwendung.

---

## 🚀 Lokale Entwicklung (5 Minuten)

### 1. Prerequisites installieren

**Python 3.9+ erforderlich:**
```bash
python3 --version
# Erwartete Ausgabe: Python 3.9.0 oder höher
```

Falls Python fehlt: [Download hier](https://www.python.org/downloads/)

### 2. Repository klonen (falls noch nicht vorhanden)
```bash
git clone https://github.com/bt1985/pca_spotrates.git
cd pca_spotrates/python-webapp
```

**Oder** navigiere zum bestehenden Verzeichnis:
```bash
cd /pfad/zu/pca_spotrates/python-webapp
```

### 3. Virtual Environment erstellen (empfohlen)

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**✅ Erfolgreich:** Du siehst nun `(venv)` vor deinem Prompt.

### 4. Dependencies installieren
```bash
pip install -r requirements.txt
```

**Installiert werden:**
- Flask (Web-Framework)
- Flask-Caching (Caching-System)
- scikit-learn (PCA-Algorithmus)
- pandas, numpy (Datenverarbeitung)
- plotly (Visualisierungen)
- openpyxl (Excel-Export)

**Dauer:** ~1-2 Minuten

### 5. App starten

**🎭 DEMO-MODUS (empfohlen für lokales Testen):**
```bash
DEMO_MODE=true python app.py
```

**Oder mit ECB API (benötigt Internet):**
```bash
python app.py
```

**Erwartete Ausgabe:**
```
INFO:services.ecb_api:🎭 DEMO MODE: Using sample data instead of ECB API
INFO:__main__:Starting Flask application in DEMO mode
 * Running on http://127.0.0.1:5000
```

### 6. Browser öffnen

✅ **Öffnen Sie http://localhost:5000 im Browser!**

**Im Demo-Modus sehen Sie:**
- Blaues "DEMO MODE" Badge oben rechts
- Vollständig funktionsfähige Anwendung mit 730 Tagen Beispieldaten

### 7. Erste Analyse durchführen

**Schritt-für-Schritt:**

1. **Startdatum eingeben:** `2022-01-01`
2. **Enddatum eingeben:** `2022-12-31`
3. **(Optional) Advanced Options öffnen:**
   - Number of PCs: `5` (Standard)
   - Stress Quantile: `0.995` (99.5%)
   - Rolling Window: `24` Monate
4. **Klick auf "Analyze"**
5. **Warten:** 2-5 Sekunden Ladezeit

**✅ Erwartetes Ergebnis:**

Sie sehen **5 interaktive Visualisierungen:**
1. **Yield Curve Evolution** - 3D-Darstellung der Zinskurvenentwicklung
2. **Principal Components** - Faktorladungen (Level, Slope, Curvature)
3. **Explained Variance** - Scree Plot (PC1 ~96%, PC2 ~3%, PC3 <1%)
4. **Stressed PC Scores** - Scatter Plot der gestressten Faktoren
5. **Stress Scenarios** - Heatmap der 99.5%-Quantil-Szenarien

**Daten exportieren:**
- **📄 Export CSV** - Rohe Zinskurvendaten (55KB, 33 Spalten)
- **📊 Export Excel** - Vollständige Analyse mit 5 Sheets (52KB)

---

## 🎭 Demo-Modus vs. ECB API

### Demo-Modus (DEMO_MODE=true)
**Vorteile:**
- ✅ Keine Internetverbindung erforderlich
- ✅ Sofort einsatzbereit
- ✅ Funktioniert hinter Firewalls/Proxies
- ✅ 730 Tage realistische Daten (2022-2023)
- ✅ Alle Features verfügbar

**Beispieldaten:**
- Zeitraum: 2022-01-01 bis 2023-12-31
- Datei: `demo_data/sample_yield_curve.csv`
- Laufzeiten: 32 Maturitäten (3M bis 30Y)
- Eigenschaften: Realistische Level-, Slope-, Curvature-Faktoren

### ECB API-Modus (DEMO_MODE=false)
**Vorteile:**
- ✅ Echte aktuelle Daten
- ✅ Beliebige Zeiträume seit 2004
- ✅ Automatische Updates

**Voraussetzungen:**
- Internetverbindung
- Zugriff auf ECB Statistical Data Warehouse
- Keine Firewall-Blockierung

**.env-Datei erstellen:**
```bash
cp .env.example .env
# Bearbeite .env:
DEMO_MODE=false
FLASK_SECRET_KEY=dein-geheimer-schluessel
CACHE_TIMEOUT=3600
```

---

## ⚡ Schnellstart (Ein Befehl)

**Linux/Mac:**
```bash
cd python-webapp && \
python3 -m venv venv && \
source venv/bin/activate && \
pip install -r requirements.txt && \
DEMO_MODE=true python app.py
```

**Windows PowerShell:**
```powershell
cd python-webapp; python -m venv venv; .\venv\Scripts\activate; pip install -r requirements.txt; $env:DEMO_MODE="true"; python app.py
```

Dann Browser öffnen: http://localhost:5000

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

### Unit & Integration Tests
```bash
# Pytest installieren
pip install pytest pytest-cov

# Alle Tests ausführen
pytest

# Mit Coverage-Report
pytest --cov=. --cov-report=html
```

**Erwartete Ergebnisse:**
- ✅ 113/113 Tests bestanden
- ✅ Coverage: ~88%

### API-Endpunkte manuell testen

**Health Check:**
```bash
curl http://localhost:5000/api/health
```
Erwartete Antwort:
```json
{
  "status": "healthy",
  "demo_mode": true,
  "cache_enabled": true
}
```

**Analyse durchführen:**
```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"start_date":"2022-01-01","end_date":"2022-12-31"}'
```

**Cache leeren:**
```bash
curl -X POST http://localhost:5000/api/cache/clear
```

### Browser-Test (Manuell)
1. Browser öffnen: http://localhost:5000
2. Start Date: `2022-01-01`
3. End Date: `2022-12-31`
4. Klick auf "Analyze"
5. Prüfen Sie die 5 Visualisierungen
6. Teste CSV-Export
7. Teste Excel-Export

---

## 🐛 Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'flask'"
**Lösung:** Dependencies neu installieren
```bash
# Virtuelle Umgebung aktivieren
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Dependencies installieren
pip install -r requirements.txt
```

### Problem: Port 5000 bereits belegt
**Symptom:** `OSError: [Errno 48] Address already in use`

**Lösung 1:** Anderen Port verwenden
```bash
# In app.py ändern (Zeile ~250):
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)  # Statt 5000
```

**Lösung 2:** Prozess beenden
```bash
# Linux/Mac
lsof -ti:5000 | xargs kill -9

# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### Problem: ECB API-Fehler (Proxy/Timeout)
**Symptom:** `HTTPSConnectionPool: Max retries exceeded`

**Lösung:** Wechsel zum Demo-Modus
```bash
DEMO_MODE=true python app.py
```

**Oder** `.env`-Datei erstellen:
```bash
echo "DEMO_MODE=true" > .env
python app.py
```

### Problem: "Permission denied" beim Installieren
**Lösung 1:** Virtuelle Umgebung verwenden (empfohlen)
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Lösung 2:** User-Installation
```bash
pip install --user -r requirements.txt
```

### Problem: Visualisierungen werden nicht angezeigt
**Mögliche Ursachen:**
1. JavaScript-Fehler → F12 → Console prüfen
2. Plotly CDN blockiert → Internet/Firewall prüfen
3. Veralteter Browser → Chrome/Firefox aktualisieren

**Lösung:**
```bash
# Browser-Cache leeren: Ctrl+Shift+Del
# Oder Inkognito-Modus verwenden
```

### Problem: "No module named 'app'"
**Lösung:** Richtiges Verzeichnis prüfen
```bash
pwd  # Zeigt aktuelles Verzeichnis
ls app.py  # Sollte app.py anzeigen

# Falls nicht im richtigen Verzeichnis:
cd /pfad/zu/pca_spotrates/python-webapp
```

### Problem: Excel-Export schlägt fehl
**Symptom:** `ModuleNotFoundError: No module named 'openpyxl'`

**Lösung:**
```bash
pip install openpyxl
```

### Problem: Demo-Daten fehlen
**Symptom:** `FileNotFoundError: demo_data/sample_yield_curve.csv`

**Lösung:** Demo-Daten neu generieren
```bash
cd demo_data
python generate_demo_data.py
cd ..
```

### Problem: Cache funktioniert nicht
**Lösung:** Cache manuell leeren
```bash
curl -X POST http://localhost:5000/api/cache/clear
```

**Oder** App neu starten
```bash
# Ctrl+C im Terminal
DEMO_MODE=true python app.py
```

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

## ✅ Checkliste für erfolgreiches Setup

Folgende Schritte sollten alle funktioniert haben:

- [ ] Python 3.9+ installiert und Version geprüft
- [ ] Repository geklont oder Verzeichnis vorhanden
- [ ] Virtuelle Umgebung erstellt (`venv/`)
- [ ] Virtuelle Umgebung aktiviert (zeigt `(venv)` im Prompt)
- [ ] Dependencies installiert (keine Fehler bei `pip install`)
- [ ] App erfolgreich gestartet (zeigt "Running on http://127.0.0.1:5000")
- [ ] Demo-Modus aktiv (sieht "DEMO MODE" im Log)
- [ ] Browser öffnet http://localhost:5000
- [ ] Webseite lädt erfolgreich
- [ ] Demo-Badge sichtbar (oben rechts)
- [ ] Erste Analyse durchgeführt (2022-01-01 bis 2022-12-31)
- [ ] 5 Visualisierungen werden angezeigt
- [ ] CSV-Export funktioniert
- [ ] Excel-Export funktioniert

**Wenn alle Punkte ✅ sind: Herzlichen Glückwunsch! 🎉**

Die Anwendung läuft erfolgreich lokal.

---

## 🎯 Nächste Schritte

**Nach erfolgreichem lokalem Setup:**

1. **📖 Dokumentation lesen**
   - [DEPLOYMENT.md](DEPLOYMENT.md) für Netcup-Deployment
   - [README.md](README.md) für Projekt-Übersicht
   - [UI_TEST_REPORT.md](UI_TEST_REPORT.md) für Test-Details

2. **🔧 Konfiguration anpassen**
   - Siehe [.env.example](.env.example) für alle 30+ Optionen
   - Cache-Timeout, PCA-Parameter, Stress-Quantile anpassen

3. **🌐 Auf Netcup deployen**
   - `.env`-Datei mit Produktions-Settings erstellen
   - `.htaccess` aus `.htaccess.example` kopieren
   - Files via FTP/SFTP hochladen
   - Passenger konfigurieren

4. **📊 Echte ECB-Daten nutzen**
   - `DEMO_MODE=false` setzen
   - ECB API-Zugriff sicherstellen
   - Längere Zeiträume testen (2004-heute)

5. **🧪 Tests erweitern**
   - Eigene Test-Szenarien hinzufügen
   - Code-Coverage verbessern
   - Load-Testing durchführen

---

## 💡 Pro-Tipps

### Entwicklung mit Auto-Reload
```bash
# Flask Debug Mode aktivieren
export FLASK_DEBUG=1  # Linux/Mac
set FLASK_DEBUG=1     # Windows CMD
$env:FLASK_DEBUG=1    # Windows PowerShell

DEMO_MODE=true python app.py
```
✨ Änderungen an Python-Files werden automatisch erkannt und die App neu geladen.

### Performance optimieren
- **Kürzere Zeiträume:** 1-2 Jahre statt 10+ Jahre
- **Weniger PCs:** 3 statt 5 (schnellere Berechnung)
- **Cache aktivieren:** Wiederholte Analysen nutzen gecachte Ergebnisse
- **Rolling Window reduzieren:** 12 statt 24 Monate

### Produktions-Konfiguration
```bash
# .env für Produktion
DEMO_MODE=false
FLASK_SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
CACHE_TIMEOUT=7200  # 2 Stunden
LOG_LEVEL=WARNING
```

### Eigene Demo-Daten erstellen
```bash
cd demo_data
python generate_demo_data.py

# Parameter anpassen in generate_demo_data.py:
# - n_days (Standard: 730)
# - Volatilität
# - Base-Zinssätze
```

### Verzeichnisstruktur verstehen
```
python-webapp/
├── app.py              # ⭐ Hauptanwendung (hier starten)
├── config.py           # Konfiguration
├── requirements.txt    # Dependencies
├── .env.example       # Beispiel-Konfiguration
├── services/          # Business Logic
│   ├── ecb_api.py     # Datenbeschaffung
│   ├── pca_analysis.py # PCA-Algorithmus
│   └── stress_scenarios.py # Stress-Testing
├── templates/
│   └── index.html     # Web-UI
├── demo_data/
│   ├── sample_yield_curve.csv  # 730 Tage Daten
│   └── generate_demo_data.py   # Generator
└── tests/             # 113 Tests (88% Coverage)
```

---

## 📞 Hilfe & Support

**Bei Problemen:**

1. **Logs prüfen:** Flask gibt detaillierte Fehlermeldungen im Terminal
2. **Health Check:** `curl http://localhost:5000/api/health`
3. **Browser-Konsole:** F12 → Console (für JavaScript-Fehler)
4. **Demo-Daten:** `head demo_data/sample_yield_curve.csv`
5. **Dokumentation:** [DEPLOYMENT.md](DEPLOYMENT.md) oder [README.md](README.md)

**Häufige Fehlerquellen:**

- ❌ Virtuelle Umgebung nicht aktiviert → `source venv/bin/activate`
- ❌ Falsches Verzeichnis → `cd python-webapp`
- ❌ Dependencies fehlen → `pip install -r requirements.txt`
- ❌ Port belegt → Anderen Port verwenden oder Prozess beenden
- ❌ ECB API blockiert → `DEMO_MODE=true` nutzen

---

**Viel Erfolg! 🎉**

Bei Fragen: Siehe [DEPLOYMENT.md](DEPLOYMENT.md) oder erstellen Sie ein GitHub Issue.
