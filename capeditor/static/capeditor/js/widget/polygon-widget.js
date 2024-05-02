function SaveCancelControl() {
}

SaveCancelControl.prototype.onAdd = function (map) {
    this.map = map;
    this._container = document.createElement('div');
    this._container.className = 'mapboxgl-ctrl save-cancel-control';
    this._container.style = 'display: none;';
    this._container.innerHTML = `
            <div class='label'>Editing Geometry</div>
              <div class="actions">
                <button class='mapboxgl-draw-actions-btn mapboxgl-draw-actions-btn_cancel' title="Cancel editing, discards all changes.">
                  Cancel
                </button>
                <button class='mapboxgl-draw-actions-btn mapboxgl-draw-actions-btn_save' title="Save changes.">
                  Save
                </button>
              </div>
          `;

    return this._container;
};

SaveCancelControl.prototype.hide = function () {
    this._container.style = 'display: none;';
};

SaveCancelControl.prototype.show = function () {
    this._container.style = 'display: block;';
};


SaveCancelControl.prototype.onRemove = function (map) {
    this._container.parentNode.removeChild(this._container);
    this.map = undefined;
};

function EditControl() {
}

EditControl.prototype.onAdd = function (map) {
    this.map = map;
    this._container = document.createElement('div');
    this._container.className =
        'mapboxgl-ctrl-group mapboxgl-ctrl edit-control';
    this._container.style = 'display: none;';

    this._container.innerHTML = `
            <button class="mapbox-gl-draw_ctrl-draw-btn mapbox-gl-draw_edit control-icon" title="Edit geometries">
                <svg class="icon" aria-hidden="true">
                    <use href="#icon-edit"></use>
                </svg>
            </button>
          `;
    return this._container;
};

EditControl.prototype.hide = function () {
    this._container.style = 'display: none;';
};

EditControl.prototype.show = function () {
    this._container.style = 'display: block;';
};

EditControl.prototype.onRemove = function (map) {
    this._container.parentNode.removeChild(this._container);
    this.map = undefined;
};


function PolygonWidget(options, initialState) {

    this.geomInput = $('#' + options.id);
    this.options = options

    this.countriesBounds = this.geomInput.data("bounds")

    const id_parts = options.id.split("-area")
    const info_id = id_parts[0]

    this.severityInput = $('#' + info_id + "-severity");
    this.emptyGeojsonData = {type: "Feature", "geometry": {type: "Polygon", coordinates: []}}

    if (this.severityInput) {
        this.severityInput.on("change", (e) => {
            this.onSeverityChange()
        })
    }


    this.initMap().then(() => {
        this.map.resize()

        this.initLayer()
        this.initDraw()

        if (initialState) {
            this.setState(initialState)
            this.initFromState()
        }
    })
}

PolygonWidget.prototype.setState = function (newState) {
    this.geomInput.val(newState);
};

PolygonWidget.prototype.getState = function () {
    return this.geomInput.val();
};

PolygonWidget.prototype.getValue = function () {
    return this.geomInput.val();
};

PolygonWidget.prototype.focus = function () {
}

