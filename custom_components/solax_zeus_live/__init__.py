"""SolaX Zeus Live integration - 10-second real-time data via WebSocket."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import (
    DOMAIN,
    PLATFORMS,
    CONF_JWT_TOKEN,
    CONF_USER_ID,
    CONF_INVERTER_SN,
    CONF_WIFI_SN,
    CONF_WS_HOST,
    CONF_SOLAX_USERNAME,
    CONF_SOLAX_PASSWORD,
    CONF_SITE_ID,
    DEFAULT_WS_HOST,
)
from .websocket_client import SolaxZeusWebSocket

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up SolaX Zeus Live from a config entry."""
    ws_client = SolaxZeusWebSocket(        inverter_sn=entry.data[CONF_INVERTER_SN],
        wifi_sn=entry.data[CONF_WIFI_SN],
        ws_host=entry.data.get(CONF_WS_HOST, DEFAULT_WS_HOST),
        jwt_token=entry.data.get(CONF_JWT_TOKEN),
        user_id=entry.data.get(CONF_USER_ID),
        solax_username=entry.data.get(CONF_SOLAX_USERNAME),
        solax_password=entry.data.get(CONF_SOLAX_PASSWORD),
        site_id=entry.data.get(CONF_SITE_ID),
    )

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = ws_client

    # Start WebSocket connection
    await ws_client.start()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    ws_client = hass.data[DOMAIN].get(entry.entry_id)
    if ws_client:
        await ws_client.stop()

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)

    return unload_ok
