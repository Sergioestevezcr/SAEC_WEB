"""
models/db.py — Capa de datos con SQL plano y helpers.
Incluye:
- Conexión MySQL/SQLite
- Tablas: users, contacts, projects, blog_posts
- CRUD de projects
- Consultas de blog
Todos los SQL están comentados para facilitar auditoría.
"""
import os, contextlib, pymysql, sqlite3, smtplib, ssl, requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from werkzeug.security import generate_password_hash

_conn_settings = {}

def init_db(app):
    _conn_settings["uri"] = app.config["DB_URI"]
    _conn_settings["mail"] = {
        "server": os.getenv("MAIL_SERVER",""),
        "port": int(os.getenv("MAIL_PORT","0") or 0),
        "use_tls": os.getenv("MAIL_USE_TLS","1") == "1",
        "username": os.getenv("MAIL_USERNAME",""),
        "password": os.getenv("MAIL_PASSWORD",""),
        "to": os.getenv("MAIL_TO","")
    }
    _conn_settings["recaptcha_secret"] = os.getenv("RECAPTCHA_SECRET_KEY","")

def _is_mysql():
    return _conn_settings["uri"].startswith("mysql")

def get_connection():
    """Crea una conexión bajo demanda por request."""
    uri = _conn_settings["uri"]
    if _is_mysql():
        # mysql+pymysql://user:pass@host:port/db
        creds, host_db = uri.split("://",1)[1].split("@",1)
        user, password = creds.split(":",1)
        hp, db = host_db.split("/",1)
        host, port = (hp.split(":")+["3306"])[:2]
        return pymysql.connect(host=host, user=user, password=password, database=db, port=int(port),
                               cursorclass=pymysql.cursors.DictCursor, autocommit=True)
    else:
        path = uri.replace("sqlite:///", "")
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        return conn

@contextlib.contextmanager
def db_cursor():
    conn = get_connection()
    try:
        cur = conn.cursor()
        yield cur
        conn.commit()
    finally:
        conn.close()

