// Шпаргалка курса: правка (✎) и удаление (✕) заметки на месте.

import { apiRequest } from '../api.js';
import { NoteEditor } from '../note-editor.js';

const template = document.getElementById('note-editor-template');

function updateGroupCount(group) {
  const count = group.querySelectorAll('[data-note-id]').length;
  if (count === 0) {
    group.remove();
  } else {
    group.querySelector('[data-group-count]').textContent = count;
  }
}

function startEdit(note) {
  if (note.querySelector('[data-note-editor]')) return;
  const body = note.querySelector('[data-note-body]');
  const title = note.querySelector('[data-note-title]');
  const fragment = template.content.cloneNode(true);
  const root = fragment.querySelector('[data-note-editor]');
  body.hidden = true;
  body.after(fragment);
  note.open = true;

  const close = () => {
    root.remove();
    body.hidden = false;
  };
  const editor = new NoteEditor(root, {
    noteId: note.dataset.noteId,
    onCancel: close,
    onSaved: (saved) => {
      title.textContent = saved.title;
      body.innerHTML = saved.body_html;   // уже очищен сервером
      close();
    },
  });
  editor.fill(title.textContent, body.innerHTML);
  editor.title.focus();
}

async function remove(note) {
  const title = note.querySelector('[data-note-title]').textContent;
  if (!window.confirm(`Удалить заметку «${title}»?`)) return;
  const response = await apiRequest('DELETE', `${template.content.querySelector('[data-note-editor]').dataset.api}${note.dataset.noteId}/`);
  if (response.ok) {
    const group = note.closest('[data-sheet-group]');
    note.remove();
    updateGroupCount(group);
  }
}

document.addEventListener('click', (event) => {
  const button = event.target.closest('[data-note-edit], [data-note-delete]');
  if (!button) return;
  event.preventDefault();   // кнопка внутри <details> — не сворачивать заметку
  const note = button.closest('[data-note-id]');
  if (button.hasAttribute('data-note-edit')) startEdit(note);
  else remove(note);
});
