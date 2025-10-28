"""
Système de vérification et prévention des doublons pour CFA
Évite les fichiers, fonctions et ressources en double
"""

import os
import hashlib
import ast
import json
from typing import Dict, List, Set, Tuple, Optional
from pathlib import Path
from collections import defaultdict
import difflib

class DuplicateChecker:
    """Vérificateur de doublons intelligent"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.file_hashes = {}
        self.function_signatures = defaultdict(list)
        self.class_signatures = defaultdict(list)
        self.duplicates_found = []
        
        # Extensions à vérifier
        self.code_extensions = {'.py', '.js', '.css', '.html', '.json', '.md'}
        self.ignore_patterns = {
            '__pycache__',
            '.git',
            'node_modules',
            '.venv',
            'venv',
            '.pytest_cache',
            '.coverage'
        }
    
    def scan_project(self) -> Dict[str, List]:
        """Scanne tout le projet pour détecter les doublons"""
        print("🔍 Scan du projet pour détecter les doublons...")
        
        results = {
            'duplicate_files': [],
            'duplicate_functions': [],
            'duplicate_classes': [],
            'similar_files': [],
            'recommendations': []
        }
        
        # Scanner les fichiers
        for file_path in self._get_project_files():
            self._analyze_file(file_path)
        
        # Détecter les doublons
        results['duplicate_files'] = self._find_duplicate_files()
        results['duplicate_functions'] = self._find_duplicate_functions()
        results['duplicate_classes'] = self._find_duplicate_classes()
        results['similar_files'] = self._find_similar_files()
        results['recommendations'] = self._generate_recommendations(results)
        
        return results
    
    def _get_project_files(self) -> List[Path]:
        """Récupère tous les fichiers du projet à analyser"""
        files = []
        
        for root, dirs, filenames in os.walk(self.project_root):
            # Ignorer les dossiers spécifiés
            dirs[:] = [d for d in dirs if d not in self.ignore_patterns]
            
            for filename in filenames:
                file_path = Path(root) / filename
                
                # Vérifier l'extension
                if file_path.suffix in self.code_extensions:
                    files.append(file_path)
        
        return files
    
    def _analyze_file(self, file_path: Path):
        """Analyse un fichier pour extraire ses caractéristiques"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Hash du contenu
            content_hash = hashlib.sha256(content.encode()).hexdigest()
            self.file_hashes[str(file_path)] = {
                'hash': content_hash,
                'size': len(content),
                'lines': len(content.splitlines())
            }
            
            # Analyser le code Python
            if file_path.suffix == '.py':
                self._analyze_python_file(file_path, content)
            
            # Analyser le JavaScript
            elif file_path.suffix == '.js':
                self._analyze_javascript_file(file_path, content)
                
        except Exception as e:
            print(f"⚠️ Erreur lors de l'analyse de {file_path}: {e}")
    
    def _analyze_python_file(self, file_path: Path, content: str):
        """Analyse spécifique pour les fichiers Python"""
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    signature = self._get_function_signature(node)
                    self.function_signatures[signature].append({
                        'file': str(file_path),
                        'name': node.name,
                        'line': node.lineno,
                        'args': [arg.arg for arg in node.args.args],
                        'body_hash': hashlib.sha256(ast.dump(node).encode()).hexdigest()
                    })
                
                elif isinstance(node, ast.ClassDef):
                    signature = self._get_class_signature(node)
                    self.class_signatures[signature].append({
                        'file': str(file_path),
                        'name': node.name,
                        'line': node.lineno,
                        'methods': [n.name for n in node.body if isinstance(n, ast.FunctionDef)],
                        'body_hash': hashlib.sha256(ast.dump(node).encode()).hexdigest()
                    })
                    
        except SyntaxError as e:
            print(f"⚠️ Erreur de syntaxe dans {file_path}: {e}")
        except Exception as e:
            print(f"⚠️ Erreur lors de l'analyse Python de {file_path}: {e}")
    
    def _analyze_javascript_file(self, file_path: Path, content: str):
        """Analyse basique pour les fichiers JavaScript"""
        # Analyse simple basée sur les patterns
        import re
        
        # Détecter les fonctions
        function_pattern = r'function\s+(\w+)\s*\([^)]*\)'
        functions = re.findall(function_pattern, content)
        
        for func_name in functions:
            signature = f"js_function_{func_name}"
            self.function_signatures[signature].append({
                'file': str(file_path),
                'name': func_name,
                'language': 'javascript'
            })
    
    def _get_function_signature(self, node: ast.FunctionDef) -> str:
        """Génère une signature unique pour une fonction"""
        args = [arg.arg for arg in node.args.args]
        return f"{node.name}({','.join(args)})"
    
    def _get_class_signature(self, node: ast.ClassDef) -> str:
        """Génère une signature unique pour une classe"""
        methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
        return f"{node.name}[{','.join(sorted(methods))}]"
    
    def _find_duplicate_files(self) -> List[Dict]:
        """Trouve les fichiers dupliqués (même contenu)"""
        duplicates = []
        hash_groups = defaultdict(list)
        
        # Grouper par hash
        for file_path, info in self.file_hashes.items():
            hash_groups[info['hash']].append(file_path)
        
        # Identifier les doublons
        for file_hash, files in hash_groups.items():
            if len(files) > 1:
                duplicates.append({
                    'hash': file_hash,
                    'files': files,
                    'size': self.file_hashes[files[0]]['size']
                })
        
        return duplicates
    
    def _find_duplicate_functions(self) -> List[Dict]:
        """Trouve les fonctions dupliquées"""
        duplicates = []
        
        for signature, functions in self.function_signatures.items():
            if len(functions) > 1:
                # Vérifier si les corps sont identiques
                body_groups = defaultdict(list)
                for func in functions:
                    body_hash = func.get('body_hash', 'unknown')
                    body_groups[body_hash].append(func)
                
                for body_hash, func_group in body_groups.items():
                    if len(func_group) > 1:
                        duplicates.append({
                            'signature': signature,
                            'functions': func_group,
                            'body_hash': body_hash
                        })
        
        return duplicates
    
    def _find_duplicate_classes(self) -> List[Dict]:
        """Trouve les classes dupliquées"""
        duplicates = []
        
        for signature, classes in self.class_signatures.items():
            if len(classes) > 1:
                # Vérifier si les corps sont identiques
                body_groups = defaultdict(list)
                for cls in classes:
                    body_hash = cls.get('body_hash', 'unknown')
                    body_groups[body_hash].append(cls)
                
                for body_hash, class_group in body_groups.items():
                    if len(class_group) > 1:
                        duplicates.append({
                            'signature': signature,
                            'classes': class_group,
                            'body_hash': body_hash
                        })
        
        return duplicates
    
    def _find_similar_files(self, similarity_threshold: float = 0.8) -> List[Dict]:
        """Trouve les fichiers similaires (mais pas identiques)"""
        similar = []
        files = list(self.file_hashes.keys())
        
        for i, file1 in enumerate(files):
            for file2 in files[i+1:]:
                # Éviter les fichiers identiques
                if self.file_hashes[file1]['hash'] == self.file_hashes[file2]['hash']:
                    continue
                
                # Calculer la similarité
                similarity = self._calculate_file_similarity(file1, file2)
                
                if similarity >= similarity_threshold:
                    similar.append({
                        'file1': file1,
                        'file2': file2,
                        'similarity': similarity
                    })
        
        return similar
    
    def _calculate_file_similarity(self, file1: str, file2: str) -> float:
        """Calcule la similarité entre deux fichiers"""
        try:
            with open(file1, 'r', encoding='utf-8') as f:
                content1 = f.read().splitlines()
            
            with open(file2, 'r', encoding='utf-8') as f:
                content2 = f.read().splitlines()
            
            # Utiliser difflib pour calculer la similarité
            matcher = difflib.SequenceMatcher(None, content1, content2)
            return matcher.ratio()
            
        except Exception:
            return 0.0
    
    def _generate_recommendations(self, results: Dict) -> List[str]:
        """Génère des recommandations pour résoudre les doublons"""
        recommendations = []
        
        # Recommandations pour les fichiers dupliqués
        if results['duplicate_files']:
            recommendations.append(
                f"🔄 {len(results['duplicate_files'])} groupe(s) de fichiers dupliqués détecté(s). "
                "Considérez la suppression ou la consolidation."
            )
        
        # Recommandations pour les fonctions dupliquées
        if results['duplicate_functions']:
            recommendations.append(
                f"🔧 {len(results['duplicate_functions'])} fonction(s) dupliquée(s) détectée(s). "
                "Créez des modules utilitaires pour éviter la duplication."
            )
        
        # Recommandations pour les classes dupliquées
        if results['duplicate_classes']:
            recommendations.append(
                f"🏗️ {len(results['duplicate_classes'])} classe(s) dupliquée(s) détectée(s). "
                "Utilisez l'héritage ou la composition pour réduire la duplication."
            )
        
        # Recommandations pour les fichiers similaires
        if results['similar_files']:
            recommendations.append(
                f"📋 {len(results['similar_files'])} fichier(s) similaire(s) détecté(s). "
                "Vérifiez s'ils peuvent être fusionnés ou refactorisés."
            )
        
        # Recommandations générales
        if not any(results.values()):
            recommendations.append("✅ Aucun doublon détecté ! Votre code est bien organisé.")
        else:
            recommendations.extend([
                "💡 Utilisez des modules partagés pour les fonctions communes",
                "📁 Organisez votre code en packages thématiques",
                "🔍 Effectuez des revues de code régulières",
                "🛠️ Utilisez des outils de refactoring automatique"
            ])
        
        return recommendations
    
    def fix_duplicates(self, results: Dict, auto_fix: bool = False) -> Dict:
        """Propose ou applique des corrections pour les doublons"""
        fixes_applied = {
            'files_removed': [],
            'functions_consolidated': [],
            'classes_consolidated': [],
            'manual_review_needed': []
        }
        
        if auto_fix:
            # Auto-fix pour les fichiers identiques
            for duplicate_group in results['duplicate_files']:
                files = duplicate_group['files']
                if len(files) > 1:
                    # Garder le premier, supprimer les autres
                    for file_to_remove in files[1:]:
                        try:
                            os.remove(file_to_remove)
                            fixes_applied['files_removed'].append(file_to_remove)
                            print(f"🗑️ Fichier supprimé: {file_to_remove}")
                        except Exception as e:
                            print(f"❌ Erreur lors de la suppression de {file_to_remove}: {e}")
        else:
            # Mode suggestion uniquement
            for duplicate_group in results['duplicate_files']:
                fixes_applied['manual_review_needed'].extend(duplicate_group['files'])
        
        return fixes_applied
    
    def generate_report(self, results: Dict) -> str:
        """Génère un rapport détaillé des doublons"""
        report = []
        report.append("=" * 60)
        report.append("🔍 RAPPORT DE DÉTECTION DES DOUBLONS - CFA")
        report.append("=" * 60)
        report.append("")
        
        # Résumé
        report.append("📊 RÉSUMÉ:")
        report.append(f"   • Fichiers dupliqués: {len(results['duplicate_files'])}")
        report.append(f"   • Fonctions dupliquées: {len(results['duplicate_functions'])}")
        report.append(f"   • Classes dupliquées: {len(results['duplicate_classes'])}")
        report.append(f"   • Fichiers similaires: {len(results['similar_files'])}")
        report.append("")
        
        # Détails des fichiers dupliqués
        if results['duplicate_files']:
            report.append("📁 FICHIERS DUPLIQUÉS:")
            for i, group in enumerate(results['duplicate_files'], 1):
                report.append(f"   Groupe {i} (Taille: {group['size']} octets):")
                for file_path in group['files']:
                    report.append(f"     - {file_path}")
                report.append("")
        
        # Détails des fonctions dupliquées
        if results['duplicate_functions']:
            report.append("🔧 FONCTIONS DUPLIQUÉES:")
            for i, group in enumerate(results['duplicate_functions'], 1):
                report.append(f"   Groupe {i} - Signature: {group['signature']}")
                for func in group['functions']:
                    report.append(f"     - {func['file']}:{func['line']} - {func['name']}")
                report.append("")
        
        # Recommandations
        if results['recommendations']:
            report.append("💡 RECOMMANDATIONS:")
            for rec in results['recommendations']:
                report.append(f"   • {rec}")
            report.append("")
        
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def save_report(self, results: Dict, output_file: str = "duplicate_report.txt"):
        """Sauvegarde le rapport dans un fichier"""
        report = self.generate_report(results)
        
        output_path = self.project_root / output_file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"📄 Rapport sauvegardé: {output_path}")
        return output_path

def check_project_duplicates(project_root: str = "/home/ubuntu/caraibes-france-asie"):
    """Fonction utilitaire pour vérifier les doublons du projet"""
    checker = DuplicateChecker(project_root)
    results = checker.scan_project()
    
    # Afficher le rapport
    print(checker.generate_report(results))
    
    # Sauvegarder le rapport
    checker.save_report(results)
    
    return results

if __name__ == "__main__":
    # Vérification automatique
    results = check_project_duplicates()
    
    # Proposer des corrections
    if any(results.values()):
        print("\n🔧 Voulez-vous appliquer les corrections automatiques ? (y/N)")
        response = input().lower().strip()
        
        if response == 'y':
            checker = DuplicateChecker("/home/ubuntu/caraibes-france-asie")
            fixes = checker.fix_duplicates(results, auto_fix=True)
            print(f"✅ Corrections appliquées: {fixes}")
        else:
            print("ℹ️ Corrections non appliquées. Consultez le rapport pour les actions manuelles.")
    else:
        print("✅ Aucune correction nécessaire !")

