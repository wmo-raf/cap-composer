function getCsrfToken() {
    const match = document.cookie.match(/csrftoken=([^;]+)/);
    return match ? decodeURIComponent(match[1]) : '';
}


class AreaFileUploadControl {
    constructor(options) {
        this._options = options || {};
    }

    onAdd(map) {
        this.map = map;
        this._container = document.createElement('div');
        this._container.className = 'maplibregl-ctrl maplibregl-ctrl-group file-upload-ctrl';
        this._container.innerHTML = `
            <div class="file-upload-ctrl-icon"></div>
            <div class="file-upload-ctrl-label">Upload file</div>
            <input type="file" accept=".json,.geojson,.zip" style="display:none;">
        `;

        this._container.addEventListener('click', (e) => {
            if (!e.target.closest('input')) {
                this._container.querySelector('input').click();
            }
        });

        this._container.querySelector('input').addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (!file) return;
            const name = file.name.toLowerCase();
            if (name.endsWith('.geojson') || name.endsWith('.json')) {
                this._readGeoJSON(file);
            } else if (name.endsWith('.zip')) {
                if (this._options.onShapefileUpload) {
                    this._options.onShapefileUpload(file);
                }
            }
            e.target.value = null;
        });

        return this._container;
    }

    _readGeoJSON(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const data = JSON.parse(e.target.result);
                if (this._options.onFileChange) {
                    this._options.onFileChange(data);
                }
            } catch (err) {
                if (this._options.onError) {
                    this._options.onError('Failed to parse GeoJSON file');
                }
            }
        };
        reader.readAsText(file);
    }

    onRemove() {
        this._container.parentNode.removeChild(this._container);
        this.map = undefined;
    }
}


class MultiPolygonWidget {
    constructor(options) {
        this.map = null;
        this.ready = false;

        this.options = options
        this.geomInput = $('#' + options.id);

        if (this.options.resize_trigger_selector) {
            this.resizeTriggerEls = $(this.options.resize_trigger_selector)
        }

        this.initialValue = this.geomInput.val()

        this.boundaryInfoUrl = this.geomInput.data("boundaryinfourl")
        this.UNGeojsonBoundaryUrl = this.geomInput.data("ungeojsonurl")
        this.convertAreaFileUrl = this.geomInput.data("convertareafileurl")

        this.createMap().then((map) => {
            this.map = map;
            if (this.resizeTriggerEls && this.resizeTriggerEls.length > 0) {
                for (let i = 0; i < this.resizeTriggerEls.length; i++) {
                    const $el = $(this.resizeTriggerEls[i]);
                    $el.on('click', () => {
                        this.fitBounds()
                    })
                }
            }

            this.fetchAndFitBounds()

            this.initDraw();

            this.initFromState()

            this.initUNBoundary()

            this.addFileUploadControl()
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
            container: this.options.map_id,
            style: defaultStyle,
            doubleClickZoom: false,
            scrollZoom: false,
        });


        map.addControl(new maplibregl.NavigationControl({
            showCompass: false,
        }), "bottom-right");

        map.addControl(new maplibregl.FullscreenControl());

        await new Promise((resolve) => map.on("load", resolve));

        return map;
    }

    fetchAndFitBounds() {
        if (this.boundaryInfoUrl) {
            fetch(this.boundaryInfoUrl)
                .then(response => response.json())
                .then(data => {
                    const {country_bounds} = data
                    if (country_bounds) {
                        this.countriesBounds = country_bounds
                    }
                    this.fitBounds()
                })
                .catch((error) => {
                    console.error('Error:', error);
                });
        }
    }

    fitBounds() {
        if (this.map) {
            this.map.resize()
            const feature = this.getValueParsed()

            if (!window.document.fullscreenElement) {
                if (feature) {
                    const bounds = turf.bbox(feature)
                    this.map.fitBounds([[bounds[0], bounds[1]], [bounds[2], bounds[3]]])
                } else {
                    if (this.countriesBounds) {
                        const bounds = [[this.countriesBounds[0], this.countriesBounds[1]], [this.countriesBounds[2], this.countriesBounds[3]]]
                        this.map.fitBounds(bounds)
                    }
                }
            }
        }
    }

    getValue() {
        return this.geomInput.val();
    }

    getValueParsed() {
        const value = this.getValue().trim()
        if (value && value !== "") {
            return JSON.parse(value)
        }
        return null
    }

    setValue(feature) {
        this.geomInput.val(feature);
    }

    initFromState() {
        const feature = this.getValueParsed()
        if (feature) {
            this.draw.add(feature);
            this.updateArea()
        }
    }

