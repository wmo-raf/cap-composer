DEFAULT_STYLE = {
    'version': 8,
    'sources': {
        'carto-dark': {
            'type': 'raster',
            'tiles': [
                "https://a.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}@2x.png",
                "https://b.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}@2x.png",
                "https://c.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}@2x.png",
                "https://d.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}@2x.png"
            ]
        },
        'carto-light': {
            'type': 'raster',
            'tiles': [
                "https://a.basemaps.cartocdn.com/light_all/{z}/{x}/{y}@2x.png",
                "https://b.basemaps.cartocdn.com/light_all/{z}/{x}/{y}@2x.png",
                "https://c.basemaps.cartocdn.com/light_all/{z}/{x}/{y}@2x.png",
                "https://d.basemaps.cartocdn.com/light_all/{z}/{x}/{y}@2x.png"
            ]
        },
        'wikimedia': {
            'type': 'raster',
            'tiles': [
                "https://maps.wikimedia.org/osm-intl/{z}/{x}/{y}.png"
            ]
        }
    },
    'layers': [{
        'id': 'carto-light-layer',
        'source': 'carto-light',
        'type': 'raster',
        'minzoom': 0,
        'maxzoom': 22
    }]
}

CAP_LAYERS = [
    {
        "type": "fill",
        "paint": {
            "fill-color": [
                "match",
                ["get", "severity"],
                "Extreme",
                "#d72f2a",
                "Severe",
                "#fe9900",
                "Moderate",
                "#ffff00",
                "Minor",
                "#03ffff",
                "#3366ff",
            ],
            "fill-opacity": 1,
        },
        "filter": [
            "in",
            ["get", "severity"],
            ["literal", ["Extreme", "Severe", "Moderate", "Minor"]],
        ],
    },
    {
        "type": "line",
        "paint": {
            "line-color": [
                "match",
                ["get", "severity"],
                "Extreme",
                "#ac2420",
                "Severe",
                "#ca7a00",
                "Moderate",
                "#cbcb00",
                "Minor",
                "#00cdcd",
                "#003df4",
            ],
            "line-width": 0.1,
        },
        "filter": [
            "in",
            ["get", "severity"],
            ["literal", ["Extreme", "Severe", "Moderate", "Minor"]],
        ],
    },
]
