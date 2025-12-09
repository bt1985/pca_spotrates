# PCA Yield Curve Stress Testing - Python Web App

Eine moderne Python-basierte Web-Anwendung zur Ableitung von Stressszenarien aus der Zinskurve mittels Hauptkomponentenanalyse (PCA).

## 🎯 Features

- ✅ **Automatischer Datenabruf**: Lädt Zinskurvendaten direkt von der EZB
- ✅ **Principal Component Analysis**: Reduziert Zinskurvenbewegungen auf Hauptkomponenten
- ✅ **Stress-Szenarien**: Generiert 99,5% Quantil-basierte Stressszenarien
- ✅ **Interaktive Visualisierungen**: 3D-Plots und Zeitreihenanalysen mit Plotly
- ✅ **Netcup-Ready**: Optimiert für Netcup Webhosting mit Phusion Passenger

## 🏗️ Architektur

```
Flask Web App (WSGI)
├── ECB API Service → Datenabruf von EZB
├── PCA Analyzer → scikit-learn PCA
├── Stress Generator → Rolling Quantile Berechnung
└── Plotly Visualizations → Interaktive Charts
```

## 📋 Voraussetzungen

- Python 3.9+
- Netcup Webhosting 4000/8000 (mit Python-Modul)
- Oder: Lokale Entwicklungsumgebung

## 🚀 Schnellstart (Lokal)

### 1. Repository klonen

```bash
git clone https://github.com/bt1985/pca_spotrates.git
cd pca_spotrates/python-webapp
```

### 2. Virtual Environment erstellen

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# oder
venv\Scripts\activate     # Windows
```

### 3. Dependencies installieren

```bash
pip install -r requirements.txt
```

### 4. Anwendung starten

```bash
python app.py
```

Die App läuft dann auf `http://localhost:5000`

## 📦 Deployment auf Netcup

Siehe [DEPLOYMENT.md](DEPLOYMENT.md) für detaillierte Anweisungen.

**Kurzversion**:

1. Dependencies lokal installieren und als `vendor/` hochladen
2. Alle Dateien in `pca-app/` Ordner auf Netcup hochladen
3. Im WCP Python-Modul konfigurieren:
   - App Root: `pca-app`
   - Startup: `passenger_wsgi.py`
4. App neuladen

## 🧪 Funktionalität testen

1. Öffnen Sie die App im Browser
2. Wählen Sie einen Zeitraum (z.B. 2020-01-01 bis heute)
3. Klicken Sie "Generate Stress Scenarios"
4. Analysieren Sie die generierten Plots:
   - Yield Curve Evolution (3D)
   - Principal Components (PC1-5)
   - Explained Variance
   - Stressed Scores
   - Yield Curve Stress Scenarios

## 📊 Datenquelle

**European Central Bank (ECB) Data Portal**
- Datenreihe: Euro area AAA-rated government bonds
- Laufzeiten: 3M bis 30Y (32 Maturities)
- API: https://data-api.ecb.europa.eu/
- Portal: https://data.ecb.europa.eu/

## 🔬 Methodik

### 1. Principal Component Analysis

Die Anwendung führt eine PCA auf der Zinskurve durch:

- **PC1**: Level (Niveau) - erklärt ~95% der Varianz
- **PC2**: Slope (Steigung) - erklärt ~4% der Varianz
- **PC3**: Curvature (Krümmung) - erklärt ~1% der Varianz

### 2. Stress-Szenarien

Für jede PC werden Stressszenarien generiert:

1. Berechnung rollierender Differenzen (30 Tage)
2. Trennung in positive/negative Bewegungen
3. Berechnung 99,5% Quantil (24-Monats-Fenster)
4. Anwendung auf aktuelle Scores
5. Rekonstruktion der gestressten Zinskurve

### 3. Regulatorischer Kontext

Die Methodik orientiert sich an:

- **Solvency II**: Artikel 105 (Interest Rate Risk)
- **IAIS ICS**: Stress-Szenarien für Level, Slope, Curvature
- **Quantitative Risk Management**: McNeil, Frey, Embrechts (2005)

## 📁 Projektstruktur

```
python-webapp/
├── app.py                  # Flask Hauptanwendung
├── passenger_wsgi.py       # WSGI Entry Point für Passenger
├── config.py               # Konfiguration
├── requirements.txt        # Python Dependencies
├── services/
│   ├── ecb_api.py         # ECB Datenimport
│   ├── pca_analysis.py    # PCA Implementierung
│   └── stress_scenarios.py # Stress-Szenarien Generator
├── templates/
│   └── index.html         # Frontend UI
├── static/
│   ├── css/
│   └── js/
└── tmp/                   # Passenger restart.txt
```

