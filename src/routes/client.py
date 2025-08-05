
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, session
from flask_login import login_required, current_user
from src.models.user import User
from src.models.product import Category, Product, ProductAvailability, IngredientOption
from src.models.order import Order, OrderItem
from src.models.promotion import Coupon
from src.database import db
from datetime import datetime

client_bp = Blueprint("client", __name__, url_prefix="/client")

@client_bp.route("/home")
@login_required
def home():
    # Produtos em destaque (últimos 6 produtos)
    featured_products = Product.query.filter_by(is_available=True).limit(6).all()
    categories = Category.query.all()
    return render_template("client/home.html", featured_products=featured_products, categories=categories)

# Em seu arquivo de rotas (client_bp)

@client_bp.route("/menu")
@login_required
def menu():
    # Imports e obtenção de data/hora permanecem os mesmos
    from datetime import datetime
    category_id = request.args.get("category", type=int)
    
    current_weekday = datetime.now().weekday()
    weekdays = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
    current_day = weekdays[current_weekday]
    
    current_hour = datetime.now().hour
    current_time = "Almoço" if current_hour < 15 else "Jantar"
    
    # A busca inicial de produtos permanece a mesma
    if category_id:
        products_query = Product.query.filter_by(category_id=category_id, is_available=True)
    else:
        products_query = Product.query.filter_by(is_available=True)
    
    # Usar options(joinedload(...)) é mais eficiente para carregar dados relacionados
    # e ajuda a evitar o problema de `product.category` ser None.
    from sqlalchemy.orm import joinedload
    products = products_query.options(joinedload(Product.category)).all()

    # --- INÍCIO DA CORREÇÃO ---

    processed_products = [] # Renomeado de available_products para maior clareza
    for product in products:
        availabilities = ProductAvailability.query.filter_by(product_id=product.id).all()
        
        is_available_now = True
        price_adjustment = 0
        
        if availabilities:
            is_available_now = False
            for availability in availabilities:
                if (availability.day_of_week == current_day or availability.day_of_week == "Todos") and \
                   (availability.time_of_day == current_time or availability.time_of_day == "Dia Todo"):
                    is_available_now = True
                    price_adjustment = availability.price_adjustment
                    break
        
        if is_available_now:
            ingredient_options = IngredientOption.query.filter_by(product_id=product.id).all()
            
            # **A MUDANÇA PRINCIPAL ESTÁ AQUI**
            # Em vez de modificar 'product', criamos um dicionário com os dados para o template.
            product_data = {
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "image_url": product.image_url,
                "price": product.price,
                "category": product.category, # O objeto de categoria inteiro é passado
                "current_price": product.price + price_adjustment,
                "price_adjustment": price_adjustment,
                "ingredient_options": ingredient_options
            }
            processed_products.append(product_data)

    # --- FIM DA CORREÇÃO ---
    
    categories = Category.query.all()
    
    # Passamos a nova lista de dicionários para o template
    return render_template("client/menu.html", 
                         products=processed_products, # A lista corrigida
                         categories=categories, 
                         selected_category=category_id,
                         current_day=current_day,
                         current_time=current_time)


