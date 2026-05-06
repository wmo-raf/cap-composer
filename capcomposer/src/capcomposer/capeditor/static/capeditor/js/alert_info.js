// alert_info.js
// Adds a Translate button to each AlertInfo block in the Wagtail admin UI
    console.log("hello")

(function() {
    function addTranslateButtons() {
        // Find all alert info blocks
        document.querySelectorAll('[data-contentpath$="alert_info"]').forEach(function(block) {
            if (block.querySelector('.alert-info-translate-btn')) return; // Only add once
            var btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'button alert-info-translate-btn';
            btn.textContent = 'Translate';
            btn.style.marginLeft = '8px';
            btn.onclick = function() {
                // Find the parent StreamBlock (info)
                var streamBlock = block.closest('[data-streamfield-stream]');
                if (!streamBlock) return;
                // Find the add button for alert_info
                var addBtn = streamBlock.querySelector('[data-streamfield-add-block-type="alert_info"]');
                if (!addBtn) return;
                addBtn.click();
                // Wait for the new block to appear, then copy values
                setTimeout(function() {
                    var blocks = streamBlock.querySelectorAll('[data-contentpath$="alert_info"]');
                    var newBlock = blocks[blocks.length - 1];
                    if (!newBlock || newBlock === block) return;
                    // Copy all input values except language
                    var inputs = block.querySelectorAll('input, textarea, select');
                    var newInputs = newBlock.querySelectorAll('input, textarea, select');
                    for (var i = 0; i < inputs.length; i++) {
                        if (inputs[i].name.endsWith('language')) continue;
                        if (inputs[i].type === 'checkbox' || inputs[i].type === 'radio') {
                            newInputs[i].checked = inputs[i].checked;
                        } else {
                            newInputs[i].value = inputs[i].value;
                        }
                        // Trigger change event
                        newInputs[i].dispatchEvent(new Event('change', {bubbles: true}));
                    }
                    // Focus the language field in the new block
                    for (var j = 0; j < newInputs.length; j++) {
                        if (newInputs[j].name.endsWith('language')) {
                            newInputs[j].focus();
                            break;
                        }
                    }
                }, 300);
            };
            // Add the button to the block header
            var header = block.querySelector('.c-sf-block__header') || block;
            header.appendChild(btn);
        });
    }
    document.addEventListener('DOMContentLoaded', addTranslateButtons);
    document.addEventListener('wagtail:streamfieldAdded', addTranslateButtons);
})();
