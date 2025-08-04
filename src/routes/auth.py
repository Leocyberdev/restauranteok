from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message
from src.models.user import User
from src.database import db
#from validate_docbr import CPF                      ESSA LINHA FOI COMENTADA PARA TESTE DEZATIVANDO A AUTENTICAÇÃO DE CPF

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for("admin.dashboard"))
        else:
            return redirect(url_for("client.home"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            if user.is_admin:
                return redirect(url_for("admin.dashboard"))
            else:
                return redirect(url_for("client.home"))
        else:
            flash("Nome de usuário ou senha inválidos")
    return render_template("login.html")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("client.home"))

    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        phone = request.form.get("phone")
        cpf = request.form.get("cpf")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        #cpf_validator = CPF()                                               ESSA LINHA FOI COMENTADA PARA TESTE DEZATIVANDO A AUTENTICAÇÃO DE CPF

        # Validações
        if not username or len(username) < 3:
            flash("Nome de usuário deve ter pelo menos 3 caracteres", "danger")
        elif not email or "@" not in email:
            flash("Email inválido", "danger")
        elif not phone or len(phone) < 10:
            flash("Telefone inválido", "danger")
        #elif not cpf or not cpf_validator.validate(cpf):                             ESSA LINHA FOI COMENTADA PARA TESTE DEZATIVANDO A AUTENTICAÇÃO DE CPF
            flash("CPF inválido", "danger")
        elif User.query.filter_by(cpf=cpf).first():
            flash("CPF já cadastrado", "danger")
        elif not password or len(password) < 6:
            flash("Senha deve ter pelo menos 6 caracteres", "danger")
        elif password != confirm_password:
            flash("As senhas não coincidem", "danger")
        elif User.query.filter_by(username=username).first():
            flash("Nome de usuário já existe", "danger")
        elif User.query.filter_by(email=email).first():
            flash("Email já registrado", "danger")
        else:
            new_user = User(
                username=username,
                email=email,
                phone=phone,
                cpf=cpf,
                is_admin=False
            )
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            flash("Registro bem-sucedido! Por favor, faça login.", "success")
            return redirect(url_for("auth.login"))

    return render_template("login.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))

@auth_bp.route("/reset_password_request", methods=["GET", "POST"])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for("client.home"))
    
    if request.method == "POST":
        email = request.form.get("email")
        user = User.query.filter_by(email=email).first()
        if user:
            token = user.get_reset_token()
            send_password_reset_email(user, token)
            flash("Verifique seu email para instruções de redefinição de senha")
            return redirect(url_for("auth.login"))
        else:
            flash("Email não encontrado")
    
    return render_template("login.html")

@auth_bp.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for("client.home"))
    
    user = User.verify_reset_token(token)
    if not user:
        flash("Token inválido ou expirado")
        return redirect(url_for("auth.reset_password_request"))
    
    if request.method == "POST":
        password = request.form.get("password")
        user.set_password(password)
        user.reset_token = None
        user.reset_token_expiration = None
        db.session.commit()
        flash("Sua senha foi redefinida com sucesso!")
        return redirect(url_for("auth.login"))
    
    return render_template("reset_password.html")

def send_password_reset_email(user, token):
    from flask import current_app
    from flask_mail import Mail
    
    mail = Mail(current_app)
    msg = Message(
        "Redefinição de Senha - Sistema de Restaurante",
        sender="noreply@restaurant.com",
        recipients=[user.email]
    )
    msg.body = f"""Para redefinir sua senha, visite o seguinte link:
{url_for("auth.reset_password", token=token, _external=True)}

Se você não fez esta solicitação, simplesmente ignore este email e nenhuma alteração será feita.
"""
    mail.send(msg)

