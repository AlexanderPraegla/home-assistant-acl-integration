# Tankstellen Sensoren - Anleitung

## Übersicht der Änderungen

Die Integration wurde erweitert, um flexiblere Tankstellen-Sensoren zu ermöglichen:

### 🎯 Hauptfeatures

1. **Separate Standorte** für günstigste und nächste Tankstelle
2. **Automatische Sensoren** für alle Kraftstoffarten (E5, E10, Diesel)
3. **Mehrere Nutzer-Standorte** für personalisierte "Nächste Tankstelle" Sensoren

## 📋 Konfiguration

### Ersteinrichtung

1. **Integration hinzufügen**
   - Einstellungen → Geräte & Dienste → Integration hinzufügen
   - "ISAL Easy Homey" suchen

2. **Basis-Konfiguration**
   ```
   - API Basis URL: http://192.168.178.31:8080/v1
   - Standort für günstigste Tankstelle: person.ich (optional)
   - Standort für nächste Tankstelle: device_tracker.handy (optional)
   - Warncell ID: 809177119
   - Suchradius: 15 km
   ```

### Benutzer-Standorte konfigurieren

1. **Optionen öffnen**
   - Einstellungen → Geräte & Dienste → ISAL Easy Homey
   - "Konfigurieren" klicken

2. **Benutzer-Standorte auswählen**
   - Im Menü "Benutzer-Standorte" wählen

3. **Standorte hinzufügen**
   - "Neuen Standort hinzufügen" wählen
   - Name eingeben (z.B. "Papa", "Mama", "Arbeit")
   - Entity auswählen (z.B. `person.papa`, `device_tracker.auto`)
   - Wiederholen für weitere Standorte

4. **Fertig klicken**
   - Änderungen werden gespeichert
   - Sensoren werden automatisch erstellt

## 📊 Verfügbare Sensoren

### Günstigste Tankstellen (3 Sensoren)

| Sensor | Beschreibung | State | Unit |
|--------|--------------|-------|------|
| `sensor.isal_easy_homey_cheapest_station_e5` | Günstigste für Super E5 | Preis | EUR |
| `sensor.isal_easy_homey_cheapest_station_e10` | Günstigste für Super E10 | Preis | EUR |
| `sensor.isal_easy_homey_cheapest_station_diesel` | Günstigste für Diesel | Preis | EUR |

**Attribute:** `fuel_type`, `station_id`, `name`, `brand`, `address`, `location`, `status`, `e5_price`, `e10_price`, `diesel_price`, `distance`

### Nächste Tankstelle (Standard)

| Sensor | Beschreibung | State | Unit |
|--------|--------------|-------|------|
| `sensor.isal_easy_homey_nearest_station` | Nächste Tankstelle vom konfigurierten Standort | Entfernung | km |

**Attribute:** `station_id`, `name`, `brand`, `address`, `location`, `status`, `e5_price`, `e10_price`, `diesel_price`, `distance`

### Nächste Tankstelle pro Nutzer (dynamisch)

Für jeden konfigurierten Benutzer-Standort wird ein Sensor erstellt:

| Beispiel-Name | Beschreibung | State | Unit |
|---------------|--------------|-------|------|
| `sensor.isal_easy_homey_nearest_station_papa` | Nächste Tankstelle für Papa | Entfernung | km |
| `sensor.isal_easy_homey_nearest_station_mama` | Nächste Tankstelle für Mama | Entfernung | km |
| `sensor.isal_easy_homey_nearest_station_arbeit` | Nächste Tankstelle nahe Arbeit | Entfernung | km |

**Attribute:** `user_name`, `station_id`, `name`, `brand`, `address`, `location`, `status`, `e5_price`, `e10_price`, `diesel_price`, `distance`

## 🎨 Dashboard-Karten Beispiele

### Entity-Karte für günstigste Diesel-Tankstelle

```yaml
type: entity
entity: sensor.isal_easy_homey_cheapest_station_diesel
name: Günstigster Diesel
icon: mdi:fuel
attribute: name
secondary_info: entity
```

### Markdown-Karte mit Details

```yaml
type: markdown
content: |
  ## Günstigste Tankstellen
  
  **Super E5:** {{ states('sensor.isal_easy_homey_cheapest_station_e5') }}€
  - {{ state_attr('sensor.isal_easy_homey_cheapest_station_e5', 'name') }}
  - {{ state_attr('sensor.isal_easy_homey_cheapest_station_e5', 'distance') }} km
  
  **Super E10:** {{ states('sensor.isal_easy_homey_cheapest_station_e10') }}€
  - {{ state_attr('sensor.isal_easy_homey_cheapest_station_e10', 'name') }}
  - {{ state_attr('sensor.isal_easy_homey_cheapest_station_e10', 'distance') }} km
  
  **Diesel:** {{ states('sensor.isal_easy_homey_cheapest_station_diesel') }}€
  - {{ state_attr('sensor.isal_easy_homey_cheapest_station_diesel', 'name') }}
  - {{ state_attr('sensor.isal_easy_homey_cheapest_station_diesel', 'distance') }} km
```

### Entities-Karte für Nutzer-Tankstellen

