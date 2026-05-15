# Plan: Integration Water Softener & Water Control Devices

Zwei neue Devices (**Wasserentkalkungsanlage** mit 28 Entitäten, **Wasserkontrolle** mit 6 Entitäten) in die bestehende `isal_easy_homey` Integration einbinden. Erfordert API-Erweiterung um POST-Support, zwei neue Coordinators, und drei neue Plattformen (`select`, `button`, `switch`).

---

## Entitäten-Übersicht

### Device 1: Wasserentkalkungsanlage (Water Softener)
Datenquelle: `GET /water/softener` (operationId: `getWaterSoftenerData`)

| #  | Entität (DE)                         | Key                                     | JSON-Pfad                                    | Typ      | Einheit | Umrechnung          | Icon                                                       | Plattform          | Steuerbar?                             |
|----|--------------------------------------|-----------------------------------------|----------------------------------------------|----------|---------|---------------------|------------------------------------------------------------|--------------------|----------------------------------------|
| 1  | Gerätestatus                         | `water_softener_device_status`          | `deviceStatus`                               | string   | -       | -                   | dynamisch aus `deviceStatusIcon.mdiIcon`                   | sensor             | nein                                   |
| 2  | Software Version                     | `water_softener_software_version`       | `softwareVersion`                            | string   | -       | -                   | `mdi:tag`                                                  | sensor             | nein                                   |
| 3  | Hardware Version                     | `water_softener_hardware_version`       | `hardwareVersion`                            | string   | -       | -                   | `mdi:tag`                                                  | sensor             | nein                                   |
| 4  | Connectivity Module Firmware Version | `water_softener_gateway_firmware`       | `gatewayFirmwareVersion`                     | string   | -       | -                   | `mdi:tag`                                                  | sensor             | nein                                   |
| 5  | Connectivity Module Hardware Version | `water_softener_gateway_hardware`       | `gatewayHardwareVersion`                     | string   | -       | -                   | `mdi:tag`                                                  | sensor             | nein                                   |
| 6  | Betriebsstunden                      | `water_softener_operating_time`         | `operatingTimeSeconds`                       | number   | h       | Sek → Std (/3600)   | `mdi:clock-outline`                                        | sensor             | nein                                   |
| 7  | Uptime                               | `water_softener_uptime`                 | `uptimeSeconds`                              | number   | h       | Sek → Std (/3600)   | `mdi:timer-outline`                                        | sensor             | nein                                   |
| 8  | Wasserszene                          | `water_softener_water_scene`            | `waterScene`                                 | enum     | -       | -                   | dynamisch aus `waterSceneIcon`                             | **select**         | **JA** → `POST changeWaterScene`       |
| 9  | Rohwasserhärte                       | `water_softener_raw_hardness`           | `waterHardness.rawHardnessDH`                | number   | °dH     | -                   | `mdi:water`                                                | sensor             | nein                                   |
| 10 | Wunschwasserhärte                    | `water_softener_desired_hardness`       | `waterHardness.desiredHardnessDH`            | number   | °dH     | -                   | `mdi:water`                                                | sensor             | nein                                   |
| 11 | Notstrom Batterie Ladestand          | `water_softener_battery_capacity`       | `batteryCapacity.percentage`                 | number   | %       | -                   | dynamisch `mdi:battery-XX`                                 | sensor             | nein                                   |
| 12 | Notstrom Batterie Restlaufzeit       | `water_softener_battery_remaining`      | `batteryCapacity.remainingTimeSeconds`       | number   | min     | Sek → Min (/60)     | `mdi:battery-clock-outline`                                | sensor             | nein                                   |
| 13 | Verbleibender Salzvorrat             | `water_softener_salt_level_percent`     | `saltLevel.saltLevelPercent`                 | number   | %       | -                   | dynamisch gauge-Icons                                      | sensor             | nein                                   |
| 14 | Aktueller Salzvorrat                 | `water_softener_salt_level_kg`          | `saltLevel.saltLevelGrams`                   | number   | kg      | g → kg (/1000)      | `mdi:shaker-outline`                                       | sensor             | nein                                   |
| 15 | Salzreichweite                       | `water_softener_salt_range`             | `saltLevel.saltRangeDays`                    | number   | d       | -                   | `mdi:chevron-triple-right`                                 | sensor             | nein                                   |
| 16 | Tage bis zur nächsten Wartung        | `water_softener_maintenance_days`       | `maintenance.daysUntilNext`                  | number   | d       | -                   | `mdi:wrench-clock`                                         | sensor             | nein                                   |
| 17 | Durchgeführte Wartungen              | `water_softener_maintenance_registered` | `maintenance.registeredMaintenances`         | number   | -       | -                   | `mdi:account-wrench`                                       | sensor             | nein                                   |
| 18 | Angeforderte Wartungen               | `water_softener_maintenance_requested`  | `maintenance.requestedMaintenances`          | number   | -       | -                   | `mdi:cog-counterclockwise`                                 | sensor             | nein                                   |
| 19 | Regenerationsstatus                  | `water_softener_regenerating`           | `regeneration.isRegenerating`                | bool     | -       | -                   | `mdi:water-sync`                                           | **binary_sensor**  | nein                                   |
| 20 | Anzahl Regenerationen                | `water_softener_regeneration_count`     | `regeneration.totalRegenerationCount`        | number   | -       | -                   | `mdi:counter`                                              | sensor             | nein                                   |
| 21 | Absperrventil (Softener)             | `water_softener_shutoff_valve`          | `leakageProtection.shutoffValveStatus`       | string   | -       | -                   | dynamisch aus `leakageProtection.shutoffValveIcon.mdiIcon` | sensor             | nein (nur lesend!)                     |
| 22 | Max. Durchfluss pro Stunde           | `water_softener_max_flow_rate`          | `leakageProtection.maxFlowRateLiterPerHour`  | number   | L/h     | -                   | `mdi:waves-arrow-up`                                       | sensor             | nein                                   |
| 23 | Max. Entnahmemenge                   | `water_softener_max_extraction_volume`  | `leakageProtection.maxExtractionVolumeLiter` | number   | L       | -                   | `mdi:cup-water`                                            | sensor             | nein                                   |
| 24 | Max. Entnahmezeit                    | `water_softener_max_extraction_time`    | `leakageProtection.maxExtractionTimeMinutes` | number   | h       | Min → Std (/60)     | `mdi:clock-end`                                            | sensor             | nein                                   |
| 25 | Kleinleckageprüfung                  | `water_softener_micro_leakage_check`    | `leakageProtection.microLeakageCheck`        | string   | -       | -                   | `mdi:pipe-leak`                                            | sensor             | nein                                   |
| 26 | Kleinleckageprüfung starten          | `water_softener_micro_leakage_start`    | - (Button)                                   | -        | -       | -                   | `mdi:clock-start`                                          | **button**         | **JA** → `POST startMicroLeakageCheck` |
| 27 | Kleinleckage Status                  | `water_softener_micro_leakage_status`   | `leakageProtection.microLeakageStatus`       | string   | -       | -                   | `mdi:pipe-leak`                                            | sensor             | nein                                   |
| 28 | Letzte Aktualisierung                | `water_softener_last_updated`           | `lastUpdatedOn`                              | datetime | -       | ISO 8601 → datetime | `mdi:update`                                               | sensor (TIMESTAMP) | nein                                   |

