# Installation und Einrichtung - isal Easy Homey Integration

Dieses Dokument beschreibt die vollständige Installation und Einrichtung der **isal Easy Homey** Integration für Home Assistant.

## Inhaltsverzeichnis

1. [Voraussetzungen](#voraussetzungen)
2. [Installation](#installation)
3. [API-Setup](#api-setup)
4. [Konfiguration](#konfiguration)
5. [Verifizierung](#verifizierung)
6. [Fehlerbehebung](#fehlerbehebung)

---

## Voraussetzungen

### Erforderlich

- **Home Assistant** Version 2024.1 oder höher
- **isal Easy Homey API** läuft und ist erreichbar
  - Standard: `http://localhost:8080/v1`
  - Alternativ: `http://192.168.178.31:8080/v1`

### Optional (aber empfohlen)

- Eine **GPS-fähige Entity** in Home Assistant für standortbasierte Funktionen:
  - `device_tracker.phone` (Phone GPS)
  - `person.you` (Person mit Standort)
  - `zone.home` (Home Zone)
- **Warning Cell ID** für Ihre Region (siehe [Warncell-Liste](https://github.com/stephan192/dwdwfsapi/blob/master/docs/warncells.md))

---

## Installation

### Option 1: HACS (empfohlen)

1. **HACS öffnen**
   - Navigieren Sie zu **HACS** → **Integrationen**

2. **Custom Repository hinzufügen**
   - Klicken Sie auf die drei Punkte (⋮) oben rechts
   - Wählen Sie **"Benutzerdefinierte Repositories"**
   - Fügen Sie hinzu:
     - **URL**: `https://github.com/AlexanderPraegla/home-assistant-acl-integration`
     - **Kategorie**: `Integration`
   - Klicken Sie **"Hinzufügen"**

3. **Integration installieren**
   - Suchen Sie nach **"isal Easy Homey"**
   - Klicken Sie auf **"Herunterladen"**
   - Warten Sie auf den Abschluss

4. **Home Assistant neu starten**
   - Gehen Sie zu **Einstellungen** → **System** → **Neustart**
   - Warten Sie, bis Home Assistant vollständig neu gestartet ist

### Option 2: Manuelle Installation

1. **Dateien kopieren**
   ```bash
   # SSH in Home Assistant
   cd /config/custom_components
   
   # Erstellen Sie das Verzeichnis
   mkdir -p isal_easy_homey
   
   # Kopieren Sie alle Dateien aus dem Repository
   # custom_components/isal_easy_homey/* → /config/custom_components/isal_easy_homey/
   ```

2. **Struktur überprüfen**
   ```
   /config/custom_components/isal_easy_homey/
   ├── __init__.py
   ├── api.py
   ├── binary_sensor.py
   ├── config_flow.py
   ├── const.py
   ├── coordinator.py
   ├── manifest.json
   ├── sensor.py
   ├── strings.json
   └── translations/
       ├── de.json
       └── en.json
   ```

3. **Home Assistant neu starten**

---

## API-Setup

### Lokale API prüfen

Bevor Sie die Integration einrichten, stellen Sie sicher, dass die API erreichbar ist:

```bash
# Test 1: Pollen-Daten abrufen
curl http://localhost:8080/v1/weather/pollen-flight

# Test 2: Unwetter-Warnungen abrufen
curl http://localhost:8080/v1/weather/warnings?warningCellId=809177119

# Test 3: Müllabfuhr-Termine abrufen
curl http://localhost:8080/v1/waste-collection/next-collection
```

Wenn die API antwortet, können Sie fortfahren.

### API-URL anpassen

Falls Ihre API auf einer anderen URL läuft, notieren Sie sich die vollständige URL:
- Lokal: `http://localhost:8080/v1`
- Netzwerk: `http://192.168.178.31:8080/v1`
- Custom: `http://YOUR_IP:YOUR_PORT/v1`

---

## Konfiguration

### Schritt 1: Integration hinzufügen

1. Navigieren Sie zu **Einstellungen** → **Geräte & Dienste**
2. Klicken Sie auf **"+ Integration hinzufügen"**
3. Suchen Sie nach **"isal Easy Homey"**
4. Klicken Sie auf das Suchergebnis

### Schritt 2: Grundkonfiguration

Füllen Sie das Konfigurationsformular aus:

#### API Base URL
- **Standard**: `http://localhost:8080/v1`
- **Beschreibung**: Die vollständige URL zu Ihrer API
- **Beispiele**:
  - Lokal: `http://localhost:8080/v1`
  - Netzwerk: `http://192.168.178.31:8080/v1`

#### Location Entity ID (Optional)
- **Beispiele**: `device_tracker.phone`, `person.you`
- **Beschreibung**: Eine Entity mit GPS-Koordinaten für standortbasierte Sensoren
- **Wird benötigt für**:
  - Nächste Tankstelle
  - Günstigste Tankstelle
- **Kann leer bleiben**, wenn Sie keine standortbasierten Funktionen nutzen möchten

#### Warning Cell ID
- **Standard**: `809177119` (Gemeinde Forstern)
- **Beschreibung**: ID für Unwetterwarnungen Ihrer Region
- **Wo finden**:
  - [DWD Warncell-Liste](https://github.com/stephan192/dwdwfsapi/blob/master/docs/warncells.md)
  - Suchen Sie nach Ihrer Gemeinde/Stadt
  - Kopieren Sie die ID (9-stellige Zahl)

#### Suchradius (km)
- **Standard**: `15`
- **Minimum**: `0.1`
- **Maximum**: `25`
- **Beschreibung**: Umkreis für die Tankstellensuche

#### Kraftstofftyp
- **Standard**: `E5`
- **Optionen**: `E5`, `E10`, `DIESEL`
- **Beschreibung**: Kraftstofftyp für die "günstigste Tankstelle"

### Schritt 3: Konfiguration abschließen

1. Klicken Sie auf **"Senden"**
2. Die Integration wird die Verbindung zur API testen
3. Bei Erfolg werden alle Sensoren erstellt
4. Sie sehen eine Erfolgsmeldung

### Schritt 4: Optionen anpassen (Optional)

Nach der Einrichtung können Sie weitere Einstellungen anpassen:

1. Gehen Sie zu **Einstellungen** → **Geräte & Dienste**
2. Finden Sie **"isal Easy Homey"**
3. Klicken Sie auf **"Konfigurieren"**

#### Verfügbare Optionen:

**Suchradius (km)**
- Ändern Sie den Umkreis für die Tankstellensuche

**Warning Cell ID**
- Ändern Sie die Region für Unwetterwarnungen

**Kraftstofftyp**
- Ändern Sie den Kraftstofftyp für die günstigste Tankstelle

**Update-Intervalle (Minuten)**
- **Tankstellen**: Standard 5 Minuten (1-1440)
- **Unwetter**: Standard 10 Minuten (1-1440)
- **Pollenflug**: Standard 30 Minuten (1-1440)
- **Müllabfuhr**: Standard 30 Minuten (1-1440)

---

## Verifizierung

### Schritt 1: Geräte prüfen

1. Gehen Sie zu **Einstellungen** → **Geräte & Dienste**
2. Finden Sie **"isal Easy Homey"**
3. Klicken Sie darauf
4. Sie sollten ein Gerät sehen: **"isal Easy Homey"**

### Schritt 2: Sensoren prüfen

Klicken Sie auf das Gerät und überprüfen Sie die Sensoren:

#### Tankstellen (2 Sensoren)
- ✓ `sensor.isal_easy_homey_nearest_station`
- ✓ `sensor.isal_easy_homey_cheapest_station`

#### Unwetter (5 Sensoren)
- ✓ `binary_sensor.isal_easy_homey_weather_warning_active`
- ✓ `binary_sensor.isal_easy_homey_upfront_warning_active`
- ✓ `sensor.isal_easy_homey_current_weather_warning`
- ✓ `sensor.isal_easy_homey_current_upfront_warning`
- ✓ `sensor.isal_easy_homey_all_weather_warnings_json`
- ✓ `sensor.isal_easy_homey_all_upfront_warnings_json`

#### Pollenflug (10 Sensoren)
- ✓ `binary_sensor.isal_easy_homey_pollen_flight_active`
- ✓ `sensor.isal_easy_homey_highest_pollen_severity`
- ✓ 8x Pollen-spezifische Sensoren (Erle, Birke, Gräser, etc.)

#### Müllabfuhr (6 Sensoren)
- ✓ `sensor.isal_easy_homey_next_waste_collection`
- ✓ 5x Müllart-spezifische Sensoren (Papier, Bio, Rest, etc.)

**Gesamt: 23 Sensoren + 3 Binary Sensoren = 26 Entities**

### Schritt 3: Daten testen

1. Gehen Sie zu **Entwicklerwerkzeuge** → **Zustände**
2. Suchen Sie nach `isal_easy_homey`
3. Überprüfen Sie, ob Sensoren Daten haben:
   - Sensoren sollten **nicht** "unavailable" sein (außer wenn keine Daten verfügbar)
   - Attribute sollten Daten enthalten

---

## Fehlerbehebung

### Problem: "Cannot connect to API"

**Ursache**: Die API ist nicht erreichbar

**Lösung**:
1. Prüfen Sie, ob die API läuft:
   ```bash
   curl http://localhost:8080/v1/weather/pollen-flight
   ```
2. Prüfen Sie die URL in der Konfiguration
3. Prüfen Sie Firewall-Einstellungen
4. Prüfen Sie, ob der Port korrekt ist

### Problem: "Timeout connecting to API"

**Ursache**: Die API antwortet zu langsam oder ist überlastet

**Lösung**:
1. Prüfen Sie die API-Performance
2. Erhöhen Sie die Update-Intervalle in den Optionen
3. Prüfen Sie die Netzwerkverbindung

### Problem: "Invalid Entity"

**Ursache**: Die Location Entity existiert nicht oder hat keine GPS-Koordinaten

**Lösung**:
1. Gehen Sie zu **Entwicklerwerkzeuge** → **Zustände**
2. Suchen Sie Ihre Entity (z.B. `device_tracker.phone`)
3. Prüfen Sie, ob Attribute `latitude` und `longitude` vorhanden sind
4. Falls nicht, wählen Sie eine andere Entity oder lassen Sie das Feld leer

### Problem: Sensoren zeigen "unavailable"

**Ursache 1**: API liefert keine Daten für diese Kategorie

**Lösung**:
- Prüfen Sie die API direkt mit curl
- Manche Sensoren sind nur verfügbar, wenn Daten existieren (z.B. Unwetterwarnungen nur bei aktiven Warnungen)

**Ursache 2**: Koordinaten nicht verfügbar

**Lösung**:
- Tankstellen-Sensoren benötigen eine Location Entity
- Prüfen Sie, ob die Entity konfiguriert ist und GPS-Daten hat

### Problem: Pollen-Sensoren zeigen "unavailable"

**Ursache**: Keine Pollendaten für diese Art verfügbar

**Lösung**:
- Normal außerhalb der Pollensaison
- Prüfen Sie mit: `curl http://localhost:8080/v1/weather/pollen-flight`

### Problem: Müll-Sensoren zeigen "unavailable"

**Ursache**: Keine zukünftigen Termine für diese Müllart

**Lösung**:
- Normal, wenn keine Termine geplant sind
- Prüfen Sie mit: `curl http://localhost:8080/v1/waste-collection/upcoming-collections`

### Logs überprüfen

1. Gehen Sie zu **Einstellungen** → **System** → **Protokolle**
2. Suchen Sie nach `isal_easy_homey`
3. Überprüfen Sie Fehler- und Warnmeldungen

Typische Log-Einträge:
```
INFO: Successfully updated petrol_station coordinator
WARNING: Entity device_tracker.phone not found
ERROR: Error communicating with API: Timeout
```

### Integration zurücksetzen

Falls nichts funktioniert:

1. Gehen Sie zu **Einstellungen** → **Geräte & Dienste**
2. Finden Sie **"isal Easy Homey"**
3. Klicken Sie auf die drei Punkte (⋮)
4. Wählen Sie **"Löschen"**
5. Bestätigen Sie
6. Starten Sie Home Assistant neu
7. Fügen Sie die Integration erneut hinzu

---

## Erweiterte Konfiguration

### Mehrere Instanzen

Sie können die Integration mehrmals hinzufügen, z.B. für:
- Verschiedene API-Instanzen
- Verschiedene Standorte
- Verschiedene Warning Cell IDs

Jede Instanz erhält eindeutige Entity-IDs.

### Service Calls

Die Integration unterstützt Standard Home Assistant Services:

```yaml
# Coordinator manuell aktualisieren
service: homeassistant.update_entity
target:
  entity_id: sensor.isal_easy_homey_nearest_station
```

### Debugging aktivieren

Fügen Sie zu `configuration.yaml` hinzu:

```yaml
logger:
  default: info
  logs:
    custom_components.isal_easy_homey: debug
```

Dann:
1. Speichern Sie die Datei
2. Gehen Sie zu **Entwicklerwerkzeuge** → **YAML** → **Konfiguration neu laden**
3. Überprüfen Sie die Logs für detaillierte Informationen

---

## Support

Bei weiteren Fragen oder Problemen:

1. **GitHub Issues**: [Issues erstellen](https://github.com/AlexanderPraegla/home-assistant-acl-integration/issues)
2. **Logs überprüfen**: Immer Logs mit anhängen
3. **Konfiguration prüfen**: Stellen Sie sicher, dass die API erreichbar ist

---

**Viel Erfolg mit der Integration! 🚀**

