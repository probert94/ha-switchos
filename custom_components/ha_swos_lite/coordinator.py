"""The Mikrotik Switch class."""

from datetime import timedelta
import logging
from typing import Any

from httpx import AsyncClient, DigestAuth, HTTPStatusError, TransportError
from python_swos_lite.client import Client
from python_swos_lite.endpoints.link import LinkEndpoint
from python_swos_lite.endpoints.poe import PoEEndpoint
from python_swos_lite.endpoints.sys import SystemEndpoint
from python_swos_lite.http import createHttpClient

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    CONF_USERNAME,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DEFAULT_UPDATE_INTERVAL, DOMAIN
from .errors import AuthError, CannotConnect
from .port import Port

_LOGGER = logging.getLogger(__name__)

type MikrotikSwosLiteConfigEntry = ConfigEntry[MikrotikSwosLiteCoordinator]


class MikrotikSwosLiteData:
    """Handle all communication with the Switch."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize the Mikrotik Client."""
        self.hass = hass
        self.config_entry = config_entry
        self.client = _create_client(config_entry.data)
        self.device: SystemEndpoint | None = None
        self.link: LinkEndpoint | None = None
        self.poe: PoEEndpoint | None = None

    async def setup(self):
        """Set up the data class by loading system information."""
        self.device = await self.client.fetch(SystemEndpoint)
        self.link = await self.client.fetch(LinkEndpoint)

    async def updatePoE(self):
        """Fetch PoE data."""
        self.poe = await self.client.fetch(PoEEndpoint)

    @property
    def ports(self) -> list[Port]:
        """Return the ports of this hub."""
        return [Port(i, self.link) for i, _ in enumerate(self.link.enabled)]


class MikrotikSwosLiteCoordinator(DataUpdateCoordinator[None]):
    """Mikrotik SwOs Lite Hub Object."""

    config_entry: MikrotikSwosLiteConfigEntry

    def __init__(
        self, hass: HomeAssistant, config_entry: MikrotikSwosLiteConfigEntry
    ) -> None:
        """Initialize the Mikrotik Client."""
        super().__init__(
            hass,
            _LOGGER,
            config_entry=config_entry,
            name=f"{DOMAIN} - {config_entry.data[CONF_HOST]}",
            update_interval=timedelta(
                seconds=config_entry.data.get(
                    CONF_SCAN_INTERVAL, DEFAULT_UPDATE_INTERVAL
                )
            ),
        )
        self._mk_data = MikrotikSwosLiteData(hass, config_entry)

    @property
    def host(self) -> str:
        """Return the host of this hub."""
        return str(self.config_entry.data[CONF_HOST])

    @property
    def identity(self) -> str:
        """Return the identity (name) of the hub."""
        return self._mk_data.device.identity

    @property
    def model(self) -> str:
        """Return the model of the hub."""
        return self._mk_data.device.model

    @property
    def firmware(self) -> str:
        """Return the firmware version of the hub."""
        return self._mk_data.device.version

    @property
    def serial_num(self) -> str:
        """Return the serial number of the hub."""
        return self._mk_data.device.serial

    @property
    def mac(self) -> str:
        """Return the MAC address of the hub."""
        return self._mk_data.device.mac

    @property
    def api(self) -> MikrotikSwosLiteData:
        """Represent Mikrotik Switch data object."""
        return self._mk_data

    async def _async_setup(self):
        await self._mk_data.setup()

    async def _async_update_data(self):
        try:
            await self._mk_data.updatePoE()
        except HTTPStatusError as err:
            if err.response.status_code == 401:
                raise ConfigEntryAuthFailed from err
            raise UpdateFailed("Error fetching data from API") from err


class MikrotikSwosLiteDevice:
    """Mikrotik SwitchOS Lite device."""

    identity: str
    serial_num: str
    model: str
    firmware: str
    ports: int

    def __init__(
        self, identity: str, serial_num: str, model: str, firmware: str, ports: int
    ) -> None:
        """Initialize the Mikrotik Switch OS Lite device."""
        self.identity = identity
        self.serial_num = serial_num
        self.model = model
        self.firmware = firmware
        self.ports = ports


async def test_connection(entry: dict[str, Any]) -> None:
    """Test connection to API with given settings."""
    _LOGGER.debug("Connecting to Mikrotik SwitchOS Lite [%s]", entry[CONF_HOST])

    client = _create_client(entry)
    try:
        await client.fetch(SystemEndpoint)
    except HTTPStatusError as err:
        if err.response.status_code == 401:
            raise AuthError from err
    except (TransportError, OSError, TimeoutError) as err:
        raise CannotConnect from err


def _create_client(entry: dict[str, Any]) -> Client:
    auth = DigestAuth(entry[CONF_USERNAME], entry[CONF_PASSWORD])
    httpClient: AsyncClient = AsyncClient(auth=auth)
    return Client(createHttpClient(httpClient), entry[CONF_HOST])
