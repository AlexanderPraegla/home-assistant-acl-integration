"""The isal Easy Homey integration."""
from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import IsalEasyHomeyApiClient
from .const import (
    CONF_API_BASE_URL,
    CONF_LOCATION_ENTITY_ID,
    CONF_LOCATION_ENTITY_ID_CHEAPEST,
    CONF_LOCATION_ENTITY_ID_NEAREST,
    CONF_USER_LOCATIONS,
    CONF_PETROL_TYPE,
    CONF_SEARCH_RADIUS,
    CONF_UPDATE_INTERVAL_PETROL,
    CONF_UPDATE_INTERVAL_POLLEN,
    CONF_UPDATE_INTERVAL_WASTE,
    CONF_UPDATE_INTERVAL_WEATHER,
    CONF_WARNING_CELL_ID,
    COORDINATOR_PETROL,
    COORDINATOR_POLLEN,
    COORDINATOR_WASTE,
    COORDINATOR_WEATHER,
    DEFAULT_PETROL_TYPE,
    DEFAULT_SEARCH_RADIUS,
    DEFAULT_UPDATE_INTERVAL_PETROL,
    DEFAULT_UPDATE_INTERVAL_POLLEN,
    DEFAULT_UPDATE_INTERVAL_WASTE,
    DEFAULT_UPDATE_INTERVAL_WEATHER,
    DEFAULT_WARNING_CELL_ID,
    DOMAIN,
)
from .coordinator import (
    PetrolStationCoordinator,
    PollenFlightCoordinator,
    WasteCollectionCoordinator,
    WeatherWarningCoordinator,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BINARY_SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up isal Easy Homey from a config entry.

    Args:
        hass: The Home Assistant instance
        entry: The config entry

    Returns:
        True if setup was successful

    """
    hass.data.setdefault(DOMAIN, {})

    # Create API client
    session = async_get_clientsession(hass)
    client = IsalEasyHomeyApiClient(entry.data[CONF_API_BASE_URL], session)

    # Get configuration values
    # Support both old (single location) and new (separate locations) config
    location_entity_id_cheapest = entry.data.get(CONF_LOCATION_ENTITY_ID_CHEAPEST) or entry.data.get(CONF_LOCATION_ENTITY_ID)
    location_entity_id_nearest = entry.data.get(CONF_LOCATION_ENTITY_ID_NEAREST) or entry.data.get(CONF_LOCATION_ENTITY_ID)
    user_locations = entry.options.get(CONF_USER_LOCATIONS, entry.data.get(CONF_USER_LOCATIONS, []))

    warning_cell_id = entry.options.get(
        CONF_WARNING_CELL_ID, entry.data.get(CONF_WARNING_CELL_ID, DEFAULT_WARNING_CELL_ID)
    )
    search_radius = entry.options.get(
        CONF_SEARCH_RADIUS, entry.data.get(CONF_SEARCH_RADIUS, DEFAULT_SEARCH_RADIUS)
    )

    # Get update intervals
    update_interval_petrol = entry.options.get(
        CONF_UPDATE_INTERVAL_PETROL, DEFAULT_UPDATE_INTERVAL_PETROL
    )
    update_interval_weather = entry.options.get(
        CONF_UPDATE_INTERVAL_WEATHER, DEFAULT_UPDATE_INTERVAL_WEATHER
    )
    update_interval_pollen = entry.options.get(
        CONF_UPDATE_INTERVAL_POLLEN, DEFAULT_UPDATE_INTERVAL_POLLEN
    )
    update_interval_waste = entry.options.get(
        CONF_UPDATE_INTERVAL_WASTE, DEFAULT_UPDATE_INTERVAL_WASTE
    )

    # Create coordinators
    coordinators = {
        COORDINATOR_PETROL: PetrolStationCoordinator(
            hass,
            client,
            location_entity_id_cheapest,
            location_entity_id_nearest,
            user_locations,
            search_radius,
            timedelta(minutes=update_interval_petrol),
            entry,
        ),
        COORDINATOR_WEATHER: WeatherWarningCoordinator(
            hass,
            client,
            warning_cell_id,
            timedelta(minutes=update_interval_weather),
            entry,
        ),
        COORDINATOR_POLLEN: PollenFlightCoordinator(
            hass,
            client,
            timedelta(minutes=update_interval_pollen),
            entry,
        ),
        COORDINATOR_WASTE: WasteCollectionCoordinator(
            hass,
            client,
            timedelta(minutes=update_interval_waste),
            entry,
        ),
    }

    # Fetch initial data
    for coordinator in coordinators.values():
        await coordinator.async_config_entry_first_refresh()

    # Store coordinators and client
    hass.data[DOMAIN][entry.entry_id] = {
        "client": client,
        "coordinators": coordinators,
    }

    # Setup platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Setup options update listener
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry.

    Args:
        hass: The Home Assistant instance
        entry: The config entry

    Returns:
        True if unload was successful

    """
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry.

    Args:
        hass: The Home Assistant instance
        entry: The config entry

    """
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)

