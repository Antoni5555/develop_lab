// «Сообщить об ошибке»: выделили текст урока или задачи — рядом появляется кнопка,
// по ней — окно с цитатой и полем «Что не так?». Сообщение уходит в админку.
//
// Разметка — templates/common/_report_error.html; где можно выделять — [data-report-scope].
// Кнопка встаёт под выделением: над ним на телефоне появляется системное меню.

import { apiRequest } from './api.js';

// Как в apps/feedback/services/reports.py
const MAX_QUOTE = 500;
const MAX_CONTEXT = 1000;
// Блоки, текст которых уходит как «текст вокруг» — чтобы найти место в уроке
const BLOCKS = 'p, li, td, th, pre, h1, h2, h3, h4, blockquote, figcaption, summary';

const button = document.querySelector('[data-report-btn]');
const dialog = document.querySelector('[data-report-dialog]');
const form = dialog.querySelector('[data-report-form]');
const quoteBox = dialog.querySelector('[data-report-quote]');
const fields = dialog.querySelector('[data-report-fields]');   // нет у гостя
const comment = dialog.querySelector('textarea');
const error = dialog.querySelector('[data-report-error]');
const done = dialog.querySelector('[data-report-done]');
const sendButton = dialog.querySelector('[data-report-send]');

let picked = null;      // { quote, context } — то, что было выделено, когда показали кнопку
let pressing = false;   // палец или мышь на кнопке: выделение вот-вот пропадёт, кнопку не прячем

function elementOf(node) {
  return node.nodeType === Node.ELEMENT_NODE ? node : node.parentElement;
}

function readSelection() {
  const selection = document.getSelection();
  if (!selection || selection.isCollapsed || !selection.rangeCount) return null;
  const range = selection.getRangeAt(0);
  if (!elementOf(range.commonAncestorContainer)?.closest('[data-report-scope]')) return null;
  const quote = selection.toString().trim();
  if (!quote) return null;
  const block = elementOf(range.startContainer)?.closest(BLOCKS);
  const context = (block?.textContent ?? '').replace(/\s+/g, ' ').trim();
  return {
    range,
    quote: quote.length > MAX_QUOTE ? `${quote.slice(0, MAX_QUOTE - 1)}…` : quote,
    context: context.slice(0, MAX_CONTEXT),
  };
}

function placeButton(range) {
  const rects = range.getClientRects();
  const last = rects[rects.length - 1] ?? range.getBoundingClientRect();
  button.hidden = false;
  const width = button.offsetWidth;
  const left = Math.min(
    Math.max(last.right - width / 2, 8),
    document.documentElement.clientWidth - width - 8,
  );
  button.style.left = `${left + window.scrollX}px`;
  button.style.top = `${last.bottom + window.scrollY + 8}px`;
}

let timer;
document.addEventListener('selectionchange', () => {
  clearTimeout(timer);
  // Ждём, пока выделение «устоится»: иначе кнопка прыгает за мышью
  timer = setTimeout(() => {
    if (pressing || dialog.open) return;
    const selected = readSelection();
    picked = selected && { quote: selected.quote, context: selected.context };
    if (selected) placeButton(selected.range);
    else button.hidden = true;
  }, 200);
});

// preventDefault: иначе нажатие на кнопку снимет выделение раньше, чем сработает click
button.addEventListener('pointerdown', (event) => {
  event.preventDefault();
  pressing = true;
});
button.addEventListener('click', () => {
  pressing = false;
  if (picked) open(picked);
});

function open({ quote }) {
  button.hidden = true;
  quoteBox.textContent = quote;
  if (fields) {
    fields.hidden = false;
    done.hidden = true;
    error.hidden = true;
    comment.value = '';
  }
  document.getSelection().removeAllRanges();   // убираем системное меню выделения
  dialog.showModal();
  // Фокус — в поле комментария; у гостя поля нет — на само окно, а не на «×»
  (comment ?? dialog).focus();
}

dialog.querySelector('[data-report-close]').addEventListener('click', () => dialog.close());
// Клик по затемнению вокруг окна — закрыть
dialog.addEventListener('click', (event) => {
  if (event.target === dialog) dialog.close();
});

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  if (!fields || !picked) return;
  sendButton.disabled = true;
  error.hidden = true;
  try {
    const response = await apiRequest('POST', form.dataset.api, {
      source: form.dataset.source,
      quote: picked.quote,
      context: picked.context,
      comment: comment.value,
    });
    if (response.ok) {
      fields.hidden = true;
      done.hidden = false;
      return;
    }
    showError(response.status === 429
      ? 'Слишком много сообщений подряд. Попробуйте через час.'
      : 'Не получилось отправить. Обновите страницу и попробуйте ещё раз.');
  } catch {
    showError('Нет связи с сервером. Попробуйте ещё раз.');
  } finally {
    sendButton.disabled = false;
  }
});

function showError(text) {
  error.textContent = text;
  error.hidden = false;
}
