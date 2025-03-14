class EventCodeWidget {
    constructor(id, initialValue) {
        this.eventCodeInput = $('#' + id);


        let infoPrefix = id.split("event_code")

        let categoryInputId = null

        if (infoPrefix) {
            categoryInputId = infoPrefix[0] + "category"
        }

        if (categoryInputId) {
            this.eventChoices = this.eventCodeInput.data("choices");
            this.categoryInput = $('#' + categoryInputId);
            this.setOptions()

            this.categoryInput.on('change', () => {
                this.setOptions()
            })

            if (initialValue) {
                this.setState(initialValue)
            }
        }
    }

    setOptions() {
        const category = this.categoryInput.val();


        if (category) {
            const options = this.eventChoices.filter(choice => choice.cats.includes(category));

            this.createOptions(options)
        }
    }

    setState(newState) {
        this.eventCodeInput.val(newState);
    };


    createOptions(options) {
        this.eventCodeInput.empty();

        this.eventCodeInput.append($('<option>', {
            value: " ",
            text: '---------',
        }));

        options.forEach(option => {
            this.eventCodeInput.append($('<option>', {
                value: option.value,
                text: `${option.label} ${option.value}`
            }));
        });
    }

}