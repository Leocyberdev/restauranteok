from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from src.models.user import User
from src.models.product import Category, Product
from src.models.order import Order, OrderItem
from src.models.employee import Employee, TimeRecord
from src.models.promotion import Promotion, Coupon
from src.models.expense import Expense
from src.database import db
from datetime import datetime, timedelta
from sqlalchemy import func, cast, Date
import pytz

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.before_request
def require_admin():
    if not current_user.is_authenticated or not current_user.is_admin:
        flash("Acesso negado. Apenas administradores podem acessar esta área.")
        return redirect(url_for("auth.login"))

@admin_bp.route("/dashboard")
@login_required
def dashboard():
    # Estatísticas gerais
    brazil_tz = pytz.timezone("America/Sao_Paulo")
    now_brazil = datetime.now(brazil_tz)
    today_start_utc = now_brazil.replace(hour=0, minute=0, second=0, microsecond=0).astimezone(pytz.utc)
    today_end_utc = now_brazil.replace(hour=23, minute=59, second=59, microsecond=999999).astimezone(pytz.utc)
    week_ago_utc = (now_brazil - timedelta(days=7)).astimezone(pytz.utc)
    month_ago_utc = (now_brazil - timedelta(days=30)).astimezone(pytz.utc)
    
    # Pedidos de hoje
    orders_today = Order.query.filter(Order.created_at >= today_start_utc, Order.created_at <= today_end_utc, Order.status != 'cancelado').count()
    
    # Vendas de hoje
    sales_today = db.session.query(func.sum(Order.total_amount)).filter(
        Order.created_at >= today_start_utc, Order.created_at <= today_end_utc, Order.status != 'cancelado'
    ).scalar() or 0
    
    # Pedidos da semana
    orders_week = Order.query.filter(Order.created_at >= week_ago_utc, Order.status != 'cancelado').count()
    
    # Vendas do mês
    sales_month = db.session.query(func.sum(Order.total_amount)).filter(
        Order.created_at >= month_ago_utc, Order.status != 'cancelado'
    ).scalar() or 0
    
    # Pedidos pendentes
    pending_orders = Order.query.filter(Order.status.in_(["recebido", "em_preparo"])).count()
    
    # Produtos mais vendidos
    top_products = db.session.query(
        Product.name,
        func.sum(OrderItem.quantity).label("total_sold")
    ).select_from(OrderItem).join(Product).group_by(Product.id).order_by(func.sum(OrderItem.quantity).desc()).limit(5).all()

    
    # Cálculo do lucro líquido estimado (vendas - custos dos produtos)
    # Busca todos os itens vendidos com seus custos
    profit_query = db.session.query(
    func.sum((Product.price - func.coalesce(Product.cost, 0)) * OrderItem.quantity).label("estimated_profit")
    ).select_from(OrderItem).join(Product).join(Order).filter(
        Order.created_at >= month_ago_utc, 
        Order.status != 'cancelado'
    ).scalar()

    estimated_profit = profit_query or 0

    # Despesas mensais
    monthly_expenses = db.session.query(func.sum(Expense.amount)).filter(
        Expense.date >= month_ago_utc
    ).scalar() or 0

    # Custo estimado dos produtos vendidos
    estimated_product_cost = db.session.query(
        func.sum(Product.cost * OrderItem.quantity)
    ).select_from(OrderItem).join(Product).join(Order).filter(
        Order.created_at >= month_ago_utc,
        Order.status != 'cancelado'
    ).scalar() or 0

    # Saldo final do mês (receita - despesa - custo dos produtos)
    # Receita é a sales_month já calculada
    final_balance = sales_month - monthly_expenses - estimated_product_cost
    
    return render_template("admin/dashboard.html",
                         orders_today=orders_today,
                         sales_today=sales_today,
                         orders_week=orders_week,
                         sales_month=sales_month,
                         pending_orders=pending_orders,
                         top_products=top_products,
                         estimated_profit=estimated_profit,
                         monthly_expenses=monthly_expenses,
                         final_balance=final_balance,
                         estimated_product_cost=estimated_product_cost)
@admin_bp.route("/products")
@login_required
def products():
    products = Product.query.all()
    categories = Category.query.all()
    return render_template("admin/products.html", products=products, categories=categories)

