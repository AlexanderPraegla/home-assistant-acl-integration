"""Sensor platform for isal Easy Homey integration."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime
import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    COORDINATOR_PETROL,
    COORDINATOR_POLLEN,
    COORDINATOR_WASTE,
    COORDINATOR_WEATHER,
    DOMAIN,
    MANUFACTURER,
    MODEL,
    POLLEN_TYPES,
    WASTE_TYPES,
)
from .coordinator import (
    PetrolStationCoordinator,
    PollenFlightCoordinator,
    WasteCollectionCoordinator,
    WeatherWarningCoordinator,
)

_LOGGER = logging.getLogger(__name__)


@dataclass
class IsalEasyHomeySensorEntityDescription(SensorEntityDescription):
    """Class describing isal Easy Homey sensor entities."""

    value_fn: Callable[[dict[str, Any]], Any] | None = None
    attributes_fn: Callable[[dict[str, Any]], dict[str, Any]] | None = None
    icon_fn: Callable[[dict[str, Any]], str] | None = None
    available_fn: Callable[[dict[str, Any]], bool] | None = None


def get_price_from_prices(prices: list[dict[str, Any]], petrol_type: str) -> float | None:
    """Extract price for a specific petrol type.

    Args:
        prices: List of price dictionaries
        petrol_type: The petrol type to find

    Returns:
        The price or None

    """
    for price in prices:
        if price.get("petrolType") == petrol_type:
            return price.get("price")
    return None


def format_address(address: dict[str, Any]) -> str:
    """Format address as string.

    Args:
        address: Address dictionary

    Returns:
        Formatted address string

    """
    parts = []
    if street := address.get("street"):
        parts.append(street)
    if house_number := address.get("houseNumber"):
        parts[-1] = f"{parts[-1]} {house_number}"
    if postal_code := address.get("postalCode"):
        parts.append(postal_code)
    if city := address.get("city"):
        parts.append(city)
    return ", ".join(parts)


# Petrol Station Sensors
PETROL_STATION_SENSORS: tuple[IsalEasyHomeySensorEntityDescription, ...] = (
    IsalEasyHomeySensorEntityDescription(
        key="nearest_station",
        translation_key="nearest_station",
        icon="mdi:gas-station-outline",
        native_unit_of_measurement="km",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("nearest_station", {})
        .get("location", {})
        .get("distance"),
        attributes_fn=lambda data: {
            "station_id": data.get("nearest_station", {}).get("stationId"),
            "name": data.get("nearest_station", {}).get("name"),
            "brand": data.get("nearest_station", {}).get("brand"),
            "address": format_address(data.get("nearest_station", {}).get("address", {})),
            "location": data.get("nearest_station", {}).get("location"),
            "status": data.get("nearest_station", {}).get("status"),
            "e5_price": get_price_from_prices(
                data.get("nearest_station", {}).get("prices", []), "E5"
            ),
            "e5_price_eur": f"{get_price_from_prices(data.get('nearest_station', {}).get('prices', []), 'E5'):.3f} €" if get_price_from_prices(data.get("nearest_station", {}).get("prices", []), "E5") is not None else "-",
            "e10_price": get_price_from_prices(
                data.get("nearest_station", {}).get("prices", []), "E10"
            ),
            "e10_price_eur": f"{get_price_from_prices(data.get('nearest_station', {}).get('prices', []), 'E10'):.3f} €" if get_price_from_prices(data.get("nearest_station", {}).get("prices", []), "E10") is not None else "-",
            "diesel_price": get_price_from_prices(
                data.get("nearest_station", {}).get("prices", []), "DIESEL"
            ),
            "diesel_price_eur": f"{get_price_from_prices(data.get('nearest_station', {}).get('prices', []), 'DIESEL'):.3f} €" if get_price_from_prices(data.get("nearest_station", {}).get("prices", []), "DIESEL") is not None else "-",
            "distance": data.get("nearest_station", {})
            .get("location", {})
            .get("distance"),
        },
        available_fn=lambda data: "nearest_station" in data and data["nearest_station"],
    ),
)


# Weather Warning Sensors
WEATHER_WARNING_SENSORS: tuple[IsalEasyHomeySensorEntityDescription, ...] = (
    IsalEasyHomeySensorEntityDescription(
        key="current_weather_warning",
        translation_key="current_weather_warning",
        value_fn=lambda data: (
            max(
                data.get("warnings", {}).get("warnings", []),
                key=lambda x: x.get("details", {})
                .get("severity", {})
                .get("severityLevel", 0),
                default={},
            )
            .get("details", {})
            .get("severity", {})
            .get("severity")
        ),
        attributes_fn=lambda data: {
            "area_name": max(
                data.get("warnings", {}).get("warnings", []),
                key=lambda x: x.get("details", {})
                .get("severity", {})
                .get("severityLevel", 0),
                default={},
            ).get("areaName"),
            "warning_id": max(
                data.get("warnings", {}).get("warnings", []),
                key=lambda x: x.get("details", {})
                .get("severity", {})
                .get("severityLevel", 0),
                default={},
            ).get("warningId"),
            "title": max(
                data.get("warnings", {}).get("warnings", []),
                key=lambda x: x.get("details", {})
                .get("severity", {})
                .get("severityLevel", 0),
                default={},
            )
            .get("details", {})
            .get("title"),
            "description": max(
                data.get("warnings", {}).get("warnings", []),
                key=lambda x: x.get("details", {})
                .get("severity", {})
                .get("severityLevel", 0),
                default={},
            )
            .get("details", {})
            .get("description"),
            "instruction": max(
                data.get("warnings", {}).get("warnings", []),
                key=lambda x: x.get("details", {})
                .get("severity", {})
                .get("severityLevel", 0),
                default={},
            )
            .get("details", {})
            .get("instruction"),
            "severity_level": max(
                data.get("warnings", {}).get("warnings", []),
                key=lambda x: x.get("details", {})
                .get("severity", {})
                .get("severityLevel", 0),
                default={},
            )
            .get("details", {})
            .get("severity", {})
            .get("severityLevel"),
            "severity_translation": max(
                data.get("warnings", {}).get("warnings", []),
                key=lambda x: x.get("details", {})
                .get("severity", {})
                .get("severityLevel", 0),
                default={},
            )
            .get("details", {})
            .get("severity", {})
            .get("severityTranslation"),
            "severity_color": max(
                data.get("warnings", {}).get("warnings", []),
                key=lambda x: x.get("details", {})
                .get("severity", {})
                .get("severityLevel", 0),
                default={},
            )
            .get("details", {})
            .get("severity", {})
            .get("severityColor", {})
            .get("hex"),
            "weather_type": max(
                data.get("warnings", {}).get("warnings", []),
                key=lambda x: x.get("details", {})
                .get("severity", {})
                .get("severityLevel", 0),
                default={},
            )
            .get("details", {})
            .get("weatherType"),
            "valid_from": max(
                data.get("warnings", {}).get("warnings", []),
                key=lambda x: x.get("details", {})
                .get("severity", {})
                .get("severityLevel", 0),
                default={},
            ).get("from"),
            "valid_until": max(
                data.get("warnings", {}).get("warnings", []),
                key=lambda x: x.get("details", {})
                .get("severity", {})
                .get("severityLevel", 0),
                default={},
            ).get("until"),
            "issued_by": max(
                data.get("warnings", {}).get("warnings", []),
                key=lambda x: x.get("details", {})
                .get("severity", {})
                .get("severityLevel", 0),
                default={},
            ).get("issuedBy"),
            "created_on": max(
                data.get("warnings", {}).get("warnings", []),
                key=lambda x: x.get("details", {})
                .get("severity", {})
                .get("severityLevel", 0),
                default={},
            ).get("createdOn"),
        },
        icon_fn=lambda data: max(
            data.get("warnings", {}).get("warnings", []),
            key=lambda x: x.get("details", {}).get("severity", {}).get("severityLevel", 0),
            default={},
        )
        .get("details", {})
        .get("weatherIcon", {})
        .get("mdiIcon", "mdi:alert"),
        available_fn=lambda data: (
            data.get("warnings", {}).get("count", 0) > 0
            and len(data.get("warnings", {}).get("warnings", [])) > 0
        ),
    ),
    IsalEasyHomeySensorEntityDescription(
        key="current_upfront_warning",
        translation_key="current_upfront_warning",
        value_fn=lambda data: (
            max(
                data.get("upfront", {}).get("warnings", []),
                key=lambda x: x.get("details", {})
                .get("severity", {})
                .get("severityLevel", 0),
                default={},
            )
            .get("details", {})
            .get("severity", {})
            .get("severity")
        ),
        attributes_fn=lambda data: {
            "area_name": max(
                data.get("upfront", {}).get("warnings", []),
                key=lambda x: x.get("details", {})
                .get("severity", {})
                .get("severityLevel", 0),
                default={},
            ).get("areaName"),
            "warning_id": max(
                data.get("upfront", {}).get("warnings", []),
                key=lambda x: x.get("details", {})
                .get("severity", {})
                .get("severityLevel", 0),
                default={},
            ).get("warningId"),
            "title": max(
                data.get("upfront", {}).get("warnings", []),
                key=lambda x: x.get("details", {})
                .get("severity", {})
                .get("severityLevel", 0),
                default={},
            )
            .get("details", {})
            .get("title"),
            "description": max(
                data.get("upfront", {}).get("warnings", []),
                key=lambda x: x.get("details", {})
                .get("severity", {})
                .get("severityLevel", 0),
                default={},
            )
            .get("details", {})
            .get("description"),
            "instruction": max(
                data.get("upfront", {}).get("warnings", []),
                key=lambda x: x.get("details", {})
                .get("severity", {})
                .get("severityLevel", 0),
                default={},
            )
            .get("details", {})
            .get("instruction"),
            "severity_level": max(
                data.get("upfront", {}).get("warnings", []),
                key=lambda x: x.get("details", {})
                .get("severity", {})
                .get("severityLevel", 0),
                default={},
            )
            .get("details", {})
            .get("severity", {})
            .get("severityLevel"),
            "severity_translation": max(
                data.get("upfront", {}).get("warnings", []),
                key=lambda x: x.get("details", {})
                .get("severity", {})
                .get("severityLevel", 0),
                default={},
            )
            .get("details", {})
            .get("severity", {})
            .get("severityTranslation"),
            "severity_color": max(
                data.get("upfront", {}).get("warnings", []),
                key=lambda x: x.get("details", {})
                .get("severity", {})
                .get("severityLevel", 0),
                default={},
            )
            .get("details", {})
            .get("severity", {})
            .get("severityColor", {})
            .get("hex"),
            "weather_type": max(
                data.get("upfront", {}).get("warnings", []),
                key=lambda x: x.get("details", {})
                .get("severity", {})
                .get("severityLevel", 0),
                default={},
            )
            .get("details", {})
            .get("weatherType"),
            "valid_from": max(
                data.get("upfront", {}).get("warnings", []),
                key=lambda x: x.get("details", {})
                .get("severity", {})
                .get("severityLevel", 0),
                default={},
            ).get("from"),
            "valid_until": max(
                data.get("upfront", {}).get("warnings", []),
                key=lambda x: x.get("details", {})
                .get("severity", {})
                .get("severityLevel", 0),
                default={},
            ).get("until"),
            "issued_by": max(
                data.get("upfront", {}).get("warnings", []),
                key=lambda x: x.get("details", {})
                .get("severity", {})
                .get("severityLevel", 0),
                default={},
            ).get("issuedBy"),
            "created_on": max(
                data.get("upfront", {}).get("warnings", []),
                key=lambda x: x.get("details", {})
                .get("severity", {})
                .get("severityLevel", 0),
                default={},
            ).get("createdOn"),
        },
        icon_fn=lambda data: max(
            data.get("upfront", {}).get("warnings", []),
            key=lambda x: x.get("details", {}).get("severity", {}).get("severityLevel", 0),
            default={},
        )
        .get("details", {})
        .get("weatherIcon", {})
        .get("mdiIcon", "mdi:information"),
        available_fn=lambda data: (
            data.get("upfront", {}).get("count", 0) > 0
            and len(data.get("upfront", {}).get("warnings", [])) > 0
        ),
    ),
    IsalEasyHomeySensorEntityDescription(
        key="all_weather_warnings_json",
        translation_key="all_weather_warnings_json",
        icon="mdi:code-json",
        value_fn=lambda data: data.get("warnings", {}).get("count", 0),
        attributes_fn=lambda data: {
            "warnings": data.get("warnings", {}).get("warnings", []),
            "raw_data": data.get("warnings", {}),
        },
    ),
    IsalEasyHomeySensorEntityDescription(
        key="all_upfront_warnings_json",
        translation_key="all_upfront_warnings_json",
        icon="mdi:code-json",
        value_fn=lambda data: data.get("upfront", {}).get("count", 0),
        attributes_fn=lambda data: {
            "warnings": data.get("upfront", {}).get("warnings", []),
            "raw_data": data.get("upfront", {}),
        },
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors from a config entry.

    Args:
        hass: The Home Assistant instance
        entry: The config entry
        async_add_entities: Callback to add entities

    """
    data = hass.data[DOMAIN][entry.entry_id]
    coordinators = data["coordinators"]

    entities: list[SensorEntity] = []

    # Add petrol station sensors
    petrol_coordinator = coordinators[COORDINATOR_PETROL]
    entities.extend(
        IsalEasyHomeySensor(
            petrol_coordinator,
            entry,
            description,
        )
        for description in PETROL_STATION_SENSORS
    )

    # Add cheapest station sensors for each fuel type (E5, E10, DIESEL)
    for fuel_type in ["E5", "E10", "DIESEL"]:
        entities.append(
            IsalEasyHomeyCheapestStationSensor(
                petrol_coordinator,
                entry,
                fuel_type,
            )
        )

    # Add nearest station sensors for each user location
    if petrol_coordinator.user_locations:
        for user_loc in petrol_coordinator.user_locations:
            user_name = user_loc.get("name")
            if user_name:
                entities.append(
                    IsalEasyHomeyUserNearestStationSensor(
                        petrol_coordinator,
                        entry,
                        user_name,
                    )
                )

    # Add sensors for specific station IDs
    if petrol_coordinator.station_ids:
        for station_id in petrol_coordinator.station_ids:
            entities.append(
                IsalEasyHomeyStationIdSensor(
                    petrol_coordinator,
                    entry,
                    station_id,
                )
            )

    # Add weather warning sensors
    weather_coordinator = coordinators[COORDINATOR_WEATHER]
    entities.extend(
        IsalEasyHomeySensor(
            weather_coordinator,
            entry,
            description,
        )
        for description in WEATHER_WARNING_SENSORS
    )

    # Add pollen sensors (highest + individual types)
    pollen_coordinator = coordinators[COORDINATOR_POLLEN]

    # Add highest pollen sensor
    entities.append(
        IsalEasyHomeyHighestPollenSensor(
            pollen_coordinator,
            entry,
        )
    )

    # Add individual pollen type sensors
    for pollen_type_key, pollen_type_name in POLLEN_TYPES.items():
        entities.append(
            IsalEasyHomeyPollenSensor(
                pollen_coordinator,
                entry,
                pollen_type_key,
                pollen_type_name,
            )
        )

    # Add waste collection sensors
    waste_coordinator = coordinators[COORDINATOR_WASTE]

    # Add next waste collection sensor
    entities.append(
        IsalEasyHomeyNextWasteCollectionSensor(
            waste_coordinator,
            entry,
        )
    )

    # Add individual waste type sensors
    for waste_type_key, waste_type_name in WASTE_TYPES.items():
        entities.append(
            IsalEasyHomeyWasteSensor(
                waste_coordinator,
                entry,
                waste_type_key,
                waste_type_name,
            )
        )

    async_add_entities(entities)


