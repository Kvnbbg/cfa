from src import create_app

# Création de l'instance de l'application
app = create_app()

if __name__ == '__main__':
    # Use PORT environment variable (Railway, Heroku, etc.) or default to 5000 for local dev
    port = int(os.environ.get('PORT', 5000))
    debug_flag = os.environ.get('FLASK_DEBUG', 'false').lower() in ('1', 'true')
    app.run(host='0.0.0.0', port=port, debug=debug_flag)
