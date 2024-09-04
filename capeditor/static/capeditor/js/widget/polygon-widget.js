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
    this._container.className = 'mapboxgl-ctrl-group mapboxgl-ctrl edit-control';
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
    let UNGeojsonBoundaryGeojson = this.geomInput.data("un-geojson")

    if (UNGeojsonBoundaryGeojson) {
        this.UNGeojsonBoundaryGeojson = UNGeojsonBoundaryGeojson
    }

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
        'version': 8, 'sources': {
            'osm': {
                'type': 'raster', 'tiles': ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"]
            }, 'wikimedia': {
                'type': 'raster', 'tiles': ["https://maps.wikimedia.org/osm-intl/{z}/{x}/{y}.png"]
            }
        }, 'layers': [{
            'id': 'osm', 'source': 'osm', 'type': 'raster', 'minzoom': 0, 'maxzoom': 22
        }]
    }

    // initialize map
    this.map = new maplibregl.Map({
        container: this.options.map_id, style: defaultStyle, doubleClickZoom: false, scrollZoom: false,
    });


    this.map.addControl(new maplibregl.NavigationControl({
        showCompass: false,
    }), "bottom-right");

    this.map.addControl(new maplibregl.FullscreenControl());

    await new Promise((resolve) => this.map.on("load", resolve));

    if (this.countriesBounds) {
        const bounds = [[this.countriesBounds[0], this.countriesBounds[1]], [this.countriesBounds[2], this.countriesBounds[3]]]
        this.map.fitBounds(bounds)
    }

    if (this.UNGeojsonBoundaryGeojson) {
        this.addUNBoundaryLayer()
    }
}

PolygonWidget.prototype.addUNBoundaryLayer = function () {
    this.map.addSource("un-boundary", {
        'type': 'geojson', data: this.UNGeojsonBoundaryGeojson
    })

    this.map.addLayer({
        'id': 'un-boundary', 'type': 'line', 'source': 'un-boundary', 'layout': {}, 'paint': {
            'line-color': '#000', 'line-width': 2,
        }
    });
    this.map.addLayer({
        'id': 'un-boundary-outline', 'type': 'line', 'source': 'un-boundary', 'layout': {}, 'paint': {
            'line-color': '#5b92e5', 'line-width': 1,
        }
    });
}

PolygonWidget.prototype.initLayer = function () {
    const severityColor = this.getSeverityColor()

    // add source
    this.map.addSource("polygon", {
        'type': 'geojson', data: this.emptyGeojsonData
    })

    // add layer
    this.map.addLayer({
        'id': 'polygon', 'type': 'fill', 'source': 'polygon', 'layout': {}, 'paint': {
            'fill-color': severityColor, 'fill-opacity': 0.8, "fill-outline-color": "#000",
        }
    });
}