@admin_bp.route("/products/add", methods=["POST"])
@login_required
def add_product():
    name = request.form.get("name")
    description = request.form.get("description")
    price = float(request.form.get("price"))
    cost = request.form.get("cost")
    cost = float(cost) if cost else None
    category_id = int(request.form.get("category_id"))
    
    product = Product(name=name, description=description, price=price, cost=cost, category_id=category_id)
    db.session.add(product)
    db.session.commit()
    
    flash("Produto adicionado com sucesso!")
    return redirect(url_for("admin.products"))

@admin_bp.route("/products/edit/<int:product_id>", methods=["GET", "POST"])
@login_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    categories = Category.query.all()
    if request.method == "POST":
        product.name = request.form.get("name")
        product.description = request.form.get("description")
        product.price = float(request.form.get("price"))
        cost = request.form.get("cost")
        product.cost = float(cost) if cost else None
        product.category_id = int(request.form.get("category_id"))
        db.session.commit()
        flash("Produto atualizado com sucesso!")
        return redirect(url_for("admin.products"))
    return render_template("admin/edit_product.html", product=product, categories=categories)

@admin_bp.route("/products/delete/<int:product_id>", methods=["POST"])
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash("Produto excluído com sucesso!")
    return redirect(url_for("admin.products"))

@admin_bp.route("/categories")
@login_required
def categories():
    categories = Category.query.all()
    return render_template("admin/categories.html", categories=categories)


@admin_bp.route("/products/<int:product_id>/toggle", methods=["POST"])
@login_required
def toggle_product_availability(product_id):
    product = Product.query.get_or_404(product_id)
    product.is_available = not product.is_available
    db.session.commit()
    flash(f"Disponibilidade do produto '{product.name}' atualizada para {'disponível' if product.is_available else 'indisponível'}.", "success")
    return redirect(url_for("admin.products"))


@admin_bp.route("/categories/add", methods=["POST"])
@login_required
def add_category():
    name = request.form.get("name")
    
    category = Category(name=name)
    db.session.add(category)
    db.session.commit()
    
    flash("Categoria adicionada com sucesso!")
    return redirect(url_for("admin.categories"))

@admin_bp.route("/categories/edit/<int:category_id>", methods=["GET", "POST"])
@login_required
def edit_category(category_id):
    category = Category.query.get_or_404(category_id)
    if request.method == "POST":
        category.name = request.form.get("name")
        db.session.commit()
        flash("Categoria atualizada com sucesso!")
        return redirect(url_for("admin.categories"))
    return render_template("admin/edit_category.html", category=category)

@admin_bp.route("/categories/delete/<int:category_id>", methods=["POST"])
@login_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    
    # LÓGICA ATUALIZADA: Verifica se existem produtos associados a esta categoria
    if category.products:
        flash(f"Não é possível excluir a categoria '{category.name}', pois ela contém produtos. Por favor, mova os produtos para outra categoria antes de excluí-la.", "danger")
        return redirect(url_for("admin.categories"))

    db.session.delete(category)
    db.session.commit()
    flash("Categoria excluída com sucesso!", "success")
    return redirect(url_for("admin.categories"))

@admin_bp.route("/orders")
@login_required
def orders():
    status_filter = request.args.get("status", "all")
    period_filter = request.args.get("period", "all")
    
    # Configurar timezone do Brasil
    brazil_tz = pytz.timezone("America/Sao_Paulo")
    now_brazil = datetime.now(brazil_tz)
    
    # Construir query base
    query = Order.query
    
    # Aplicar filtro de período
    if period_filter == "today":
        today_start_utc = now_brazil.replace(hour=0, minute=0, second=0, microsecond=0).astimezone(pytz.utc)
        today_end_utc = now_brazil.replace(hour=23, minute=59, second=59, microsecond=999999).astimezone(pytz.utc)
        query = query.filter(Order.created_at >= today_start_utc, Order.created_at <= today_end_utc)
    elif period_filter == "week":
        week_start = now_brazil - timedelta(days=now_brazil.weekday())
        week_start_utc = week_start.replace(hour=0, minute=0, second=0, microsecond=0).astimezone(pytz.utc)
        query = query.filter(Order.created_at >= week_start_utc)
    elif period_filter == "month":
        month_start = now_brazil.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_start_utc = month_start.astimezone(pytz.utc)
        query = query.filter(Order.created_at >= month_start_utc)
    
    # Aplicar filtro de status
    if status_filter != "all":
        query = query.filter_by(status=status_filter)
    
    # Executar query e ordenar por data
    orders = query.order_by(Order.created_at.desc()).all()
    
    # Calcular estatísticas para o período selecionado
    total_orders = len(orders)
    total_revenue = sum(order.total_amount for order in orders if order.status != 'cancelado')
    pending_orders = len([order for order in orders if order.status in ['recebido', 'em_preparo']])
    
    return render_template("admin/orders.html", 
                         orders=orders, 
                         status_filter=status_filter,
                         period_filter=period_filter,
                         total_orders=total_orders,
                         total_revenue=total_revenue,
                         pending_orders=pending_orders)

