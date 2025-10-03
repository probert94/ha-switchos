"""Platform for sensor integration."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfPower,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTR_MANUFACTURER, DOMAIN
from .coordinator import (
    MikrotikSwitchOSConfigEntry,
    MikrotikSwitchOSCoordinator,
    MikrotikSwitchOSData,
)
from .port import Port


@dataclass(frozen=True, kw_only=True)
class MikrotikSwitchOSEntityDescription(SensorEntityDescription):
    """Describes a Mikrotik SwitchOS Sensor."""

    endpoint: str
    property: str
    enabled_by_default: Callable[[MikrotikSwitchOSData], bool] | None = None


GLOBAL_SENSORS: tuple[MikrotikSwitchOSEntityDescription, ...] = (
    MikrotikSwitchOSEntityDescription(
        key="cpu_temperature",
        translation_key="cpu_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        suggested_display_precision=0,
        endpoint="sys",
        property="cpu_temp",
    ),
    MikrotikSwitchOSEntityDescription(
        key="psu1_current",
        translation_key="psu1_current",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricCurrent.MILLIAMPERE,
        suggested_display_precision=0,
        endpoint="sys",
        property="psu1_current",
        enabled_by_default=lambda api: api.poe is not None,
    ),
    MikrotikSwitchOSEntityDescription(
        key="psu1_voltage",
        translation_key="psu1_voltage",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        suggested_display_precision=2,
        endpoint="sys",
        property="psu1_voltage",
        enabled_by_default=lambda api: api.poe is not None,
    ),
    MikrotikSwitchOSEntityDescription(
        key="psu1_power",
        translation_key="psu1_power",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        suggested_display_precision=1,
        endpoint="sys",
        property="psu1_power",
        enabled_by_default=lambda api: api.poe is not None,
    ),
    MikrotikSwitchOSEntityDescription(
        key="psu2_current",
        translation_key="psu2_current",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricCurrent.MILLIAMPERE,
        suggested_display_precision=0,
        endpoint="sys",
        property="psu2_current",
        enabled_by_default=lambda api: api.poe is not None,
    ),
    MikrotikSwitchOSEntityDescription(
        key="psu2_voltage",
        translation_key="psu2_voltage",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        suggested_display_precision=2,
        endpoint="sys",
        property="psu2_voltage",
        enabled_by_default=lambda api: api.poe is not None,
    ),
    MikrotikSwitchOSEntityDescription(
        key="psu2_power",
        translation_key="psu2_power",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        suggested_display_precision=1,
        endpoint="sys",
        property="psu2_power",
        enabled_by_default=lambda api: api.poe is not None,
    ),
    MikrotikSwitchOSEntityDescription(
        key="total_power",
        translation_key="total_power",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        suggested_display_precision=1,
        endpoint="sys",
        property="power_consumption",
        enabled_by_default=lambda api: api.poe is not None,
    ),
)

PORT_SENSORS: tuple[MikrotikSwitchOSEntityDescription, ...] = (
    MikrotikSwitchOSEntityDescription(
        key="poe_power",
        translation_key="poe_power",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        suggested_display_precision=1,
        endpoint="poe",
        property="power",
    ),
    MikrotikSwitchOSEntityDescription(
        key="poe_current",
        translation_key="poe_current",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricCurrent.MILLIAMPERE,
        suggested_display_precision=1,
        endpoint="poe",
        property="current",
    ),
    MikrotikSwitchOSEntityDescription(
        key="poe_voltage",
        translation_key="poe_voltage",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        suggested_display_precision=1,
        endpoint="poe",
        property="voltage",
    ),
)


async def async_setup_entry(
    _: HomeAssistant,
    config_entry: MikrotikSwitchOSConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Setup sensor for Mikrotik SwitchOS component."""
    coordinator = config_entry.runtime_data

    device = {
        "identifiers": {(DOMAIN, coordinator.serial_num)},
        "connections": {("mac", coordinator.mac)},
        "manufacturer": ATTR_MANUFACTURER,
        "model": coordinator.model,
        "name": coordinator.identity,
        "serial_number": coordinator.serial_num,
        "sw_version": coordinator.firmware,
    }

    async_add_entities(
        [
            MikrotikSwitchOSSensor(coordinator, device, global_sensor)
            for global_sensor in GLOBAL_SENSORS
            if _global_entity_exists(global_sensor, coordinator.api)
        ]
    )
    async_add_entities(
        [
            MikrotikSwitchOSPortSensor(coordinator, device, port_sensor, port)
            for port_sensor in PORT_SENSORS
            for port in coordinator.api.ports
            if _port_entity_exists(port_sensor, coordinator.api, port)
        ]
    )


def _global_entity_exists(
    entity_desc: MikrotikSwitchOSEntityDescription, api: MikrotikSwitchOSData
) -> bool:
    return (
        getattr(getattr(api, entity_desc.endpoint, None), entity_desc.property, None)
        is not None
    )


def _port_entity_exists(
    entity_desc: MikrotikSwitchOSEntityDescription,
    api: MikrotikSwitchOSData,
    port: Port,
) -> bool:
    value = getattr(
        getattr(api, entity_desc.endpoint, None), entity_desc.property, None
    )
    return isinstance(value, (tuple, list)) and len(value) > port.num


class MikrotikSwitchOSSensor(
    CoordinatorEntity[MikrotikSwitchOSCoordinator], SensorEntity
):
    """Representation of a Mikrotik SwitchOS Sensor."""

    entity_description: MikrotikSwitchOSEntityDescription

    def __init__(
        self,
        coordinator: MikrotikSwitchOSCoordinator,
        device: DeviceInfo,
        entity_description: MikrotikSwitchOSEntityDescription,
    ) -> None:
        """Initialize the sensor entity."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self.has_entity_name = True
        self._attr_unique_id = f"{coordinator.serial_num}_{entity_description.key}"
        self._attr_device_info = device

    @property
    def native_value(self) -> float:
        """Returns the current value from the API."""
        return getattr(
            getattr(self.coordinator.api, self.entity_description.endpoint),
            self.entity_description.property,
        )

    @property
    def entity_registry_enabled_default(self) -> bool:
        """Returns whether the entity should be enabled by default."""
        return (
            self.entity_description.enabled_by_default is None
            or self.entity_description.enabled_by_default(self.coordinator.api)
        )


class MikrotikSwitchOSPortSensor(MikrotikSwitchOSSensor):
    """Representation of a Mikrotik SwitchOS Port Sensor."""

    entity_description: MikrotikSwitchOSEntityDescription

    def __init__(
        self,
        coordinator: MikrotikSwitchOSCoordinator,
        device: DeviceInfo,
        entity_description: MikrotikSwitchOSEntityDescription,
        port: Port,
    ) -> None:
        """Initialize the sensor entity."""
        super().__init__(coordinator, device, entity_description)
        self.port = port
        self._attr_translation_placeholders = {
            "port_num": f"{(port.num + 1):02d}",
            "port_name": port.name,
        }
        self._attr_unique_id = (
            f"{coordinator.serial_num}_{port.num}_{entity_description.key}"
        )

    @property
    def native_value(self) -> float:
        """Returns the current value from the API."""
        return getattr(
            getattr(self.coordinator.api, self.entity_description.endpoint),
            self.entity_description.property,
        )[self.port.num]
