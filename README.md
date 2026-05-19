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
- 📊 **48 sensors** — grid power, PV, battery, voltages, currents, frequencies, MPPT strings, EPS, power quality, and more
- 🏠 **House consumption** — calculated consumption sensor included

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

All 48 sensors are **enabled by default** and grouped by category:

### Primary Power Flows

| Sensor | Code | Unit | Description |
|--------|------|------|-------------|
| Grid Power | `siteP` | W | Power at the grid meter. Positive = exporting, negative = importing |
| PV Power | `pvP` | W | Total solar production |
| Battery Power | `batP` | W | Positive = discharging, negative = charging |
| Battery SOC | `soc` | % | State of charge |
| Inverter AC Power | `acP` | W | Inverter output power |
| Consumption Power | `consumePower` | W | Calculated: PV + Battery − Grid |

### MPPT / DC Power

| Sensor | Code | Unit | Description |
|--------|------|------|-------------|
| MPPT1–4 Power | `powerdc1`–`powerdc4` | W | Individual string power |

### Grid Voltage & Current (L1/L2/L3)

| Sensor | Code | Unit |
|--------|------|------|
| Grid Voltage L1–L3 | `siteUa`/`siteUb`/`siteUc` | V |
| Grid Current L1–L3 | `siteIa`/`siteIb`/`siteIc` | A |

### AC Voltage, Current & Frequency (L1/L2/L3)

| Sensor | Code | Unit |
|--------|------|------|
| AC Voltage L1–L3 | `acUa`/`acUb`/`acUc` | V |
| AC Current L1–L3 | `acIa`/`acIb`/`acIc` | A |
| AC Frequency L1–L3 | `acFa`/`acFb`/`acFc` | Hz |

### Power Quality

| Sensor | Code | Unit |
|--------|------|------|
| Power Factor | `PF` | — |
| AC Apparent Power | `acS` | VA |
| AC Reactive Power (total + L1/L2/L3) | `acQ`/`acQa`/`acQb`/`acQc` | var |

### Grid Reactive & Apparent Power

| Sensor | Code | Unit |
|--------|------|------|
| Grid Reactive Power (total + L1/L2/L3) | `siteQ`/`siteQa`/`siteQb`/`siteQc` | var |
| Grid Apparent Power | `siteS` | VA |

### EPS (Backup Power)

| Sensor | Code | Unit |
|--------|------|------|
| EPS Power | `epsP` | VA |
| EPS Voltage L1–L3 | `epsUa`/`epsUb`/`epsUc` | V |
| EPS Current L1–L3 | `epsIa`/`epsIb`/`epsIc` | A |
| EPS Frequency L1–L3 | `epsFa`/`epsFb`/`epsFc` | Hz |

### Other

| Sensor | Code | Unit | Description |
|--------|------|------|-------------|
| Meter 2 Power | `m2P` | W | Second meter (if installed) |
| Zeus WS Connection | — | — | WebSocket connection status |

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
