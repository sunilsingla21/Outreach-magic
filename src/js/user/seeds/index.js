const form = document.querySelector('#new-batch-form');

const desiredTotalInput = form.querySelector('#desired_total');
const notEnoughText = form.querySelector('[data-not-enough]');

let maxExceeded = false;

const generateTotalInput = form.querySelector('#generate_total');
const hostSettingsLoading = form.querySelector('[data-host-settings-loading]');
const hostSettingsContainer = form.querySelector('[data-host-settings-fields]');
const hostSelect = form.querySelector('#host');
const allInputs = form.querySelectorAll(':is(input, button, select)');
const maxExceededText = form.querySelector('[data-max-exceeded]');

function updateEspValues() {
    const desiredTotal = parseInt(desiredTotalInput.value);
    if (!desiredTotal) return;
    const remaining = autoFillFieldsEvenly(desiredTotal);
    if (remaining) {
        notEnoughText.classList.remove('hidden');
    } else {
        notEnoughText.classList.add('hidden');
    }
    updateTotal();
}

function updateTotal() {
    const total = [...form.querySelectorAll('[data-esp-fields] input')]
        .map(field => parseInt(field.value) || 0)
        .reduce((total, value) => value + total, 0);

    maxExceeded = total > parseInt(desiredTotalInput.max);
    maxExceededText.classList.toggle('hidden', !maxExceeded);
    generateTotalInput.value = total;
}

function addListenerForEspInputs() {
    form.querySelectorAll('[data-esp-fields] input').forEach(input =>
        input.addEventListener('input', updateTotal)
    );
}

function autoFillFieldsEvenly(total) {
    // Sort fields based on their max values in descending order to prioritize filling fields with more capacity
    let sortedFields = [
        ...form.querySelectorAll('[data-esp-fields] input'),
    ].sort((a, b) => {
        return parseInt(a.max) - parseInt(b.max);
    });

    // Initialize fields with current values set to 0
    let currentAllocation = sortedFields.map(field => ({
        field,
        max: parseInt(field.max),
        current: 0,
    }));
    let remainingTotal = total;
    let remainingFields = currentAllocation.length;

    // First pass: distribute evenly without exceeding max values
    while (remainingFields > 0 && remainingTotal > 0) {
        let evenDistribution = Math.floor(remainingTotal / remainingFields);

        for (let i = 0; i < currentAllocation.length; i++) {
            let field = currentAllocation[i];
            if (field.current < field.max) {
                let availableToFill = Math.min(
                    evenDistribution,
                    field.max - field.current
                );
                field.current += availableToFill;
                remainingTotal -= availableToFill;

                // If the field is filled to its max, decrease the count of remaining fields
                if (field.current === field.max) {
                    remainingFields--;
                }
            }
        }

        // Prevent infinite loop if total cannot be distributed
        if (evenDistribution === 0) break;
    }

    currentAllocation.forEach(({ field, current }) => (field.value = current));
    return remainingTotal > sortedFields.length;
}

desiredTotalInput.addEventListener('input', updateEspValues);

hostSelect.addEventListener('change', () => {
    hostSettingsLoading.classList.remove('hidden');
    hostSettingsContainer.classList.add('hidden');
    allInputs.forEach(input => {
        if (input.disabled) {
            input.dataset.prevDisabledState = input.disabled;
        } else {
            delete input.dataset.prevDisabledState;
        }
        input.disabled = true;
    });

    const hostSettingsUrl = form.dataset.hostSettings.replace(
        'hostId',
        hostSelect.value
    );
    fetch(hostSettingsUrl)
        .then(res => res.json())
        .then(data => {
            for (const key in data) {
                if (typeof data[key] === 'boolean') {
                    const checkbox = document.querySelector(`#${key}`);
                    checkbox.checked = data[key];
                } else if (Array.isArray(data[key])) {
                    document.querySelector(`#${key}`).value =
                        data[key].join('\n');
                }
            }
        })
        .catch(console.error)
        .finally(() => {
            hostSettingsLoading.classList.add('hidden');
            hostSettingsContainer.classList.remove('hidden');
            allInputs.forEach(
                input => (input.disabled = input.dataset.prevDisabledState)
            );
        });
});

addListenerForEspInputs();

form.addEventListener('submit', e => {
    if (maxExceeded) {
        e.preventDefault();
        maxExceededText.classList.remove('hidden');
    } else {
        maxExceededText.classList.add('hidden');
    }
});
