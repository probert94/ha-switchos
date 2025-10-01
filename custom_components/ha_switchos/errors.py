"""Errors for the Mikrotik component."""

from homeassistant.exceptions import HomeAssistantError


class CannotConnect(HomeAssistantError):
    """Unable to connect to the hub."""


class AuthError(HomeAssistantError):
    """Unable to authenticate against the hub."""
