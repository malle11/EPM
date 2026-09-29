-- ============================================================
-- EPM - Enterprise Project Management
-- Base de datos MySQL - Luz Mallely Zapata
-- ============================================================

DROP DATABASE IF EXISTS epm_db;
CREATE DATABASE epm_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE epm_db;

-- ---------- ROLES ----------
CREATE TABLE roles (
    id     INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(30) NOT NULL UNIQUE
) ENGINE=InnoDB;

-- ---------- USUARIOS ----------
CREATE TABLE usuarios (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    nombre     VARCHAR(80)  NOT NULL,
    email      VARCHAR(120) NOT NULL UNIQUE,
    password   VARCHAR(255) NOT NULL COMMENT 'hash SHA256, nunca texto plano',
    rol_id     INT          NOT NULL,
    cargo      VARCHAR(60)  DEFAULT NULL,
    activo     TINYINT(1)   NOT NULL DEFAULT 1,
    creado_en  TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_usuarios_rol FOREIGN KEY (rol_id) REFERENCES roles(id)
) ENGINE=InnoDB;

-- ---------- PROYECTOS ----------
CREATE TABLE proyectos (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    codigo       VARCHAR(20)  NOT NULL UNIQUE,
    nombre       VARCHAR(120) NOT NULL,
    descripcion  TEXT,
    fecha_inicio DATE,
    fecha_fin    DATE,
    presupuesto  DECIMAL(14,2) NOT NULL DEFAULT 0,
    estado       ENUM('PLANIFICACION','EN_CURSO','PAUSADO','FINALIZADO')
                 NOT NULL DEFAULT 'PLANIFICACION',
    creado_por   INT          NOT NULL,
    creado_en    TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_proyectos_autor FOREIGN KEY (creado_por) REFERENCES usuarios(id)
) ENGINE=InnoDB;

-- ---------- TAREAS ----------
CREATE TABLE tareas (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    proyecto_id  INT          NOT NULL,
    titulo       VARCHAR(150) NOT NULL,
    descripcion  TEXT,
    asignado_a   INT          DEFAULT NULL,
    prioridad    ENUM('BAJA','MEDIA','ALTA') NOT NULL DEFAULT 'MEDIA',
    estado       ENUM('PENDIENTE','EN_PROGRESO','BLOQUEADA','COMPLETADA')
                 NOT NULL DEFAULT 'PENDIENTE',
    fecha_limite DATE,
    creado_en    TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_tareas_proyecto FOREIGN KEY (proyecto_id)
        REFERENCES proyectos(id) ON DELETE CASCADE,
    CONSTRAINT fk_tareas_usuario FOREIGN KEY (asignado_a)
        REFERENCES usuarios(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- ---------- BITACORA (auditoria / transacciones admin) ----------
CREATE TABLE bitacora (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT          DEFAULT NULL,
    usuario    VARCHAR(80)  NOT NULL,
    accion     VARCHAR(60)  NOT NULL,
    entidad    VARCHAR(40)  NOT NULL,
    entidad_id INT          DEFAULT NULL,
    detalle    TEXT,
    fecha      TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ---------- INDICADORES (metrica de gestion) ----------
CREATE TABLE indicadores (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    proyecto_id INT          NOT NULL,
    nombre      VARCHAR(120) NOT NULL,
    formula     VARCHAR(200) NOT NULL,
    meta        DECIMAL(10,2) NOT NULL DEFAULT 0,
    creado_en   TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_indicadores_proyecto FOREIGN KEY (proyecto_id)
        REFERENCES proyectos(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================
-- DATOS INICIALES
-- password de los 3 usuarios = admin123
-- hash SHA256('admin123') = 240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9
-- ============================================================
INSERT INTO roles (id, nombre) VALUES
    (1, 'ADMINISTRADOR'),
    (2, 'USUARIO');

INSERT INTO usuarios (nombre, email, password, rol_id, cargo) VALUES
    ('Luz Mallely Zapata', 'admin@epm.com',
     '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 1, 'Administradora del sistema'),
    ('Sara Guisao', 'sara@epm.com',
     '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 2, 'Analista de proyectos'),
    ('Carlos Ramirez', 'carlos@epm.com',
     '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 2, 'Desarrollador');

INSERT INTO proyectos (codigo, nombre, descripcion, fecha_inicio, fecha_fin, presupuesto, estado, creado_por) VALUES
    ('EPM-001', 'Migracion de base de datos a la nube',
     'Mover el servidor de base de datos corporate al VPS y configurar respaldos.',
     '2026-09-15', '2026-11-30', 45000000, 'EN_CURSO', 1),
    ('EPM-002', 'Portal web de proveedores',
     'Diseno e implementacion del portal de registro y seguimiento de proveedores.',
     '2026-10-01', '2027-01-15', 28000000, 'PLANIFICACION', 1),
    ('EPM-003', 'Automatizacion de reportes mensuales',
     'Scripts en Python para generar los reportes de indicadores de cada mes.',
     '2026-08-01', '2026-10-20', 12000000, 'FINALIZADO', 1);

INSERT INTO tareas (proyecto_id, titulo, descripcion, asignado_a, prioridad, estado, fecha_limite) VALUES
    (1, 'Levantar servidor Ubuntu en el VPS', 'Crear la maquina virtual y asegurar el acceso por SSH.', 3, 'ALTA', 'COMPLETADA', '2026-09-20'),
    (1, 'Configurar Apache y MySQL', 'Instalar y asegurar los servicios en el servidor.', 3, 'ALTA', 'EN_PROGRESO', '2026-09-29'),
    (1, 'Migrar esquema de base de datos', 'Ejecutar schema.sql y seed.sql en el servidor.', 2, 'ALTA', 'PENDIENTE', '2026-10-02'),
    (2, 'Diseno de la base de datos', 'Modelo entidad relacion de proveedores y contratos.', 2, 'MEDIA', 'PENDIENTE', '2026-10-10'),
    (2, 'Pantalla de registro de proveedores', 'Formulario con validacion de datos.', 3, 'MEDIA', 'PENDIENTE', '2026-10-20'),
    (3, 'Script generador de PDF', 'Generar el reporte mensual en PDF.', 2, 'BAJA', 'COMPLETADA', '2026-09-25'),
    (3, 'Envio automático por correo', 'Programar el envio del reporte a los Gerentes.', 2, 'BAJA', 'COMPLETADA', '2026-09-28');

INSERT INTO indicadores (proyecto_id, nombre, formula, meta) VALUES
    (1, '% de tareas completadas', 'tareas COMPLETADA / total tareas * 100', 80),
    (2, '% de avance del proyecto', 'tareas COMPLETADA / total tareas * 100', 60),
    (3, 'Horas de ahorro al mes', 'horas manuales - horas automaticas', 20);
