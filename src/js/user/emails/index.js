function emoji(result) {
    if (result === undefined) {
        return '❓';
    } else if (result) {
        return '✅';
    } else {
        return '🚫';
    }
}

function lastUpdated(date) {
    if (!date) return 'This value has never been saved';
    return `Last updated: ${date}`;
}

function showButtons(row) {
    row.querySelector('[data-buttons]').classList.remove('hidden');
    row.querySelector('.loading').parentElement.classList.add('hidden');
}

function hideButtons(row) {
    row.querySelector('[data-buttons]').classList.add('hidden');
    row.querySelector('.loading').parentElement.classList.remove('hidden');
}

function init() {
    const newForm = document.querySelector('form[data-new-email]');
    newForm.querySelector('#add_google')?.addEventListener('click', () => {
        newForm.action = newForm.dataset.googleUrl;
    });
    newForm.querySelector('#add_microsoft')?.addEventListener('click', () => {
        newForm.action = newForm.dataset.microsoftUrl;
    });
    newForm.querySelector('#add_yahoo')?.addEventListener('click', () => {
        newForm.action = newForm.dataset.yahooUrl;
    });

    const deleteForms = document.querySelectorAll('form[data-delete-account]');
    deleteForms.forEach(form => {
        form.addEventListener('submit', () => {
            hideButtons(form.closest('tr'));
        });
    });

    const editForm = document.querySelector('form[data-edit-form]');
    const addressInput = editForm.querySelector('#account-address');
    const statusInput = editForm.querySelector('#status');
    const passwordInput = editForm.querySelector('#password');
    const twoFaInput = editForm.querySelector('#two_fa');
    const inboxPlacementInput = editForm.querySelector(
        '#inbox_placement_active'
    );
    const inboxEngagementInput = editForm.querySelector(
        '#inbox_engagement_active'
    );
    const placementAccountInput = editForm.querySelector(
        '#placement_account_active'
    );
    const engagementAccountInput = editForm.querySelector(
        '#engagement_account_active'
    );
    const inboxResetInput = editForm.querySelector('#inbox_reset');
    const relayAccountInput = editForm.querySelector('#relay_account');
    const vpsInput = editForm.querySelector('#vps');

    const editButtons = document.querySelectorAll('button[data-edit]');
    editButtons.forEach(button => {
        button.addEventListener('click', () => {
            const row = button.closest('tr');
            const address = row
                .querySelector('[data-email]')
                ?.textContent.trim();
            const status = row
                .querySelector('[data-status]')
                ?.textContent.trim();
            const inboxPlacement =
                row
                    .querySelector('[data-inbox-placement-active]')
                    ?.textContent.trim() === 'On';
            const inboxEngagement =
                row
                    .querySelector('[data-inbox-engagement-active]')
                    ?.textContent.trim() === 'On';
            const placementAccount =
                row
                    .querySelector('[data-placement-account-active]')
                    ?.textContent.trim() === 'On';
            const engagementAccount =
                row
                    .querySelector('[data-engagement-account-active]')
                    ?.textContent.trim() === 'On';
            const inboxReset =
                row.querySelector('[data-inbox-reset]')?.textContent.trim() ===
                'On';
            const relayAccount =
                row
                    .querySelector('[data-relay-account]')
                    ?.textContent.trim() === 'On';
            const vps = row.querySelector('[data-vps]')?.dataset.vps;
            const lastUpdatedPassword = row
                .querySelector('[data-last-updated-password]')
                ?.textContent.trim();
            const lastUpdated2fa = row
                .querySelector('[data-last-updated-2fa]')
                ?.textContent.trim();
            const engagementVia = row
                .querySelector('[data-engagement-via]')
                ?.textContent.trim();
            const engageViaRadioInput = editForm.querySelector(
                `[name="engagement_via"][value="${engagementVia}"]`
            );

            editForm.closest('section').classList.remove('hidden');
            editForm.action = button.dataset.edit;
            addressInput.value = address;
            statusInput.value = status;
            statusInput.focus();
            if (passwordInput) {
                passwordInput.placeholder = lastUpdated(lastUpdatedPassword);
            }
            if (twoFaInput) {
                twoFaInput.placeholder = lastUpdated(lastUpdated2fa);
            }
            if (engageViaRadioInput) {
                engageViaRadioInput.checked = true;
            }
            inboxPlacementInput.checked = inboxPlacement;
            inboxEngagementInput.checked = inboxEngagement;
            if (placementAccountInput) {
                placementAccountInput.checked = placementAccount;
            }
            if (engagementAccountInput) {
                engagementAccountInput.checked = engagementAccount;
            }
            if (inboxResetInput) {
                inboxResetInput.checked = inboxReset;
            }
            if (relayAccountInput) {
                relayAccountInput.checked = relayAccount;
            }
            if (vpsInput) {
                vpsInput.value = vps || 'none';
            }
        });
    });

    const testButtons = document.querySelectorAll('button[data-test]');
    testButtons.forEach(button => {
        const tr = button.closest('tr');
        button.addEventListener('click', async () => {
            hideButtons(tr);
            const response = await fetch(button.dataset.test, {
                method: 'post',
            });
            if (response.status >= 400) {
                alert('There was an error doing the tests. Please try again');
                return;
            }
            const data = await response.json();
            tr.querySelector('[data-smtp-result]').textContent = emoji(
                data.smtp
            );
            tr.querySelector('[data-imap-result]').textContent = emoji(
                data.imap
            );
            showButtons(tr);
        });
    });
}

init();
