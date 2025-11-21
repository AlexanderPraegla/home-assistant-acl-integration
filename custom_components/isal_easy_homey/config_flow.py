"""Config flow for isal Easy Homey integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import (
    IsalEasyHomeyApiClient,
    IsalEasyHomeyApiConnectionError,
    IsalEasyHomeyApiError,
    IsalEasyHomeyApiTimeoutError,
)
from .const import (
    CONF_API_BASE_URL,
    CONF_LOCATION_ENTITY_ID,
    CONF_PETROL_TYPE,
    CONF_SEARCH_RADIUS,
    CONF_UPDATE_INTERVAL_PETROL,
    CONF_UPDATE_INTERVAL_POLLEN,
    CONF_UPDATE_INTERVAL_WASTE,
    CONF_UPDATE_INTERVAL_WEATHER,
    CONF_WARNING_CELL_ID,
    DEFAULT_API_BASE_URL,
    DEFAULT_PETROL_TYPE,
    DEFAULT_SEARCH_RADIUS,
    DEFAULT_UPDATE_INTERVAL_PETROL,
    DEFAULT_UPDATE_INTERVAL_POLLEN,
    DEFAULT_UPDATE_INTERVAL_WASTE,
    DEFAULT_UPDATE_INTERVAL_WEATHER,
    DEFAULT_WARNING_CELL_ID,
    DOMAIN,
    MAX_SEARCH_RADIUS,
    MIN_SEARCH_RADIUS,
    PETROL_TYPES,
)

_LOGGER = logging.getLogger(__name__)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Args:
        hass: The Home Assistant instance
        data: The user input data

    Returns:
        Info dict with title

    Raises:
        IsalEasyHomeyApiError: If validation fails

    """
    session = async_get_clientsession(hass)
    client = IsalEasyHomeyApiClient(data[CONF_API_BASE_URL], session)

    # Test the connection
    await client.test_connection()

    # Validate that the location entity exists if provided
    if CONF_LOCATION_ENTITY_ID in data and data[CONF_LOCATION_ENTITY_ID]:
        state = hass.states.get(data[CONF_LOCATION_ENTITY_ID])
        if state is None:
            raise ValueError(f"Entity {data[CONF_LOCATION_ENTITY_ID]} not found")

        # Check if entity has location attributes
        if not (
            state.attributes.get("latitude") and state.attributes.get("longitude")
        ):
            raise ValueError(
                f"Entity {data[CONF_LOCATION_ENTITY_ID]} does not have location attributes"
            )

    return {"title": "isal Easy Homey"}


class IsalEasyHomeyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for isal Easy Homey."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step.

        Args:
            user_input: The user input data

        Returns:
            The flow result

        """
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except IsalEasyHomeyApiConnectionError:
                errors["base"] = "cannot_connect"
            except IsalEasyHomeyApiTimeoutError:
                errors["base"] = "timeout"
            except ValueError as err:
                _LOGGER.error("Validation error: %s", err)
                errors["base"] = "invalid_entity"
            except IsalEasyHomeyApiError:
                errors["base"] = "unknown"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_API_BASE_URL, default=DEFAULT_API_BASE_URL
                    ): str,
                    vol.Optional(CONF_LOCATION_ENTITY_ID): selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain=["device_tracker", "person", "zone"]
                        )
                    ),
                    vol.Required(
                        CONF_WARNING_CELL_ID, default=DEFAULT_WARNING_CELL_ID
                    ): str,
                    vol.Required(
                        CONF_SEARCH_RADIUS, default=DEFAULT_SEARCH_RADIUS
                    ): vol.All(
                        vol.Coerce(float),
                        vol.Range(min=MIN_SEARCH_RADIUS, max=MAX_SEARCH_RADIUS),
                    ),
                    vol.Optional(CONF_PETROL_TYPE, default=DEFAULT_PETROL_TYPE): vol.In(
                        PETROL_TYPES
                    ),
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> IsalEasyHomeyOptionsFlow:
        """Get the options flow for this handler.

        Args:
            config_entry: The config entry

        Returns:
            The options flow handler

        """
        return IsalEasyHomeyOptionsFlow(config_entry)


class IsalEasyHomeyOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for isal Easy Homey."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow.

        Args:
            config_entry: The config entry

        """
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options.

        Args:
            user_input: The user input data

        Returns:
            The flow result

        """
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_SEARCH_RADIUS,
                        default=self.config_entry.options.get(
                            CONF_SEARCH_RADIUS,
                            self.config_entry.data.get(
                                CONF_SEARCH_RADIUS, DEFAULT_SEARCH_RADIUS
                            ),
                        ),
                    ): vol.All(
                        vol.Coerce(float),
                        vol.Range(min=MIN_SEARCH_RADIUS, max=MAX_SEARCH_RADIUS),
                    ),
                    vol.Optional(
                        CONF_WARNING_CELL_ID,
                        default=self.config_entry.options.get(
                            CONF_WARNING_CELL_ID,
                            self.config_entry.data.get(
                                CONF_WARNING_CELL_ID, DEFAULT_WARNING_CELL_ID
                            ),
                        ),
                    ): str,
                    vol.Optional(
                        CONF_PETROL_TYPE,
                        default=self.config_entry.options.get(
                            CONF_PETROL_TYPE,
                            self.config_entry.data.get(
                                CONF_PETROL_TYPE, DEFAULT_PETROL_TYPE
                            ),
                        ),
                    ): vol.In(PETROL_TYPES),
                    vol.Optional(
                        CONF_UPDATE_INTERVAL_PETROL,
                        default=self.config_entry.options.get(
                            CONF_UPDATE_INTERVAL_PETROL,
                            DEFAULT_UPDATE_INTERVAL_PETROL,
                        ),
                    ): vol.All(vol.Coerce(int), vol.Range(min=1, max=1440)),
                    vol.Optional(
                        CONF_UPDATE_INTERVAL_WEATHER,
                        default=self.config_entry.options.get(
                            CONF_UPDATE_INTERVAL_WEATHER,
                            DEFAULT_UPDATE_INTERVAL_WEATHER,
                        ),
                    ): vol.All(vol.Coerce(int), vol.Range(min=1, max=1440)),
                    vol.Optional(
                        CONF_UPDATE_INTERVAL_POLLEN,
                        default=self.config_entry.options.get(
                            CONF_UPDATE_INTERVAL_POLLEN,
                            DEFAULT_UPDATE_INTERVAL_POLLEN,
                        ),
                    ): vol.All(vol.Coerce(int), vol.Range(min=1, max=1440)),
                    vol.Optional(
                        CONF_UPDATE_INTERVAL_WASTE,
                        default=self.config_entry.options.get(
                            CONF_UPDATE_INTERVAL_WASTE,
                            DEFAULT_UPDATE_INTERVAL_WASTE,
                        ),
                    ): vol.All(vol.Coerce(int), vol.Range(min=1, max=1440)),
                }
            ),
        )

