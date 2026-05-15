# Plan: Enum-Übersetzungen für Water Softener Sensoren

## Ziel

Die folgenden 4 Sensoren zeigen aktuell rohe API-Enum-Werte an (z.B. `ONLINE`, `IDLE`, `NO_LEAKAGE`).
Diese sollen über den Home Assistant Übersetzungsmechanismus (`SensorDeviceClass.ENUM` + `state`-Translations) in DE und EN lokalisiert werden.

## Betroffene Enums & Übersetzungen

### DeviceStatus

> Sensor: `water_softener_device_status`

| Enum-Wert | DE              | EN      |
|-----------|-----------------|---------|
| `ONLINE`  | Online          | Online  |
| `OFFLINE` | Offline         | Offline |
| `UNKNOWN` | Unbekannt       | Unknown |

### ShutoffValveStatus

> Sensor: `water_softener_shutoff_valve`

| Enum-Wert | DE           | EN     |
|-----------|--------------|--------|
| `OPEN`    | Geöffnet     | Open   |
| `CLOSED`  | Geschlossen  | Closed |

### MicroLeakageCheck

> Sensor: `water_softener_micro_leakage_check`

| Enum-Wert | DE       | EN      |
|-----------|----------|---------|
| `IDLE`    | Inaktiv  | Idle    |
| `RUNNING` | Läuft    | Running |

### MicroLeakageStatus

> Sensor: `water_softener_micro_leakage_status`

| Enum-Wert          | DE               | EN               |
|--------------------|------------------|------------------|
| `NO_LEAKAGE`       | Keine Leckage    | No Leakage       |
| `LEAKAGE_DETECTED` | Leckage erkannt  | Leakage Detected |

## Zu ändernde Dateien

### 1. `sensor.py`

Für jede der 4 Sensor-Descriptions `SensorDeviceClass.ENUM` und `options` ergänzen:

```python
# water_softener_device_status
IsalEasyHomeySensorEntityDescription(
    key="water_softener_device_status",
    ...
    device_class=SensorDeviceClass.ENUM,
    options=["ONLINE", "OFFLINE", "UNKNOWN"],
    ...
)

# water_softener_shutoff_valve
IsalEasyHomeySensorEntityDescription(
    key="water_softener_shutoff_valve",
    ...
    device_class=SensorDeviceClass.ENUM,
    options=["OPEN", "CLOSED"],
    ...
)

# water_softener_micro_leakage_check
IsalEasyHomeySensorEntityDescription(
    key="water_softener_micro_leakage_check",
    ...
    device_class=SensorDeviceClass.ENUM,
    options=["IDLE", "RUNNING"],
    ...
)

# water_softener_micro_leakage_status
IsalEasyHomeySensorEntityDescription(
    key="water_softener_micro_leakage_status",
    ...
    device_class=SensorDeviceClass.ENUM,
    options=["NO_LEAKAGE", "LEAKAGE_DETECTED"],
    ...
)
```

### 2. `strings.json` (EN - Basis)

`state`-Einträge zu den bestehenden Sensor-Definitionen hinzufügen:

```json
"water_softener_device_status": {
  "name": "Device Status",
  "state": {
    "ONLINE": "Online",
    "OFFLINE": "Offline",
    "UNKNOWN": "Unknown"
  }
},
"water_softener_shutoff_valve": {
  "name": "Shutoff Valve (Softener)",
  "state": {
    "OPEN": "Open",
    "CLOSED": "Closed"
  }
},
"water_softener_micro_leakage_check": {
  "name": "Micro Leakage Check",
  "state": {
    "IDLE": "Idle",
    "RUNNING": "Running"
  }
},
"water_softener_micro_leakage_status": {
  "name": "Micro Leakage Status",
  "state": {
    "NO_LEAKAGE": "No Leakage",
    "LEAKAGE_DETECTED": "Leakage Detected"
  }
}
```

### 3. `translations/en.json`

Identisch zu `strings.json` – gleiche `state`-Einträge.

### 4. `translations/de.json`

```json
"water_softener_device_status": {
  "name": "Gerätestatus",
  "state": {
    "ONLINE": "Online",
    "OFFLINE": "Offline",
    "UNKNOWN": "Unbekannt"
  }
},
"water_softener_shutoff_valve": {
  "name": "Absperrventil (Entkalkung)",
  "state": {
    "OPEN": "Geöffnet",
    "CLOSED": "Geschlossen"
  }
},
"water_softener_micro_leakage_check": {
  "name": "Kleinleckageprüfung",
  "state": {
    "IDLE": "Inaktiv",
    "RUNNING": "Läuft"
  }
},
"water_softener_micro_leakage_status": {
  "name": "Kleinleckage Status",
  "state": {
    "NO_LEAKAGE": "Keine Leckage",
    "LEAKAGE_DETECTED": "Leckage erkannt"
  }
}
```

## Bestehendes Muster

Das Muster ist bereits bei der Select-Entity `water_softener_water_scene` implementiert (siehe `translations/de.json`, Zeile 296-305). Für Sensoren wird statt `select` der Bereich `sensor` unter `entity` verwendet, zusammen mit `SensorDeviceClass.ENUM`.

## Reihenfolge der Umsetzung

1. `sensor.py` – `device_class` und `options` ergänzen
2. `strings.json` – `state`-Blöcke einfügen
3. `translations/en.json` – `state`-Blöcke einfügen
4. `translations/de.json` – `state`-Blöcke einfügen
5. Testen: Sensoren sollten lokalisierte Werte in der HA-UI anzeigen

