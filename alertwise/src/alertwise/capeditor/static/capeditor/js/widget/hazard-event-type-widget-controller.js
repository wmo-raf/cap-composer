class HazardEventTypeWidgetController extends window.StimulusModule.Controller {
    connect() {
        new HazardEventTypeWidget(this.element.id, this.element.value);
    }
}

window.wagtail.app.register('hazard-event-type-widget', HazardEventTypeWidgetController);