function init() {
    const form = document.querySelector('form[data-edit-form]');
    const nameInput = form.querySelector('#edit-name');
    const statusInput = form.querySelector('#edit-status');
    const machineIdInput = form.querySelector('#edit-machine_id');
    const hardwareInput = form.querySelector('#edit-hardware');
    const providerInput = form.querySelector('#edit-provider');

    const editButtons = document.querySelectorAll('button[data-edit]');
    editButtons.forEach(button => {
        button.addEventListener('click', () => {
            const row = button.closest('tr');
            const name = row.querySelector('[data-name]')?.textContent.trim();
            const status = row
                .querySelector('[data-status]')
                ?.textContent.trim()
                .toLowerCase();
            const machineId = row
                .querySelector('[data-machine-id]')
                ?.textContent.trim();
            const hardware = row
                .querySelector('[data-hardware]')
                ?.textContent.trim();
            const provider = row
                .querySelector('[data-provider]')
                ?.textContent.trim();

            form.closest('section').classList.remove('hidden');
            form.action = button.dataset.edit;
            nameInput.value = name;
            statusInput.focus();
            statusInput.value = status;
            machineIdInput.value = machineId;
            hardwareInput.value = hardware;
            providerInput.value = provider;
        });
    });
}

init();
