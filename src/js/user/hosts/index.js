function init() {
    // TODO: replace functionality with form[data-select-current-timezone]
    const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
    const option = document.querySelector(
        `#timezone option[value="${timezone}"]`
    );
    if (option) option.selected = true;
}

init();
