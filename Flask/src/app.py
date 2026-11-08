from flask import Flask, jsonify
from flask_cors import CORS

from config import config
from database import mysql
from blueprints.pizzeria.routes import pizzeria_bp

app = Flask(__name__)
app.config.from_object(config["development"])

# Importante: SIN init_app, Flask-MySQLdb genera KeyError 'MYSQL_UNIX_SOCKET'.
mysql.init_app(app)
CORS(app, resources={r"/api/*": {"origins": "*"}})
app.register_blueprint(pizzeria_bp)


@app.route("/", methods=["GET"])
def inicio():
    return jsonify({"exito": True, "mensaje": "API de Pizzeria funcionando"})


@app.route("/test-db", methods=["GET"])
def test_db():
    cursor = None
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT DATABASE()")
        fila = cursor.fetchone()
        return jsonify({
            "exito": True,
            "mensaje": "Conexión a MySQL exitosa",
            "base_datos": fila[0] if fila else None
        })
    except Exception as error:
        return jsonify({"exito": False, "mensaje": str(error)}), 500
    finally:
        if cursor is not None:
            cursor.close()


if __name__ == "__main__":
    # Esta impresión permite comprobar qué archivo se está ejecutando.
    print("ARCHIVO APP:", __file__, flush=True)
    print("MYSQL_CONFIGURADO:", "MYSQL_UNIX_SOCKET" in app.config, flush=True)
    print("RUTAS REGISTRADAS:", app.url_map, flush=True)
    # Sin segundo proceso de autorecarga: facilita detectar copias antiguas.
    app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=False)