@client_bp.route("/add_to_cart", methods=["POST"])
@login_required
def add_to_cart():
    product_id = int(request.form.get("product_id"))
    quantity = int(request.form.get("quantity", 1))
    
    # Obter ingredientes opcionais selecionados
    selected_ingredients = request.form.getlist("ingredients")  # Lista de IDs dos ingredientes
    
    # Inicializar carrinho na sessão se não existir
    if "cart" not in session:
        session["cart"] = {}
    
    # Criar uma chave única para o item do carrinho incluindo ingredientes
    cart_key = f"{product_id}_{'-'.join(sorted(selected_ingredients))}"
    
    # Calcular preço total do item com ingredientes
    product = Product.query.get(product_id)
    if not product:
        flash("Produto não encontrado!", "error")
        return redirect(url_for("client.menu"))
    
    # Calcular ajuste de preço por disponibilidade
    from datetime import datetime
    current_weekday = datetime.now().weekday()
    weekdays = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
    current_day = weekdays[current_weekday]
    current_hour = datetime.now().hour
    current_time = "Almoço" if current_hour < 15 else "Jantar"
    
    price_adjustment = 0
    availabilities = ProductAvailability.query.filter_by(product_id=product_id).all()
    for availability in availabilities:
        if (availability.day_of_week == current_day or availability.day_of_week == "Todos") and \
           (availability.time_of_day == current_time or availability.time_of_day == "Dia Todo"):
            price_adjustment = availability.price_adjustment
            break
    
    # Calcular ajuste de preço por ingredientes
    ingredient_adjustment = 0
    ingredient_names = []
    for ingredient_id in selected_ingredients:
        ingredient = IngredientOption.query.get(int(ingredient_id))
        if ingredient and ingredient.product_id == product_id:
            ingredient_adjustment += ingredient.price_adjustment
            ingredient_names.append(ingredient.name)
    
    # Adicionar produto ao carrinho com informações detalhadas
    cart_item = {
        "product_id": product_id,
        "quantity": quantity,
        "base_price": product.price,
        "price_adjustment": price_adjustment,
        "ingredient_adjustment": ingredient_adjustment,
        "selected_ingredients": selected_ingredients,
        "ingredient_names": ingredient_names,
        "final_price": product.price + price_adjustment + ingredient_adjustment
    }
    
    if cart_key in session["cart"]:
        session["cart"][cart_key]["quantity"] += quantity
    else:
        session["cart"][cart_key] = cart_item
    
    session.modified = True
    flash("Produto adicionado ao carrinho!")
    return redirect(url_for("client.menu"))

@client_bp.route("/cart")
@login_required
def cart():
    cart_items = []
    total = 0
    
    if "cart" in session:
        for cart_key, cart_item in session["cart"].items():
            if isinstance(cart_item, dict):  # Novo formato
                product = Product.query.get(cart_item["product_id"])
                if product:
                    item_total = cart_item["final_price"] * cart_item["quantity"]
                    cart_items.append({
                        "cart_key": cart_key,
                        "product": product,
                        "quantity": cart_item["quantity"],
                        "base_price": cart_item["base_price"],
                        "price_adjustment": cart_item["price_adjustment"],
                        "ingredient_adjustment": cart_item["ingredient_adjustment"],
                        "ingredient_names": cart_item["ingredient_names"],
                        "final_price": cart_item["final_price"],
                        "total": item_total
                    })
                    total += item_total
            else:  # Formato antigo (compatibilidade)
                product = Product.query.get(int(cart_key))
                if product:
                    item_total = product.price * cart_item
                    cart_items.append({
                        "cart_key": cart_key,
                        "product": product,
                        "quantity": cart_item,
                        "base_price": product.price,
                        "price_adjustment": 0,
                        "ingredient_adjustment": 0,
                        "ingredient_names": [],
                        "final_price": product.price,
                        "total": item_total
                    })
                    total += item_total
    
    return render_template("client/cart.html", cart_items=cart_items, total=total)

@client_bp.route("/update_cart", methods=["POST"])
@login_required
def update_cart():
    product_id = request.form.get("product_id")
    quantity = int(request.form.get("quantity"))
    
    if "cart" in session:
        if quantity > 0:
            session["cart"][product_id] = quantity
        else:
            session["cart"].pop(product_id, None)
        session.modified = True
    
    return redirect(url_for("client.cart"))

@client_bp.route("/remove_from_cart/<int:product_id>")
@login_required
def remove_from_cart(product_id):
    if "cart" in session:
        session["cart"].pop(str(product_id), None)
        session.modified = True
    
    flash("Produto removido do carrinho!")
    return redirect(url_for("client.cart"))

@client_bp.route("/checkout")
@login_required
def checkout():
    if "cart" not in session or not session["cart"]:
        flash("Seu carrinho está vazio!")
        return redirect(url_for("client.menu"))
    
    cart_items = []
    total = 0
    
    for product_id, quantity in session["cart"].items():
        product = Product.query.get(int(product_id))
        if product:
            item_total = product.price * quantity
            cart_items.append({
                "product": product,
                "quantity": quantity,
                "total": item_total
            })
            total += item_total
    
    return render_template("client/checkout.html", cart_items=cart_items, total=total)

