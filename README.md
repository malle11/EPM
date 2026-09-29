# EPM - Enterprise Project Management

Aplicacion web de gestion de proyectos enterprise, desarrollada con **Python (Flask)** y **MySQL**,
para la Actividad 2 - Deploy manual + Marketplace (ITM 2026).

**Autora:** Luz Mallely Zapata

---

## 1. Que hace la aplicacion

| Modulo | Descripcion |
|---|---|
| **Autenticacion** | Inicio de sesion con usuario y contrasena (hash SHA256, nunca texto plano). |
| **Roles** | `ADMINISTRADOR` y `USUARIO`, con permisos distintos. |
| **Panel de control** | Indicadores de gestion, avance de proyectos y tareas asignadas. |
| **Proyectos** | Codigo, nombre, descripcion, fechas, presupuesto y estados. |
| **Tareas** | Prioridad, estado, responsable y fecha limite. El usuario solo cambia el estado de sus propias tareas. |
| **Administracion** | Crear usuarios, cambiar roles, activar/desactivar cuentas y reiniciar contrasenas. |
| **Bitacora** | Registro (auditoria) de cada transaccion administrativa. |

## 2. Roles y permisos

| Accion | USUARIO | ADMINISTRADOR |
|---|:--:|:--:|
| Ver panel y proyectos | Si | Si |
| Cambiar estado de sus tareas | Si | Si |
| Ver todas las tareas del equipo | No | Si |
| Crear / editar proyectos | No | Si |
| Crear, cambiar rol, activar usuarios | No | Si |
| Ver bitacora de transacciones | No | Si |

## 3. Estructura del proyecto

```
EPM/
├── app.py              # Configuracion de la aplicacion Flask
├── wsgi.py             # Punto de entrada para Gunicorn / mod_wsgi
├── config.py           # Lee variables de entorno y el archivo .env
├── db.py               # Pool de conexiones MySQL y funciones de consulta
├── auth.py             # Inicio de sesion y decoradores de permiso
├── routes.py           # Paginas del usuario (panel, proyectos, tareas)
├── admin.py            # Paginas del administrador (usuarios, bitacora)
├── schema.sql          # Creacion de la base de datos y datos iniciales
├── requirements.txt    # Dependencias de Python
├── templates/          # Plantillas HTML con Jinja2
├── static/style.css    # Estilos de la interfaz
├── deploy/
│   ├── deploy.sh       # Despliegue automatizado en Ubuntu (sin Docker)
│   └── README.md       # Instrucciones del despliegue
└── docs/
    └── EVIDENCIAS.md   # Guia de las capturas que pide la actividad
```

## 4. Base de datos

| Tabla | Contenido |
|---|---|
| `roles` | Catalogo de roles. |
| `usuarios` | Cuentas con correo, hash de contrasena, rol y estado. |
| `proyectos` | Proyectos con presupuesto, fechas y estado. |
| `tareas` | Tareas por proyecto, con responsable, prioridad y estado. |
| `indicadores` | Metricas de gestion con formula y meta. |
| `bitacora` | Auditoria de las transacciones administrativas. |

## 5. Ejecutar en local

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Crear la base de datos
mysql -u root < schema.sql

# 3. Configurar la conexion
copy .env.example .env      # Windows: copy .env.example .env
#    Editar .env con tus datos

# 4. Arrancar
python wsgi.py
```

Abrir <http://127.0.0.1:5000>

## 6. Cuentas de prueba

| Rol | Correo | Contrasena |
|---|---|---|
| Administrador | `admin@epm.com` | `admin123` |
| Usuario | `malle@epm.com` | `admin123` |
| Usuario | `carlos@epm.com` | `admin123` |

## 7. Despliegue en la nube

El despliegue se hace **sin Docker**, con Apache + mod_wsgi + MySQL sobre una VM Ubuntu.
El procedimiento completo esta en [`deploy/README.md`](deploy/README.md) y se automatiza con:

```bash
sudo bash deploy/deploy.sh
```

## 8. Technologias

- Python 3.12 y Flask 3
- MySQL 8 con `mysql-connector-python`
- Apache 2 con `mod_wsgi`
- Jinja2 para las plantillas
- HTML y CSS puro para la interfaz
