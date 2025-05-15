document.addEventListener('DOMContentLoaded', () => {
    const themeToggle = document.getElementById('theme-toggle');
    const htmlElement = document.documentElement;
    const iconPath   = '/static/assets'; // или ваш путь к статике

    // Функция обновления иконки
    function updateIcon(theme) {
        // предполагаем, что у вас лежат theme-light.svg и theme-dark.svg
        themeToggle.src = `${iconPath}/theme-${theme}.svg`;
    }

    // Функция инициализации темы
    function initTheme() {
        const savedTheme = localStorage.getItem('theme');
        const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

        const initialTheme = savedTheme || (systemDark ? 'dark' : 'light');
        htmlElement.setAttribute('data-theme', initialTheme);
        updateIcon(initialTheme);
    }

    // Функция переключения темы
    function toggleTheme() {
        const currentTheme = htmlElement.getAttribute('data-theme');
        const newTheme     = currentTheme === 'dark' ? 'light' : 'dark';

        htmlElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        updateIcon(newTheme);

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
            const newSysTheme = e.matches ? 'dark' : 'light';
            htmlElement.setAttribute('data-theme', newSysTheme);
            updateIcon(newSysTheme);
        }
    });
});