### Device 2: Wasserkontrolle (Water Control)
Datenquelle: `GET /water/control` (operationId: `getWaterControlStatus`)

| # | Entität (DE) | Key | JSON-Pfad | Typ | Einheit | Umrechnung | Icon | Plattform | Steuerbar? |
|---|-------------|-----|-----------|-----|---------|------------|------|-----------|-----------|
| 1 | Aktueller Durchfluss | `water_control_flow_rate` | `currentFlowRate` | number | L/h | - | `mdi:waves-arrow-right` | sensor | nein |
| 2 | Gesamtwasserverbrauch | `water_control_total_consumption` | `totalWaterConsumption` | number | m³ | L → m³ (/1000) | `mdi:water` | sensor (WATER, TOTAL_INCREASING) | nein |
| 3 | Aufbereitetes Wasser | `water_control_treated_consumption` | `treatedWaterConsumption` | number | m³ | L → m³ (/1000) | `mdi:water-check` | sensor (WATER, TOTAL_INCREASING) | nein |
| 4 | Hartes Wasser | `water_control_untreated_consumption` | `untreatedWaterConsumption` | number | m³ | L → m³ (/1000) | `mdi:water-alert` | sensor (WATER, TOTAL_INCREASING) | nein |
| 5 | Absperrventil | `water_control_shutoff_valve` | `shutoffValveStatus` | toggle | - | - | dynamisch aus `shutoffValveIcon.mdiIcon` | **switch** | **JA** → `POST controlShutoffValve` (Toggle) |
| 6 | Letzte Aktualisierung | `water_control_last_updated` | `lastUpdatedOn` | datetime | - | ISO 8601 → datetime | `mdi:update` | sensor (TIMESTAMP) | nein |

---

## Implementierungsschritte

### Schritt 1: `const.py` erweitern

