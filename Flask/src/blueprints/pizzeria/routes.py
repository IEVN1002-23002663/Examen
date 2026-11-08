from flask import Blueprint, jsonify, request
from database import mysql
from datetime import date
from decimal import Decimal, InvalidOperation

pizzeria_bp = Blueprint("pizzeria", __name__, url_prefix="/api")


def respuesta_error(mensaje, codigo=400):
    return jsonify({"mensaje": mensaje, "exito": False}), codigo


def obtener_json():
    datos = request.get_json(silent=True)
    return datos if isinstance(datos, dict) else None


def numero_decimal(valor, campo):
    try:
        numero = Decimal(str(valor))
        if not numero.is_finite() or numero < 0:
            raise ValueError
        return numero
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError(f"El campo {campo} debe ser un número válido mayor o igual a cero")


def fila_cliente(fila):
    return {
        "idcliente": fila[0],
        "nombre": fila[1],
        "direccion": fila[2],
        "telefono": fila[3]
    }


# Precios acordados con el formulario de Angular.
PRECIOS = {"chica": Decimal("40"), "mediana": Decimal("80"), "grande": Decimal("120")}
INGREDIENTES = {"jamon": "Jamon", "pina": "Pina", "piña": "Pina",
                "champinones": "Champinones", "champiñones": "Champinones"}


def normalizar_fecha(valor):
    if valor is None or valor == "":
        return date.today().isoformat()
    try:
        return date.fromisoformat(str(valor)).isoformat()
    except ValueError:
        raise ValueError("La fecha debe tener formato AAAA-MM-DD")


def preparar_pizzas(pizzas):
    """Valida y calcula montos en Flask; nunca confía en subtotales del cliente."""
    if not isinstance(pizzas, list) or not pizzas:
        raise ValueError("Agrega al menos una pizza")

    total = Decimal("0")
    detalles = []
    for pizza in pizzas:
        if not isinstance(pizza, dict):
            raise ValueError("Cada pizza debe ser un objeto")
        tamano = str(pizza.get("tamano") or "").strip().lower()
        if tamano not in PRECIOS:
            raise ValueError("Tamaño inválido. Usa Chica, Mediana o Grande")
        cantidad = pizza.get("cantidad")
        if isinstance(cantidad, bool) or not isinstance(cantidad, int) or cantidad < 1:
            raise ValueError("La cantidad de pizzas debe ser un entero mayor o igual a 1")
        ingredientes = pizza.get("ingredientes", [])
        if isinstance(ingredientes, str):
            ingredientes = [x.strip() for x in ingredientes.split(",") if x.strip()]
        if not isinstance(ingredientes, list):
            raise ValueError("Los ingredientes deben ser una lista")

        extras = []
        for ingrediente in ingredientes:
            nombre = str(ingrediente).strip().lower()
            if nombre not in INGREDIENTES:
                raise ValueError(f"Ingrediente inválido: {ingrediente}")
            normalizado = INGREDIENTES[nombre]
            if normalizado in extras:
                raise ValueError("No repitas ingredientes en la misma pizza")
            extras.append(normalizado)

        subtotal = (PRECIOS[tamano] + Decimal("10") * len(extras)) * cantidad
        total += subtotal
        detalles.append((tamano.capitalize(), ", ".join(extras), cantidad, subtotal))
    return detalles, total


# ---------------- CLIENTES: GET ----------------
@pizzeria_bp.route("/clientes", methods=["GET"])
def lista_clientes():
    cursor = None
    con = None
    try:
        con = mysql.connection
        cursor = con.cursor()
        cursor.execute("""
            SELECT idcliente, nombre, direccion, telefono
            FROM clientes
            ORDER BY idcliente DESC
        """)
        clientes = [fila_cliente(f) for f in cursor.fetchall()]
        return jsonify({"clientes": clientes, "exito": True})
    except Exception as ex:
        return respuesta_error(str(ex), 500)
    finally:
        if cursor:
            cursor.close()


