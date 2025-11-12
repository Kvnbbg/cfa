"""
Module d'algorithmes de tarification et calculs pour CFA
"""

from src.algorithms.pricing import PricingEngine
from src.algorithms.competition import CompetitionAnalyzer
from src.algorithms.taxes import TaxCalculator
from src.algorithms.demand import DemandPredictor

__all__ = [
    'PricingEngine',
    'CompetitionAnalyzer', 
    'TaxCalculator',
    'DemandPredictor'
]