Neue Konstanten:
```python
# Coordinator-Keys
COORDINATOR_WATER_SOFTENER: Final = "water_softener"
COORDINATOR_WATER_CONTROL: Final = "water_control"

# Device Models
MODEL_WATER_SOFTENER: Final = "Water Softener"
MODEL_WATER_CONTROL: Final = "Water Control"

# Device Names
DEVICE_NAME_WATER_SOFTENER: Final = "Easy Homey Wasserentkalkungsanlage"
DEVICE_NAME_WATER_CONTROL: Final = "Easy Homey Wasserkontrolle"

# Update Intervals
CONF_UPDATE_INTERVAL_WATER_SOFTENER: Final = "update_interval_water_softener"
CONF_UPDATE_INTERVAL_WATER_CONTROL: Final = "update_interval_water_control"
DEFAULT_UPDATE_INTERVAL_WATER_SOFTENER: Final = 5
DEFAULT_UPDATE_INTERVAL_WATER_CONTROL: Final = 5

# API Endpoints
ENDPOINT_WATER_SOFTENER: Final = "/water/softener"
ENDPOINT_WATER_SOFTENER_SCENE: Final = "/water/softener/water-scene"
ENDPOINT_WATER_SOFTENER_LEAKAGE_CHECK: Final = "/water/softener/micro-leakage-check"
ENDPOINT_WATER_CONTROL: Final = "/water/control"
ENDPOINT_WATER_CONTROL_VALVE: Final = "/water/control/shutoff-valve"

# Enum-Konstanten
WATER_SCENES: Final = ["NORMAL", "SHOWER", "WATERING", "HEATER", "WASHING"]
SHUTOFF_VALVE_STATUSES: Final = ["OPEN", "CLOSED"]
```

`PLATFORMS` erweitern um `"select"`, `"button"`, `"switch"`.

`get_device_info()` Mapping ergänzen:
```
COORDINATOR_WATER_SOFTENER → (DEVICE_NAME_WATER_SOFTENER, MODEL_WATER_SOFTENER)
COORDINATOR_WATER_CONTROL → (DEVICE_NAME_WATER_CONTROL, MODEL_WATER_CONTROL)
```

---

### Schritt 2: `api.py` erweitern

**`_request` Methode um JSON-Body-Support erweitern:**
- Neuer optionaler Parameter `json_body: dict[str, Any] | None = None`
- Im `session.request()`-Aufruf: `json=json_body` wenn vorhanden

**Neue API-Methoden:**

| Methode | HTTP | Endpoint | Body |
|---------|------|----------|------|
| `get_water_softener_data()` | GET | `/water/softener` | - |
| `change_water_scene(water_scene: str)` | POST | `/water/softener/water-scene` | `{"waterScene": water_scene}` |
| `start_micro_leakage_check()` | POST | `/water/softener/micro-leakage-check` | - |
| `get_water_control_data()` | GET | `/water/control` | - |
| `control_shutoff_valve(new_status: str)` | POST | `/water/control/shutoff-valve` | `{"newStatus": new_status}` |

---

### Schritt 3: `coordinator.py` erweitern

Zwei neue Klassen analog zu `ServiceInfoCoordinator`:

- **`WaterSoftenerCoordinator`**: ruft `client.get_water_softener_data()` auf
- **`WaterControlCoordinator`**: ruft `client.get_water_control_data()` auf

---

### Schritt 4: `__init__.py` erweitern

- Neue Imports für Konstanten und Coordinators
- `PLATFORMS` um `Platform.SELECT`, `Platform.BUTTON`, `Platform.SWITCH` erweitern
- Neue Coordinators im `coordinators` Dict instanziieren:
  ```python
  COORDINATOR_WATER_SOFTENER: WaterSoftenerCoordinator(hass, client, timedelta(...), entry)
  COORDINATOR_WATER_CONTROL: WaterControlCoordinator(hass, client, timedelta(...), entry)
  ```

---

### Schritt 5: `sensor.py` erweitern

- Neues Tuple `WATER_SOFTENER_SENSORS` (s. Entitäten-Tabelle oben, alle nicht-steuerbaren, nicht-binären Sensoren)
- Neues Tuple `WATER_CONTROL_SENSORS` (s. Entitäten-Tabelle oben)
- In `async_setup_entry`: Neue Sensoren über `IsalEasyHomeySensor` mit korrektem Coordinator-Key erstellen

**Dynamische Icons:**
- **Batterie**: `mdi:battery` (100), `mdi:battery-90`, ..., `mdi:battery-10`, `mdi:battery-alert` (0-5%)
- **Salzvorrat**: `mdi:gauge-full` (>75%), `mdi:gauge` (50-75%), `mdi:gauge-low` (25-50%), `mdi:gauge-empty` (<25%)

---

### Schritt 6: `binary_sensor.py` erweitern

Neues Tuple `WATER_SOFTENER_BINARY_SENSORS`:
- `water_softener_regenerating`: `data.get("regeneration", {}).get("isRegenerating", False)`
- Icon: `mdi:water-sync` (on) / `mdi:water-sync-outline` (off)

