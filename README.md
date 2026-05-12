# SolaX Zeus Live

[![HACS][hacs-badge]][hacs-url]
[![GitHub Release][release-badge]][release-url]
[![License][license-badge]][license-url]

**10-second real-time data** from SolaX inverters via the SolaX Cloud Zeus WebSocket API for [Home Assistant](https://www.home-assistant.io/).

## Why?

The standard SolaX Cloud API only updates every ~5 minutes. The SolaX Zeus API (used internally by the SolaX Cloud web app) pushes data **every 10 seconds** via WebSocket — giving you true real-time monitoring of solar production, battery state, grid power, and house consumption.

Works with any SolaX inverter connected to SolaX Cloud (including via XHub gateway).

## Features

- ⚡ **10-second real-time updates** via WebSocket push (no polling)
- 🔐 **Auto-login** — just enter your SolaX Cloud email & password
- 🔍 **Auto-detection** — inverter serial, gateway serial, site ID all discovered automatically
- 🔄 **Self-healing** — auto-reconnect with exponential backoff, stale data watchdog
- 📊 **27 sensors** — grid power, PV, battery, voltages, currents, frequencies, MPPT strings
- 🏠 **House consumption** — calculated template sensor included

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click the three dots menu → **Custom repositories**
3. Add `https://github.com/dkalinai/homeassistant-solax-zeus-live` as **Integration**
4. Search for "SolaX Zeus Live" and install
5. Restart Home Assistant

### Manual

1. Copy the `custom_components/solax_zeus_live` folder to your Home Assistant `config/custom_components/` directory
2. Restart Home Assistant

## Configuration

1. Go to **Settings → Devices & Services → Add Integration**
2. Search for **SolaX Zeus Live**
3. Enter your **SolaX Cloud email** and **password**
4. Everything else is detected automatically ✨

That's it! Your inverter, gateway, and site are discovered from your SolaX Cloud account.

## Sensors

### Primary (enabled by default)

| Sensor | Code | Unit | Description |
|--------|------|------|-------------|
| Grid Power | `siteP` | W | Power flow at the grid meter. Positive = exporting, negative = importing |
| Inverter AC Power | `acP` | W | Inverter output power |
| PV Power | `pvP` | W | Total solar production |
| Battery Power | `batP` | W | Positive = discharging, negative = charging |
| Battery SOC | `soc` | % | State of charge |

### Additional (disabled by default)

Grid/AC voltages (L1/L2/L3), currents, frequency, reactive power, apparent power, EPS power, and individual MPPT string power (up to 4 strings).

## House Consumption Template

Add this to your `templates.yaml` for a calculated house consumption sensor:

```yaml
- sensor:
    - name: "Zeus House Consumption"
      unique_id: zeus_house_consumption
      unit_of_measurement: "W"
      device_class: power
      state_class: measurement
      icon: mdi:home-lightning-bolt
      state: >
        {% set pv = states('sensor.solax_inverter_YOURSN_pv_power') | float(0) %}
        {% set bat = states('sensor.solax_inverter_YOURSN_battery_power') | float(0) %}
        {% set grid = states('sensor.solax_inverter_YOURSN_grid_power') | float(0) %}
        {{ (pv + bat - grid) | round(0) }}
```

Replace `YOURSN` with your inverter serial number.

## How It Works

This integration uses SolaX Cloud's internal **Zeus API** — the same real-time backend that powers the SolaX Cloud web app's live view. It:

1. Logs in with your SolaX Cloud credentials
2. Calls `liveDataEnable` to activate the real-time stream from your gateway
3. Opens a WebSocket connection for push-based data delivery
4. Periodically re-enables the stream and monitors for stale data

No browser needs to be open. The integration runs fully autonomously on your Home Assistant instance.

## Requirements

- A SolaX inverter connected to SolaX Cloud (via WiFi dongle, LAN dongle, or XHub gateway)
- A SolaX Cloud account (the same one you use at [solaxcloud.com](https://www.solaxcloud.com))

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Invalid credentials" | Verify your email/password at [solaxcloud.com](https://www.solaxcloud.com) |
| "No inverters found" | Make sure your inverter is online in SolaX Cloud |
| Data stops updating | The watchdog should auto-recover within 60s. Check logs for DNS issues. |
| Connection shows "Stale" | Integration detected no data for 60s and is reconnecting |

## License

[Apache License 2.0](LICENSE)

[hacs-badge]: https://img.shields.io/badge/HACS-Custom-41BDF5.svg
[hacs-url]: https://github.com/hacs/integration
[release-badge]: https://img.shields.io/github/v/release/dkalinai/homeassistant-solax-zeus-live
[release-url]: https://github.com/dkalinai/homeassistant-solax-zeus-live/releases
[license-badge]: https://img.shields.io/github/license/dkalinai/homeassistant-solax-zeus-live
[license-url]: https://github.com/dkalinai/homeassistant-solax-zeus-live/blob/main/LICENSE