# ---------------- CLIENTES: GET POR ID ----------------
@pizzeria_bp.route("/clientes/<int:idcliente>", methods=["GET"])
def obtener_cliente(idcliente):
    cursor = None
    con = None
    try:
        con = mysql.connection
        cursor = con.cursor()
        cursor.execute("""
            SELECT idcliente, nombre, direccion, telefono
            FROM clientes WHERE idcliente = %s
        """, (idcliente,))
        fila = cursor.fetchone()
        if not fila:
            return respuesta_error("Cliente no encontrado", 404)
        return jsonify({"cliente": fila_cliente(fila), "exito": True})
    except Exception as ex:
        return respuesta_error(str(ex), 500)
    finally:
        if cursor:
            cursor.close()


# ---------------- CLIENTES: POST ----------------
@pizzeria_bp.route("/clientes", methods=["POST"])
def registrar_cliente():
    datos = obtener_json()
    if datos is None:
        return respuesta_error("Envía los datos del cliente en formato JSON")

    nombre = str(datos.get("nombre") or "").strip()
    direccion = str(datos.get("direccion") or "").strip()
    telefono = str(datos.get("telefono") or "").strip()

    if not nombre or not direccion or not telefono:
        return respuesta_error("Nombre, dirección y teléfono son obligatorios")

    cursor = None
    con = None
    try:
        con = mysql.connection
        cursor = con.cursor()
        cursor.execute("""
            INSERT INTO clientes (nombre, direccion, telefono)
            VALUES (%s, %s, %s)
        """, (nombre, direccion, telefono))
        con.commit()
        nuevo_id = cursor.lastrowid
        return jsonify({
            "mensaje": "Cliente registrado correctamente",
            "idcliente": nuevo_id,
            "exito": True
        }), 201
    except Exception as ex:
        if con is not None:
            con.rollback()
        return respuesta_error(str(ex), 500)
    finally:
        if cursor:
            cursor.close()


# ---------------- CLIENTES: PUT ----------------
@pizzeria_bp.route("/clientes/<int:idcliente>", methods=["PUT"])
def actualizar_cliente(idcliente):
    datos = obtener_json()
    if datos is None:
        return respuesta_error("Envía los datos del cliente en formato JSON")

    nombre = str(datos.get("nombre") or "").strip()
    direccion = str(datos.get("direccion") or "").strip()
    telefono = str(datos.get("telefono") or "").strip()
    if not nombre or not direccion or not telefono:
        return respuesta_error("Nombre, dirección y teléfono son obligatorios")

    cursor = None
    con = None
    try:
        con = mysql.connection
        cursor = con.cursor()
        cursor.execute("""
            UPDATE clientes
            SET nombre = %s, direccion = %s, telefono = %s
            WHERE idcliente = %s
        """, (nombre, direccion, telefono, idcliente))
        if cursor.rowcount == 0:
            cursor.execute("SELECT idcliente FROM clientes WHERE idcliente = %s", (idcliente,))
            if not cursor.fetchone():
                return respuesta_error("Cliente no encontrado", 404)
        con.commit()
        return jsonify({"mensaje": "Cliente actualizado correctamente", "exito": True})
    except Exception as ex:
        if con is not None:
            con.rollback()
        return respuesta_error(str(ex), 500)
    finally:
        if cursor:
            cursor.close()


# ---------------- CLIENTES: DELETE ----------------
@pizzeria_bp.route("/clientes/<int:idcliente>", methods=["DELETE"])
def eliminar_cliente(idcliente):
    cursor = None
    con = None
    try:
        con = mysql.connection
        cursor = con.cursor()
        cursor.execute("SELECT idcliente FROM clientes WHERE idcliente = %s", (idcliente,))
        if not cursor.fetchone():
            return respuesta_error("Cliente no encontrado", 404)

        cursor.execute("SELECT idpedido FROM pedidos WHERE idcliente = %s LIMIT 1", (idcliente,))
        if cursor.fetchone():
            return respuesta_error(
                "No se puede eliminar el cliente porque tiene pedidos registrados",
                409
            )

        cursor.execute("DELETE FROM clientes WHERE idcliente = %s", (idcliente,))
        con.commit()
        return jsonify({"mensaje": "Cliente eliminado correctamente", "exito": True})
    except Exception as ex:
        if con is not None:
            con.rollback()
        return respuesta_error(str(ex), 500)
    finally:
        if cursor:
            cursor.close()


