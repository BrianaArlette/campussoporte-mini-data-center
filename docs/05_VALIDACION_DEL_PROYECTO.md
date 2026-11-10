# Verificación previa y pruebas pendientes

## Verificaciones de desarrollo realizadas

- Archivos `docker-compose.yml` y `observabilidad/loki.yaml` interpretados como YAML sin errores de sintaxis.
- Diez servicios, tres redes y cuatro volúmenes identificados en Compose.
- API Python compilada sin errores de sintaxis.
- JavaScript verificado con Node (`node --check`).
- Cuatro pruebas HTTP de la API aprobadas con una base SQLite temporal que sustituye a MariaDB: salud y resumen; ciclo crear/consultar/editar/eliminar; rechazo de datos inválidos; visitas y registro de pruebas.
- Interfaz visualizada en navegador de pruebas con datos ficticios y backend simulado, sin errores de JavaScript. **Esto no es evidencia del Docker ejecutándose.**
- Documento Word renderizado y revisado visualmente (2 páginas).

## Comprobaciones que faltan en la PC de la estudiante

- Ejecución real de `docker compose config --quiet` y `docker compose up -d --build`.
- Descarga y compatibilidad de las imágenes Docker con su equipo.
- Inicialización y permisos efectivos de MariaDB.
- Consultas CRUD reales desde la aplicación.
- Comportamiento de Nginx al distribuir solicitudes y al caer `web2`.
- Llegada de logs Alloy → Loki → Grafana y visualización del tablero.
- Persistencia después de reiniciar los servicios.
- Capturas reales y resultados medidos.

## Diagnóstico si algún servicio no arranca

```powershell
docker compose ps
docker compose logs --tail 100 db api lb
docker compose logs --tail 100 grafana loki alloy
docker compose logs --tail 50 web1 web2 web3
```

**No borres los volúmenes para intentar arreglar un problema sin antes guardar o revisar los datos.**
