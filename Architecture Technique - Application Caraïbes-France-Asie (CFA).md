# Architecture Technique - Application Caraïbes-France-Asie (CFA)

## Vue d'ensemble du projet

**Nom de l'application :** Caraïbes-France-Asie (CFA)  
**Fondateur :** Kevin Marville  
**Tagline :** "Chaîne d'approvisionnement de la ferme à la table, enracinée dans l'écologie"  
**Objectif :** Plateforme de commerce électronique spécialisée dans les produits exotiques et écologiques provenant de France, d'Asie, d'Inde et des Caraïbes

## Architecture générale

### Stack technologique principal
- **Backend :** Python Flask (MVP adapté mobile)
- **Base de données :** PostgreSQL avec SQLAlchemy ORM
- **Frontend :** Templates Jinja2 avec Bootstrap 5 (responsive)
- **Authentification :** JWT + bcrypt
- **Paiements :** Stripe API
- **Stockage :** Système de fichiers local + AWS S3 (optionnel)
- **API :** RESTful avec endpoints JSON
- **Logs :** Python logging + fichiers structurés

### Architecture en couches

#### 1. Couche de présentation (Frontend)
```
/templates/
├── base.html (template principal)
├── index.html (page d'accueil)
├── products/ (pages produits)
├── auth/ (authentification)
├── admin/ (panneau d'administration)
└── slides/ (interface quiz transformée)

/static/
├── css/ (styles personnalisés)
├── js/ (JavaScript pour interactivité)
├── images/ (logos, icônes)
└── uploads/ (images produits)
```

#### 2. Couche logique métier (Backend Flask)
```
/app/
├── __init__.py (configuration Flask)
├── models/ (modèles SQLAlchemy)
├── routes/ (endpoints API)
├── services/ (logique métier)
├── utils/ (utilitaires)
└── algorithms/ (algorithmes de tarification)
```

#### 3. Couche de données
```
/database/
├── migrations/ (Alembic migrations)
├── seeds/ (données de test)
└── backups/ (sauvegardes)
```

## Schéma de base de données détaillé

### Tables principales

#### Users (Utilisateurs)
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    role ENUM('buyer', 'seller', 'admin') DEFAULT 'buyer',
    phone VARCHAR(20),
    address TEXT,
    city VARCHAR(100),
    country VARCHAR(100),
    postal_code VARCHAR(20),
    stripe_customer_id TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### Products (Produits)
```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    short_description VARCHAR(500),
    origin_country VARCHAR(100),
    origin_region VARCHAR(100),
    category ENUM('food', 'spices', 'herbs', 'alcohol', 'drinks', 'medical_herbs') NOT NULL,
    subcategory VARCHAR(100),
    base_price DECIMAL(10,2) NOT NULL,
    current_price DECIMAL(10,2) NOT NULL,
    discounted_price DECIMAL(10,2),
    cost_price DECIMAL(10,2),
    stock_quantity INT DEFAULT 0,
    min_stock_level INT DEFAULT 5,
    weight DECIMAL(8,2),
    unit VARCHAR(20) DEFAULT 'kg',
    image_url TEXT,
    gallery_images TEXT[], -- Array of image URLs
    seller_id INT REFERENCES users(id),
    ecology_score INT DEFAULT 0 CHECK (ecology_score >= 0 AND ecology_score <= 100),
    fair_trade BOOLEAN DEFAULT FALSE,
    organic BOOLEAN DEFAULT FALSE,
    carbon_footprint DECIMAL(8,2), -- kg CO2
    is_active BOOLEAN DEFAULT TRUE,
    featured BOOLEAN DEFAULT FALSE,
    tags TEXT[],
    nutritional_info JSONB,
    storage_instructions TEXT,
    expiry_date DATE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### Orders (Commandes)
```sql
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    user_id INT REFERENCES users(id),
    total_amount DECIMAL(10,2) NOT NULL,
    tax_amount DECIMAL(10,2) DEFAULT 0,
    shipping_amount DECIMAL(10,2) DEFAULT 0,
    discount_amount DECIMAL(10,2) DEFAULT 0,
    final_amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'EUR',
    status ENUM('pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled', 'refunded') DEFAULT 'pending',
    payment_status ENUM('pending', 'paid', 'failed', 'refunded') DEFAULT 'pending',
    stripe_payment_intent_id TEXT,
    stripe_session_id TEXT,
    shipping_address JSONB,
    billing_address JSONB,
    tracking_number VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### Order_Items (Articles de commande)
```sql
CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INT REFERENCES orders(id) ON DELETE CASCADE,
    product_id INT REFERENCES products(id),
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(10,2) NOT NULL,
    product_snapshot JSONB -- Snapshot du produit au moment de la commande
);
```

