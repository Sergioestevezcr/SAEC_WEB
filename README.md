# SAEC — Sitio corporativo (Flask MVC)

## Estructura
```
saec_site/
  app.py
  controllers/
  models/
  templates/
  static/
  schema.sql
  requirements.txt
  .env.example
```
## Setup rápido (dev)
1) Crea y activa venv
```
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # y edita credenciales
```
2) Ejecuta
```
python app.py
```
3) Admin por defecto:
- email: admin@saec.com
- password: Admin123!

## Producción
- Usa `MYSQL_URL` para tu servidor MySQL (RDS/Aurora/PlanetScale/etc.).
- Ejecuta con Gunicorn: `gunicorn -w 2 -b 0.0.0.0:8000 app:create_app()`
- Configura Nginx para servir `/static/` con cache y gzip.
- Añade HTTPS y HTTP/2. Genera sitemap.xml y robots.txt (puedes servirlos como estáticos).

