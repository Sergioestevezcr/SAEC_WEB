"""
app.py — Punto de entrada de la aplicación Flask.
- Carga configuración.
- Inicializa conexión a BD.
- Registra controladores (Blueprints) siguiendo MVC.
- Expone comandos útiles (crear tablas y admin).
"""
from flask import Flask
from dotenv import load_dotenv
import os

# Modelos / DB
from models.db import init_db, create_tables_if_not_exist

# Controladores
from controllers.main_controller import main_bp
from controllers.auth_controller import auth_bp
from controllers.admin_controller import admin_bp

def create_app():
    """Factory de Flask para facilitar pruebas/despliegue."""
    load_dotenv()  # Carga variables de entorno desde .env si existe (dev)
    app = Flask(__name__, instance_relative_config=True)
    # Configuración básica y SECRET_KEY para sesiones
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-me")

    # Configuración de BD: si hay MYSQL_URL, úsala; si no, SQLite en instance/
    mysql_url = os.getenv("MYSQL_URL")
    sqlite_path = os.getenv("SQLITE_PATH", "instance/saec.sqlite3")
    if mysql_url:
        app.config["DB_URI"] = mysql_url
    else:
        # Garantiza carpeta instance/ para SQLite
        os.makedirs(os.path.dirname(sqlite_path), exist_ok=True)
        app.config["DB_URI"] = f"sqlite:///{sqlite_path}"

    # Inicializa pool/conexión global
    init_db(app)

    # Registra Blueprints (rutas)
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")

    # Crea tablas si no existen (ambiente dev)
    with app.app_context():
        create_tables_if_not_exist()

    return app

# Permite correr con: python app.py
if __name__ == "__main__":
    app = create_app()
    # En producción usa Gunicorn / uWSGI. En dev, ejecuta el built-in.
    app.run(host="0.0.0.0", port=5001)
