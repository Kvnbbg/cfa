"""
Système d'optimisation des performances pour CFA
Algorithmes intelligents pour économiser les ressources serveur
"""

import time
import threading
import functools
import hashlib
import pickle
from typing import Any, Callable, Dict, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, OrderedDict
import psutil
import gc
from dataclasses import dataclass

@dataclass
class PerformanceMetrics:
    """Métriques de performance"""
    cpu_usage: float
    memory_usage: float
    response_time: float
    cache_hit_rate: float
    active_connections: int
    timestamp: datetime

class IntelligentCache:
    """Cache intelligent avec éviction adaptative"""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache = OrderedDict()
        self.access_counts = defaultdict(int)
        self.last_access = {}
        self.hit_count = 0
        self.miss_count = 0
        self._lock = threading.RLock()
    
    def get(self, key: str) -> Optional[Any]:
        """Récupère une valeur du cache"""
        with self._lock:
            if key in self.cache:
                value, timestamp = self.cache[key]
                
                # Vérifier l'expiration
                if datetime.now() - timestamp > timedelta(seconds=self.ttl_seconds):
                    del self.cache[key]
                    del self.access_counts[key]
                    del self.last_access[key]
                    self.miss_count += 1
                    return None
                
                # Mettre à jour les statistiques d'accès
                self.access_counts[key] += 1
                self.last_access[key] = datetime.now()
                
                # Déplacer vers la fin (LRU)
                self.cache.move_to_end(key)
                
                self.hit_count += 1
                return value
            
            self.miss_count += 1
            return None
    
    def set(self, key: str, value: Any) -> None:
        """Stocke une valeur dans le cache"""
        with self._lock:
            # Éviction si nécessaire
            if len(self.cache) >= self.max_size:
                self._evict_items()
            
            self.cache[key] = (value, datetime.now())
            self.access_counts[key] = 1
            self.last_access[key] = datetime.now()
    
    def _evict_items(self) -> None:
        """Éviction intelligente basée sur la fréquence et la récence"""
        items_to_remove = max(1, len(self.cache) // 4)  # Supprimer 25%
        
        # Calculer un score pour chaque élément
        scores = {}
        now = datetime.now()
        
        for key in self.cache:
            frequency = self.access_counts[key]
            recency = (now - self.last_access[key]).total_seconds()
            
            # Score combiné (plus élevé = plus important à garder)
            scores[key] = frequency / (1 + recency / 3600)  # Normaliser par heure
        
        # Supprimer les éléments avec les scores les plus bas
        items_to_remove_list = sorted(scores.items(), key=lambda x: x[1])[:items_to_remove]
        
        for key, _ in items_to_remove_list:
            del self.cache[key]
            del self.access_counts[key]
            del self.last_access[key]
    
    def clear(self) -> None:
        """Vide le cache"""
        with self._lock:
            self.cache.clear()
            self.access_counts.clear()
            self.last_access.clear()
            self.hit_count = 0
            self.miss_count = 0
    
    @property
    def hit_rate(self) -> float:
        """Taux de succès du cache"""
        total = self.hit_count + self.miss_count
        return self.hit_count / total if total > 0 else 0.0
    
    def get_stats(self) -> Dict:
        """Statistiques du cache"""
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hit_count': self.hit_count,
            'miss_count': self.miss_count,
            'hit_rate': self.hit_rate,
            'memory_usage': self._estimate_memory_usage()
        }
    
    def _estimate_memory_usage(self) -> int:
        """Estime l'usage mémoire du cache"""
        try:
            return len(pickle.dumps(self.cache))
        except:
            return 0

