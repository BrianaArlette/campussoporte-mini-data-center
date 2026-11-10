"""API CampusSoporte: incidencias CRUD, estadisticas y pruebas de infraestructura.

Solo para laboratorio local. Sin autenticación de usuarios: no publicar en Internet.
"""
import json
import os
import re
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit, parse_qs

import pymysql

DB = {
    "host": os.getenv("DB_HOST", "db"),
    "user": os.getenv("DB_USER", "app_user"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "dc_app"),
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
    "connect_timeout": 4,
    "read_timeout": 5,
    "write_timeout": 5,
    "autocommit": True,
}
CATEGORIAS = {"Internet", "Computadora", "Proyector", "Plataforma", "Otro"}
PRIORIDADES = {"Baja", "Media", "Alta"}
ESTADOS = {"Pendiente", "En proceso", "Resuelto"}
NODOS = {"web1", "web2", "web3"}
MAX_BODY = 16 * 1024
RUTA_ID = re.compile(r"^/api/incidencias/([1-9][0-9]{0,12})$")


def ejecutar(sql, params=(), *, one=False):
    con = pymysql.connect(**DB)
    try:
        with con.cursor() as cur:
            cur.execute(sql, params)
            if sql.lstrip().upper().startswith("SELECT"):
                return cur.fetchone() if one else cur.fetchall()
            return cur.rowcount, cur.lastrowid
    finally:
        con.close()


def texto(data, campo, limite, requerido=True):
    v = data.get(campo, "")
    if not isinstance(v, str):
        raise ValueError(f"{campo}: se requiere texto")
    v = v.strip()
    if requerido and not v:
        raise ValueError(f"{campo}: no puede estar vacío")
    if len(v) > limite:
        raise ValueError(f"{campo}: máximo {limite} caracteres")
    return v


def validar_incidencia(data, parcial=False):
    if not isinstance(data, dict):
        raise ValueError("Debes enviar un objeto JSON")
    campos = {"titulo": 100, "descripcion": 700, "ubicacion": 100}
    permitidos = set(campos) | {"categoria", "prioridad", "estado"}
    if not set(data).issubset(permitidos):
        raise ValueError("Se enviaron campos no permitidos")
    obligatorio = {"titulo", "descripcion", "ubicacion", "categoria"}
    if not parcial and not obligatorio.issubset(data):
        raise ValueError("Faltan título, descripción, ubicación o categoría")
    if parcial and not data:
        raise ValueError("No se enviaron campos para modificar")
    salida = {k: texto(data, k, limit) for k, limit in campos.items() if k in data}
    for campo, opciones in (("categoria", CATEGORIAS), ("prioridad", PRIORIDADES), ("estado", ESTADOS)):
        if campo in data:
            if not isinstance(data[campo], str) or data[campo] not in opciones:
                raise ValueError(f"{campo}: valor inválido")
            salida[campo] = data[campo]
    if not parcial:
        salida.setdefault("estado", "Pendiente")
        salida.setdefault("prioridad", "Media")
    return salida


