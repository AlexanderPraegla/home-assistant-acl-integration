# Refactoring-Plan: Entities auf mehrere Devices aufteilen

## Übersicht

Aktuell werden **alle Entities** einem einzigen Device `"isal Easy Homey"` zugeordnet über identische `identifiers: {(DOMAIN, entry.entry_id)}`. Die Änderung besteht darin, **pro Coordinator/OpenAPI-Tag ein eigenes Sub-Device** zu erstellen und diese über ein **Hub-Device** (Gateway) zu verknüpfen.

Da `unique_id` der Entities unverändert bleibt, bleiben Entity-Namen und Entity-IDs in Home Assistant erhalten – die Entities wandern lediglich auf neue Devices.

---

## Device-Hierarchie (Hub + Sub-Devices)

```
Easy Homey (Hub/Gateway)
├── Easy Homey Tankstellen
├── Easy Homey Wetterwarnungen
├── Easy Homey Pollenflug
└── Easy Homey Abfallkalender
```

### Device-Definitionen

| # | Device-Name | Identifier | Model | `via_device` | Entities |
|---|---|---|---|---|---|
| **Hub** | **Easy Homey** | `(DOMAIN, entry_id)` | `API Gateway` | – | `service_uptime` |
| 1 | **Easy Homey Tankstellen** | `(DOMAIN, f"{entry_id}_petrol_station")` | `Petrol Station` | `(DOMAIN, entry_id)` | `nearest_station`, `cheapest_station_*`, `nearest_station_{user}`, `station_{id}` |
| 2 | **Easy Homey Wetterwarnungen** | `(DOMAIN, f"{entry_id}_weather_warning")` | `Weather Warnings` | `(DOMAIN, entry_id)` | `current_weather_warning`, `current_upfront_warning`, `all_weather_warnings_json`, `all_upfront_warnings_json`, `weather_warning_active`, `upfront_warning_active` |
| 3 | **Easy Homey Pollenflug** | `(DOMAIN, f"{entry_id}_pollen_flight")` | `Pollen Flight` | `(DOMAIN, entry_id)` | `highest_pollen_severity`, `pollen_{type}` (×8), `pollen_flight_active` |
| 4 | **Easy Homey Abfallkalender** | `(DOMAIN, f"{entry_id}_waste_collection")` | `Waste Collection` | `(DOMAIN, entry_id)` | `next_waste_collection`, `waste_{type}` (×5) |

### Device-Info Beispiel (Python)

```python
# Hub-Device (für service_uptime Entity)
{
    "identifiers": {(DOMAIN, entry.entry_id)},
    "name": "Easy Homey",
    "manufacturer": MANUFACTURER,
    "model": "API Gateway",
}

# Sub-Device Beispiel (Tankstellen)
{
    "identifiers": {(DOMAIN, f"{entry.entry_id}_petrol_station")},
    "name": "Easy Homey Tankstellen",
    "manufacturer": MANUFACTURER,
    "model": "Petrol Station",
    "via_device": (DOMAIN, entry.entry_id),
}
```

---

## Dateien und Änderungen

### 1. `const.py` – Neue Konstanten

```python
# Device models
MODEL_GATEWAY: Final = "API Gateway"
MODEL_PETROL: Final = "Petrol Station"
MODEL_WEATHER: Final = "Weather Warnings"
MODEL_POLLEN: Final = "Pollen Flight"
MODEL_WASTE: Final = "Waste Collection"

# Device names (deutsch, da HA keine Device-Name-Translations unterstützt)
DEVICE_NAME_HUB: Final = "Easy Homey"
DEVICE_NAME_PETROL: Final = "Easy Homey Tankstellen"
DEVICE_NAME_WEATHER: Final = "Easy Homey Wetterwarnungen"
DEVICE_NAME_POLLEN: Final = "Easy Homey Pollenflug"
DEVICE_NAME_WASTE: Final = "Easy Homey Abfallkalender"
```

Die alte `MODEL`-Konstante kann entfernt werden, sobald sie nicht mehr referenziert wird.

### 2. Neue Helper-Funktion (in `const.py` oder neuer `device.py`)

