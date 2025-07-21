"""
Calculateur de taxes pour CFA
Support international avec serveur basé en France
"""

from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json

class TaxRegion(Enum):
    FRANCE = "FR"
    KOREA = "KR"
    INDIA = "IN"
    CHINA = "CN"
    CARIBBEAN = "CB"
    EU = "EU"
    OTHER = "OTHER"

@dataclass
class TaxCalculation:
    """Résultat du calcul de taxes"""
    base_amount: float
    tax_rate: float
    tax_amount: float
    total_amount: float
    tax_breakdown: Dict[str, float]
    region: TaxRegion
    currency: str
    notes: str

class TaxCalculator:
    """Calculateur de taxes international avec hub France"""
    
    def __init__(self):
        # Taux de TVA par région (serveur France = hub central)
        self.tax_rates = {
            TaxRegion.FRANCE: {
                'food': 0.055,          # Taux réduit alimentaire
                'spices': 0.055,        # Taux réduit
                'herbs': 0.055,         # Taux réduit
                'alcohol': 0.20,        # Taux normal + accises
                'drinks': 0.055,        # Taux réduit
                'medical_herbs': 0.021, # Taux super réduit
                'default': 0.20
            },
            TaxRegion.KOREA: {
                'food': 0.0,            # Exonéré
                'spices': 0.10,         # VAT standard
                'herbs': 0.0,           # Exonéré si médical
                'alcohol': 0.10,        # VAT + taxes spéciales
                'drinks': 0.10,         # VAT standard
                'medical_herbs': 0.0,   # Exonéré
                'default': 0.10
            },
            TaxRegion.INDIA: {
                'food': 0.0,            # Exonéré
                'spices': 0.05,         # GST réduit
                'herbs': 0.05,          # GST réduit
                'alcohol': 0.28,        # GST maximum + taxes état
                'drinks': 0.12,         # GST standard
                'medical_herbs': 0.05,  # GST réduit
                'default': 0.18
            },
            TaxRegion.CHINA: {
                'food': 0.09,           # VAT réduit
                'spices': 0.09,         # VAT réduit
                'herbs': 0.09,          # VAT réduit
                'alcohol': 0.13,        # VAT + taxes consommation
                'drinks': 0.09,         # VAT réduit
                'medical_herbs': 0.09,  # VAT réduit
                'default': 0.13
            },
            TaxRegion.CARIBBEAN: {
                'food': 0.0,            # Généralement exonéré
                'spices': 0.15,         # Taux moyen Caraïbes
                'herbs': 0.10,          # Taux réduit
                'alcohol': 0.25,        # Taux élevé + droits
                'drinks': 0.15,         # Taux standard
                'medical_herbs': 0.0,   # Exonéré
                'default': 0.15
            },
            TaxRegion.EU: {
                'food': 0.05,           # Moyenne UE taux réduit
                'spices': 0.05,         # Moyenne UE taux réduit
                'herbs': 0.05,          # Moyenne UE taux réduit
                'alcohol': 0.20,        # Moyenne UE taux normal
                'drinks': 0.05,         # Moyenne UE taux réduit
                'medical_herbs': 0.05,  # Moyenne UE taux réduit
                'default': 0.20
            }
        }
        
        # Droits de douane (France = hub, donc import/export)
        self.customs_duties = {
            TaxRegion.KOREA: 0.08,      # Accord UE-Corée
            TaxRegion.INDIA: 0.12,      # Droits standards
            TaxRegion.CHINA: 0.15,      # Droits élevés
            TaxRegion.CARIBBEAN: 0.0,   # Préférences ACP
        }
        
        # Frais de transit France (hub central)
        self.transit_fees = {
            'processing': 0.02,         # 2% frais traitement
            'storage': 0.01,            # 1% frais stockage
            'certification': 0.005      # 0.5% certification bio/équitable
        }
    
    def calculate_taxes(self, amount: float, product_category: str,
                       origin_region: TaxRegion, destination_region: TaxRegion,
                       is_organic: bool = False, is_fair_trade: bool = False) -> TaxCalculation:
        """
        Calcule les taxes pour un produit transitant par la France
        """
        tax_breakdown = {}
        total_tax = 0.0
        notes = []
        
        # 1. Droits de douane à l'entrée en France (si hors UE)
        if origin_region not in [TaxRegion.FRANCE, TaxRegion.EU]:
            customs_rate = self.customs_duties.get(origin_region, 0.10)
            customs_amount = amount * customs_rate
            tax_breakdown['customs_duty'] = customs_amount
            total_tax += customs_amount
            notes.append(f"Droits de douane {origin_region.value}: {customs_rate*100:.1f}%")
        
        # 2. Frais de transit France (hub central)
        processing_fee = amount * self.transit_fees['processing']
        storage_fee = amount * self.transit_fees['storage']
        tax_breakdown['france_processing'] = processing_fee
        tax_breakdown['france_storage'] = storage_fee
        total_tax += processing_fee + storage_fee
        notes.append("Frais de transit France (hub central)")
        
        # 3. Certification écologique/équitable (réduction)
        if is_organic or is_fair_trade:
            cert_reduction = amount * self.transit_fees['certification']
            tax_breakdown['eco_certification_bonus'] = -cert_reduction
            total_tax -= cert_reduction
            notes.append("Bonus certification écologique/équitable")
        
        # 4. TVA destination (si livraison finale)
        destination_rates = self.tax_rates.get(destination_region, self.tax_rates[TaxRegion.EU])
        vat_rate = destination_rates.get(product_category, destination_rates['default'])
        
        # Base taxable = montant + droits de douane
        taxable_base = amount + tax_breakdown.get('customs_duty', 0)
        vat_amount = taxable_base * vat_rate
        tax_breakdown['vat'] = vat_amount
        total_tax += vat_amount
        notes.append(f"TVA {destination_region.value}: {vat_rate*100:.1f}%")
        
        # 5. Taxes spéciales alcool
        if product_category == 'alcohol':
            excise_rate = 0.05  # 5% accises moyennes
            excise_amount = amount * excise_rate
            tax_breakdown['excise_duty'] = excise_amount
            total_tax += excise_amount
            notes.append("Droits d'accises sur l'alcool")
        
        # 6. Soutien aux producteurs locaux (réduction)
        if self._is_local_producer_support(origin_region, destination_region):
            local_support = amount * 0.02  # 2% de réduction
            tax_breakdown['local_producer_support'] = -local_support
            total_tax -= local_support
            notes.append("Soutien aux producteurs locaux")
        
        return TaxCalculation(
            base_amount=amount,
            tax_rate=total_tax / amount if amount > 0 else 0,
            tax_amount=round(total_tax, 2),
            total_amount=round(amount + total_tax, 2),
            tax_breakdown=tax_breakdown,
            region=destination_region,
            currency="EUR",  # Hub France = EUR
            notes="; ".join(notes)
        )
    
    def _is_local_producer_support(self, origin: TaxRegion, destination: TaxRegion) -> bool:
        """
        Vérifie si le produit bénéficie du soutien aux producteurs locaux
        (contre les grandes surfaces comme Carrefour/Leclerc)
        """
        # Soutien pour les circuits courts et producteurs directs
        local_circuits = [
            (TaxRegion.CARIBBEAN, TaxRegion.FRANCE),  # Caraïbes -> France
            (TaxRegion.INDIA, TaxRegion.FRANCE),      # Inde -> France
            (TaxRegion.KOREA, TaxRegion.FRANCE),      # Corée -> France
            (TaxRegion.CHINA, TaxRegion.FRANCE),      # Chine -> France
        ]
        return (origin, destination) in local_circuits
    
    def calculate_bulk_taxes(self, items: list) -> Dict[str, TaxCalculation]:
        """
        Calcule les taxes pour plusieurs produits
        """
        results = {}
        
        for item in items:
            try:
                calc = self.calculate_taxes(
                    amount=item['amount'],
                    product_category=item['category'],
                    origin_region=TaxRegion(item['origin']),
                    destination_region=TaxRegion(item['destination']),
                    is_organic=item.get('is_organic', False),
                    is_fair_trade=item.get('is_fair_trade', False)
                )
                results[item['id']] = calc
            except Exception as e:
                print(f"Erreur calcul taxes pour {item['id']}: {e}")
                continue
        
        return results
    
    def get_tax_summary_by_region(self) -> Dict[str, Dict[str, float]]:
        """
        Retourne un résumé des taux de taxes par région
        """
        summary = {}
        
        for region, rates in self.tax_rates.items():
            summary[region.value] = {
                'food_rate': rates.get('food', 0) * 100,
                'alcohol_rate': rates.get('alcohol', 0) * 100,
                'default_rate': rates.get('default', 0) * 100,
                'customs_duty': self.customs_duties.get(region, 0) * 100
            }
        
        return summary
    
    def estimate_total_cost(self, base_price: float, product_category: str,
                          origin: str, destination: str) -> Dict[str, float]:
        """
        Estime le coût total incluant taxes et frais
        """
        try:
            origin_region = TaxRegion(origin)
            dest_region = TaxRegion(destination)
        except ValueError:
            origin_region = TaxRegion.OTHER
            dest_region = TaxRegion.EU
        
        tax_calc = self.calculate_taxes(
            amount=base_price,
            product_category=product_category,
            origin_region=origin_region,
            destination_region=dest_region
        )
        
        # Frais de livraison estimés (basés sur la distance)
        shipping_cost = self._estimate_shipping_cost(origin_region, dest_region, base_price)
        
        return {
            'base_price': base_price,
            'taxes': tax_calc.tax_amount,
            'shipping': shipping_cost,
            'total': base_price + tax_calc.tax_amount + shipping_cost,
            'tax_rate': tax_calc.tax_rate * 100
        }
    
    def _estimate_shipping_cost(self, origin: TaxRegion, destination: TaxRegion, 
                              base_price: float) -> float:
        """
        Estime les frais de livraison selon les régions
        """
        # Frais de base selon la distance (France = hub)
        shipping_rates = {
            TaxRegion.FRANCE: 0.05,      # 5% livraison locale
            TaxRegion.EU: 0.08,           # 8% livraison UE
            TaxRegion.KOREA: 0.15,        # 15% livraison Asie
            TaxRegion.CHINA: 0.15,        # 15% livraison Asie
            TaxRegion.INDIA: 0.12,        # 12% livraison Inde
            TaxRegion.CARIBBEAN: 0.10,    # 10% livraison Caraïbes
        }
        
        rate = shipping_rates.get(destination, 0.10)
        return base_price * rate
    
    def get_anti_monopoly_benefits(self) -> Dict[str, str]:
        """
        Retourne les avantages anti-monopole contre les grandes surfaces
        """
        return {
            'local_producer_support': "Réduction de 2% pour soutenir les producteurs locaux",
            'direct_trade': "Élimination des intermédiaires des grandes surfaces",
            'fair_pricing': "Prix équitables sans marge excessive des supermarchés",
            'quality_guarantee': "Traçabilité directe du producteur au consommateur",
            'ecological_bonus': "Réductions pour produits bio et équitables",
            'cultural_preservation': "Soutien aux variétés locales vs standardisation industrielle"
        }
    
    def calculate_savings_vs_supermarket(self, our_price: float, 
                                       supermarket_price: float) -> Dict[str, any]:
        """
        Calcule les économies par rapport aux grandes surfaces
        """
        savings = supermarket_price - our_price
        savings_percentage = (savings / supermarket_price) * 100 if supermarket_price > 0 else 0
        
        return {
            'our_price': our_price,
            'supermarket_price': supermarket_price,
            'savings_amount': round(savings, 2),
            'savings_percentage': round(savings_percentage, 1),
            'message': f"Économisez {savings:.2f}€ ({savings_percentage:.1f}%) vs grandes surfaces",
            'benefits': [
                "Prix direct producteur",
                "Qualité supérieure",
                "Soutien aux producteurs locaux",
                "Traçabilité complète"
            ]
        }

