"""Pruebas locales de la API usando SQLite en memoria como sustituto.

Permiten validar el flujo HTTP/CRUD sin Docker. NO demuestran conectividad
real con MariaDB, Grafana o Nginx; esas pruebas se hacen con Docker Desktop.
"""
import importlib.util
import json
from pathlib import Path
import sqlite3
import sys
import threading
import types
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

# Sustituto de PyMySQL para las pruebas de la lógica HTTP.
conexion_ancora = sqlite3.connect('file:campus_tests?mode=memory&cache=shared', uri=True, check_same_thread=False)
conexion_ancora.row_factory = sqlite3.Row
conexion_ancora.executescript('''
CREATE TABLE incidencias (id INTEGER PRIMARY KEY AUTOINCREMENT,titulo TEXT NOT NULL,descripcion TEXT NOT NULL,categoria TEXT NOT NULL,ubicacion TEXT NOT NULL,prioridad TEXT NOT NULL,estado TEXT NOT NULL DEFAULT 'Pendiente',creado_en TEXT DEFAULT CURRENT_TIMESTAMP,actualizado_en TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE visitas (id INTEGER PRIMARY KEY AUTOINCREMENT,nodo TEXT NOT NULL);
CREATE TABLE pruebas (id INTEGER PRIMARY KEY AUTOINCREMENT,fecha TEXT DEFAULT CURRENT_TIMESTAMP,total INTEGER,exitos INTEGER,fallos INTEGER,t_prom_ms REAL,distribucion TEXT,cliente TEXT);
''')
conexion_ancora.commit()

class CursorMock:
    def __init__(self, conn): self.c = conn.cursor()
    def __enter__(self): return self
    def __exit__(self,*_): self.c.close()
    def execute(self, sql, params=()):
        self.c.execute(sql.replace('%s','?'), params)
        return self.c.rowcount
    @property
    def lastrowid(self): return self.c.lastrowid
    @property
    def rowcount(self): return self.c.rowcount
    def fetchone(self):
        row=self.c.fetchone()
        return dict(row) if row else None
    def fetchall(self): return [dict(row) for row in self.c.fetchall()]

class ConexionMock:
    def __init__(self):
        self.conn=sqlite3.connect('file:campus_tests?mode=memory&cache=shared', uri=True, check_same_thread=False)
        self.conn.row_factory=sqlite3.Row
    def cursor(self):return CursorMock(self.conn)
    def close(self):self.conn.commit();self.conn.close()

fake=types.ModuleType('pymysql')
fake.cursors=types.SimpleNamespace(DictCursor=dict)
fake.MySQLError=sqlite3.Error
fake.connect=lambda **kwargs: ConexionMock()
sys.modules['pymysql']=fake
ruta=Path(__file__).resolve().parents[1]/'api'/'app.py'
spec=importlib.util.spec_from_file_location('campus_api_pruebas',ruta)
app=importlib.util.module_from_spec(spec)
spec.loader.exec_module(app)

class PruebaAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.servidor=app.ThreadingHTTPServer(('127.0.0.1',0),app.Api)
        cls.base=f'http://127.0.0.1:{cls.servidor.server_port}'
        cls.hilo=threading.Thread(target=cls.servidor.serve_forever,daemon=True)
        cls.hilo.start()

    @classmethod
    def tearDownClass(cls):
        cls.servidor.shutdown();cls.servidor.server_close()
        conexion_ancora.close()

    def solicitar(self, method,path,data=None):
        payload=json.dumps(data).encode('utf-8') if data is not None else None
        request=Request(self.base+path, data=payload, method=method,
                        headers={'Content-Type':'application/json'})
        try:
            with urlopen(request,timeout=3) as respuesta:
                return respuesta.status,json.loads(respuesta.read())
        except HTTPError as e:
            return e.code,json.loads(e.read())

    def test_01_salud_y_resumen(self):
        status,res=self.solicitar('GET','/api/salud')
        self.assertEqual(status,200);self.assertEqual(res['db'],'ok')
        status,res=self.solicitar('GET','/api/resumen')
        self.assertEqual(status,200);self.assertEqual(res['total'],0)

    def test_02_crud(self):
        datos={'titulo':'Falla de red','descripcion':'No carga una página','categoria':'Internet','ubicacion':'Biblioteca','prioridad':'Alta'}
        status,res=self.solicitar('POST','/api/incidencias',datos)
        self.assertEqual(status,201);id_=res['id']
        status,res=self.solicitar('GET','/api/incidencias')
        self.assertEqual(status,200);self.assertTrue(any(x['id']==id_ for x in res['incidencias']))
        status,res=self.solicitar('PATCH',f'/api/incidencias/{id_}',{'estado':'En proceso'})
        self.assertEqual(status,200)
        status,res=self.solicitar('GET',f'/api/incidencias/{id_}')
        self.assertEqual(res['estado'],'En proceso')
        status,res=self.solicitar('DELETE',f'/api/incidencias/{id_}')
        self.assertEqual(status,200)
        status,res=self.solicitar('GET',f'/api/incidencias/{id_}')
        self.assertEqual(status,404)

    def test_03_rechaza_campos_invalidos(self):
        status,res=self.solicitar('POST','/api/incidencias',{'titulo':'abc'})
        self.assertEqual(status,400)
        status,res=self.solicitar('POST','/api/incidencias',{'titulo':'abc','descripcion':'x','ubicacion':'y','categoria':'Inexistente'})
        self.assertEqual(status,400)
        status,res=self.solicitar('PATCH','/api/incidencias/1',{'una_columna_sql':'DROP TABLE'})
        self.assertEqual(status,400)

    def test_04_prueba_y_visita(self):
        status,res=self.solicitar('POST','/api/visitas',{'nodo':'web2'})
        self.assertEqual(status,201)
        status,res=self.solicitar('GET','/api/visitas')
        self.assertEqual(status,200);self.assertEqual(res['visitas'][0]['nodo'],'web2')
        status,res=self.solicitar('POST','/api/pruebas',{'total':6,'exitos':6,'fallos':0,'t_prom_ms':10.2,'distribucion':{'web1':2,'web2':2,'web3':2}})
        self.assertEqual(status,201)
        status,res=self.solicitar('GET','/api/pruebas')
        self.assertEqual(status,200);self.assertEqual(res['pruebas'][0]['total'],6)

if __name__=='__main__':unittest.main()