## 🔧 Konfiguration

Anpassen in `config.py`:

```python
# PCA Einstellungen
N_COMPONENTS = 5              # Anzahl PC
STRESS_QUANTILE = 0.995       # 99,5% Quantil
ROLLING_WINDOW_MONTHS = 24    # Rolling Window
ROLLING_UNIT_DAYS = 30        # Unit für Differenzen

# API Settings
REQUEST_TIMEOUT = 30          # ECB API Timeout
MAX_DATE_RANGE_DAYS = 3650    # Max. Zeitraum
```

## 🐛 Fehlersuche

### App startet nicht auf Netcup

1. Prüfen Sie Python-Modul im WCP (aktiviert?)
2. Modus auf "Entwicklung" → Fehlermeldungen sichtbar
3. Prüfen Sie Passenger-Logs im WCP

### ECB-Daten können nicht geladen werden

- Prüfen Sie Internetverbindung
- ECB API evtl. temporär nicht verfügbar
- Firewall-Einstellungen prüfen

### Import-Fehler

- Dependencies nicht vollständig → Siehe DEPLOYMENT.md Schritt 1
- Python-Version zu alt → Mindestens 3.9

## 📈 Performance

### Typische Response-Zeiten

- ECB API Abruf: 2-5 Sekunden
- PCA Berechnung: 0.5-2 Sekunden
- Visualisierung: 0.5-1 Sekunde
- **Gesamt**: ~5-10 Sekunden

### Caching empfohlen

Für Production-Setup siehe [DEPLOYMENT.md](DEPLOYMENT.md) Abschnitt "Performance-Optimierung"

## 🔒 Sicherheit

- ✅ HTTPS via Netcup SSL (Let's Encrypt)
- ✅ Input-Validierung für Datumsbereich
- ✅ Error-Handling für API-Fehler
- ⚠️ SECRET_KEY in Production ändern!
- 💡 Optional: Rate Limiting implementieren

## 📚 Weiterführende Literatur

- Alexander (2002): Principal component models for generating large GARCH covariance matrix
- EIOPA (2019): Opinion on the 2020 review of Solvency II
- McNeil, Frey, Embrechts (2005): Quantitative Risk Management
- Redfern, McLean (2014): Principal Component Analysis for Yield Curve Modelling

## 🤝 Vergleich zur R-Shiny App

| Feature | R-Shiny | Python-Flask |
|---------|---------|--------------|
| Datenquelle | ECB + Azure Storage | ECB direkt |
| PCA | R `prcomp` | scikit-learn |
| Visualisierung | plotly R | plotly Python |
| Deployment | shinyapps.io | Netcup Passenger |
| Dependencies | Azure Storage | Keine Cloud-Abhängigkeit |
| Performance | ⭐⭐⭐ | ⭐⭐⭐⭐ |

## 🛠️ Entwicklung

### Lokale Tests

```bash
# Unittest (optional)
pytest tests/

# Manuelle Tests
python app.py
# Öffne http://localhost:5000
```

### Code-Style

```bash
# Formatierung
black app.py services/

# Linting
flake8 app.py services/
```

## 📝 Lizenz

Apache License 2.0 - Siehe [LICENSE](../LICENSE)

## 👨‍💻 Migration von R

Diese Python-App ist eine 1:1-Portierung der R-Shiny-App mit folgenden Verbesserungen:

1. ✅ Keine Azure Storage-Abhängigkeit
2. ✅ Direkter ECB-API-Zugriff
3. ✅ Deployment auf eigenem Server (Netcup)
4. ✅ Bessere Performance
5. ✅ Einfachere Wartung

## 🔮 Geplante Erweiterungen

- [ ] Excel/CSV-Export der Stressszenarien
- [ ] Mehrere Stress-Quantile (95%, 99%, 99,5%)
- [ ] Nelson-Siegel-Modell zum Vergleich
- [ ] PC-GARCH für Volatilitätsmodellierung
- [ ] API-Endpunkte für externe Integration
- [ ] User-Management & Sessions

## 📞 Support

- **GitHub Issues**: https://github.com/bt1985/pca_spotrates/issues
- **Netcup Forum**: https://forum.netcup.de/
- **ECB API Docs**: https://data.ecb.europa.eu/help/api/overview

---

**Entwickelt mit ❤️ für Risikomanagement im Finanzsektor**
