class AreaRegistry {
    constructor(widgetId, map) {
        this.widgetId = widgetId
        this.map = map

        window.alertAreas = window.alertAreas || {}
        window.alertAreaWidgets = window.alertAreaWidgets || {}

        window.alertAreas[widgetId] = null
        window.alertAreaWidgets[widgetId] = this

        this.intersectionThreshold = 1000 // default until fetched

        this.initSiblingAreasLayer()
        this.fetchMapWidgetConfig()
        this.observeBlockRemoval()
    }

    fetchMapWidgetConfig() {
        const widgetEl = document.getElementById(this.widgetId)
        if (!widgetEl) return

        const mapWidgetConfigUrl = widgetEl.dataset.mapWidgetConfigUrl
        if (!mapWidgetConfigUrl) return

        // If already cached, use it directly
        if (window.alertAreaConfig) {
            this.intersectionThreshold = window.alertAreaConfig.intersection_area_threshold || 1000
            return
        }

        // If a fetch is already in flight, wait for it
        if (window.alertAreaConfigPromise) {
            window.alertAreaConfigPromise.then(config => {
                this.intersectionThreshold = config.intersection_area_threshold || 1000
            })
            return
        }

        // First widget to init — fetch and cache
        window.alertAreaConfigPromise = fetch(mapWidgetConfigUrl)
            .then(res => res.json())
            .then(config => {
                window.alertAreaConfig = config
                // Update all already-initialized widgets with the fetched threshold
                Object.values(window.alertAreaWidgets).forEach(registry => {
                    registry.intersectionThreshold = config.intersection_area_threshold || 1000
                })
                return config
            })
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
                "fill-opacity": 0.7  // subtle tint, doesn't compete with active area
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

        const intersectionError = this.checkIntersections()
        this.onIntersectionStateChange(intersectionError !== null)

        Object.values(window.alertAreaWidgets).forEach(registry => {
            if (registry.widgetId !== this.widgetId) {
                registry.refreshSiblingAreas()
            }
        })
    }

    onIntersectionStateChange(hasIntersection) {
        window.alertAreasHasIntersection = hasIntersection
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
        const threshold = (window.alertAreaConfig && window.alertAreaConfig.intersection_area_threshold)
            || this.intersectionThreshold

        for (let i = 0; i < entries.length; i++) {
            for (let j = i + 1; j < entries.length; j++) {
                const [, geomA] = entries[i]
                const [, geomB] = entries[j]

                const featureA = turf.feature(geomA)
                const featureB = turf.feature(geomB)

                if (turf.booleanIntersects(featureA, featureB)) {
                    const intersection = turf.intersect(turf.featureCollection([featureA, featureB]))

                    if (intersection) {
                        const intersectionArea = turf.area(intersection)
                        if (intersectionArea > threshold) {
                            return "This area overlaps with another alert area. Intersecting areas are not allowed"
                        }
                    }
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

        // If no widgets remain, clean up global state entirely
        if (Object.keys(window.alertAreaWidgets).length === 0) {
            window.alertAreaConfig = null
            window.alertAreaConfigPromise = null
            window.alertAreasHasIntersection = false
        }

        Object.values(window.alertAreaWidgets).forEach(registry => {
            registry.refreshSiblingAreas()
            const intersectionError = registry.checkIntersections()
            registry.onIntersectionStateChange(intersectionError !== null)
        })
    }
}