class IsalEasyHomeySensor(
    CoordinatorEntity[
        PetrolStationCoordinator
        | WeatherWarningCoordinator
        | PollenFlightCoordinator
        | WasteCollectionCoordinator
    ],
    SensorEntity,
):
    """Representation of a isal Easy Homey sensor."""

    entity_description: IsalEasyHomeySensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: (
            PetrolStationCoordinator
            | WeatherWarningCoordinator
            | PollenFlightCoordinator
            | WasteCollectionCoordinator
        ),
        entry: ConfigEntry,
        description: IsalEasyHomeySensorEntityDescription,
    ) -> None:
        """Initialize the sensor.

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
    def native_value(self) -> Any:
        """Return the state of the sensor.

        Returns:
            The sensor state

        """
        if self.entity_description.value_fn:
            return self.entity_description.value_fn(self.coordinator.data)
        return None

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
            return self.entity_description.icon_fn(self.coordinator.data)
        return self.entity_description.icon

    @property
    def available(self) -> bool:
        """Return if entity is available.

        Returns:
            True if available

        """
        if self.entity_description.available_fn:
            return (
                super().available
                and self.entity_description.available_fn(self.coordinator.data)
            )
        return super().available


class IsalEasyHomeyHighestPollenSensor(
    CoordinatorEntity[PollenFlightCoordinator], SensorEntity
):
    """Sensor for highest pollen severity."""

    _attr_has_entity_name = True
    _attr_translation_key = "highest_pollen_severity"

    def __init__(
        self,
        coordinator: PollenFlightCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor.

        Args:
            coordinator: The data coordinator
            entry: The config entry

        """
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_highest_pollen_severity"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "isal Easy Homey",
            "manufacturer": MANUFACTURER,
            "model": MODEL,
        }

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor.

        Returns:
            The severity type

        """
        highest = self.coordinator.data.get("highest", {}).get("highestSeverity")
        if highest:
            return highest.get("today", {}).get("severityType")
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes.

        Returns:
            Dictionary of attributes

        """
        highest = self.coordinator.data.get("highest", {}).get("highestSeverity", {})
        return {
            "pollen_type": highest.get("pollenType"),
            "pollen_type_translation": highest.get("pollenTypeTranslation"),
            "severity_level": highest.get("today", {}).get("severityLevel"),
            "severity_translation": highest.get("today", {}).get("severityTranslation"),
            "severity_color": highest.get("today", {})
            .get("severityColor", {})
            .get("hex"),
            "today": highest.get("today", {}).get("severityType"),
            "tomorrow": highest.get("tomorrow", {}).get("severityType"),
            "day_after_tomorrow": highest.get("dayAfterTomorrow", {}).get(
                "severityType"
            ),
        }

    @property
    def icon(self) -> str:
        """Return the icon.

        Returns:
            Icon string

        """
        highest = self.coordinator.data.get("highest", {}).get("highestSeverity", {})
        return highest.get("pollenIcon", {}).get("mdiIcon", "mdi:flower-pollen")

    @property
    def available(self) -> bool:
        """Return if entity is available.

        Returns:
            True if available

        """
        return super().available and bool(
            self.coordinator.data.get("highest", {}).get("highestSeverity")
        )


