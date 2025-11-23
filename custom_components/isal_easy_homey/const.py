"""Constants for the isal Easy Homey integration."""
from typing import Final

# Integration domain
DOMAIN: Final = "isal_easy_homey"

# Configuration keys
CONF_API_BASE_URL: Final = "api_base_url"
CONF_LOCATION_ENTITY_ID: Final = "location_entity_id"
CONF_LOCATION_ENTITY_ID_CHEAPEST: Final = "location_entity_id_cheapest"
CONF_LOCATION_ENTITY_ID_NEAREST: Final = "location_entity_id_nearest"
CONF_USER_LOCATIONS: Final = "user_locations"
CONF_WARNING_CELL_ID: Final = "warning_cell_id"
CONF_SEARCH_RADIUS: Final = "search_radius"
CONF_STATION_ID: Final = "station_id"
CONF_PETROL_TYPE: Final = "petrol_type"

# Update intervals
CONF_UPDATE_INTERVAL_PETROL: Final = "update_interval_petrol"
CONF_UPDATE_INTERVAL_WEATHER: Final = "update_interval_weather"
CONF_UPDATE_INTERVAL_POLLEN: Final = "update_interval_pollen"
CONF_UPDATE_INTERVAL_WASTE: Final = "update_interval_waste"

# Default values
DEFAULT_API_BASE_URL: Final = "http://192.168.178.31:8080/v1"
DEFAULT_WARNING_CELL_ID: Final = "809177119"
DEFAULT_SEARCH_RADIUS: Final = 15.0
DEFAULT_PETROL_TYPE: Final = "E5"

# Default update intervals (in minutes)
DEFAULT_UPDATE_INTERVAL_PETROL: Final = 5
DEFAULT_UPDATE_INTERVAL_WEATHER: Final = 10
DEFAULT_UPDATE_INTERVAL_POLLEN: Final = 30
DEFAULT_UPDATE_INTERVAL_WASTE: Final = 30

# Update interval limits
MIN_SEARCH_RADIUS: Final = 0.1
MAX_SEARCH_RADIUS: Final = 25.0

# Coordinator names
COORDINATOR_PETROL: Final = "petrol_station"
COORDINATOR_WEATHER: Final = "weather_warning"
COORDINATOR_POLLEN: Final = "pollen_flight"
COORDINATOR_WASTE: Final = "waste_collection"

# Device info
MANUFACTURER: Final = "isal"
MODEL: Final = "Easy Homey API Integration"

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

# Platforms
PLATFORMS: Final = ["sensor", "binary_sensor"]

