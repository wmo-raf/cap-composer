function PolygonWidget(options) {

    this.geomInput = $('#' + options.id);

    // initialize map
    this.map = L.map(options.map_id, {
        center: [2.7128726951001596, 23.379626859864345],
        zoom: 5,
        zoomControl: false,
    })

    // add base layer
    L.tileLayer("http://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png", {
        maxZoom: 24,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="http://cartodb.com/attributions">CartoDB</a>'
    }).addTo(this.map)


    // boundaries
    L.vectorGrid.protobuf("http://127.0.0.1:8300/api/admin-boundary/tiles/{z}/{x}/{y}", {
        vectorTileLayerStyles: {
            default: {
                weight: 0,
                fillColor: '#fff',
                fillOpacity: 0,
            }
        }
    }).addTo(this.map);

    // zoom control
    L.control.zoom({
        position: 'bottomright'
    }).addTo(this.map);

    // full screen control
    this.map.addControl(new L.Control.Fullscreen({position: 'bottomright',}));

    this.drawControl = null
    this.uploadControl = null

    // initialize feature group of drawn items
    this.drawnItems = new L.FeatureGroup();
    this.map.addLayer(this.drawnItems);

    this.initControls()

    setTimeout(() => {
        this.map.invalidateSize()
    }, 400);


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


PolygonWidget.prototype.initControls = function () {
    // set file upload control
    this.setUploadControl()

    // set draw control
    this.setDrawControl()


    this.map.on("draw:created", (e) => {
        this.drawnItems.addLayer(e.layer);
        const geomString = JSON.stringify(e.layer.toGeoJSON().geometry)

        this.map.fitBounds(e.layer.getBounds())

        this.setState(geomString)
        this.setDrawControl()
        this.setUploadControl()
    });

    this.map.on("draw:edited", (e) => {
        e.layers.eachLayer((layer) => {
            let isIntersecting = false;

            this.drawnItems.eachLayer((existingLayer) => {
                if (layer !== existingLayer && layer.intersects(existingLayer)) {
                    this.drawnItems.removeLayer(layer);
                    isIntersecting = true;
                }
            });

            if (!isIntersecting) {
                layer.setStyle({color: "blue"});
            }

            const geomString = JSON.stringify(layer.toGeoJSON().geometry)
            this.setState(geomString)

            this.setDrawControl()
            this.setUploadControl()
        });
    });

    this.map.on("draw:deleted", (e) => {
        const deletedLayers = e.layers._layers
        if (Object.keys(deletedLayers).length > 0) {
            this.setState("")
            this.setDrawControl()
            this.setUploadControl()
        }
    });
}


PolygonWidget.prototype.setDrawControl = function () {
    const value = this.getState()

    const hasGeomValue = Boolean(value)


    if (this.drawControl) {
        this.map.removeControl(this.drawControl)
    }

    this.drawControl = new L.Control.Draw({
        edit: {
            featureGroup: this.drawnItems,
            edit: hasGeomValue,
            remove: hasGeomValue,
            poly: {
                allowIntersection: true,
            },
            allowIntersection: true,
        },
        draw: {
            polyline: false,
            marker: false,
            circle: false,
            circlemarker: false,
            rectangle: !hasGeomValue,
            polygon: !hasGeomValue,
        },
    });

    this.map.addControl(this.drawControl);
}


PolygonWidget.prototype.setUploadControl = function () {
    const value = this.getState()
    const hasGeomValue = Boolean(value)


    if (this.uploadControl) {
        this.map.removeControl(this.uploadControl)
    }


    const style = {
        color: '#3288ff',
        opacity: 1.0,
        fillOpacity: 0.3,
        weight: 3,
        clickable: false
    };

    L.Control.FileLayerLoad.LABEL = `<div class="upload-icon" title="Upload File" ><svg class="icon icon-upload" aria-hidden="true">
                                        <use href="#icon-upload"></use>
                                     </svg></div>`;

    this.uploadControl = L.Control.fileLayerLoad({
        fitBounds: true,
        addToMap: false,
        layerOptions: {
            style: style,
            pointToLayer: function (data, latlng) {
                return L.circleMarker(latlng, {style: style}
                );
            }
        }
    });


    if (!hasGeomValue) {
        this.map.addControl(this.uploadControl);
        this.uploadControl.loader.on('data:loaded', (e) => {
            const geojson = e.layer.toGeoJSON()
            if (geojson.features) {
                const geojsonFeature = geojson.features[0]


                if (geojsonFeature.geometry.type !== "Polygon") {
                    alert(`Uploaded type ${geojsonFeature.geometry.type} not supported`)
                } else {
                    const geojsonLayer = L.geoJSON(geojsonFeature)

                    geojsonLayer.eachLayer((layer) => {
                        this.drawnItems.addLayer(layer);
                        this.setState(JSON.stringify(geojsonFeature.geometry))
                    });

                    this.setDrawControl()
                    this.setUploadControl()
                }
            }
        });
    }
}


PolygonWidget.prototype.initFromState = function () {
    const value = this.getState()

    if (value) {
        const geojsonFeature = JSON.parse(value)
        const geojsonLayer = L.geoJSON(geojsonFeature)
        geojsonLayer.eachLayer((layer) => {
            this.drawnItems.addLayer(layer);
        });

        this.setDrawControl()
        this.setUploadControl()

        setTimeout(() => {
            this.map.fitBounds(geojsonLayer.getBounds())
        }, 400);

    }
}