```python
def get_device_info(entry_id: str, coordinator_key: str) -> dict:
    """Get device info dict for given coordinator key."""
    mapping = {
        COORDINATOR_PETROL: (DEVICE_NAME_PETROL, MODEL_PETROL),
        COORDINATOR_WEATHER: (DEVICE_NAME_WEATHER, MODEL_WEATHER),
        COORDINATOR_POLLEN: (DEVICE_NAME_POLLEN, MODEL_POLLEN),
        COORDINATOR_WASTE: (DEVICE_NAME_WASTE, MODEL_WASTE),
        COORDINATOR_SERVICE_INFO: (DEVICE_NAME_HUB, MODEL_GATEWAY),
    }
    name, model = mapping[coordinator_key]
    
    device_info = {
        "identifiers": {(DOMAIN, f"{entry_id}_{coordinator_key}" if coordinator_key != COORDINATOR_SERVICE_INFO else entry_id)},
        "name": name,
        "manufacturer": MANUFACTURER,
        "model": model,
    }
    
    # Sub-Devices verweisen auf den Hub
    if coordinator_key != COORDINATOR_SERVICE_INFO:
        device_info["via_device"] = (DOMAIN, entry_id)
    
    return device_info
```

### 3. `sensor.py` – `_attr_device_info` in allen Entity-Klassen anpassen

| Entity-Klasse | Aktuell | Neu (coordinator_key) |
|---|---|---|
| `IsalEasyHomeySensor` (generisch) | `(DOMAIN, entry.entry_id)` | Parameter `coordinator_key` → `get_device_info()` |
| `IsalEasyHomeyHighestPollenSensor` | `(DOMAIN, entry.entry_id)` | `COORDINATOR_POLLEN` |
| `IsalEasyHomeyPollenSensor` | `(DOMAIN, entry.entry_id)` | `COORDINATOR_POLLEN` |
| `IsalEasyHomeyNextWasteCollectionSensor` | `(DOMAIN, entry.entry_id)` | `COORDINATOR_WASTE` |
| `IsalEasyHomeyWasteSensor` | `(DOMAIN, entry.entry_id)` | `COORDINATOR_WASTE` |
| `IsalEasyHomeyCheapestStationSensor` | `(DOMAIN, entry.entry_id)` | `COORDINATOR_PETROL` |
| `IsalEasyHomeyUserNearestStationSensor` | `(DOMAIN, entry.entry_id)` | `COORDINATOR_PETROL` |
| `IsalEasyHomeyStationIdSensor` | `(DOMAIN, entry.entry_id)` | `COORDINATOR_PETROL` |
| `IsalEasyHomeyServiceInfoSensor` | `(DOMAIN, entry.entry_id)` | `COORDINATOR_SERVICE_INFO` (= Hub) |

**Änderung in `async_setup_entry`:**

Die generische `IsalEasyHomeySensor`-Klasse bekommt einen neuen Parameter `coordinator_key`:
```python
# Petrol sensors
IsalEasyHomeySensor(petrol_coordinator, entry, description, COORDINATOR_PETROL)

# Weather sensors
IsalEasyHomeySensor(weather_coordinator, entry, description, COORDINATOR_WEATHER)
```

### 4. `binary_sensor.py` – `_attr_device_info` anpassen

| Entity-Klasse | Neuer coordinator_key |
|---|---|
| `IsalEasyHomeyBinarySensor` (Weather) | `COORDINATOR_WEATHER` |
| `IsalEasyHomeyBinarySensor` (Pollen) | `COORDINATOR_POLLEN` |

Analog zu `sensor.py` den `coordinator_key` als Parameter übergeben.

### 5. Keine Änderungen nötig

- `coordinator.py` – Unverändert
- `__init__.py` – Unverändert (Device-Registrierung erfolgt implizit über `_attr_device_info`)
- `api.py` – Unverändert
- `config_flow.py` – Unverändert
- `manifest.json` – Nur Version-Bump auf `1.1.0`
- `strings.json` / `translations/` – Keine Änderung (Device-Namen nicht übersetzbar)

---

## Migrations-Überlegungen (bestehende Nutzer)