# ---------------- PEDIDOS: GET TODOS ----------------
@pizzeria_bp.route("/pedidos", methods=["GET"])
def lista_pedidos():
    cursor = None
    con = None
    try:
        con = mysql.connection
        cursor = con.cursor()
        cursor.execute("""
            SELECT p.idpedido, p.idcliente, c.nombre, c.direccion,
                   c.telefono, p.fecha, p.total
            FROM pedidos p
            INNER JOIN clientes c ON p.idcliente = c.idcliente
            ORDER BY p.idpedido DESC
        """)
        pedidos = []
        for f in cursor.fetchall():
            pedidos.append({
                "idpedido": f[0],
                "idcliente": f[1],
                "nombre": f[2],
                "direccion": f[3],
                "telefono": f[4],
                "fecha": str(f[5]),
                "total": float(f[6])
            })
        return jsonify({"pedidos": pedidos, "exito": True})
    except Exception as ex:
        return respuesta_error(str(ex), 500)
    finally:
        if cursor:
            cursor.close()


# ---------------- PEDIDOS: POST ----------------
@pizzeria_bp.route("/pedidos", methods=["POST"])
def registrar_pedido():
    datos = obtener_json()
    if datos is None:
        return respuesta_error("Debes enviar un objeto JSON con los datos del pedido")
    try:
        detalles, total = preparar_pizzas(datos.get("pizzas"))
        fecha = normalizar_fecha(datos.get("fecha"))
    except (ValueError, TypeError) as ex:
        return respuesta_error(str(ex))

    cursor = None
    con = None
    try:
        con = mysql.connection
        cursor = con.cursor()
        idcliente = datos.get("idcliente")
        if idcliente is not None:
            cursor.execute("SELECT idcliente FROM clientes WHERE idcliente = %s", (idcliente,))
            if not cursor.fetchone():
                return respuesta_error("El cliente seleccionado no existe", 404)
        else:
            nombre = str(datos.get("nombre") or "").strip()
            direccion = str(datos.get("direccion") or "").strip()
            telefono = str(datos.get("telefono") or "").strip()
            if not nombre or not direccion or not telefono:
                return respuesta_error("Faltan nombre, dirección o teléfono del cliente")
            cursor.execute("""
                INSERT INTO clientes (nombre, direccion, telefono)
                VALUES (%s, %s, %s)
            """, (nombre, direccion, telefono))
            idcliente = cursor.lastrowid

        cursor.execute("""
            INSERT INTO pedidos (idcliente, fecha, total)
            VALUES (%s, %s, %s)
        """, (idcliente, fecha, total))
        idpedido = cursor.lastrowid

        for tamano, ingredientes, cantidad, subtotal in detalles:
            cursor.execute("""
                INSERT INTO detalle_pedido
                (idpedido, tamano, ingredientes, cantidad, subtotal)
                VALUES (%s, %s, %s, %s, %s)
            """, (idpedido, tamano, ingredientes, cantidad, subtotal))
        con.commit()
        return jsonify({
            "mensaje": "Pedido registrado correctamente",
            "idpedido": idpedido,
            "idcliente": idcliente,
            "total": float(total),
            "exito": True
        }), 201
    except Exception as ex:
        if con is not None:
            con.rollback()
        return respuesta_error(str(ex), 500)
    finally:
        if cursor is not None:
            cursor.close()


