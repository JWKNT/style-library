(() => {
  const tabs = [...document.querySelectorAll('.tabs a')];
  const panels = tabs.map(tab => document.querySelector(tab.hash));
  const bar = document.querySelector('.tabs');
  bar.setAttribute('role', 'tablist');
  tabs.forEach((tab, i) => {
    tab.setAttribute('role', 'tab');
    tab.setAttribute('aria-controls', panels[i].id);
    panels[i].setAttribute('role', 'tabpanel');
    panels[i].tabIndex = 0;
  });
  const activate = () => {
    const chosen = location.hash === '#icons' ? 1 : 0;
    tabs.forEach((tab, i) => {
      tab.setAttribute('aria-selected', String(i === chosen));
      tab.tabIndex = i === chosen ? 0 : -1;
      panels[i].hidden = i !== chosen;
    });
  };
  bar.addEventListener('keydown', event => {
    const index = tabs.indexOf(document.activeElement);
    if (index < 0 || !['ArrowLeft','ArrowRight','Home','End'].includes(event.key)) return;
    event.preventDefault();
    const next = event.key === 'Home' ? 0 : event.key === 'End' ? tabs.length - 1 : (index + (event.key === 'ArrowRight' ? 1 : -1) + tabs.length) % tabs.length;
    tabs[next].focus();
    history.replaceState(null, '', tabs[next].hash);
    activate();
  });
  tabs.forEach(tab => tab.addEventListener('click', event => {
    event.preventDefault();
    if (location.hash !== tab.hash) history.pushState(null, '', tab.hash);
    activate();
  }));
  window.addEventListener('hashchange', activate);
  window.addEventListener('popstate', activate);
  document.querySelector('#sample').addEventListener('input', event => {
    document.querySelectorAll('.font-preview').forEach(preview => { preview.textContent = event.target.value; });
  });
  activate();
})();
