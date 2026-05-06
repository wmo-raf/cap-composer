from django.utils.translation import gettext_lazy as _

CATEGORY_TYPES = (
    _('Geo'),
    _('Met'),
    _('Safety'),
    _('Security'),
    _('Rescue'),
    _('Fire'),
    _('Health'),
    _('Env'),
    _('Transport'),
    _('Infra'),
    _('CBRNE'),
    _('Other'),
)

URGENCY_TYPES = (
    _('Immediate'),
    _('Expected'),
    _('Future'),
    _('Past'),
    # ('Unknown') Not recommended
)

SEVERITY_TYPES = (
    _('Extreme'),
    _('Severe'),
    _('Moderate'),
    _('Minor'),
    # ('Unknown', _("Unknown - Severity unknown")),  Not recommended
)

CERTAINTY_TYPES = (
    _('Observed'),
    _('Likely'),
    _('Possible'),
    _('Unlikely', ),
    # ('Unknown', _("Unknown - Certainty unknown")),  Not recommended
)

RESPONSE_TYPES = (
    _("Shelter"),
    _("Evacuate"),
    _("Prepare"),
    _("Execute"),
    _("Avoid", ),
    _("Monitor"),
    _("Assess"),
    _("AllClear"),
    _("None"),
)

# wmo event types list per Cg-18
WMO_HAZARD_EVENTS_TYPE_CHOICES = (
    ("Avalanche", _("Avalanche")),
    ("Cold wave", _("Cold wave")),
    ("Drought/Dry spell", _("Drought/Dry spell")),
    ("Dust storm/Sandstorm", _("Dust storm/Sandstorm")),
    ("Extra-tropical cyclone", _("Extra-tropical cyclone")),
    ("Flood", _("Flood")),
    ("Fog", _("Fog")),
    ("Haze/Smoke", _("Haze/Smoke")),
    ("Frost", _("Frost")),
    ("Hail", _("Hail")),
    ("Heat wave", _("Heat wave")),
    ("High UV radiation", _("High UV radiation")),
    ("Icing", _("Icing")),
    ("Freezing rain", _("Freezing rain")),
    ("Landslide/Mudslide & Debris flow", _("Landslide/Mudslide & Debris flow")),
    ("Lightning", _("Lightning")),
    ("Pollen pollution/Polluted air", _("Pollen pollution/Polluted air")),
    ("Rain/Wet Spell", _("Rain/Wet Spell")),
    ("Snow", _("Snow")),
    ("Snowstorm", _("Snowstorm")),
    ("Space weather event", _("Space weather event")),
    ("High Seas/Rogue waves etc.", _("High Seas/Rogue waves etc.")),
    ("Storm surge/Coastal flood", _("Storm surge/Coastal flood")),
    ("Thunderstorms/Squall lines", _("Thunderstorms/Squall lines")),
    ("Tornado", _("Tornado")),
    ("Tropical cyclone", _("Tropical cyclone")),
    ("Tsunami", _("Tsunami")),
    ("Volcanic ash", _("Volcanic ash")),
    ("Wild land fire/Forest fire", _("Wild land fire/Forest fire")),
    ("Wind", _("Wind")),
)

CAP_MESSAGE_ORDER_SEQUENCE = {
    "alert": [
        "identifier",
        "sender",
        "sent",
        "status",
        "msgType",
        "source",
        "scope",
        "restriction",
        "addresses",
        "code",
        "note",
        "references",
        "incidents",
        "info"
    ],
    "info": [
        "language",
        "category",
        "event",
        "responseType",
        "urgency",
        "severity",
        "certainty",
        "audience",
        "eventCode",
        "effective",
        "onset",
        "expires",
        "senderName",
        "headline",
        "description",
        "instruction",
        "web",
        "contact",
        "parameter",
        "resource",
        "area"
    ],
    "resource": [
        "resourceDesc",
        "mimeType",
        "size",
        "uri",
        "derefUri",
        "digest",
    ],
    "area": [
        "areaDesc",
        "polygon",
        "polygons",  # added to support multiple polygons. Not in CAP spec
        "circle",
        "geocode",
        "altitude",
        "ceiling"
    ]
}

SEVERITY_MAPPING = {
    "Extreme": {
        "label": _("Extreme severity"),
        "color": "#d42d41",
        "background_color": "#FEE2E2",
        "border_color": "#DC2626",
        "icon_color": "#DC2626",
        "severity": "Extreme",
        "id": 4
    },
    "Severe": {
        "label": _("Severe severity"),
        "color": "#f08c11",           # burnt orange
        "background_color": "#FDE8D0", # soft peach
        "border_color": "#C2600A",
        "icon_color": "#C2600A",
        "severity": "Severe",
        "id": 3
    },
    "Moderate": {
        "label": _("Moderate severity"),
        "color": "#f4cf00",           # dark amber text
        "background_color": "#FEF08A", # bright yellow bg
        "border_color": "#A16207",
        "icon_color": "#A16207",
        "severity": "Moderate",
        "id": 2
    },
    "Minor": {
        "label": _("Minor severity"),
        "color": "#399cc7",
        "background_color": "#CFFAFE",
        "border_color": "#0E7490",
        "icon_color": "#0E7490",
        "severity": "Minor",
        "id": 1
    },
    "Unknown": {
        "label": _("Unknown severity"),
        "color": "#82a8df",
        "background_color": "#E0E7FF",
        "border_color": "#4B6CB7",
        "icon_color": "#4B6CB7",
        "severity": "Unknown",
        "id": 0
    }
}

URGENCY_MAPPING = {
    "Immediate": {
        "label": _("Immediate"),
        "certainty": "Immediate",
        "id": 4
    },
    "Expected": {
        "label": _("Expected"),
        "certainty": "Expected",
        "id": 3
    },
    "Future": {
        "label": _("Future"),
        "certainty": "Future",
        "id": 2
    },
    "Past": {
        "label": _("Past"),
        "certainty": "Past",
        "id": 1
    },
    "Unknown": {
        "label": _("Unknown"),
        "certainty": "Unknown",
        "id": 0
    },
}

CERTAINTY_MAPPING = {
    "Observed": {
        "label": _("Observed"),
        "certainty": "Observed",
        "id": 4
    },
    "Likely": {
        "label": _("Likely"),
        "certainty": "Likely",
        "id": 3
    },
    "Possible": {
        "label": _("Possible"),
        "certainty": "Possible",
        "id": 2
    },
    "Unlikely": {
        "label": _("Unlikely"),
        "certainty": "Unlikely",
        "id": 1
    },
    "Unknown": {
        "label": _("Unknown"),
        "certainty": "Unknown",
        "id": 0
    },
}

OET_VERSION_NAME = "OET:v1.2"
