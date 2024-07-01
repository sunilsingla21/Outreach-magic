export function initIframes() {
    document.querySelectorAll('iframe[data-src]').forEach(iframe => {
        iframe.src = iframe.dataset.src;
        delete iframe.dataset.src;
    });
}
