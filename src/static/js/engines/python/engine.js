// Движок Python для страницы: запускает Pyodide в Web Worker и общается с ним.
// Интерфейс как у всех движков тренажёров: init(), run(code), check(code, exercise), reset().
//
// Тайм-аут: если программа не ответила вовремя (бесконечный цикл), воркер
// останавливается и запускается заново — Pyodide второй раз берётся из кэша браузера.

const RUN_TIMEOUT = 2500;      // 2 секунды на программу + запас на передачу данных
const CHECK_TIMEOUT = 8000;    // проверка запускает код несколько раз (тесты с run())

export const TIMEOUT_MESSAGE = 'Программа не завершилась за 2 секунды — возможно, бесконечный цикл.';

export class PythonEngine {
  /**
   * @param {object} urls — { worker, runner, pyodide } (из data-атрибутов страницы)
   * @param {function} onStatus — 'loading' | 'ready' | 'busy' | 'failed'
   */
  constructor(urls, onStatus = () => {}) {
    this.urls = urls;
    this.onStatus = onStatus;
    this.worker = null;
    this.pending = new Map();
    this.nextId = 1;
    this.readyPromise = null;
  }

  init() {
    if (this.readyPromise) return this.readyPromise;
    this.onStatus('loading');

    const url = new URL(this.urls.worker, location.href);
    url.searchParams.set('pyodide', this.urls.pyodide);
    url.searchParams.set('runner', new URL(this.urls.runner, location.href).href);
    this.worker = new Worker(url, { type: 'module' });

    this.readyPromise = new Promise((resolve, reject) => {
      this.worker.onmessage = ({ data }) => {
        if (data.type === 'ready') {
          this.onStatus('ready');
          resolve();
        } else if (data.type === 'failed') {
          this.onStatus('failed');
          reject(new Error(data.error));
        } else {
          this.finish(data);
        }
      };
    });
    return this.readyPromise;
  }

  finish({ id, ok, result, error }) {
    const request = this.pending.get(id);
    if (!request) return;
    clearTimeout(request.timer);
    this.pending.delete(id);
    this.onStatus('ready');
    if (ok) request.resolve(result);
    else request.reject(new Error(error));
  }

  async request(action, data, timeout) {
    await this.init();
    this.onStatus('busy');
    const id = this.nextId++;
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        this.pending.delete(id);
        this.reset();
        resolve({ timedOut: true });
      }, timeout);
      this.pending.set(id, { resolve, reject, timer });
      this.worker.postMessage({ id, action, ...data });
    });
  }

  /** Запустить программу: { output, error } */
  run(code, inputs = '') {
    return this.request('run', { code, inputs }, RUN_TIMEOUT);
  }

  /** Проверить решение задачи по её типу (exercise — тесты, predict — ответ). */
  check(code, exercise) {
    if (exercise.type === 'predict') {
      return this.request('predict', { code: exercise.code, answer: code }, RUN_TIMEOUT);
    }
    return this.request('check', { code, task: exercise }, CHECK_TIMEOUT);
  }

  /** Остановить воркер и запустить заново (после зависания или по кнопке). */
  reset() {
    if (this.worker) this.worker.terminate();
    for (const request of this.pending.values()) clearTimeout(request.timer);
    this.pending.clear();
    this.readyPromise = null;
    this.worker = null;
    return this.init();
  }
}
