# Guía para presentar CampusSoporte

## Orden sugerido para la demostración
1. **Problema:** cuando hay fallas en equipos o plataformas, no siempre existe un registro claro de seguimiento.
2. **Propuesta:** CampusSoporte permite registrar y administrar incidencias de manera local.
3. **Arquitectura:** navegador → Nginx → web1, web2, web3; las solicitudes a la API → Python → MariaDB; Alloy → Loki → Grafana. Portainer administra contenedores.
4. **Demostración:** crear un reporte, cambiarlo a «En proceso», ejecutar 30 solicitudes y mostrar la gráfica por nodo.
5. **Persistencia y disponibilidad:** mostrar que los datos se conservan y que la aplicación sigue disponible cuando se detiene temporalmente un nodo web.
6. **Aprendizaje:** explicar qué mejoró en la comprensión de Docker, volúmenes, redes y monitoreo.

## Explicación breve para decir de forma natural
«Para este proyecto desarrollé una aplicación de reportes tecnológicos llamada CampusSoporte. Permite registrar problemas como fallas de internet, computadoras o proyectores. La aplicación corre sobre un mini centro de datos simulado con Docker. Nginx reparte las solicitudes entre tres servidores web; una API en Python conecta el sistema con MariaDB, donde los reportes se guardan de forma persistente. También integré Grafana y Loki para observar el tráfico y los registros de los servicios. La idea es comprobar no solo que la página abre, sino que la infraestructura responde, conserva los datos y permite detectar fallas».

**Revisar el guion y adaptarlo a lo que efectivamente hayas hecho y probado.** Si es un trabajo en equipo, cada integrante debe describir sus aportaciones reales.

## Preguntas posibles
**¿Por qué Docker en vez de instalar todo directamente?** Porque cada servicio tiene su entorno y sus dependencias, lo que facilita replicarlo y gestionarlo.

**¿Qué es una imagen y qué es un contenedor?** Imagen: plantilla lista para ejecutar. Contenedor: instancia en funcionamiento de esa imagen.

**¿Para qué sirve Nginx?** Recibe solicitudes y las distribuye entre los tres servidores web para repartir el tráfico. El modo utilizado es round-robin.

**¿Qué pasa si se detiene un nodo web?** Se esperan respuestas de los nodos restantes, después de que el balanceador detecta el fallo. Debe comprobarse con una prueba real.

**¿Para qué es el volumen?** Hace persistentes los datos de MariaDB, incluso si eliminas y vuelves a crear el contenedor sin eliminar el volumen.

**¿Loki simula usuarios?** No. Loki almacena logs; las peticiones las simula un script o el botón de la aplicación. Alloy recoge logs; Grafana los muestra.

**¿La app es productiva?** No. Es una demostración académica local; le faltan autenticación, permisos y otros controles para publicarla.