---

### Schritt 7: Neue Datei `select.py` erstellen

**`IsalEasyHomeyWaterSceneSelect`** (CoordinatorEntity + SelectEntity):
- Options: `["NORMAL", "SHOWER", "WATERING", "HEATER", "WASHING"]`
- `current_option`: aus `coordinator.data.get("waterScene")`
- `icon`: dynamisch nach aktiver Szene (NORMAL→faucet, SHOWER→shower, etc.)
- `async_select_option(option)`:
  1. `await coordinator.client.change_water_scene(option)` – bei Exception abbrechen, nichts ändern
  2. **Optimistic Update:** `self.coordinator.data["waterScene"] = option`
  3. `self.async_write_ha_state()` – sofort neuen State in HA anzeigen
  4. `await self.coordinator.async_request_refresh()` – echte Daten nachladen
- Device: `COORDINATOR_WATER_SOFTENER`

---

### Schritt 8: Neue Datei `button.py` erstellen

**`IsalEasyHomeyMicroLeakageCheckButton`** (CoordinatorEntity + ButtonEntity):
- Icon: `mdi:clock-start`
- `async_press()`:
  1. `await coordinator.client.start_micro_leakage_check()` – bei Exception abbrechen
  2. **Optimistic Update:** `self.coordinator.data["leakageProtection"]["microLeakageCheck"] = "RUNNING"`
  3. `self.async_write_ha_state()`
  4. `await self.coordinator.async_request_refresh()`
- Device: `COORDINATOR_WATER_SOFTENER`

---

### Schritt 9: Neue Datei `switch.py` erstellen

**`IsalEasyHomeyShutoffValveSwitch`** (CoordinatorEntity + SwitchEntity):
- `is_on`: `coordinator.data.get("shutoffValveStatus") == "OPEN"`
- `icon`: dynamisch aus `shutoffValveIcon.mdiIcon` oder `mdi:valve-open`/`mdi:valve-closed`
- `async_turn_on()`:
  1. `await coordinator.client.control_shutoff_valve("OPEN")` – bei Exception abbrechen
  2. **Optimistic Update:** `self.coordinator.data["shutoffValveStatus"] = "OPEN"`
  3. `self.async_write_ha_state()`
  4. `await self.coordinator.async_request_refresh()`
- `async_turn_off()`:
  1. `await coordinator.client.control_shutoff_valve("CLOSED")` – bei Exception abbrechen
  2. **Optimistic Update:** `self.coordinator.data["shutoffValveStatus"] = "CLOSED"`
  3. `self.async_write_ha_state()`
  4. `await self.coordinator.async_request_refresh()`
- Device: `COORDINATOR_WATER_CONTROL`

---

### Schritt 10: Übersetzungen erweitern

`translations/de.json`, `translations/en.json`, `strings.json`:
- Abschnitte `entity.sensor`, `entity.binary_sensor`, `entity.select`, `entity.button`, `entity.switch` ergänzen
- Alle neuen Entity-Keys mit passenden deutschen/englischen Bezeichnungen
- Optional: `options.step` für Update-Intervall-Konfiguration

---

### Schritt 11: `manifest.json` aktualisieren

- Version von `"1.1.0"` auf `"1.2.0"` bumpen

---

## Designentscheidungen

### Optimistic Updates nach POST-Requests
Nach einem erfolgreichen POST-Request (HTTP 200) wird der lokale Coordinator-State **sofort optimistisch aktualisiert**, ohne auf den nächsten regulären Poll zu warten. Ablauf:

1. POST-Request an die API senden
2. **Nur bei erfolgreicher Antwort (kein Exception):** Den lokalen `coordinator.data` optimistisch patchen
3. `self.async_write_ha_state()` aufrufen, damit HA sofort den neuen State anzeigt
4. Danach `await self.coordinator.async_request_refresh()` aufrufen, um beim nächsten Zyklus die echten Daten von der API zu holen

**Konkret für jede steuerbare Entität:**

- **Select (Wasserszene):** Nach erfolgreichem `change_water_scene(option)` → `coordinator.data["waterScene"] = option` setzen
- **Switch (Absperrventil):** Nach erfolgreichem `control_shutoff_valve(new_status)` → `coordinator.data["shutoffValveStatus"] = new_status` setzen
- **Button (Kleinleckageprüfung):** Nach erfolgreichem `start_micro_leakage_check()` → `coordinator.data["leakageProtection"]["microLeakageCheck"] = "RUNNING"` setzen

Bei einem **fehlgeschlagenen** POST-Request (Exception) wird **nichts** am lokalen State geändert – der alte State bleibt bestehen und der Fehler wird geloggt.


