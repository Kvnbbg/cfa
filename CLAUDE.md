# CFA Agentic Workflow Guide

Ce fichier conserve le contexte opérationnel du projet afin d'améliorer la continuité et la qualité des contributions. Il est aligné sur les recommandations Anthropic pour les flux de travail agentiques.

## 🎯 Contexte du projet
- **Stack** : Flask (Python), WSGI via `main.py`, entry Vercel via `app.py`.
- **Objectif** : Plateforme communautaire pour logistique ferroviaire, supply chain et préservation culturelle.
- **Déploiements** : Railway (Procfile/Gunicorn) + Vercel (serverless Python).

## 🧭 Méthode de travail recommandée
- **Conserver le contexte** : garder ce fichier à jour avec les décisions, conventions et états de déploiement.
- **Intervention temps réel** : utiliser la touche Échap pour interrompre un plan si une contrainte change.
- **Paralléliser avec sous-agents** : déléguer l’audit, les tests, ou la doc à des agents distincts pour accélérer.

## ✅ Checklist avant PR
- [ ] Mise à jour des docs (README/DEPLOYMENT) si déploiement modifié.
- [ ] Validation de la configuration Vercel (fichier `vercel.json`).
- [ ] Consistance des points d’entrée WSGI (`main.py`, `app.py`).
- [ ] Ajout/MAJ de variables d’environnement décrites.

## 🧪 Commandes utiles
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

## 🚀 Déploiement Vercel (rappel)
- Le handler Vercel pointe sur `app.py`.
- Le fichier `vercel.json` configure `@vercel/python` et route tout vers `app.py`.
- Variables d’environnement (Vercel dashboard) : `SECRET_KEY`, `DATABASE_URL`, `FLASK_DEBUG=false`.

## 🧩 Notes d’architecture
- Préserver la séparation **création d’app** (`src.create_app`) / **run** (`main.py`).
- Éviter les side-effects au chargement de module côté serverless.
