from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from models.db import query_all_contacts, get_projects, get_project, create_project, update_project, delete_project, get_posts, get_post_by_slug, create_post, update_post, delete_post

admin_bp = Blueprint("admin", __name__, template_folder="../templates/admin")

def _require_admin():
    return True if (session.get("user_id") and session.get("user_role") == "admin") else False

@admin_bp.route("/")
def dashboard():
    if not _require_admin():
        flash("Debes iniciar sesión como administrador.", "error")
        return redirect(url_for("auth.login"))
    contactos = query_all_contacts()
    proyectos = get_projects()
    posts = get_posts()
    return render_template("admin/dashboard.html", contactos=contactos, proyectos=proyectos, posts=posts)

# === PROJECTS CRUD ===
@admin_bp.route("/projects/new", methods=["GET","POST"])
def project_new():
    if not _require_admin(): return redirect(url_for("auth.login"))
    if request.method == "POST":
        data = {
            "title": request.form.get("title","").strip(),
            "description": request.form.get("description","").strip(),
            "image_url": request.form.get("image_url","").strip(),
            "repo_url": request.form.get("repo_url","").strip(),
            "live_url": request.form.get("live_url","").strip(),
            "is_open_source": request.form.get("is_open_source","1")
        }
        create_project(data)
        flash("Proyecto creado.", "success")
        return redirect(url_for("admin.dashboard"))
    return render_template("admin/project_form.html", item=None)

@admin_bp.route("/projects/<int:id>/edit", methods=["GET","POST"])
def project_edit(id):
    if not _require_admin(): return redirect(url_for("auth.login"))
    item = get_project(id)
    if not item:
        flash("Proyecto no encontrado.", "error")
        return redirect(url_for("admin.dashboard"))
    if request.method == "POST":
        data = {
            "title": request.form.get("title","").strip(),
            "description": request.form.get("description","").strip(),
            "image_url": request.form.get("image_url","").strip(),
            "repo_url": request.form.get("repo_url","").strip(),
            "live_url": request.form.get("live_url","").strip(),
            "is_open_source": request.form.get("is_open_source","1")
        }
        update_project(id, data)
        flash("Proyecto actualizado.", "success")
        return redirect(url_for("admin.dashboard"))
    return render_template("admin/project_form.html", item=item)

@admin_bp.route("/projects/<int:id>/delete", methods=["POST"])
def project_delete(id):
    if not _require_admin(): return redirect(url_for("auth.login"))
    delete_project(id)
    flash("Proyecto eliminado.", "success")
    return redirect(url_for("admin.dashboard"))

# === BLOG CRUD básico ===
@admin_bp.route("/posts/new", methods=["GET","POST"])
def post_new():
    if not _require_admin(): return redirect(url_for("auth.login"))
    if request.method == "POST":
        data = {
            "title": request.form.get("title","").strip(),
            "slug": request.form.get("slug","").strip(),
            "excerpt": request.form.get("excerpt","").strip(),
            "content": request.form.get("content","").strip(),
            "image_url": request.form.get("image_url","").strip(),
        }
        create_post(data)
        flash("Post creado.", "success")
        return redirect(url_for("admin.dashboard"))
    return render_template("admin/post_form.html", item=None)

@admin_bp.route("/posts/<slug>/edit", methods=["GET","POST"])
def post_edit(slug):
    if not _require_admin(): return redirect(url_for("auth.login"))
    item = get_post_by_slug(slug)
    if not item:
        flash("Post no encontrado.", "error")
        return redirect(url_for("admin.dashboard"))
    if request.method == "POST":
        data = {
            "title": request.form.get("title","").strip(),
            "slug": request.form.get("slug","").strip(),
            "excerpt": request.form.get("excerpt","").strip(),
            "content": request.form.get("content","").strip(),
            "image_url": request.form.get("image_url","").strip(),
        }
        update_post(item["id"], data)
        flash("Post actualizado.", "success")
        return redirect(url_for("admin.dashboard"))
    return render_template("admin/post_form.html", item=item)

@admin_bp.route("/posts/<slug>/delete", methods=["POST"])
def post_delete(slug):
    if not _require_admin(): return redirect(url_for("auth.login"))
    item = get_post_by_slug(slug)
    if item:
        delete_post(item["id"])
        flash("Post eliminado.", "success")
    return redirect(url_for("admin.dashboard"))
