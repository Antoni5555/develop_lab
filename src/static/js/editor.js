// Редактор кода на обычном <textarea>: номера строк, Tab, автоотступ, Ctrl+Enter.
// Без библиотек: полноценный редактор (CodeMirror) весит сотни КБ и требует сборщика.
//
// Разметка (как в макете):
//   <div class="editor">
//     <div class="editor__gutter" aria-hidden="true"></div>
//     <textarea class="editor__code" spellcheck="false"></textarea>
//   </div>

const INDENT = '    ';

export class CodeEditor {
  /**
   * @param {HTMLElement} root — элемент .editor
   * @param {object} options — { onRun: функция для Ctrl+Enter, onChange: при каждом вводе }
   */
  constructor(root, { onRun = () => {}, onChange = () => {} } = {}) {
    this.textarea = root.querySelector('.editor__code');
    this.gutter = root.querySelector('.editor__gutter');
    this.onRun = onRun;
    this.onChange = onChange;

    this.textarea.addEventListener('input', () => this.changed());
    this.textarea.addEventListener('keydown', (event) => this.keydown(event));
    this.textarea.addEventListener('scroll', () => {
      this.gutter.scrollTop = this.textarea.scrollTop;
    });
    this.updateGutter();
  }

  get value() {
    return this.textarea.value;
  }

  set value(text) {
    this.textarea.value = text;
    this.updateGutter();
  }

  changed() {
    this.updateGutter();
    this.onChange(this.value);
  }

  updateGutter() {
    const lines = this.value.split('\n').length;
    this.gutter.textContent = Array.from({ length: lines }, (_, i) => i + 1).join('\n');
  }

  /** Вставить текст на место выделения так, чтобы работала отмена (Ctrl+Z). */
  insert(text) {
    document.execCommand('insertText', false, text);
  }

  keydown(event) {
    if (event.key === 'Enter' && (event.ctrlKey || event.metaKey)) {
      event.preventDefault();
      this.onRun();
      return;
    }
    if (event.key === 'Tab' && !event.shiftKey) {
      event.preventDefault();
      this.insert(INDENT);
      return;
    }
    if (event.key === 'Enter') {
      // Новая строка с тем же отступом; после «:» — на уровень глубже, как в IDE
      const { selectionStart, value } = this.textarea;
      const lineStart = value.lastIndexOf('\n', selectionStart - 1) + 1;
      const line = value.slice(lineStart, selectionStart);
      let indent = line.match(/^\s*/)[0];
      if (line.trimEnd().endsWith(':')) indent += INDENT;
      event.preventDefault();
      this.insert('\n' + indent);
    }
  }
}
