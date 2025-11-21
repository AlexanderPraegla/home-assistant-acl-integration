"""Binary sensor platform for isal Easy Homey integration."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import logging
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    COORDINATOR_POLLEN,
    COORDINATOR_WEATHER,
    DOMAIN,
    MANUFACTURER,
    MODEL,
)
from .coordinator import PollenFlightCoordinator, WeatherWarningCoordinator

_LOGGER = logging.getLogger(__name__)


@dataclass
class IsalEasyHomeyBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Class describing isal Easy Homey binary sensor entities."""

    value_fn: Callable[[dict[str, Any]], bool] | None = None
    attributes_fn: Callable[[dict[str, Any]], dict[str, Any]] | None = None
    icon_fn: Callable[[bool], str] | None = None


WEATHER_WARNING_BINARY_SENSORS: tuple[IsalEasyHomeyBinarySensorEntityDescription, ...] = (
    IsalEasyHomeyBinarySensorEntityDescription(
        key="weather_warning_active",
        translation_key="weather_warning_active",
        device_class=BinarySensorDeviceClass.SAFETY,
        value_fn=lambda data: data.get("warnings", {}).get("count", 0) > 0,
        attributes_fn=lambda data: {
            "count": data.get("warnings", {}).get("count", 0),
            "cell_id": data.get("warnings", {}).get("warningCellId"),
        },
        icon_fn=lambda is_on: "mdi:alert" if is_on else "mdi:check-circle",
    ),
    IsalEasyHomeyBinarySensorEntityDescription(
        key="upfront_warning_active",
        translation_key="upfront_warning_active",
        device_class=BinarySensorDeviceClass.SAFETY,
        value_fn=lambda data: data.get("upfront", {}).get("count", 0) > 0,
        attributes_fn=lambda data: {
            "count": data.get("upfront", {}).get("count", 0),
            "cell_id": data.get("upfront", {}).get("warningCellId"),
        },
        icon_fn=lambda is_on: "mdi:information" if is_on else "mdi:check-circle",
    ),
)

POLLEN_BINARY_SENSORS: tuple[IsalEasyHomeyBinarySensorEntityDescription, ...] = (
    IsalEasyHomeyBinarySensorEntityDescription(
        key="pollen_flight_active",
        translation_key="pollen_flight_active",
        value_fn=lambda data: any(
            flight.get("today", {}).get("severityLevel", 0) > 0
            for flight in data.get("all_pollen", {}).get("flights", [])
        ),
        attributes_fn=lambda data: {
            "region": data.get("all_pollen", {}).get("regionName"),
            "part_region": data.get("all_pollen", {}).get("partRegionName"),
            "last_updated": data.get("all_pollen", {}).get("lastUpdatedOn"),
        },
        icon_fn=lambda is_on: "mdi:flower-pollen" if is_on else "mdi:flower-pollen-outline",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up binary sensors from a config entry.

    Args:
        hass: The Home Assistant instance
        entry: The config entry
        async_add_entities: Callback to add entities

    """
    data = hass.data[DOMAIN][entry.entry_id]
    coordinators = data["coordinators"]

    entities: list[BinarySensorEntity] = []

    # Add weather warning binary sensors
    weather_coordinator = coordinators[COORDINATOR_WEATHER]
    entities.extend(
        IsalEasyHomeyBinarySensor(
            weather_coordinator,
            entry,
            description,
        )
        for description in WEATHER_WARNING_BINARY_SENSORS
    )

    # Add pollen binary sensors
    pollen_coordinator = coordinators[COORDINATOR_POLLEN]
    entities.extend(
        IsalEasyHomeyBinarySensor(
            pollen_coordinator,
            entry,
            description,
        )
        for description in POLLEN_BINARY_SENSORS
    )

    async_add_entities(entities)


class IsalEasyHomeyBinarySensor(
    CoordinatorEntity[WeatherWarningCoordinator | PollenFlightCoordinator],
    BinarySensorEntity,
):
    """Representation of a isal Easy Homey binary sensor."""

    entity_description: IsalEasyHomeyBinarySensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: WeatherWarningCoordinator | PollenFlightCoordinator,
        entry: ConfigEntry,
        description: IsalEasyHomeyBinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary sensor.

        Args:
            coordinator: The data coordinator
            entry: The config entry
            description: The entity description

        """
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "isal Easy Homey",
            "manufacturer": MANUFACTURER,
            "model": MODEL,
        }

    @property
    def is_on(self) -> bool:
        """Return true if the binary sensor is on.

        Returns:
            True if sensor is on

        """
        if self.entity_description.value_fn:
            return self.entity_description.value_fn(self.coordinator.data)
        return False

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return the state attributes.

        Returns:
            Dictionary of attributes

        """
        if self.entity_description.attributes_fn:
            return self.entity_description.attributes_fn(self.coordinator.data)
        return None

    @property
    def icon(self) -> str | None:
        """Return the icon.

        Returns:
            Icon string

        """
        if self.entity_description.icon_fn:
            return self.entity_description.icon_fn(self.is_on)
        return None