class ResourceMonitor:
    """Moniteur de ressources système"""
    
    def __init__(self):
        self.metrics_history = []
        self.max_history = 100
        self.alert_thresholds = {
            'cpu': 80.0,
            'memory': 85.0,
            'response_time': 2.0
        }
        self.is_monitoring = False
    
    def start_monitoring(self):
        """Démarre la surveillance"""
        if not self.is_monitoring:
            self.is_monitoring = True
            threading.Thread(target=self._monitor_loop, daemon=True).start()
    
    def stop_monitoring(self):
        """Arrête la surveillance"""
        self.is_monitoring = False
    
    def _monitor_loop(self):
        """Boucle de surveillance"""
        while self.is_monitoring:
            try:
                metrics = self._collect_metrics()
                self.metrics_history.append(metrics)
                
                # Garder seulement les dernières métriques
                if len(self.metrics_history) > self.max_history:
                    self.metrics_history.pop(0)
                
                # Vérifier les seuils d'alerte
                self._check_alerts(metrics)
                
                time.sleep(30)  # Collecter toutes les 30 secondes
                
            except Exception as e:
                print(f"Erreur monitoring: {e}")
                time.sleep(60)
    
    def _collect_metrics(self) -> PerformanceMetrics:
        """Collecte les métriques système"""
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        return PerformanceMetrics(
            cpu_usage=cpu_usage,
            memory_usage=memory.percent,
            response_time=0.0,  # À mesurer par l'application
            cache_hit_rate=0.0,  # À mesurer par le cache
            active_connections=len(psutil.net_connections()),
            timestamp=datetime.now()
        )
    
    def _check_alerts(self, metrics: PerformanceMetrics):
        """Vérifie les seuils d'alerte"""
        if metrics.cpu_usage > self.alert_thresholds['cpu']:
            self._trigger_cpu_optimization()
        
        if metrics.memory_usage > self.alert_thresholds['memory']:
            self._trigger_memory_cleanup()
    
    def _trigger_cpu_optimization(self):
        """Déclenche l'optimisation CPU"""
        # Réduire la fréquence de certaines tâches
        # Mettre en pause les tâches non critiques
        print("Optimisation CPU déclenchée")
    
    def _trigger_memory_cleanup(self):
        """Déclenche le nettoyage mémoire"""
        gc.collect()  # Garbage collection forcé
        print("Nettoyage mémoire déclenché")
    
    def get_current_metrics(self) -> Optional[PerformanceMetrics]:
        """Retourne les métriques actuelles"""
        return self.metrics_history[-1] if self.metrics_history else None
    
    def get_average_metrics(self, minutes: int = 10) -> Dict:
        """Retourne les métriques moyennes sur une période"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        recent_metrics = [
            m for m in self.metrics_history 
            if m.timestamp >= cutoff_time
        ]
        
        if not recent_metrics:
            return {}
        
        return {
            'avg_cpu': sum(m.cpu_usage for m in recent_metrics) / len(recent_metrics),
            'avg_memory': sum(m.memory_usage for m in recent_metrics) / len(recent_metrics),
            'avg_response_time': sum(m.response_time for m in recent_metrics) / len(recent_metrics),
            'sample_count': len(recent_metrics)
        }

class AdaptiveRateLimiter:
    """Limiteur de débit adaptatif"""
    
    def __init__(self):
        self.request_counts = defaultdict(list)
        self.base_limits = {
            'api': 100,      # requêtes par minute
            'search': 50,
            'upload': 10
        }
        self.current_limits = self.base_limits.copy()
        self.blocked_ips = set()
    
    def is_allowed(self, identifier: str, endpoint_type: str = 'api') -> bool:
        """Vérifie si la requête est autorisée"""
        if identifier in self.blocked_ips:
            return False
        
        now = time.time()
        minute_ago = now - 60
        
        # Nettoyer les anciennes requêtes
        self.request_counts[identifier] = [
            req_time for req_time in self.request_counts[identifier]
            if req_time > minute_ago
        ]
        
        # Vérifier la limite
        current_count = len(self.request_counts[identifier])
        limit = self.current_limits.get(endpoint_type, self.base_limits['api'])
        
        if current_count >= limit:
            return False
        
        # Enregistrer la requête
        self.request_counts[identifier].append(now)
        return True
    
    def adapt_limits(self, system_load: float):
        """Adapte les limites selon la charge système"""
        if system_load > 0.8:  # Charge élevée
            factor = 0.5
        elif system_load > 0.6:  # Charge modérée
            factor = 0.7
        else:  # Charge normale
            factor = 1.0
        
        for endpoint_type, base_limit in self.base_limits.items():
            self.current_limits[endpoint_type] = int(base_limit * factor)
    
    def block_ip(self, ip: str, duration: int = 3600):
        """Bloque une IP temporairement"""
        self.blocked_ips.add(ip)
        threading.Timer(duration, lambda: self.blocked_ips.discard(ip)).start()

class QueryOptimizer:
    """Optimiseur de requêtes base de données"""
    
    def __init__(self):
        self.query_cache = IntelligentCache(max_size=500, ttl_seconds=1800)
        self.slow_queries = []
        self.query_stats = defaultdict(list)
    
    def cache_query_result(self, query_hash: str, result: Any, execution_time: float):
        """Met en cache le résultat d'une requête"""
        # Ne cacher que les requêtes rapides et fréquentes
        if execution_time < 1.0:  # Moins d'1 seconde
            self.query_cache.set(query_hash, result)
        
        # Enregistrer les statistiques
        self.query_stats[query_hash].append(execution_time)
        
        # Détecter les requêtes lentes
        if execution_time > 2.0:
            self.slow_queries.append({
                'query_hash': query_hash,
                'execution_time': execution_time,
                'timestamp': datetime.now()
            })
    
    def get_cached_result(self, query_hash: str) -> Optional[Any]:
        """Récupère un résultat mis en cache"""
        return self.query_cache.get(query_hash)
    
    def get_query_recommendations(self) -> List[Dict]:
        """Retourne des recommandations d'optimisation"""
        recommendations = []
        
        # Analyser les requêtes lentes
        if self.slow_queries:
            recent_slow = [
                q for q in self.slow_queries
                if datetime.now() - q['timestamp'] < timedelta(hours=1)
            ]
            
            if recent_slow:
                recommendations.append({
                    'type': 'slow_queries',
                    'count': len(recent_slow),
                    'message': f"{len(recent_slow)} requêtes lentes détectées dans la dernière heure"
                })
        
        # Analyser le taux de cache
        cache_stats = self.query_cache.get_stats()
        if cache_stats['hit_rate'] < 0.5:
            recommendations.append({
                'type': 'low_cache_hit',
                'hit_rate': cache_stats['hit_rate'],
                'message': f"Taux de cache faible: {cache_stats['hit_rate']:.1%}"
            })
        
        return recommendations

