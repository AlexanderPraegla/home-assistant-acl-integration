"""Select platform for isal Easy Homey integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    COORDINATOR_WATER_SOFTENER,
    DOMAIN,
    WATER_SCENES,
    get_device_info,
)
from .coordinator import WaterSoftenerCoordinator

_LOGGER = logging.getLogger(__name__)

WATER_SCENE_ICONS: dict[str, str] = {
    "NORMAL": "mdi:faucet",
    "SHOWER": "mdi:shower",
    "WATERING": "mdi:watering-can",
    "HEATER": "mdi:radiator",
    "WASHING": "mdi:washing-machine",
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up select entities from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinators = data["coordinators"]

    water_softener_coordinator = coordinators[COORDINATOR_WATER_SOFTENER]

    async_add_entities([
        IsalEasyHomeyWaterSceneSelect(
            water_softener_coordinator,
            entry,
        )
    ])


class IsalEasyHomeyWaterSceneSelect(
    CoordinatorEntity[WaterSoftenerCoordinator],
    SelectEntity,
):
    """Select entity for water scene."""

    _attr_has_entity_name = True
    _attr_translation_key = "water_softener_water_scene"
    _attr_options = WATER_SCENES

    def __init__(
        self,
        coordinator: WaterSoftenerCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_water_softener_water_scene"
        self._attr_device_info = get_device_info(entry.entry_id, COORDINATOR_WATER_SOFTENER)

    @property
    def current_option(self) -> str | None:
        """Return the current selected option."""
        return self.coordinator.data.get("waterScene")

    @property
    def icon(self) -> str:
        """Return the icon based on current scene."""
        scene = self.coordinator.data.get("waterScene")
        if scene:
            # Try dynamic icon from API first
            scene_icon = self.coordinator.data.get("waterSceneIcon", {})
            if scene_icon and scene_icon.get("mdiIcon"):
                return scene_icon["mdiIcon"]
            return WATER_SCENE_ICONS.get(scene, "mdi:faucet")
        return "mdi:faucet"

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        try:
            await self.coordinator.client.change_water_scene(option)
        except Exception:
            _LOGGER.exception("Failed to change water scene to %s", option)
            return

        # Optimistic update
        self.coordinator.data["waterScene"] = option
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

