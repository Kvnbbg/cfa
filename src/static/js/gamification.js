(() => {
  const CFA = window.CFA || (window.CFA = {});
  const utils = CFA.utils || (CFA.utils = {});
  const $ = utils.$ || ((selector, scope = document) => scope.querySelector(selector));

  const cartBtn = $('.cart-btn');
  const cartCount = cartBtn ? cartBtn.querySelector('.cart-count') : null;

  if (cartBtn && cartCount) {
    cartBtn.addEventListener('click', () => {
      const current = Number(cartCount.textContent || 0);
      const next = current + 1;
      cartCount.textContent = next.toString();
      cartBtn.classList.add('pulse');
      setTimeout(() => cartBtn.classList.remove('pulse'), 600);
    });
  }
})();
