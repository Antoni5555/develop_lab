// Вкладки: в макете их переключали radio-кнопки на CSS, в проекте — этот скрипт.
// Разметка: [data-tabs] > .tabs > button.tab[data-tab="id"] + панели [data-panel="id"].

for (const tabset of document.querySelectorAll('[data-tabs]')) {
  const buttons = tabset.querySelectorAll('[data-tab]');
  const panels = tabset.querySelectorAll('[data-panel]');

  const select = (id) => {
    for (const button of buttons) {
      const active = button.dataset.tab === id;
      button.classList.toggle('tab--active', active);
      button.setAttribute('aria-selected', active);
    }
    for (const panel of panels) panel.hidden = panel.dataset.panel !== id;
  };

  for (const button of buttons) {
    button.addEventListener('click', () => select(button.dataset.tab));
  }
  select(buttons[0].dataset.tab);
}
