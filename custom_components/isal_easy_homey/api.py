"""API Client for isal Easy Homey."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp
from aiohttp import ClientError, ClientSession, ClientTimeout

_LOGGER = logging.getLogger(__name__)

API_TIMEOUT = 30


class IsalEasyHomeyApiError(Exception):
    """Base exception for API errors."""


class IsalEasyHomeyApiConnectionError(IsalEasyHomeyApiError):
    """Exception for connection errors."""


class IsalEasyHomeyApiTimeoutError(IsalEasyHomeyApiError):
    """Exception for timeout errors."""


class IsalEasyHomeyApiClient:
    """API Client for isal Easy Homey."""

    def __init__(
        self,
        base_url: str,
        session: ClientSession,
    ) -> None:
        """Initialize the API client.

        Args:
            base_url: The base URL of the API
            session: The aiohttp session to use for requests

        """
        self._base_url = base_url.rstrip("/")
        self._session = session

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Make a request to the API.

        Args:
            method: The HTTP method to use
            endpoint: The endpoint to request
            params: Optional query parameters

        Returns:
            The JSON response from the API

        Raises:
            IsalEasyHomeyApiConnectionError: If there is a connection error
            IsalEasyHomeyApiTimeoutError: If the request times out

        """
        url = f"{self._base_url}{endpoint}"
        _LOGGER.debug("Making %s request to %s with params %s", method, url, params)

        try:
            async with asyncio.timeout(API_TIMEOUT):
                response = await self._session.request(
                    method,
                    url,
                    params=params,
                )
                response.raise_for_status()
                data = await response.json()
                _LOGGER.debug("Received response: %s", data)
                return data

        except asyncio.TimeoutError as err:
            _LOGGER.error("Timeout connecting to API: %s", err)
            raise IsalEasyHomeyApiTimeoutError(
                f"Timeout connecting to API: {err}"
            ) from err
        except ClientError as err:
            _LOGGER.error("Error connecting to API: %s", err)
            raise IsalEasyHomeyApiConnectionError(
                f"Error connecting to API: {err}"
            ) from err
        except Exception as err:
            _LOGGER.error("Unexpected error: %s", err)
            raise IsalEasyHomeyApiError(f"Unexpected error: {err}") from err

    # Petrol Station endpoints

    async def get_petrol_station(self, station_id: str) -> dict[str, Any]:
        """Get details for a specific petrol station.

        Args:
            station_id: The ID of the petrol station

        Returns:
            Petrol station details

        """
        endpoint = f"/patrol-stations/{station_id}"
        return await self._request("GET", endpoint)

    async def search_petrol_stations(
        self,
        latitude: float,
        longitude: float,
        distance: float,
    ) -> list[dict[str, Any]]:
        """Search for petrol stations around coordinates.

        Args:
            latitude: The latitude
            longitude: The longitude
            distance: The search radius in km

        Returns:
            List of petrol stations

        """
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "distance": distance,
        }
        return await self._request("GET", "/patrol-stations", params=params)

    async def get_cheapest_petrol_station(
        self,
        latitude: float,
        longitude: float,
        distance: float,
        petrol_type: str = "E5",
    ) -> dict[str, Any]:
        """Get the cheapest petrol station.

        Args:
            latitude: The latitude
            longitude: The longitude
            distance: The search radius in km
            petrol_type: The petrol type (E5, E10, DIESEL)

        Returns:
            Cheapest petrol station details

        """
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "distance": distance,
            "petrolType": petrol_type,
        }
        return await self._request("GET", "/patrol-stations/cheapest", params=params)

    # Weather Warning endpoints

    async def get_weather_warnings(
        self,
        warning_cell_id: str,
        warning_type: str | None = None,
    ) -> dict[str, Any]:
        """Get weather warnings for a cell.

        Args:
            warning_cell_id: The warning cell ID
            warning_type: Optional warning type filter (WARNING, UPFRONT_INFORMATION)

        Returns:
            Weather warnings data

        """
        params = {"warningCellId": warning_cell_id}
        if warning_type:
            params["weatherWarningType"] = warning_type
        return await self._request("GET", "/weather/warnings", params=params)

    # Pollen Flight endpoints

    async def get_pollen_flight(self) -> dict[str, Any]:
        """Get pollen flight information.

        Returns:
            Pollen flight data

        """
        return await self._request("GET", "/weather/pollen-flight")

    async def get_highest_pollen_flight(self) -> dict[str, Any]:
        """Get the highest pollen flight severity.

        Returns:
            Highest pollen flight data

        """
        return await self._request("GET", "/weather/pollen-flight/highest")

    # Waste Collection endpoints

    async def get_all_waste_collections(self) -> dict[str, Any]:
        """Get all future waste collections.

        Returns:
            All waste collection data

        """
        return await self._request("GET", "/waste-collection")

    async def get_upcoming_waste_collections(self) -> dict[str, Any]:
        """Get upcoming waste collections per type.

        Returns:
            Upcoming waste collections data

        """
        return await self._request("GET", "/waste-collection/upcoming-collections")

    async def get_next_waste_collection(self) -> dict[str, Any]:
        """Get the next waste collection.

        Returns:
            Next waste collection data

        """
        return await self._request("GET", "/waste-collection/next-collection")

    async def test_connection(self) -> bool:
        """Test the connection to the API.

        Returns:
            True if connection is successful

        Raises:
            IsalEasyHomeyApiError: If the connection fails

        """
        try:
            # Try to get pollen flight data as a simple test
            await self.get_pollen_flight()
            return True
        except Exception as err:
            _LOGGER.error("Connection test failed: %s", err)
            raise

