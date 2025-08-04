import os
import sys
from flask import Flask, send_from_directory, redirect, url_for
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env (apenas em desenvolvimento)
load_dotenv()

import logging
from flask import Flask

app = Flask(__name__)

# Configuração básica de log
logging.basicConfig(level=logging.INFO)  # mudar para DEBUG durante debug
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
)
handler.setFormatter(formatter)
app.logger.addHandler(handler)

@app.errorhandler(500)
def internal_error(e):
    app.logger.exception("Erro interno do servidor")
    return "Erro interno", 500

# seu restante de setup abaixo...


# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# Configurações usando variáveis de ambiente
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'asdf#FGSgvasgf$5$WGT')

# Database configuration - usa PostgreSQL no Render, SQLite localmente

database_url = os.getenv("DATABASE_URL")
print(f"DEBUG: Valor de DATABASE_URL do ambiente: {database_url}") # Adicione esta linha

if database_url:
    # Se DATABASE_URL está definida (Render), usa ela
    if database_url.startswith("postgres://"):
        # Render usa postgres://, mas SQLAlchemy 1.4+ precisa de postgresql://
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    print(f"DEBUG: Usando DATABASE_URI (produção): {app.config['SQLALCHEMY_DATABASE_URI']}") # Adicione esta linha
else:
    # Fallback para SQLite local
    sqlite_path = os.path.join(os.path.dirname(__file__), 'database', 'app.db')
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{sqlite_path}"
    print(f"DEBUG: Usando DATABASE_URI (local): {app.config['SQLALCHEMY_DATABASE_URI']}") # Adicione esta linha
    print(f"DEBUG: Caminho completo do SQLite: {os.path.abspath(sqlite_path)}") # Adicione esta linha


app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
from src.database import db
db.init_app(app)

# Flask-Login configuration
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# Flask-Mail configuration
app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER", "smtp.googlemail.com")
app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT", 587))
app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS", "True").lower() == "true"
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME", "restau10rante@gmail.com")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD", "vdpm xnas qrak rvjl")
mail = Mail(app)

# Flask-Migrate configuration
migrate = Migrate(app, db)

# Import models after db is initialized
from src.models.user import User
from src.models.product import Category, Product
from src.models.order import Order, OrderItem
from src.models.employee import Employee, TimeRecord
from src.models.promotion import Promotion, Coupon
from src.models.expense import Expense

with app.app_context():
    db.create_all()
    print("✅ Tabelas criadas com sucesso!")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Default route
@app.route('/')
def index():
    return redirect(url_for('auth.login'))

# Serve static files (if needed, this is usually handled by web server in production)
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


from src.routes.auth import auth_bp
from src.routes.admin import admin_bp
from src.routes.client import client_bp

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(client_bp)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)