PolygonWidget.prototype.initDraw = function () {
    const value = this.getState()
    const hasGeomValue = Boolean(value)

    // remove
    this.clearDraw()

    this.draw = new MapboxDraw({
        displayControlsDefault: false, controls: {
            polygon: !hasGeomValue, trash: true
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

        // clear any map error
        this.clearMapErrors()

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

            const source = this.map.getSource("polygon")
            const data = source._data
            this.setDrawData(data)

            // clean up draw
            this.draw.changeMode('simple_select');
            this.draw.deleteAll();

            this.initDraw()
        }
    })

    this.map.on("draw.create", (e) => {
        let combinedFeatures

        // combine all features into one multi polygon
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

PolygonWidget.prototype.clearMapErrors = function () {
    this.map.getContainer().querySelectorAll(".map-error").forEach((el) => {
        el.remove()
    })
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
        // truncate geometry to 6 decimal places
        const geometry = turf.truncate(featureGeom, {
            precision: 6, coordinates: 2, mutate: true
        })

        const bbox = turf.bbox(geometry)
        const bounds = [[bbox[0], bbox[1]], [bbox[2], bbox[3]]]

        this.setSourceData(geometry)
        this.map.setLayoutProperty("polygon", "visibility", "visible")

        this.map.fitBounds(bounds, {padding: 50})
        const geomString = JSON.stringify(geometry)

        this.setState(geomString)

        // clear any map error
        this.hideWarnings()

        // check if the drawn feature has any issues with the UN boundary
        this.checkUNBoundaryIssues(featureGeom)

    } else {
        this.setSourceData(null)
        this.setState("")
    }

    this.initDraw()
    this.maybeShowEditControl()
}


PolygonWidget.prototype.checkUNBoundaryIssues = function (featureGeom) {
    if (this.UNGeojsonBoundaryGeojson && featureGeom) {
        const drawnFeature = turf.feature(featureGeom)
        const UNBoundaryFeature = turf.feature(this.UNGeojsonBoundaryGeojson)

        // First check if the drawn feature intersects with the UN boundary
        const intersects = turf.booleanIntersects(drawnFeature, UNBoundaryFeature);
        if (!intersects) {
            const message = `The drawn area does not intersect with the country UN boundary. 
            This might prevent the alert from being picked by other tools like SWIC`
            this.showWarning(message)
            return
        }


        for (let i = 0; i < drawnFeature.geometry.coordinates.length; i++) {
            const polygon = turf.polygon(drawnFeature.geometry.coordinates[i])

            // check if the UN boundary contains the drawn feature
            const isWithin = turf.booleanWithin(polygon, UNBoundaryFeature);


            if (!isWithin) {
                const message = `The drawn area is not contained within the country UN boundary.
                This might prevent the alert from being picked by other tools like SWIC`
                this.showWarning(message, {showSnapButton: true})
                return;
            }
        }
    }
}


PolygonWidget.prototype.showWarning = function (message, options) {
    const notificationEl = this.createWarningNotificationEl(message, options)
    const mapContainer = this.map.getContainer()
    mapContainer.appendChild(notificationEl)
}

PolygonWidget.prototype.hideWarnings = function () {
    const mapContainer = this.map.getContainer()
    mapContainer.querySelectorAll(".map-error").forEach((el) => {
        el.remove()
    })
}

PolygonWidget.prototype.createWarningNotificationEl = function (message, options) {
    const el = document.createElement("div")
    el.className = "notification is-warning map-error"
    el.innerHTML = `
        <div class="notification-content">
            <span class="icon">
              <svg class="icon icon-warning messages-icon" aria-hidden="true">
                <use href="#icon-warning"></use>
               </svg>
            </span>
            <span class="message">${message}</span>
        </div>
    `

    if (options && options.showSnapButton) {
        const snapButton = document.createElement("button")
        snapButton.className = "button button-small snap-to-boundary"
        snapButton.textContent = "Snap to boundary"
        el.appendChild(snapButton)

        snapButton.onclick = (e) => {
            e.preventDefault()
            this.snapToUNBoundary()
        }
    }


    return el
}

PolygonWidget.prototype.snapToUNBoundary = function () {
    const source = this.map.getSource("polygon")
    const data = source._data

    if (data && data.coordinates && !!data.coordinates.length) {
        const feature = turf.feature(data)
        const UNBoundaryFeature = turf.feature(this.UNGeojsonBoundaryGeojson)

        let snappedFeature = turf.intersect(turf.featureCollection([feature, UNBoundaryFeature]))

        if (snappedFeature) {
            // buffer the snapped feature by a small amount to prevent booleanWithin failing
            snappedFeature = turf.buffer(snappedFeature, -0.0001)

            // convert to multipolygon
            if (snappedFeature.geometry.type === "Polygon") {
                snappedFeature.geometry = {
                    type: "MultiPolygon", coordinates: [snappedFeature.geometry.coordinates]
                }
            }

            this.setDrawData(snappedFeature.geometry)
        }
    }
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