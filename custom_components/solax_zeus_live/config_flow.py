"""Config flow for SolaX Zeus Live integration."""
from __future__ import annotations

import asyncio
import json
import logging
import ssl

import aiohttp
import voluptuous as vol
import websockets

from homeassistant import config_entries

from .const import (
    DOMAIN,
    CONF_JWT_TOKEN,
    CONF_USER_ID,
    CONF_INVERTER_SN,
    CONF_WIFI_SN,
    CONF_WS_HOST,
    CONF_SOLAX_USERNAME,
    CONF_SOLAX_PASSWORD,
    CONF_SITE_ID,
    CONF_INVERTER_TYPE,
    CONF_ENTITY_PREFIX,
    DEFAULT_WS_HOST,
    LOGIN_URL,
    LIVE_DATA_ENABLE_URL,
)

_LOGGER = logging.getLogger(__name__)


async def _login(username: str, password: str, host: str) -> dict | None:
    """Login to SolaX Cloud and return tokenId + userId."""
    login_url = LOGIN_URL.format(host=host)
    headers = {
        "version": "green",
        "Lang": "en_US",
        "deviceType": "3",
    }
    form_data = aiohttp.FormData()
    form_data.add_field("userName", username)
    form_data.add_field("password", password)

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                login_url, data=form_data, headers=headers,
                timeout=aiohttp.ClientTimeout(total=15),
            ) as resp:
                data = await resp.json()

        if data.get("success"):
            return data["result"]
    except Exception as err:
        _LOGGER.error("Login failed: %s", err)
    return None


async def _fetch_site_and_devices(token: str, host: str) -> dict | None:
    """Fetch site_id, inverter SN, and wifi SN from SolaX Cloud."""
    headers = {
        "Content-Type": "application/json",
        "tokenId": token,
        "version": "green",
    }

    try:
        async with aiohttp.ClientSession() as session:
            # Get site list
            async with session.post(
                f"https://{host}/zeus/v1/site/getSiteList",
                json={}, headers=headers,
                timeout=aiohttp.ClientTimeout(total=15),
            ) as resp:
                site_data = await resp.json()

            if not site_data.get("success"):
                return None

            records = site_data.get("result", {}).get("records", [])
            if not records:
                return None

            site_id = str(records[0]["siteId"])
            site_name = records[0].get("siteName", "")

            # Get device list via liveDataEnable
            async with session.post(
                LIVE_DATA_ENABLE_URL.format(host=host),
                json={"siteId": site_id}, headers=headers,
                timeout=aiohttp.ClientTimeout(total=15),
            ) as resp:
                device_data = await resp.json()

            if not device_data.get("success") or not device_data.get("result"):
                return None

            # Find the inverter
            for dev in device_data["result"]:
                if dev.get("category") == "Inverter":
                    return {
                        "site_id": site_id,
                        "site_name": site_name,
                        "inverter_sn": dev["inverterSn"],
                        "wifi_sn": dev["wifiSn"],
                        "inverter_type": dev.get("inverterType", "Unknown"),
                    }

    except Exception as err:
        _LOGGER.error("Failed to fetch site/device info: %s", err)
    return None


async def _test_ws(token: str, user_id: str, host: str) -> bool:
    """Test WebSocket connection with a token."""
    url = f"wss://{host}/websocket/{user_id}/{token}/web"
    try:
        loop = asyncio.get_running_loop()
        ssl_ctx = await loop.run_in_executor(None, ssl.create_default_context)
        async with websockets.connect(
            url, ssl=ssl_ctx,
            additional_headers={"Origin": f"https://{host}"},
            open_timeout=10,
        ) as ws:
            await ws.send(json.dumps({"command": "PING"}))
            msg = await asyncio.wait_for(ws.recv(), timeout=10)
            return json.loads(msg).get("command") == "PONG"
    except Exception as err:
        _LOGGER.error("WS test failed: %s", err)
        return False


class SolaxZeusLiveConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SolaX Zeus Live."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            host = user_input.get(CONF_WS_HOST) or DEFAULT_WS_HOST
            user_input[CONF_WS_HOST] = host
            username = user_input[CONF_SOLAX_USERNAME].strip()
            password = user_input[CONF_SOLAX_PASSWORD]

            # Login to SolaX Cloud
            result = await _login(username, password, host)
            if not result:
                errors["base"] = "invalid_auth"
            else:
                token = result["tokenId"]
                user_id = result["userId"]

                # Auto-detect site and device info
                info = await _fetch_site_and_devices(token, host)
                if not info:
                    errors["base"] = "no_devices"
                elif not await _test_ws(token, user_id, host):
                    errors["base"] = "cannot_connect"
                else:
                    data = {
                        CONF_SOLAX_USERNAME: username,
                        CONF_SOLAX_PASSWORD: password,
                        CONF_WS_HOST: host,
                        CONF_JWT_TOKEN: token,
                        CONF_USER_ID: user_id,
                        CONF_SITE_ID: info["site_id"],
                        CONF_INVERTER_SN: info["inverter_sn"],
                        CONF_WIFI_SN: info["wifi_sn"],
                        CONF_INVERTER_TYPE: info["inverter_type"],
                        CONF_ENTITY_PREFIX: user_input.get(CONF_ENTITY_PREFIX, "").strip(),
                    }

                    await self.async_set_unique_id(info["inverter_sn"])
                    self._abort_if_unique_id_configured()

                    title = f"SolaX {info['inverter_type']} ({info['inverter_sn']})"
                    return self.async_create_entry(title=title, data=data)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_SOLAX_USERNAME): str,
                    vol.Required(CONF_SOLAX_PASSWORD): str,
                    vol.Optional(CONF_ENTITY_PREFIX, default=""): str,
                    vol.Optional(CONF_WS_HOST, default=DEFAULT_WS_HOST): str,
                }
            ),
            errors=errors,
        )
