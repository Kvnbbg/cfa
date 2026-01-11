(() => {
  const CFA = window.CFA || (window.CFA = {});
  const utils = CFA.utils || (CFA.utils = {});
  const $ = utils.$ || ((selector, scope = document) => scope.querySelector(selector));
  const $$ = utils.$$ || ((selector, scope = document) => Array.from(scope.querySelectorAll(selector)));

  const typingTarget = $('.typing-text');
  if (typingTarget) {
    const text = typingTarget.dataset.text || typingTarget.textContent || '';
    let index = 0;
    const type = () => {
      typingTarget.textContent = text.slice(0, index);
      index += 1;
      if (index <= text.length) {
        setTimeout(type, 45);
      }
    };
    type();
  }

  const animatedItems = $$('[data-animate]');
  if (animatedItems.length) {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const animationClass = entry.target.dataset.animate || 'fade-in';
            entry.target.classList.add(animationClass);
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.2 }
    );
    animatedItems.forEach((item) => observer.observe(item));
  }

  const counterItems = $$('[data-counter]');
  if (counterItems.length) {
    const animateCounter = (element) => {
      const target = Number(element.dataset.counter || 0);
      const duration = 1200;
      const startTime = performance.now();

      const tick = (now) => {
        const progress = Math.min((now - startTime) / duration, 1);
        const value = Math.floor(target * progress);
        element.textContent = value.toString();
        if (progress < 1) {
          requestAnimationFrame(tick);
        } else {
          element.textContent = target.toString();
        }
      };
      requestAnimationFrame(tick);
    };

    const counterObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            animateCounter(entry.target);
            counterObserver.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.4 }
    );
    counterItems.forEach((item) => counterObserver.observe(item));
  }
})();
