"""Genera contraseñas nuevas en .env sin modificar archivos de código."""
from pathlib import Path
import secrets

root = Path(__file__).resolve().parents[1]
archivo = root / '.env'
if archivo.exists():
    print('Ya existe .env; no se modificó para proteger tus datos.')
else:
    contenido = f'''# CampusSoporte - configuración LOCAL y privada. No compartir ni subir a GitHub.
LB_PUERTO=8080
GRAFANA_PUERTO=3000
DB_PUERTO=3307
DB_ROOT_PASSWORD={secrets.token_hex(20)}
APP_DB_PASSWORD={secrets.token_hex(20)}
GRAFANA_DB_PASSWORD={secrets.token_hex(20)}
GRAFANA_ADMIN_USER=admin_campus
GRAFANA_ADMIN_PASSWORD={secrets.token_hex(20)}
'''
    archivo.write_text(contenido, encoding='utf-8')
    print('Se creó .env con cuatro contraseñas aleatorias. NO se mostraron en pantalla.')
print('Directorio del proyecto:', root)
print('Siguiente paso: docker compose up -d --build')
