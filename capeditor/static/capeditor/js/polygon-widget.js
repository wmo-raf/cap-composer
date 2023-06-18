function PolygonWidget(options) {

    this.geomInput = $('#' + options.id);

    // initialize map
    this.map = L.map(options.map_id, {
        center: [2.7128726951001596, 23.379626859864345],
        zoom: 5
    })

    // add base layer
    L.tileLayer("http://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png", {
        maxZoom: 24,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="http://cartodb.com/attributions">CartoDB</a>'
    }).addTo(this.map)

    this.drawControl = null

    this.initDrawControl()
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


PolygonWidget.prototype.initDrawControl = function () {
    // initialize feature group of drawn items
    this.drawnItems = new L.FeatureGroup();
    this.map.addLayer(this.drawnItems);

    // set draw control
    this.setDrawControl()

    this.map.on("draw:created", (e) => {
        this.drawnItems.addLayer(e.layer);
        const geomString = JSON.stringify(e.layer.toGeoJSON().geometry)
        this.setState(geomString)
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
        });
    });

    this.map.on("draw:deleted", (e) => {
        this.drawControl.setDrawingOptions({draw: true})
    });
}


PolygonWidget.prototype.setDrawControl = function () {
    const value = this.getValue()
    const canCreate = !Boolean(value)

    if (this.drawControl) {
        this.map.removeControl(this.drawControl)
    }

    this.drawControl = new L.Control.Draw({
        edit: {
            featureGroup: this.drawnItems,
            edit: !canCreate,
            remove: !canCreate,
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
            rectangle: canCreate,
            polygon: canCreate,
        },
    });

    this.map.addControl(this.drawControl);
}


PolygonWidget.prototype.initFromState = function () {
    const value = this.getState()
    // const feature = JSON.parse(value)


    const feature = {
        "type": "Polygon",
        "coordinates": [[
            [-109.05, 41.00],
            [-102.06, 40.99],
            [-102.03, 36.99],
            [-109.04, 36.99],
            [-109.05, 41.00]
        ]]
    }

    if (feature && feature.coordinates) {

        // const revCoords = feature.coordinates.reduce((all, coord) => {
        //     all.push([coord[1], coord[0]])
        //     return all
        // }, [])

        const myStyle = {
            "color": "#ff7800",
            "weight": 5,
            "opacity": 0.65
        };

        const polygon = L.polygon(feature.coordinates, myStyle).addTo(this.map)


        // fit to bounds
        // this.map.fitBounds(polygon.getBounds());

        // this.setDrawControl()
    }
}