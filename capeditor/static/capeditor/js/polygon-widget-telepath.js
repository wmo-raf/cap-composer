(function () {
    function PolygonInput(html) {
        this.html = html;
    }

    PolygonInput.prototype.render = function (placeholder, name, id, initialState) {
        const html = this.html.replace(/__NAME__/g, name).replace(/__ID__/g, id);
        placeholder.outerHTML = html;

        const options = {
            id: id,
            map_id: `${id}_map`,
            name: name
        };

        const polygonWidget = new PolygonWidget(options);
        polygonWidget.setState(initialState);

        if (initialState) {
            polygonWidget.initFromState()
        }

        return polygonWidget;
    };

    window.telepath.register('capeditor.widgets.PolygonInput', PolygonInput);
})();