| Aspekt | Auswirkung |
|---|---|
| **Entity-Identität** | `unique_id` bleibt gleich → Entity-IDs, Namen, Automationen, Dashboards bleiben intakt ✅ |
| **Historische Daten** | Kein Datenverlust, da `unique_id` unverändert ✅ |
| **Hub-Device** | Behält den bisherigen Identifier `(DOMAIN, entry.entry_id)` → Das alte Device wird zum Hub-Device "umbenannt" (von "isal Easy Homey" zu "Easy Homey") ✅ |
| **Neue Sub-Devices** | 4 neue Sub-Devices werden automatisch erstellt ✅ |
| **Config-Migration** | Nicht nötig – `entry.data`/`entry.options` ändern sich nicht ✅ |
| **Entity Migration** | Entities die bisher auf dem alten Device lagen, wandern auf die neuen Sub-Devices. Nur `service_uptime` bleibt auf dem Hub. |

**Wichtig:** Da der Hub-Device denselben Identifier wie das bisherige Device hat (`(DOMAIN, entry.entry_id)`), wird das alte Device nicht verwaist – es wird lediglich umbenannt und die meisten Entities wandern auf Sub-Devices ab. Das ist der sauberste Migrationspfad.

---

## Implementierungsreihenfolge

| Schritt | Aktion | Datei(en) |
|---|---|---|
| 1 | Neue Konstanten anlegen | `const.py` |
| 2 | Helper-Funktion `get_device_info()` erstellen | `const.py` oder `device.py` |
| 3 | `IsalEasyHomeySensor.__init__` um `coordinator_key` erweitern | `sensor.py` |
| 4 | Alle spezialisierten Sensor-Klassen anpassen | `sensor.py` |
| 5 | `async_setup_entry` in `sensor.py` anpassen (coordinator_key mitgeben) | `sensor.py` |
| 6 | `IsalEasyHomeyBinarySensor.__init__` um `coordinator_key` erweitern | `binary_sensor.py` |
| 7 | `async_setup_entry` in `binary_sensor.py` anpassen | `binary_sensor.py` |
| 8 | Alte `MODEL`-Konstante entfernen | `const.py` |
| 9 | Version-Bump | `manifest.json` |
| 10 | Testen & verifizieren | – |

---

## Erwartetes Ergebnis in Home Assistant

Nach dem Umbau sieht die Device-Übersicht wie folgt aus:

```
Geräte & Dienste → IsAl Easy Homey
│
├── Easy Homey                    [API Gateway]
│   └── sensor.service_uptime
│
├── Easy Homey Tankstellen        [Petrol Station]
│   ├── sensor.nearest_station
│   ├── sensor.cheapest_station_e5
│   ├── sensor.cheapest_station_e10
│   ├── sensor.cheapest_station_diesel
│   ├── sensor.nearest_station_{user}
│   └── sensor.station_{id}
│
├── Easy Homey Wetterwarnungen    [Weather Warnings]
│   ├── sensor.current_weather_warning
│   ├── sensor.current_upfront_warning
│   ├── sensor.all_weather_warnings_json
│   ├── sensor.all_upfront_warnings_json
│   ├── binary_sensor.weather_warning_active
│   └── binary_sensor.upfront_warning_active
│
├── Easy Homey Pollenflug         [Pollen Flight]
│   ├── sensor.highest_pollen_severity
│   ├── sensor.pollen_alder ... (×8)
│   └── binary_sensor.pollen_flight_active
│
└── Easy Homey Abfallkalender     [Waste Collection]
    ├── sensor.next_waste_collection
    └── sensor.waste_paper ... (×5)
```

---

## Testplan

1. **Clean Install**: Neue Installation → 5 Devices korrekt erstellt, Hub-Hierarchie vorhanden
2. **Upgrade**: Bestehende Installation → Entities behalten ihre IDs, altes Device wird zum Hub
3. **Automationen**: Bestehende Automationen funktionieren weiterhin
4. **Options Flow**: Änderungen in den Optionen → Devices bleiben stabil
5. **Reload**: Integration neu laden → Devices bleiben korrekt zugeordnet
6. **Device-Seite**: Jedes Sub-Device zeigt "Über: Easy Homey" an (via_device)

