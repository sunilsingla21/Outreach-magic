const updateForm = document.querySelector('form[data-update]');
const updateButtons = document.querySelectorAll('button[data-update]');

function resetAnimations() {
    document
        .querySelectorAll('tr')
        .forEach(tr => tr.classList.remove('animate-pulse'));
}

updateButtons.forEach(button => {
    button.addEventListener('click', () => {
        resetAnimations();
        const row = button.closest('tr');
        row.classList.add('animate-pulse');
        const index = row.querySelector('[data-index]').textContent.trim();
        updateForm.reset();
        updateForm.querySelector('[data-index]').textContent = index;
        updateForm.action = button.dataset.update;
        updateForm.classList.remove('hidden');
        updateForm.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
});
