(() => {
  const root = document.documentElement;
  const preference = matchMedia('(prefers-color-scheme: dark)');
  const KEY = 'course-pages-theme';
  let selected;
  try { selected = localStorage.getItem(KEY); } catch {}
  if (selected !== 'light' && selected !== 'dark') selected = null;

  function apply() {
    const theme = selected || (preference.matches ? 'dark' : 'light');
    root.dataset.theme = theme;
    const toggle = document.querySelector('.theme-toggle');
    if (!toggle) return;
    const dark = theme === 'dark';
    toggle.setAttribute('aria-pressed', String(dark));
    toggle.innerHTML = dark
      ? '<span aria-hidden="true">◑</span> حالت روشن'
      : '<span aria-hidden="true">◐</span> حالت تاریک';
  }

  apply();
  if (preference.addEventListener) preference.addEventListener('change', apply);

  document.addEventListener('DOMContentLoaded', () => {
    const toggle = document.querySelector('.theme-toggle');
    if (!toggle) return;
    toggle.addEventListener('click', () => {
      selected = root.dataset.theme === 'dark' ? 'light' : 'dark';
      try { localStorage.setItem(KEY, selected); } catch {}
      apply();
    });
    apply();
    toggle.hidden = false;
  });
})();
