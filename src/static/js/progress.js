// Прогресс по задачам и урокам.
//   Гость: ключи решённых задач и открытых уроков — в localStorage; отметки в программе
//          курса и на задаче рисует этот скрипт (сервер прогресс гостя не знает).
//   Вошедший: отметки ставит сервер; задачу «решено» отправляем в API. Если в браузере
//          остался прогресс гостя (вошёл после решения задач) — один раз переносим его.
// Ключ задачи: «python/first-steps/strings/sku-parts», урока: «python/first-steps/strings».

const body = document.body;
const isAuthenticated = body.dataset.auth === '1';
const STORE_KEY = 'progress:v1';

function load() {
  try {
    const data = JSON.parse(localStorage.getItem(STORE_KEY));
    return { solved: data?.solved ?? [], viewed: data?.viewed ?? [] };
  } catch (e) {
    return { solved: [], viewed: [] };
  }
}

function save(data) {
  try {
    localStorage.setItem(STORE_KEY, JSON.stringify(data));
  } catch (e) {
    // localStorage недоступен (приватный режим) — прогресс гостя просто не сохранится
  }
}

function post(url, payload) {
  return fetch(url, {
    method: 'POST',
    credentials: 'same-origin',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content,
    },
    body: JSON.stringify(payload),
  });
}

function remember(list, key) {
  const data = load();
  if (!data[list].includes(key)) {
    data[list].push(key);
    save(data);
  }
}

/** Отметки в программе курса и на задаче — по ключам из localStorage (для гостя). */
function showGuestProgress() {
  const { solved, viewed } = load();
  for (const item of document.querySelectorAll('[data-exercise-key]')) {
    if (solved.includes(item.dataset.exerciseKey)) item.classList.add('lesson--done');
  }
  for (const item of document.querySelectorAll('[data-lesson-key]')) {
    if (viewed.includes(item.dataset.lessonKey)) item.classList.add('lesson--done');
  }
  // счётчик темы: «2/3» вместо «3», если что-то решено
  for (const topic of document.querySelectorAll('[data-topic-count]')) {
    const done = topic.closest('.topic').querySelectorAll('.lesson--task.lesson--done').length;
    if (done) topic.textContent = `${done}/${topic.dataset.total}`;
  }
  const badge = document.querySelector('[data-solved-badge]');
  if (badge && solved.includes(badge.dataset.solvedBadge)) badge.hidden = false;
}

/** Задача решена — вызывает страница задачи после «Верно!». */
export async function markSolved(key) {
  if (isAuthenticated) {
    await post(body.dataset.progressSolved, { exercise: key });
  } else {
    remember('solved', key);
  }
  for (const item of document.querySelectorAll(`[data-exercise-key="${key}"]`)) {
    item.classList.add('lesson--done');
  }
  const badge = document.querySelector('[data-solved-badge]');
  if (badge) badge.hidden = false;
}

/** После входа: перенести прогресс гостя на сервер и очистить браузер. */
async function importGuestProgress() {
  const data = load();
  if (!data.solved.length && !data.viewed.length) return;
  const response = await post(body.dataset.progressImport, data);
  if (response.ok) {
    try {
      localStorage.removeItem(STORE_KEY);
    } catch (e) {
      // не удалось — перенесём ещё раз, повтор ничего не испортит
    }
  }
}

if (isAuthenticated) {
  importGuestProgress();
} else {
  const lesson = document.querySelector('[data-current-lesson]');
  if (lesson) remember('viewed', lesson.dataset.currentLesson);
  showGuestProgress();
}
