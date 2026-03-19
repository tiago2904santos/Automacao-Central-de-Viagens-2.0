document.addEventListener('DOMContentLoaded', function() {
    var root = document.querySelector('[data-oficios-view-root]');
    if (!root) {
        return;
    }

    var storageKey = 'central-viagens.oficios.view-mode';
    var allowedModes = { rich: true, basic: true };
    var buttons = Array.prototype.slice.call(root.querySelectorAll('[data-oficios-view-toggle]'));

    function applyMode(mode, persist) {
        var nextMode = allowedModes[mode] ? mode : 'rich';
        root.setAttribute('data-view-mode', nextMode);
        buttons.forEach(function(button) {
            var isActive = button.getAttribute('data-oficios-view-toggle') === nextMode;
            button.classList.toggle('is-active', isActive);
            button.setAttribute('aria-pressed', isActive ? 'true' : 'false');
        });
        if (persist) {
            window.localStorage.setItem(storageKey, nextMode);
        }
    }

    var storedMode = window.localStorage.getItem(storageKey);
    applyMode(storedMode, false);

    buttons.forEach(function(button) {
        button.addEventListener('click', function() {
            applyMode(button.getAttribute('data-oficios-view-toggle'), true);
        });
    });

    var filtersForm = root.querySelector('[data-oficios-filters-form]');
    if (!filtersForm) {
        return;
    }

    var autoFields = Array.prototype.slice.call(filtersForm.querySelectorAll('[data-oficios-autosubmit]'));
    var submitDelay = 280;
    var timerId = null;

    function submitFilters() {
        if (timerId) {
            window.clearTimeout(timerId);
            timerId = null;
        }
        filtersForm.submit();
    }

    function scheduleSubmit(delay) {
        if (timerId) {
            window.clearTimeout(timerId);
        }
        timerId = window.setTimeout(submitFilters, delay);
    }

    autoFields.forEach(function(field) {
        var tagName = (field.tagName || '').toLowerCase();
        var type = (field.getAttribute('type') || '').toLowerCase();
        if (tagName === 'input' && (type === 'text' || type === 'search')) {
            field.addEventListener('input', function() {
                scheduleSubmit(submitDelay);
            });
            field.addEventListener('keydown', function(event) {
                if (event.key === 'Enter') {
                    event.preventDefault();
                    submitFilters();
                }
            });
            return;
        }

        field.addEventListener('change', function() {
            scheduleSubmit(40);
        });
    });
});