@admin_bp.route("/orders/<int:order_id>/update_status", methods=["POST"])
@login_required
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get("status")
    
    order.status = new_status
    db.session.commit()
    
    flash(f"Status do pedido #{order_id} atualizado para {new_status}")
    return redirect(url_for("admin.orders"))

@admin_bp.route("/employees")
@login_required
def employees():
    employees = Employee.query.all()
    return render_template("admin/employees.html", employees=employees)

@admin_bp.route("/employees/add", methods=["POST"])
@login_required
def add_employee():
    name = request.form.get("name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    role = request.form.get("role")
    
    employee = Employee(name=name, email=email, phone=phone, role=role)
    db.session.add(employee)
    db.session.commit()
    
    flash("Funcionário adicionado com sucesso!")
    return redirect(url_for("admin.employees"))

@admin_bp.route("/employees/edit/<int:employee_id>", methods=["GET", "POST"])
@login_required
def edit_employee(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    if request.method == "POST":
        employee.name = request.form.get("name")
        employee.email = request.form.get("email")
        employee.phone = request.form.get("phone")
        employee.role = request.form.get("role")
        employee.is_active = bool(request.form.get("is_active"))
        db.session.commit()
        flash("Funcionário atualizado com sucesso!")
        return redirect(url_for("admin.employees"))
    return render_template("admin/edit_employee.html", employee=employee)

@admin_bp.route("/employees/delete/<int:employee_id>", methods=["POST"])
@login_required
def delete_employee(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    db.session.delete(employee)
    db.session.commit()
    flash("Funcionário excluído com sucesso!")
    return redirect(url_for("admin.employees"))

@admin_bp.route("/promotions")
@login_required
def promotions():
    promotions = Promotion.query.all()
    coupons = Coupon.query.all()
    return render_template("admin/promotions.html", promotions=promotions, coupons=coupons)

@admin_bp.route("/promotions/add", methods=["POST"])
@login_required
def add_promotion():
    name = request.form.get("name")
    description = request.form.get("description")
    discount_type = request.form.get("discount_type")
    discount_value = float(request.form.get("discount_value"))
    start_date = datetime.strptime(request.form.get("start_date"), "%Y-%m-%d")
    end_date = datetime.strptime(request.form.get("end_date"), "%Y-%m-%d")
    
    promotion = Promotion(
        name=name,
        description=description,
        discount_type=discount_type,
        discount_value=discount_value,
        start_date=start_date,
        end_date=end_date
    )
    db.session.add(promotion)
    db.session.commit()
    
    flash("Promoção adicionada com sucesso!")
    return redirect(url_for("admin.promotions"))

@admin_bp.route("/promotions/edit/<int:promotion_id>", methods=["GET", "POST"])
@login_required
def edit_promotion(promotion_id):
    promotion = Promotion.query.get_or_404(promotion_id)
    if request.method == "POST":
        promotion.name = request.form.get("name")
        promotion.description = request.form.get("description")
        promotion.discount_type = request.form.get("discount_type")
        promotion.discount_value = float(request.form.get("discount_value"))
        promotion.start_date = datetime.strptime(request.form.get("start_date"), "%Y-%m-%d")
        promotion.end_date = datetime.strptime(request.form.get("end_date"), "%Y-%m-%d")
        promotion.is_active = bool(request.form.get("is_active"))
        db.session.commit()
        flash("Promoção atualizada com sucesso!")
        return redirect(url_for("admin.promotions"))
    return render_template("admin/edit_promotion.html", promotion=promotion)

@admin_bp.route("/promotions/delete/<int:promotion_id>", methods=["POST"])
@login_required
def delete_promotion(promotion_id):
    promotion = Promotion.query.get_or_404(promotion_id)
    db.session.delete(promotion)
    db.session.commit()
    flash("Promoção excluída com sucesso!")
    return redirect(url_for("admin.promotions"))

@admin_bp.route("/coupons/add", methods=["POST"])
@login_required
def add_coupon():
    code = request.form.get("code")
    discount_type = request.form.get("discount_type")
    discount_value = float(request.form.get("discount_value"))
    min_order_value = float(request.form.get("min_order_value", 0))
    usage_limit = int(request.form.get("usage_limit", 1))
    start_date = datetime.strptime(request.form.get("start_date"), "%Y-%m-%d")
    end_date = datetime.strptime(request.form.get("end_date"), "%Y-%m-%d")
    
    coupon = Coupon(
        code=code,
        discount_type=discount_type,
        discount_value=discount_value,
        min_order_value=min_order_value,
        usage_limit=usage_limit,
        start_date=start_date,
        end_date=end_date
    )
    db.session.add(coupon)
    db.session.commit()
    
    flash("Cupom adicionado com sucesso!")
    return redirect(url_for("admin.promotions"))

@admin_bp.route("/coupons/edit/<int:coupon_id>", methods=["GET", "POST"])
@login_required
def edit_coupon(coupon_id):
    coupon = Coupon.query.get_or_404(coupon_id)
    if request.method == "POST":
        coupon.code = request.form.get("code")
        coupon.discount_type = request.form.get("discount_type")
        coupon.discount_value = float(request.form.get("discount_value"))
        coupon.min_order_value = float(request.form.get("min_order_value"))
        coupon.usage_limit = int(request.form.get("usage_limit"))
        coupon.start_date = datetime.strptime(request.form.get("start_date"), "%Y-%m-%d")
        coupon.end_date = datetime.strptime(request.form.get("end_date"), "%Y-%m-%d")
        coupon.is_active = bool(request.form.get("is_active"))
        db.session.commit()
        flash("Cupom atualizado com sucesso!")
        return redirect(url_for("admin.promotions"))
    return render_template("admin/edit_coupon.html", coupon=coupon)

@admin_bp.route("/coupons/delete/<int:coupon_id>", methods=["POST"])
@login_required
def delete_coupon(coupon_id):
    coupon = Coupon.query.get_or_404(coupon_id)
    db.session.delete(coupon)
    db.session.commit()
    flash("Cupom excluído com sucesso!")
    return redirect(url_for("admin.promotions"))






@admin_bp.route("/clients")
@login_required
def clients():
    clients = User.query.filter_by(is_admin=False).all()
    return render_template("admin/clients.html", clients=clients)





@admin_bp.route("/expenses")
@login_required
def expenses():
    expenses = Expense.query.order_by(Expense.date.desc()).all()
    return render_template("admin/expenses.html", expenses=expenses)

@admin_bp.route("/expenses/add", methods=["POST"])
@login_required
def add_expense():
    description = request.form.get("description")
    amount = float(request.form.get("amount"))
    expense_type = request.form.get("expense_type")
    date_str = request.form.get("date")
    date = datetime.strptime(date_str, "%Y-%m-%d") if date_str else datetime.utcnow()

    expense = Expense(description=description, amount=amount, expense_type=expense_type, date=date)
    db.session.add(expense)
    db.session.commit()
    flash("Despesa adicionada com sucesso!")
    return redirect(url_for("admin.expenses"))

@admin_bp.route("/expenses/edit/<int:expense_id>", methods=["GET", "POST"])
@login_required
def edit_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    if request.method == "POST":
        expense.description = request.form.get("description")
        expense.amount = float(request.form.get("amount"))
        expense.expense_type = request.form.get("expense_type")
        date_str = request.form.get("date")
        expense.date = datetime.strptime(date_str, "%Y-%m-%d") if date_str else datetime.utcnow()
        db.session.commit()
        flash("Despesa atualizada com sucesso!")
        return redirect(url_for("admin.expenses"))
    return render_template("admin/edit_expense.html", expense=expense)

@admin_bp.route("/expenses/delete/<int:expense_id>", methods=["POST"])
@login_required
def delete_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    db.session.delete(expense)
    db.session.commit()
    flash("Despesa excluída com sucesso!")
    return redirect(url_for("admin.expenses"))