@client_bp.route("/place_order", methods=["POST"])
@login_required
def place_order():
    if "cart" not in session or not session["cart"]:
        flash("Seu carrinho está vazio!")
        return redirect(url_for("client.menu"))
    
    # Dados do formulário
    payment_method = request.form.get("payment_method")
    delivery_type = request.form.get("delivery_type")
    delivery_address = request.form.get("delivery_address") if delivery_type == "entrega" else None
    coupon_code = request.form.get("coupon_code")
    
    # Calcular total
    total = 0
    order_items = []
    
    for product_id, quantity in session["cart"].items():
        product = Product.query.get(int(product_id))
        if product:
            item_total = product.price * quantity
            total += item_total
            order_items.append({
                "product": product,
                "quantity": quantity,
                "unit_price": product.price
            })
    
    # Aplicar cupom se fornecido
    discount = 0
    if coupon_code:
        coupon = Coupon.query.filter_by(code=coupon_code, is_active=True).first()
        if coupon and coupon.used_count < coupon.usage_limit and total >= coupon.min_order_value:
            if coupon.discount_type == "percentage":
                discount = total * (coupon.discount_value / 100)
            else:
                discount = coupon.discount_value
            
            total -= discount
            coupon.used_count += 1
    
    # Criar pedido
    order = Order(
        user_id=current_user.id,
        total_amount=total,
        payment_method=payment_method,
        delivery_type=delivery_type,
        delivery_address=delivery_address
    )
    db.session.add(order)
    db.session.flush()  # Para obter o ID do pedido
    
    # Adicionar itens do pedido
    for item in order_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item["product"].id,
            quantity=item["quantity"],
            unit_price=item["unit_price"]
        )
        db.session.add(order_item)
    
    db.session.commit()
    
    # Limpar carrinho
    session.pop("cart", None)
    
    flash(f"Pedido #{order.id} realizado com sucesso!")
    return redirect(url_for("client.order_tracking", order_id=order.id))

@client_bp.route("/order_tracking/<int:order_id>")
@login_required
def order_tracking(order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    return render_template("client/order_tracking.html", order=order)

@client_bp.route("/order_history")
@login_required
def order_history():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template("client/order_history.html", orders=orders)

@client_bp.route("/repeat_order/<int:order_id>")
@login_required
def repeat_order(order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    
    # Limpar carrinho atual
    session["cart"] = {}
    
    # Adicionar itens do pedido ao carrinho
    for item in order.items:
        if item.product.is_available:
            session["cart"][str(item.product_id)] = item.quantity
    
    session.modified = True
    flash("Itens do pedido adicionados ao carrinho!")
    return redirect(url_for("client.cart"))

@client_bp.route("/validate_coupon", methods=["POST"])
@login_required
def validate_coupon():
    coupon_code = request.json.get("coupon_code")
    total = float(request.json.get("total"))
    
    coupon = Coupon.query.filter_by(code=coupon_code, is_active=True).first()
    
    if not coupon:
        return jsonify({"valid": False, "message": "Cupom inválido"})
    
    if coupon.used_count >= coupon.usage_limit:
        return jsonify({"valid": False, "message": "Cupom esgotado"})
    
    if total < coupon.min_order_value:
        return jsonify({"valid": False, "message": f"Valor mínimo do pedido: R$ {coupon.min_order_value:.2f}"})
    
    if coupon.discount_type == "percentage":
        discount = total * (coupon.discount_value / 100)
    else:
        discount = coupon.discount_value
    
    new_total = total - discount
    
    return jsonify({
        "valid": True,
        "discount": discount,
        "new_total": new_total,
        "message": f"Cupom aplicado! Desconto de R$ {discount:.2f}"
    })


@client_bp.route("/remove_from_cart_key", methods=["POST"])
@login_required
def remove_from_cart_key():
    cart_key = request.form.get("cart_key")
    if "cart" in session and cart_key in session["cart"]:
        del session["cart"][cart_key]
        session.modified = True
        flash("Item removido do carrinho!", "success")
    return redirect(url_for("client.cart"))