class IsalEasyHomeyPollenSensor(
    CoordinatorEntity[PollenFlightCoordinator], SensorEntity
):
    """Sensor for individual pollen type."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: PollenFlightCoordinator,
        entry: ConfigEntry,
        pollen_type: str,
        pollen_name: str,
    ) -> None:
        """Initialize the sensor.

        Args:
            coordinator: The data coordinator
            entry: The config entry
            pollen_type: The pollen type key
            pollen_name: The pollen type name

        """
        super().__init__(coordinator)
        self._pollen_type = pollen_type
        self._pollen_name = pollen_name
        self._attr_unique_id = f"{entry.entry_id}_pollen_{pollen_name}"
        self._attr_translation_key = f"pollen_{pollen_name}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "isal Easy Homey",
            "manufacturer": MANUFACTURER,
            "model": MODEL,
        }

    def _get_pollen_data(self) -> dict[str, Any] | None:
        """Get pollen data for this type.

        Returns:
            Pollen data dictionary or None

        """
        flights = self.coordinator.data.get("all_pollen", {}).get("flights", [])
        for flight in flights:
            if flight.get("pollenType") == self._pollen_type:
                return flight
        return None

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor.

        Returns:
            Today's severity type

        """
        pollen_data = self._get_pollen_data()
        if pollen_data:
            return pollen_data.get("today", {}).get("severityType")
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes.

        Returns:
            Dictionary of attributes

        """
        pollen_data = self._get_pollen_data()
        if not pollen_data:
            return {}

        return {
            "pollen_type": pollen_data.get("pollenType"),
            "pollen_type_translation": pollen_data.get("pollenTypeTranslation"),
            "severity_level_today": pollen_data.get("today", {}).get("severityLevel"),
            "severity_today": pollen_data.get("today", {}).get("severityType"),
            "severity_translation_today": pollen_data.get("today", {}).get(
                "severityTranslation"
            ),
            "severity_color_today": pollen_data.get("today", {})
            .get("severityColor", {})
            .get("hex"),
            "severity_level_tomorrow": pollen_data.get("tomorrow", {}).get(
                "severityLevel"
            ),
            "severity_tomorrow": pollen_data.get("tomorrow", {}).get("severityType"),
            "severity_translation_tomorrow": pollen_data.get("tomorrow", {}).get(
                "severityTranslation"
            ),
            "severity_color_tomorrow": pollen_data.get("tomorrow", {})
            .get("severityColor", {})
            .get("hex"),
            "severity_level_day_after_tomorrow": pollen_data.get(
                "dayAfterTomorrow", {}
            ).get("severityLevel"),
            "severity_day_after_tomorrow": pollen_data.get("dayAfterTomorrow", {}).get(
                "severityType"
            ),
            "severity_translation_day_after_tomorrow": pollen_data.get(
                "dayAfterTomorrow", {}
            ).get("severityTranslation"),
            "severity_color_day_after_tomorrow": pollen_data.get(
                "dayAfterTomorrow", {}
            )
            .get("severityColor", {})
            .get("hex"),
        }

    @property
    def icon(self) -> str:
        """Return the icon.

        Returns:
            Icon string

        """
        pollen_data = self._get_pollen_data()
        if pollen_data:
            return pollen_data.get("pollenIcon", {}).get("mdiIcon", "mdi:flower")
        return "mdi:flower"

    @property
    def available(self) -> bool:
        """Return if entity is available.

        Returns:
            True if available

        """
        return super().available and bool(self._get_pollen_data())


class IsalEasyHomeyNextWasteCollectionSensor(
    CoordinatorEntity[WasteCollectionCoordinator], SensorEntity
):
    """Sensor for next waste collection."""

    _attr_has_entity_name = True
    _attr_translation_key = "next_waste_collection"
    _attr_device_class = SensorDeviceClass.DATE
    _attr_icon = "mdi:trash-can-outline"

    def __init__(
        self,
        coordinator: WasteCollectionCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor.

        Args:
            coordinator: The data coordinator
            entry: The config entry

        """
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_next_waste_collection"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "isal Easy Homey",
            "manufacturer": MANUFACTURER,
            "model": MODEL,
        }

    @property
    def native_value(self) -> date | None:
        """Return the state of the sensor.

        Returns:
            The next collection date

        """
        scheduled_on = self.coordinator.data.get("next", {}).get("scheduledOn")
        if scheduled_on:
            return datetime.fromisoformat(scheduled_on).date()
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes.

        Returns:
            Dictionary of attributes

        """
        next_data = self.coordinator.data.get("next", {})
        collections = next_data.get("scheduledCollections", [])

        waste_types = [c.get("wasteType") for c in collections]
        waste_types_translations = [c.get("wasteTypeTranslation") for c in collections]

        # Calculate days until collection
        days_until = None
        if scheduled_on := next_data.get("scheduledOn"):
            collection_date = datetime.fromisoformat(scheduled_on).date()
            today = datetime.now().date()
            days_until = (collection_date - today).days

        return {
            "scheduled_on": next_data.get("scheduledOn"),
            "days_until_collection": days_until,
            "waste_types": waste_types,
            "waste_types_translations": waste_types_translations,
            "collections": collections,
        }


class IsalEasyHomeyWasteSensor(
    CoordinatorEntity[WasteCollectionCoordinator], SensorEntity
):
    """Sensor for individual waste type."""

    _attr_has_entity_name = True
    _attr_device_class = SensorDeviceClass.DATE

    def __init__(
        self,
        coordinator: WasteCollectionCoordinator,
        entry: ConfigEntry,
        waste_type: str,
        waste_name: str,
    ) -> None:
        """Initialize the sensor.

        Args:
            coordinator: The data coordinator
            entry: The config entry
            waste_type: The waste type key
            waste_name: The waste type name

        """
        super().__init__(coordinator)
        self._waste_type = waste_type
        self._waste_name = waste_name
        self._attr_unique_id = f"{entry.entry_id}_waste_{waste_name}"
        self._attr_translation_key = f"waste_{waste_name}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "isal Easy Homey",
            "manufacturer": MANUFACTURER,
            "model": MODEL,
        }

    def _get_waste_data(self) -> dict[str, Any] | None:
        """Get waste collection data for this type.

        Returns:
            Waste collection data or None

        """
        collections = (
            self.coordinator.data.get("upcoming", {}).get("scheduledCollections", [])
        )
        for collection in collections:
            if collection.get("wasteType") == self._waste_type:
                return collection
        return None

    @property
    def native_value(self) -> date | None:
        """Return the state of the sensor.

        Returns:
            The next collection date

        """
        waste_data = self._get_waste_data()
        if waste_data and (scheduled_on := waste_data.get("scheduledOn")):
            return datetime.fromisoformat(scheduled_on).date()
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes.

        Returns:
            Dictionary of attributes

        """
        waste_data = self._get_waste_data()
        if not waste_data:
            return {}

        # Calculate days until collection
        days_until = None
        if scheduled_on := waste_data.get("scheduledOn"):
            collection_date = datetime.fromisoformat(scheduled_on).date()
            today = datetime.now().date()
            days_until = (collection_date - today).days

        return {
            "waste_type": waste_data.get("wasteType"),
            "waste_type_translation": waste_data.get("wasteTypeTranslation"),
            "scheduled_on": waste_data.get("scheduledOn"),
            "days_until_collection": days_until,
            "color_primary": waste_data.get("wasteColorPrimary", {}).get("hex"),
            "color_secondary": waste_data.get("wasteColorSecondary", {}).get("hex"),
        }

    @property
    def icon(self) -> str:
        """Return the icon.

        Returns:
            Icon string

        """
        waste_data = self._get_waste_data()
        if waste_data:
            return waste_data.get("icon", {}).get("mdiIcon", "mdi:trash-can")
        return "mdi:trash-can"

    @property
    def available(self) -> bool:
        """Return if entity is available.

        Returns:
            True if available

        """
        return super().available and bool(self._get_waste_data())


