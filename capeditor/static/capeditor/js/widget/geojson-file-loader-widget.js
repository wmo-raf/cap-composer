class FileUploadControl {
    constructor(options) {
        this._options = Object.assign({}, this._options, options)
    }

    onAdd(map) {
        this.map = map;
        this._container = document.createElement('div');
        this._container.className = 'maplibregl-ctrl maplibregl-ctrl-group file-upload-ctrl';
        this._container.innerHTML = `
                <div class="file-upload-ctrl-icon"></div>
                <div class='file-upload-ctrl-label'>Upload new</div>
                <input class="hidden" type="file" accept=".json,.geojson" style="display: none;">
          `;

        this._container.addEventListener('click', (e) => {
            this._container.querySelector('input').click();
        });

        this._container.querySelector('input').addEventListener('change', (e) => {
            const file = e.target.files[0];
            const reader = new FileReader();
            reader.onload = (e) => {
                try {
                    const data = JSON.parse(e.target.result);
                    if (this._options.onFileChange) {
                        this._options.onFileChange(data);
                    }
                } catch (err) {
                    console.error('Error parsing file', err);
                }
            };
            reader.readAsText(file);

            reader.onerror = function (e) {
                console.error('File could not be read! Code ' + e)
            }

            e.target.value = null;
            return false;
        })

        return this._container;
    }

    onRemove() {
        this._container.parentNode.removeChild(this._container);
        this.map = undefined;
    }
}


class GeojsonFileLoaderDrawWidget {
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

            if (this.initialValue) {
                const data = this.getValue()
                this.addFileLayer(data)
            }

            this.addFileUploadControl()
        });
    }

    onFileChanged(data) {
        if (!data.type || data.type !== 'FeatureCollection') {
            console.error('Invalid GeoJSON file');
        }

        // take the first feature
        const feature = data.features[0];
        // truncate coordinates to 6 decimal places
        const truncatedFeature = turf.truncate(feature, {
            precision: 6, coordinates: 2, mutate: true
        })

        const geomType = truncatedFeature.geometry.type;
        if (!(geomType === 'Polygon' || geomType === 'MultiPolygon')) {
            console.error('Invalid geometry type');
        }

        this.addFileLayer(truncatedFeature);
        this.setValue(JSON.stringify(truncatedFeature.geometry));
    }

    addFileLayer(data) {
        const source = this.map.getSource('geojson');

        if (source) {
            source.setData(data);
        } else {
            this.map.addSource('geojson', {
                type: 'geojson', data: data,
            });

            this.map.addLayer({
                id: 'geojson', type: 'fill', source: 'geojson', paint: {
                    'fill-color': '#088', 'fill-opacity': 0.8,
                },
            })
        }
        const bounds = turf.bbox(data);
        this.map.fitBounds([[bounds[0], bounds[1]], [bounds[2], bounds[3]]], {padding: 20});

        this.showDeleteButton();
    }

    addFileUploadControl() {
        const fileUploadControl = new FileUploadControl({onFileChange: this.onFileChanged.bind(this)});
        this.map.addControl(fileUploadControl, 'top-right');
        return fileUploadControl;
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

    createDeleteButton() {
        const deleteButton = document.createElement('button');
        deleteButton.className = 'delete-geom-btn';
        deleteButton.title = 'Delete';
        deleteButton.addEventListener('click', (e) => {
            e.preventDefault()

            this.setValue('');
            this.map.removeLayer('geojson');
            this.map.removeSource('geojson');

            this.hideDeleteButton();
        });
        this.map.getContainer().appendChild(deleteButton);
    }


    showDeleteButton() {
        const deleteButton = this.map.getContainer().querySelector('.delete-geom-btn');
        if (deleteButton) {
            deleteButton.style.display = 'block';
        } else {
            this.createDeleteButton();
        }
    }

    hideDeleteButton() {
        const deleteButton = this.map.getContainer().querySelector('.delete-geom-btn');
        if (deleteButton) {
            deleteButton.style.display = 'none';
        }
    }
}
