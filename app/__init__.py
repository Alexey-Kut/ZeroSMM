from flask import Flask, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_TYPE'] = "filesystem"

    db.init_app(app)
    bcrypt.init_app(app)

    from app.auth import auth_bp
    from app.smm import smm_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(smm_bp, url_prefix='/smm')

    @app.route('/')
    def index():
        """Редиректит пользователя на dashboard, если он залогинен, иначе на страницу входа."""
        if 'user_id' in session:
            return redirect(url_for('smm.dashboard'))
        return redirect(url_for('auth.login'))

    with app.app_context():
        db.create_all()

    return app
