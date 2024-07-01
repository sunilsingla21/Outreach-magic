const navbar = document.querySelector('nav');
const toggleNavbarCheckbox = navbar?.querySelector('#navbar-toggle');

function removeEventListeners() {
    document.removeEventListener('click', clickHandler);
    document.removeEventListener('keydown', clickHandler);
}

function addEventListeners() {
    document.addEventListener('click', clickHandler);
    document.addEventListener('keydown', clickHandler);
}

function clickHandler(e) {
    if (
        (e.type === 'click' && !navbar.contains(e.target)) || // Clicked outside of navbar
        (e.type === 'keydown' && e.keyCode === 27) // Pressed escape
    ) {
        toggleNavbarCheckbox.checked = false;
        removeEventListeners();
    }
}

export function initNavbar() {
    if (!navbar) return;

    toggleNavbarCheckbox.addEventListener('change', () => {
        removeEventListeners();
        if (!toggleNavbarCheckbox.checked) return;

        addEventListeners();
    });
}
