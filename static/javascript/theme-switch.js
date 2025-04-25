document.addEventListener('DOMContentLoaded', () => {
    const themeToggle = document.getElementById('theme-toggle');
    const htmlElement = document.documentElement;

    // Функция инициализации темы
    function initTheme() {
        const savedTheme = localStorage.getItem('theme');
        const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

        const initialTheme = savedTheme || (systemDark ? 'dark' : 'light');
        htmlElement.setAttribute('data-theme', initialTheme);
    }

    // Функция переключения темы
    function toggleTheme() {
        const currentTheme = htmlElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

        htmlElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);

        // Анимация иконки
        themeToggle.classList.add('theme-rotate');
        setTimeout(() => themeToggle.classList.remove('theme-rotate'), 300);
    }

    // Инициализация и обработчики
    initTheme();
    themeToggle.addEventListener('click', toggleTheme);

    // Синхронизация с системными настройками
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
        if (!localStorage.getItem('theme')) {
            htmlElement.setAttribute('data-theme', e.matches ? 'dark' : 'light');
        }
    });
});
