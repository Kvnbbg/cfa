"""
Système d'internationalisation pour CFA
Support: Français, Anglais, Coréen, Mandarin
"""

from typing import Dict, Optional
import json
import os

class I18nManager:
    """Gestionnaire d'internationalisation"""
    
    def __init__(self):
        self.current_language = 'fr'
        self.supported_languages = ['fr', 'en', 'ko', 'zh']
        self.translations = self._load_translations()
    
    def _load_translations(self) -> Dict[str, Dict[str, str]]:
        """Charge les traductions"""
        return {
            'fr': {
                # Navigation
                'home': 'Accueil',
                'products': 'Produits',
                'recipes': 'Recettes',
                'about': 'À propos',
                'contact': 'Contact',
                'cart': 'Panier',
                'account': 'Mon compte',
                'login': 'Connexion',
                'register': 'Inscription',
                'logout': 'Déconnexion',
                
                # Produits
                'add_to_cart': 'Ajouter au panier',
                'buy_now': 'Acheter maintenant',
                'out_of_stock': 'Rupture de stock',
                'in_stock': 'En stock',
                'price': 'Prix',
                'origin': 'Origine',
                'category': 'Catégorie',
                'ecology_score': 'Score écologique',
                'fair_trade': 'Commerce équitable',
                'organic': 'Bio',
                
                # Recherche
                'search_placeholder': 'Rechercher des produits, recettes...',
                'search_recipes': 'Rechercher des recettes',
                'no_results': 'Aucun résultat trouvé',
                'filters': 'Filtres',
                'sort_by': 'Trier par',
                
                # Panier et commande
                'checkout': 'Commander',
                'total': 'Total',
                'shipping': 'Livraison',
                'taxes': 'Taxes',
                'order_summary': 'Résumé de commande',
                'payment': 'Paiement',
                
                # Messages
                'welcome_message': 'Bienvenue sur Caraïbes-France-Asie',
                'tagline': 'Chaîne d\'approvisionnement de la ferme à la table, enracinée dans l\'écologie',
                'support_local': 'Soutenez les producteurs locaux contre les grandes surfaces',
                'quality_guarantee': 'Qualité garantie, traçabilité complète',
                
                # Contact Kevin Marville
                'contact_kevin': 'Contacter Kevin Marville',
                'linkedin_kevin': 'LinkedIn de Kevin',
                'support_project': 'Soutenir le projet',
                'buy_coffee': 'Offrir un café',
                'donate': 'Faire un don',
                
                # Thème
                'dark_mode': 'Mode sombre',
                'light_mode': 'Mode clair',
                'theme_toggle': 'Changer de thème',
                
                # Recettes
                'recipe_search': 'Recherche de recettes',
                'prep_time': 'Temps de préparation',
                'cook_time': 'Temps de cuisson',
                'total_time': 'Temps total',
                'servings': 'Portions',
                'ingredients': 'Ingrédients',
                'instructions': 'Instructions',
                'difficulty': 'Difficulté',
                'cuisine_type': 'Type de cuisine',
                
                # Anti-monopole
                'vs_supermarket': 'vs Grandes surfaces',
                'local_support': 'Soutien local',
                'direct_trade': 'Commerce direct',
                'fair_pricing': 'Prix équitables',
                'no_middleman': 'Sans intermédiaire',
            },
            
            'en': {
                # Navigation
                'home': 'Home',
                'products': 'Products',
                'recipes': 'Recipes',
                'about': 'About',
                'contact': 'Contact',
                'cart': 'Cart',
                'account': 'My Account',
                'login': 'Login',
                'register': 'Sign Up',
                'logout': 'Logout',
                
                # Products
                'add_to_cart': 'Add to Cart',
                'buy_now': 'Buy Now',
                'out_of_stock': 'Out of Stock',
                'in_stock': 'In Stock',
                'price': 'Price',
                'origin': 'Origin',
                'category': 'Category',
                'ecology_score': 'Ecology Score',
                'fair_trade': 'Fair Trade',
                'organic': 'Organic',
                
                # Search
                'search_placeholder': 'Search products, recipes...',
                'search_recipes': 'Search recipes',
                'no_results': 'No results found',
                'filters': 'Filters',
                'sort_by': 'Sort by',
                
                # Cart and order
                'checkout': 'Checkout',
                'total': 'Total',
                'shipping': 'Shipping',
                'taxes': 'Taxes',
                'order_summary': 'Order Summary',
                'payment': 'Payment',
                
                # Messages
                'welcome_message': 'Welcome to Caribbean-France-Asia',
                'tagline': 'Farm to table supply chain, rooted in ecology',
                'support_local': 'Support local producers against big retailers',
                'quality_guarantee': 'Quality guaranteed, full traceability',
                
                # Contact Kevin Marville
                'contact_kevin': 'Contact Kevin Marville',
                'linkedin_kevin': 'Kevin\'s LinkedIn',
                'support_project': 'Support the project',
                'buy_coffee': 'Buy me a coffee',
                'donate': 'Donate',
                
                # Theme
                'dark_mode': 'Dark mode',
                'light_mode': 'Light mode',
                'theme_toggle': 'Toggle theme',
                
                # Recipes
                'recipe_search': 'Recipe search',
                'prep_time': 'Prep time',
                'cook_time': 'Cook time',
                'total_time': 'Total time',
                'servings': 'Servings',
                'ingredients': 'Ingredients',
                'instructions': 'Instructions',
                'difficulty': 'Difficulty',
                'cuisine_type': 'Cuisine type',
                
                # Anti-monopoly
                'vs_supermarket': 'vs Supermarkets',
                'local_support': 'Local support',
                'direct_trade': 'Direct trade',
                'fair_pricing': 'Fair pricing',
                'no_middleman': 'No middleman',
            },
            
            'ko': {
                # Navigation
                'home': '홈',
                'products': '제품',
                'recipes': '레시피',
                'about': '소개',
                'contact': '연락처',
                'cart': '장바구니',
                'account': '내 계정',
                'login': '로그인',
                'register': '회원가입',
                'logout': '로그아웃',
                
                # Products
                'add_to_cart': '장바구니에 추가',
                'buy_now': '지금 구매',
                'out_of_stock': '품절',
                'in_stock': '재고 있음',
                'price': '가격',
                'origin': '원산지',
                'category': '카테고리',
                'ecology_score': '생태 점수',
                'fair_trade': '공정무역',
                'organic': '유기농',
                
                # Search
                'search_placeholder': '제품, 레시피 검색...',
                'search_recipes': '레시피 검색',
                'no_results': '검색 결과가 없습니다',
                'filters': '필터',
                'sort_by': '정렬',
                
                # Cart and order
                'checkout': '주문하기',
                'total': '총계',
                'shipping': '배송',
                'taxes': '세금',
                'order_summary': '주문 요약',
                'payment': '결제',
                
                # Messages
                'welcome_message': '카리브-프랑스-아시아에 오신 것을 환영합니다',
                'tagline': '농장에서 식탁까지, 생태학에 뿌리를 둔 공급망',
                'support_local': '대형 마트에 맞서 지역 생산자를 지원하세요',
                'quality_guarantee': '품질 보장, 완전한 추적성',
                
                # Contact Kevin Marville
                'contact_kevin': 'Kevin Marville 연락하기',
                'linkedin_kevin': 'Kevin의 LinkedIn',
                'support_project': '프로젝트 지원',
                'buy_coffee': '커피 사주기',
                'donate': '기부하기',
                
                # Theme
                'dark_mode': '다크 모드',
                'light_mode': '라이트 모드',
                'theme_toggle': '테마 변경',
                
                # Recipes
                'recipe_search': '레시피 검색',
                'prep_time': '준비 시간',
                'cook_time': '조리 시간',
                'total_time': '총 시간',
                'servings': '인분',
                'ingredients': '재료',
                'instructions': '조리법',
                'difficulty': '난이도',
                'cuisine_type': '요리 종류',
                
                # Anti-monopoly
                'vs_supermarket': 'vs 대형마트',
                'local_support': '지역 지원',
                'direct_trade': '직접 거래',
                'fair_pricing': '공정한 가격',
                'no_middleman': '중간업체 없음',
            },
            
            'zh': {
                # Navigation
                'home': '首页',
                'products': '产品',
                'recipes': '食谱',
                'about': '关于',
                'contact': '联系',
                'cart': '购物车',
                'account': '我的账户',
                'login': '登录',
                'register': '注册',
                'logout': '退出',
                
                # Products
                'add_to_cart': '加入购物车',
                'buy_now': '立即购买',
                'out_of_stock': '缺货',
                'in_stock': '有库存',
                'price': '价格',
                'origin': '产地',
                'category': '类别',
                'ecology_score': '生态评分',
                'fair_trade': '公平贸易',
                'organic': '有机',
                
                # Search
                'search_placeholder': '搜索产品、食谱...',
                'search_recipes': '搜索食谱',
                'no_results': '未找到结果',
                'filters': '筛选',
                'sort_by': '排序',
                
                # Cart and order
                'checkout': '结账',
                'total': '总计',
                'shipping': '运费',
                'taxes': '税费',
                'order_summary': '订单摘要',
                'payment': '付款',
                
                # Messages
                'welcome_message': '欢迎来到加勒比-法国-亚洲',
                'tagline': '从农场到餐桌的供应链，植根于生态学',
                'support_local': '支持本地生产者对抗大型超市',
                'quality_guarantee': '质量保证，完全可追溯',
                
                # Contact Kevin Marville
                'contact_kevin': '联系 Kevin Marville',
                'linkedin_kevin': 'Kevin 的 LinkedIn',
                'support_project': '支持项目',
                'buy_coffee': '请我喝咖啡',
                'donate': '捐赠',
                
                # Theme
                'dark_mode': '深色模式',
                'light_mode': '浅色模式',
                'theme_toggle': '切换主题',
                
                # Recipes
                'recipe_search': '食谱搜索',
                'prep_time': '准备时间',
                'cook_time': '烹饪时间',
                'total_time': '总时间',
                'servings': '份数',
                'ingredients': '配料',
                'instructions': '制作方法',
                'difficulty': '难度',
                'cuisine_type': '菜系',
                
                # Anti-monopoly
                'vs_supermarket': 'vs 超市',
                'local_support': '本地支持',
                'direct_trade': '直接贸易',
                'fair_pricing': '公平定价',
                'no_middleman': '无中间商',
            }
        }
    
    def set_language(self, language: str):
        """Définit la langue actuelle"""
        if language in self.supported_languages:
            self.current_language = language
    
    def get_text(self, key: str, language: Optional[str] = None) -> str:
        """Récupère un texte traduit"""
        lang = language or self.current_language
        
        if lang not in self.translations:
            lang = 'fr'  # Fallback vers le français
        
        return self.translations[lang].get(key, key)
    
    def get_language_name(self, language: str) -> str:
        """Retourne le nom de la langue"""
        names = {
            'fr': 'Français',
            'en': 'English',
            'ko': '한국어',
            'zh': '中文'
        }
        return names.get(language, language)
    
    def get_language_flag(self, language: str) -> str:
        """Retourne l'emoji du drapeau"""
        flags = {
            'fr': '🇫🇷',
            'en': '🇺🇸',
            'ko': '🇰🇷',
            'zh': '🇨🇳'
        }
        return flags.get(language, '🌍')
    
    def detect_language_from_request(self, request):
        """Détecte la langue depuis la requête HTTP"""
        # Vérifier le paramètre URL
        if hasattr(request, 'args') and 'lang' in request.args:
            lang = request.args.get('lang')
            if lang in self.supported_languages:
                return lang
        
        # Vérifier les headers Accept-Language
        if hasattr(request, 'headers') and 'Accept-Language' in request.headers:
            accept_lang = request.headers.get('Accept-Language', '')
            for lang in self.supported_languages:
                if lang in accept_lang:
                    return lang
        
        return 'fr'  # Défaut français
    
    def get_all_translations(self, language: Optional[str] = None) -> Dict[str, str]:
        """Retourne toutes les traductions pour une langue"""
        lang = language or self.current_language
        return self.translations.get(lang, self.translations['fr'])

# Instance globale
i18n = I18nManager()

