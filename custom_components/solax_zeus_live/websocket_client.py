"""WebSocket client for SolaX Zeus 10-second live data."""
from __future__ import annotations

import asyncio
import json
import logging
import ssl
import time
from typing import Any, Callable

import aiohttp
import websockets

from .const import DEFAULT_WS_HOST, LOGIN_URL, LIVE_DATA_ENABLE_URL

_LOGGER = logging.getLogger(__name__)

PING_INTERVAL = 5
RECONNECT_DELAY = 10
MAX_RECONNECT_DELAY = 300
TOKEN_REFRESH_BUFFER = 3600  # refresh token 1 hour before expiry
DATA_STALE_TIMEOUT = 60  # force reconnect if no PUSH_DATA for this many seconds
LIVE_ENABLE_INTERVAL = 120  # re-call liveDataEnable every 2 minutes


class SolaxZeusWebSocket:
    """Manages WebSocket connection to SolaX Cloud for live data."""

    def __init__(
        self,
        inverter_sn: str,
        wifi_sn: str,
        ws_host: str = DEFAULT_WS_HOST,
        jwt_token: str | None = None,
        user_id: str | None = None,
        solax_username: str | None = None,
        solax_password: str | None = None,
        site_id: str | None = None,
    ) -> None:
        self._jwt_token = jwt_token
        self._user_id = user_id
        self._inverter_sn = inverter_sn
        self._wifi_sn = wifi_sn
        self._ws_host = ws_host
        self._solax_username = solax_username
        self._solax_password = solax_password
        self._site_id = site_id
        self._ws: websockets.WebSocketClientProtocol | None = None
        self._running = False
        self._task: asyncio.Task | None = None
        self._callbacks: list[Callable[[dict[str, Any]], None]] = []
        self._last_data: dict[str, Any] = {}
        self._reconnect_delay = RECONNECT_DELAY
        self._connected = False
        self._token_acquired_at: float = time.time() if jwt_token else 0
        self._last_push_data_at: float = 0

    @property
    def connected(self) -> bool:
        return self._connected

    @property
    def data_stale(self) -> bool:
        """True if connected but no PUSH_DATA received recently."""
        if not self._connected or self._last_push_data_at == 0:
            return False
        return (time.time() - self._last_push_data_at) > DATA_STALE_TIMEOUT

    @property
    def last_data(self) -> dict[str, Any]:
        return self._last_data

    def register_callback(self, callback: Callable[[dict[str, Any]], None]) -> None:
        self._callbacks.append(callback)

    def remove_callback(self, callback: Callable[[dict[str, Any]], None]) -> None:
        self._callbacks.remove(callback)

    def _build_url(self) -> str:
        return f"wss://{self._ws_host}/websocket/{self._user_id}/{self._jwt_token}/web"

    async def _login(self) -> bool:
        """Login to SolaX Cloud and obtain a fresh tokenId."""
        if not self._solax_username or not self._solax_password:
            _LOGGER.debug("No credentials configured, skipping login")
            return False

        login_url = LOGIN_URL.format(host=self._ws_host)
        headers = {
            "version": "green",
            "Lang": "en_US",
            "deviceType": "3",
        }
        form_data = aiohttp.FormData()
        form_data.add_field("userName", self._solax_username)
        form_data.add_field("password", self._solax_password)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    login_url, data=form_data, headers=headers,
                    timeout=aiohttp.ClientTimeout(total=15),
                ) as resp:
                    data = await resp.json()

            if not data.get("success"):
                _LOGGER.error(
                    "SolaX login failed: %s", data.get("exception", "Unknown error")
                )
                return False

            result = data["result"]
            self._jwt_token = result["tokenId"]
            self._user_id = result["userId"]
            self._token_acquired_at = time.time()
            _LOGGER.info("SolaX login successful, new token acquired")
            return True

        except Exception as err:
            _LOGGER.error("SolaX login error: %s", err)
            return False

    async def _ensure_token(self) -> bool:
        """Ensure we have a valid token, refreshing via login if needed."""
        if self._solax_username and self._solax_password:
            # Always login to get a fresh token before connecting
            return await self._login()
        # Fall back to stored JWT
        return bool(self._jwt_token and self._user_id)

    async def _enable_live_data(self) -> bool:
        """Call liveDataEnable to tell SolaX Cloud to stream real-time data from the XHub."""
        if not self._jwt_token:
            return False

        # Auto-fetch site_id if not configured
        if not self._site_id:
            await self._fetch_site_id()
            if not self._site_id:
                _LOGGER.debug("No site_id available, skipping liveDataEnable")
                return False

        url = LIVE_DATA_ENABLE_URL.format(host=self._ws_host)
        headers = {
            "Content-Type": "application/json",
            "tokenId": self._jwt_token,
            "version": "green",
        }
        payload = {"siteId": self._site_id}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url, json=payload, headers=headers,
                    timeout=aiohttp.ClientTimeout(total=15),
                ) as resp:
                    data = await resp.json()

            if data.get("success"):
                _LOGGER.debug("liveDataEnable successful for site %s", self._site_id)
                return True
            _LOGGER.warning("liveDataEnable failed: %s", data.get("message"))
            return False
        except Exception as err:
            _LOGGER.warning("liveDataEnable error: %s", err)
            return False

    async def _fetch_site_id(self) -> None:
        """Fetch the site/plant ID from SolaX Cloud."""
        if not self._jwt_token:
            return

        url = f"https://{self._ws_host}/zeus/v1/site/getSiteList"
        headers = {
            "Content-Type": "application/json",
            "tokenId": self._jwt_token,
            "version": "green",
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url, json={}, headers=headers,
                    timeout=aiohttp.ClientTimeout(total=15),
                ) as resp:
                    data = await resp.json()

            if data.get("success"):
                records = data.get("result", {}).get("records", [])
                if records:
                    self._site_id = str(records[0].get("siteId", ""))
                    _LOGGER.info("Auto-detected site_id: %s", self._site_id)
        except Exception as err:
            _LOGGER.warning("Failed to fetch site_id: %s", err)

    async def _live_enable_loop(self) -> None:
        """Periodically re-call liveDataEnable to keep the real-time stream active."""
        while self._running and self._ws:
            try:
                await asyncio.sleep(LIVE_ENABLE_INTERVAL)
                if self._running and self._site_id:
                    await self._enable_live_data()
            except Exception:
                break

    def _build_start_message(self) -> str:
        return json.dumps({
            "type": 2,
            "version": 6,
            "data": {
                "inverterSn": self._inverter_sn,
                "wifiSn": self._wifi_sn,
            },
        })

    def _parse_push_data(self, msg: dict[str, Any]) -> dict[str, Any]:
        """Parse PUSH_DATA message into flat dict of code -> value."""
        result = msg.get("result", {})
        data: dict[str, Any] = {}

        # Parse inverter array
        for item in result.get("inverter", []):
            code = item.get("code")
            value = item.get("value")
            if code and value is not None:
                data[code] = value

        # Parse battery array
        for item in result.get("battery", []):
            code = item.get("code")
            value = item.get("value")
            if code and value is not None:
                data[code] = value

        # Add metadata
        if "time" in msg:
            data["_time"] = msg["time"]
        if "inverterSn" in msg:
            data["_inverterSn"] = msg["inverterSn"]

        return data

    async def _ping_loop(self) -> None:
        """Send periodic pings to keep connection alive."""
        while self._running and self._ws:
            try:
                await asyncio.sleep(PING_INTERVAL)
                if self._ws and self._running:
                    await self._ws.send(json.dumps({"command": "PING"}))
            except Exception:
                break

    async def _watchdog_loop(self) -> None:
        """Force reconnect if no PUSH_DATA received within timeout."""
        while self._running and self._ws:
            try:
                await asyncio.sleep(DATA_STALE_TIMEOUT / 2)
                if not self._running or not self._ws:
                    break
                if self._last_push_data_at > 0:
                    elapsed = time.time() - self._last_push_data_at
                    if elapsed > DATA_STALE_TIMEOUT:
                        _LOGGER.warning(
                            "No PUSH_DATA for %.0fs — data is stale, forcing reconnect",
                            elapsed,
                        )
                        await self._ws.close()
                        break
            except Exception:
                break

    async def _listen(self) -> None:
        """Listen for messages on the WebSocket."""
        loop = asyncio.get_running_loop()
        ssl_ctx = await loop.run_in_executor(None, ssl.create_default_context)

        while self._running:
            try:
                # Refresh token before each connection attempt
                if not await self._ensure_token():
                    _LOGGER.error("Cannot obtain SolaX token, retrying in %ds", self._reconnect_delay)
                    await asyncio.sleep(self._reconnect_delay)
                    self._reconnect_delay = min(self._reconnect_delay * 2, MAX_RECONNECT_DELAY)
                    continue

                url = self._build_url()
                _LOGGER.info("Connecting to SolaX Zeus WebSocket at %s", self._ws_host)

                # Enable live data stream before connecting WebSocket
                await self._enable_live_data()

                async with websockets.connect(
                    url,
                    ssl=ssl_ctx,
                    additional_headers={"Origin": f"https://{self._ws_host}"},
                    open_timeout=15,
                    ping_interval=None,
                ) as ws:
                    self._ws = ws
                    self._connected = True
                    self._reconnect_delay = RECONNECT_DELAY
                    _LOGGER.info("Connected to SolaX Zeus WebSocket")

                    # Send start message to subscribe to live data
                    await ws.send(self._build_start_message())
                    _LOGGER.info("Sent start message, waiting for data...")

                    # Reset push data timestamp for this connection
                    self._last_push_data_at = time.time()

                    # Start ping, watchdog, and live-enable loops
                    ping_task = asyncio.create_task(self._ping_loop())
                    watchdog_task = asyncio.create_task(self._watchdog_loop())
                    enable_task = asyncio.create_task(self._live_enable_loop())

                    try:
                        async for raw_msg in ws:
                            if not self._running:
                                break

                            try:
                                msg = json.loads(raw_msg)
                            except json.JSONDecodeError:
                                _LOGGER.debug("Non-JSON message: %s", raw_msg[:100])
                                continue

                            # Skip PONG responses
                            if msg.get("type") == "COMMAND":
                                continue

                            # Process PUSH_DATA
                            if msg.get("type") == "PUSH_DATA":
                                self._last_push_data_at = time.time()
                                data = self._parse_push_data(msg)
                                if data:
                                    self._last_data = data
                                    _LOGGER.debug(
                                        "Live data: siteP=%s acP=%s batP=%s",
                                        data.get("siteP"), data.get("acP"), data.get("batP")
                                    )
                                    for callback in self._callbacks:
                                        try:
                                            callback(data)
                                        except Exception as err:
                                            _LOGGER.error(
                                                "Callback error: %s", err
                                            )
                    finally:
                        ping_task.cancel()
                        watchdog_task.cancel()
                        enable_task.cancel()
                        try:
                            await ping_task
                        except asyncio.CancelledError:
                            pass
                        try:
                            await watchdog_task
                        except asyncio.CancelledError:
                            pass
                        try:
                            await enable_task
                        except asyncio.CancelledError:
                            pass

            except asyncio.CancelledError:
                break
            except Exception as err:
                self._connected = False
                self._ws = None
                if self._running:
                    _LOGGER.warning(
                        "WebSocket disconnected (%s), reconnecting in %ds",
                        err,
                        self._reconnect_delay,
                    )
                    await asyncio.sleep(self._reconnect_delay)
                    self._reconnect_delay = min(
                        self._reconnect_delay * 2, MAX_RECONNECT_DELAY
                    )

        self._connected = False
        self._ws = None

    async def start(self) -> None:
        """Start the WebSocket listener."""
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._listen())

    async def stop(self) -> None:
        """Stop the WebSocket listener."""
        self._running = False
        if self._ws:
            await self._ws.close()
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        self._connected = False
        self._ws = None
