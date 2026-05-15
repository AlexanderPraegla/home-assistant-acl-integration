"""Constants for the isal Easy Homey integration."""
from typing import Final

# Integration domain
DOMAIN: Final = "isal_easy_homey"

# Configuration keys
CONF_API_BASE_URL: Final = "api_base_url"
CONF_API_KEY: Final = "api_key"
CONF_LOCATION_ENTITY_ID: Final = "location_entity_id"
CONF_LOCATION_ENTITY_ID_CHEAPEST: Final = "location_entity_id_cheapest"
CONF_LOCATION_ENTITY_ID_NEAREST: Final = "location_entity_id_nearest"
CONF_USER_LOCATIONS: Final = "user_locations"
CONF_STATION_IDS: Final = "station_ids"
CONF_WARNING_CELL_ID: Final = "warning_cell_id"
CONF_SEARCH_RADIUS: Final = "search_radius"
CONF_STATION_ID: Final = "station_id"
CONF_PETROL_TYPE: Final = "petrol_type"

# Update intervals
CONF_UPDATE_INTERVAL_PETROL: Final = "update_interval_petrol"
CONF_UPDATE_INTERVAL_WEATHER: Final = "update_interval_weather"
CONF_UPDATE_INTERVAL_POLLEN: Final = "update_interval_pollen"
CONF_UPDATE_INTERVAL_WASTE: Final = "update_interval_waste"
CONF_UPDATE_INTERVAL_SERVICE_INFO: Final = "update_interval_service_info"
CONF_UPDATE_INTERVAL_WATER_SOFTENER: Final = "update_interval_water_softener"
CONF_UPDATE_INTERVAL_WATER_CONTROL: Final = "update_interval_water_control"

# Default values
DEFAULT_API_BASE_URL: Final = "https://easy-homey.local.isal-home.de/v1"
DEFAULT_WARNING_CELL_ID: Final = "809177119"
DEFAULT_SEARCH_RADIUS: Final = 15.0
DEFAULT_PETROL_TYPE: Final = "E5"

# Default update intervals (in minutes)
DEFAULT_UPDATE_INTERVAL_PETROL: Final = 5
DEFAULT_UPDATE_INTERVAL_WEATHER: Final = 10
DEFAULT_UPDATE_INTERVAL_POLLEN: Final = 30
DEFAULT_UPDATE_INTERVAL_WASTE: Final = 30
DEFAULT_UPDATE_INTERVAL_SERVICE_INFO: Final = 5
DEFAULT_UPDATE_INTERVAL_WATER_SOFTENER: Final = 30  # Seconds
DEFAULT_UPDATE_INTERVAL_WATER_CONTROL: Final = 30  # Seconds

# Update interval limits
MIN_SEARCH_RADIUS: Final = 0.1
MAX_SEARCH_RADIUS: Final = 25.0

# Coordinator names
COORDINATOR_PETROL: Final = "petrol_station"
COORDINATOR_WEATHER: Final = "weather_warning"
COORDINATOR_POLLEN: Final = "pollen_flight"
COORDINATOR_WASTE: Final = "waste_collection"
COORDINATOR_SERVICE_INFO: Final = "service_info"
COORDINATOR_WATER_SOFTENER: Final = "water_softener"
COORDINATOR_WATER_CONTROL: Final = "water_control"

# Device info
MANUFACTURER: Final = "isal"

# Device models
MODEL_GATEWAY: Final = "API Gateway"
MODEL_PETROL: Final = "Petrol Station"
MODEL_WEATHER: Final = "Weather Warnings"
MODEL_POLLEN: Final = "Pollen Flight"
MODEL_WASTE: Final = "Waste Collection"
MODEL_WATER_SOFTENER: Final = "Water Softener"
MODEL_WATER_CONTROL: Final = "Water Control"

