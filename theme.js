(() => {
  const root = document.documentElement;
  const preference = matchMedia('(prefers-color-scheme: dark)');
  let selected;
  try { selected = localStorage.getItem('course-pages-theme'); } catch {}
  if (selected !== 'light' && selected !== 'dark') selected = null;

  function apply() {
    const theme = selected || (preference.matches ? 'dark' : 'light');
    root.dataset.theme = theme;
    const toggle = document.querySelector('.theme-toggle');
    if (toggle) toggle.setAttribute('aria-pressed', String(theme === 'dark'));
  }

  apply();
  preference.addEventListener('change', apply);
  document.addEventListener('DOMContentLoaded', () => {
    const toggle = document.querySelector('.theme-toggle');
    toggle.addEventListener('click', () => {
      selected = root.dataset.theme === 'dark' ? 'light' : 'dark';
      try { localStorage.setItem('course-pages-theme', selected); } catch {}
      apply();
    });
    apply();
    toggle.hidden = false;
  });
})();
