function init() {
    const form = document.querySelector('form[data-edit-form]');
    const addressInput = form.querySelector('#account-address');
    const hostInput = form.querySelector('#host');
    const espInput = form.querySelector('#esp');

    const editButtons = document.querySelectorAll('button[data-edit]');
    editButtons.forEach(button => {
        button.addEventListener('click', () => {
            const row = button.closest('tr');
            const address = row
                .querySelector('[data-email]')
                ?.textContent.trim();
            const host = row.querySelector('[data-host]')?.dataset.host;
            const esp = row.querySelector('[data-esp]')?.textContent.trim();

            form.closest('section').classList.remove('hidden');
            form.action = button.dataset.edit;
            addressInput.value = address;
            hostInput.focus();
            hostInput.value = host;
            espInput.value = esp;
        });
    });
}

init();
