class BoundaryPolygonWidget {
    constructor(options, initialState) {
        this.geomInput = $('#' + options.id);
        this.options = options

        this.boundaryTilesUrl = this.geomInput.data("boundarytilesurl")
        this.boundaryDetailUrl = this.geomInput.data("boundarydetailurl")
        this.countriesBounds = this.geomInput.data("bounds")

        let UNGeojsonBoundaryGeojson = this.geomInput.data("un-geojson")

        if (UNGeojsonBoundaryGeojson) {
            this.UNGeojsonBoundaryGeojson = UNGeojsonBoundaryGeojson
        }

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

            if (this.UNGeojsonBoundaryGeojson) {
                this.addUNBoundaryLayer()
            }


            if (initialState) {
                this.setState(initialState)
                this.initFromState()
            }
        })
    }

    setState(newState) {
        this.geomInput.val(newState);
    };

    getState() {
        return this.geomInput.val();
    };

    getValue() {
        return this.geomInput.val();
    };

    focus() {
    }

    async initMap() {
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

    }

    initLayer() {
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

    setSourceData(featureGeom) {
        if (featureGeom) {
            // add data to source
            this.map.getSource("polygon").setData(featureGeom)

            // fit map to bounds
            const bbox = turf.bbox(featureGeom)
            const bounds = [[bbox[0], bbox[1]], [bbox[2], bbox[3]]]
            this.map.fitBounds(bounds, {padding: 50})

            // set state
            const geomString = JSON.stringify(featureGeom)
            this.setState(geomString)
            // clear any map error
            this.hideWarnings()

            // check if the drawn feature has any issues with the UN boundary
            this.checkUNBoundaryIssues(featureGeom)


        } else {

            // clear source data
            this.map.getSource("polygon").setData(this.emptyGeojsonData)

            // clear area desctiption
            this.areaDescInput.val("")

            // set state to empty string
            this.setState("")
        }
    }

    initFromState() {
        const value = this.getState()

        if (value) {
            const feature = JSON.parse(value)
            this.setSourceData(feature)
        }
    }

    onSeverityChange() {
        const severityColor = this.getSeverityColor()
        if (severityColor) {
            this.map.setPaintProperty("polygon", "fill-color", severityColor)
        }
    }

    onAdminLevelSelectorChange() {
        this.setSourceData(null)
        const selectedAdminLevel = this.getSelectedAdminLevel()
        const adminFilter = ["==", "level", Number(selectedAdminLevel)]
        const hasSource = this.map.getSource("admin-boundary-source")

        if (hasSource) {
            this.map.setFilter("admin-boundary-fill", adminFilter)
            this.map.setFilter("admin-boundary-line", adminFilter)
        }
    }

    getSeverityColor() {
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

    getSelectedAdminLevel() {
        return this.adminLevelSelector.find(":checked").val()
    }

    addAdminBoundaryLayer() {
        const selectedAdminLevel = this.getSelectedAdminLevel()
        const adminFilter = ["==", "level", Number(selectedAdminLevel)]

        // add source
        this.map.addSource("admin-boundary-source", {
            type: "vector", tiles: [this.boundaryTilesUrl],
        })

        // add layer
        this.map.addLayer({
            'id': 'admin-boundary-fill',
            'type': 'fill',
            'source': 'admin-boundary-source',
            "source-layer": "default",
            "filter": adminFilter,
            'paint': {
                'fill-color': "#fff", 'fill-opacity': 0,
            }
        });

        this.map.addLayer({
            'id': 'admin-boundary-line',
            'type': 'line',
            'source': 'admin-boundary-source',
            "source-layer": "default",
            "filter": adminFilter,
            'paint': {
                "line-color": "#444444", "line-width": 0.7,
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
                            precision: 6, coordinates: 2, mutate: true
                        })

                        this.setSourceData(truncatedFeature)
                    })
                }
            }
        });
    }

    addUNBoundaryLayer() {
        this.map.addSource("un-boundary", {
            type: 'geojson', data: this.UNGeojsonBoundaryGeojson
        })

        this.map.addLayer({
            id: 'un-boundary', source: 'un-boundary', type: 'line', paint: {
                "line-color": "#C0FF24", "line-width": 1, "line-offset": 1,
            }
        });

        this.map.addLayer({
            id: "un-boundary-2", source: 'un-boundary', type: 'line', paint: {
                "line-color": "#000", "line-width": 1.5,
            }
        });

        this.addUNBoundaryLayerLegend()
    }

    addUNBoundaryLayerLegend() {
        const legendEl = document.createElement("div")
        legendEl.className = "un-map-legend"
        legendEl.innerHTML = `
        <div class="legend-item">
            <div class="legend-item-colors">
                <div class="legend-item-color" style="background-color: #C0FF24;height: 2px"></div>
                <div class="legend-item-color" style="background-color: #000;height: 3px"></div>
            </div>
            <div class="legend-item-text">UN Boundary</div>
        </div>
    `
        const mapContainer = this.map.getContainer()
        mapContainer.appendChild(legendEl)
    }

    snapToUNBoundary() {
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

                this.setSourceData(snappedFeature.geometry)
            }
        }
    }

    createWarningNotificationEl(message, options) {
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

    showWarning(message, options) {
        const notificationEl = this.createWarningNotificationEl(message, options)
        const mapContainer = this.map.getContainer()
        mapContainer.appendChild(notificationEl)
    }

    hideWarnings() {
        const mapContainer = this.map.getContainer()
        mapContainer.querySelectorAll(".map-error").forEach((el) => {
            el.remove()
        })
    }

    checkUNBoundaryIssues(featureGeom) {
        if (this.UNGeojsonBoundaryGeojson && featureGeom) {
            const selectedFeature = turf.feature(featureGeom)
            const UNBoundaryFeature = turf.feature(this.UNGeojsonBoundaryGeojson)

            // First check if the drawn feature intersects with the UN boundary
            const intersects = turf.booleanIntersects(selectedFeature, UNBoundaryFeature);
            if (!intersects) {
                const message = `The drawn area does not intersect with the country UN boundary. 
            This might prevent the alert from being picked by other tools like SWIC`
                this.showWarning(message)
                return
            }

            for (let i = 0; i < selectedFeature.geometry.coordinates.length; i++) {
                const polygon = turf.polygon(selectedFeature.geometry.coordinates[i])

                // check if the UN boundary contains the selected feature
                const isWithin = turf.booleanWithin(polygon, UNBoundaryFeature);

                if (!isWithin) {
                    const message = `The selected area is not completely within the country's UN boundary.
                    This might prevent the alert from being picked by other tools like SWIC`
                    this.showWarning(message, {showSnapButton: true})
                    return;
                }
            }
        }
    }
}



