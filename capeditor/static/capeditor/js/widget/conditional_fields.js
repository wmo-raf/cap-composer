$(document).ready(function () {

        const $scope = $('#id_scope')


        const $messageType = $('#id_msgType')


        const $status = $('#id_status')


        const referencesPanel = $(".cap-alert__panel-references")
        const notePanel = $(".cap-alert__panel-note")
        const restrictionPanel = $(".cap-alert__panel-restriction")
        const addressesPanel = $(".cap-alert__panel-addresses")


        // check scope
        if ($scope.val() === 'Restricted') {
            restrictionPanel.show()
            addressesPanel.hide()
        }

        if ($scope.val() === 'Private') {
            addressesPanel.show()
            restrictionPanel.hide()
        }

        if ($scope.val() === 'Public') {
            restrictionPanel.hide()
            addressesPanel.hide()
        }

        // check message
        if ($messageType.val() === 'Error') {
            notePanel.show()
            referencesPanel.show()
        } else if ($messageType.val() === 'Update' || $messageType.val() === 'Cancel' || $messageType.val() === 'Ack') {
            referencesPanel.show()
            notePanel.hide()
        } else {
            notePanel.hide()
            referencesPanel.hide()
        }

        $scope.on('change', function (e) {
            const optionSelected = $("option:selected", this)
            const valueSelected = optionSelected.val();

            if (valueSelected === 'Restricted') {
                restrictionPanel.show()
                addressesPanel.hide()
            }

            if (valueSelected === 'Private') {
                addressesPanel.show()
                restrictionPanel.hide()

            }

            if (valueSelected === 'Public') {
                restrictionPanel.hide()
                addressesPanel.hide()
            }

        })

        $messageType.on('change', function (e) {
            const optionSelected = $("option:selected", this)
            const valueSelected = optionSelected.val();

            if (valueSelected === 'Error') {
                referencesPanel.show()


                if ($status.val() === "Exercise") {
                    notePanel.show()
                } else {
                    notePanel.hide()
                }

            } else if (valueSelected === 'Update' || valueSelected === 'Cancel' || valueSelected === 'Ack') {
                referencesPanel.show()
                notePanel.hide()
            } else {
                notePanel.hide()
                referencesPanel.hide()
            }
        })


        $status.on('change', function (e) {
            const optionSelected = $("option:selected", this)
            const valueSelected = optionSelected.val();


            if (valueSelected === 'Exercise' && $messageType.val() === "Error") {
                notePanel.show()
            } else {
                notePanel.hide()
            }
        })
    }
);