#### Price_History (Historique des prix)
```sql
CREATE TABLE price_history (
    id SERIAL PRIMARY KEY,
    product_id INT REFERENCES products(id),
    old_price DECIMAL(10,2),
    new_price DECIMAL(10,2),
    change_reason VARCHAR(255),
    algorithm_used VARCHAR(100),
    market_data JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### Competitor_Prices (Prix concurrents)
```sql
CREATE TABLE competitor_prices (
    id SERIAL PRIMARY KEY,
    product_name VARCHAR(255),
    competitor_name VARCHAR(100),
    competitor_price DECIMAL(10,2),
    competitor_url TEXT,
    our_product_id INT REFERENCES products(id),
    scraped_at TIMESTAMP DEFAULT NOW()
);
```

#### Categories (Catégories)
```sql
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    parent_id INT REFERENCES categories(id),
    image_url TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INT DEFAULT 0
);
```

#### Reviews (Avis)
```sql
CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    product_id INT REFERENCES products(id),
    user_id INT REFERENCES users(id),
    rating INT CHECK (rating >= 1 AND rating <= 5),
    title VARCHAR(255),
    comment TEXT,
    verified_purchase BOOLEAN DEFAULT FALSE,
    is_approved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### Logs (Journaux)
```sql
CREATE TABLE logs (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50),
    entity_id INT,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    metadata JSONB,
    level VARCHAR(20) DEFAULT 'INFO',
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### Coupons (Coupons de réduction)
```sql
CREATE TABLE coupons (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    discount_type ENUM('percentage', 'fixed_amount') NOT NULL,
    discount_value DECIMAL(10,2) NOT NULL,
    minimum_amount DECIMAL(10,2) DEFAULT 0,
    maximum_discount DECIMAL(10,2),
    usage_limit INT,
    used_count INT DEFAULT 0,
    valid_from TIMESTAMP,
    valid_until TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Algorithmes de tarification

### 1. Algorithme de réduction de prix dynamique

```python
def calculate_dynamic_price(product_id, base_price, market_data):
    """
    Calcule le prix dynamique basé sur plusieurs facteurs
    """
    # Facteurs de base
    competitor_price = get_lowest_competitor_price(product_id)
    stock_level = get_stock_level(product_id)
    demand_factor = calculate_demand_factor(product_id)
    ecology_score = get_ecology_score(product_id)
    
    # Coefficients
    COMPETITOR_WEIGHT = 0.4
    STOCK_WEIGHT = 0.2
    DEMAND_WEIGHT = 0.2
    ECOLOGY_WEIGHT = 0.2
    
    # Calcul du facteur concurrentiel
    if competitor_price:
        competitor_factor = min(1.0, competitor_price / base_price * 0.95)  # 5% sous la concurrence
    else:
        competitor_factor = 1.0
    
    # Facteur de stock (stock faible = prix plus élevé)
    stock_factor = 1.0 + (1.0 - stock_level) * 0.3
    
    # Facteur de demande
    demand_factor_calc = 1.0 + demand_factor * 0.25
    
    # Bonus écologique (score élevé = réduction)
    ecology_factor = 1.0 - (ecology_score / 100) * 0.1
    
    # Prix final
    final_price = base_price * (
        competitor_factor * COMPETITOR_WEIGHT +
        stock_factor * STOCK_WEIGHT +
        demand_factor_calc * DEMAND_WEIGHT +
        ecology_factor * ECOLOGY_WEIGHT
    )
    
    return round(final_price, 2)
```

### 2. Algorithme de manipulation de prix

```python
def apply_price_manipulation(base_price, manipulation_type, parameters):
    """
    Applique différents types de manipulation de prix
    """
    if manipulation_type == 'psychological':
        # Prix psychologique (ex: 9.99 au lieu de 10.00)
        return apply_psychological_pricing(base_price)
    
    elif manipulation_type == 'bundle':
        # Prix de bundle
        return calculate_bundle_price(base_price, parameters['bundle_items'])
    
    elif manipulation_type == 'seasonal':
        # Ajustement saisonnier
        return apply_seasonal_adjustment(base_price, parameters['season'])
    
    elif manipulation_type == 'loyalty':
        # Prix fidélité
        return apply_loyalty_discount(base_price, parameters['customer_tier'])
    
    return base_price
```

### 3. Calcul des taxes

```python
def calculate_taxes(price, product_category, customer_country, seller_country):
    """
    Calcule les taxes applicables selon la législation
    """
    tax_rates = {
        'FR': {'food': 0.055, 'alcohol': 0.20, 'default': 0.20},
        'EU': {'food': 0.05, 'alcohol': 0.18, 'default': 0.18},
        'DEFAULT': {'food': 0.0, 'alcohol': 0.0, 'default': 0.0}
    }
    
    # Déterminer le taux applicable
    country_rates = tax_rates.get(customer_country, tax_rates['DEFAULT'])
    tax_rate = country_rates.get(product_category, country_rates['default'])
    
    tax_amount = price * tax_rate
    return {
        'tax_rate': tax_rate,
        'tax_amount': round(tax_amount, 2),
        'price_including_tax': round(price + tax_amount, 2)
    }
```

### 4. Algorithme de concurrence de marché

```python
def analyze_market_competition(product_id):
    """
    Analyse la concurrence pour un produit donné
    """
    competitors = get_competitor_data(product_id)
    our_price = get_current_price(product_id)
    
    analysis = {
        'position': 'unknown',
        'price_difference': 0,
        'recommended_action': 'maintain',
        'confidence_score': 0
    }
    
    if competitors:
        avg_competitor_price = sum(c['price'] for c in competitors) / len(competitors)
        min_competitor_price = min(c['price'] for c in competitors)
        
        # Position sur le marché
        if our_price <= min_competitor_price:
            analysis['position'] = 'leader'
        elif our_price <= avg_competitor_price:
            analysis['position'] = 'competitive'
        else:
            analysis['position'] = 'expensive'
        
        # Recommandation
        price_diff = (our_price - min_competitor_price) / min_competitor_price
        
        if price_diff > 0.1:  # Plus de 10% au-dessus
            analysis['recommended_action'] = 'reduce'
        elif price_diff < -0.05:  # Plus de 5% en dessous
            analysis['recommended_action'] = 'increase'
        
        analysis['price_difference'] = price_diff
        analysis['confidence_score'] = min(len(competitors) / 5.0, 1.0)
    
    return analysis
```

## API Endpoints

### Authentification
- `POST /api/auth/register` - Inscription
- `POST /api/auth/login` - Connexion
- `POST /api/auth/logout` - Déconnexion
- `POST /api/auth/refresh` - Renouvellement token
- `POST /api/auth/forgot-password` - Mot de passe oublié

### Produits
- `GET /api/products` - Liste des produits (avec filtres)
- `GET /api/products/{id}` - Détail d'un produit
- `POST /api/products` - Ajouter un produit (vendeur)
- `PUT /api/products/{id}` - Modifier un produit
- `DELETE /api/products/{id}` - Supprimer un produit
- `POST /api/products/{id}/share` - Partager un produit

### Commandes
- `GET /api/orders` - Mes commandes
- `POST /api/orders` - Créer une commande
- `GET /api/orders/{id}` - Détail d'une commande
- `PUT /api/orders/{id}/status` - Mettre à jour le statut

### Paiements
- `POST /api/payments/create-session` - Créer session Stripe
- `POST /api/payments/webhook` - Webhook Stripe
- `GET /api/payments/success` - Confirmation paiement

### Administration
- `GET /api/admin/dashboard` - Tableau de bord
- `GET /api/admin/logs` - Journaux système
- `POST /api/admin/pricing/recalculate` - Recalculer les prix
- `GET /api/admin/analytics` - Analyses

### Exports
- `GET /api/export/excel` - Export Excel
- `GET /api/export/pdf` - Export PDF
- `POST /api/export/google-sheets` - Export Google Sheets

## Intégrations externes

### Stripe
Configuration pour les paiements sécurisés avec support des devises multiples et des abonnements.

### Google Sheets API
Pour l'export automatique des données de vente et de stock.

### Excel/LibreOffice
Génération de rapports détaillés au format Excel.

### PDF
Génération de factures, bons de livraison et rapports.

## Sécurité

### Authentification et autorisation
- JWT avec refresh tokens
- Hachage bcrypt pour les mots de passe
- Validation des rôles utilisateur
- Protection CSRF

### Protection des données
- Chiffrement des données sensibles
- Validation stricte des entrées
- Protection contre l'injection SQL
- Logs de sécurité

### Conformité
- RGPD pour la protection des données
- Gestion des consentements
- Droit à l'oubli
- Portabilité des données

## Observabilité et logs

### Système de logs
- Logs applicatifs structurés
- Logs de sécurité
- Logs de performance
- Logs d'audit

### Métriques
- Performance des API
- Utilisation des ressources
- Taux de conversion
- Satisfaction client

### Alertes
- Erreurs critiques
- Performance dégradée
- Tentatives de sécurité
- Stock faible

## Déploiement et maintenance

### Environnements
- Développement local
- Test/Staging
- Production

### CI/CD
- Tests automatisés
- Déploiement automatique
- Rollback rapide
- Monitoring continu

### Sauvegarde
- Base de données quotidienne
- Images et fichiers
- Configuration système
- Logs archivés

Cette architecture garantit une application robuste, évolutive et maintenable, adaptée aux besoins spécifiques de la chaîne d'approvisionnement écologique de Kevin Marville.

