(function () {
    function BoundaryPolygonInput(html) {
        this.html = html;
    }

    BoundaryPolygonInput.prototype.render = function (placeholder, name, id, initialState) {
        const html = this.html.replace(/__NAME__/g, name).replace(/__ID__/g, id);
        placeholder.outerHTML = html;

        const options = {
            id: id,
            map_id: `${id}_map`,
            name: name,
        };

        return new BoundaryPolygonWidget(options, initialState);
    };

    window.telepath.register('capeditor.widgets.BoundaryPolygonInput', BoundaryPolygonInput);
})();