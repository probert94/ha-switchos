"""Config flow for Mikrotik SwitchOS integration."""

from collections.abc import Mapping
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    CONF_USERNAME,
)

from .const import DEFAULT_NAME, DEFAULT_UPDATE_INTERVAL, DOMAIN
from .coordinator import test_connection
from .errors import AuthError, CannotConnect


class MikrotikSwitchOSConfigFlowHandler(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Mikrotik SwitchOS."""

    VERSION = 1
    MINOR_VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""

        host = user_input.get(CONF_HOST, "") if user_input else ""

        errors = {}
        if user_input is not None:
            self._async_abort_entries_match({CONF_HOST: user_input[CONF_HOST]})
            try:
                await test_connection(user_input)
            except CannotConnect:
                errors[CONF_HOST] = "cannot_connect"
            except AuthError:
                errors[CONF_PASSWORD] = "invalid_auth"
            if not errors:
                return self.async_create_entry(
                    title=f"{DEFAULT_NAME} ({user_input[CONF_HOST]})", data=user_input
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST, default=host): str,
                    vol.Required(CONF_USERNAME, default="admin"): str,
                    vol.Required(CONF_PASSWORD): str,
                    vol.Optional(
                        CONF_SCAN_INTERVAL, default=DEFAULT_UPDATE_INTERVAL
                    ): vol.All(vol.Coerce(int), vol.Range(min=5)),
                }
            ),
            errors=errors,
        )

    async def async_step_reauth(self, _: Mapping[str, Any]) -> ConfigFlowResult:
        """Handle re-authentication."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input=None) -> ConfigFlowResult:
        """Confirm reauth dialog."""
        errors = {}

        reauth_entry = self._get_reauth_entry()
        if user_input is not None:
            try:
                await test_connection(user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except AuthError:
                errors[CONF_PASSWORD] = "invalid_auth"
            if not errors:
                return self.async_update_reload_and_abort(reauth_entry, data=user_input)

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        "username", default=reauth_entry.data.get("username")
                    ): str,
                    vol.Required("password"): str,
                }
            ),
            errors=errors,
        )
