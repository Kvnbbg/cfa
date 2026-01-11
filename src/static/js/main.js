(() => {
  const CFA = window.CFA || (window.CFA = {});
  const utils = CFA.utils || (CFA.utils = {});

  utils.$ = (selector, scope = document) => scope.querySelector(selector);
  utils.$$ = (selector, scope = document) => Array.from(scope.querySelectorAll(selector));
  utils.clamp = (value, min, max) => Math.min(Math.max(value, min), max);
  utils.createToast = (message) => {
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;
    document.body.appendChild(toast);
    requestAnimationFrame(() => toast.classList.add('show'));
    setTimeout(() => {
      toast.classList.remove('show');
      setTimeout(() => toast.remove(), 300);
    }, 3000);
  };

  const root = document.documentElement;
  const themeToggle = utils.$('#theme-toggle');
  const storedTheme = localStorage.getItem('cfa-theme');

  if (storedTheme) {
    root.setAttribute('data-theme', storedTheme);
  }

  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      const currentTheme = root.getAttribute('data-theme') || 'light';
      const nextTheme = currentTheme === 'light' ? 'dark' : 'light';
      root.setAttribute('data-theme', nextTheme);
      localStorage.setItem('cfa-theme', nextTheme);
    });
  }

  const modal = utils.$('#signup-modal');
  const openModalBtn = utils.$('#easy-signup-btn');
  const closeModalBtn = modal ? utils.$('.modal-close', modal) : null;

  const closeModal = () => {
    if (modal) {
      modal.classList.remove('open');
    }
  };

  if (openModalBtn && modal) {
    openModalBtn.addEventListener('click', () => {
      modal.classList.add('open');
    });
  }

  if (closeModalBtn) {
    closeModalBtn.addEventListener('click', closeModal);
  }

  if (modal) {
    modal.addEventListener('click', (event) => {
      if (event.target === modal) {
        closeModal();
      }
    });
  }

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
      closeModal();
    }
  });

  const mobileToggle = utils.$('.mobile-menu-toggle');
  if (mobileToggle) {
    mobileToggle.addEventListener('click', () => {
      document.body.classList.toggle('nav-open');
    });
  }

  const languageButtons = utils.$$('.lang-btn');
  languageButtons.forEach((button) => {
    button.addEventListener('click', () => {
      languageButtons.forEach((btn) => btn.classList.remove('active'));
      button.classList.add('active');
    });
  });

  const brakeRange = utils.$('.brake-range');
  const brakeFill = utils.$('[data-brake-fill]');
  const brakeValue = utils.$('[data-brake-value]');
  const brakeState = utils.$('[data-brake-state]');
  const whiteoutToggle = utils.$('[data-whiteout-toggle]');
  const brakeBoost = utils.$('.brake-boost');

  const updateBrakeDisplay = (value) => {
    const level = utils.clamp(Number(value), 0, 100);
    if (brakeFill) {
      brakeFill.style.width = `${level}%`;
    }
    if (brakeValue) {
      brakeValue.textContent = `${level}%`;
    }
    if (brakeState) {
      if (level >= 75) {
        brakeState.textContent = 'Freinage intensif';
      } else if (level >= 45) {
        brakeState.textContent = 'Stabilisé';
      } else {
        brakeState.textContent = 'Éco-conduite';
      }
    }
  };

  if (brakeRange) {
    updateBrakeDisplay(brakeRange.value);
    brakeRange.addEventListener('input', (event) => updateBrakeDisplay(event.target.value));
  }

  if (whiteoutToggle) {
    whiteoutToggle.addEventListener('change', (event) => {
      if (event.target.checked) {
        updateBrakeDisplay(70);
        if (brakeRange) {
          brakeRange.value = 70;
        }
      }
    });
  }

  if (brakeBoost) {
    brakeBoost.addEventListener('click', () => {
      updateBrakeDisplay(85);
      if (brakeRange) {
        brakeRange.value = 85;
      }
      utils.createToast('Stabilisation activée pour conditions extrêmes.');
    });
  }

  const chips = utils.$$('.chip');
  const meterFill = utils.$('.meter-fill');
  chips.forEach((chip) => {
    chip.addEventListener('click', () => {
      chips.forEach((item) => item.classList.remove('active'));
      chip.classList.add('active');
      if (meterFill) {
        const target = chip.dataset.chip;
        const value = target === 'eco' ? 84 : target === 'speed' ? 58 : 72;
        meterFill.style.width = `${value}%`;
      }
    });
  });

  const alertButton = utils.$('[data-alert-btn]');
  if (alertButton) {
    alertButton.addEventListener('click', () => {
      utils.createToast('Alertes activées: vous serez notifié en temps réel.');
    });
  }

  window.addEventListener('load', () => {
    const loadingScreen = utils.$('#loading-screen');
    if (loadingScreen) {
      loadingScreen.classList.add('fade-out');
      setTimeout(() => loadingScreen.remove(), 600);
    }
  });
})();
