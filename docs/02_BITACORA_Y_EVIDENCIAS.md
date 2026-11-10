# Bitácora del proyecto — plantilla editable

**Asignatura:** Centro de Datos  
**Proyecto:** CampusSoporte — Mini Centro de Datos  
**Equipo:** [Agregar integrantes y roles]  
**Fecha:** [Fecha real de las pruebas]

## Objetivo
Implementar en una computadora un mini centro de datos con Docker Compose que ejecute un sistema de reportes tecnológicos, distribuya accesos entre tres servidores web y mantenga datos y registros para el monitoreo.

## Herramientas
Docker Desktop, Docker Compose, Nginx, Python, MariaDB, Grafana, Loki, Alloy, Portainer, VS Code y PowerShell.

## Desarrollo y evidencia

**1. Estructura del proyecto.** Mostrar la carpeta con `docker-compose.yml`, `api`, `sitios`, `nginx`, `mariadb`, `observabilidad` y `grafana`.

[Insertar captura 1: VS Code y árbol de archivos]

**2. Despliegue.** Se inició la infraestructura con `docker compose up -d --build`. El comando `docker compose ps` permitió revisar los servicios.

[Insertar captura 2: terminal y servicios `running`/`healthy`]

**3. Aplicación y persistencia.** Se registró una incidencia de prueba, se modificó su estado y se comprobó que el registro permaneció tras detener y reiniciar los contenedores sin borrar los volúmenes.

[Insertar captura 3: portal con la incidencia nueva]

[Insertar captura 4: edición / estado cambiado]

[Insertar captura 5: registro conservado después de reiniciar]

**4. Balanceo de carga.** Se enviaron [número real] solicitudes a Nginx. El resultado observado fue: web1=[ ], web2=[ ], web3=[ ], fallos=[ ].

[Insertar captura 6: gráfica de distribución de nodos en el portal]

**5. Monitoreo.** Se consultó Grafana para visualizar las solicitudes y el estado de las incidencias. Alloy recopila los registros que Loki almacena.

[Insertar captura 7: dashboard Grafana]

[Insertar captura 8: registros del balanceador en Loki]

**6. Gestión.** Se inspeccionaron los contenedores y volúmenes desde Portainer.

[Insertar captura 9: Portainer con contenedores]

**7. Prueba de disponibilidad.** Se detuvo `web2`, se ejecutaron [ ] solicitudes y se registraron los resultados de los otros nodos.

[Insertar captura 10: fallo de web2 y nuevos resultados; posteriormente recuperar el nodo]

## Resultados
[Anotar exclusivamente los resultados reales; no inventar cifras ni capturas.]

## Problemas y soluciones
[Explicar brevemente errores reales: puertos ocupados, contenedor no saludable, configuración de credenciales, etc.]

## Conclusión personal — ejemplo a ajustar después de las pruebas
Con este proyecto entendí mejor cómo se relacionan los contenedores dentro de una misma aplicación. Al principio veía Docker como una herramienta para ejecutar programas por separado, pero al configurar Nginx, MariaDB y el monitoreo pude observar cómo cada servicio cumple una función. Me parece importante la persistencia porque evita que los reportes desaparezcan cuando se reinicia la infraestructura. Lo que más necesito practicar es la interpretación de los registros de Grafana y la solución de errores, ya que no basta con encender los contenedores: también hay que comprobar que realmente funcionan.
