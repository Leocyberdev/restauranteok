import os
import sys
from flask import Flask, redirect, url_for
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env (apenas em desenvolvimento)
load_dotenv()

# ==============================================================================
# CORREÇÃO 1: INICIALIZAR EXTENSÕES SEM O APP
# Inicializamos as extensões aqui, mas as conectamos ao app dentro da função create_app.
# ==============================================================================
from src.database import db
login_manager = LoginManager()
mail = Mail()
migrate = Migrate()

# Importar modelos aqui para que o Alembic (Migrate) possa encontrá-los
from src.models.user import User
from src.models.product import Category, Product, ProductAvailability, IngredientOption
from src.models.order import Order, OrderItem
from src.models.employee import Employee, TimeRecord
from src.models.promotion import Promotion, Coupon
from src.models.expense import Expense


# ==============================================================================
# CORREÇÃO 2: A FUNÇÃO "APPLICATION FACTORY" (create_app)
# Todo o código de configuração do app é movido para dentro desta função.
# ==============================================================================
def create_app():
    """Cria e configura uma instância da aplicação Flask."""
    app = Flask(__name__, static_folder='static')

    # Configurações usando variáveis de ambiente
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'uma-chave-secreta-padrao-forte')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Configuração do Banco de Dados
    database_url = os.getenv("DATABASE_URL")
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url or f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"

    # Conecta as extensões ao app
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)

    # Configuração do Flask-Login
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Configuração do Flask-Mail
    app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER", "smtp.googlemail.com")
    app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT", 587))
    app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS", "True").lower() == "true"
    app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
    app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")

    # Importar e registrar Blueprints (rotas)
    from src.routes.auth import auth_bp
    from src.routes.admin import admin_bp
    from src.routes.client import client_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(client_bp)

    # Rota principal
    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))

    # ==============================================================================
    # CORREÇÃO 3: MOVER A CRIAÇÃO DO ADMIN PARA UM COMANDO CLI
    # Isso evita que o código seja executado na importação.
    # ==============================================================================
    @app.cli.command("create-admin")
    def create_admin_command():
        """Cria o usuário administrador padrão."""
        if User.query.filter_by(username='admin').first():
            print('⚠️ Usuário admin já existe.')
        else:
            admin_user = User(
                username='admin',
                email='admin@example.com',
                cpf='000.000.000-00',
                is_admin=True
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            db.session.commit()
            print('✅ Usuário admin criado com sucesso!')

    return app

# ==============================================================================
# CORREÇÃO 4: PROTEGER A EXECUÇÃO DO APP
# Este bloco só é executado quando você roda "python src/main.py" diretamente.
# ==============================================================================
if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)


