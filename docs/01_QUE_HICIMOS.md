# ¿Qué es CampusSoporte y por qué esta aplicación?

El material del profesor propone un mini centro de datos con múltiples contenedores, volúmenes, Nginx, una base de datos y supervisión con Grafana/Loki. También propone que la infraestructura respalde una aplicación decidida por el equipo.

**Decisión de proyecto:** desarrollar CampusSoporte, un sistema local de reportes de incidencias tecnológicas para estudiantes. Se elige porque responde al tema de necesidades de la comunidad del 23 de octubre y permite demostrar infraestructura y software al mismo tiempo.

## Objetivo general
Diseñar e implementar un mini centro de datos virtualizado mediante Docker Compose que permita registrar incidencias tecnológicas y demostrar disponibilidad, balanceo de carga, persistencia de datos y monitoreo de servicios.

## Objetivos específicos
1. Desplegar tres servidores web y un balanceador Nginx con distribución round-robin.
2. Implementar una API en Python para crear, consultar, editar y eliminar incidencias.
3. Guardar los reportes y las pruebas en una base de datos MariaDB con volumen persistente.
4. Capturar logs con Alloy y Loki y visualizarlos en Grafana.
5. Administrar el proyecto en Portainer y probar una falla de un nodo sin detener por completo la aplicación.

## Alcance real
- Sí realiza: CRUD, tres réplicas web, pruebas HTTP locales, logs, dashboard, cuatro volúmenes y redes separadas.
- No realiza: autenticación de personal, notificaciones, envío de correos, acceso remoto ni servidores físicos.
- No es un sistema oficial de la UPQ. Todos los reportes de ejemplo son ficticios.

## En una frase para la exposición
«La aplicación permite registrar fallas tecnológicas y usa una infraestructura de contenedores para distribuir las solicitudes, conservar información y monitorear el funcionamiento de los servicios».
