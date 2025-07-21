"""
Algorithme d'analyse de la concurrence pour CFA
Surveille les prix concurrents et recommande des ajustements
"""

import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class CompetitivePosition(Enum):
    LEADER = "leader"           # Prix le plus bas
    COMPETITIVE = "competitive" # Dans la moyenne
    EXPENSIVE = "expensive"     # Plus cher que la moyenne
    PREMIUM = "premium"         # Positionnement premium assumé

class MarketTrend(Enum):
    RISING = "rising"           # Tendance à la hausse
    FALLING = "falling"         # Tendance à la baisse
    STABLE = "stable"           # Prix stables
    VOLATILE = "volatile"       # Prix très variables

@dataclass
class CompetitorData:
    """Données d'un concurrent"""
    name: str
    price: float
    url: Optional[str] = None
    last_updated: Optional[datetime] = None
    availability: bool = True
    shipping_cost: float = 0.0
    rating: Optional[float] = None
    review_count: Optional[int] = None

@dataclass
class MarketAnalysis:
    """Analyse du marché concurrentiel"""
    our_price: float
    competitor_count: int
    min_price: float
    max_price: float
    avg_price: float
    median_price: float
    our_position: CompetitivePosition
    market_trend: MarketTrend
    price_gap: float  # Écart avec le prix moyen
    recommended_action: str
    confidence_score: float
    insights: List[str]

