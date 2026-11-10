-- CampusSoporte | Base de datos local de demostración.
-- Este archivo se ejecuta solo cuando el volumen db_data está vacío.
CREATE DATABASE IF NOT EXISTS dc_app CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE dc_app;

CREATE TABLE IF NOT EXISTS incidencias (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  titulo VARCHAR(100) NOT NULL,
  descripcion VARCHAR(700) NOT NULL,
  categoria ENUM('Internet', 'Computadora', 'Proyector', 'Plataforma', 'Otro') NOT NULL,
  ubicacion VARCHAR(100) NOT NULL,
  prioridad ENUM('Baja', 'Media', 'Alta') NOT NULL DEFAULT 'Media',
  estado ENUM('Pendiente', 'En proceso', 'Resuelto') NOT NULL DEFAULT 'Pendiente',
  creado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  actualizado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  INDEX idx_estado (estado),
  INDEX idx_categoria (categoria),
  INDEX idx_creado (creado_en)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS nodos (
  id VARCHAR(32) PRIMARY KEY,
  nombre VARCHAR(64) NOT NULL,
  rack VARCHAR(32) NOT NULL,
  rol VARCHAR(120) NOT NULL
) ENGINE=InnoDB;
INSERT IGNORE INTO nodos (id,nombre,rack,rol) VALUES
('web1','Campus Norte','Rack A · U12','Servidor web 1'),
('web2','Campus Centro','Rack A · U14','Servidor web 2'),
('web3','Campus Sur','Rack B · U08','Servidor web 3');

CREATE TABLE IF NOT EXISTS visitas (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  nodo VARCHAR(32) NOT NULL,
  fecha DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  INDEX idx_visita_nodo (nodo),
  INDEX idx_visita_fecha (fecha)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS pruebas (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  fecha DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  total INT NOT NULL,
  exitos INT NOT NULL,
  fallos INT NOT NULL,
  t_prom_ms DECIMAL(9,2) NOT NULL,
  distribucion JSON NOT NULL,
  cliente VARCHAR(45) NULL
) ENGINE=InnoDB;

-- Datos ficticios para mostrar el sistema sin tener que crearlo todo a mano.
INSERT INTO incidencias (titulo, descripcion, categoria, ubicacion, prioridad, estado) VALUES
('Wi-Fi intermitente en biblioteca','La conexión se desconecta durante las consultas de materiales digitales.','Internet','Biblioteca','Alta','Pendiente'),
('Equipo sin acceso al software del laboratorio','La computadora muestra un error al iniciar la aplicación.','Computadora','Laboratorio de cómputo 2','Media','En proceso'),
('Proyector no detecta la computadora','No aparece la imagen al conectar el cable HDMI.','Proyector','Aula B-104','Media','Pendiente'),
('Error al cargar archivos de clase','La plataforma marca error cuando se sube un archivo PDF.','Plataforma','Plataforma virtual','Alta','En proceso'),
('Actualización de navegador completada','Se actualizó el navegador del equipo de consulta.','Computadora','Sala de estudio','Baja','Resuelto');