# ---------------- PEDIDOS: GET POR ID Y DETALLE ----------------
@pizzeria_bp.route("/pedidos/<int:idpedido>", methods=["GET"])
def detalle_pedido(idpedido):
    cursor = None
    con = None
    try:
        con = mysql.connection
        cursor = con.cursor()
        cursor.execute("""
            SELECT p.idpedido, p.idcliente, c.nombre, c.direccion,
                   c.telefono, p.fecha, p.total
            FROM pedidos p
            INNER JOIN clientes c ON p.idcliente = c.idcliente
            WHERE p.idpedido = %s
        """, (idpedido,))
        pedido = cursor.fetchone()
        if not pedido:
            return respuesta_error("Pedido no encontrado", 404)

        cursor.execute("""
            SELECT iddetalle, tamano, ingredientes, cantidad, subtotal
            FROM detalle_pedido
            WHERE idpedido = %s
            ORDER BY iddetalle
        """, (idpedido,))
        filas = cursor.fetchall()
        pizzas = [{
            "iddetalle": f[0],
            "tamano": f[1],
            "ingredientes": f[2],
            "cantidad": f[3],
            "subtotal": float(f[4])
        } for f in filas]

        return jsonify({
            "pedido": {
                "idpedido": pedido[0],
                "idcliente": pedido[1],
                "nombre": pedido[2],
                "direccion": pedido[3],
                "telefono": pedido[4],
                "fecha": str(pedido[5]),
                "total": float(pedido[6]),
                "pizzas": pizzas
            },
            "exito": True
        })
    except Exception as ex:
        return respuesta_error(str(ex), 500)
    finally:
        if cursor:
            cursor.close()


# ---------------- PEDIDOS: PUT ----------------
@pizzeria_bp.route("/pedidos/<int:idpedido>", methods=["PUT"])
def actualizar_pedido(idpedido):
    datos = obtener_json()
    if datos is None:
        return respuesta_error("Envía los datos del pedido en formato JSON")
    try:
        detalles, total = (preparar_pizzas(datos["pizzas"])
                           if "pizzas" in datos else (None, None))
        fecha = normalizar_fecha(datos["fecha"]) if "fecha" in datos else None
    except (ValueError, TypeError) as ex:
        return respuesta_error(str(ex))

    cursor = None
    con = None
    try:
        con = mysql.connection
        cursor = con.cursor()
        cursor.execute("SELECT idcliente, total FROM pedidos WHERE idpedido = %s", (idpedido,))
        existente = cursor.fetchone()
        if not existente:
            return respuesta_error("Pedido no encontrado", 404)
        idcliente = datos.get("idcliente", existente[0])
        cursor.execute("SELECT nombre, direccion, telefono FROM clientes WHERE idcliente = %s", (idcliente,))
        cliente = cursor.fetchone()
        if not cliente:
            return respuesta_error("Cliente no encontrado", 404)
        if any(k in datos for k in ("nombre", "direccion", "telefono")):
            nombre = str(datos.get("nombre", cliente[0]) or "").strip()
            direccion = str(datos.get("direccion", cliente[1]) or "").strip()
            telefono = str(datos.get("telefono", cliente[2]) or "").strip()
            if not nombre or not direccion or not telefono:
                return respuesta_error("Nombre, dirección y teléfono son obligatorios")
            cursor.execute("""
                UPDATE clientes SET nombre=%s, direccion=%s, telefono=%s
                WHERE idcliente=%s
            """, (nombre, direccion, telefono, idcliente))

        if detalles is not None:
            cursor.execute("DELETE FROM detalle_pedido WHERE idpedido = %s", (idpedido,))
            for tamano, ingredientes, cantidad, subtotal in detalles:
                cursor.execute("""
                    INSERT INTO detalle_pedido
                    (idpedido, tamano, ingredientes, cantidad, subtotal)
                    VALUES (%s, %s, %s, %s, %s)
                """, (idpedido, tamano, ingredientes, cantidad, subtotal))
        else:
            total = existente[1]

        cursor.execute("""
            UPDATE pedidos
            SET idcliente=%s, fecha=COALESCE(%s, fecha), total=%s
            WHERE idpedido=%s
        """, (idcliente, fecha, total, idpedido))
        con.commit()
        return jsonify({"mensaje": "Pedido actualizado correctamente", "exito": True})
    except Exception as ex:
        if con is not None:
            con.rollback()
        return respuesta_error(str(ex), 500)
    finally:
        if cursor is not None:
            cursor.close()