class Api(BaseHTTPRequestHandler):
    server_version = "CampusSoporte/1.0"
    sys_version = ""

    def log_message(self, format, *args):
        print(json.dumps({"servicio": "api", "mensaje": format % args}, ensure_ascii=False), flush=True)

    def json_out(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def json_in(self):
        try:
            size = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            raise ValueError("Content-Length inválido")
        if not 0 < size <= MAX_BODY:
            raise ValueError("El cuerpo debe tener entre 1 y 16384 bytes")
        try:
            value = json.loads(self.rfile.read(size))
        except (ValueError, UnicodeDecodeError):
            raise ValueError("JSON inválido")
        if not isinstance(value, dict):
            raise ValueError("Se requiere un objeto JSON")
        return value

    def dispatch(self, metodo):
        inicio = time.perf_counter()
        try:
            self.route(metodo)
        except ValueError as exc:
            self.json_out(400, {"error": str(exc)})
        except pymysql.MySQLError:
            self.json_out(503, {"error": "No fue posible consultar la base de datos"})
        except Exception as exc:
            print(json.dumps({"servicio": "api", "nivel": "error", "tipo": type(exc).__name__}), flush=True)
            self.json_out(500, {"error": "Error interno del servidor"})
        finally:
            print(json.dumps({"servicio": "api", "metodo": metodo,
                              "ruta": urlsplit(self.path).path,
                              "ms": round((time.perf_counter()-inicio)*1000, 2)}), flush=True)

    def do_GET(self): self.dispatch("GET")
    def do_POST(self): self.dispatch("POST")
    def do_PATCH(self): self.dispatch("PATCH")
    def do_DELETE(self): self.dispatch("DELETE")

    def route(self, metodo):
        ruta = urlsplit(self.path).path.rstrip("/")
        qs = parse_qs(urlsplit(self.path).query)
        m = RUTA_ID.fullmatch(ruta)

        if metodo == "GET" and ruta == "/api/salud":
            ejecutar("SELECT 1 AS ok", one=True)
            return self.json_out(200, {"api": "ok", "db": "ok"})

        if metodo == "GET" and ruta == "/api/resumen":
            filas = ejecutar("SELECT estado, COUNT(*) AS total FROM incidencias GROUP BY estado")
            datos = {"Pendiente": 0, "En proceso": 0, "Resuelto": 0}
            for f in filas: datos[f["estado"]] = f["total"]
            return self.json_out(200, {"estados": datos, "total": sum(datos.values())})

        if metodo == "GET" and ruta == "/api/incidencias":
            where, args = [], []
            estado = qs.get("estado", [""])[0]
            categoria = qs.get("categoria", [""])[0]
            if estado:
                if estado not in ESTADOS: raise ValueError("estado no permitido")
                where.append("estado = %s"); args.append(estado)
            if categoria:
                if categoria not in CATEGORIAS: raise ValueError("categoría no permitida")
                where.append("categoria = %s"); args.append(categoria)
            sql = "SELECT id,titulo,descripcion,categoria,ubicacion,prioridad,estado,creado_en,actualizado_en FROM incidencias"
            if where: sql += " WHERE " + " AND ".join(where)
            sql += " ORDER BY id DESC LIMIT 200"
            return self.json_out(200, {"incidencias": ejecutar(sql, tuple(args))})

        if metodo == "GET" and m:
            fila = ejecutar("SELECT * FROM incidencias WHERE id = %s", (int(m.group(1)),), one=True)
            return self.json_out(200, fila) if fila else self.json_out(404, {"error": "No encontrado"})

        if metodo == "POST" and ruta == "/api/incidencias":
            d = validar_incidencia(self.json_in())
            _, nuevo = ejecutar("INSERT INTO incidencias (titulo, descripcion, categoria, ubicacion, prioridad, estado) VALUES (%s,%s,%s,%s,%s,%s)",
                               (d["titulo"],d["descripcion"],d["categoria"],d["ubicacion"],d["prioridad"],d["estado"]))
            print(json.dumps({"servicio":"api","accion":"incidencia_creada","folio":nuevo}), flush=True)
            return self.json_out(201, {"id": nuevo, "mensaje": "Incidencia registrada"})

        if metodo == "PATCH" and m:
            d = validar_incidencia(self.json_in(), parcial=True)
            campos = list(d)
            # Los nombres de campo vienen únicamente del conjunto blanco de validar_incidencia.
            set_clause = ", ".join(f"{k} = %s" for k in campos)
            filas, _ = ejecutar(f"UPDATE incidencias SET {set_clause} WHERE id = %s", (*[d[k] for k in campos], int(m.group(1))))
            if filas == 0:
                existe = ejecutar("SELECT id FROM incidencias WHERE id=%s", (int(m.group(1)),), one=True)
                if not existe: return self.json_out(404, {"error": "No encontrado"})
            print(json.dumps({"servicio":"api","accion":"incidencia_actualizada","folio":int(m.group(1))}), flush=True)
            return self.json_out(200, {"actualizado": True})

        if metodo == "DELETE" and m:
            filas, _ = ejecutar("DELETE FROM incidencias WHERE id = %s", (int(m.group(1)),))
            if not filas: return self.json_out(404, {"error": "No encontrado"})
            print(json.dumps({"servicio":"api","accion":"incidencia_eliminada","folio":int(m.group(1))}), flush=True)
            return self.json_out(200, {"eliminado": True})

        if metodo == "POST" and ruta == "/api/visitas":
            d = self.json_in()
            if d.get("nodo") not in NODOS: raise ValueError("nodo desconocido")
            _, pk = ejecutar("INSERT INTO visitas (nodo) VALUES (%s)", (d["nodo"],))
            return self.json_out(201, {"id": pk})

        if metodo == "GET" and ruta == "/api/visitas":
            filas = ejecutar("SELECT nodo, COUNT(*) AS total FROM visitas GROUP BY nodo ORDER BY nodo")
            return self.json_out(200, {"visitas": filas})

        if metodo == "POST" and ruta == "/api/pruebas":
            d = self.json_in()
            try:
                total = int(d.get("total")); exitos = int(d.get("exitos")); fallos = int(d.get("fallos"))
                prom = round(float(d.get("t_prom_ms")), 2)
            except (TypeError, ValueError, OverflowError):
                raise ValueError("resultados de prueba inválidos")
            dist = d.get("distribucion")
            if not isinstance(dist, dict) or set(dist) - NODOS:
                raise ValueError("distribución inválida")
            if not 1 <= total <= 1000 or min(exitos, fallos) < 0 or exitos + fallos != total or not 0 <= prom <= 100000:
                raise ValueError("conteos fuera de rango")
            if any(not isinstance(v, int) or isinstance(v, bool) or v < 0 or v > total for v in dist.values()):
                raise ValueError("conteos por nodo inválidos")
            if sum(dist.values()) > exitos: raise ValueError("distribución supera éxitos")
            _, pk = ejecutar("INSERT INTO pruebas (total,exitos,fallos,t_prom_ms,distribucion,cliente) VALUES (%s,%s,%s,%s,%s,%s)",
                             (total, exitos, fallos, prom, json.dumps(dist), self.client_address[0]))
            return self.json_out(201, {"id": pk})

        if metodo == "GET" and ruta == "/api/pruebas":
            filas = ejecutar("SELECT id,fecha,total,exitos,fallos,t_prom_ms,distribucion FROM pruebas ORDER BY id DESC LIMIT 15")
            for f in filas: f["distribucion"] = json.loads(f["distribucion"])
            return self.json_out(200, {"pruebas": filas})

        self.json_out(404, {"error": "Ruta no encontrada"})


if __name__ == "__main__":
    port = int(os.getenv("API_PUERTO", "5000"))
    print(json.dumps({"servicio":"api","evento":"iniciado","puerto":port}), flush=True)
    ThreadingHTTPServer(("0.0.0.0",port), Api).serve_forever()