class IsalEasyHomeyCheapestStationSensor(
    CoordinatorEntity[PetrolStationCoordinator], SensorEntity
):
    """Sensor for cheapest gas station for a specific fuel type."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:currency-eur"
    _attr_native_unit_of_measurement = "EUR"
    _attr_device_class = SensorDeviceClass.MONETARY

    def __init__(
        self,
        coordinator: PetrolStationCoordinator,
        entry: ConfigEntry,
        fuel_type: str,
    ) -> None:
        """Initialize the sensor.

        Args:
            coordinator: The data coordinator
            entry: The config entry
            fuel_type: The fuel type (E5, E10, DIESEL)

        """
        super().__init__(coordinator)
        self._fuel_type = fuel_type
        fuel_type_lower = fuel_type.lower()
        self._attr_unique_id = f"{entry.entry_id}_cheapest_station_{fuel_type_lower}"
        self._attr_translation_key = f"cheapest_station_{fuel_type_lower}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "isal Easy Homey",
            "manufacturer": MANUFACTURER,
            "model": MODEL,
        }

    def _get_station_data(self) -> dict[str, Any] | None:
        """Get station data for this fuel type.

        Returns:
            Station data dictionary or None

        """
        cheapest_stations = self.coordinator.data.get("cheapest_stations", {})
        return cheapest_stations.get(self._fuel_type)

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor.

        Returns:
            The price

        """
        station_data = self._get_station_data()
        if station_data:
            return get_price_from_prices(
                station_data.get("prices", []), self._fuel_type
            )
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes.

        Returns:
            Dictionary of attributes

        """
        station_data = self._get_station_data()
        if not station_data:
            return {}

        return {
            "fuel_type": self._fuel_type,
            "station_id": station_data.get("stationId"),
            "name": station_data.get("name"),
            "brand": station_data.get("brand"),
            "address": format_address(station_data.get("address", {})),
            "location": station_data.get("location"),
            "status": station_data.get("status"),
            "e5_price": get_price_from_prices(
                station_data.get("prices", []), "E5"
            ),
            "e5_price_eur": f"{get_price_from_prices(station_data.get('prices', []), 'E5'):.3f} €" if get_price_from_prices(station_data.get("prices", []), "E5") is not None else "-",
            "e10_price": get_price_from_prices(
                station_data.get("prices", []), "E10"
            ),
            "e10_price_eur": f"{get_price_from_prices(station_data.get('prices', []), 'E10'):.3f} €" if get_price_from_prices(station_data.get("prices", []), "E10") is not None else "-",
            "diesel_price": get_price_from_prices(
                station_data.get("prices", []), "DIESEL"
            ),
            "diesel_price_eur": f"{get_price_from_prices(station_data.get('prices', []), 'DIESEL'):.3f} €" if get_price_from_prices(station_data.get("prices", []), "DIESEL") is not None else "-",
            "distance": station_data.get("location", {}).get("distance"),
        }

    @property
    def available(self) -> bool:
        """Return if entity is available.

        Returns:
            True if available

        """
        return super().available and bool(self._get_station_data())


class IsalEasyHomeyUserNearestStationSensor(
    CoordinatorEntity[PetrolStationCoordinator], SensorEntity
):
    """Sensor for nearest gas station for a specific user location."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:gas-station-outline"
    _attr_native_unit_of_measurement = "km"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator: PetrolStationCoordinator,
        entry: ConfigEntry,
        user_name: str,
    ) -> None:
        """Initialize the sensor.

        Args:
            coordinator: The data coordinator
            entry: The config entry
            user_name: The user name

        """
        super().__init__(coordinator)
        self._user_name = user_name
        # Create a safe unique_id from user_name
        safe_user_name = user_name.lower().replace(" ", "_")
        self._attr_unique_id = f"{entry.entry_id}_nearest_station_{safe_user_name}"
        self._attr_name = f"Nächste Tankstelle {user_name}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "isal Easy Homey",
            "manufacturer": MANUFACTURER,
            "model": MODEL,
        }

    def _get_station_data(self) -> dict[str, Any] | None:
        """Get station data for this user.

        Returns:
            Station data dictionary or None

        """
        user_nearest_stations = self.coordinator.data.get("user_nearest_stations", {})
        return user_nearest_stations.get(self._user_name)

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor.

        Returns:
            The distance in km

        """
        station_data = self._get_station_data()
        if station_data:
            return station_data.get("location", {}).get("distance")
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes.

        Returns:
            Dictionary of attributes

        """
        station_data = self._get_station_data()
        if not station_data:
            return {"user_name": self._user_name}

        return {
            "user_name": self._user_name,
            "station_id": station_data.get("stationId"),
            "name": station_data.get("name"),
            "brand": station_data.get("brand"),
            "address": format_address(station_data.get("address", {})),
            "location": station_data.get("location"),
            "status": station_data.get("status"),
            "e5_price": get_price_from_prices(
                station_data.get("prices", []), "E5"
            ),
            "e5_price_eur": f"{get_price_from_prices(station_data.get('prices', []), 'E5'):.3f} €" if get_price_from_prices(station_data.get("prices", []), "E5") is not None else "-",
            "e10_price": get_price_from_prices(
                station_data.get("prices", []), "E10"
            ),
            "e10_price_eur": f"{get_price_from_prices(station_data.get('prices', []), 'E10'):.3f} €" if get_price_from_prices(station_data.get("prices", []), "E10") is not None else "-",
            "diesel_price": get_price_from_prices(
                station_data.get("prices", []), "DIESEL"
            ),
            "diesel_price_eur": f"{get_price_from_prices(station_data.get('prices', []), 'DIESEL'):.3f} €" if get_price_from_prices(station_data.get("prices", []), "DIESEL") is not None else "-",
            "distance": station_data.get("location", {}).get("distance"),
        }

    @property
    def available(self) -> bool:
        """Return if entity is available.

        Returns:
            True if available

        """
        return super().available and bool(self._get_station_data())


