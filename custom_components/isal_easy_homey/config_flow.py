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
    CONF_API_KEY,
    CONF_LOCATION_ENTITY_ID,
    CONF_LOCATION_ENTITY_ID_CHEAPEST,
    CONF_LOCATION_ENTITY_ID_NEAREST,
    CONF_USER_LOCATIONS,
    CONF_STATION_IDS,
    CONF_PETROL_TYPE,
    CONF_SEARCH_RADIUS,
    CONF_UPDATE_INTERVAL_PETROL,
    CONF_UPDATE_INTERVAL_POLLEN,
    CONF_UPDATE_INTERVAL_WASTE,
    CONF_UPDATE_INTERVAL_WEATHER,
    CONF_UPDATE_INTERVAL_SERVICE_INFO,
    CONF_WARNING_CELL_ID,
    DEFAULT_API_BASE_URL,
    DEFAULT_PETROL_TYPE,
    DEFAULT_SEARCH_RADIUS,
    DEFAULT_UPDATE_INTERVAL_PETROL,
    DEFAULT_UPDATE_INTERVAL_POLLEN,
    DEFAULT_UPDATE_INTERVAL_WASTE,
    DEFAULT_UPDATE_INTERVAL_WEATHER,
    DEFAULT_UPDATE_INTERVAL_SERVICE_INFO,
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
    api_key = data.get(CONF_API_KEY)
    client = IsalEasyHomeyApiClient(data[CONF_API_BASE_URL], session, api_key)

    # Test the connection
    await client.test_connection()

    # Validate location entity for cheapest station
    if CONF_LOCATION_ENTITY_ID_CHEAPEST in data and data[CONF_LOCATION_ENTITY_ID_CHEAPEST]:
        state = hass.states.get(data[CONF_LOCATION_ENTITY_ID_CHEAPEST])
        if state is None:
            raise ValueError(f"Entity {data[CONF_LOCATION_ENTITY_ID_CHEAPEST]} not found")

        # Check if entity has location attributes
        if not (
            state.attributes.get("latitude") and state.attributes.get("longitude")
        ):
            raise ValueError(
                f"Entity {data[CONF_LOCATION_ENTITY_ID_CHEAPEST]} does not have location attributes"
            )

    # Validate location entity for nearest station
    if CONF_LOCATION_ENTITY_ID_NEAREST in data and data[CONF_LOCATION_ENTITY_ID_NEAREST]:
        state = hass.states.get(data[CONF_LOCATION_ENTITY_ID_NEAREST])
        if state is None:
            raise ValueError(f"Entity {data[CONF_LOCATION_ENTITY_ID_NEAREST]} not found")

        # Check if entity has location attributes
        if not (
            state.attributes.get("latitude") and state.attributes.get("longitude")
        ):
            raise ValueError(
                f"Entity {data[CONF_LOCATION_ENTITY_ID_NEAREST]} does not have location attributes"
            )

    # Validate old location entity if provided (backwards compatibility)
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
                    vol.Required(CONF_API_KEY): str,
                    vol.Optional(CONF_LOCATION_ENTITY_ID_CHEAPEST): selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain=["device_tracker", "person", "zone"]
                        )
                    ),
                    vol.Optional(CONF_LOCATION_ENTITY_ID_NEAREST): selector.EntitySelector(
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
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
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
        _LOGGER.debug("Initializing options flow for entry: %s", config_entry.entry_id)
        super().__init__()
        self._config_entry = config_entry
        try:
            _LOGGER.debug("Options: %s", config_entry.options)
            _LOGGER.debug("Data: %s", config_entry.data)
            self._user_locations = list(
                config_entry.options.get(
                    CONF_USER_LOCATIONS,
                    config_entry.data.get(CONF_USER_LOCATIONS, [])
                )
            )
            self._station_ids = list(
                config_entry.options.get(
                    CONF_STATION_IDS,
                    config_entry.data.get(CONF_STATION_IDS, [])
                )
            )
            _LOGGER.debug("Loaded %d user locations and %d station IDs",
                         len(self._user_locations), len(self._station_ids))
        except Exception as err:
            _LOGGER.exception("Error initializing options flow: %s", err)
            self._user_locations = []
            self._station_ids = []

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options.

        Args:
            user_input: The user input data

        Returns:
            The flow result

        """
        _LOGGER.debug("Options flow init step, user_input: %s", user_input)
        try:
            return self.async_show_menu(
                step_id="init",
                menu_options=["general_settings", "user_locations", "station_ids"],
            )
        except Exception as err:
            _LOGGER.exception("Error in options flow init: %s", err)
            raise

    async def async_step_general_settings(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage general settings.

        Args:
            user_input: The user input data

        Returns:
            The flow result

        """
        _LOGGER.debug("General settings step, user_input: %s", user_input)
        if user_input is not None:
            # Merge with existing user_locations and station_ids
            user_input[CONF_USER_LOCATIONS] = self._user_locations
            user_input[CONF_STATION_IDS] = self._station_ids
            _LOGGER.debug("Saving general settings: %s", user_input)
            return self.async_create_entry(title="", data=user_input)

        # Get current values with proper fallbacks
        _LOGGER.debug("Loading current general settings")
        try:
            api_base_url = self._config_entry.options.get(
                CONF_API_BASE_URL,
                self._config_entry.data.get(CONF_API_BASE_URL, DEFAULT_API_BASE_URL)
            )
            api_key = self._config_entry.options.get(
                CONF_API_KEY,
                self._config_entry.data.get(CONF_API_KEY, "")
            )
            search_radius = self._config_entry.options.get(
                CONF_SEARCH_RADIUS,
                self._config_entry.data.get(CONF_SEARCH_RADIUS, DEFAULT_SEARCH_RADIUS)
            )
            warning_cell_id = self._config_entry.options.get(
                CONF_WARNING_CELL_ID,
                self._config_entry.data.get(CONF_WARNING_CELL_ID, DEFAULT_WARNING_CELL_ID)
            )
        except Exception as err:
            _LOGGER.exception("Error getting current settings: %s", err)
            api_base_url = DEFAULT_API_BASE_URL
            api_key = ""
            search_radius = DEFAULT_SEARCH_RADIUS
            warning_cell_id = DEFAULT_WARNING_CELL_ID

        return self.async_show_form(
            step_id="general_settings",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_API_BASE_URL,
                        default=api_base_url,
                    ): str,
                    vol.Required(
                        CONF_API_KEY,
                        default=api_key,
                    ): str,
                    vol.Optional(
                        CONF_SEARCH_RADIUS,
                        default=search_radius,
                    ): vol.All(
                        vol.Coerce(float),
                        vol.Range(min=MIN_SEARCH_RADIUS, max=MAX_SEARCH_RADIUS),
                    ),
                    vol.Optional(
                        CONF_WARNING_CELL_ID,
                        default=warning_cell_id,
                    ): str,
                    vol.Optional(
                        CONF_UPDATE_INTERVAL_PETROL,
                        default=self._config_entry.options.get(
                            CONF_UPDATE_INTERVAL_PETROL,
                            DEFAULT_UPDATE_INTERVAL_PETROL,
                        ),
                    ): vol.All(vol.Coerce(int), vol.Range(min=1, max=1440)),
                    vol.Optional(
                        CONF_UPDATE_INTERVAL_WEATHER,
                        default=self._config_entry.options.get(
                            CONF_UPDATE_INTERVAL_WEATHER,
                            DEFAULT_UPDATE_INTERVAL_WEATHER,
                        ),
                    ): vol.All(vol.Coerce(int), vol.Range(min=1, max=1440)),
                    vol.Optional(
                        CONF_UPDATE_INTERVAL_POLLEN,
                        default=self._config_entry.options.get(
                            CONF_UPDATE_INTERVAL_POLLEN,
                            DEFAULT_UPDATE_INTERVAL_POLLEN,
                        ),
                    ): vol.All(vol.Coerce(int), vol.Range(min=1, max=1440)),
                    vol.Optional(
                        CONF_UPDATE_INTERVAL_WASTE,
                        default=self._config_entry.options.get(
                            CONF_UPDATE_INTERVAL_WASTE,
                            DEFAULT_UPDATE_INTERVAL_WASTE,
                        ),
                    ): vol.All(vol.Coerce(int), vol.Range(min=1, max=1440)),
                    vol.Optional(
                        CONF_UPDATE_INTERVAL_SERVICE_INFO,
                        default=self._config_entry.options.get(
                            CONF_UPDATE_INTERVAL_SERVICE_INFO,
                            DEFAULT_UPDATE_INTERVAL_SERVICE_INFO,
                        ),
                    ): vol.All(vol.Coerce(int), vol.Range(min=1, max=1440)),
                }
            ),
        )

    async def async_step_user_locations(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage user locations.

        Args:
            user_input: The user input data

        Returns:
            The flow result

        """
        if user_input is not None:
            action = user_input.get("action")
            if action == "add":
                return await self.async_step_add_user_location()
            elif action == "remove" and self._user_locations:
                return await self.async_step_remove_user_location()
            elif action == "done":
                # Save and return
                options = dict(self._config_entry.options)
                options[CONF_USER_LOCATIONS] = self._user_locations
                return self.async_create_entry(title="", data=options)

        # Show current user locations
        locations_info = "\n".join(
            [
                f"- {loc.get('name')}: {loc.get('entity_id')}"
                for loc in self._user_locations
            ]
        ) if self._user_locations else "Keine Benutzer-Standorte konfiguriert"

        return self.async_show_form(
            step_id="user_locations",
            data_schema=vol.Schema(
                {
                    vol.Required("action", default="done"): vol.In(
                        {
                            "add": "Neuen Standort hinzufügen",
                            "remove": "Standort entfernen",
                            "done": "Fertig",
                        }
                    ),
                }
            ),
            description_placeholders={"locations": locations_info},
        )

    async def async_step_add_user_location(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Add a new user location.

        Args:
            user_input: The user input data

        Returns:
            The flow result

        """
        errors: dict[str, str] = {}

        if user_input is not None:
            name = user_input.get("name")
            entity_id = user_input.get("entity_id")

            # Validate entity exists
            if entity_id:
                state = self.hass.states.get(entity_id)
                if state is None:
                    errors["entity_id"] = "invalid_entity"
                elif not (
                    state.attributes.get("latitude") and state.attributes.get("longitude")
                ):
                    errors["entity_id"] = "invalid_entity"

            if not errors:
                # Add to list
                self._user_locations.append(
                    {
                        "name": name,
                        "entity_id": entity_id,
                    }
                )
                return await self.async_step_user_locations()

        return self.async_show_form(
            step_id="add_user_location",
            data_schema=vol.Schema(
                {
                    vol.Required("name"): str,
                    vol.Required("entity_id"): selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain=["device_tracker", "person", "zone"]
                        )
                    ),
                }
            ),
            errors=errors,
        )

    async def async_step_remove_user_location(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Remove a user location.

        Args:
            user_input: The user input data

        Returns:
            The flow result

        """
        if user_input is not None:
            location_to_remove = user_input.get("location")
            self._user_locations = [
                loc
                for loc in self._user_locations
                if loc.get("name") != location_to_remove
            ]
            return await self.async_step_user_locations()

        # Build selection list
        location_options = {
            loc.get("name"): f"{loc.get('name')} ({loc.get('entity_id')})"
            for loc in self._user_locations
        }

        return self.async_show_form(
            step_id="remove_user_location",
            data_schema=vol.Schema(
                {
                    vol.Required("location"): vol.In(location_options),
                }
            ),
        )

    async def async_step_station_ids(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage station IDs.

        Args:
            user_input: The user input data

        Returns:
            The flow result

        """
        if user_input is not None:
            action = user_input.get("action")
            if action == "add":
                return await self.async_step_add_station_id()
            elif action == "remove" and self._station_ids:
                return await self.async_step_remove_station_id()
            elif action == "done":
                # Save and return
                options = dict(self._config_entry.options)
                options[CONF_STATION_IDS] = self._station_ids
                options[CONF_USER_LOCATIONS] = self._user_locations
                return self.async_create_entry(title="", data=options)

        # Show current station IDs
        stations_info = "\n".join(
            [f"- {station_id}" for station_id in self._station_ids]
        ) if self._station_ids else "Keine Tankstellen-IDs konfiguriert"

        return self.async_show_form(
            step_id="station_ids",
            data_schema=vol.Schema(
                {
                    vol.Required("action", default="done"): vol.In(
                        {
                            "add": "Neue Tankstellen-ID hinzufügen",
                            "remove": "Tankstellen-ID entfernen",
                            "done": "Fertig",
                        }
                    ),
                }
            ),
            description_placeholders={"stations": stations_info},
        )

    async def async_step_add_station_id(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Add a new station ID.

        Args:
            user_input: The user input data

        Returns:
            The flow result

        """
        errors: dict[str, str] = {}

        if user_input is not None:
            station_id = user_input.get("station_id", "").strip()

            # Validate station ID
            if not station_id:
                errors["station_id"] = "invalid_station_id"
            elif station_id in self._station_ids:
                errors["station_id"] = "station_id_exists"
            else:
                # Try to fetch the station to validate it exists
                # But allow adding even if API is not reachable (for reconfiguration scenarios)
                try:
                    session = async_get_clientsession(self.hass)
                    api_base_url = self._config_entry.options.get(
                        CONF_API_BASE_URL,
                        self._config_entry.data.get(CONF_API_BASE_URL, DEFAULT_API_BASE_URL)
                    )
                    api_key = self._config_entry.options.get(
                        CONF_API_KEY,
                        self._config_entry.data.get(CONF_API_KEY)
                    )
                    client = IsalEasyHomeyApiClient(api_base_url, session, api_key)
                    await client.get_petrol_station(station_id)
                    _LOGGER.debug("Successfully validated station ID %s", station_id)

                except (IsalEasyHomeyApiConnectionError, IsalEasyHomeyApiTimeoutError):
                    # API not reachable - allow adding anyway
                    _LOGGER.warning(
                        "Could not validate station ID %s - API not reachable. Adding anyway.",
                        station_id
                    )
                except IsalEasyHomeyApiError as err:
                    # Other API error - station might not exist
                    _LOGGER.error("Error validating station ID %s: %s", station_id, err)
                    errors["station_id"] = "invalid_station_id"
                except Exception as err:
                    # Unexpected error - log but allow adding
                    _LOGGER.exception("Unexpected error validating station ID %s: %s", station_id, err)

                if not errors:
                    # Add to list
                    self._station_ids.append(station_id)
                    return await self.async_step_station_ids()

        return self.async_show_form(
            step_id="add_station_id",
            data_schema=vol.Schema(
                {
                    vol.Required("station_id"): str,
                }
            ),
            errors=errors,
        )

    async def async_step_remove_station_id(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Remove a station ID.

        Args:
            user_input: The user input data

        Returns:
            The flow result

        """
        if user_input is not None:
            station_to_remove = user_input.get("station_id")
            self._station_ids = [
                sid for sid in self._station_ids if sid != station_to_remove
            ]
            return await self.async_step_station_ids()

        # Build selection list
        station_options = {sid: sid for sid in self._station_ids}

        return self.async_show_form(
            step_id="remove_station_id",
            data_schema=vol.Schema(
                {
                    vol.Required("station_id"): vol.In(station_options),
                }
            ),
        )

