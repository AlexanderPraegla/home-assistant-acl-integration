"""Button platform for isal Easy Homey integration."""
from __future__ import annotations

import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    COORDINATOR_WATER_SOFTENER,
    DOMAIN,
    get_device_info,
)
from .coordinator import WaterSoftenerCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up button entities from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinators = data["coordinators"]

    water_softener_coordinator = coordinators[COORDINATOR_WATER_SOFTENER]

    async_add_entities([
        IsalEasyHomeyMicroLeakageCheckButton(
            water_softener_coordinator,
            entry,
        )
    ])


class IsalEasyHomeyMicroLeakageCheckButton(
    CoordinatorEntity[WaterSoftenerCoordinator],
    ButtonEntity,
):
    """Button entity to start micro leakage check."""

    _attr_has_entity_name = True
    _attr_translation_key = "water_softener_micro_leakage_start"
    _attr_icon = "mdi:clock-start"

    def __init__(
        self,
        coordinator: WaterSoftenerCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the button entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_water_softener_micro_leakage_start"
        self._attr_device_info = get_device_info(entry.entry_id, COORDINATOR_WATER_SOFTENER)

    async def async_press(self) -> None:
        """Handle the button press."""
        try:
            await self.coordinator.client.start_micro_leakage_check()
        except Exception:
            _LOGGER.exception("Failed to start micro leakage check")
            return

        # Optimistic update
        leakage_protection = self.coordinator.data.get("leakageProtection", {})
        leakage_protection["microLeakageCheck"] = "RUNNING"
        self.coordinator.data["leakageProtection"] = leakage_protection
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

