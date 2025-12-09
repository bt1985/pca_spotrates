# Deployment Guide für Netcup Webhosting

Diese Anleitung beschreibt Schritt für Schritt, wie die PCA Yield Curve Web-App auf Netcup Webhosting 4000/8000 mit Phusion Passenger deployt wird.

## Voraussetzungen

- ✅ Netcup Webhosting 4000 oder Webhosting 8000
- ✅ Python-Modul aktiviert (im Webhosting Control Panel)
- ✅ FTP/SFTP-Zugang oder Dateimanager im WCP

## Verzeichnisstruktur auf Netcup

```
/
├── html/                           # Document Root (leer lassen!)
├── pca-app/                        # App Root (hier die App ablegen)
│   ├── passenger_wsgi.py          # ⚠️ WICHTIG: Startup-Datei
│   ├── app.py
│   ├── config.py
│   ├── requirements.txt
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ecb_api.py
│   │   ├── pca_analysis.py
│   │   └── stress_scenarios.py
│   ├── templates/
│   │   └── index.html
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   └── tmp/                       # Wird von Passenger benötigt
└── logs/
```

## Deployment-Schritte

### Schritt 1: Dependencies installieren

⚠️ **WICHTIG**: Netcup Webhosting erlaubt keine CLI/SSH-Installation. Dependencies müssen Sie entweder:

**Option A: Lokale Installation + Upload (EMPFOHLEN)**

1. Lokal ein virtuelles Environment erstellen:
```bash
# Auf Ihrem lokalen Rechner
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# oder
venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

2. Erstellen Sie ein Deployment-Paket mit allen Dependencies:
```bash
pip install --target ./vendor -r requirements.txt
```

3. Laden Sie den `vendor/` Ordner zusammen mit der App hoch.

4. Passen Sie `passenger_wsgi.py` an:
```python
import sys
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Vendor-Pfad hinzufügen
vendor_path = os.path.join(CURRENT_DIR, 'vendor')
if vendor_path not in sys.path:
    sys.path.insert(0, vendor_path)

if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from app import app as application
```

**Option B: Netcup Support kontaktieren**

Fragen Sie den Netcup Support, ob sie pip-Installationen für Ihr Webhosting durchführen können.

### Schritt 2: Dateien hochladen

1. **Per FTP/SFTP**:
   - Verbinden Sie sich mit Ihrem Netcup Webspace
   - Erstellen Sie den Ordner `pca-app` außerhalb von `html/`
   - Laden Sie alle Dateien in `pca-app/` hoch

2. **Per Webhosting Control Panel (WCP)**:
   - Melden Sie sich im WCP an
   - Navigieren Sie zu "Dateien"
   - Erstellen Sie `pca-app/` Verzeichnis
   - Laden Sie alle Dateien hoch

### Schritt 3: Python-Modul konfigurieren

1. Melden Sie sich im **Webhosting Control Panel (WCP)** an

2. Navigieren Sie zu **Dashboard → Entwicklertools → Python**

3. Konfigurieren Sie folgende Einstellungen:

   | Einstellung | Wert |
   |-------------|------|
   | **Einschalten** | ✅ Aktivieren |
   | **App Root** | `pca-app` |
   | **Startup Datei** | `passenger_wsgi.py` |
   | **Python Version** | Neueste verfügbare (z.B. 3.11) |
   | **Modus** | Produktiv (später auf Entwicklung für Debugging) |

4. Klicken Sie auf **"Konfiguration neu schreiben"**

5. Klicken Sie auf **"Anwendung Neuladen"**

### Schritt 4: Domain/Subdomain einrichten

Die Python-App wird auf der konfigurierten Domain/Subdomain laufen.

**Option A: Subdomain** (empfohlen)
- Erstellen Sie eine Subdomain: `pca.ihre-domain.de`
- Richten Sie diese auf den App Root `pca-app` aus

**Option B: Hauptdomain**
- Konfigurieren Sie die Hauptdomain
- ⚠️ Document Root muss leer sein (keine index.html/php)

### Schritt 5: Testen

1. Öffnen Sie im Browser: `https://pca.ihre-domain.de`

2. Sie sollten die Startseite der App sehen

3. Testen Sie die Funktionalität:
   - Start Date: 2020-01-01
   - End Date: Heute
   - Klicken Sie "Generate Stress Scenarios"

### Schritt 6: Fehlersuche (Falls es nicht funktioniert)

#### Problem: "Startup-Datei existiert nicht"

**Lösung**:
- Prüfen Sie, dass `passenger_wsgi.py` im `pca-app/` Verzeichnis liegt
- Dateiname muss exakt `passenger_wsgi.py` sein (Groß-/Kleinschreibung!)
- Versuchen Sie einen anderen Browser

#### Problem: HTTP 500 Fehler

**Lösung**:
1. Setzen Sie **Modus** auf **"Entwicklung"** im WCP
2. Laden Sie die Seite neu
3. Fehlermeldungen werden jetzt angezeigt

