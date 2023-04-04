const accordion = (function () {
    const $accordion = $(".js-accordion");
    const $accordion_header = $accordion.find(".js-accordion-header");
    const $accordion_item = $(".js-accordion-item");

    // default settings
    const settings = {
        // animation speed
        speed: 400,

        // close all other accordion items if true
        oneOpen: false
    };

    return {
        // pass configurable object literal
        init: function ($settings) {
            $accordion_header.on("click", function () {
                accordion.toggle($(this));
            });

            $.extend(settings, $settings);

            // ensure only one accordion is active if oneOpen is true
            if (settings.oneOpen && $(".js-accordion-item.active").length > 1) {
                $(".js-accordion-item.active:not(:first)").removeClass("active");
            }

            // reveal the active accordion bodies
            $(".js-accordion-item.active")
                .find("> .js-accordion-body")
                .show();
        },
        toggle: function ($this) {
            if (
                settings.oneOpen &&
                $this[0] !=
                $this
                    .closest(".js-accordion")
                    .find("> .js-accordion-item.active > .js-accordion-header")[0]
            ) {
                $this
                    .closest(".js-accordion")
                    .find("> .js-accordion-item")
                    .removeClass("active")
                    .find(".js-accordion-body")
                    .slideUp();
            }
            // show/hide the clicked accordion item
            $this.closest(".js-accordion-item").toggleClass("active");
            $this
                .next()
                .stop()
                .slideToggle(settings.speed);
        }
    };
})();

const getParams = function (url) {
    const params = {};
    const parser = document.createElement('a');
    parser.href = url;
    const query = parser.search.substring(1);

    if (query) {
        const vars = query.split('&');

        for (let i = 0; i < vars.length; i++) {
            if (vars[i]) {
                const pair = vars[i].split('=');
                params[pair[0]] = decodeURIComponent(pair[1]);

            }
        }
    }
    return params
};

function markCheckboxesFromUrlParams(className, params = [], callback) {

    // take params and check appropriate checkboxes
    for (const param in params) {
        const split_param = params[param].split(',').filter(Boolean);

        const $filter = $(`.${className}.${param}`);

        $filter.each(function () {
            const $this = $(this);
            if (split_param.includes($this.val())) {
                $this.prop("checked", true)
            }
        });

        if (callback) {
            // pass params to callback
            callback(params)
        }
    }
}

function filterChangeListener(className, params = {}, callback) {

    const $filterInput = $(`.${className}`);


    $filterInput.on('click change', function (e) {

        const clicked = $(this);

        const nodeName = clicked.get(0).nodeName

        let changed = false
        let scrollToResults = true

        // If is input
        if (nodeName === 'INPUT') {
            if (e.type === 'change') {
                if (clicked.is(':checkbox')) {
                    const param = clicked.attr('name')
                    const value = clicked.val()
                    changed = true

                    if (clicked.is(':checked')) {
                        // add
                        if (params[param]) {
                            const param_values = params[param].split(',')
                            param_values.push(value)
                            params[param] = param_values.join(',')

                        } else {
                            params[param] = value
                        }
                    } else {
                        //remove
                        if (params[param]) {
                            const param_values = params[param].split(',')

                            const index = param_values.indexOf(value);

                            if (index !== -1) {
                                param_values.splice(index, 1);
                                params[param] = param_values.join(',')

                                if (!params[param]) {
                                    delete params[param]
                                }
                            }
                        }
                    }
                }
            }

        }

        // If is SELECT
        else if (nodeName === 'SELECT') {
            if (e.type === 'change') {
                const param = clicked.attr('name')
                params[param] = clicked.val()

                changed = true
                scrollToResults = false
            }
        }
        // If is button
        else if (nodeName === 'BUTTON' && clicked.attr('name') === 'view') {
            if (!clicked.hasClass('active')) {
                params['view'] = clicked.val()
            }
            changed = true
        }

        // if anything changed
        if (changed) {
            const url_params = urlParamsFromObject(params)

            if (callback) {
                callback(clicked, url_params, scrollToResults)
            }
        }
    });
}

function urlParamsFromObject(paramsObject, exclude = []) {

    return Object.keys(paramsObject).reduce(function (all, key) {
        const value = paramsObject[key]

        if (!exclude.includes(key)) {
            if (value) {
                if (all) {
                    all = all + `&${key}=${value}`
                } else {
                    all = `${key}=${value}`
                }
            }

        }
        return all
    }, '')
}