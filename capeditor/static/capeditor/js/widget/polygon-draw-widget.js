/* global ol */
'use strict';

class PolygonDrawWidget {
    constructor(options) {
        this.map = null;
        this.ready = false;

        this.options = options
        this.geomInput = document.getElementById(this.options.id)


        if (this.options.resize_trigger_selector) {
            this.resizeTriggerEls = document.querySelectorAll(this.options.resize_trigger_selector)
        }

        this.initalValue = this.geomInput.value
        this.countriesBounds = this.geomInput.dataset.bounds ? JSON.parse(this.geomInput.dataset.bounds) : null

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
        });

    }


    async createMap() {
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
        const map = new maplibregl.Map({
            container: this.options.map_id,
            style: defaultStyle,
            doubleClickZoom: false,
            scrollZoom: false,
        });


        map.addControl(
            new maplibregl.NavigationControl({
                showCompass: false,
            }), "bottom-right"
        );

        map.addControl(new maplibregl.FullscreenControl());

        await new Promise((resolve) => map.on("load", resolve));

        return map;
    }

    fitBounds() {
        if (this.map) {
            this.map.resize()
            if (!window.document.fullscreenElement) {
                if (this.initalValue) {
                    const feature = JSON.parse(this.initalValue)
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
            type: 'Feature',
            geometry: geom,
        };
    }

    setValue(feature) {
        this.geomInput.value = feature;
    }

    initDraw() {
        const feature = this.getValue()
        this.draw = new MapboxDraw({
            displayControlsDefault: false,
            controls: {
                polygon: true,
                trash: true
            },
        });
        this.map.addControl(this.draw, 'top-left');

        if (feature) {
            this.draw.add(feature);
        }


        this.map.on("draw.create", this.updateArea);
        this.map.on("draw.delete", this.updateArea);
        this.map.on("draw.update", this.updateArea);
        this.map.on("draw.combine", this.updateArea);
        this.map.on("draw.uncombine", this.updateArea);


    }

    updateArea = () => {
        let combinedFeatures

        const featureCollection = this.draw.getAll()
        if (featureCollection && featureCollection.features && !!featureCollection.features.length) {
            combinedFeatures = turf.combine(featureCollection)
        }

        if (combinedFeatures) {
            const feature = combinedFeatures.features[0]


            const truncatedFeature = turf.truncate(feature, {
                precision: 2,
                coordinates: 2,
                mutate: true
            })

            this.setValue(JSON.stringify(truncatedFeature.geometry))

        } else {
            this.setValue("")
        }
    }
}
