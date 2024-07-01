export function initCookies() {
    const inTenYears = new Date();
    inTenYears.setTime(inTenYears.getTime() + 10 * 365 * 24 * 60 * 60 * 1000); // Ten years in milliseconds

    const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
    document.cookie = `timezone=${timezone}; expires=${inTenYears.toUTCString()}; path=/;`;
}
