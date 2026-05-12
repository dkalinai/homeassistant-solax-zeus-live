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

DEFAULT_WS_HOST = "global.solaxcloud.com"
LOGIN_URL = "https://{host}/proxy/login/login"
LIVE_DATA_ENABLE_URL = "https://{host}/zeus/v1/ts/liveDataEnable"

# Sensor definitions: code -> (name, unit, device_class, state_class, icon)
SENSOR_DEFS = {
    "siteP": ("Grid Power", "W", "power", "measurement", "mdi:transmission-tower"),
    "acP": ("Inverter AC Power", "W", "power", "measurement", "mdi:solar-power-variant"),
    "batP": ("Battery Power", "W", "power", "measurement", "mdi:battery-charging"),
    "pvP": ("PV Power", "W", "power", "measurement", "mdi:solar-panel-large"),
    "soc": ("Battery SOC", "%", "battery", "measurement", "mdi:battery"),
    "acS": ("AC Apparent Power", "VA", "apparent_power", "measurement", None),
    "epsP": ("EPS Power", "VA", "apparent_power", "measurement", "mdi:power-plug-off"),
    "siteUa": ("Grid Voltage L1", "V", "voltage", "measurement", None),
    "siteUb": ("Grid Voltage L2", "V", "voltage", "measurement", None),
    "siteUc": ("Grid Voltage L3", "V", "voltage", "measurement", None),
    "siteIa": ("Grid Current L1", "A", "current", "measurement", None),
    "siteIb": ("Grid Current L2", "A", "current", "measurement", None),
    "siteIc": ("Grid Current L3", "A", "current", "measurement", None),
    "siteQ": ("Grid Reactive Power", "var", "reactive_power", "measurement", None),
    "acUa": ("AC Voltage L1", "V", "voltage", "measurement", None),
    "acUb": ("AC Voltage L2", "V", "voltage", "measurement", None),
    "acUc": ("AC Voltage L3", "V", "voltage", "measurement", None),
    "acIa": ("AC Current L1", "A", "current", "measurement", None),
    "acIb": ("AC Current L2", "A", "current", "measurement", None),
    "acIc": ("AC Current L3", "A", "current", "measurement", None),
    "acFa": ("AC Frequency L1", "Hz", "frequency", "measurement", None),
    "powerdc1": ("MPPT1 Power", "W", "power", "measurement", "mdi:solar-panel"),
    "powerdc2": ("MPPT2 Power", "W", "power", "measurement", "mdi:solar-panel"),
    "powerdc3": ("MPPT3 Power", "W", "power", "measurement", "mdi:solar-panel"),
    "powerdc4": ("MPPT4 Power", "W", "power", "measurement", "mdi:solar-panel"),
    "consumePower": ("Consumption Power", "W", "power", "measurement", "mdi:home-lightning-bolt"),
}

# Primary sensors shown by default (rest are disabled)
PRIMARY_SENSORS = {"siteP", "acP", "batP", "pvP", "soc", "consumePower"}
