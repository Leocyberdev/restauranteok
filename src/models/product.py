
product.py
from src.database import db

class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    products = db.relationship("Product", backref="category", lazy=True)

    def __repr__(self):
        return f"<Category {self.name}>"


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    cost = db.Column(db.Float, nullable=True)
    image_url = db.Column(db.String(200), nullable=True)
    is_available = db.Column(db.Boolean, default=True)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)

    # Relacionamento com ProductAvailability
    availabilities = db.relationship("ProductAvailability", backref="product", lazy=True, cascade="all, delete-orphan")
    # Relacionamento com IngredientOption
    ingredient_options = db.relationship("IngredientOption", backref="product", lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Product {self.name}>"

class ProductAvailability(db.Model):
    __tablename__ = "product_availabilities"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    day_of_week = db.Column(db.String(10), nullable=False) # Ex: 'Segunda', 'Terça', 'Todos'
    time_of_day = db.Column(db.String(10), nullable=False) # Ex: 'Almoço', 'Jantar', 'Dia Todo'
    price_adjustment = db.Column(db.Float, default=0.0)

    def __repr__(self):
        return f"<ProductAvailability Product:{self.product_id} Day:{self.day_of_week} Time:{self.time_of_day}>"

class IngredientOption(db.Model):
    __tablename__ = "ingredient_options"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False) # Ex: 'Sem Cebola', 'Queijo Extra'
    price_adjustment = db.Column(db.Float, default=0.0)
    is_removable = db.Column(db.Boolean, default=False) # Se é uma opção para remover um ingrediente

    def __repr__(self):
        return f"<IngredientOption Product:{self.product_id} Name:{self.name}>"


