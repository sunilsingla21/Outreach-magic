function slideOut(li) {
    clearTimeout(li.dataset.timeout);
    li.classList.add('flash-slide-out');
    li.addEventListener(
        'animationend',
        () => {
            li.style.display = 'none';
        },
        { once: true }
    );
}

export function initFlashMessages() {
    const liCollection = document.querySelectorAll('.messages-list li');
    liCollection.forEach((li, index) => {
        li.style.setProperty(
            '--slide-in-delay',
            `${(liCollection.length - 1 - index) * 100}ms`
        );
        li.dataset.timeout = setTimeout(() => {
            slideOut(li);
        }, 15000);
        const closeButton = li.querySelector('button');
        li.addEventListener('click', () => closeButton.click());
        closeButton.addEventListener('click', e => {
            e.stopImmediatePropagation();
            slideOut(li);
        });
    });
}