class PerformanceOptimizer:
    """Optimiseur de performance principal"""
    
    def __init__(self):
        self.cache = IntelligentCache()
        self.monitor = ResourceMonitor()
        self.rate_limiter = AdaptiveRateLimiter()
        self.query_optimizer = QueryOptimizer()
        self.optimization_active = False
    
    def start_optimization(self):
        """Démarre l'optimisation"""
        if not self.optimization_active:
            self.optimization_active = True
            self.monitor.start_monitoring()
            threading.Thread(target=self._optimization_loop, daemon=True).start()
    
    def stop_optimization(self):
        """Arrête l'optimisation"""
        self.optimization_active = False
        self.monitor.stop_monitoring()
    
    def _optimization_loop(self):
        """Boucle d'optimisation principale"""
        while self.optimization_active:
            try:
                # Obtenir les métriques actuelles
                metrics = self.monitor.get_current_metrics()
                
                if metrics:
                    # Adapter les limites de débit
                    system_load = max(metrics.cpu_usage, metrics.memory_usage) / 100
                    self.rate_limiter.adapt_limits(system_load)
                    
                    # Optimiser le cache si nécessaire
                    if metrics.memory_usage > 80:
                        self._optimize_cache()
                    
                    # Nettoyer la mémoire si nécessaire
                    if metrics.memory_usage > 85:
                        self._cleanup_memory()
                
                time.sleep(60)  # Optimiser toutes les minutes
                
            except Exception as e:
                print(f"Erreur optimisation: {e}")
                time.sleep(120)
    
    def _optimize_cache(self):
        """Optimise l'utilisation du cache"""
        # Réduire la taille du cache
        current_size = len(self.cache.cache)
        new_size = max(100, current_size // 2)
        
        # Éviction forcée
        items_to_remove = current_size - new_size
        if items_to_remove > 0:
            for _ in range(items_to_remove):
                if self.cache.cache:
                    self.cache.cache.popitem(last=False)  # FIFO
    
    def _cleanup_memory(self):
        """Nettoie la mémoire"""
        # Garbage collection
        gc.collect()
        
        # Vider les caches moins importants
        self.query_optimizer.query_cache.clear()
        
        # Nettoyer les anciennes métriques
        if len(self.monitor.metrics_history) > 50:
            self.monitor.metrics_history = self.monitor.metrics_history[-50:]
    
    def get_performance_report(self) -> Dict:
        """Génère un rapport de performance"""
        current_metrics = self.monitor.get_current_metrics()
        avg_metrics = self.monitor.get_average_metrics()
        cache_stats = self.cache.get_stats()
        query_recommendations = self.query_optimizer.get_query_recommendations()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'current_metrics': {
                'cpu_usage': current_metrics.cpu_usage if current_metrics else 0,
                'memory_usage': current_metrics.memory_usage if current_metrics else 0,
                'active_connections': current_metrics.active_connections if current_metrics else 0
            },
            'average_metrics': avg_metrics,
            'cache_performance': cache_stats,
            'rate_limiting': {
                'current_limits': self.rate_limiter.current_limits,
                'blocked_ips': len(self.rate_limiter.blocked_ips)
            },
            'recommendations': query_recommendations,
            'optimization_status': 'active' if self.optimization_active else 'inactive'
        }

# Décorateurs pour l'optimisation

def cached(ttl: int = 3600):
    """Décorateur pour mettre en cache les résultats de fonction"""
    def decorator(func: Callable) -> Callable:
        cache = IntelligentCache(ttl_seconds=ttl)
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Créer une clé de cache
            key = hashlib.sha256(
                f"{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}".encode()
            ).hexdigest()
            
            # Vérifier le cache
            result = cache.get(key)
            if result is not None:
                return result
            
            # Exécuter la fonction
            result = func(*args, **kwargs)
            
            # Mettre en cache
            cache.set(key, result)
            
            return result
        
        wrapper.cache = cache
        return wrapper
    
    return decorator

def rate_limited(requests_per_minute: int = 60):
    """Décorateur pour limiter le débit d'une fonction"""
    def decorator(func: Callable) -> Callable:
        rate_limiter = AdaptiveRateLimiter()
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Identifier l'appelant (simplification)
            identifier = f"{func.__name__}:{id(threading.current_thread())}"
            
            if not rate_limiter.is_allowed(identifier):
                raise Exception("Rate limit exceeded")
            
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator

def performance_monitored(func: Callable) -> Callable:
    """Décorateur pour surveiller les performances d'une fonction"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            execution_time = time.time() - start_time
            
            # Log des performances si lent
            if execution_time > 1.0:
                print(f"Fonction lente détectée: {func.__name__} ({execution_time:.2f}s)")
    
    return wrapper

# Instance globale de l'optimiseur
performance_optimizer = PerformanceOptimizer()

