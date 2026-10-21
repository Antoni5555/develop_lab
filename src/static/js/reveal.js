// Появление блоков главной при прокрутке. Подключается только на главной (defer).
// Без JS или при prefers-reduced-motion классы не ставятся — всё видно сразу.
// CSS — base.css, «Появление блоков при прокрутке» (.js-reveal .reveal).
(() => {
  if (!('IntersectionObserver' in window) || matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  const items = document.querySelectorAll(
    '.stack-home > section, .stack-home > .cta, .showcase__row, .journey__step',
  );
  document.documentElement.classList.add('js-reveal');
  // Шаги «Как это работает» появляются по очереди
  document.querySelectorAll('.journey__step').forEach((el, i) => {
    el.style.setProperty('--reveal-delay', `${i * 120}ms`);
  });

  const observer = new IntersectionObserver((entries) => {
    for (const entry of entries) {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      }
    }
  }, { threshold: 0.15 });

  items.forEach((el) => {
    el.classList.add('reveal');
    observer.observe(el);
  });
})();