# Device names
DEVICE_NAME_HUB: Final = "Easy Homey"
DEVICE_NAME_PETROL: Final = "Easy Homey Tankstellen"
DEVICE_NAME_WEATHER: Final = "Easy Homey Wetterwarnungen"
DEVICE_NAME_POLLEN: Final = "Easy Homey Pollenflug"
DEVICE_NAME_WASTE: Final = "Easy Homey Abfallkalender"
DEVICE_NAME_WATER_SOFTENER: Final = "Easy Homey Wasserentkalkungsanlage"
DEVICE_NAME_WATER_CONTROL: Final = "Easy Homey Wasserkontrolle"

# Petrol types
PETROL_TYPES: Final = ["E5", "E10", "DIESEL"]

# Pollen types
POLLEN_TYPES: Final = {
    "ALDER": "alder",
    "AMBROSIA": "ambrosia",
    "ASH_TREE": "ash_tree",
    "BIRCH": "birch",
    "GRASSES": "grasses",
    "HAZEL": "hazel",
    "MUGWORT": "mugwort",
    "RYE": "rye",
}

# Waste types
WASTE_TYPES: Final = {
    "PAPER": "paper",
    "BIO": "bio",
    "GENERAL": "general",
    "YELLOW_BAG": "yellow_bag",
    "PROBLEM": "problem",
}

# Weather warning types
WEATHER_WARNING_TYPE_WARNING: Final = "WARNING"
WEATHER_WARNING_TYPE_UPFRONT: Final = "UPFRONT_INFORMATION"

# API endpoints
ENDPOINT_PETROL_STATION: Final = "/patrol-stations/{station_id}"
ENDPOINT_PETROL_STATIONS_SEARCH: Final = "/patrol-stations"
ENDPOINT_PETROL_STATIONS_CHEAPEST: Final = "/patrol-stations/cheapest"
ENDPOINT_POLLEN_FLIGHT: Final = "/weather/pollen-flight"
ENDPOINT_POLLEN_FLIGHT_HIGHEST: Final = "/weather/pollen-flight/highest"
ENDPOINT_WEATHER_WARNINGS: Final = "/weather/warnings"
ENDPOINT_WASTE_COLLECTION_ALL: Final = "/waste-collection"
ENDPOINT_WASTE_COLLECTION_UPCOMING: Final = "/waste-collection/upcoming-collections"
ENDPOINT_WASTE_COLLECTION_NEXT: Final = "/waste-collection/next-collection"
ENDPOINT_WATER_SOFTENER: Final = "/water/softener"
ENDPOINT_WATER_SOFTENER_SCENE: Final = "/water/softener/water-scene"
ENDPOINT_WATER_SOFTENER_LEAKAGE_CHECK: Final = "/water/softener/micro-leakage-check"
ENDPOINT_WATER_CONTROL: Final = "/water/control"
ENDPOINT_WATER_CONTROL_VALVE: Final = "/water/control/shutoff-valve"

# Water scene enum constants
WATER_SCENES: Final = ["NORMAL", "SHOWER", "WATERING", "HEATER", "WASHING"]
SHUTOFF_VALVE_STATUSES: Final = ["OPEN", "CLOSED"]

# Platforms
PLATFORMS: Final = ["sensor", "binary_sensor", "select", "button", "switch"]


def get_device_info(entry_id: str, coordinator_key: str) -> dict:
    """Get device info dict for given coordinator key."""
    mapping = {
        COORDINATOR_PETROL: (DEVICE_NAME_PETROL, MODEL_PETROL),
        COORDINATOR_WEATHER: (DEVICE_NAME_WEATHER, MODEL_WEATHER),
        COORDINATOR_POLLEN: (DEVICE_NAME_POLLEN, MODEL_POLLEN),
        COORDINATOR_WASTE: (DEVICE_NAME_WASTE, MODEL_WASTE),
        COORDINATOR_SERVICE_INFO: (DEVICE_NAME_HUB, MODEL_GATEWAY),
        COORDINATOR_WATER_SOFTENER: (DEVICE_NAME_WATER_SOFTENER, MODEL_WATER_SOFTENER),
        COORDINATOR_WATER_CONTROL: (DEVICE_NAME_WATER_CONTROL, MODEL_WATER_CONTROL),
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
