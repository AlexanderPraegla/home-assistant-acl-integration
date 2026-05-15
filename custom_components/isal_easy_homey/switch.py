"""Switch platform for isal Easy Homey integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    COORDINATOR_WATER_CONTROL,
    DOMAIN,
    get_device_info,
)
from .coordinator import WaterControlCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up switch entities from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinators = data["coordinators"]

    water_control_coordinator = coordinators[COORDINATOR_WATER_CONTROL]

    async_add_entities([
        IsalEasyHomeyShutoffValveSwitch(
            water_control_coordinator,
            entry,
        )
    ])


class IsalEasyHomeyShutoffValveSwitch(
    CoordinatorEntity[WaterControlCoordinator],
    SwitchEntity,
):
    """Switch entity for shutoff valve control."""

    _attr_has_entity_name = True
    _attr_translation_key = "water_control_shutoff_valve"

    def __init__(
        self,
        coordinator: WaterControlCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the switch entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_water_control_shutoff_valve"
        self._attr_device_info = get_device_info(entry.entry_id, COORDINATOR_WATER_CONTROL)

    @property
    def is_on(self) -> bool:
        """Return true if the valve is closed (shutoff active)."""
        return self.coordinator.data.get("shutoffValveStatus") == "CLOSED"

    @property
    def icon(self) -> str:
        """Return the icon based on valve status."""
        # Try dynamic icon from API first
        valve_icon = self.coordinator.data.get("shutoffValveIcon", {})
        if valve_icon and valve_icon.get("mdiIcon"):
            return valve_icon["mdiIcon"]
        return "mdi:valve-closed" if self.is_on else "mdi:valve-open"

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on (close) the shutoff valve."""
        try:
            await self.coordinator.client.control_shutoff_valve("CLOSED")
        except Exception:
            _LOGGER.exception("Failed to close shutoff valve")
            return

        # Optimistic update
        self.coordinator.data["shutoffValveStatus"] = "CLOSED"
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off (open) the shutoff valve."""
        try:
            await self.coordinator.client.control_shutoff_valve("OPEN")
        except Exception:
            _LOGGER.exception("Failed to open shutoff valve")
            return

        # Optimistic update
        self.coordinator.data["shutoffValveStatus"] = "OPEN"
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

