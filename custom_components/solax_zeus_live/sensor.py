"""Sensor platform for SolaX Zeus Live integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    CONF_INVERTER_SN,
    CONF_INVERTER_TYPE,
    CONF_ENTITY_PREFIX,
    SENSOR_DEFS,
    PRIMARY_SENSORS,
)

_LOGGER = logging.getLogger(__name__)

DEVICE_CLASS_MAP = {
    "power": SensorDeviceClass.POWER,
    "voltage": SensorDeviceClass.VOLTAGE,
    "current": SensorDeviceClass.CURRENT,
    "frequency": SensorDeviceClass.FREQUENCY,
    "battery": SensorDeviceClass.BATTERY,
    "apparent_power": SensorDeviceClass.APPARENT_POWER,
    "reactive_power": SensorDeviceClass.REACTIVE_POWER,
    "power_factor": SensorDeviceClass.POWER_FACTOR,
}

STATE_CLASS_MAP = {
    "measurement": SensorStateClass.MEASUREMENT,
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up SolaX Zeus Live sensors."""
    ws_client = hass.data[DOMAIN][entry.entry_id]
    inverter_sn = entry.data[CONF_INVERTER_SN]
    inverter_type = entry.data.get(CONF_INVERTER_TYPE, "SolaX Inverter")
    prefix = entry.data.get(CONF_ENTITY_PREFIX, "").strip()

    entities = []
    for code, (name, unit, dev_class, state_class, icon) in SENSOR_DEFS.items():
        display_name = f"{prefix} {name}" if prefix else name
        entities.append(
            SolaxZeusLiveSensor(
                ws_client=ws_client,
                code=code,
                name=display_name,
                unit=unit,
                device_class_str=dev_class,
                state_class_str=state_class,
                icon_str=icon,
                inverter_sn=inverter_sn,
                inverter_type=inverter_type,
                enabled_default=code in PRIMARY_SENSORS,
            )
        )

    # Connection status sensor
    conn_name = f"{prefix} Zeus WS Connection" if prefix else "Zeus WS Connection"
    entities.append(
        SolaxZeusConnectionSensor(
            ws_client=ws_client,
            inverter_sn=inverter_sn,
            name=conn_name,
        )
    )

    async_add_entities(entities)


class SolaxZeusLiveSensor(SensorEntity):
    """A sensor that receives 10-second updates from SolaX Zeus WebSocket."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(
        self,
        ws_client,
        code: str,
        name: str,
        unit: str,
        device_class_str: str,
        state_class_str: str,
        icon_str: str | None,
        inverter_sn: str,
        inverter_type: str,
        enabled_default: bool = True,
    ) -> None:
        self._ws_client = ws_client
        self._code = code
        self._attr_name = name
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = DEVICE_CLASS_MAP.get(device_class_str)
        self._attr_state_class = STATE_CLASS_MAP.get(state_class_str)
        if icon_str:
            self._attr_icon = icon_str
        self._attr_unique_id = f"solax_zeus_{inverter_sn}_{code}"
        self._attr_entity_registry_enabled_default = enabled_default
        self._inverter_sn = inverter_sn
        self._inverter_type = inverter_type

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._inverter_sn)},
            name=f"SolaX Inverter {self._inverter_sn}",
            manufacturer="SolaX Power",
            model=self._inverter_type,
            sw_version="Zeus Live WS",
        )

    async def async_added_to_hass(self) -> None:
        """Register callback when entity is added."""
        self._ws_client.register_callback(self._handle_data)
        # Set initial value from last data
        if self._code in self._ws_client.last_data:
            self._attr_native_value = self._ws_client.last_data[self._code]

    async def async_will_remove_from_hass(self) -> None:
        """Remove callback when entity is removed."""
        try:
            self._ws_client.remove_callback(self._handle_data)
        except ValueError:
            pass

    @callback
    def _handle_data(self, data: dict[str, Any]) -> None:
        """Handle incoming WebSocket data."""
        if self._code in data:
            self._attr_native_value = data[self._code]
            self.async_write_ha_state()


class SolaxZeusConnectionSensor(SensorEntity):
    """Shows WebSocket connection status."""

    _attr_has_entity_name = True
    _attr_should_poll = True
    _attr_icon = "mdi:websocket"

    def __init__(self, ws_client, inverter_sn: str, name: str = "Zeus WS Connection") -> None:
        self._ws_client = ws_client
        self._attr_name = name
        self._attr_unique_id = f"solax_zeus_{inverter_sn}_connection"
        self._inverter_sn = inverter_sn

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._inverter_sn)},
        )

    @property
    def native_value(self) -> str:
        if self._ws_client.data_stale:
            return "Stale"
        return "Connected" if self._ws_client.connected else "Disconnected"
