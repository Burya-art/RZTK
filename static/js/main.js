document.querySelectorAll('.save-scroll').forEach(button => {
    button.addEventListener('click', () => {
        sessionStorage.setItem('scrollPosition', window.scrollY);
    });
});