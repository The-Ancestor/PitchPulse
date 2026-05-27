from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import config_options

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager() 

def create_app(config_name='development') :
    app = Flask(__name__)
    app.config.from_object(config_options[config_name])
    db.init_app(app)
    migrate.init_app(app, db)
    
    from app.routes import analytics_bp
    app.register_blueprint(analytics_bp)
    
    login_manager.init_app(app)
    login_manager.login_view = 'analytics.login' # Where to redirect unauthorized guests
    login_manager.login_message_category = 'info'
    
    from app.models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    return app
    
