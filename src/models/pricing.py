"""
Algorithme de tarification dynamique pour CFA
Inclut réduction de prix, manipulation de prix, et optimisation écologique
"""

import math
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class PricingFactors:
    """Facteurs utilisés pour le calcul de prix"""
    base_price: float
    competitor_price: Optional[float] = None
    stock_level: float = 1.0  # 0-1 (0 = rupture, 1 = stock plein)
    demand_factor: float = 0.5  # 0-1 (0 = faible demande, 1 = forte demande)
    ecology_score: int = 50  # 0-100
    seasonality: float = 1.0  # Facteur saisonnier
    customer_tier: str = "standard"  # standard, premium, vip
    product_age_days: int = 0  # Âge du produit en jours
    margin_target: float = 0.3  # Marge cible (30%)

@dataclass
class PricingResult:
    """Résultat du calcul de prix"""
    final_price: float
    original_price: float
    discount_amount: float
    discount_percentage: float
    factors_applied: Dict[str, float]
    algorithm_used: str
    confidence_score: float
    reasoning: List[str]

class PricingEngine:
    """Moteur de tarification dynamique avancé"""
    
    def __init__(self):
        self.algorithms = {
            'dynamic': self._dynamic_pricing,
            'competitive': self._competitive_pricing,
            'psychological': self._psychological_pricing,
            'ecological': self._ecological_pricing,
            'seasonal': self._seasonal_pricing,
            'clearance': self._clearance_pricing,
            'premium': self._premium_pricing
        }
        
        # Coefficients par défaut
        self.default_weights = {
            'competitor': 0.35,
            'stock': 0.20,
            'demand': 0.25,
            'ecology': 0.15,
            'seasonality': 0.05
        }
    
    def calculate_optimal_price(self, factors: PricingFactors, 
                              algorithm: str = 'dynamic') -> PricingResult:
        """
        Calcule le prix optimal selon l'algorithme spécifié
        """
        if algorithm not in self.algorithms:
            algorithm = 'dynamic'
        
        return self.algorithms[algorithm](factors)
    
    def _dynamic_pricing(self, factors: PricingFactors) -> PricingResult:
        """
        Algorithme de tarification dynamique principal
        Combine tous les facteurs avec pondération intelligente
        """
        reasoning = []
        factors_applied = {}
        
        # Prix de base
        current_price = factors.base_price
        reasoning.append(f"Prix de base: {current_price:.2f}€")
        
        # Facteur concurrentiel
        competitor_factor = 1.0
        if factors.competitor_price:
            if factors.competitor_price < factors.base_price:
                # Concurrence moins chère - ajuster à la baisse
                competitor_factor = min(1.0, factors.competitor_price / factors.base_price * 0.95)
                reasoning.append(f"Concurrence détectée à {factors.competitor_price:.2f}€ - réduction de 5%")
            else:
                # Nous sommes moins chers - légère augmentation possible
                competitor_factor = min(1.1, factors.competitor_price / factors.base_price * 1.02)
                reasoning.append(f"Prix concurrentiel favorable - légère augmentation")
        
        factors_applied['competitor'] = competitor_factor
        
        # Facteur de stock (stock faible = prix plus élevé)
        stock_factor = 1.0 + (1.0 - factors.stock_level) * 0.25
        if factors.stock_level < 0.2:
            reasoning.append(f"Stock très faible ({factors.stock_level*100:.0f}%) - augmentation urgence")
        elif factors.stock_level > 0.8:
            reasoning.append(f"Stock élevé ({factors.stock_level*100:.0f}%) - prix stable")
        
        factors_applied['stock'] = stock_factor
        
        # Facteur de demande
        demand_factor = 1.0 + factors.demand_factor * 0.3
        if factors.demand_factor > 0.7:
            reasoning.append(f"Forte demande ({factors.demand_factor*100:.0f}%) - augmentation")
        elif factors.demand_factor < 0.3:
            reasoning.append(f"Faible demande ({factors.demand_factor*100:.0f}%) - réduction")
        
        factors_applied['demand'] = demand_factor
        
        # Bonus écologique (score élevé = réduction pour encourager)
        ecology_factor = 1.0 - (factors.ecology_score / 100) * 0.15
        if factors.ecology_score > 80:
            reasoning.append(f"Excellent score écologique ({factors.ecology_score}) - bonus client")
        elif factors.ecology_score < 40:
            reasoning.append(f"Score écologique faible ({factors.ecology_score}) - prix standard")
        
        factors_applied['ecology'] = ecology_factor
        
        # Facteur saisonnier
        seasonal_factor = factors.seasonality
        if seasonal_factor > 1.1:
            reasoning.append(f"Saison haute - augmentation saisonnière")
        elif seasonal_factor < 0.9:
            reasoning.append(f"Saison basse - réduction saisonnière")
        
        factors_applied['seasonality'] = seasonal_factor
        
        # Calcul du prix final avec pondération
        weights = self.default_weights
        final_price = factors.base_price * (
            competitor_factor * weights['competitor'] +
            stock_factor * weights['stock'] +
            demand_factor * weights['demand'] +
            ecology_factor * weights['ecology'] +
            seasonal_factor * weights['seasonality']
        )
        
        # Ajustements finaux
        final_price = self._apply_pricing_rules(final_price, factors)
        
        # Calcul des métriques
        discount_amount = factors.base_price - final_price
        discount_percentage = (discount_amount / factors.base_price) * 100 if factors.base_price > 0 else 0
        
        # Score de confiance basé sur la disponibilité des données
        confidence_score = self._calculate_confidence(factors)
        
        return PricingResult(
            final_price=round(final_price, 2),
            original_price=factors.base_price,
            discount_amount=round(discount_amount, 2),
            discount_percentage=round(discount_percentage, 2),
            factors_applied=factors_applied,
            algorithm_used='dynamic',
            confidence_score=confidence_score,
            reasoning=reasoning
        )
    
    def _competitive_pricing(self, factors: PricingFactors) -> PricingResult:
        """
        Algorithme de tarification concurrentielle agressive
        """
        reasoning = []
        
        if not factors.competitor_price:
            # Pas de données concurrentielles - utiliser l'algorithme dynamique
            return self._dynamic_pricing(factors)
        
        # Stratégie agressive : battre la concurrence de 3-7%
        reduction_percentage = random.uniform(0.03, 0.07)
        final_price = factors.competitor_price * (1 - reduction_percentage)
        
        # S'assurer de maintenir une marge minimale
        min_price = factors.base_price * 0.7  # Marge minimale de 30%
        final_price = max(final_price, min_price)
        
        reasoning.append(f"Prix concurrent: {factors.competitor_price:.2f}€")
        reasoning.append(f"Réduction concurrentielle: {reduction_percentage*100:.1f}%")
        reasoning.append(f"Prix final: {final_price:.2f}€")
        
        discount_amount = factors.base_price - final_price
        discount_percentage = (discount_amount / factors.base_price) * 100
        
        return PricingResult(
            final_price=round(final_price, 2),
            original_price=factors.base_price,
            discount_amount=round(discount_amount, 2),
            discount_percentage=round(discount_percentage, 2),
            factors_applied={'competitive_reduction': reduction_percentage},
            algorithm_used='competitive',
            confidence_score=0.8,
            reasoning=reasoning
        )
    
    def _psychological_pricing(self, factors: PricingFactors) -> PricingResult:
        """
        Algorithme de tarification psychologique
        """
        reasoning = []
        
        # Commencer avec le prix dynamique
        base_result = self._dynamic_pricing(factors)
        price = base_result.final_price
        
        # Appliquer les règles psychologiques
        if price >= 10:
            # Prix se terminant par .99, .95, .89
            endings = [0.99, 0.95, 0.89]
            integer_part = int(price)
            
            # Choisir la terminaison qui se rapproche le plus du prix calculé
            best_ending = min(endings, key=lambda x: abs(price - (integer_part + x)))
            psychological_price = integer_part + best_ending
            
            reasoning.append(f"Prix calculé: {price:.2f}€")
            reasoning.append(f"Prix psychologique: {psychological_price:.2f}€")
        else:
            # Pour les petits prix, arrondir à .49, .79, .99
            if price < 5:
                psychological_price = math.floor(price) + 0.49
            else:
                psychological_price = math.floor(price) + 0.79
            
            reasoning.append(f"Petit prix ajusté: {psychological_price:.2f}€")
        
        # S'assurer que le prix psychologique n'est pas trop éloigné du prix calculé
        if abs(psychological_price - price) / price > 0.1:  # Plus de 10% d'écart
            psychological_price = price  # Garder le prix calculé
            reasoning.append("Écart trop important - prix calculé conservé")
        
        discount_amount = factors.base_price - psychological_price
        discount_percentage = (discount_amount / factors.base_price) * 100
        
        return PricingResult(
            final_price=round(psychological_price, 2),
            original_price=factors.base_price,
            discount_amount=round(discount_amount, 2),
            discount_percentage=round(discount_percentage, 2),
            factors_applied=base_result.factors_applied,
            algorithm_used='psychological',
            confidence_score=base_result.confidence_score,
            reasoning=base_result.reasoning + reasoning
        )
    
    def _ecological_pricing(self, factors: PricingFactors) -> PricingResult:
        """
        Algorithme de tarification écologique
        Favorise les produits avec un bon score écologique
        """
        reasoning = []
        
        # Bonus/malus basé sur le score écologique
        if factors.ecology_score >= 80:
            eco_factor = 0.85  # 15% de réduction pour excellent score
            reasoning.append(f"Excellent score écologique ({factors.ecology_score}) - 15% de réduction")
        elif factors.ecology_score >= 60:
            eco_factor = 0.92  # 8% de réduction pour bon score
            reasoning.append(f"Bon score écologique ({factors.ecology_score}) - 8% de réduction")
        elif factors.ecology_score >= 40:
            eco_factor = 1.0   # Prix normal
            reasoning.append(f"Score écologique moyen ({factors.ecology_score}) - prix standard")
        else:
            eco_factor = 1.1   # 10% d'augmentation pour mauvais score
            reasoning.append(f"Score écologique faible ({factors.ecology_score}) - 10% d'augmentation")
        
        final_price = factors.base_price * eco_factor
        
        # Ajuster selon la demande pour les produits écologiques
        if factors.ecology_score > 70 and factors.demand_factor > 0.6:
            final_price *= 1.05  # Légère augmentation si forte demande pour produit écologique
            reasoning.append("Forte demande pour produit écologique - ajustement +5%")
        
        discount_amount = factors.base_price - final_price
        discount_percentage = (discount_amount / factors.base_price) * 100
        
        return PricingResult(
            final_price=round(final_price, 2),
            original_price=factors.base_price,
            discount_amount=round(discount_amount, 2),
            discount_percentage=round(discount_percentage, 2),
            factors_applied={'ecology': eco_factor},
            algorithm_used='ecological',
            confidence_score=0.9,
            reasoning=reasoning
        )
    
    def _seasonal_pricing(self, factors: PricingFactors) -> PricingResult:
        """
        Algorithme de tarification saisonnière
        """
        reasoning = []
        
        # Déterminer la saison actuelle
        month = datetime.now().month
        
        # Facteurs saisonniers pour produits exotiques
        if month in [12, 1, 2]:  # Hiver
            seasonal_factor = 1.15  # Augmentation hivernale pour produits exotiques
            reasoning.append("Saison hivernale - augmentation pour produits exotiques (+15%)")
        elif month in [6, 7, 8]:  # Été
            seasonal_factor = 1.05  # Légère augmentation estivale
            reasoning.append("Saison estivale - légère augmentation (+5%)")
        elif month in [11, 12]:  # Période des fêtes
            seasonal_factor = 1.25  # Forte augmentation pour les fêtes
            reasoning.append("Période des fêtes - forte augmentation (+25%)")
        else:
            seasonal_factor = factors.seasonality
            reasoning.append(f"Facteur saisonnier standard: {seasonal_factor}")
        
        final_price = factors.base_price * seasonal_factor
        
        # Ajustements selon le type de produit (simulé par ecology_score)
        if factors.ecology_score > 80:  # Produits premium
            final_price *= 1.1
            reasoning.append("Produit premium - majoration +10%")
        
        discount_amount = factors.base_price - final_price
        discount_percentage = (discount_amount / factors.base_price) * 100
        
        return PricingResult(
            final_price=round(final_price, 2),
            original_price=factors.base_price,
            discount_amount=round(discount_amount, 2),
            discount_percentage=round(discount_percentage, 2),
            factors_applied={'seasonal': seasonal_factor},
            algorithm_used='seasonal',
            confidence_score=0.7,
            reasoning=reasoning
        )
    
    def _clearance_pricing(self, factors: PricingFactors) -> PricingResult:
        """
        Algorithme de liquidation pour produits en fin de vie
        """
        reasoning = []
        
        # Réductions basées sur l'âge du produit et le stock
        age_factor = min(factors.product_age_days / 30, 3)  # Max 3 mois
        stock_urgency = 1 - factors.stock_level
        
        # Calcul de la réduction de liquidation
        clearance_reduction = 0.2 + (age_factor * 0.1) + (stock_urgency * 0.3)
        clearance_reduction = min(clearance_reduction, 0.7)  # Max 70% de réduction
        
        final_price = factors.base_price * (1 - clearance_reduction)
        
        reasoning.append(f"Âge du produit: {factors.product_age_days} jours")
        reasoning.append(f"Niveau de stock: {factors.stock_level*100:.0f}%")
        reasoning.append(f"Réduction de liquidation: {clearance_reduction*100:.0f}%")
        
        discount_amount = factors.base_price - final_price
        discount_percentage = (discount_amount / factors.base_price) * 100
        
        return PricingResult(
            final_price=round(final_price, 2),
            original_price=factors.base_price,
            discount_amount=round(discount_amount, 2),
            discount_percentage=round(discount_percentage, 2),
            factors_applied={'clearance_reduction': clearance_reduction},
            algorithm_used='clearance',
            confidence_score=0.95,
            reasoning=reasoning
        )
    
    def _premium_pricing(self, factors: PricingFactors) -> PricingResult:
        """
        Algorithme de tarification premium pour clients VIP
        """
        reasoning = []
        
        # Réductions selon le niveau client
        if factors.customer_tier == "vip":
            tier_discount = 0.15  # 15% pour VIP
            reasoning.append("Client VIP - réduction de 15%")
        elif factors.customer_tier == "premium":
            tier_discount = 0.10  # 10% pour Premium
            reasoning.append("Client Premium - réduction de 10%")
        else:
            tier_discount = 0.05  # 5% pour fidélité
            reasoning.append("Client fidèle - réduction de 5%")
        
        final_price = factors.base_price * (1 - tier_discount)
        
        # Bonus supplémentaire pour produits écologiques
        if factors.ecology_score > 70:
            eco_bonus = 0.05
            final_price *= (1 - eco_bonus)
            reasoning.append(f"Bonus écologique supplémentaire: {eco_bonus*100:.0f}%")
        
        discount_amount = factors.base_price - final_price
        discount_percentage = (discount_amount / factors.base_price) * 100
        
        return PricingResult(
            final_price=round(final_price, 2),
            original_price=factors.base_price,
            discount_amount=round(discount_amount, 2),
            discount_percentage=round(discount_percentage, 2),
            factors_applied={'tier_discount': tier_discount},
            algorithm_used='premium',
            confidence_score=0.9,
            reasoning=reasoning
        )
    
    def _apply_pricing_rules(self, price: float, factors: PricingFactors) -> float:
        """
        Applique les règles métier de tarification
        """
        # Prix minimum (marge minimale)
        min_price = factors.base_price * 0.5
        price = max(price, min_price)
        
        # Prix maximum (éviter les prix excessifs)
        max_price = factors.base_price * 2.0
        price = min(price, max_price)
        
        return price
    
    def _calculate_confidence(self, factors: PricingFactors) -> float:
        """
        Calcule un score de confiance basé sur la disponibilité des données
        """
        confidence = 0.5  # Base
        
        if factors.competitor_price:
            confidence += 0.2
        if factors.stock_level > 0:
            confidence += 0.1
        if factors.demand_factor > 0:
            confidence += 0.1
        if factors.ecology_score > 0:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def bulk_price_update(self, products_factors: List[Tuple[int, PricingFactors]], 
                         algorithm: str = 'dynamic') -> Dict[int, PricingResult]:
        """
        Mise à jour en lot des prix pour plusieurs produits
        """
        results = {}
        
        for product_id, factors in products_factors:
            try:
                result = self.calculate_optimal_price(factors, algorithm)
                results[product_id] = result
            except Exception as e:
                # Log l'erreur et continuer avec les autres produits
                print(f"Erreur lors du calcul de prix pour le produit {product_id}: {e}")
                continue
        
        return results
    
    def simulate_price_scenarios(self, factors: PricingFactors) -> Dict[str, PricingResult]:
        """
        Simule différents scénarios de tarification
        """
        scenarios = {}
        
        for algorithm_name in self.algorithms.keys():
            try:
                result = self.calculate_optimal_price(factors, algorithm_name)
                scenarios[algorithm_name] = result
            except Exception as e:
                print(f"Erreur simulation {algorithm_name}: {e}")
                continue
        
        return scenarios

