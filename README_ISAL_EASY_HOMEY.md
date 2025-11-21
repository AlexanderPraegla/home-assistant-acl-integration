# isal Easy Homey Integration für Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

Eine vollständige Home Assistant Integration für die isal Easy Homey API, die Sensoren für Tankstellenpreise, Unwetterwarnungen, Pollenflug-Informationen und Müllabfuhr-Termine bereitstellt.

## Features

### 🚗 Tankstellen-Sensoren
- **Nächste Tankstelle**: Zeigt die nächstgelegene Tankstelle basierend auf GPS-Koordinaten
- **Günstigste Tankstelle**: Findet die günstigste Tankstelle im konfigurierten Umkreis
- Preise für Super E5, E10 und Diesel
- Öffnungszeiten und Status-Informationen
- Dynamische GPS-basierte Suche

### 🌪️ Unwetter-Warnungen
- **Unwetterwarnung aktiv** (Binary Sensor): Zeigt an, ob eine Unwetterwarnung aktiv ist
- **Vorabwarnung aktiv** (Binary Sensor): Zeigt an, ob eine Vorabwarnung aktiv ist
- **Aktuelle Unwetterwarnung**: Details zur schwersten aktiven Warnung
- **Aktuelle Vorabwarnung**: Details zur schwersten aktiven Vorabwarnung
- **Alle Warnungen (JSON)**: Vollständige Daten für Dashboard-Anzeige
- Warnstufen, Beschreibungen und Handlungsempfehlungen
- Dynamische Icons basierend auf Wettertyp

### 🌸 Pollenflug-Sensoren
- **Pollenflug aktiv** (Binary Sensor): Zeigt an, ob Pollenflug vorhanden ist
- **Höchste Pollenbelastung**: Die aktuell höchste Belastung aller Pollenarten
- **Individuelle Pollen-Sensoren** für:
  - Erle, Ambrosia, Esche, Birke
  - Gräser, Hasel, Beifuß, Roggen
- 3-Tages-Vorhersage (heute, morgen, übermorgen)
- Schweregrade und Farbcodes
- Dynamische Icons pro Pollenart

### 🗑️ Müllabfuhr-Sensoren
- **Nächste Müllabholung**: Zeigt das nächste Abholdatum mit allen Müllarten
- **Individuelle Müll-Sensoren** für:
  - Papiermüll, Biomüll, Restmüll
  - Gelber Sack, Problemmüll
- Tage bis zur Abholung
- Farbcodes für visuelle Darstellung
- Dynamische Icons pro Müllart

## Installation

### HACS (empfohlen)

1. Öffnen Sie HACS in Home Assistant
2. Gehen Sie zu "Integrationen"
3. Klicken Sie auf die drei Punkte oben rechts und wählen Sie "Benutzerdefinierte Repositories"
4. Fügen Sie die Repository-URL hinzu: `https://github.com/apraegla/home-assistant-acl-integration`
5. Kategorie: "Integration"
6. Klicken Sie auf "Hinzufügen"
7. Suchen Sie nach "isal Easy Homey" und installieren Sie es
8. Starten Sie Home Assistant neu

### Manuelle Installation

1. Kopieren Sie den `custom_components/isal_easy_homey` Ordner in Ihr `custom_components` Verzeichnis
2. Starten Sie Home Assistant neu

## Konfiguration

### Initiale Einrichtung

1. Gehen Sie zu **Einstellungen** → **Geräte & Dienste** → **Integration hinzufügen**
2. Suchen Sie nach "isal Easy Homey"
3. Geben Sie die folgenden Informationen ein:
   - **API Base URL**: Die URL Ihrer API (Standard: `http://localhost:8080/v1`)
   - **Standort Entity** (optional): Eine Entity mit GPS-Koordinaten (z.B. `device_tracker.phone`)
   - **Warning Cell ID**: ID für Unwetterwarnungen (Standard: `809177119` für Gemeinde Forstern)
   - **Suchradius**: Umkreis für Tankstellensuche in km (Standard: 15 km)
   - **Kraftstofftyp**: Kraftstofftyp für günstigste Tankstelle (E5, E10 oder DIESEL)

