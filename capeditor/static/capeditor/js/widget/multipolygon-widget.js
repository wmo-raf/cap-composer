class MultiPolygonWidget {
    constructor(options) {
        this.map = null;
        this.ready = false;

        this.options = options
        this.geomInput = document.getElementById(this.options.id)


        if (this.options.resize_trigger_selector) {
            this.resizeTriggerEls = document.querySelectorAll(this.options.resize_trigger_selector)
        }

        this.initialValue = this.geomInput.value
        this.countriesBounds = this.geomInput.dataset.bounds ? JSON.parse(this.geomInput.dataset.bounds) : null


        let UNGeojsonBoundaryGeojson = this.geomInput.dataset.unGeojson ? JSON.parse(this.geomInput.dataset.unGeojson) : null

        if (UNGeojsonBoundaryGeojson) {
            this.UNGeojsonBoundaryGeojson = UNGeojsonBoundaryGeojson
        }

        this.createMap().then((map) => {
            this.map = map;
            this.fitBounds()

            if (this.resizeTriggerEls && this.resizeTriggerEls.length > 0) {
                for (let i = 0; i < this.resizeTriggerEls.length; i++) {
                    const el = this.resizeTriggerEls[i];
                    el.addEventListener('click', () => {
                        this.fitBounds()
                    })
                }
            }

            this.initDraw();


            if (this.UNGeojsonBoundaryGeojson) {
                this.addUNBoundaryLayer()
            }
        });

    }


    async createMap() {
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
        const map = new maplibregl.Map({
            container: this.options.map_id, style: defaultStyle, doubleClickZoom: false, scrollZoom: false,
        });


        map.addControl(new maplibregl.NavigationControl({
            showCompass: false,
        }), "bottom-right");

        map.addControl(new maplibregl.FullscreenControl());

        await new Promise((resolve) => map.on("load", resolve));

        return map;
    }

    fitBounds() {
        if (this.map) {
            this.map.resize()
            if (!window.document.fullscreenElement) {
                if (this.initialValue) {
                    const feature = JSON.parse(this.initialValue)
                    const bounds = turf.bbox(feature)
                    this.map.fitBounds([[bounds[0], bounds[1]], [bounds[2], bounds[3]]], {padding: 20})
                } else {
                    if (this.countriesBounds) {
                        const bounds = [[this.countriesBounds[0], this.countriesBounds[1]], [this.countriesBounds[2], this.countriesBounds[3]]]
                        this.map.fitBounds(bounds, {padding: 20})
                    }
                }
            }
        }
    }


    getValue() {

        if (!this.geomInput.value) {
            return null;
        }

        const geom = JSON.parse(this.geomInput.value);

        return {
            type: 'Feature', geometry: geom,
        };
    }

    setValue(feature) {
        this.geomInput.value = feature;
    }

    initDraw() {
        const feature = this.getValue()
        this.draw = new MapboxDraw({
            displayControlsDefault: false, controls: {
                polygon: true, trash: true
            },
        });
        this.map.addControl(this.draw, 'top-left');

        if (feature) {
            this.draw.add(feature);
            this.updateArea()
        }


        this.map.on("draw.create", this.updateArea);
        this.map.on("draw.delete", this.updateArea);
        this.map.on("draw.update", this.updateArea);
        this.map.on("draw.combine", this.updateArea);
        this.map.on("draw.uncombine", this.updateArea);


    }


    getDrawFeatures() {
        let combinedFeatures

        const featureCollection = this.draw.getAll()
        if (featureCollection && featureCollection.features && !!featureCollection.features.length) {
            combinedFeatures = turf.combine(featureCollection)
        }
        return combinedFeatures
    }

    updateArea = () => {
        const drawnFeatures = this.getDrawFeatures()
        if (drawnFeatures) {
            const feature = drawnFeatures.features[0]

            const truncatedFeature = turf.truncate(feature, {
                precision: 6, coordinates: 2, mutate: true
            })

            this.setValue(JSON.stringify(truncatedFeature.geometry))

            // clear any map error
            this.hideWarnings()

            // check if the drawn feature has any issues with the UN boundary
            this.checkUNBoundaryIssues(truncatedFeature.geometry)

        } else {
            this.setValue("")
        }
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

    checkUNBoundaryIssues(featureGeom) {
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

    snapToUNBoundary() {
        const drawnFeatures = this.getDrawFeatures()


        if (drawnFeatures && drawnFeatures.features && drawnFeatures.features.length) {
            const feature = drawnFeatures.features[0]


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

                this.draw.deleteAll()
                this.draw.add(snappedFeature)

                this.updateArea()

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

    clearMapErrors() {
        this.map.getContainer().querySelectorAll(".map-error").forEach((el) => {
            el.remove()
        })
    }
}
