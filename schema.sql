-- Crea base de datos y tablas (MySQL). Para SQLite ignora CREATE DATABASE.
-- CREATE DATABASE IF NOT EXISTS saec_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
-- USE saec_db;

CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  email VARCHAR(190) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  role VARCHAR(50) NOT NULL DEFAULT 'admin',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS contacts (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(150) NOT NULL,
  email VARCHAR(190) NOT NULL,
  phone VARCHAR(50),
  message TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS projects (
  id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(200) NOT NULL,
  description TEXT NOT NULL,
  image_url VARCHAR(300),
  repo_url VARCHAR(300),
  live_url VARCHAR(300),
  is_open_source TINYINT NOT NULL DEFAULT 1,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Admin por defecto (password: Admin123!)
INSERT INTO users (email, password_hash, role) VALUES
('admin@saec.com', '$pbkdf2-sha256$29000$example$hash.cambia.usando.script', 'admin');
-- Nota: Reemplaza por hash real generado por Werkzeug o crea tu propio admin desde app.