def create_tables_if_not_exist():
    """Crea tablas si no existen (id autoincrement en ambos motores)."""
    with db_cursor() as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTO_INCREMENT
                """ + ("" if _is_mysql() else " /*SQLite*/") + r""",
            email VARCHAR(190) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            role VARCHAR(50) NOT NULL DEFAULT 'admin',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTO_INCREMENT
                """ + ("" if _is_mysql() else " /*SQLite*/") + r""",
            name VARCHAR(150) NOT NULL,
            email VARCHAR(190) NOT NULL,
            phone VARCHAR(50),
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTO_INCREMENT
                """ + ("" if _is_mysql() else " /*SQLite*/") + r""",
            title VARCHAR(200) NOT NULL,
            description TEXT NOT NULL,
            image_url VARCHAR(300),
            repo_url VARCHAR(300),
            live_url VARCHAR(300),
            is_open_source TINYINT NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS blog_posts (
            id INTEGER PRIMARY KEY AUTO_INCREMENT
                """ + ("" if _is_mysql() else " /*SQLite*/") + r""",
            title VARCHAR(220) NOT NULL,
            slug VARCHAR(240) UNIQUE NOT NULL,
            excerpt VARCHAR(300),
            content TEXT NOT NULL,
            image_url VARCHAR(300),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
    # Admin por defecto
    with db_cursor() as cur:
        q = "SELECT COUNT(*) as c FROM users"
        cur.execute(q)
        row = cur.fetchone()
        c = row["c"] if isinstance(row, dict) else list(row)[0]
    if c == 0:
        with db_cursor() as cur:
            sql = "INSERT INTO users (email, password_hash, role) VALUES (%s,%s,%s)" if _is_mysql() else \
                  "INSERT INTO users (email, password_hash, role) VALUES (?,?,?)"
            cur.execute(sql, ("admin@saec.com", generate_password_hash("Admin123!"), "admin"))

# === CONTACTS ===
def query_all_contacts():
    with db_cursor() as cur:
        cur.execute("SELECT * FROM contacts ORDER BY created_at DESC")
        return [dict(r) for r in cur.fetchall()]

def insert_contact(name, email, phone, message):
    with db_cursor() as cur:
        sql = "INSERT INTO contacts (name,email,phone,message) VALUES (%s,%s,%s,%s)" if _is_mysql() else \
              "INSERT INTO contacts (name,email,phone,message) VALUES (?,?,?,?)"
        cur.execute(sql, (name, email, phone, message))

# === USERS ===
def get_user_by_email(email):
    with db_cursor() as cur:
        sql = "SELECT * FROM users WHERE email=%s" if _is_mysql() else "SELECT * FROM users WHERE email=?"
        cur.execute(sql, (email,))
        row = cur.fetchone()
        return dict(row) if row else None

# === PROJECTS CRUD ===
def get_projects(open_source=None):
    with db_cursor() as cur:
        if open_source is None:
            cur.execute("SELECT * FROM projects ORDER BY created_at DESC")
        else:
            sql = "SELECT * FROM projects WHERE is_open_source=%s ORDER BY created_at DESC" if _is_mysql() else \
                  "SELECT * FROM projects WHERE is_open_source=? ORDER BY created_at DESC"
            cur.execute(sql, (1 if open_source else 0,))
        return [dict(r) for r in cur.fetchall()]

def get_project(id):
    with db_cursor() as cur:
        sql = "SELECT * FROM projects WHERE id=%s" if _is_mysql() else "SELECT * FROM projects WHERE id=?"
        cur.execute(sql, (id,))
        r = cur.fetchone()
        return dict(r) if r else None

def create_project(data):
    with db_cursor() as cur:
        sql = """INSERT INTO projects (title,description,image_url,repo_url,live_url,is_open_source)
                 VALUES ({},{},{},{},{},{})""".format(*(["%s"]*6) if _is_mysql() else ["?"]*6)
        cur.execute(sql, (data["title"], data["description"], data.get("image_url"), data.get("repo_url"),
                          data.get("live_url"), 1 if str(data.get("is_open_source","1")) in ("1","true","True") else 0))

def update_project(id, data):
    with db_cursor() as cur:
        sql = """UPDATE projects SET title={}, description={}, image_url={}, repo_url={}, live_url={}, is_open_source={}
                 WHERE id={}""".format(*(["%s"]*7) if _is_mysql() else ["?"]*7)
        cur.execute(sql, (data["title"], data["description"], data.get("image_url"), data.get("repo_url"),
                          data.get("live_url"), 1 if str(data.get("is_open_source","1")) in ("1","true","True") else 0, id))

def delete_project(id):
    with db_cursor() as cur:
        sql = "DELETE FROM projects WHERE id=%s" if _is_mysql() else "DELETE FROM projects WHERE id=?"
        cur.execute(sql, (id,))

# === BLOG ===
def get_posts():
    with db_cursor() as cur:
        cur.execute("SELECT * FROM blog_posts ORDER BY created_at DESC")
        return [dict(r) for r in cur.fetchall()]

def get_post_by_slug(slug):
    with db_cursor() as cur:
        sql = "SELECT * FROM blog_posts WHERE slug=%s" if _is_mysql() else "SELECT * FROM blog_posts WHERE slug=?"
        cur.execute(sql, (slug,))
        r = cur.fetchone()
        return dict(r) if r else None

def create_post(data):
    with db_cursor() as cur:
        sql = """INSERT INTO blog_posts (title,slug,excerpt,content,image_url)
                 VALUES ({},{},{},{},{})""".format(*(["%s"]*5) if _is_mysql() else ["?"]*5)
        cur.execute(sql, (data["title"], data["slug"], data.get("excerpt"), data["content"], data.get("image_url")))

def update_post(id, data):
    with db_cursor() as cur:
        sql = """UPDATE blog_posts SET title={}, slug={}, excerpt={}, content={}, image_url={} WHERE id={}""".format(*(["%s"]*6) if _is_mysql() else ["?"]*6)
        cur.execute(sql, (data["title"], data["slug"], data.get("excerpt"), data["content"], data.get("image_url"), id))

def delete_post(id):
    with db_cursor() as cur:
        sql = "DELETE FROM blog_posts WHERE id=%s" if _is_mysql() else "DELETE FROM blog_posts WHERE id=?"
        cur.execute(sql, (id,))

# === Notificaciones por email ===
def send_contact_email(payload):
    """Envía email con SMTP simple usando datos de .env. Silencioso si faltan credenciales."""
    m = _conn_settings.get("mail", {})
    if not (m.get("server") and m.get("username") and m.get("password") and m.get("to")):
        return False
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Nuevo contacto SAEC: {payload.get('name')}"
    msg["From"] = m["username"]
    msg["To"] = m["to"]
    html = f"""
    <h2>Nuevo contacto</h2>
    <ul>
      <li><b>Nombre:</b> {payload.get('name')}</li>
      <li><b>Email:</b> {payload.get('email')}</li>
      <li><b>Teléfono:</b> {payload.get('phone')}</li>
    </ul>
    <p>{payload.get('message')}</p>
    """
    msg.attach(MIMEText(html, "html"))
    context = ssl.create_default_context()
    with smtplib.SMTP(m["server"], m["port"]) as server:
        if m["use_tls"]:
            server.starttls(context=context)
        server.login(m["username"], m["password"])
        server.sendmail(m["username"], [m["to"]], msg.as_string())
    return True

# === reCAPTCHA verify ===
def verify_recaptcha(token):
    secret = _conn_settings.get("recaptcha_secret")
    if not secret or not token:
        return False
    try:
        r = requests.post("https://www.google.com/recaptcha/api/siteverify",
                          data={"secret": secret, "response": token}, timeout=5)
        data = r.json()
        return bool(data.get("success"))
    except Exception:
        return False
