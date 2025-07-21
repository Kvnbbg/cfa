"""
Système de gamification et récompenses numériques pour CFA
Encourage l'engagement utilisateur et le soutien aux producteurs locaux
"""

import json
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from src.models.base import BaseModel, db
from sqlalchemy import JSON

class RewardType(Enum):
    POINTS = "points"
    BADGE = "badge"
    DISCOUNT = "discount"
    CASHBACK = "cashback"
    EXPERIENCE = "experience"
    ACHIEVEMENT = "achievement"

class ActionType(Enum):
    PURCHASE = "purchase"
    REVIEW = "review"
    REFERRAL = "referral"
    RECIPE_SHARE = "recipe_share"
    LOCAL_SUPPORT = "local_support"
    ECO_CHOICE = "eco_choice"
    DAILY_LOGIN = "daily_login"
    SOCIAL_SHARE = "social_share"
    QUIZ_COMPLETE = "quiz_complete"
    STREAK_MAINTAIN = "streak_maintain"

@dataclass
class RewardRule:
    """Règle de récompense"""
    action: ActionType
    points: int
    multiplier: float = 1.0
    conditions: Dict = None
    cooldown_hours: int = 0
    max_per_day: Optional[int] = None

class UserReward(BaseModel):
    """Récompenses utilisateur"""
    __tablename__ = 'user_rewards'
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    reward_type = db.Column(db.Enum(RewardType), nullable=False)
    action_type = db.Column(db.Enum(ActionType), nullable=False)
    
    # Valeurs de récompense
    points_earned = db.Column(db.Integer, default=0)
    badge_name = db.Column(db.String(100))
    discount_percentage = db.Column(db.Float)
    cashback_amount = db.Column(db.Numeric(10, 2))
    experience_points = db.Column(db.Integer, default=0)
    
    # Métadonnées
    description = db.Column(db.Text)
    metadata = db.Column(JSON)
    expires_at = db.Column(db.DateTime)
    is_claimed = db.Column(db.Boolean, default=False)
    claimed_at = db.Column(db.DateTime)

class UserStats(BaseModel):
    """Statistiques utilisateur pour gamification"""
    __tablename__ = 'user_stats'
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    
    # Points et niveaux
    total_points = db.Column(db.Integer, default=0)
    current_level = db.Column(db.Integer, default=1)
    experience_points = db.Column(db.Integer, default=0)
    
    # Streaks et engagement
    login_streak = db.Column(db.Integer, default=0)
    purchase_streak = db.Column(db.Integer, default=0)
    last_login = db.Column(db.DateTime)
    last_purchase = db.Column(db.DateTime)
    
    # Compteurs d'actions
    total_purchases = db.Column(db.Integer, default=0)
    total_reviews = db.Column(db.Integer, default=0)
    total_referrals = db.Column(db.Integer, default=0)
    recipes_shared = db.Column(db.Integer, default=0)
    local_products_bought = db.Column(db.Integer, default=0)
    eco_products_bought = db.Column(db.Integer, default=0)
    
    # Badges et achievements
    badges_earned = db.Column(JSON, default=list)
    achievements = db.Column(JSON, default=list)
    
    # Récompenses disponibles
    available_points = db.Column(db.Integer, default=0)
    pending_cashback = db.Column(db.Numeric(10, 2), default=0)

