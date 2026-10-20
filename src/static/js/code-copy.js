// Кнопка «Копировать» у блоков кода в уроке (.code-block__copy).

const LABEL = 'Копировать';

document.addEventListener('click', async (event) => {
  const button = event.target.closest('.code-block__copy');
  if (!button) return;

  const code = button.closest('.code-block').querySelector('pre').innerText;
  try {
    await navigator.clipboard.writeText(code);
    button.textContent = 'Скопировано';
  } catch (e) {
    button.textContent = 'Не удалось';
  }
  setTimeout(() => { button.textContent = LABEL; }, 1500);
});
