const main = document.querySelector('main');

document.querySelector('form').addEventListener('submit', async e => {
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