### Optionen anpassen

Nach der Einrichtung können Sie die Einstellungen anpassen:

1. Gehen Sie zu **Einstellungen** → **Geräte & Dienste**
2. Finden Sie "isal Easy Homey" und klicken Sie auf "Konfigurieren"
3. Passen Sie folgende Optionen an:
   - **Suchradius**: Umkreis für Tankstellensuche
   - **Warning Cell ID**: ID für Unwetterwarnungen
   - **Kraftstofftyp**: Für günstigste Tankstelle
   - **Update-Intervalle**: Für jede Sensor-Kategorie separat
     - Tankstellen (Standard: 5 Minuten)
     - Unwetterwarnungen (Standard: 10 Minuten)
     - Pollenflug (Standard: 30 Minuten)
     - Müllabfuhr (Standard: 30 Minuten)

## Sensoren

### Alle verfügbaren Sensoren

#### Tankstellen
- `sensor.isal_easy_homey_nearest_station`
- `sensor.isal_easy_homey_cheapest_station`

#### Unwetter
- `binary_sensor.isal_easy_homey_weather_warning_active`
- `binary_sensor.isal_easy_homey_upfront_warning_active`
- `sensor.isal_easy_homey_current_weather_warning`
- `sensor.isal_easy_homey_current_upfront_warning`
- `sensor.isal_easy_homey_all_weather_warnings_json`
- `sensor.isal_easy_homey_all_upfront_warnings_json`

#### Pollenflug
- `binary_sensor.isal_easy_homey_pollen_flight_active`
- `sensor.isal_easy_homey_highest_pollen_severity`
- `sensor.isal_easy_homey_pollen_alder`
- `sensor.isal_easy_homey_pollen_ambrosia`
- `sensor.isal_easy_homey_pollen_ash_tree`
- `sensor.isal_easy_homey_pollen_birch`
- `sensor.isal_easy_homey_pollen_grasses`
- `sensor.isal_easy_homey_pollen_hazel`
- `sensor.isal_easy_homey_pollen_mugwort`
- `sensor.isal_easy_homey_pollen_rye`

#### Müllabfuhr
- `sensor.isal_easy_homey_next_waste_collection`
- `sensor.isal_easy_homey_waste_paper`
- `sensor.isal_easy_homey_waste_bio`
- `sensor.isal_easy_homey_waste_general`
- `sensor.isal_easy_homey_waste_yellow_bag`
- `sensor.isal_easy_homey_waste_problem`

## Beispiel Dashboard-Karte

### Tankstellen-Karte

```yaml
type: entities
title: Tankstellen
entities:
  - entity: sensor.isal_easy_homey_nearest_station
    name: Nächste Tankstelle
  - entity: sensor.isal_easy_homey_cheapest_station
    name: Günstigste Tankstelle
```

### Unwetter-Karte

```yaml
type: conditional
conditions:
  - entity: binary_sensor.isal_easy_homey_weather_warning_active
    state: 'on'
card:
  type: markdown
  content: >
    ## {{ state_attr('sensor.isal_easy_homey_current_weather_warning', 'title') }}

    **Beschreibung:** {{ state_attr('sensor.isal_easy_homey_current_weather_warning', 'description') }}

    **Warnstufe:** {{ state_attr('sensor.isal_easy_homey_current_weather_warning', 'severity_translation') }}

    **Gültig:** {{ state_attr('sensor.isal_easy_homey_current_weather_warning', 'valid_from') }} bis {{ state_attr('sensor.isal_easy_homey_current_weather_warning', 'valid_until') }}
```

### Pollenflug-Karte

```yaml
type: entities
title: Pollenflug
entities:
  - entity: binary_sensor.isal_easy_homey_pollen_flight_active
    name: Pollenflug aktiv
  - entity: sensor.isal_easy_homey_highest_pollen_severity
    name: Höchste Belastung
  - type: divider
  - entity: sensor.isal_easy_homey_pollen_birch
    name: Birke
  - entity: sensor.isal_easy_homey_pollen_grasses
    name: Gräser
  - entity: sensor.isal_easy_homey_pollen_hazel
    name: Hasel
```