class CompetitionAnalyzer:
    """Analyseur de concurrence avancé"""
    
    def __init__(self):
        self.price_history = {}  # Historique des prix par concurrent
        self.market_segments = {
            'budget': (0, 20),
            'mid_range': (20, 50),
            'premium': (50, 100),
            'luxury': (100, float('inf'))
        }
    
    def analyze_market_position(self, our_price: float, 
                              competitors: List[CompetitorData],
                              product_name: str = "") -> MarketAnalysis:
        """
        Analyse la position concurrentielle d'un produit
        """
        if not competitors:
            return self._create_no_competition_analysis(our_price)
        
        # Filtrer les concurrents avec des prix valides
        valid_competitors = [c for c in competitors if c.price > 0 and c.availability]
        
        if not valid_competitors:
            return self._create_no_competition_analysis(our_price)
        
        # Calculs statistiques de base
        competitor_prices = [c.price for c in valid_competitors]
        min_price = min(competitor_prices)
        max_price = max(competitor_prices)
        avg_price = statistics.mean(competitor_prices)
        median_price = statistics.median(competitor_prices)
        
        # Déterminer notre position
        position = self._determine_position(our_price, competitor_prices)
        
        # Analyser la tendance du marché
        trend = self._analyze_market_trend(valid_competitors, product_name)
        
        # Calculer l'écart avec la moyenne
        price_gap = our_price - avg_price
        price_gap_percentage = (price_gap / avg_price) * 100 if avg_price > 0 else 0
        
        # Générer des insights
        insights = self._generate_insights(our_price, valid_competitors, position, trend)
        
        # Recommandation d'action
        recommended_action = self._recommend_action(position, trend, price_gap_percentage)
        
        # Score de confiance
        confidence_score = self._calculate_confidence_score(valid_competitors)
        
        return MarketAnalysis(
            our_price=our_price,
            competitor_count=len(valid_competitors),
            min_price=min_price,
            max_price=max_price,
            avg_price=avg_price,
            median_price=median_price,
            our_position=position,
            market_trend=trend,
            price_gap=price_gap,
            recommended_action=recommended_action,
            confidence_score=confidence_score,
            insights=insights
        )
    
    def _determine_position(self, our_price: float, competitor_prices: List[float]) -> CompetitivePosition:
        """Détermine notre position concurrentielle"""
        min_price = min(competitor_prices)
        avg_price = statistics.mean(competitor_prices)
        
        if our_price <= min_price:
            return CompetitivePosition.LEADER
        elif our_price <= avg_price * 1.1:  # Dans les 10% de la moyenne
            return CompetitivePosition.COMPETITIVE
        elif our_price <= avg_price * 1.3:  # Jusqu'à 30% au-dessus
            return CompetitivePosition.EXPENSIVE
        else:
            return CompetitivePosition.PREMIUM
    
    def _analyze_market_trend(self, competitors: List[CompetitorData], 
                            product_name: str) -> MarketTrend:
        """Analyse la tendance du marché"""
        # Simuler l'analyse de tendance basée sur l'historique
        # Dans une vraie implémentation, ceci utiliserait des données historiques
        
        prices = [c.price for c in competitors]
        price_variance = statistics.variance(prices) if len(prices) > 1 else 0
        avg_price = statistics.mean(prices)
        
        # Coefficient de variation pour mesurer la volatilité
        cv = (price_variance ** 0.5) / avg_price if avg_price > 0 else 0
        
        if cv > 0.3:  # Forte variation
            return MarketTrend.VOLATILE
        elif cv > 0.15:  # Variation modérée
            # Simuler une tendance basée sur d'autres facteurs
            return MarketTrend.RISING if len(competitors) > 3 else MarketTrend.FALLING
        else:
            return MarketTrend.STABLE
    
    def _generate_insights(self, our_price: float, competitors: List[CompetitorData],
                          position: CompetitivePosition, trend: MarketTrend) -> List[str]:
        """Génère des insights sur le marché"""
        insights = []
        
        # Insights sur la position
        if position == CompetitivePosition.LEADER:
            insights.append("🏆 Vous avez le prix le plus compétitif du marché")
        elif position == CompetitivePosition.COMPETITIVE:
            insights.append("✅ Votre prix est dans la moyenne du marché")
        elif position == CompetitivePosition.EXPENSIVE:
            insights.append("⚠️ Votre prix est au-dessus de la moyenne")
        else:
            insights.append("💎 Positionnement premium par rapport au marché")
        
        # Insights sur la tendance
        if trend == MarketTrend.RISING:
            insights.append("📈 Le marché montre une tendance à la hausse")
        elif trend == MarketTrend.FALLING:
            insights.append("📉 Le marché montre une tendance à la baisse")
        elif trend == MarketTrend.VOLATILE:
            insights.append("🌊 Le marché est très volatil")
        else:
            insights.append("📊 Le marché est stable")
        
        # Insights sur les concurrents
        competitor_count = len(competitors)
        if competitor_count > 10:
            insights.append(f"🏪 Marché très concurrentiel avec {competitor_count} concurrents")
        elif competitor_count > 5:
            insights.append(f"🏬 Marché modérément concurrentiel avec {competitor_count} concurrents")
        else:
            insights.append(f"🏪 Marché peu concurrentiel avec {competitor_count} concurrents")
        
        # Insights sur les prix
        prices = [c.price for c in competitors]
        price_range = max(prices) - min(prices)
        avg_price = statistics.mean(prices)
        
        if price_range / avg_price > 0.5:  # Écart de plus de 50%
            insights.append("💰 Large éventail de prix sur le marché")
        
        # Insights sur les concurrents avec de bons ratings
        rated_competitors = [c for c in competitors if c.rating and c.rating > 4.0]
        if rated_competitors:
            avg_rated_price = statistics.mean([c.price for c in rated_competitors])
            if our_price < avg_rated_price:
                insights.append("⭐ Votre prix est inférieur aux concurrents bien notés")
        
        return insights
    
    def _recommend_action(self, position: CompetitivePosition, trend: MarketTrend,
                         price_gap_percentage: float) -> str:
        """Recommande une action basée sur l'analyse"""
        
        if position == CompetitivePosition.LEADER:
            if trend == MarketTrend.RISING:
                return "Maintenir le prix ou légère augmentation possible"
            else:
                return "Maintenir la position de leader"
        
        elif position == CompetitivePosition.COMPETITIVE:
            if trend == MarketTrend.RISING:
                return "Suivre la tendance du marché"
            elif trend == MarketTrend.FALLING:
                return "Surveiller et ajuster si nécessaire"
            else:
                return "Prix optimal, maintenir"
        
        elif position == CompetitivePosition.EXPENSIVE:
            if price_gap_percentage > 20:
                return "Réduction de prix recommandée"
            else:
                return "Surveiller la concurrence de près"
        
        else:  # PREMIUM
            return "Justifier la valeur premium ou repositionner"
    
    def _calculate_confidence_score(self, competitors: List[CompetitorData]) -> float:
        """Calcule un score de confiance pour l'analyse"""
        score = 0.5  # Base
        
        # Plus de concurrents = plus de confiance
        competitor_count = len(competitors)
        if competitor_count >= 5:
            score += 0.3
        elif competitor_count >= 3:
            score += 0.2
        else:
            score += 0.1
        
        # Données récentes = plus de confiance
        recent_data = [c for c in competitors if c.last_updated and 
                      (datetime.now() - c.last_updated).days <= 7]
        if len(recent_data) / len(competitors) > 0.8:
            score += 0.2
        
        return min(score, 1.0)
    
    def _create_no_competition_analysis(self, our_price: float) -> MarketAnalysis:
        """Crée une analyse quand il n'y a pas de concurrents"""
        return MarketAnalysis(
            our_price=our_price,
            competitor_count=0,
            min_price=our_price,
            max_price=our_price,
            avg_price=our_price,
            median_price=our_price,
            our_position=CompetitivePosition.LEADER,
            market_trend=MarketTrend.STABLE,
            price_gap=0.0,
            recommended_action="Aucune concurrence détectée - prix libre",
            confidence_score=0.3,
            insights=["🎯 Aucun concurrent direct identifié", 
                     "🚀 Opportunité de définir le prix du marché"]
        )
    
    def find_price_opportunities(self, our_price: float, 
                               competitors: List[CompetitorData]) -> Dict[str, float]:
        """
        Identifie les opportunités de tarification
        """
        opportunities = {}
        
        if not competitors:
            return opportunities
        
        prices = [c.price for c in competitors if c.price > 0]
        if not prices:
            return opportunities
        
        min_price = min(prices)
        avg_price = statistics.mean(prices)
        
        # Prix pour être leader
        opportunities['leader_price'] = min_price * 0.95
        
        # Prix pour être compétitif
        opportunities['competitive_price'] = avg_price * 0.98
        
        # Prix optimal basé sur la distribution
        if len(prices) > 2:
            # Prix au 25e percentile
            sorted_prices = sorted(prices)
            q1_index = len(sorted_prices) // 4
            opportunities['aggressive_price'] = sorted_prices[q1_index]
        
        # Prix de pénétration (10% sous le minimum)
        opportunities['penetration_price'] = min_price * 0.90
        
        return opportunities
    
    def simulate_price_impact(self, current_price: float, new_price: float,
                            competitors: List[CompetitorData]) -> Dict[str, any]:
        """
        Simule l'impact d'un changement de prix
        """
        current_analysis = self.analyze_market_position(current_price, competitors)
        new_analysis = self.analyze_market_position(new_price, competitors)
        
        return {
            'current_position': current_analysis.our_position.value,
            'new_position': new_analysis.our_position.value,
            'position_change': new_analysis.our_position != current_analysis.our_position,
            'price_change_percentage': ((new_price - current_price) / current_price) * 100,
            'market_gap_change': new_analysis.price_gap - current_analysis.price_gap,
            'recommendation': new_analysis.recommended_action
        }
    
    def get_competitive_alerts(self, our_price: float, 
                             competitors: List[CompetitorData]) -> List[str]:
        """
        Génère des alertes concurrentielles
        """
        alerts = []
        
        if not competitors:
            return alerts
        
        # Alerte si un concurrent est significativement moins cher
        min_competitor_price = min(c.price for c in competitors if c.price > 0)
        if min_competitor_price < our_price * 0.8:  # 20% moins cher
            alerts.append(f"🚨 Concurrent avec prix 20% inférieur: {min_competitor_price:.2f}€")
        
        # Alerte si beaucoup de concurrents sont moins chers
        cheaper_competitors = [c for c in competitors if c.price < our_price]
        if len(cheaper_competitors) / len(competitors) > 0.7:  # Plus de 70%
            alerts.append("⚠️ Plus de 70% des concurrents ont un prix inférieur")
        
        # Alerte sur les concurrents bien notés et moins chers
        good_rated_cheaper = [c for c in competitors 
                            if c.price < our_price and c.rating and c.rating > 4.0]
        if good_rated_cheaper:
            alerts.append(f"⭐ {len(good_rated_cheaper)} concurrent(s) bien noté(s) et moins cher(s)")
        
        return alerts
    
    def export_competitive_report(self, analysis: MarketAnalysis, 
                                competitors: List[CompetitorData]) -> Dict[str, any]:
        """
        Exporte un rapport concurrentiel complet
        """
        return {
            'summary': {
                'our_price': analysis.our_price,
                'position': analysis.our_position.value,
                'competitor_count': analysis.competitor_count,
                'market_trend': analysis.market_trend.value,
                'confidence': analysis.confidence_score
            },
            'market_stats': {
                'min_price': analysis.min_price,
                'max_price': analysis.max_price,
                'avg_price': analysis.avg_price,
                'median_price': analysis.median_price,
                'price_gap': analysis.price_gap
            },
            'competitors': [
                {
                    'name': c.name,
                    'price': c.price,
                    'rating': c.rating,
                    'availability': c.availability
                } for c in competitors
            ],
            'insights': analysis.insights,
            'recommendation': analysis.recommended_action,
            'opportunities': self.find_price_opportunities(analysis.our_price, competitors),
            'alerts': self.get_competitive_alerts(analysis.our_price, competitors)
        }

