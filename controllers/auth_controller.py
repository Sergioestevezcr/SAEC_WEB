from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from models.db import get_user_by_email

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Login para administradores: guarda user_id en sesión al validar credenciales."""
    if request.method == "POST":
        email = request.form.get("email","").strip().lower()
        password = request.form.get("password","")
        user = get_user_by_email(email)
        if not user or not check_password_hash(user["password_hash"], password):
            flash("Credenciales inválidas", "error")
            return redirect(url_for("auth.login"))
        session["user_id"] = user["id"]
        session["user_email"] = user["email"]
        session["user_role"] = user["role"]
        flash("Bienvenido al panel de administración", "success")
        return redirect(url_for("admin.dashboard"))
    return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    """Cierra sesión limpiando variables de sesión."""
    session.clear()
    flash("Sesión cerrada.", "success")
    return redirect(url_for("auth.login"))
