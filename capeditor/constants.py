# wmo event types list per Cg-18
WMO_HAZARD_EVENTS_TYPE_CHOICES = (
    ("Avalanche", "Avalanche"),
    ("Cold wave", "Cold wave"),
    ("Drought/Dry spell", "Drought/Dry spell"),
    ("Dust storm/Sandstorm", "Dust storm/Sandstorm"),
    ("Extra-tropical cyclone", "Extra-tropical cyclone"),
    ("Flood", "Flood"),
    ("Fog", "Fog"),
    ("Haze/Smoke", "Haze/Smoke"),
    ("Frost", "Frost"),
    ("Hail", "Hail"),
    ("Heat wave", "Heat wave"),
    ("High UV radiation", "High UV radiation"),
    ("Icing", "Icing"),
    ("Freezing rain", "Freezing rain"),
    ("Landslide/Mudslide & Debris flow", "Landslide/Mudslide & Debris flow"),
    ("Lighting", "Lighting"),
    ("Pollen pollution/Polluted air", "Pollen pollution/Polluted air"),
    ("Rain/Wet Spell", "Rain/Wet Spell"),
    ("Snow", "Snow"),
    ("Snowstorm", "Snowstorm"),
    ("Space weather event", "Space weather event"),
    ("High Seas/Rogue waves etc.", "High Seas/Rogue waves etc."),
    ("Storm surge/Coastal flood", "Storm surge/Coastal flood"),
    ("Thunderstorms/Squall lines", "Thunderstorms/Squall lines"),
    ("Tornado", "Tornado"),
    ("Tropical cyclone", "Tropical cyclone"),
    ("Tsunami", "Tsunami"),
    ("Volcanic ash", "Volcanic ash"),
    ("Wild land fire/Forest fire", "Wild land fire/Forest fire"),
    ("Wind", "Wind"),
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
        "label": "Red severity",
        "color": "#d72f2a",
        "background_color": "#fcf2f2",
        "border_color": "#721515",
        "icon_color": "#fff",
        "severity": "Extreme",
        "id": 4
    },
    "Severe": {
        "label": "Orange severity",
        "color": "#fe9900",
        "background_color": "#fff9f2",
        "border_color": "#9a6100",
        "severity": "Severe",
        "id": 3
    },
    "Moderate": {
        "label": "Yellow severity",
        "color": "#ffff00",
        "background_color": "#fffdf1",
        "border_color": "#938616",
        "severity": "Moderate",
        "id": 2
    },
    "Minor": {
        "label": "Minor severity",
        "color": "#03ffff",
        "background_color": "#fffdf1",
        "border_color": "#938616",
        "severity": "Minor",
        "id": 1
    },
    "Unknown": {
        "label": "Unknown severity",
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
        "label": "Immediate",
        "certainty": "Immediate",
        "id": 4
    },
    "Expected": {
        "label": "Expected",
        "certainty": "Expected",
        "id": 3
    },
    "Future": {
        "label": "Future",
        "certainty": "Future",
        "id": 2
    },
    "Past": {
        "label": "Past",
        "certainty": "Past",
        "id": 1
    },
    "Unknown": {
        "label": "Unknown",
        "certainty": "Unknown",
        "id": 0
    },
}

CERTAINTY_MAPPING = {
    "Observed": {
        "label": "Observed",
        "certainty": "Observed",
        "id": 4
    },
    "Likely": {
        "label": "Likely",
        "certainty": "Likely",
        "id": 3
    },
    "Possible": {
        "label": "Possible",
        "certainty": "Possible",
        "id": 2
    },
    "Unlikely": {
        "label": "Unlikely",
        "certainty": "Unlikely",
        "id": 1
    },
    "Unknown": {
        "label": "Unknown",
        "certainty": "Unknown",
        "id": 0
    },
}
