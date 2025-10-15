from app import create_app  # Importa la factory de la aplicación Flask

# Crea una instancia de la app
app = create_app()

if __name__ == "__main__":
    # Ejecuta el servidor local en modo desarrollo
    # host='0.0.0.0' permite acceso externo (ideal para Docker o Railway)
    # debug=True recarga automáticamente los cambios
    app.run(host="0.0.0.0", port=5001, debug=True)
