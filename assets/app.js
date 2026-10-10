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
    const chosen = Math.max(0, tabs.findIndex(tab => tab.hash === location.hash));
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
  const fontItems = [...document.querySelectorAll('.font-item')];
  const loadFont = async item => {
    if (item.dataset.fontStatus === 'loading' || item.dataset.fontStatus === 'loaded') return;
    item.dataset.fontStatus = 'loading';
    try {
      const font = new FontFace(item.dataset.fontFamily, `url("${item.dataset.fontUrl}")`, {display: 'swap'});
      await font.load();
      document.fonts.add(font);
      item.querySelector('.font-preview').style.fontFamily = `"${item.dataset.fontFamily}",${item.dataset.fontFallback}`;
      item.dataset.fontStatus = 'loaded';
    } catch {
      item.dataset.fontStatus = 'error';
      item.querySelector('.font-preview').title = 'Font could not load. Use the download link to get the font file.';
    }
  };
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          loadFont(entry.target);
          observer.unobserve(entry.target);
        }
      });
    }, {rootMargin: '350px 0px'});
    fontItems.forEach(item => observer.observe(item));
  } else {
    const loadVisible = () => {
      if (document.querySelector('#fonts').hidden) return;
      fontItems.forEach(item => {
        const bounds = item.getBoundingClientRect();
        if (bounds.bottom >= -350 && bounds.top <= window.innerHeight + 350) loadFont(item);
      });
    };
    window.addEventListener('scroll', loadVisible, {passive: true});
    window.addEventListener('resize', loadVisible);
    window.addEventListener('hashchange', loadVisible);
    window.addEventListener('popstate', loadVisible);
    tabs.forEach(tab => tab.addEventListener('click', loadVisible));
    bar.addEventListener('keydown', loadVisible);
    requestAnimationFrame(loadVisible);
  }
  document.querySelector('#fonts').addEventListener('focusin', event => {
    const item = event.target.closest('.font-item');
    if (item) loadFont(item);
  });
  activate();
})();