    initDraw() {
        this.draw = new MapboxDraw({
            displayControlsDefault: false, controls: {
                polygon: true, trash: true
            },
        });
        this.map.addControl(this.draw, 'top-left');

        this.map.on("draw.create", (e) => {
            // Replace any previously drawn polygon with the new one
            const newId = e.features[0].id;
            this.draw.getAll().features.forEach(f => {
                if (f.id !== newId) this.draw.delete(f.id);
            });
            this.updateArea();
        });
        this.map.on("draw.delete", this.updateArea);
        this.map.on("draw.update", this.updateArea);
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

            // clear any previous warnings
            this.hideWarnings()

            // Check for kinks before committing
            const kinks = turf.kinks(feature)
            if (kinks.features.length > 0) {
                // Find and delete only the offending feature(s)
                const allFeatures = this.draw.getAll().features
                allFeatures.forEach(f => {
                    const featureKinks = turf.kinks(f)
                    if (featureKinks.features.length > 0) {
                        this.draw.delete(f.id)
                    }
                })
                this.showWarning(
                    "The polygon you drew has self-intersecting edges. Please redraw without crossing lines"
                )
                return
            }

            const truncatedFeature = turf.truncate(feature, {
                precision: 6, coordinates: 2, mutate: true
            })

            this.setValue(JSON.stringify(truncatedFeature.geometry))

            // clear any map error
            this.hideWarnings()

            // check for self-intersecting polygons first; skip UN check if invalid
            const hasSelfIntersection = this.checkSelfIntersection(truncatedFeature.geometry)
            if (!hasSelfIntersection) {
                // check if the drawn feature has any issues with the UN boundary
                this.checkUNBoundaryIssues(truncatedFeature.geometry)
            }

        } else {
            this.setValue("")
        }
    }

    checkSelfIntersection(featureGeom) {
        if (!featureGeom) return false;

        const polygons = featureGeom.type === 'Polygon'
            ? [featureGeom.coordinates]
            : featureGeom.type === 'MultiPolygon'
                ? featureGeom.coordinates
                : [];

        for (const coords of polygons) {
            const kinks = turf.kinks(turf.polygon(coords));
            if (kinks.features.length > 0) {
                this.showWarning(
                    'The drawn polygon is self-intersecting (lines cross each other). ' +
                    'Please redraw the area so that no edges overlap.'
                );
                return true;
            }
        }

        return false;
    }

    initUNBoundary() {
        if (this.UNGeojsonBoundaryUrl) {
            fetch(this.UNGeojsonBoundaryUrl).then(res => res.json()).then(geojson => {
                // ensure not empty geojson
                if (geojson && Object.keys(geojson).length === 0 && geojson.constructor === Object) {
                    return
                }

                this.UNGeojsonBoundaryGeojson = geojson
                if (this.map) {
                    this.addUNBoundaryLayer()
                }
            })
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

    addFileUploadControl() {
        const control = new AreaFileUploadControl({
            onFileChange: (data) => {
                try {
                    const geom = this._extractMultiPolygon(data);
                    this._loadGeometry(geom);
                } catch (err) {
                    this.showWarning(err.message);
                }
            },
            onShapefileUpload: (file) => {
                this._uploadShapefile(file);
            },
            onError: (msg) => {
                this.showWarning(msg);
            },
        });
        this.map.addControl(control, 'top-right');
    }

    _extractMultiPolygon(data) {
        let geom;
        if (data.type === 'FeatureCollection') {
            const polygonFeatures = (data.features || []).filter(
                f => f.geometry && (f.geometry.type === 'Polygon' || f.geometry.type === 'MultiPolygon')
            );
            if (!polygonFeatures.length) {
                throw new Error('No Polygon or MultiPolygon features found in file');
            }
            // Merge all polygons/multipolygons into a single (multi)polygon
            let merged = turf.feature(polygonFeatures[0].geometry);
            for (let i = 1; i < polygonFeatures.length; i++) {
                merged = turf.union(merged, turf.feature(polygonFeatures[i].geometry));
            }
            geom = merged.geometry;
        } else if (data.type === 'Feature') {
            geom = data.geometry;
        } else {
            geom = data;
        }

        if (!geom) throw new Error('No geometry found in file');

        // If the result is MultiPolygon with only one part, convert to Polygon
        if (geom.type === 'MultiPolygon' && geom.coordinates.length === 1) {
            return {type: 'Polygon', coordinates: geom.coordinates[0]};
        } else if (geom.type === 'Polygon' || geom.type === 'MultiPolygon') {
            return geom;
        } else {
            throw new Error(`Unsupported geometry type: ${geom.type}. Only Polygon and MultiPolygon are supported.`);
        }
    }

    _loadGeometry(geom) {
        const truncated = turf.truncate(turf.feature(geom), {precision: 6, coordinates: 2, mutate: true});
        this.draw.deleteAll();
        this.draw.add(truncated.geometry);
        this.updateArea();
        const bounds = turf.bbox(truncated);
        this.map.fitBounds([[bounds[0], bounds[1]], [bounds[2], bounds[3]]], {padding: 20});
    }

    _setLoading(loading) {
        const container = this.map.getContainer();
        let overlay = container.querySelector('.file-upload-loading');
        if (loading) {
            if (!overlay) {
                overlay = document.createElement('div');
                overlay.className = 'file-upload-loading';
                overlay.innerHTML = '<div class="file-upload-loading-spinner"></div><span>Converting shapefile…</span>';
                container.appendChild(overlay);
            }
        } else if (overlay) {
            overlay.remove();
        }
    }

    async _uploadShapefile(file) {
        if (!this.convertAreaFileUrl) {
            this.showWarning('Shapefile conversion endpoint is not configured');
            return;
        }

        this._setLoading(true);

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch(this.convertAreaFileUrl, {
                method: 'POST',
                headers: {'X-CSRFToken': getCsrfToken()},
                body: formData,
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Failed to convert shapefile');
            }

            this._loadGeometry(data.geometry);
        } catch (err) {
            this.showWarning(err.message);
        } finally {
            this._setLoading(false);
        }
    }
}
