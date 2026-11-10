# Distribución propuesta de trabajo — Scrum / DevOps

Estos roles son una **recomendación de organización**, no una distribución confirmada por el profesor.

| Rol | Responsabilidad | Evidencia |
|---|---|---|
| Gestor/a de contenedores | Docker Compose, redes, puertos, Nginx y balanceo. | `docker compose ps`, distribución por nodos. |
| Gestor/a de base de datos | Esquema MariaDB, usuarios, volumen, persistencia. | Tabla de incidencias y prueba tras reiniciar. |
| Gestor/a de aplicación | Interfaz CampusSoporte y API Python CRUD. | Registrar, editar, consultar y eliminar. |
| Gestor/a de monitoreo | Grafana, Loki, Alloy y Portainer. | Dashboard y logs. |
| Gestor/a de bitácora | Evidencia, documentación, resultados y presentación. | Capturas, guía y presentación. |

**Backlog / tareas del sprint**
- [ ] Descargar y abrir el proyecto en VS Code.
- [ ] Configurar `.env` y comprobar que Docker Desktop funciona.
- [ ] Desplegar todos los contenedores.
- [ ] Comprobar CRUD de CampusSoporte.
- [ ] Ejecutar carga y registrar el resultado real.
- [ ] Inspeccionar Grafana, Alloy, Loki y Portainer.
- [ ] Verificar persistencia y caída controlada de web2.
- [ ] Reunir capturas y preparar explicación oral.

**Criterio de terminado:** ninguna tarea se marca como terminada hasta que exista evidencia de funcionamiento. No basta con que el código esté escrito.
