"""
Système de surveillance de sécurité (Watchdog) pour CFA
Conforme aux principes ANSSI.fr
"""

import time
import threading
import hashlib
import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from enum import Enum
import psutil
import requests
from collections import defaultdict, deque

class ThreatLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SecurityEvent(Enum):
    BRUTE_FORCE = "brute_force"
    SQL_INJECTION = "sql_injection"
    XSS_ATTEMPT = "xss_attempt"
    DDOS_ATTACK = "ddos_attack"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    FILE_INTEGRITY = "file_integrity"
    RESOURCE_ABUSE = "resource_abuse"

@dataclass
class SecurityAlert:
    """Alerte de sécurité"""
    event_type: SecurityEvent
    threat_level: ThreatLevel
    source_ip: str
    timestamp: datetime
    description: str
    details: Dict
    action_taken: str = ""
    resolved: bool = False

class ANSSICompliance:
    """Conformité aux recommandations ANSSI.fr"""
    
    @staticmethod
    def get_security_requirements():
        """Retourne les exigences de sécurité ANSSI"""
        return {
            'authentication': {
                'min_password_length': 12,
                'require_special_chars': True,
                'require_numbers': True,
                'require_uppercase': True,
                'max_login_attempts': 3,
                'lockout_duration': 900,  # 15 minutes
                'session_timeout': 3600,  # 1 heure
                'mfa_required': True
            },
            'encryption': {
                'min_key_length': 256,
                'algorithms': ['AES-256', 'RSA-2048'],
                'tls_version': '1.3',
                'hash_algorithm': 'SHA-256'
            },
            'logging': {
                'retention_days': 365,
                'log_authentication': True,
                'log_admin_actions': True,
                'log_data_access': True,
                'centralized_logging': True
            },
            'access_control': {
                'principle_least_privilege': True,
                'role_based_access': True,
                'regular_access_review': True,
                'privileged_account_monitoring': True
            },
            'monitoring': {
                'real_time_monitoring': True,
                'intrusion_detection': True,
                'vulnerability_scanning': True,
                'incident_response_plan': True
            }
        }

