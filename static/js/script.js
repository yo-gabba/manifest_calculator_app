function showPage(pageId) {
    document.querySelectorAll('.page').forEach(page => {
    page.style.display = 'none';
    });
    document.getElementById(pageId).style.display = 'block';

    document.querySelectorAll('nav a').forEach(link => {
    link.classList.remove('active');
    });
    event.target.classList.add('active');
}

function addManifest() {
    alert("Open manifest form here!");
}
