class CircleWidget {
    constructor(options, initialState) {
        this.circleInput = $('#' + options.id);
        this.options = options

        this.latInput = $('#' + options.id + "_circle_lat");
        this.lonInput = $('#' + options.id + "_circle_lon");
        this.radiusInput = $('#' + options.id + "_circle_radius");

        this.countriesBounds = this.circleInput.data("bounds")

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

            this.initMarker()

            this.initLayer()


            if (initialState) {
                this.setState(initialState)
                this.initFromState()
            }
        })

        this.latInput.on("change", () => {
            this.onCoordsChange()
        })
        this.lonInput.on("change", () => {
            this.onCoordsChange()
        })
        this.radiusInput.on("change", () => {
            this.onCoordsChange()
        })

        this.latInput.bind('keypress keydown keyup', (e) => {
            if (e.keyCode === 13) {
                e.preventDefault();
                this.onCoordsChange()
            }
        });

        this.lonInput.bind('keypress keydown keyup', (e) => {
            if (e.keyCode === 13) {
                e.preventDefault();
                this.onCoordsChange()
            }
        });

        this.radiusInput.bind('keypress keydown keyup', (e) => {
            if (e.keyCode === 13) {
                e.preventDefault();
                this.onCoordsChange()
            }
        });
    }

    setState(newState) {
        this.circleInput.val(newState);
    };

    getState() {
        return this.circleInput.val();
    };

    getValue() {
        return this.circleInput.val();
    };

    focus() {
    }

    async initMap() {
        const defaultStyle = {
            'version': 8,
            'sources': {
                'osm': {
                    'type': 'raster',
                    'tiles': [
                        "https://tile.openstreetmap.org/{z}/{x}/{y}.png"
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
                'id': 'osm',
                'source': 'osm',
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

    initMarker() {
        this.marker = new maplibregl.Marker({
            draggable: true
        }).setLngLat([0, 0]).addTo(this.map);


        if (this.countriesBounds) {
            const bboxPolygon = turf.bboxPolygon(this.countriesBounds)
            const center = turf.center(bboxPolygon)


            if (center && center.geometry && !!center.geometry.coordinates.length) {
                const {coordinates} = center.geometry
                this.marker.setLngLat(coordinates)
            }
        }


        this.marker.on('dragend', () => {
            const lngLat = this.marker.getLngLat();
            const {lat, lng} = lngLat
            this.latInput.val(lat)
            this.lonInput.val(lng)

            this.onCoordsChange()
        });
    }

    onCoordsChange() {
        const lat = this.latInput.val()
        const lon = this.lonInput.val()
        const radius = this.radiusInput.val()

        if (lat && lon && radius) {
            const options = {steps: 64, units: 'kilometers'}
            const circle = turf.circle([lon, lat], radius, options);

            this.setSourceData(circle)
        }
    }

    getCircleValue() {
        const lat = this.latInput.val()
        const lon = this.lonInput.val()
        const radius = this.radiusInput.val()

        if (lat && lon && radius) {
            return `${lon},${lat} ${radius}`
        }

        return null
    }

    parseCircleValue() {
        const circleValue = this.getState()

        if (circleValue) {
            const parts = circleValue.split(" ")
            if (parts.length > 1) {
                const radius = Number(parts[1])
                const [lon, lat] = parts[0].split(",")
                if (radius && lon && lat) {
                    return {lon, lat, radius}

                }
            }
        }

        return null
    }

    initLayer() {
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

    setSourceData(feature) {
        if (feature) {
            // add data to source
            this.map.getSource("polygon").setData(feature)

            // fit map to bounds
            const bbox = turf.bbox(feature)
            const bounds = [[bbox[0], bbox[1]], [bbox[2], bbox[3]]]
            this.map.fitBounds(bounds, {padding: 50})


            const circleValue = this.getCircleValue()

            if (circleValue) {
                this.setState(circleValue)
            }

        } else {
            // clear source data
            this.map.getSource("polygon").setData(this.emptyGeojsonData)

            // set state to empty string
            this.setState("")
        }
    }

    initFromState() {
        const circeValue = this.getState()

        if (circeValue) {
            const {lon, lat, radius} = this.parseCircleValue(circeValue) || {}


            if (lon && lat && radius) {
                this.lonInput.val(lon)
                this.latInput.val(lat)
                this.radiusInput.val(radius)

                // set marker
                this.marker.setLngLat([lon, lat])

                this.onCoordsChange()
            }
        }
    }

    onSeverityChange() {
        const severityColor = this.getSeverityColor()
        if (severityColor) {
            this.map.setPaintProperty("polygon", "fill-color", severityColor)
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
}