```yaml
type: entities
title: Nächste Tankstellen
entities:
  - entity: sensor.isal_easy_homey_nearest_station_papa
    name: Papa
    secondary_info: attribute
    attribute: name
  - entity: sensor.isal_easy_homey_nearest_station_mama
    name: Mama
    secondary_info: attribute
    attribute: name
  - entity: sensor.isal_easy_homey_nearest_station_arbeit
    name: Arbeit
    secondary_info: attribute
    attribute: name
```

## 🤖 Automations-Beispiele

### Benachrichtigung bei günstigem Preis

```yaml
automation:
  - alias: "Diesel unter 1.50€"
    trigger:
      - platform: numeric_state
        entity_id: sensor.isal_easy_homey_cheapest_station_diesel
        below: 1.50
    condition:
      - condition: time
        after: "08:00:00"
        before: "20:00:00"
    action:
      - service: notify.mobile_app_iphone
        data:
          title: "⛽ Günstiger Diesel!"
          message: >
            {{ states('sensor.isal_easy_homey_cheapest_station_diesel') }}€/L
            bei {{ state_attr('sensor.isal_easy_homey_cheapest_station_diesel', 'name') }}
            ({{ state_attr('sensor.isal_easy_homey_cheapest_station_diesel', 'distance') }} km entfernt)
```

### Benachrichtigung wenn Nutzer in der Nähe einer Tankstelle ist

```yaml
automation:
  - alias: "Papa nahe an günstiger Tankstelle"
    trigger:
      - platform: numeric_state
        entity_id: sensor.isal_easy_homey_nearest_station_papa
        below: 1
    condition:
      - condition: numeric_state
        entity_id: sensor.isal_easy_homey_cheapest_station_diesel
        below: 1.55
    action:
      - service: notify.papa
        data:
          title: "⛽ Tankstelle in der Nähe"
          message: >
            {{ state_attr('sensor.isal_easy_homey_nearest_station_papa', 'name') }}
            ist nur {{ states('sensor.isal_easy_homey_nearest_station_papa') }} km entfernt.
            Diesel: {{ state_attr('sensor.isal_easy_homey_nearest_station_papa', 'diesel_price') }}€
```

### Tägliche Zusammenfassung

```yaml
automation:
  - alias: "Tägliche Tankstellen-Info"
    trigger:
      - platform: time
        at: "07:00:00"
    action:
      - service: notify.family
        data:
          title: "⛽ Aktuelle Spritpreise"
          message: >
            Günstigste Preise heute:
            
            Super E5: {{ states('sensor.isal_easy_homey_cheapest_station_e5') }}€
            {{ state_attr('sensor.isal_easy_homey_cheapest_station_e5', 'name') }}
            
            Super E10: {{ states('sensor.isal_easy_homey_cheapest_station_e10') }}€
            {{ state_attr('sensor.isal_easy_homey_cheapest_station_e10', 'name') }}
            
            Diesel: {{ states('sensor.isal_easy_homey_cheapest_station_diesel') }}€
            {{ state_attr('sensor.isal_easy_homey_cheapest_station_diesel', 'name') }}
```

## 🔧 Troubleshooting

### Sensoren werden nicht erstellt

1. Prüfen Sie die Logs: Einstellungen → System → Protokolle
2. Suchen Sie nach "isal_easy_homey" oder "petrol"
3. Stellen Sie sicher, dass die Location-Entities gültige GPS-Koordinaten haben

### Benutzer-Standort Sensor fehlt

1. Optionen öffnen und "Benutzer-Standorte" prüfen
2. Sicherstellen, dass die Entity existiert und GPS-Koordinaten hat
3. Nach Änderungen Home Assistant neu laden oder Integration neu laden

### Falsche Entfernungen

1. Prüfen Sie, ob die Location-Entity aktuelle Koordinaten hat
2. Öffnen Sie die Entity und prüfen Sie die Attribute `latitude` und `longitude`
3. Bei Device Trackern: Stellen Sie sicher, dass das Gerät seine Position teilt

## 📝 Hinweise

- **Suchradius:** Standardmäßig 15 km, kann in den Optionen angepasst werden (0.1 - 25 km)
- **Update-Intervall:** Standardmäßig 5 Minuten, kann in den Optionen angepasst werden
- **API-Calls:** Jeder Benutzer-Standort generiert zusätzliche API-Aufrufe beim Update
- **Sensor-Namen:** Werden automatisch aus dem Benutzer-Namen generiert (Leerzeichen werden zu Unterstrichen)

## 🆕 Neue Features vs. Alte Version

| Feature | Alte Version | Neue Version |
|---------|--------------|--------------|
| Location für Sensoren | 1 gemeinsame | 2 separate (günstigste/nächste) |
| Günstigste Tankstelle | 1 Sensor (nur E5) | 3 Sensoren (E5, E10, Diesel) |
| Nächste Tankstelle | 1 Sensor | 1 + beliebig viele für Nutzer |
| Kraftstoffauswahl | In Options wählbar | Automatisch alle |
| Nutzer-Standorte | Nicht verfügbar | Unbegrenzt konfigurierbar |

