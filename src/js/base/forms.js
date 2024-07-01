const forms = document.querySelectorAll('form[data-custom-form]');
const timezoneForms = document.querySelectorAll(
    'form[data-select-current-timezone]'
);
const hostForms = document.querySelectorAll('form[data-host-form]');

function initForm(form) {
    form.addEventListener('submit', async e => {
        e.preventDefault();
        const formData = new FormData(form);
        const url = form.action;
        form.querySelectorAll('[data-hide]').forEach(elem =>
            elem.classList.add('hidden')
        );
        form.querySelector('.loading')?.classList.remove('hidden');

        await fetch(url, {
            method: form.dataset.method,
            body: formData,
        });
        if (form.dataset.afterSubmit === 'reload') {
            location.reload();
        }
    });
}

function initHostForm(form) {
    const autoCCActiveInput = form.querySelector('#auto_cc_active');
    const customMessageInput = form.querySelector(
        '#has_custom_auto_cc_message'
    );

    function checkInputs() {
        const hasToShow =
            autoCCActiveInput.checked && customMessageInput.checked;
        form.querySelector('[data-custom-message]').classList.toggle(
            'hidden',
            !hasToShow
        );
        form.querySelector('[data-auto-cc-active]').classList.toggle(
            'hidden',
            !autoCCActiveInput.checked
        );
    }
    autoCCActiveInput?.addEventListener('change', checkInputs);
    customMessageInput?.addEventListener('change', checkInputs);
}

export function initForms() {
    forms.forEach(form => {
        try {
            initForm(form);
        } catch (error) {
            console.error(`Error while initializing custom form: ${error}`);
        }
    });
    hostForms.forEach(form => {
        try {
            initHostForm(form);
        } catch (error) {
            console.error(`Error while initializing host form: ${error}`);
        }
    });
    timezoneForms.forEach(form => {
        const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
        const option = form.querySelector(`option[value="${timezone}"]`);
        if (option) option.selected = true;
    });
}
