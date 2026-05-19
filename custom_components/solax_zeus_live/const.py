DOMAIN = "solax_zeus_live"
PLATFORMS = ["sensor"]

CONF_JWT_TOKEN = "jwt_token"
CONF_USER_ID = "user_id"
CONF_INVERTER_SN = "inverter_sn"
CONF_WIFI_SN = "wifi_sn"
CONF_WS_HOST = "ws_host"
CONF_SOLAX_USERNAME = "solax_username"
CONF_SOLAX_PASSWORD = "solax_password"

CONF_SITE_ID = "site_id"
CONF_INVERTER_TYPE = "inverter_type"
CONF_ENTITY_PREFIX = "entity_prefix"

DEFAULT_WS_HOST = "global.solaxcloud.com"
LOGIN_URL = "https://{host}/proxy/login/login"
LIVE_DATA_ENABLE_URL = "https://{host}/zeus/v1/ts/liveDataEnable"

# Sensor definitions: code -> (name, unit, device_class, state_class, icon)
# Ordered by importance — primary power flows first, then details
SENSOR_DEFS = {
    # === Primary power flows ===
    "siteP": ("Grid Power", "W", "power", "measurement", "mdi:transmission-tower"),
    "pvP": ("PV Power", "W", "power", "measurement", "mdi:solar-panel-large"),
    "batP": ("Battery Power", "W", "power", "measurement", "mdi:battery-charging"),
    "soc": ("Battery SOC", "%", "battery", "measurement", "mdi:battery"),
    "acP": ("Inverter AC Power", "W", "power", "measurement", "mdi:solar-power-variant"),
    "consumePower": ("Consumption Power", "W", "power", "measurement", "mdi:home-lightning-bolt"),
    # === MPPT / DC power ===
    "powerdc1": ("MPPT1 Power", "W", "power", "measurement", "mdi:solar-panel"),
    "powerdc2": ("MPPT2 Power", "W", "power", "measurement", "mdi:solar-panel"),
    "powerdc3": ("MPPT3 Power", "W", "power", "measurement", "mdi:solar-panel"),
    "powerdc4": ("MPPT4 Power", "W", "power", "measurement", "mdi:solar-panel"),
    # === Grid voltage / current ===
    "siteUa": ("Grid Voltage L1", "V", "voltage", "measurement", None),
    "siteUb": ("Grid Voltage L2", "V", "voltage", "measurement", None),
    "siteUc": ("Grid Voltage L3", "V", "voltage", "measurement", None),
    "siteIa": ("Grid Current L1", "A", "current", "measurement", None),
    "siteIb": ("Grid Current L2", "A", "current", "measurement", None),
    "siteIc": ("Grid Current L3", "A", "current", "measurement", None),
    # === AC voltage / current / frequency ===
    "acUa": ("AC Voltage L1", "V", "voltage", "measurement", None),
    "acUb": ("AC Voltage L2", "V", "voltage", "measurement", None),
    "acUc": ("AC Voltage L3", "V", "voltage", "measurement", None),
    "acIa": ("AC Current L1", "A", "current", "measurement", None),
    "acIb": ("AC Current L2", "A", "current", "measurement", None),
    "acIc": ("AC Current L3", "A", "current", "measurement", None),
    "acFa": ("AC Frequency L1", "Hz", "frequency", "measurement", None),
    "acFb": ("AC Frequency L2", "Hz", "frequency", "measurement", None),
    "acFc": ("AC Frequency L3", "Hz", "frequency", "measurement", None),
    # === Power quality ===
    "PF": ("Power Factor", None, "power_factor", "measurement", None),
    "acS": ("AC Apparent Power", "VA", "apparent_power", "measurement", None),
    "acQ": ("AC Reactive Power", "var", "reactive_power", "measurement", None),
    "acQa": ("AC Reactive Power L1", "var", "reactive_power", "measurement", None),
    "acQb": ("AC Reactive Power L2", "var", "reactive_power", "measurement", None),
    "acQc": ("AC Reactive Power L3", "var", "reactive_power", "measurement", None),
    # === Grid reactive / apparent ===
    "siteQ": ("Grid Reactive Power", "var", "reactive_power", "measurement", None),
    "siteQa": ("Grid Reactive Power L1", "var", "reactive_power", "measurement", None),
    "siteQb": ("Grid Reactive Power L2", "var", "reactive_power", "measurement", None),
    "siteQc": ("Grid Reactive Power L3", "var", "reactive_power", "measurement", None),
    "siteS": ("Grid Apparent Power", "VA", "apparent_power", "measurement", None),
    # === EPS (backup power) ===
    "epsP": ("EPS Power", "VA", "apparent_power", "measurement", "mdi:power-plug-off"),
    "epsUa": ("EPS Voltage L1", "V", "voltage", "measurement", "mdi:power-plug-battery"),
    "epsUb": ("EPS Voltage L2", "V", "voltage", "measurement", "mdi:power-plug-battery"),
    "epsUc": ("EPS Voltage L3", "V", "voltage", "measurement", "mdi:power-plug-battery"),
    "epsIa": ("EPS Current L1", "A", "current", "measurement", None),
    "epsIb": ("EPS Current L2", "A", "current", "measurement", None),
    "epsIc": ("EPS Current L3", "A", "current", "measurement", None),
    "epsFa": ("EPS Frequency L1", "Hz", "frequency", "measurement", None),
    "epsFb": ("EPS Frequency L2", "Hz", "frequency", "measurement", None),
    "epsFc": ("EPS Frequency L3", "Hz", "frequency", "measurement", None),
    # === Meter 2 ===
    "m2P": ("Meter 2 Power", "W", "power", "measurement", "mdi:transmission-tower"),
}

# All sensors enabled by default
PRIMARY_SENSORS = set(SENSOR_DEFS.keys())
