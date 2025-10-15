from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.db import insert_contact, get_projects, send_contact_email, verify_recaptcha, get_posts, get_post_by_slug
import os

main_bp = Blueprint("main", __name__)

@main_bp.context_processor
def inject_seo_defaults():
    """Variables globales para templates: marcas, colores, analítica y reCAPTCHA site key."""
    return {
        "SITE_NAME": os.getenv("SITE_NAME", "SAEC"),
        "SITE_DOMAIN": os.getenv("SITE_DOMAIN", "https://example.com"),
        "OG_IMAGE": os.getenv("OG_IMAGE", "/static/img/og-image.jpg"),
        "PRIMARY_COLOR": os.getenv("PRIMARY_COLOR", "#C9A227"),
        "SECONDARY_COLOR": os.getenv("SECONDARY_COLOR", "#0D0D0D"),
        "GA4_ID": os.getenv("GA4_ID",""),
        "FB_PIXEL_ID": os.getenv("FB_PIXEL_ID",""),
        "RECAPTCHA_SITE_KEY": os.getenv("RECAPTCHA_SITE_KEY",""),
    }

@main_bp.route("/")
def index():
    open_projects = get_projects(open_source=True)
    closed_projects = get_projects(open_source=False)
    return render_template("index.html", open_projects=open_projects, closed_projects=closed_projects)

@main_bp.route("/proyectos")
def proyectos():
    all_projects = get_projects()
    return render_template("projects.html", projects=all_projects)

@main_bp.route("/contacto", methods=["GET", "POST"])
def contacto():
    if request.method == "POST":
        # 1) Verifica reCAPTCHA
        token = request.form.get("g-recaptcha-response")
        if not verify_recaptcha(token):
            flash("Valida el reCAPTCHA antes de enviar.", "error")
            return redirect(url_for("main.contacto"))
        # 2) Guarda contacto y dispara email
        payload = {
            "name": request.form.get("name","").strip(),
            "email": request.form.get("email","").strip(),
            "phone": request.form.get("phone","").strip(),
            "message": request.form.get("message","").strip(),
        }
        if not payload["name"] or not payload["email"] or not payload["message"]:
            flash("Por favor completa nombre, correo y mensaje.", "error")
            return redirect(request.referrer or url_for("main.contacto"))
        insert_contact(**payload)
        send_contact_email(payload)
        flash("¡Gracias! Tu mensaje fue enviado correctamente.", "success")
        return redirect(url_for("main.contacto"))
    return render_template("contact.html")

@main_bp.route("/conocenos")
def conocenos():
    return render_template("about.html")

# NUEVAS PÁGINAS
@main_bp.route("/casos-de-exito")
def casos():
    return render_template("cases.html")

@main_bp.route("/planes")
def planes():
    return render_template("plans.html")

# BLOG
@main_bp.route("/blog")
def blog():
    posts = get_posts()
    return render_template("blog_list.html", posts=posts)

@main_bp.route("/blog/<slug>")
def blog_detail(slug):
    post = get_post_by_slug(slug)
    if not post:
        return render_template("404.html"), 404
    return render_template("blog_detail.html", post=post)
