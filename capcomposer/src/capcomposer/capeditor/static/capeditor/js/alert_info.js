// alert_info.js
// Replaces the Duplicate button with a Translate button on the source AlertInfo block.
// Hides "+" add buttons so alert_info blocks can only be created via Translate.
// Shows "Update Translation" on translated blocks when source editable fields change.

(function () {
    var TRANSLATABLE_FIELDS = ['headline', 'description', 'instruction', 'audience'];

    var ADMIN_PREFIX = '/' + window.location.pathname.split('/').filter(Boolean)[0];

    var LOCK_STORAGE_KEY = 'alert-info-locked:' + window.location.pathname;

    // Tracks which translatable fields have changed in the source block since last full update.
    // WeakMap<blockElement, Set<fieldName>>
    var sourceChangedFields = new WeakMap();

    function getLockedIds() {
        try { return JSON.parse(localStorage.getItem(LOCK_STORAGE_KEY) || '[]'); }
        catch (e) { return []; }
    }

    function markBlockLocked(id) {
        if (!id) return;
        var ids = getLockedIds();
        if (ids.indexOf(id) === -1) { ids.push(id); }
        try { localStorage.setItem(LOCK_STORAGE_KEY, JSON.stringify(ids)); } catch (e) {}
    }

    function getBlockId(block) {
        var idInput = block.querySelector('input[name$="-id"]');
        return idInput ? idInput.value : null;
    }

    function isTranslatedBlock(block) {
        if (block.classList.contains('alert-info-translation')) return true;
        var blockId = getBlockId(block);
        return blockId ? getLockedIds().indexOf(blockId) !== -1 : false;
    }

    function getAlertInfoBlocks(container) {
        return Array.from(container.querySelectorAll('[data-streamfield-child]')).filter(function (b) {
            var ti = b.querySelector('input[name$="-type"]');
            return ti && ti.value === 'alert_info';
        });
    }

    function getTranslatedBlocksInContainer(container) {
        return getAlertInfoBlocks(container).filter(isTranslatedBlock);
    }

    function getUsedLanguages(container) {
        var used = [];
        getTranslatedBlocksInContainer(container).forEach(function (b) {
            var langSel = b.querySelector('select[name$="language"]');
            if (langSel && langSel.value) used.push(langSel.value);
        });
        return used;
    }

    function getCookie(name) {
        var m = document.cookie.match(new RegExp('(?:^|;\\s*)' + name + '=([^;]*)'));
        return m ? decodeURIComponent(m[1]) : null;
    }

    function injectLockStyles() {
        if (document.getElementById('alert-info-translation-styles')) return;
        var style = document.createElement('style');
        style.id = 'alert-info-translation-styles';
        style.textContent = [
            '.alert-info-translation input[readonly]:not([type="hidden"]) {',
            '  opacity: 0.6; cursor: not-allowed; background: #f5f5f5;',
            '}',
            '.alert-info-translation .alert-info-locked-stream {',
            '  opacity: 0.6; pointer-events: none; user-select: none;',
            '}',
            '.alert-info-translation select.alert-info-locked-select {',
            '  opacity: 0.6; pointer-events: none; cursor: not-allowed;',
            '}',
            '.alert-info-translation textarea[readonly] {',
            '  opacity: 0.6; cursor: not-allowed; background: #f5f5f5;',
            '}',
        ].join('\n');
        document.head.appendChild(style);
    }

    function lockTranslatedBlock(block) {
        injectLockStyles();
        block.classList.add('alert-info-translation');
        // Remove any translate button that was added before locking (timing race with MutationObserver).
        var earlyBtn = block.querySelector('.alert-info-translate-btn');
        if (earlyBtn) earlyBtn.remove();
        markBlockLocked(getBlockId(block));

        block.querySelectorAll('input:not([type="hidden"]), textarea').forEach(function (el) {
            if (!el.name) return;
            var isEditable = TRANSLATABLE_FIELDS.some(function (f) { return el.name.endsWith(f); });
            if (!isEditable) el.setAttribute('readonly', '');
        });

        block.querySelectorAll('select').forEach(function (el) {
            if (!el.name) return;
            var isEditable = TRANSLATABLE_FIELDS.some(function (f) { return el.name.endsWith(f); });
            if (!isEditable) el.classList.add('alert-info-locked-select');
        });

        block.querySelectorAll('[data-streamfield-stream-container]').forEach(function (container) {
            container.classList.add('alert-info-locked-stream');
            container.querySelectorAll('[data-streamfield-action]').forEach(function (btn) {
                btn.style.display = 'none';
            });
            container.querySelectorAll('.c-sf-add-button').forEach(function (btn) {
                btn.style.display = 'none';
            });
        });
    }

    function showLanguageModal(options, onSelect) {
        var overlay = document.createElement('div');
        overlay.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.5);z-index:9999;display:flex;align-items:center;justify-content:center;';

        var modal = document.createElement('div');
        modal.style.cssText = 'background:#fff;border-radius:6px;padding:24px;min-width:320px;max-width:420px;box-shadow:0 4px 24px rgba(0,0,0,0.3);font-family:inherit;';

        var title = document.createElement('h3');
        title.textContent = 'Translate to which language?';
        title.style.cssText = 'margin:0 0 16px;font-size:16px;font-weight:600;';
        modal.appendChild(title);

        var select = document.createElement('select');
        select.style.cssText = 'width:100%;padding:8px 10px;margin-bottom:20px;border:1px solid #ccc;border-radius:4px;font-size:14px;box-sizing:border-box;';

        var blankOpt = document.createElement('option');
        blankOpt.value = '';
        blankOpt.textContent = '— Select a language —';
        select.appendChild(blankOpt);

        options.forEach(function (o) {
            var opt = document.createElement('option');
            opt.value = o.value;
            opt.textContent = o.label + ' (' + o.value + ')';
            select.appendChild(opt);
        });
        modal.appendChild(select);

        var btnRow = document.createElement('div');
        btnRow.style.cssText = 'display:flex;justify-content:flex-end;gap:8px;';

        var cancelBtn = document.createElement('button');
        cancelBtn.type = 'button';
        cancelBtn.textContent = 'Cancel';
        cancelBtn.className = 'button button-secondary';
        cancelBtn.style.cssText = 'margin:0;';

        var okBtn = document.createElement('button');
        okBtn.type = 'button';
        okBtn.textContent = 'Translate';
        okBtn.className = 'button';
        okBtn.style.cssText = 'margin:0;';

        function close() {
            document.body.removeChild(overlay);
            document.removeEventListener('keydown', onKeyDown);
        }

        function onKeyDown(e) { if (e.key === 'Escape') close(); }
        document.addEventListener('keydown', onKeyDown);

        overlay.onclick = function (e) { if (e.target === overlay) close(); };
        cancelBtn.onclick = close;

        okBtn.onclick = function () {
            var val = select.value;
            if (!val) { select.style.borderColor = '#e5212a'; return; }
            close();
            onSelect(val);
        };

        btnRow.appendChild(cancelBtn);
        btnRow.appendChild(okBtn);
        modal.appendChild(btnRow);
        overlay.appendChild(modal);
        document.body.appendChild(overlay);
        select.focus();
    }

    // Clears changedFields once no translated blocks still have a pending update button.
    function checkAndClearChangedFields(sourceBlock) {
        var container = sourceBlock.closest('[data-streamfield-stream-container]');
        if (!container) return;
        var anyPending = getTranslatedBlocksInContainer(container).some(function (b) {
            return !!b.querySelector('.alert-info-update-btn');
        });
        if (!anyPending) sourceChangedFields.set(sourceBlock, new Set());
    }

    function showUpdateTranslationButton(translatedBlock, sourceBlock) {
        if (translatedBlock.querySelector('.alert-info-update-btn')) return;

        var btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'button alert-info-update-btn';
        btn.style.cssText = 'margin:0 4px;';
        btn.textContent = 'Update Translation';

        btn.onclick = function () {
            var changedFields = sourceChangedFields.get(sourceBlock) || new Set();
            if (changedFields.size === 0) { btn.remove(); return; }

            // Collect only the changed field values from the source
            var textsToTranslate = {};
            sourceBlock.querySelectorAll('input:not([type="hidden"]), textarea').forEach(function (inp) {
                if (!inp.name || !inp.value.trim()) return;
                TRANSLATABLE_FIELDS.forEach(function (f) {
                    if (inp.name.endsWith(f) && changedFields.has(f)) {
                        textsToTranslate[f] = inp.value;
                    }
                });
            });

            var sourceLangSel = sourceBlock.querySelector('select[name$="language"]');
            var sourceLanguage = sourceLangSel ? sourceLangSel.value : 'auto';
            var targetLangSel = translatedBlock.querySelector('select[name$="language"]');
            var targetLanguage = targetLangSel ? targetLangSel.value : '';

            if (!targetLanguage || Object.keys(textsToTranslate).length === 0) {
                btn.remove();
                checkAndClearChangedFields(sourceBlock);
                return;
            }

            btn.textContent = 'Updating…';
            btn.disabled = true;

            fetch(ADMIN_PREFIX + '/cap/translate-text/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken') || '',
                },
                body: JSON.stringify({
                    texts: textsToTranslate,
                    target_language: targetLanguage,
                    source_language: sourceLanguage || 'auto',
                }),
            }).then(function (r) {
                if (!r.ok) return r.text().then(function (body) {
                    throw new Error('Server error ' + r.status + ': ' + body.slice(0, 200));
                });
                return r.json();
            }).then(function (data) {
                var translated = (data && data.translated) || {};
                translatedBlock.querySelectorAll('input:not([type="hidden"]), textarea').forEach(function (inp) {
                    if (!inp.name) return;
                    TRANSLATABLE_FIELDS.forEach(function (f) {
                        if (inp.name.endsWith(f) && translated[f]) {
                            inp.value = translated[f];
                            inp.dispatchEvent(new Event('input', { bubbles: true }));
                            inp.dispatchEvent(new Event('change', { bubbles: true }));
                        }
                    });
                });
                btn.remove();
                checkAndClearChangedFields(sourceBlock);
            }).catch(function (err) {
                console.error('[alert_info] Update translation error:', err);
                alert('Update translation failed: ' + err.message);
                btn.textContent = 'Update Translation';
                btn.disabled = false;
            });
        };

        var controls = translatedBlock.querySelector('[data-panel-controls]');
        if (controls) {
            controls.appendChild(btn);
        } else {
            translatedBlock.insertBefore(btn, translatedBlock.firstChild);
        }
    }

    // Attach a single delegated listener on the source block so we catch all translatable field changes.
    function attachSourceChangeListeners(sourceBlock) {
        if (sourceBlock._alertInfoListenersAttached) return;
        sourceBlock._alertInfoListenersAttached = true;

        sourceBlock.addEventListener('change', function (e) {
            // Guard: if this block was subsequently locked (became a translation), ignore.
            if (isTranslatedBlock(sourceBlock)) return;

            var inp = e.target;
            if (!inp || !inp.name) return;

            var fieldName = null;
            TRANSLATABLE_FIELDS.forEach(function (f) {
                if (inp.name.endsWith(f)) fieldName = f;
            });
            if (!fieldName) return;

            var container = sourceBlock.closest('[data-streamfield-stream-container]');
            if (!container) return;
            var translatedBlocks = getTranslatedBlocksInContainer(container);
            if (translatedBlocks.length === 0) return;

            var changed = sourceChangedFields.get(sourceBlock) || new Set();
            changed.add(fieldName);
            sourceChangedFields.set(sourceBlock, changed);

            translatedBlocks.forEach(function (tb) {
                showUpdateTranslationButton(tb, sourceBlock);
            });
        });
    }

    function decorateBlock(block) {
        var typeInput = block.querySelector('input[name$="-type"]');
        if (!typeInput || typeInput.value !== 'alert_info') return;

        // Restore lock state persisted from a previous session
        var blockId = getBlockId(block);
        if (blockId && getLockedIds().indexOf(blockId) !== -1) {
            lockTranslatedBlock(block);
        }

        var dupBtn = block.querySelector('[data-streamfield-action="DUPLICATE"]');
        if (dupBtn) dupBtn.style.display = 'none';

        var streamContainer = block.closest('[data-streamfield-stream-container]');
        if (streamContainer) {
            streamContainer.querySelectorAll('.c-sf-add-button').forEach(function (b) {
                // Only hide add buttons that belong to this top-level stream, not those
                // nested inside an alert_info block's own sub-streams (area, resource, etc.).
                var parentBlock = b.closest('[data-streamfield-child]');
                if (!parentBlock || !streamContainer.contains(parentBlock)) {
                    b.style.display = 'none';
                }
            });
        }

        // Translated blocks get no translate button — only the source does.
        if (isTranslatedBlock(block)) return;

        if (block.querySelector('.alert-info-translate-btn')) return;

        // Source block: attach change listeners for "Update Translation" propagation.
        attachSourceChangeListeners(block);

        var btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'button button--icon text-replace white alert-info-translate-btn';
        btn.setAttribute('data-streamfield-action', 'TRANSLATE');
        btn.title = 'Translate';
        btn.innerHTML = '<svg class="icon icon-site" aria-hidden="true"><use href="#icon-site"></use></svg>Translate';

        btn.onclick = function () {
            var languageSelect = block.querySelector('select[name$="language"]');
            if (!languageSelect) { alert("Language field not found"); return; }

            var container = block.closest('[data-streamfield-stream-container]');
            if (!container) return;

            var currentLanguage = languageSelect.value;

            // Exclude source language and already-translated languages from the options.
            var usedLanguages = getUsedLanguages(container);
            if (currentLanguage && usedLanguages.indexOf(currentLanguage) === -1) {
                usedLanguages.push(currentLanguage);
            }

            var options = [];
            for (var i = 0; i < languageSelect.options.length; i++) {
                var opt = languageSelect.options[i];
                if (!opt.value) continue;
                if (usedLanguages.indexOf(opt.value) !== -1) continue;
                options.push({ value: opt.value, label: opt.text });
            }

            if (options.length === 0) {
                alert('All available languages have already been translated.');
                return;
            }

            showLanguageModal(options, function (selectedLanguage) {

                var textsToTranslate = {};
                block.querySelectorAll('input:not([type="hidden"]), textarea').forEach(function (inp) {
                    if (!inp.name || !inp.value.trim()) return;
                    TRANSLATABLE_FIELDS.forEach(function (f) {
                        if (inp.name.endsWith(f)) textsToTranslate[f] = inp.value;
                    });
                });

                var translatePromise = Object.keys(textsToTranslate).length > 0
                    ? fetch(ADMIN_PREFIX + '/cap/translate-text/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCookie('csrftoken') || '',
                        },
                        body: JSON.stringify({
                            texts: textsToTranslate,
                            target_language: selectedLanguage,
                            source_language: currentLanguage || 'auto',
                        }),
                    }).then(function (r) {
                        if (!r.ok) return r.text().then(function (body) {
                            throw new Error('Server error ' + r.status + ': ' + body.slice(0, 200));
                        });
                        return r.json();
                    })
                    : Promise.resolve({ translated: {} });

                if (!dupBtn) { alert("Duplicate button not found — cannot translate"); return; }

                var beforeBlocks = getAlertInfoBlocks(container);

                var newBlockPromise = new Promise(function (resolve, reject) {
                    var attempts = 0;
                    function check() {
                        var afterBlocks = getAlertInfoBlocks(container);
                        for (var i = 0; i < afterBlocks.length; i++) {
                            if (beforeBlocks.indexOf(afterBlocks[i]) === -1) {
                                var found = afterBlocks[i];
                                // Pre-emptively mark as a translation so decorateBlock (which may
                                // have already run via MutationObserver) cannot treat it as a source.
                                found.classList.add('alert-info-translation');
                                var earlyBtn = found.querySelector('.alert-info-translate-btn');
                                if (earlyBtn) earlyBtn.remove();
                                return resolve(found);
                            }
                        }
                        if (++attempts < 30) setTimeout(check, 100);
                        else reject(new Error('Duplicated block did not appear in time'));
                    }
                    setTimeout(check, 50);
                });

                dupBtn.click();

                Promise.all([translatePromise, newBlockPromise]).then(function (results) {
                    var data = results[0];
                    var newBlock = results[1];
                    var translated = (data && data.translated) || {};

                    if (Object.keys(translated).length === 0) {
                        console.warn('[alert_info] Translation API returned no translated fields. Response:', data);
                    }

                    // Lock first so that change events fired during field updates below do not
                    // trigger the spurious "Update Translation" listener that decorateBlock may
                    // have attached when the block briefly appeared unlocked.
                    lockTranslatedBlock(newBlock);

                    newBlock.querySelectorAll('input:not([type="hidden"]), textarea').forEach(function (inp) {
                        if (!inp.name) return;
                        TRANSLATABLE_FIELDS.forEach(function (f) {
                            if (inp.name.endsWith(f) && translated[f]) {
                                inp.value = translated[f];
                                inp.dispatchEvent(new Event('input', { bubbles: true }));
                                inp.dispatchEvent(new Event('change', { bubbles: true }));
                            }
                        });
                    });

                    var langSelect = newBlock.querySelector('select[name$="language"]');
                    if (langSelect) {
                        langSelect.value = selectedLanguage;
                        langSelect.dispatchEvent(new Event('change', { bubbles: true }));
                        langSelect.focus();
                    }

                }).catch(function (err) {
                    console.error('[alert_info] Translation error:', err);
                    alert('Translation failed: ' + err.message);
                });

            }); // end showLanguageModal callback
        };

        var controls = block.querySelector('[data-panel-controls]');
        if (controls) {
            if (dupBtn) {
                dupBtn.parentNode.insertBefore(btn, dupBtn);
            } else {
                controls.appendChild(btn);
            }
        }
    }

    function scanAllBlocks() {
        document.querySelectorAll('[data-streamfield-child]').forEach(decorateBlock);
    }

    var observer = new MutationObserver(function (mutations) {
        for (var i = 0; i < mutations.length; i++) {
            var added = mutations[i].addedNodes;
            for (var j = 0; j < added.length; j++) {
                var node = added[j];
                if (node.nodeType !== 1) continue;
                if (node.matches && node.matches('[data-streamfield-child]')) decorateBlock(node);
                if (node.querySelectorAll) node.querySelectorAll('[data-streamfield-child]').forEach(decorateBlock);
            }
        }
        scanAllBlocks();
    });

    function startObserver() {
        observer.observe(document.body, { childList: true, subtree: true });
        scanAllBlocks();
    }

    if (document.body) {
        startObserver();
    } else {
        document.addEventListener('DOMContentLoaded', startObserver);
    }
})();
