class AreaRegistry {
    constructor(widgetId, map) {
        this.widgetId = widgetId
        this.map = map

        window.alertAreas = window.alertAreas || {}
        window.alertAreaWidgets = window.alertAreaWidgets || {}

        window.alertAreas[widgetId] = null
        window.alertAreaWidgets[widgetId] = this

        this.initSiblingAreasLayer()

        this.observeBlockRemoval()
    }

    observeBlockRemoval() {
        const widgetEl = document.getElementById(this.widgetId)
        if (!widgetEl) return

        // The actual deletion container is the data-streamfield-child div
        const streamfieldChild = widgetEl.closest('[data-streamfield-child]')
        if (!streamfieldChild) return

        this.mutationObserver = new MutationObserver(() => {
            if (streamfieldChild.getAttribute('aria-hidden') === 'true') {
                this.destroy()
            }
        })

        this.mutationObserver.observe(streamfieldChild, {
            attributes: true,
            attributeFilter: ['aria-hidden']
        })
    }

    initSiblingAreasLayer() {
        this.map.addSource("sibling-areas", {
            type: "geojson",
            data: {type: "FeatureCollection", features: []}
        })

        this.map.addLayer({
            id: "sibling-areas-fill",
            type: "fill",
            source: "sibling-areas",
            paint: {
                "fill-color": "#666666",
                "fill-opacity": 0.15  // subtle tint, doesn't compete with active area
            }
        })

        this.map.addLayer({
            id: "sibling-areas-outline",
            type: "line",
            source: "sibling-areas",
            paint: {
                "line-color": "#666666",
                "line-width": 1.5,
                "line-dasharray": [2, 2]  // dashed line signals "inactive" without being heavy
            }
        })


        this.refreshSiblingAreas()
    }

    update(geom) {
        window.alertAreas[this.widgetId] = geom || null
        this.refreshSiblingAreas()

        // notify all other widgets to refresh their sibling layers
        Object.values(window.alertAreaWidgets).forEach(registry => {
            if (registry.widgetId !== this.widgetId) {
                registry.refreshSiblingAreas()
            }
        })
    }

    refreshSiblingAreas() {
        const features = Object.entries(window.alertAreas)
            .filter(([id, geom]) => id !== this.widgetId && geom !== null)
            .map(([id, geom]) => ({
                type: "Feature",
                geometry: geom,
                properties: {id}
            }))

        this.map.getSource("sibling-areas").setData({
            type: "FeatureCollection",
            features
        })
    }

    checkIntersections() {
        const areas = window.alertAreas
        const entries = Object.entries(areas).filter(([, geom]) => geom !== null)

        for (let i = 0; i < entries.length; i++) {
            for (let j = i + 1; j < entries.length; j++) {
                const [, geomA] = entries[i]
                const [, geomB] = entries[j]

                if (turf.booleanIntersects(turf.feature(geomA), turf.feature(geomB))) {
                    return "This area overlaps with another alert area. Intersecting areas are not allowed"
                }
            }
        }

        return null
    }

    destroy() {
        if (this.mutationObserver) {
            this.mutationObserver.disconnect()
            this.mutationObserver = null
        }

        delete window.alertAreas[this.widgetId]
        delete window.alertAreaWidgets[this.widgetId]

        Object.values(window.alertAreaWidgets).forEach(registry => {
            registry.refreshSiblingAreas()
        })
    }
}