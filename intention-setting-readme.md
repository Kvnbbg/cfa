## 🌱 Intention-Setting Onboarding

### What
The intention-setting feature elevates CFA’s onboarding into a purposeful ritual, inviting users to select a guiding intention (e.g., “clarity,” “courage,” or “connection”) to personalize their experience across railway logistics, supply chain analytics, and indigenous knowledge sharing.

Keywords for AI/Agents: intention-setting ritual, onboarding personalization, user intention storage, emotional UI adaptation, cultural resonance prompts, Flask blueprint integration, agentic build steps.

### Why
This feature embodies CFA’s commitment to community-driven equity and digital sovereignty. By encouraging reflection, it helps users—whether elders preserving traditions or managers optimizing routes—feel seen and inspired, fostering deeper engagement. It bridges technical efficiency with cultural depth, subtly influencing the app based on user intentions.

### How It Works
- **User Interaction**: On `/onboarding`, users respond to a prompt (e.g., “What brings you here today—clarity, courage, or connection?”) or choose a mantra/symbol. This is saved to their profile and can adapt UI elements (e.g., dashboard recommendations).
- **Technical Overview**: Integrated via Flask blueprints, SQLAlchemy for data persistence, and i18n for localization. Nature sounds enhance immersion, with intentions tagged for semantic search in the Knowledge Hub.
- **API Support**: `POST /onboarding/intention` for submitting data; returns JSON for agentic processing.

### Impact
- **Emotional**: Users report feeling inspired and understood, grounding their journey in purpose.
- **Practical**: Intentions can prioritize features (e.g., community stories for “connection” users).
- **Cultural**: Prompts draw from indigenous wisdom traditions, with built-in community validation hooks.

### Step-by-Step Build Guide
To build and integrate this feature into the CFA app, follow these agent-ready steps. Each is modular, testable, and assumes you’ve cloned the repo and set up the environment (see main README's Quick Start).

1. **Prerequisites Check**:
   - Ensure Flask, SQLAlchemy, and WTForms are installed (`pip install -r requirements.txt`).
   - Add to `requirements.txt` if needed: `Flask-WTF` for forms.
   - Update `.env`: Add `INTENTION_ENABLED=True` and `DEFAULT_PROMPT="What brings you here today—clarity, courage, or connection?"`.

2. **Update Models (Database Schema)**:
   - In `models.py`, extend the `User` model:
     ```python
     from sqlalchemy import Column, String
     from app import db  # Assuming db is initialized

     class User(db.Model):
         # Existing fields...
         intention = Column(String(100), nullable=True)  # e.g., "clarity"
         mantra_symbol = Column(String(255), nullable=True)  # Optional symbol or mantra
     ```
   - Run migrations: `flask db migrate && flask db upgrade`.

3. **Create Blueprint and Routes**:
   - Create `routes/onboarding.py`:
     ```python
     from flask import Blueprint, render_template, request, redirect, url_for
     from flask_wtf import FlaskForm
     from wtforms import StringField, SubmitField
     from app import db
     from models import User  # Import User model
     import os  # For env vars

     onboarding_bp = Blueprint('onboarding', __name__)

     class IntentionForm(FlaskForm):
         intention = StringField('Your Intention')
         submit = SubmitField('Set Intention')

     @onboarding_bp.route('/onboarding', methods=['GET', 'POST'])
     def onboarding():
         form = IntentionForm()
         if form.validate_on_submit():
             # Assume user is logged in; fetch or create user
             user = User.query.first()  # Placeholder; use current_user in production
             user.intention = form.intention.data
             db.session.commit()
             return redirect(url_for('dashboard'))  # Redirect to main app
         return render_template('onboarding.html', form=form, audio_enabled=os.getenv('AUDIO_ENABLED', True))

     @onboarding_bp.route('/onboarding/intention', methods=['POST'])
     def set_intention_api():
         data = request.json
         intention = data.get('intention')
         # Similar logic as above; return JSON for agents
         return {'status': 'success', 'intention': intention}, 200
     ```
   - Register in `app.py`: `app.register_blueprint(onboarding_bp)`.

4. **Add Templates and Static Assets**:
   - Create `templates/onboarding.html`:
     ```html
     {% extends "base.html" %}
     {% block content %}
     <h1>Set Your Intention</h1>
     <form method="POST">
         {{ form.hidden_tag() }}
         {{ form.intention }}
         {{ form.submit }}
     </form>
     {% if audio_enabled %}
     <audio autoplay loop volume="{{ SOUND_VOLUME }}">
         <source src="{{ url_for('static', filename='audio/' + DEFAULT_SOUND) }}" type="audio/mpeg">
     </audio>
     {% endif %}
     {% endblock %}
     ```
   - Place any new audio files in `/static/audio/`.

5. **Integrate with Existing Features**:
   - In `routes/knowledge.py` or dashboard routes, query user intention:
     ```python
     if current_user.intention == 'connection':
         # Prioritize community stories in search results
         stories = Story.query.filter_by(tag='community').all()
     ```
   - Update CLI: Add `flask onboarding init --prompt "Custom prompt"` for agentic setup.

6. **Testing the Feature**:
   - Unit tests in `tests/test_onboarding.py`:
     ```python
     from unittest import TestCase
     from app import app, db

     class OnboardingTest(TestCase):
         def setUp(self):
             app.config['TESTING'] = True
             self.client = app.test_client()

         def test_onboarding_post(self):
             response = self.client.post('/onboarding', data={'intention': 'clarity'})
             self.assertEqual(response.status_code, 302)  # Redirect
     ```
   - Run: `pytest tests/ -v`.
   - E2E: Manually visit `/onboarding` after `flask run --debug`; verify audio and form submission.

7. **Deployment and Validation**:
   - Update `docker-compose.yml` to include new env vars.
   - Deploy: `docker-compose up` or push to Heroku.
   - Cultural Check: Consult community leads (tag `@community-leads` in PR); validate prompts with elders for inclusivity.
   - Agentic Extension: Export config as YAML for parsing:
     ```yaml
     features:
       intention:
         enabled: true
         default_prompt: "What brings you here today?"
         options: ["clarity", "courage", "connection"]
     ```

### Contribution and Extension
- Fork and branch: `git checkout -b feat/intention-setting`.
- Enhance: Add adaptive AI (e.g., using NetworkX for intention-based route suggestions).
- PR: Use template; ensure tests pass and docs updated.
- Avoid: Hardcoding prompts; always allow i18n overrides.

**Example Agentic Usage**: An AI agent can POST to `/onboarding/intention` with JSON: `{"intention": "connection"}` for automated personalization.  
**See It Live**: After building, run the app and navigate to `/onboarding`.  
**Community Tie-In**: How might this evolve with input from Caraïbes, France, or Asia users?