class GamificationEngine:
    """Moteur de gamification intelligent"""
    
    def __init__(self):
        self.reward_rules = self._initialize_reward_rules()
        self.level_thresholds = self._initialize_level_system()
        self.badges = self._initialize_badges()
        self.achievements = self._initialize_achievements()
    
    def _initialize_reward_rules(self) -> Dict[ActionType, RewardRule]:
        """Initialise les règles de récompenses"""
        return {
            ActionType.PURCHASE: RewardRule(
                action=ActionType.PURCHASE,
                points=10,
                multiplier=1.0,
                conditions={'min_amount': 20}
            ),
            ActionType.REVIEW: RewardRule(
                action=ActionType.REVIEW,
                points=25,
                max_per_day=5,
                cooldown_hours=1
            ),
            ActionType.REFERRAL: RewardRule(
                action=ActionType.REFERRAL,
                points=100,
                conditions={'successful_signup': True}
            ),
            ActionType.RECIPE_SHARE: RewardRule(
                action=ActionType.RECIPE_SHARE,
                points=50,
                max_per_day=3
            ),
            ActionType.LOCAL_SUPPORT: RewardRule(
                action=ActionType.LOCAL_SUPPORT,
                points=30,
                multiplier=1.5,  # Bonus pour soutien local
                conditions={'local_producer': True}
            ),
            ActionType.ECO_CHOICE: RewardRule(
                action=ActionType.ECO_CHOICE,
                points=20,
                multiplier=1.2,
                conditions={'ecology_score': 70}
            ),
            ActionType.DAILY_LOGIN: RewardRule(
                action=ActionType.DAILY_LOGIN,
                points=5,
                max_per_day=1
            ),
            ActionType.SOCIAL_SHARE: RewardRule(
                action=ActionType.SOCIAL_SHARE,
                points=15,
                max_per_day=3
            ),
            ActionType.QUIZ_COMPLETE: RewardRule(
                action=ActionType.QUIZ_COMPLETE,
                points=40,
                conditions={'min_score': 80}
            ),
            ActionType.STREAK_MAINTAIN: RewardRule(
                action=ActionType.STREAK_MAINTAIN,
                points=0,  # Calculé dynamiquement
                multiplier=1.0
            )
        }
    
    def _initialize_level_system(self) -> Dict[int, Dict]:
        """Initialise le système de niveaux"""
        levels = {}
        for level in range(1, 101):  # 100 niveaux max
            # Progression exponentielle modérée
            xp_required = int(100 * (level ** 1.5))
            
            levels[level] = {
                'xp_required': xp_required,
                'title': self._get_level_title(level),
                'benefits': self._get_level_benefits(level),
                'badge': f"level_{level}"
            }
        
        return levels
    
    def _get_level_title(self, level: int) -> str:
        """Retourne le titre du niveau"""
        if level < 5:
            return "Explorateur"
        elif level < 10:
            return "Découvreur"
        elif level < 20:
            return "Connaisseur"
        elif level < 35:
            return "Expert"
        elif level < 50:
            return "Maître"
        elif level < 75:
            return "Ambassadeur"
        else:
            return "Légende CFA"
    
    def _get_level_benefits(self, level: int) -> List[str]:
        """Retourne les avantages du niveau"""
        benefits = []
        
        if level >= 5:
            benefits.append("Réduction 5% sur tous les produits")
        if level >= 10:
            benefits.append("Accès aux produits exclusifs")
        if level >= 20:
            benefits.append("Livraison gratuite")
        if level >= 35:
            benefits.append("Support prioritaire")
        if level >= 50:
            benefits.append("Réduction 15% sur tous les produits")
        if level >= 75:
            benefits.append("Accès VIP aux nouveautés")
        
        return benefits
    
    def _initialize_badges(self) -> Dict[str, Dict]:
        """Initialise les badges"""
        return {
            'first_purchase': {
                'name': 'Premier Achat',
                'description': 'Votre première commande sur CFA',
                'icon': '🛒',
                'rarity': 'common'
            },
            'eco_warrior': {
                'name': 'Guerrier Écologique',
                'description': '10 produits écologiques achetés',
                'icon': '🌱',
                'rarity': 'uncommon'
            },
            'local_hero': {
                'name': 'Héros Local',
                'description': 'Soutien de 20 producteurs locaux',
                'icon': '🏠',
                'rarity': 'rare'
            },
            'recipe_master': {
                'name': 'Maître des Recettes',
                'description': '50 recettes partagées',
                'icon': '👨‍🍳',
                'rarity': 'epic'
            },
            'streak_legend': {
                'name': 'Légende des Séries',
                'description': '30 jours de connexion consécutifs',
                'icon': '🔥',
                'rarity': 'legendary'
            },
            'ambassador': {
                'name': 'Ambassadeur CFA',
                'description': '100 parrainages réussis',
                'icon': '👑',
                'rarity': 'legendary'
            }
        }
    
    def _initialize_achievements(self) -> Dict[str, Dict]:
        """Initialise les achievements"""
        return {
            'spice_collector': {
                'name': 'Collectionneur d\'Épices',
                'description': 'Achetez 25 épices différentes',
                'progress_max': 25,
                'reward_points': 200,
                'icon': '🌶️'
            },
            'global_explorer': {
                'name': 'Explorateur Mondial',
                'description': 'Achetez des produits de 5 pays différents',
                'progress_max': 5,
                'reward_points': 300,
                'icon': '🌍'
            },
            'review_champion': {
                'name': 'Champion des Avis',
                'description': 'Laissez 100 avis produits',
                'progress_max': 100,
                'reward_points': 500,
                'icon': '⭐'
            },
            'social_influencer': {
                'name': 'Influenceur Social',
                'description': 'Partagez 50 produits sur les réseaux',
                'progress_max': 50,
                'reward_points': 250,
                'icon': '📱'
            }
        }
    
    def process_user_action(self, user_id: int, action: ActionType, 
                          context: Dict = None) -> List[UserReward]:
        """Traite une action utilisateur et attribue les récompenses"""
        rewards = []
        
        # Vérifier si l'action est éligible
        if not self._is_action_eligible(user_id, action, context):
            return rewards
        
        # Obtenir la règle de récompense
        rule = self.reward_rules.get(action)
        if not rule:
            return rewards
        
        # Calculer les points
        points = self._calculate_points(user_id, rule, context)
        
        if points > 0:
            # Créer la récompense
            reward = UserReward(
                user_id=user_id,
                reward_type=RewardType.POINTS,
                action_type=action,
                points_earned=points,
                description=f"Points gagnés pour {action.value}",
                metadata=context or {}
            )
            
            db.session.add(reward)
            rewards.append(reward)
            
            # Mettre à jour les stats utilisateur
            self._update_user_stats(user_id, action, points, context)
            
            # Vérifier les badges et achievements
            new_badges = self._check_badges(user_id, action, context)
            new_achievements = self._check_achievements(user_id, action, context)
            
            rewards.extend(new_badges)
            rewards.extend(new_achievements)
        
        db.session.commit()
        return rewards
    
    def _is_action_eligible(self, user_id: int, action: ActionType, 
                          context: Dict = None) -> bool:
        """Vérifie si l'action est éligible pour des récompenses"""
        rule = self.reward_rules.get(action)
        if not rule:
            return False
        
        # Vérifier les conditions
        if rule.conditions and context:
            for condition, required_value in rule.conditions.items():
                if context.get(condition) != required_value:
                    return False
        
        # Vérifier le cooldown
        if rule.cooldown_hours > 0:
            last_reward = UserReward.query.filter_by(
                user_id=user_id,
                action_type=action
            ).order_by(UserReward.created_at.desc()).first()
            
            if last_reward:
                time_diff = datetime.now() - last_reward.created_at
                if time_diff.total_seconds() < rule.cooldown_hours * 3600:
                    return False
        
        # Vérifier la limite quotidienne
        if rule.max_per_day:
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            today_count = UserReward.query.filter(
                UserReward.user_id == user_id,
                UserReward.action_type == action,
                UserReward.created_at >= today_start
            ).count()
            
            if today_count >= rule.max_per_day:
                return False
        
        return True
    
    def _calculate_points(self, user_id: int, rule: RewardRule, 
                         context: Dict = None) -> int:
        """Calcule les points à attribuer"""
        base_points = rule.points
        
        # Appliquer le multiplicateur
        points = int(base_points * rule.multiplier)
        
        # Bonus pour les streaks
        if rule.action == ActionType.STREAK_MAINTAIN:
            user_stats = UserStats.query.filter_by(user_id=user_id).first()
            if user_stats:
                streak_bonus = min(user_stats.login_streak * 2, 50)  # Max 50 points bonus
                points = streak_bonus
        
        # Bonus de niveau utilisateur
        user_stats = UserStats.query.filter_by(user_id=user_id).first()
        if user_stats and user_stats.current_level > 1:
            level_multiplier = 1 + (user_stats.current_level - 1) * 0.05  # 5% par niveau
            points = int(points * level_multiplier)
        
        # Bonus pour montant d'achat
        if rule.action == ActionType.PURCHASE and context:
            amount = context.get('amount', 0)
            if amount > 0:
                # 1 point par euro dépensé
                amount_bonus = int(amount)
                points += amount_bonus
        
        return points
    
    def _update_user_stats(self, user_id: int, action: ActionType, 
                          points: int, context: Dict = None):
        """Met à jour les statistiques utilisateur"""
        user_stats = UserStats.query.filter_by(user_id=user_id).first()
        if not user_stats:
            user_stats = UserStats(user_id=user_id)
            db.session.add(user_stats)
        
        # Ajouter les points
        user_stats.total_points += points
        user_stats.available_points += points
        user_stats.experience_points += points
        
        # Mettre à jour les compteurs spécifiques
        if action == ActionType.PURCHASE:
            user_stats.total_purchases += 1
            user_stats.last_purchase = datetime.now()
            
            # Vérifier le streak d'achat
            if user_stats.last_purchase:
                days_diff = (datetime.now() - user_stats.last_purchase).days
                if days_diff <= 7:  # Achat dans les 7 jours
                    user_stats.purchase_streak += 1
                else:
                    user_stats.purchase_streak = 1
        
        elif action == ActionType.REVIEW:
            user_stats.total_reviews += 1
        
        elif action == ActionType.REFERRAL:
            user_stats.total_referrals += 1
        
        elif action == ActionType.RECIPE_SHARE:
            user_stats.recipes_shared += 1
        
        elif action == ActionType.LOCAL_SUPPORT:
            user_stats.local_products_bought += 1
        
        elif action == ActionType.ECO_CHOICE:
            user_stats.eco_products_bought += 1
        
        elif action == ActionType.DAILY_LOGIN:
            user_stats.last_login = datetime.now()
            
            # Calculer le streak de connexion
            if user_stats.last_login:
                days_diff = (datetime.now() - user_stats.last_login).days
                if days_diff == 1:  # Connexion quotidienne
                    user_stats.login_streak += 1
                elif days_diff > 1:  # Streak cassé
                    user_stats.login_streak = 1
            else:
                user_stats.login_streak = 1
        
        # Vérifier le changement de niveau
        self._check_level_up(user_stats)
    
    def _check_level_up(self, user_stats: UserStats):
        """Vérifie et applique les montées de niveau"""
        current_level = user_stats.current_level
        current_xp = user_stats.experience_points
        
        # Trouver le niveau approprié
        new_level = current_level
        for level, data in self.level_thresholds.items():
            if current_xp >= data['xp_required'] and level > new_level:
                new_level = level
        
        if new_level > current_level:
            user_stats.current_level = new_level
            
            # Créer une récompense de niveau
            level_reward = UserReward(
                user_id=user_stats.user_id,
                reward_type=RewardType.ACHIEVEMENT,
                action_type=ActionType.EXPERIENCE,
                description=f"Niveau {new_level} atteint !",
                metadata={
                    'level': new_level,
                    'title': self.level_thresholds[new_level]['title'],
                    'benefits': self.level_thresholds[new_level]['benefits']
                }
            )
            db.session.add(level_reward)
    
    def _check_badges(self, user_id: int, action: ActionType, 
                     context: Dict = None) -> List[UserReward]:
        """Vérifie et attribue les badges"""
        badges = []
        user_stats = UserStats.query.filter_by(user_id=user_id).first()
        
        if not user_stats:
            return badges
        
        earned_badges = user_stats.badges_earned or []
        
        # Badge premier achat
        if action == ActionType.PURCHASE and 'first_purchase' not in earned_badges:
            badges.append(self._create_badge_reward(user_id, 'first_purchase'))
            earned_badges.append('first_purchase')
        
        # Badge guerrier écologique
        if (user_stats.eco_products_bought >= 10 and 
            'eco_warrior' not in earned_badges):
            badges.append(self._create_badge_reward(user_id, 'eco_warrior'))
            earned_badges.append('eco_warrior')
        
        # Badge héros local
        if (user_stats.local_products_bought >= 20 and 
            'local_hero' not in earned_badges):
            badges.append(self._create_badge_reward(user_id, 'local_hero'))
            earned_badges.append('local_hero')
        
        # Badge maître des recettes
        if (user_stats.recipes_shared >= 50 and 
            'recipe_master' not in earned_badges):
            badges.append(self._create_badge_reward(user_id, 'recipe_master'))
            earned_badges.append('recipe_master')
        
        # Badge légende des séries
        if (user_stats.login_streak >= 30 and 
            'streak_legend' not in earned_badges):
            badges.append(self._create_badge_reward(user_id, 'streak_legend'))
            earned_badges.append('streak_legend')
        
        # Badge ambassadeur
        if (user_stats.total_referrals >= 100 and 
            'ambassador' not in earned_badges):
            badges.append(self._create_badge_reward(user_id, 'ambassador'))
            earned_badges.append('ambassador')
        
        # Mettre à jour la liste des badges
        user_stats.badges_earned = earned_badges
        
        return badges
    
    def _create_badge_reward(self, user_id: int, badge_key: str) -> UserReward:
        """Crée une récompense de badge"""
        badge_info = self.badges[badge_key]
        
        return UserReward(
            user_id=user_id,
            reward_type=RewardType.BADGE,
            action_type=ActionType.ACHIEVEMENT,
            badge_name=badge_key,
            description=f"Badge obtenu: {badge_info['name']}",
            metadata=badge_info
        )
    
    def _check_achievements(self, user_id: int, action: ActionType, 
                          context: Dict = None) -> List[UserReward]:
        """Vérifie et attribue les achievements"""
        achievements = []
        # Implementation des achievements spécifiques
        return achievements
    
    def get_user_dashboard(self, user_id: int) -> Dict:
        """Retourne le tableau de bord gamification de l'utilisateur"""
        user_stats = UserStats.query.filter_by(user_id=user_id).first()
        
        if not user_stats:
            return self._create_default_dashboard(user_id)
        
        # Calculer le progrès vers le niveau suivant
        current_level = user_stats.current_level
        next_level = current_level + 1
        
        current_xp = user_stats.experience_points
        current_threshold = self.level_thresholds.get(current_level, {}).get('xp_required', 0)
        next_threshold = self.level_thresholds.get(next_level, {}).get('xp_required', current_xp)
        
        progress_percentage = 0
        if next_threshold > current_threshold:
            progress_percentage = ((current_xp - current_threshold) / 
                                 (next_threshold - current_threshold)) * 100
        
        return {
            'user_id': user_id,
            'level': {
                'current': current_level,
                'title': self.level_thresholds.get(current_level, {}).get('title', 'Explorateur'),
                'progress_percentage': min(progress_percentage, 100),
                'xp_current': current_xp,
                'xp_next_level': next_threshold,
                'benefits': self.level_thresholds.get(current_level, {}).get('benefits', [])
            },
            'points': {
                'total': user_stats.total_points,
                'available': user_stats.available_points,
                'pending_cashback': float(user_stats.pending_cashback or 0)
            },
            'streaks': {
                'login': user_stats.login_streak,
                'purchase': user_stats.purchase_streak
            },
            'stats': {
                'total_purchases': user_stats.total_purchases,
                'total_reviews': user_stats.total_reviews,
                'total_referrals': user_stats.total_referrals,
                'recipes_shared': user_stats.recipes_shared,
                'local_products_bought': user_stats.local_products_bought,
                'eco_products_bought': user_stats.eco_products_bought
            },
            'badges': [
                {
                    'key': badge_key,
                    'name': self.badges[badge_key]['name'],
                    'description': self.badges[badge_key]['description'],
                    'icon': self.badges[badge_key]['icon'],
                    'rarity': self.badges[badge_key]['rarity']
                }
                for badge_key in (user_stats.badges_earned or [])
                if badge_key in self.badges
            ],
            'recent_rewards': self._get_recent_rewards(user_id, limit=5)
        }
    
    def _create_default_dashboard(self, user_id: int) -> Dict:
        """Crée un tableau de bord par défaut pour un nouvel utilisateur"""
        # Créer les stats par défaut
        user_stats = UserStats(user_id=user_id)
        db.session.add(user_stats)
        db.session.commit()
        
        return self.get_user_dashboard(user_id)
    
    def _get_recent_rewards(self, user_id: int, limit: int = 5) -> List[Dict]:
        """Récupère les récompenses récentes"""
        rewards = UserReward.query.filter_by(user_id=user_id)\
                                 .order_by(UserReward.created_at.desc())\
                                 .limit(limit).all()
        
        return [
            {
                'type': reward.reward_type.value,
                'action': reward.action_type.value,
                'points': reward.points_earned,
                'description': reward.description,
                'created_at': reward.created_at.isoformat() if reward.created_at else None
            }
            for reward in rewards
        ]
    
    def redeem_points(self, user_id: int, points_to_redeem: int, 
                     reward_type: str) -> Optional[UserReward]:
        """Échange des points contre des récompenses"""
        user_stats = UserStats.query.filter_by(user_id=user_id).first()
        
        if not user_stats or user_stats.available_points < points_to_redeem:
            return None
        
        # Calculer la valeur de la récompense
        if reward_type == 'discount':
            # 100 points = 1% de réduction (max 20%)
            discount_percentage = min(points_to_redeem / 100, 20)
            
            reward = UserReward(
                user_id=user_id,
                reward_type=RewardType.DISCOUNT,
                action_type=ActionType.PURCHASE,
                discount_percentage=discount_percentage,
                description=f"Réduction de {discount_percentage}% échangée",
                expires_at=datetime.now() + timedelta(days=30)
            )
        
        elif reward_type == 'cashback':
            # 1000 points = 1€ de cashback
            cashback_amount = points_to_redeem / 1000
            
            reward = UserReward(
                user_id=user_id,
                reward_type=RewardType.CASHBACK,
                action_type=ActionType.PURCHASE,
                cashback_amount=cashback_amount,
                description=f"Cashback de {cashback_amount}€ échangé"
            )
        
        else:
            return None
        
        # Déduire les points
        user_stats.available_points -= points_to_redeem
        
        db.session.add(reward)
        db.session.commit()
        
        return reward

# Instance globale du moteur de gamification
gamification_engine = GamificationEngine()

