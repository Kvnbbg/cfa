(() => {
  const CFA = window.CFA || (window.CFA = {});
  const utils = CFA.utils || (CFA.utils = {});
  const $ = utils.$ || ((selector, scope = document) => scope.querySelector(selector));
  const $$ = utils.$$ || ((selector, scope = document) => Array.from(scope.querySelectorAll(selector)));
  const createToast = utils.createToast || ((message) => alert(message));

  const links = {
    donate: 'https://buymeacoffee.com/kevinmarville',
    subscribe: 'https://patreon.com/cfaplatform',
    product: 'https://github.com/kvnbbg/cfa'
  };

  $$('[data-stripe-link]').forEach((button) => {
    button.addEventListener('click', () => {
      const key = button.dataset.stripeLink;
      if (links[key]) {
        createToast('Redirection sécurisée en cours...');
        window.open(links[key], '_blank', 'noopener');
      }
    });
  });
})();
