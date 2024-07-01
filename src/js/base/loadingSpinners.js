export function initLoadingSpinners() {
    document.querySelectorAll('.loading[data-for]').forEach(spinner => {
        const id = spinner.dataset.for;
        document.getElementById(id)?.addEventListener('load', e => {
            e.target.classList.remove('hidden');
            spinner.classList.add('hidden');
        });
    });
}
