function BoundaryPolygonWidget(options, initialState) {
    this.geomInput = $('#' + options.id);
    this.options = options

    this.boundaryTilesUrl = this.geomInput.data("boundarytilesurl")
    this.boundaryDetailUrl = this.geomInput.data("boundarydetailurl")
    this.countriesBounds = this.geomInput.data("bounds")

    // Admin level selector
    const adminLevelInputId = options.id.replace("boundary", "admin_level")
    this.adminLevelSelector = $('#' + adminLevelInputId);
    if (this.adminLevelSelector) {
        this.adminLevelSelector.on("change", (e) => {
            this.onAdminLevelSelectorChange()
        })
    }

    // area description input selector
    const areaDescInputId = options.id.replace("boundary", "areaDesc")
    this.areaDescInput = $('#' + areaDescInputId);

    const id_parts = options.id.split("-area")
    const info_id = id_parts[0]

    const severityInputId = `#${info_id}-severity`

    this.severityInput = $(severityInputId);

    this.emptyGeojsonData = {type: "Feature", "geometry": {type: "Polygon", coordinates: []}}

    if (this.severityInput) {
        this.severityInput.on("change", (e) => {
            this.onSeverityChange()
        })
    }

    this.initMap().then(() => {
        this.map.resize()

        this.initLayer()
        this.addAdminBoundaryLayer()


        if (initialState) {
            this.setState(initialState)
            this.initFromState()
        }
    })
}

BoundaryPolygonWidget.prototype.setState = function (newState) {
    this.geomInput.val(newState);
};

BoundaryPolygonWidget.prototype.getState = function () {
    return this.geomInput.val();
};

BoundaryPolygonWidget.prototype.getValue = function () {
    return this.geomInput.val();
};

BoundaryPolygonWidget.prototype.focus = function () {
}

BoundaryPolygonWidget.prototype.initMap = async function () {
    const defaultStyle = {
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

    // initialize map
    this.map = new maplibregl.Map({
        container: this.options.map_id,
        style: defaultStyle,
        doubleClickZoom: false,
        scrollZoom: false,
    });


    this.map.addControl(
        new maplibregl.NavigationControl({
            showCompass: false,
        }), "bottom-right"
    );

    this.map.addControl(new maplibregl.FullscreenControl());

    await new Promise((resolve) => this.map.on("load", resolve));


    if (this.countriesBounds) {
        const bounds = [[this.countriesBounds[0], this.countriesBounds[1]], [this.countriesBounds[2], this.countriesBounds[3]]]
        this.map.fitBounds(bounds)
    }

}

BoundaryPolygonWidget.prototype.initLayer = function () {
    const severityColor = this.getSeverityColor()

    // add source
    this.map.addSource("polygon", {
            'type': 'geojson',
            data: this.emptyGeojsonData
        }
    )

    // add layer
    this.map.addLayer({
        'id': 'polygon',
        'type': 'fill',
        'source': 'polygon',
        'layout': {},
        'paint': {
            'fill-color': severityColor,
            'fill-opacity': 0.8,
            "fill-outline-color": "#000",
        }
    });
}


BoundaryPolygonWidget.prototype.setSourceData = function (feature) {
    if (feature) {

        // add data to source
        this.map.getSource("polygon").setData(feature)

        // fit map to bounds
        const bbox = turf.bbox(feature)
        const bounds = [[bbox[0], bbox[1]], [bbox[2], bbox[3]]]
        this.map.fitBounds(bounds, {padding: 50})

        // set state
        const geomString = JSON.stringify(feature)
        this.setState(geomString)
    } else {

        // clear source data
        this.map.getSource("polygon").setData(this.emptyGeojsonData)

        // clear area desctiption
        this.areaDescInput.val("")

        // set state to empty string
        this.setState("")
    }
}

BoundaryPolygonWidget.prototype.initFromState = function () {
    const value = this.getState()

    if (value) {
        const feature = JSON.parse(value)
        this.setSourceData(feature)
    }
}

BoundaryPolygonWidget.prototype.onSeverityChange = function () {
    const severityColor = this.getSeverityColor()
    if (severityColor) {
        this.map.setPaintProperty("polygon", "fill-color", severityColor)
    }
}

BoundaryPolygonWidget.prototype.onAdminLevelSelectorChange = function () {

    this.setSourceData(null)

    const selectedAdminLevel = this.getSelectedAdminLevel()
    const adminFilter = ["==", "level", Number(selectedAdminLevel)]

    const hasSource = this.map.getSource("admin-boundary-source")

    if (hasSource) {
        this.map.setFilter("admin-boundary-fill", adminFilter)
        this.map.setFilter("admin-boundary-line", adminFilter)
    }

}

BoundaryPolygonWidget.prototype.getSeverityColor = function () {
    const severity = this.severityInput.val()
    switch (severity) {
        case "Extreme":
            return "#d72f2a"
        case "Severe":
            return "#fe9900"
        case "Moderate":
            return "#ffff00"
        case "Minor":
            return "#03ffff"
        default:
            return "#3366ff"
    }
}


BoundaryPolygonWidget.prototype.getSelectedAdminLevel = function () {
    return this.adminLevelSelector.find(":checked").val()
}

BoundaryPolygonWidget.prototype.addAdminBoundaryLayer = function () {
    const selectedAdminLevel = this.getSelectedAdminLevel()
    const adminFilter = ["==", "level", Number(selectedAdminLevel)]

    // add source
    this.map.addSource("admin-boundary-source", {
            type: "vector",
            tiles: [this.boundaryTilesUrl],
        }
    )

    // add layer
    this.map.addLayer({
        'id': 'admin-boundary-fill',
        'type': 'fill',
        'source': 'admin-boundary-source',
        "source-layer": "default",
        "filter": adminFilter,
        'paint': {
            'fill-color': "#fff",
            'fill-opacity': 0,
        }
    });

    this.map.addLayer({
        'id': 'admin-boundary-line',
        'type': 'line',
        'source': 'admin-boundary-source',
        "source-layer": "default",
        "filter": adminFilter,
        'paint': {
            "line-color": "#444444",
            "line-width": 0.7,
        }
    });

    this.map.on('mouseenter', 'admin-boundary-fill', () => {
        this.map.getCanvas().style.cursor = 'pointer'
    })
    this.map.on('mouseleave', 'admin-boundary-fill', () => {
        this.map.getCanvas().style.cursor = ''
    })

    this.map.on('click', 'admin-boundary-fill', (e) => {
        const feat = e.features[0]
        if (feat) {
            const {id} = feat.properties

            if (id) {
                fetch(`${this.boundaryDetailUrl}/${id}`).then(res => res.json()).then(boundary => {
                    const {feature, level} = boundary
                    const name = boundary[`name_${level}`]

                    if (name) {
                        this.areaDescInput.val(name)
                    }

                    const truncatedFeature = turf.truncate(feature, {
                        precision: 2,
                        coordinates: 2,
                        mutate: true
                    })

                    this.setSourceData(truncatedFeature)
                })
            }
        }
    });
}