Häufige Fehler:
- Fehlende Dependencies → Siehe Schritt 1
- Import-Fehler → Prüfen Sie `passenger_wsgi.py` Pfade
- Python-Version inkompatibel → Wählen Sie Python 3.9+

#### Problem: Seite lädt, aber API-Fehler

**Lösung**:
- Öffnen Sie Browser Developer Console (F12)
- Prüfen Sie Network-Tab für API-Fehler
- Häufig: ECB-API nicht erreichbar (Firewall?)

### Schritt 7: Neustart bei Code-Änderungen

Nach jeder Code-Änderung:

**Methode 1: WCP**
- Dashboard → Python → "Anwendung Neuladen"

**Methode 2: restart.txt**
- Erstellen/Ändern Sie die Datei `pca-app/tmp/restart.txt`
- Passenger erkennt dies automatisch und lädt neu

## Performance-Optimierung

### Caching aktivieren

Fügen Sie in `app.py` hinzu:

```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.route('/api/analyze', methods=['POST'])
@cache.cached(timeout=300, query_string=True)
def analyze():
    # ... existing code
```

### Datei-basiertes Caching für ECB-Daten

Erstellen Sie `services/cache.py`:

```python
import os
import pickle
from datetime import datetime, timedelta

CACHE_DIR = 'cache'

def get_cached_data(key, max_age_hours=24):
    cache_file = os.path.join(CACHE_DIR, f"{key}.pkl")
    if os.path.exists(cache_file):
        age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(cache_file))
        if age < timedelta(hours=max_age_hours):
            with open(cache_file, 'rb') as f:
                return pickle.load(f)
    return None

def save_cached_data(key, data):
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_file = os.path.join(CACHE_DIR, f"{key}.pkl")
    with open(cache_file, 'wb') as f:
        pickle.dump(data, f)
```

## Sicherheitshinweise

### Produktions-Secret ändern

In `config.py`:
```python
SECRET_KEY = os.environ.get('SECRET_KEY') or 'HIER-EINEN-SICHEREN-KEY-EINTRAGEN'
```

Generieren Sie einen sicheren Key:
```python
import secrets
print(secrets.token_hex(32))
```

### Rate Limiting (Optional)

Installieren Sie Flask-Limiter:
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)

@app.route('/api/analyze', methods=['POST'])
@limiter.limit("10 per minute")
def analyze():
    # ...
```

## Monitoring & Logs

### Log-Dateien auf Netcup

Passenger-Logs finden Sie in:
- WCP → Logs → Python-Application-Logs

### Eigene Logs aktivieren

In `app.py`:
```python
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('PCA App startup')
```

## Backup-Strategie

### Regelmäßige Backups

1. **Code**: Git-Repository (GitHub/GitLab)
2. **Daten**: Nicht nötig (on-demand von ECB)
3. **Konfiguration**: Dokumentieren Sie WCP-Einstellungen

## Support & Troubleshooting

### Netcup Forum
https://forum.netcup.de/

### Passenger Dokumentation
https://www.phusionpassenger.com/docs/

### ECB API Dokumentation
https://data.ecb.europa.eu/help/api/overview

## Update-Prozess

1. Lokale Änderungen testen
2. Geänderte Dateien hochladen (via FTP/WCP)
3. `tmp/restart.txt` erstellen/ändern
4. Funktionalität prüfen

## Häufige Fragen (FAQ)

**Q: Kann ich SSH verwenden?**
A: Nein, Webhosting 4000/8000 bietet kein SSH. Nur VPS-Tarife.

**Q: Wie installiere ich neue Python-Packages?**
A: Lokal installieren + vendor/ Upload (siehe Schritt 1)

**Q: Kann ich Cronjobs verwenden?**
A: Nein, nicht in der Passenger-Umgebung. Für automatisierte Tasks benötigen Sie einen VPS.

**Q: Wie viel Traffic kann die App verarbeiten?**
A: Abhängig von Ihrem Tarif. Webhosting 4000: 200GB/Monat, 8000: 400GB/Monat

**Q: Funktioniert HTTPS automatisch?**
A: Ja, Netcup bietet kostenlose SSL-Zertifikate (Let's Encrypt)

## Produktions-Checkliste

- [ ] Dependencies komplett hochgeladen
- [ ] `passenger_wsgi.py` vorhanden
- [ ] Python-Modul aktiviert im WCP
- [ ] App Root korrekt: `pca-app`
- [ ] Startup-Datei korrekt: `passenger_wsgi.py`
- [ ] Modus auf "Produktiv" gesetzt
- [ ] SECRET_KEY geändert
- [ ] Domain/Subdomain konfiguriert
- [ ] Funktionstest durchgeführt
- [ ] Fehlerbehandlung getestet
- [ ] Browser-Kompatibilität geprüft
- [ ] Backup-Strategie definiert

---

**Viel Erfolg beim Deployment! 🚀**

Bei Fragen: Netcup Support oder Forum nutzen.
