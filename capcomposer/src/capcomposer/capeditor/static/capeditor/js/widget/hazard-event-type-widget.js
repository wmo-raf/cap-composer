function HazardEventTypeWidget(id, initialValue) {
    const inputId = '#' + id
    this.input = $(inputId);

    const wmoListSelectId = id + "_wmo_list"
    this.wmoListSelectInput = $("#" + wmoListSelectId);


    const isWmoInputId = id.split("-event")[0] + "-is_in_wmo_event_types_list"
    this.checkIsWmoInput = $("#" + isWmoInputId)

    const that = this


    this.checkIsWmoInput.change(function () {
        const checked = $(this).is(":checked")

        if (checked) {
            that.input.hide()
            that.wmoListSelectInput.show()
        } else {
            that.input.show()
            that.wmoListSelectInput.hide()
        }

    })

    if (this.checkIsWmoInput.is(":checked")) {
        // clear any previous value
        that.wmoListSelectInput.show()
    } else {
        that.input.show()
    }

    this.wmoListSelectInput.change(function () {
        const selectedVal = $(this).val()
        that.setState(selectedVal)
    })
}

HazardEventTypeWidget.prototype.setState = function (newState) {
    this.input.val(newState);
};

HazardEventTypeWidget.prototype.getState = function () {
    return this.input.val();
};

HazardEventTypeWidget.prototype.getValue = function () {
    return this.input.val();
};

HazardEventTypeWidget.prototype.focus = function () {
}