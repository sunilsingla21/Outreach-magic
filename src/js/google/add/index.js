function showSection(section) {
    main.classList.remove(...allSectionClasses);
    allSections.forEach(section => section.classList.add('hidden'));

    section.classList.remove('hidden');
    main.classList.add(...section.dataset.classes.split(' '));
}

const main = document.querySelector('main');

const enableImapSection = document.querySelector('section[data-enable-imap]');

const chooseConnectionTypeSection = document.querySelector(
    'section[data-choose-connection-type]'
);
const optionContainers = chooseConnectionTypeSection.querySelectorAll(
    '[data-option-container]'
);

const addAppSection = document.querySelector(
    'section[data-add-app-to-workspace]'
);

const addWithAppPasswordSection = document.querySelector(
    'section[data-add-with-app-password]'
);

const allSections = document.querySelectorAll('section');

const allSectionClasses = [...allSections]
    .map(section => section.dataset.classes.split(' '))
    .flat();

// Imap section
enableImapSection
    .querySelector('button[data-continue]')
    .addEventListener('click', () => {
        showSection(chooseConnectionTypeSection);
    });

// Choose connection type section
chooseConnectionTypeSection
    .querySelector('button[data-continue]')
    .addEventListener('click', () => {
        const selectedInput = document.querySelector(
            'input[name=connection_type]:checked'
        );
        if (!selectedInput) return;

        if (selectedInput.id === 'oauth') {
            showSection(addAppSection);
        } else if (selectedInput.id === 'app_password') {
            showSection(addWithAppPasswordSection);
        }
    });

chooseConnectionTypeSection
    .querySelector('button[data-back]')
    .addEventListener('click', () => {
        showSection(enableImapSection);
    });
optionContainers.forEach(container =>
    container.addEventListener('click', () => {
        const input = container.querySelector('input[type=radio]');
        input.click();
        input.focus();
    })
);

// Add app to workspace section
addAppSection
    .querySelector('button[data-back]')
    .addEventListener('click', () => {
        showSection(chooseConnectionTypeSection);
    });

// Add with App Password section
addWithAppPasswordSection
    .querySelector('button[data-back]')
    .addEventListener('click', () => {
        showSection(chooseConnectionTypeSection);
    });

addWithAppPasswordSection
    .querySelector('form')
    .addEventListener('submit', async e => {
        e.preventDefault();
        const formData = new FormData(e.target);
        const response = await fetch(e.target.action, {
            body: formData,
            method: 'post',
        });
        if (response.status >= 400) {
            const data = await response.json();
            alert(data.message);
            return;
        }
        location.href = main.dataset.success;
    });
