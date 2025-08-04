from src.main import app
from src.database import db
from src.models.user import User

with app.app_context():
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        admin_user = User(username='admin', email='admin@example.com', cpf='000.000.000-00', is_admin=True)
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        db.session.commit()
        print('Usuário admin adicionado com sucesso!')
    else:
        print('Usuário admin já existe.')


