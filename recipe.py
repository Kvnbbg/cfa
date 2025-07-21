"""
Modèle Recipe pour les recettes liées aux produits CFA
"""

from src.models.base import BaseModel, db
from sqlalchemy import JSON

class Recipe(BaseModel):
    """Recettes associées aux produits"""
    __tablename__ = 'recipes'
    
    # Informations de base
    title = db.Column(db.String(255), nullable=False, index=True)
    description = db.Column(db.Text)
    difficulty = db.Column(db.String(20), default='facile')  # facile, moyen, difficile
    prep_time = db.Column(db.Integer)  # en minutes
    cook_time = db.Column(db.Integer)  # en minutes
    servings = db.Column(db.Integer, default=4)
    
    # Contenu multilingue
    title_en = db.Column(db.String(255))
    title_ko = db.Column(db.String(255))
    title_zh = db.Column(db.String(255))
    description_en = db.Column(db.Text)
    description_ko = db.Column(db.Text)
    description_zh = db.Column(db.Text)
    
    # Ingrédients et instructions (JSON pour flexibilité)
    ingredients = db.Column(JSON)  # Liste d'ingrédients avec quantités
    instructions = db.Column(JSON)  # Étapes de préparation
    
    # Ingrédients et instructions multilingues
    ingredients_en = db.Column(JSON)
    ingredients_ko = db.Column(JSON)
    ingredients_zh = db.Column(JSON)
    instructions_en = db.Column(JSON)
    instructions_ko = db.Column(JSON)
    instructions_zh = db.Column(JSON)
    
    # Métadonnées
    cuisine_type = db.Column(db.String(100))  # française, coréenne, chinoise, indienne, caribéenne
    dietary_tags = db.Column(JSON)  # végétarien, vegan, sans gluten, etc.
    nutrition_info = db.Column(JSON)  # informations nutritionnelles
    
    # Médias
    image_url = db.Column(db.Text)
    video_url = db.Column(db.Text)
    gallery_images = db.Column(JSON)
    
    # Relations avec les produits
    featured_products = db.Column(JSON)  # IDs des produits mis en avant
    
    # Engagement
    views_count = db.Column(db.Integer, default=0)
    likes_count = db.Column(db.Integer, default=0)
    
    # Statut
    is_published = db.Column(db.Boolean, default=False)
    is_featured = db.Column(db.Boolean, default=False)
    
    # Auteur (Kevin Marville ou contributeurs)
    author_name = db.Column(db.String(100), default='Kevin Marville')
    author_bio = db.Column(db.Text)
    
    def get_localized_content(self, language='fr'):
        """Retourne le contenu dans la langue demandée"""
        if language == 'en':
            return {
                'title': self.title_en or self.title,
                'description': self.description_en or self.description,
                'ingredients': self.ingredients_en or self.ingredients,
                'instructions': self.instructions_en or self.instructions
            }
        elif language == 'ko':
            return {
                'title': self.title_ko or self.title,
                'description': self.description_ko or self.description,
                'ingredients': self.ingredients_ko or self.ingredients,
                'instructions': self.instructions_ko or self.instructions
            }
        elif language == 'zh':
            return {
                'title': self.title_zh or self.title,
                'description': self.description_zh or self.description,
                'ingredients': self.ingredients_zh or self.ingredients,
                'instructions': self.instructions_zh or self.instructions
            }
        else:  # français par défaut
            return {
                'title': self.title,
                'description': self.description,
                'ingredients': self.ingredients,
                'instructions': self.instructions
            }
    
    @property
    def total_time(self):
        """Temps total de préparation"""
        prep = self.prep_time or 0
        cook = self.cook_time or 0
        return prep + cook
    
    def increment_views(self):
        """Incrémente le compteur de vues"""
        self.views_count += 1
        db.session.commit()
    
    def to_dict(self, language='fr', include_products=False):
        """Convertit la recette en dictionnaire"""
        localized = self.get_localized_content(language)
        
        data = {
            'id': self.id,
            'title': localized['title'],
            'description': localized['description'],
            'difficulty': self.difficulty,
            'prep_time': self.prep_time,
            'cook_time': self.cook_time,
            'total_time': self.total_time,
            'servings': self.servings,
            'ingredients': localized['ingredients'] or [],
            'instructions': localized['instructions'] or [],
            'cuisine_type': self.cuisine_type,
            'dietary_tags': self.dietary_tags or [],
            'nutrition_info': self.nutrition_info,
            'image_url': self.image_url,
            'video_url': self.video_url,
            'gallery_images': self.gallery_images or [],
            'views_count': self.views_count,
            'likes_count': self.likes_count,
            'is_featured': self.is_featured,
            'author_name': self.author_name,
            'author_bio': self.author_bio,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_products and self.featured_products:
            from src.models.product import Product
            products = Product.query.filter(Product.id.in_(self.featured_products)).all()
            data['featured_products'] = [p.to_dict() for p in products]
        
        return data
    
    def __repr__(self):
        return f'<Recipe {self.title}>'


class RecipeSearch:
    """Moteur de recherche de recettes"""
    
    @staticmethod
    def search_recipes(query: str, language='fr', filters=None):
        """
        Recherche de recettes avec query "recipe + {title of the article for food}"
        """
        # Nettoyer la query
        if query.lower().startswith('recipe '):
            search_term = query[7:].strip()  # Enlever "recipe "
        else:
            search_term = query.strip()
        
        # Base query
        recipes_query = Recipe.query.filter(Recipe.is_published == True)
        
        # Recherche multilingue
        if language == 'en':
            recipes_query = recipes_query.filter(
                db.or_(
                    Recipe.title_en.contains(search_term),
                    Recipe.description_en.contains(search_term),
                    Recipe.title.contains(search_term)
                )
            )
        elif language == 'ko':
            recipes_query = recipes_query.filter(
                db.or_(
                    Recipe.title_ko.contains(search_term),
                    Recipe.description_ko.contains(search_term),
                    Recipe.title.contains(search_term)
                )
            )
        elif language == 'zh':
            recipes_query = recipes_query.filter(
                db.or_(
                    Recipe.title_zh.contains(search_term),
                    Recipe.description_zh.contains(search_term),
                    Recipe.title.contains(search_term)
                )
            )
        else:  # français
            recipes_query = recipes_query.filter(
                db.or_(
                    Recipe.title.contains(search_term),
                    Recipe.description.contains(search_term)
                )
            )
        
        # Appliquer les filtres
        if filters:
            if filters.get('cuisine_type'):
                recipes_query = recipes_query.filter(Recipe.cuisine_type == filters['cuisine_type'])
            
            if filters.get('difficulty'):
                recipes_query = recipes_query.filter(Recipe.difficulty == filters['difficulty'])
            
            if filters.get('max_time'):
                max_time = filters['max_time']
                recipes_query = recipes_query.filter(
                    (Recipe.prep_time + Recipe.cook_time) <= max_time
                )
            
            if filters.get('dietary_tags'):
                # Recherche dans les tags JSON
                for tag in filters['dietary_tags']:
                    recipes_query = recipes_query.filter(
                        Recipe.dietary_tags.contains([tag])
                    )
        
        # Trier par pertinence (featured first, puis par vues)
        recipes_query = recipes_query.order_by(
            Recipe.is_featured.desc(),
            Recipe.views_count.desc(),
            Recipe.created_at.desc()
        )
        
        return recipes_query.all()
    
    @staticmethod
    def get_recipes_for_product(product_name: str, language='fr'):
        """
        Trouve des recettes pour un produit spécifique
        """
        search_query = f"recipe {product_name}"
        return RecipeSearch.search_recipes(search_query, language)
    
    @staticmethod
    def get_featured_recipes(language='fr', limit=6):
        """Récupère les recettes mises en avant"""
        recipes = Recipe.query.filter(
            Recipe.is_published == True,
            Recipe.is_featured == True
        ).order_by(Recipe.views_count.desc()).limit(limit).all()
        
        return [recipe.to_dict(language) for recipe in recipes]
    
    @staticmethod
    def get_popular_recipes(language='fr', limit=10):
        """Récupère les recettes populaires"""
        recipes = Recipe.query.filter(
            Recipe.is_published == True
        ).order_by(Recipe.views_count.desc()).limit(limit).all()
        
        return [recipe.to_dict(language) for recipe in recipes]

