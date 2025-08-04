from datetime import datetime
from src.database import db
import pytz

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default="recebido")  # recebido, em_preparo, pronto, saiu_para_entrega, entregue, cancelado
    payment_method = db.Column(db.String(20), nullable=False)  # dinheiro, cartao, pix
    delivery_type = db.Column(db.String(20), nullable=False)  # entrega, retirada
    delivery_address = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(pytz.utc))
    estimated_time = db.Column(db.Integer, default=30)  # tempo estimado em minutos
    
    user = db.relationship("User", backref="orders")
    items = db.relationship("OrderItem", backref="order", lazy=True)

    def __repr__(self):
        return f"<Order {self.id}>"

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    
    product = db.relationship("Product", backref="order_items")

    def __repr__(self):
        return f"<OrderItem {self.id}>"

