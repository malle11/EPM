# Guia de evidencias - Actividad 2

La actividad pide demostrar **2 de 3** grupos de evidencias. Este documento indica
cual grupo.take cada captura y donde guardarla.

Carpeta sugerida para las capturas:

```
evidencias/
├── 01_servidor/
├── 02_configuracion/
├── 03_aplicacion/
└── 04_transacciones/
```

---

## Grupo A - Implementacion y configuracion de servicios en la nube

Demuestra que la app quedo **publicada y funcionando** en un servidor real.

| # | Evidencia | Como se toma | Captura de terminal |
|---|---|---|---|
| A1 | Servidor VPS creado y activo | Panel del proveedor (AWS, Oracle, DigitalOcean) | `hostname -I` y `lsb_release -a` |
| A2 | Conectado por SSH al VPS | Terminal con `ssh usuario@IP` | La misma terminal |
| A3 | Apache instalado y corriendo | Panel o terminal | `sudo systemctl status apache2` |
| A4 | MySQL instalado y corriendo | Terminal | `sudo systemctl status mysql` |
| A5 | Puertos abiertos | Terminal | `sudo ufw status` y `sudo ss -tlnp` |
| A6 | La app responde por IP publica | Navegador | `curl -I http://IP_DEL_SERVIDOR` |

---

## Grupo B - Configuracion de la aplicacion (usuarios y administrador)

Demuestra la gestion de **usuarios, roles y permisos** desde la interfaz.

| # | Evidencia | Como se toma |
|---|---|---|
| B1 | Pantalla de login de EPM | Navegador con `http://IP_DEL_SERVIDOR` |
| B2 | Ingreso como ADMINISTRADOR | `admin@epm.com` / `admin123` |
| B3 | Creacion de un usuario nuevo | Pestana **Usuarios** -> formulario "Crear usuario" -> enviar |
| B4 | El usuario nuevo aparece en la tabla | Captura de la tabla con el usuario agregado |
| B5 | Cambio de rol | Formulario "Cambiar rol" -> seleccionar **ADMINISTRADOR** -> enviar |
| B6 | Activar / desactivar un usuario | Boton "Desactivar" -> la etiqueta pasa a INACTIVO |
| B7 | Reinicio de contrasena | Boton "Reiniciar contrasena" -> la alerta muestra la nueva |
| B8 | Proteccion de rutas: un USUARIO no entra al admin | Iniciar sesion con `sara@epm.com` y entrar a `/admin/usuarios` |

---

## Grupo C - Funcionamiento y transacciones de la administracion

Demuestra la app en uso y las operaciones administrativas sobre la base de datos.

| # | Evidencia | Como se toma |
|---|---|---|
| C1 | Panel con indicadores | Dashboard de la app |
| C2 | Lista de proyectos con avance | Pagina **Proyectos** |
| C3 | Detalle de un proyecto con sus tareas | Detalle de `EPM-001` |
| C4 | Un USUARIO cambia el estado de una tarea | Selector "Actualizar" en su tarea |
| C5 | El ADMINISTRADOR crea un proyecto | **Nuevo proyecto** -> guardar |
| C6 | El ADMINISTRADOR crea una tarea y la asigna | Detalle del proyecto -> "Asignar nueva tarea" |
| C7 | El ADMINISTRADOR cambia el estado de un proyecto | Selector "Cambiar estado" |
| C8 | **Bitacora de transacciones** con los cambios | Pagina **Bitacora** (ultimas 100) |
| C9 | Confirmar en la base de datos | `sudo mysql -u epm_user -p epm_db` -> `SELECT * FROM bitacora;` |

---

## Estructura sugerida del PDF final

1. Portada: materia, nombre del trabajo, autora, fecha.
2. Contexto: que es la actividad y que se hizo.
3. Infraestructura creada (Grupo A).
4. Configuracion de la aplicacion (Grupo B).
5. Funcionamiento y transacciones (Grupo C).
6. Conclusiones.
7. Referencias bibliograficas.

Datos de la entrega:

- **Correo:** `enriquegonzalez5940@correo.itm.edu.co`
- **Fecha limite:** 5 de octubre de 2026
- **Formato:** PDF formal, indicando materia y nombre del trabajo