PolygonWidget.prototype.initMap = async function () {
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

PolygonWidget.prototype.initLayer = function () {
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


PolygonWidget.prototype.initDraw = function () {
    const value = this.getState()
    const hasGeomValue = Boolean(value)

    // remove
    this.clearDraw()

    this.draw = new MapboxDraw({
        displayControlsDefault: false,
        controls: {
            polygon: !hasGeomValue,
            trash: true
        },
    });

    this.editControl = new EditControl();
    this.saveCancelControl = new SaveCancelControl()

    this.map.addControl(this.draw, 'top-left');
    this.map.addControl(this.editControl, 'top-left');
    this.map.addControl(this.saveCancelControl, 'top-left');

    this.hideTrash()

    this.maybeShowEditControl()

    this.map.doubleClickZoom.disable()

    const $geomEdit = $(".mapbox-gl-draw_edit")

    $geomEdit.on("click", (e) => {
        e.preventDefault()

        this.showTrash()

        this.map.setLayoutProperty("polygon", "visibility", "none")

        const source = this.map.getSource("polygon")
        const data = source._data
        data.id = "feature_polygon"
        const featureIds = this.draw.add(data)

        this.draw.changeMode('simple_select', {featureIds});

        this.editControl.hide()
        this.saveCancelControl.show()
    })


    const $geomEditAction = $(".mapboxgl-draw-actions-btn")

    $geomEditAction.on("click", (e) => {
        e.preventDefault()
        const isSaveButton = e.target.classList.contains("mapboxgl-draw-actions-btn_save")
        if (isSaveButton) {

            let combinedFeatures

            const featureCollection = this.draw.getAll()
            if (featureCollection && featureCollection.features && !!featureCollection.features.length) {
                combinedFeatures = turf.combine(featureCollection)
            }

            if (combinedFeatures) {
                const feature = combinedFeatures.features[0]

                this.setDrawData(feature.geometry)
            } else {
                this.setDrawData(null)
            }

        } else {
            this.map.setLayoutProperty("polygon", "visibility", "visible")

            // clean up draw
            this.draw.changeMode('simple_select');
            this.draw.deleteAll();

            this.initDraw()
        }
    })

    this.map.on("draw.create", (e) => {
        let combinedFeatures

        const featureCollection = this.draw.getAll()
        if (featureCollection && featureCollection.features && !!featureCollection.features.length) {
            combinedFeatures = turf.combine(featureCollection)
        }

        if (combinedFeatures) {
            const feature = combinedFeatures.features[0]

            this.setDrawData(feature.geometry)
        }
    });
}


PolygonWidget.prototype.clearDraw = function () {
    if (this.draw) {
        this.map.removeControl(this.draw)
        this.draw = null
    }

    if (this.editControl) {
        this.map.removeControl(this.editControl)
        this.editControl = null
    }

    if (this.saveCancelControl) {
        this.map.removeControl(this.saveCancelControl)
        this.saveCancelControl = null
    }
}


PolygonWidget.prototype.setDrawData = function (featureGeom) {
    if (featureGeom) {

        // truncate geometry
        const geometry = turf.truncate(featureGeom, {
            precision: 2,
            coordinates: 2,
            mutate: true
        })

        const bbox = turf.bbox(geometry)
        const bounds = [[bbox[0], bbox[1]], [bbox[2], bbox[3]]]

        this.setSourceData(geometry)
        this.map.setLayoutProperty("polygon", "visibility", "visible")

        this.map.fitBounds(bounds, {padding: 50})
        const geomString = JSON.stringify(geometry)


        this.setState(geomString)
    } else {
        this.setSourceData(null)
        this.setState("")
    }


    this.initDraw()
    this.maybeShowEditControl()
}


PolygonWidget.prototype.setSourceData = function (data) {
    if (data) {
        this.map.getSource("polygon").setData(data)
    } else {
        this.map.getSource("polygon").setData(this.emptyGeojsonData)
    }
}

PolygonWidget.prototype.initFromState = function () {
    const value = this.getState()

    if (value) {
        const feature = JSON.parse(value)
        this.setDrawData(feature)
    }
}

PolygonWidget.prototype.onSeverityChange = function () {
    const severityColor = this.getSeverityColor()
    if (severityColor) {
        this.map.setPaintProperty("polygon", "fill-color", severityColor)
    }
}


PolygonWidget.prototype.getSeverityColor = function () {
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


PolygonWidget.prototype.hideTrash = function () {
    if (this.draw) {
        const drawPolygon = $(".mapbox-gl-draw_trash")
        if (!!drawPolygon.length) {
            drawPolygon.hide()
        }
    }
}

PolygonWidget.prototype.showTrash = function () {
    if (this.draw) {
        const drawPolygon = $(".mapbox-gl-draw_trash")
        if (!!drawPolygon.length) {
            drawPolygon.show()
        }
    }
}

PolygonWidget.prototype.maybeShowEditControl = function () {
    const source = this.map.getSource("polygon")
    const data = source && source._data

    if (data && data.coordinates && !!data.coordinates.length && this.editControl) {
        this.editControl.show()
    }
}