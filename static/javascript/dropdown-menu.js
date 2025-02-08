document.addEventListener('DOMContentLoaded', function () {
    const dropdown = document.querySelector('.dropdown');
    const dropdownMenu = dropdown.querySelector('.dropdown-menu');

    dropdown.addEventListener('mouseenter', function () {
        dropdown.classList.add('show');
        dropdownMenu.style.height = dropdownMenu.scrollHeight + 'px';
    });

    dropdown.addEventListener('mouseleave', function () {
        dropdown.classList.remove('show');
        dropdownMenu.style.height = '0';
    });
});
