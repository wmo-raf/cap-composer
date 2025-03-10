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
        "label": _("Red severity"),
        "color": "#d72f2a",
        "background_color": "#fcf2f2",
        "border_color": "#721515",
        "icon_color": "#fff",
        "severity": "Extreme",
        "id": 4
    },
    "Severe": {
        "label": _("Orange severity"),
        "color": "#fe9900",
        "background_color": "#fff9f2",
        "border_color": "#9a6100",
        "severity": "Severe",
        "id": 3
    },
    "Moderate": {
        "label": _("Yellow severity"),
        "color": "#ffff00",
        "background_color": "#fffdf1",
        "border_color": "#938616",
        "severity": "Moderate",
        "id": 2
    },
    "Minor": {
        "label": _("Minor severity"),
        "color": "#03ffff",
        "background_color": "#fffdf1",
        "border_color": "#938616",
        "severity": "Minor",
        "id": 1
    },
    "Unknown": {
        "label": _("Unknown severity"),
        "color": "#3366ff",
        "background_color": "#fffdf1",
        "border_color": "#122663",
        "icon_color": "#fff",
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

