// Переключатель темы: кнопка [data-theme-toggle] в шапке.
// Выбор хранится в localStorage; пока пользователь не выбрал — тема как в системе.
// Сохранённую тему ставит маленький скрипт в <head> (base.html), ещё до отрисовки.

const root = document.documentElement;
const systemDark = window.matchMedia('(prefers-color-scheme: dark)');

function currentTheme() {
  return root.dataset.theme || (systemDark.matches ? 'dark' : 'light');
}

function toggleTheme() {
  const next = currentTheme() === 'dark' ? 'light' : 'dark';
  root.dataset.theme = next;
  try {
    localStorage.setItem('theme', next);
  } catch (e) {
    // localStorage недоступен (приватный режим) — тема сработает до перезагрузки
  }
}

document.querySelectorAll('[data-theme-toggle]').forEach((button) => {
  button.addEventListener('click', toggleTheme);
});
