document.addEventListener('DOMContentLoaded', function () {
    const wis2BoxCheckbox = document.querySelector('#id_is_wis2box');
    const metadataPanel = document.querySelector('#panel-wis2box_metadata_id-section');
    const internalTopicPanel = document.querySelector('#panel-topic-section');

    function toggleFields() {
        if (!metadataPanel || !internalTopicPanel) {
            return;
        }
        // Show metadata panel if WIS2 node is checked, otherwise show internal topic panel
        metadataPanel.style.display = wis2BoxCheckbox.checked ? 'block' : 'none';
        internalTopicPanel.style.display = wis2BoxCheckbox.checked ? 'none' : 'block';
    }


    if (wis2BoxCheckbox) {
        toggleFields();
        wis2BoxCheckbox.addEventListener('change', toggleFields);
    }
});
