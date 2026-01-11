(() => {
  const CFA = window.CFA || (window.CFA = {});
  const utils = CFA.utils || (CFA.utils = {});
  const $ = utils.$ || ((selector, scope = document) => scope.querySelector(selector));
  const $$ = utils.$$ || ((selector, scope = document) => Array.from(scope.querySelectorAll(selector)));

  const translations = {
    fr: {
      home: 'Accueil',
      products: 'Produits',
      recipes: 'Recettes',
      about: 'À propos',
      contact: 'Contact',
      register: 'Inscription Facile',
      login: 'Connexion',
      search_placeholder: 'Rechercher...',
      welcome_message: 'Bienvenue sur Caraïbes-France-Asie',
      tagline: "Chaîne d'approvisionnement de la ferme à la table, enracinée dans l'écologie",
      support_local: 'Soutenez les producteurs locaux contre les grandes surfaces comme Carrefour et Leclerc',
      quality_guarantee: 'Qualité garantie',
      fair_trade: 'Commerce équitable'
    },
    en: {
      home: 'Home',
      products: 'Products',
      recipes: 'Recipes',
      about: 'About',
      contact: 'Contact',
      register: 'Easy Signup',
      login: 'Sign in',
      search_placeholder: 'Search...',
      welcome_message: 'Welcome to Caribbean-France-Asia',
      tagline: 'Farm-to-table supply chain, rooted in ecology',
      support_local: 'Support local producers versus big retailers',
      quality_guarantee: 'Quality guaranteed',
      fair_trade: 'Fair trade'
    },
    ko: {
      home: '홈',
      products: '제품',
      recipes: '레시피',
      about: '소개',
      contact: '문의',
      register: '간편 가입',
      login: '로그인',
      search_placeholder: '검색...',
      welcome_message: '카리브-프랑스-아시아에 오신 것을 환영합니다',
      tagline: '생태 기반의 팜투테이블 공급망',
      support_local: '지역 생산자를 지원하세요',
      quality_guarantee: '품질 보증',
      fair_trade: '공정 거래'
    },
    zh: {
      home: '主页',
      products: '产品',
      recipes: '食谱',
      about: '关于',
      contact: '联系',
      register: '快速注册',
      login: '登录',
      search_placeholder: '搜索...',
      welcome_message: '欢迎来到加勒比-法国-亚洲',
      tagline: '扎根生态的农场到餐桌供应链',
      support_local: '支持本地生产者',
      quality_guarantee: '品质保障',
      fair_trade: '公平贸易'
    }
  };

  const applyTranslations = (lang) => {
    const dictionary = translations[lang] || translations.fr;
    $$('[data-i18n]').forEach((element) => {
      const key = element.dataset.i18n;
      if (dictionary[key]) {
        element.textContent = dictionary[key];
      }
    });
    $$('[data-i18n-placeholder]').forEach((element) => {
      const key = element.dataset.i18nPlaceholder;
      if (dictionary[key]) {
        element.setAttribute('placeholder', dictionary[key]);
      }
    });
  };

  const buttons = $$('.lang-btn');
  buttons.forEach((button) => {
    button.addEventListener('click', () => {
      const lang = button.dataset.lang;
      applyTranslations(lang);
      localStorage.setItem('cfa-lang', lang);
    });
  });

  const storedLang = localStorage.getItem('cfa-lang');
  if (storedLang) {
    applyTranslations(storedLang);
  }
})();
