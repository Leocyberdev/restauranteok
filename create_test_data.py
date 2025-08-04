#!/usr/bin/env python3
"""
Script para criar dados de teste no sistema de restaurante
"""

import sys
import os

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.main import app
from src.database import db
from src.models.user import User
from src.models.product import Category, Product
from src.models.employee import Employee
from src.models.promotion import Promotion, Coupon
from datetime import datetime, timedelta

def create_test_data():
    """Criar dados de teste para o sistema"""
    
    with app.app_context():
        # Criar tabelas se não existirem
        db.create_all()
        
        print("Criando dados de teste...")
        
        # Criar usuário administrador
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', email='admin@restaurant.com', cpf='123.456.789-00', is_admin=True)
            admin.set_password('admin123')
            db.session.add(admin)
            print("✓ Usuário administrador criado")
        
        # Criar usuário cliente
        if not User.query.filter_by(username='cliente').first():
            client = User(username='cliente', email='cliente@restaurant.com', cpf='987.654.321-00', is_admin=False)
            client.set_password('cliente123')
            db.session.add(client)
            print("✓ Usuário cliente criado")
        
        # Criar categorias
        categories_data = [
            'Pratos Principais',
            'Bebidas',
            'Sobremesas'
        ]
        
        for cat_name in categories_data:
            if not Category.query.filter_by(name=cat_name).first():
                category = Category(name=cat_name)
                db.session.add(category)
                print(f"✓ Categoria '{cat_name}' criada")
        
        db.session.commit()
        
        # Criar produtos
        products_data = [
            {
                'name': 'Hambúrguer Artesanal',
                'description': 'Hambúrguer com carne bovina, queijo e salada',
                'price': 25.90,
                'category': 'Pratos Principais'
            },
            {
                'name': 'Pizza Margherita',
                'description': 'Pizza com molho de tomate, mussarela e manjericão',
                'price': 32.50,
                'category': 'Pratos Principais'
            },
            {
                'name': 'Coca-Cola 350ml',
                'description': 'Refrigerante gelado',
                'price': 5.50,
                'category': 'Bebidas'
            },
            {
                'name': 'Suco de Laranja',
                'description': 'Suco natural de laranja',
                'price': 8.90,
                'category': 'Bebidas'
            },
            {
                'name': 'Pudim de Leite',
                'description': 'Pudim caseiro com calda de caramelo',
                'price': 12.90,
                'category': 'Sobremesas'
            },
            {
                'name': 'Brownie com Sorvete',
                'description': 'Brownie quente com sorvete de baunilha',
                'price': 15.90,
                'category': 'Sobremesas'
            }
        ]
        
        for prod_data in products_data:
            if not Product.query.filter_by(name=prod_data['name']).first():
                category = Category.query.filter_by(name=prod_data['category']).first()
                if category:
                    product = Product(
                        name=prod_data['name'],
                        description=prod_data['description'],
                        price=prod_data['price'],
                        category_id=category.id,
                        is_available=True
                    )
                    db.session.add(product)
                    print(f"✓ Produto '{prod_data['name']}' criado")
        
        # Criar funcionários
        employees_data = [
            {
                'name': 'João Silva',
                'email': 'joao@restaurant.com',
                'phone': '(11) 99999-1111',
                'role': 'cozinha'
            },
            {
                'name': 'Maria Santos',
                'email': 'maria@restaurant.com',
                'phone': '(11) 99999-2222',
                'role': 'caixa'
            },
            {
                'name': 'Pedro Oliveira',
                'email': 'pedro@restaurant.com',
                'phone': '(11) 99999-3333',
                'role': 'entregador'
            }
        ]
        
        for emp_data in employees_data:
            if not Employee.query.filter_by(email=emp_data['email']).first():
                employee = Employee(
                    name=emp_data['name'],
                    email=emp_data['email'],
                    phone=emp_data['phone'],
                    role=emp_data['role'],
                    is_active=True
                )
                db.session.add(employee)
                print(f"✓ Funcionário '{emp_data['name']}' criado")
        
        # Criar promoções
        if not Promotion.query.filter_by(name='Desconto de Fim de Semana').first():
            promotion = Promotion(
                name='Desconto de Fim de Semana',
                description='10% de desconto em todos os produtos',
                discount_type='percentage',
                discount_value=10.0,
                start_date=datetime.now(),
                end_date=datetime.now() + timedelta(days=30),
                is_active=True
            )
            db.session.add(promotion)
            print("✓ Promoção 'Desconto de Fim de Semana' criada")
        
        # Criar cupons
        coupons_data = [
            {
                'code': 'BEMVINDO',
                'discount_type': 'percentage',
                'discount_value': 15.0,
                'min_order_value': 30.0,
                'usage_limit': 100
            },
            {
                'code': 'FRETE10',
                'discount_type': 'fixed',
                'discount_value': 10.0,
                'min_order_value': 50.0,
                'usage_limit': 50
            }
        ]
        
        for coup_data in coupons_data:
            if not Coupon.query.filter_by(code=coup_data['code']).first():
                coupon = Coupon(
                    code=coup_data['code'],
                    discount_type=coup_data['discount_type'],
                    discount_value=coup_data['discount_value'],
                    min_order_value=coup_data['min_order_value'],
                    usage_limit=coup_data['usage_limit'],
                    used_count=0,
                    start_date=datetime.now(),
                    end_date=datetime.now() + timedelta(days=60),
                    is_active=True
                )
                db.session.add(coupon)
                print(f"✓ Cupom '{coup_data['code']}' criado")
        
        db.session.commit()
        print("\n🎉 Dados de teste criados com sucesso!")
        print("\nCredenciais de acesso:")
        print("Administrador - Usuário: admin | Senha: admin123")
        print("Cliente - Usuário: cliente | Senha: cliente123")
        print("\nCupons disponíveis:")
        print("- BEMVINDO: 15% de desconto (pedido mínimo R$ 30)")
        print("- FRETE10: R$ 10 de desconto (pedido mínimo R$ 50)")

if __name__ == '__main__':
    create_test_data()