# ---------------- PEDIDOS: DELETE ----------------
@pizzeria_bp.route("/pedidos/<int:idpedido>", methods=["DELETE"])
def eliminar_pedido(idpedido):
    cursor = None
    con = None
    try:
        con = mysql.connection
        cursor = con.cursor()
        cursor.execute("SELECT idpedido FROM pedidos WHERE idpedido = %s", (idpedido,))
        if not cursor.fetchone():
            return respuesta_error("Pedido no encontrado", 404)

        cursor.execute("DELETE FROM detalle_pedido WHERE idpedido = %s", (idpedido,))
        cursor.execute("DELETE FROM pedidos WHERE idpedido = %s", (idpedido,))
        con.commit()
        return jsonify({"mensaje": "Pedido eliminado correctamente", "exito": True})
    except Exception as ex:
        if con is not None:
            con.rollback()
        return respuesta_error(str(ex), 500)
    finally:
        if cursor:
            cursor.close()


# ---------------- REPORTES DE VENTAS ----------------
@pizzeria_bp.route("/ventas/dia/<dia>", methods=["GET"])
def ventas_dia(dia):
    dias = {"domingo": 1, "lunes": 2, "martes": 3, "miercoles": 4,
            "miércoles": 4, "jueves": 5, "viernes": 6, "sabado": 7, "sábado": 7}
    dia = dia.lower()
    if dia not in dias:
        return respuesta_error("Día inválido", 400)

    cursor = None
    con = None
    try:
        con = mysql.connection
        cursor = con.cursor()
        cursor.execute("""
            SELECT p.idpedido, c.nombre, p.fecha, p.total
            FROM pedidos p
            INNER JOIN clientes c ON p.idcliente = c.idcliente
            WHERE DAYOFWEEK(p.fecha) = %s
            ORDER BY p.fecha DESC
        """, (dias[dia],))
        ventas = [{"idpedido": f[0], "nombre": f[1],
                   "fecha": str(f[2]), "total": float(f[3])}
                  for f in cursor.fetchall()]
        return jsonify({"ventas": ventas, "total": sum(v["total"] for v in ventas), "exito": True})
    except Exception as ex:
        return respuesta_error(str(ex), 500)
    finally:
        if cursor:
            cursor.close()


@pizzeria_bp.route("/ventas/mes/<mes>", methods=["GET"])
def ventas_mes(mes):
    meses = {"enero": 1, "febrero": 2, "marzo": 3, "abril": 4,
             "mayo": 5, "junio": 6, "julio": 7, "agosto": 8,
             "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12}
    mes = mes.lower()
    if mes not in meses:
        return respuesta_error("Mes inválido", 400)

    cursor = None
    con = None
    try:
        con = mysql.connection
        cursor = con.cursor()
        cursor.execute("""
            SELECT p.idpedido, c.nombre, p.fecha, p.total
            FROM pedidos p
            INNER JOIN clientes c ON p.idcliente = c.idcliente
            WHERE MONTH(p.fecha) = %s
            ORDER BY p.fecha DESC
        """, (meses[mes],))
        ventas = [{"idpedido": f[0], "nombre": f[1],
                   "fecha": str(f[2]), "total": float(f[3])}
                  for f in cursor.fetchall()]
        return jsonify({"ventas": ventas, "total": sum(v["total"] for v in ventas), "exito": True})
    except Exception as ex:
        return respuesta_error(str(ex), 500)
    finally:
        if cursor:
            cursor.close()