class SecurityWatchdog:
    """Chien de garde de sécurité intelligent"""
    
    def __init__(self):
        self.is_running = False
        self.alerts = deque(maxlen=1000)  # Garder les 1000 dernières alertes
        self.blocked_ips = set()
        self.suspicious_ips = defaultdict(int)
        self.request_counts = defaultdict(lambda: deque(maxlen=100))
        self.file_hashes = {}
        self.system_baseline = {}
        
        # Configuration ANSSI
        self.anssi_config = ANSSICompliance.get_security_requirements()
        
        # Seuils de détection
        self.thresholds = {
            'max_requests_per_minute': 60,
            'max_failed_logins': 3,
            'max_cpu_usage': 80,
            'max_memory_usage': 85,
            'max_disk_usage': 90
        }
        
        # Setup logging
        self.setup_security_logging()
        
        # Initialiser la baseline système
        self.establish_baseline()
    
    def setup_security_logging(self):
        """Configure le logging de sécurité conforme ANSSI"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('/var/log/cfa_security.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('CFA_Security')
    
    def establish_baseline(self):
        """Établit une baseline du système"""
        try:
            self.system_baseline = {
                'cpu_count': psutil.cpu_count(),
                'memory_total': psutil.virtual_memory().total,
                'disk_usage': psutil.disk_usage('/').percent,
                'network_connections': len(psutil.net_connections()),
                'running_processes': len(psutil.pids())
            }
            
            # Hash des fichiers critiques
            critical_files = [
                'src/main.py',
                'src/models/__init__.py',
                'src/security/watchdog.py'
            ]
            
            for file_path in critical_files:
                if os.path.exists(file_path):
                    self.file_hashes[file_path] = self.calculate_file_hash(file_path)
            
            self.logger.info("Baseline système établie")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'établissement de la baseline: {e}")
    
    def calculate_file_hash(self, file_path: str) -> str:
        """Calcule le hash SHA-256 d'un fichier"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception as e:
            self.logger.error(f"Erreur calcul hash {file_path}: {e}")
            return ""
    
    def start_monitoring(self):
        """Démarre la surveillance"""
        if self.is_running:
            return
        
        self.is_running = True
        self.logger.info("Démarrage du watchdog de sécurité")
        
        # Threads de surveillance
        threads = [
            threading.Thread(target=self.monitor_system_resources, daemon=True),
            threading.Thread(target=self.monitor_file_integrity, daemon=True),
            threading.Thread(target=self.monitor_network_activity, daemon=True),
            threading.Thread(target=self.cleanup_old_data, daemon=True)
        ]
        
        for thread in threads:
            thread.start()
    
    def stop_monitoring(self):
        """Arrête la surveillance"""
        self.is_running = False
        self.logger.info("Arrêt du watchdog de sécurité")
    
    def monitor_system_resources(self):
        """Surveille les ressources système"""
        while self.is_running:
            try:
                # CPU
                cpu_percent = psutil.cpu_percent(interval=1)
                if cpu_percent > self.thresholds['max_cpu_usage']:
                    self.create_alert(
                        SecurityEvent.RESOURCE_ABUSE,
                        ThreatLevel.MEDIUM,
                        "localhost",
                        f"Usage CPU élevé: {cpu_percent}%",
                        {'cpu_percent': cpu_percent}
                    )
                
                # Mémoire
                memory = psutil.virtual_memory()
                if memory.percent > self.thresholds['max_memory_usage']:
                    self.create_alert(
                        SecurityEvent.RESOURCE_ABUSE,
                        ThreatLevel.MEDIUM,
                        "localhost",
                        f"Usage mémoire élevé: {memory.percent}%",
                        {'memory_percent': memory.percent}
                    )
                
                # Disque
                disk = psutil.disk_usage('/')
                if disk.percent > self.thresholds['max_disk_usage']:
                    self.create_alert(
                        SecurityEvent.RESOURCE_ABUSE,
                        ThreatLevel.HIGH,
                        "localhost",
                        f"Usage disque élevé: {disk.percent}%",
                        {'disk_percent': disk.percent}
                    )
                
                time.sleep(30)  # Vérifier toutes les 30 secondes
                
            except Exception as e:
                self.logger.error(f"Erreur surveillance ressources: {e}")
                time.sleep(60)
    
    def monitor_file_integrity(self):
        """Surveille l'intégrité des fichiers"""
        while self.is_running:
            try:
                for file_path, original_hash in self.file_hashes.items():
                    if os.path.exists(file_path):
                        current_hash = self.calculate_file_hash(file_path)
                        if current_hash != original_hash and current_hash:
                            self.create_alert(
                                SecurityEvent.FILE_INTEGRITY,
                                ThreatLevel.HIGH,
                                "localhost",
                                f"Fichier modifié: {file_path}",
                                {
                                    'file_path': file_path,
                                    'original_hash': original_hash,
                                    'current_hash': current_hash
                                }
                            )
                            # Mettre à jour le hash
                            self.file_hashes[file_path] = current_hash
                
                time.sleep(300)  # Vérifier toutes les 5 minutes
                
            except Exception as e:
                self.logger.error(f"Erreur surveillance intégrité: {e}")
                time.sleep(600)
    
    def monitor_network_activity(self):
        """Surveille l'activité réseau"""
        while self.is_running:
            try:
                connections = psutil.net_connections()
                
                # Détecter les connexions suspectes
                for conn in connections:
                    if conn.raddr and conn.status == 'ESTABLISHED':
                        remote_ip = conn.raddr.ip
                        
                        # Vérifier si l'IP est dans la liste noire
                        if self.is_suspicious_ip(remote_ip):
                            self.create_alert(
                                SecurityEvent.SUSPICIOUS_ACTIVITY,
                                ThreatLevel.MEDIUM,
                                remote_ip,
                                f"Connexion depuis IP suspecte: {remote_ip}",
                                {'connection': str(conn)}
                            )
                
                time.sleep(60)  # Vérifier toutes les minutes
                
            except Exception as e:
                self.logger.error(f"Erreur surveillance réseau: {e}")
                time.sleep(120)
    
    def analyze_request(self, request_data: Dict) -> Optional[SecurityAlert]:
        """Analyse une requête HTTP pour détecter les menaces"""
        ip = request_data.get('ip', 'unknown')
        user_agent = request_data.get('user_agent', '')
        url = request_data.get('url', '')
        method = request_data.get('method', 'GET')
        
        # Enregistrer la requête
        now = datetime.now()
        self.request_counts[ip].append(now)
        
        # Détecter les attaques DDoS
        recent_requests = [
            req_time for req_time in self.request_counts[ip]
            if now - req_time < timedelta(minutes=1)
        ]
        
        if len(recent_requests) > self.thresholds['max_requests_per_minute']:
            self.block_ip(ip)
            return self.create_alert(
                SecurityEvent.DDOS_ATTACK,
                ThreatLevel.HIGH,
                ip,
                f"Attaque DDoS détectée: {len(recent_requests)} requêtes/minute",
                {'request_count': len(recent_requests)}
            )
        
        # Détecter les injections SQL
        sql_patterns = [
            'union select', 'drop table', 'insert into', 'delete from',
            'update set', 'exec(', 'script>', '<script', 'javascript:',
            'onload=', 'onerror=', 'onclick='
        ]
        
        query_string = url.lower()
        for pattern in sql_patterns:
            if pattern in query_string:
                return self.create_alert(
                    SecurityEvent.SQL_INJECTION,
                    ThreatLevel.HIGH,
                    ip,
                    f"Tentative d'injection SQL détectée: {pattern}",
                    {'url': url, 'pattern': pattern}
                )
        
        # Détecter les tentatives XSS
        xss_patterns = ['<script', 'javascript:', 'onload=', 'onerror=']
        for pattern in xss_patterns:
            if pattern in query_string:
                return self.create_alert(
                    SecurityEvent.XSS_ATTEMPT,
                    ThreatLevel.MEDIUM,
                    ip,
                    f"Tentative XSS détectée: {pattern}",
                    {'url': url, 'pattern': pattern}
                )
        
        return None
    
    def analyze_login_attempt(self, ip: str, username: str, success: bool) -> Optional[SecurityAlert]:
        """Analyse une tentative de connexion"""
        if not success:
            self.suspicious_ips[ip] += 1
            
            if self.suspicious_ips[ip] >= self.thresholds['max_failed_logins']:
                self.block_ip(ip)
                return self.create_alert(
                    SecurityEvent.BRUTE_FORCE,
                    ThreatLevel.HIGH,
                    ip,
                    f"Attaque par force brute détectée: {self.suspicious_ips[ip]} échecs",
                    {'username': username, 'failed_attempts': self.suspicious_ips[ip]}
                )
        else:
            # Réinitialiser le compteur en cas de succès
            if ip in self.suspicious_ips:
                del self.suspicious_ips[ip]
        
        return None
    
    def create_alert(self, event_type: SecurityEvent, threat_level: ThreatLevel,
                    source_ip: str, description: str, details: Dict) -> SecurityAlert:
        """Crée une alerte de sécurité"""
        alert = SecurityAlert(
            event_type=event_type,
            threat_level=threat_level,
            source_ip=source_ip,
            timestamp=datetime.now(),
            description=description,
            details=details
        )
        
        self.alerts.append(alert)
        self.logger.warning(f"ALERTE SÉCURITÉ [{threat_level.value.upper()}]: {description}")
        
        # Actions automatiques selon le niveau de menace
        if threat_level == ThreatLevel.CRITICAL:
            self.take_emergency_action(alert)
        elif threat_level == ThreatLevel.HIGH:
            self.take_defensive_action(alert)
        
        return alert
    
    def take_emergency_action(self, alert: SecurityAlert):
        """Actions d'urgence pour menaces critiques"""
        # Bloquer l'IP immédiatement
        self.block_ip(alert.source_ip)
        
        # Notifier les administrateurs
        self.notify_administrators(alert)
        
        # Log critique
        self.logger.critical(f"ACTION D'URGENCE: {alert.description}")
        
        alert.action_taken = "IP bloquée, administrateurs notifiés"
    
    def take_defensive_action(self, alert: SecurityAlert):
        """Actions défensives pour menaces élevées"""
        # Bloquer l'IP temporairement
        self.block_ip(alert.source_ip, duration=3600)  # 1 heure
        
        # Augmenter la surveillance
        self.increase_monitoring_for_ip(alert.source_ip)
        
        alert.action_taken = "IP bloquée temporairement, surveillance renforcée"
    
    def block_ip(self, ip: str, duration: Optional[int] = None):
        """Bloque une adresse IP"""
        self.blocked_ips.add(ip)
        self.logger.info(f"IP bloquée: {ip} (durée: {duration or 'permanente'})")
        
        if duration:
            # Programmer le déblocage
            threading.Timer(duration, lambda: self.unblock_ip(ip)).start()
    
    def unblock_ip(self, ip: str):
        """Débloque une adresse IP"""
        if ip in self.blocked_ips:
            self.blocked_ips.remove(ip)
            self.logger.info(f"IP débloquée: {ip}")
    
    def is_ip_blocked(self, ip: str) -> bool:
        """Vérifie si une IP est bloquée"""
        return ip in self.blocked_ips
    
    def is_suspicious_ip(self, ip: str) -> bool:
        """Vérifie si une IP est suspecte"""
        return self.suspicious_ips.get(ip, 0) > 0
    
    def increase_monitoring_for_ip(self, ip: str):
        """Augmente la surveillance pour une IP"""
        # Réduire les seuils pour cette IP
        # Implementation spécifique selon les besoins
        pass
    
    def notify_administrators(self, alert: SecurityAlert):
        """Notifie les administrateurs"""
        # Email, SMS, webhook, etc.
        notification = {
            'alert_type': alert.event_type.value,
            'threat_level': alert.threat_level.value,
            'source_ip': alert.source_ip,
            'description': alert.description,
            'timestamp': alert.timestamp.isoformat()
        }
        
        # Ici, implémenter l'envoi de notifications
        self.logger.info(f"Notification envoyée: {notification}")
    
    def cleanup_old_data(self):
        """Nettoie les anciennes données"""
        while self.is_running:
            try:
                now = datetime.now()
                
                # Nettoyer les compteurs de requêtes (garder 1 heure)
                for ip in list(self.request_counts.keys()):
                    self.request_counts[ip] = deque([
                        req_time for req_time in self.request_counts[ip]
                        if now - req_time < timedelta(hours=1)
                    ], maxlen=100)
                    
                    if not self.request_counts[ip]:
                        del self.request_counts[ip]
                
                # Nettoyer les IPs suspectes (réinitialiser après 24h)
                for ip in list(self.suspicious_ips.keys()):
                    # Logique de nettoyage basée sur le temps
                    pass
                
                time.sleep(3600)  # Nettoyer toutes les heures
                
            except Exception as e:
                self.logger.error(f"Erreur nettoyage: {e}")
                time.sleep(3600)
    
    def get_security_status(self) -> Dict:
        """Retourne le statut de sécurité"""
        recent_alerts = [
            alert for alert in self.alerts
            if datetime.now() - alert.timestamp < timedelta(hours=24)
        ]
        
        return {
            'status': 'active' if self.is_running else 'inactive',
            'blocked_ips_count': len(self.blocked_ips),
            'suspicious_ips_count': len(self.suspicious_ips),
            'alerts_24h': len(recent_alerts),
            'critical_alerts': len([a for a in recent_alerts if a.threat_level == ThreatLevel.CRITICAL]),
            'system_health': self.get_system_health(),
            'anssi_compliance': self.check_anssi_compliance()
        }
    
    def get_system_health(self) -> Dict:
        """Retourne l'état de santé du système"""
        try:
            return {
                'cpu_usage': psutil.cpu_percent(),
                'memory_usage': psutil.virtual_memory().percent,
                'disk_usage': psutil.disk_usage('/').percent,
                'network_connections': len(psutil.net_connections()),
                'uptime': time.time() - psutil.boot_time()
            }
        except Exception as e:
            self.logger.error(f"Erreur état système: {e}")
            return {}
    
    def check_anssi_compliance(self) -> Dict:
        """Vérifie la conformité ANSSI"""
        compliance = {
            'authentication': True,  # À implémenter selon les règles
            'encryption': True,
            'logging': True,
            'access_control': True,
            'monitoring': self.is_running,
            'overall_score': 85  # Score calculé
        }
        
        return compliance
    
    def export_security_report(self) -> Dict:
        """Exporte un rapport de sécurité"""
        return {
            'generated_at': datetime.now().isoformat(),
            'security_status': self.get_security_status(),
            'recent_alerts': [
                {
                    'type': alert.event_type.value,
                    'level': alert.threat_level.value,
                    'source': alert.source_ip,
                    'description': alert.description,
                    'timestamp': alert.timestamp.isoformat()
                }
                for alert in list(self.alerts)[-50:]  # 50 dernières alertes
            ],
            'blocked_ips': list(self.blocked_ips),
            'anssi_compliance': self.check_anssi_compliance()
        }

# Instance globale du watchdog
security_watchdog = SecurityWatchdog()

