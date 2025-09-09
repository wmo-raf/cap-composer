class EventCodeWidgetController extends window.StimulusModule.Controller {
    connect() {
        new EventCodeWidget(this.element.id, this.element.dataset.value);
    }
}

window.wagtail.app.register('event-code', EventCodeWidgetController);