class IsalEasyHomeyStationIdSensor(
    CoordinatorEntity[PetrolStationCoordinator], SensorEntity
):
    """Sensor for a specific petrol station by ID."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:gas-station"

    def __init__(
        self,
        coordinator: PetrolStationCoordinator,
        entry: ConfigEntry,
        station_id: str,
    ) -> None:
        """Initialize the sensor.

        Args:
            coordinator: The data coordinator
            entry: The config entry
            station_id: The station ID

        """
        super().__init__(coordinator)
        self._station_id = station_id
        # Create a safe unique_id from station_id
        safe_station_id = station_id.replace("-", "_")
        self._attr_unique_id = f"{entry.entry_id}_station_{safe_station_id}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "isal Easy Homey",
            "manufacturer": MANUFACTURER,
            "model": MODEL,
        }

    def _get_station_data(self) -> dict[str, Any] | None:
        """Get station data for this station ID.

        Returns:
            Station data dictionary or None

        """
        stations_by_id = self.coordinator.data.get("stations_by_id", {})
        return stations_by_id.get(self._station_id)

    @property
    def name(self) -> str | None:
        """Return the name of the sensor.

        Returns:
            The station name

        """
        station_data = self._get_station_data()
        if station_data:
            return station_data.get("name", self._station_id)
        return self._station_id

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor.

        Returns:
            The station status

        """
        station_data = self._get_station_data()
        if station_data:
            return station_data.get("statusTranslation", station_data.get("status"))
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes.

        Returns:
            Dictionary of attributes

        """
        station_data = self._get_station_data()
        if not station_data:
            return {"station_id": self._station_id}

        return {
            "station_id": station_data.get("stationId"),
            "name": station_data.get("name"),
            "brand": station_data.get("brand"),
            "address": format_address(station_data.get("address", {})),
            "location": station_data.get("location"),
            "status": station_data.get("status"),
            "status_translation": station_data.get("statusTranslation"),
            "e5_price": get_price_from_prices(
                station_data.get("prices", []), "E5"
            ),
            "e5_price_eur": f"{get_price_from_prices(station_data.get('prices', []), 'E5'):.3f} €" if get_price_from_prices(station_data.get("prices", []), "E5") is not None else "-",
            "e10_price": get_price_from_prices(
                station_data.get("prices", []), "E10"
            ),
            "e10_price_eur": f"{get_price_from_prices(station_data.get('prices', []), 'E10'):.3f} €" if get_price_from_prices(station_data.get("prices", []), "E10") is not None else "-",
            "diesel_price": get_price_from_prices(
                station_data.get("prices", []), "DIESEL"
            ),
            "diesel_price_eur": f"{get_price_from_prices(station_data.get('prices', []), 'DIESEL'):.3f} €" if get_price_from_prices(station_data.get("prices", []), "DIESEL") is not None else "-",
            "all_day_opened": station_data.get("openingHours", {}).get("allDayOpened"),
            "opening_hours": station_data.get("openingHours", {}).get("openingHours"),
        }

    @property
    def icon(self) -> str:
        """Return the icon.

        Returns:
            Icon string based on status

        """
        station_data = self._get_station_data()
        if station_data:
            status = station_data.get("status")
            if status == "OPEN":
                return "mdi:gas-station"
            elif status == "CLOSED":
                return "mdi:gas-station-off"
            elif status == "NO_PRICES":
                return "mdi:gas-station-outline"
        return "mdi:gas-station"

    @property
    def available(self) -> bool:
        """Return if entity is available.

        Returns:
            True if available

        """
        return super().available and bool(self._get_station_data())
