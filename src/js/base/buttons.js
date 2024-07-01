export function initButtons() {
    const buttons = document.querySelectorAll(
        ':is(button, .button)[data-confirm]'
    );
    buttons.forEach(button => {
        button.addEventListener('click', e => {
            if (!confirm(button.dataset.confirm)) e.preventDefault();
        });
    });

    const copyButtons = document.querySelectorAll('button[data-copy]');
    copyButtons.forEach(button => {
        button.addEventListener('click', () => {
            const copyableElement = document.querySelector(
                `[data-copyable="${button.dataset.copy}"]`
            );
            if (!copyableElement) {
                console.error(`No copyable element found for this button`);
                console.error(button);
                return;
            }
            navigator.clipboard.writeText(copyableElement.textContent.trim());

            const clipboard = button.querySelector('img[data-clipboard]');
            const tick = button.querySelector('img[data-tick]');
            clipboard.classList.add('hidden');
            tick.classList.remove('hidden');
            setTimeout(() => {
                clipboard.classList.remove('hidden');
                tick.classList.add('hidden');
            }, 4000);
        });
    });
}
