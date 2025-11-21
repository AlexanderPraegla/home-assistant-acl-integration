"""Data Update Coordinators for isal Easy Homey integration."""
from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import IsalEasyHomeyApiClient, IsalEasyHomeyApiError
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


def get_coordinates_from_entity(
    hass: HomeAssistant, entity_id: str | None
) -> tuple[float, float] | None:
    """Get latitude and longitude from entity.

    Args:
        hass: The Home Assistant instance
        entity_id: The entity ID to get coordinates from

    Returns:
        Tuple of (latitude, longitude) or None if not available

    """
    if not entity_id:
        return None

    state = hass.states.get(entity_id)
    if state is None:
        _LOGGER.warning("Entity %s not found", entity_id)
        return None

    latitude = state.attributes.get("latitude")
    longitude = state.attributes.get("longitude")

    if latitude is None or longitude is None:
        _LOGGER.warning("Entity %s does not have location attributes", entity_id)
        return None

    return (float(latitude), float(longitude))


class PetrolStationCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator for petrol station data."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: IsalEasyHomeyApiClient,
        location_entity_id: str | None,
        search_radius: float,
        petrol_type: str,
        update_interval: timedelta,
    ) -> None:
        """Initialize the coordinator.

        Args:
            hass: The Home Assistant instance
            client: The API client
            location_entity_id: Entity ID to get coordinates from
            search_radius: Search radius in km
            petrol_type: Petrol type for cheapest station
            update_interval: Update interval

        """
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_petrol_station",
            update_interval=update_interval,
        )
        self.client = client
        self.location_entity_id = location_entity_id
        self.search_radius = search_radius
        self.petrol_type = petrol_type

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API.

        Returns:
            Dictionary with petrol station data

        Raises:
            UpdateFailed: If update fails

        """
        try:
            data: dict[str, Any] = {}

            # Get coordinates if entity is configured
            coordinates = get_coordinates_from_entity(self.hass, self.location_entity_id)

            if coordinates:
                latitude, longitude = coordinates

                # Get all stations in radius
                stations = await self.client.search_petrol_stations(
                    latitude, longitude, self.search_radius
                )
                data["all_stations"] = stations

                # Get nearest station
                if stations:
                    nearest = min(
                        stations, key=lambda x: x.get("location", {}).get("distance", float("inf"))
                    )
                    data["nearest_station"] = nearest

                # Get cheapest station
                cheapest = await self.client.get_cheapest_petrol_station(
                    latitude, longitude, self.search_radius, self.petrol_type
                )
                data["cheapest_station"] = cheapest

            return data

        except IsalEasyHomeyApiError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err


class WeatherWarningCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator for weather warning data."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: IsalEasyHomeyApiClient,
        warning_cell_id: str,
        update_interval: timedelta,
    ) -> None:
        """Initialize the coordinator.

        Args:
            hass: The Home Assistant instance
            client: The API client
            warning_cell_id: Warning cell ID
            update_interval: Update interval

        """
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_weather_warning",
            update_interval=update_interval,
        )
        self.client = client
        self.warning_cell_id = warning_cell_id

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API.

        Returns:
            Dictionary with weather warning data

        Raises:
            UpdateFailed: If update fails

        """
        try:
            # Get warnings
            warnings = await self.client.get_weather_warnings(
                self.warning_cell_id, "WARNING"
            )

            # Get upfront information
            upfront = await self.client.get_weather_warnings(
                self.warning_cell_id, "UPFRONT_INFORMATION"
            )

            return {
                "warnings": warnings,
                "upfront": upfront,
            }

        except IsalEasyHomeyApiError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err


class PollenFlightCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator for pollen flight data."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: IsalEasyHomeyApiClient,
        update_interval: timedelta,
    ) -> None:
        """Initialize the coordinator.

        Args:
            hass: The Home Assistant instance
            client: The API client
            update_interval: Update interval

        """
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_pollen_flight",
            update_interval=update_interval,
        )
        self.client = client

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API.

        Returns:
            Dictionary with pollen flight data

        Raises:
            UpdateFailed: If update fails

        """
        try:
            # Get all pollen flight data
            all_pollen = await self.client.get_pollen_flight()

            # Get highest pollen flight
            highest = await self.client.get_highest_pollen_flight()

            return {
                "all_pollen": all_pollen,
                "highest": highest,
            }

        except IsalEasyHomeyApiError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err


class WasteCollectionCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator for waste collection data."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: IsalEasyHomeyApiClient,
        update_interval: timedelta,
    ) -> None:
        """Initialize the coordinator.

        Args:
            hass: The Home Assistant instance
            client: The API client
            update_interval: Update interval

        """
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_waste_collection",
            update_interval=update_interval,
        )
        self.client = client

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API.

        Returns:
            Dictionary with waste collection data

        Raises:
            UpdateFailed: If update fails

        """
        try:
            # Get upcoming waste collections
            upcoming = await self.client.get_upcoming_waste_collections()

            # Get next waste collection
            next_collection = await self.client.get_next_waste_collection()

            return {
                "upcoming": upcoming,
                "next": next_collection,
            }

        except IsalEasyHomeyApiError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err