### Müllabfuhr-Karte

```yaml
type: entities
title: Müllabfuhr
entities:
  - entity: sensor.isal_easy_homey_next_waste_collection
    name: Nächste Abholung
  - type: divider
  - entity: sensor.isal_easy_homey_waste_paper
    name: Papier
  - entity: sensor.isal_easy_homey_waste_bio
    name: Biomüll
  - entity: sensor.isal_easy_homey_waste_general
    name: Restmüll
  - entity: sensor.isal_easy_homey_waste_yellow_bag
    name: Gelber Sack
```

## Automatisierungen

### Benachrichtigung bei Unwetterwarnung

```yaml
automation:
  - alias: "Unwetterwarnung Benachrichtigung"
    trigger:
      - platform: state
        entity_id: binary_sensor.isal_easy_homey_weather_warning_active
        to: 'on'
    action:
      - service: notify.mobile_app
        data:
          title: "⚠️ Unwetterwarnung"
          message: >
            {{ state_attr('sensor.isal_easy_homey_current_weather_warning', 'title') }}
            
            {{ state_attr('sensor.isal_easy_homey_current_weather_warning', 'description') }}
```

### Erinnerung an Müllabfuhr

```yaml
automation:
  - alias: "Müllabfuhr Erinnerung"
    trigger:
      - platform: time
        at: "20:00:00"
    condition:
      - condition: template
        value_template: >
          {{ state_attr('sensor.isal_easy_homey_next_waste_collection', 'days_until_collection') == 0 }}
    action:
      - service: notify.mobile_app
        data:
          title: "🗑️ Müllabfuhr Morgen"
          message: >
            Morgen wird abgeholt: {{ state_attr('sensor.isal_easy_homey_next_waste_collection', 'waste_types_translations') | join(', ') }}
```

## API-Anforderungen

Diese Integration benötigt eine laufende Instanz der isal Easy Homey API. Die API sollte unter der konfigurierten URL erreichbar sein.

Standardmäßig wird `http://localhost:8080/v1` verwendet.

## Fehlerbehebung

### Sensoren zeigen "Nicht verfügbar"

1. Überprüfen Sie, ob die API erreichbar ist
2. Prüfen Sie die Logs unter **Einstellungen** → **System** → **Protokolle**
3. Stellen Sie sicher, dass die API-URL korrekt ist
4. Wenn Sie eine Standort-Entity verwenden, prüfen Sie, ob diese GPS-Koordinaten hat

### GPS-basierte Sensoren funktionieren nicht

1. Stellen Sie sicher, dass Sie eine Entity mit GPS-Koordinaten konfiguriert haben
2. Überprüfen Sie, ob die Entity existiert und aktuelle Daten hat
3. Prüfen Sie die Attribute der Entity (sollte `latitude` und `longitude` enthalten)

### Update-Intervalle anpassen

Wenn die Standard-Update-Intervalle zu häufig oder zu selten sind:
1. Gehen Sie zu den Optionen der Integration
2. Passen Sie die Update-Intervalle für jede Kategorie an
3. Die Integration wird neu geladen und die neuen Intervalle werden angewendet

## Entwicklung

### Voraussetzungen

- Python 3.11+
- Home Assistant 2024.1+

### Lokale Entwicklung

```bash
# Repository klonen
git clone https://github.com/apraegla/home-assistant-acl-integration.git
cd home-assistant-acl-integration

# Development Container verwenden (empfohlen)
# Öffnen Sie das Projekt in VS Code und verwenden Sie "Reopen in Container"

# Oder manuell:
pip install -r requirements.txt
```

## Lizenz

Siehe [LICENSE](LICENSE) Datei.

## Support

Bei Problemen oder Fragen erstellen Sie bitte ein Issue im [GitHub Repository](https://github.com/apraegla/home-assistant-acl-integration/issues).

## Credits

Entwickelt von [@apraegla](https://github.com/apraegla)

---

**Hinweis:** Diese Integration ist nicht offiziell von Home Assistant oder isal unterstützt.

