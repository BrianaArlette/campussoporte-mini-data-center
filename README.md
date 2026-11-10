# CampusSoporte — Mini Centro de Datos

**Proyecto académico funcional para montar en Docker Desktop.** CampusSoporte es una aplicación de demostración para registrar, consultar, editar y eliminar incidentes tecnológicos de un campus. No pertenece a ninguna universidad ni ofrece soporte real.

Esta carpeta **adapta la infraestructura didáctica** compartida por el profesor para una app distinta: un portal de reportes con base de datos, tres nodos de servicio, balanceador, registros y paneles de monitoreo.

## Qué contiene

| Capa | Servicio | Función |
|---|---|---|
| Entrada | `lb` (Nginx) | Balanceador round-robin, accesible por `http://localhost:8080` |
| Web | `web1`, `web2`, `web3` (Nginx) | Tres réplicas de CampusSoporte. Cada respuesta indica qué nodo atendió. |
| API | `api` (Python) | Operaciones CRUD de incidencias y registro de pruebas. |
| Datos | `db` (MariaDB) | Incidencias, visitas y pruebas guardadas en volumen `db_data`. |
| Logs | `alloy`, `loki` | Alloy lee los logs de Docker y los envía a Loki. |
| Tableros | `grafana` | Muestra el tráfico, respuestas HTTP, logs e incidencias. |
| Administración | `portainer` | Gestiona los contenedores en interfaz web. |

**Total: 10 contenedores/servicios.** Una PC con Docker ejecuta la simulación; esto no equivale a diez máquinas físicas. Se utilizan redes virtuales, puertos en localhost y cuatro volúmenes persistentes.

## Inicio en Windows / VS Code

1. Extrae **toda** esta carpeta en tu computadora, por ejemplo en `Documentos\CampusSoporte_Mini_Data_Center` (mejor fuera de OneDrive).
2. Abre **esta carpeta**, no un archivo suelto, en VS Code.
3. Abre Docker Desktop y asegúrate de que esté ejecutando contenedores **Linux**.
4. En la terminal PowerShell de VS Code, estando en la raíz de esta carpeta, ejecuta:

   ```powershell
   python scripts/preparar.py
   docker compose config --quiet
   docker compose up -d --build
   docker compose ps
   ```

   - `preparar.py`: genera `.env` con contraseñas privadas y aleatorias, sin sobrescribir las anteriores.
   - `docker compose config --quiet`: revisa configuración y variables sin mostrar contraseñas.
   - `docker compose up -d --build`: descarga imágenes, construye API y enciende la infraestructura en segundo plano.
   - `docker compose ps`: muestra estado y puertos de contenedores.

   Si Windows responde que no encuentra `python`, usa `py -3 scripts/preparar.py`.

5. Abre los servicios (son direcciones de **tu computadora**, no sitios de internet):

   | Servicio | Dirección |
   |---|---|
   | CampusSoporte | http://localhost:8080 |
   | Grafana | http://localhost:3000 |
   | Portainer (HTTPS) | https://localhost:9443 |
   | API salud | http://localhost:8080/api/salud |
   | Alloy (opcional) | http://localhost:12345 |

6. Accede a Grafana con `GRAFANA_ADMIN_USER` y `GRAFANA_ADMIN_PASSWORD` del archivo `.env`. En Portainer crea la contraseña de administrador en el primer acceso. En Portainer puede aparecer un aviso de certificado local/autofirmado para el laboratorio.

7. El panel de Grafana se llama **CampusSoporte | Centro de Datos: tráfico e incidencias**. Debe mostrar tablas de incidencias y, después de enviar peticiones, registros y gráficos del balanceador.

## Primera demostración completa

1. En CampusSoporte, crea una incidencia ficticia. Comprueba que aparece en la lista y que incrementa el total.
2. Edita el incidente para cambiar su estado a «En proceso»; verifica el cambio del contador.
3. En «Simulación de solicitudes» ejecuta **30** peticiones. Comprueba que llegan a `web1`, `web2` y `web3` y se registra la prueba.
4. Abre Grafana. Revisa «Incidencias por estado», «Peticiones por nodo» y la bitácora del balanceador.
5. Abre Portainer. Revisa que se muestran los contenedores y los volúmenes.
6. Para comprobar persistencia, anota el folio de la incidencia creada; ejecuta `docker compose down` y después `docker compose up -d`. Verifica que el folio sigue presente. **No uses `down -v`: borraría los volúmenes y los datos.**
7. Para demostrar tolerancia a fallos, ejecuta `docker compose stop web2`, vuelve a enviar 30 solicitudes y verifica que continúan atendiendo `web1` y `web3`. Después ejecuta `docker compose start web2`.

**Importante:** el primer acceso de los servicios puede no ser inmediato después de `up`; la base MariaDB debe inicializar y el resto conectarse. Si algún servicio no arranca, consulta los logs con `docker compose logs --tail 80 api db lb grafana alloy loki`.

## Comandos de administración

```powershell
docker compose ps                              # Ver servicios
docker compose logs --tail 80 api db          # Diagnosticar API y BD
docker compose logs --tail 80 lb              # Ver peticiones que recibió Nginx
docker compose stop web2                      # Simular falla de un servidor web
docker compose start web2                     # Recuperarlo
docker compose down                           # Detener y quitar contenedores (preserva volúmenes)
docker volume ls                              # Ver volúmenes
```

Desde Workbench: servidor `127.0.0.1`, puerto `3307`, usuario `app_user`, contraseña `APP_DB_PASSWORD` de `.env`, base `dc_app`.

## Qué se entrega

- Proyecto completo: archivos `docker-compose.yml`, `api/`, `sitios/`, `nginx/`, `mariadb/`, `grafana/` y `observabilidad/`, más `pruebas/` y `docs/`.
- Capturas **reales** de Docker Desktop, CampusSoporte, operaciones CRUD, prueba de carga, Grafana, Portainer y persistencia.
- Bitácora técnica y una exposición con explicación de la arquitectura y los resultados. Usa los documentos de `docs/` como guía.
- **No subas `.env` a GitHub**; el `.gitignore` lo excluye. Si compartes la carpeta, quita `.env`.

Este documento resume una propuesta preparada con base en el material proporcionado: **no constituye una rúbrica oficial**. La presentación del docente sí evalúa contenido técnico, claridad, creatividad/estructura y funcionamiento. La entrega final exacta y las responsabilidades del equipo deben confirmarse con el profesor.

## Seguridad y limitaciones

- Solo se publican interfaces en `127.0.0.1` para evitar acceso desde otras computadoras. No abrir puertos del router.
- El portal no tiene inicio de sesión: es un laboratorio, **no se deben registrar datos personales reales** y no debe desplegarse en internet sin autenticación, permisos, HTTPS y protección adicionales.
- Alloy y Portainer acceden al socket de Docker, que equivale a permisos administrativos sobre Docker: son herramientas del laboratorio local.
- Grafana y los logs requieren memoria; cierra programas pesados si tu computadora tiene pocos recursos.
- Es necesario probar el proyecto en tu PC con Docker Desktop. La revisión estática de archivos no equivale a una ejecución real.

## Procedencia

La estructura de contenedores/observabilidad se basó en `minidc-ejercicio1(1).zip` del profesor. CampusSoporte es una adaptación con un caso de uso nuevo, interfaz propia, API CRUD, tablas de incidencias, nuevas consultas para Grafana y material de pruebas/documentación.
