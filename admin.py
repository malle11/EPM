import functools
import hashlib
import secrets

from flask import Blueprint, flash, redirect, render_template, request, url_for

from auth import es_admin, requiere_admin, usuario_actual
from db import execute, hash_password, query, registrar_bitacora

bp = Blueprint("admin", __name__, url_prefix="/admin")


def solo_admin(f):
    @functools.wraps(f)
    def envoltura(*args, **kwargs):
        if not es_admin():
            flash("Acceso restringido: se requiere rol ADMINISTRADOR.", "error")
            return redirect(url_for("main.dashboard"))
        return f(*args, **kwargs)

    return envoltura


@bp.route("/usuarios")
@solo_admin
def usuarios():
    lista = query(
        """SELECT u.id, u.nombre, u.email, u.cargo, u.activo, u.creado_en, r.nombre AS rol
           FROM usuarios u JOIN roles r ON r.id = u.rol_id ORDER BY u.id"""
    )
    roles = query("SELECT * FROM roles ORDER BY id")
    return render_template("admin_usuarios.html", usuario=usuario_actual(), es_admin=True,
                           usuarios=lista, roles=roles)


@bp.route("/usuarios/crear", methods=["POST"])
@solo_admin
def crear_usuario():
    nombre = request.form["nombre"].strip()
    email = request.form["email"].strip().lower()
    cargo = request.form.get("cargo", "").strip()
    rol_id = request.form["rol_id"]
    password = request.form.get("password") or secrets.token_urlsafe(8)

    if not nombre or not email or "@" not in email:
        flash("Nombre y correo valido son obligatorios.", "error")
        return redirect(url_for("admin.usuarios"))

    if query("SELECT id FROM usuarios WHERE email = %s", (email,), one=True):
        flash(f"El correo {email} ya esta registrado.", "error")
        return redirect(url_for("admin.usuarios"))

    nuevo_id, _ = execute(
        """INSERT INTO usuarios (nombre, email, password, rol_id, cargo)
           VALUES (%s, %s, %s, %s, %s)""",
        (nombre, email, hash_password(password), int(rol_id), cargo),
    )
    registrar_bitacora(usuario_actual(), "Creacion de usuario", "usuarios", nuevo_id,
                       f"{nombre} <{email}> rol_id={rol_id}")
    flash(f"Usuario {nombre} creado. Contrasena temporal: {password}", "ok")
    return redirect(url_for("admin.usuarios"))


@bp.route("/usuarios/<int:usuario_id>/rol", methods=["POST"])
@solo_admin
def cambiar_rol(usuario_id):
    rol_id = int(request.form["rol_id"])
    objetivo = query("SELECT * FROM usuarios WHERE id = %s", (usuario_id,), one=True)
    if not objetivo:
        flash("Usuario no encontrado.", "error")
        return redirect(url_for("admin.usuarios"))
    if objetivo["id"] == usuario_actual()["id"]:
        flash("No puedes cambiar tu propio rol.", "error")
        return redirect(url_for("admin.usuarios"))

    execute("UPDATE usuarios SET rol_id = %s WHERE id = %s", (rol_id, usuario_id))
    registrar_bitacora(usuario_actual(), "Cambio de rol", "usuarios", usuario_id,
                       f"{objetivo['nombre']}: rol_id {objetivo['rol_id']} -> {rol_id}")
    flash(f"Rol de {objetivo['nombre']} actualizado.", "ok")
    return redirect(url_for("admin.usuarios"))


@bp.route("/usuarios/<int:usuario_id>/estado", methods=["POST"])
@solo_admin
def activar_desactivar(usuario_id):
    objetivo = query("SELECT * FROM usuarios WHERE id = %s", (usuario_id,), one=True)
    if not objetivo:
        flash("Usuario no encontrado.", "error")
        return redirect(url_for("admin.usuarios"))
    if objetivo["id"] == usuario_actual()["id"]:
        flash("No puedes desactivar tu propia cuenta.", "error")
        return redirect(url_for("admin.usuarios"))

    nuevo = 0 if objetivo["activo"] else 1
    execute("UPDATE usuarios SET activo = %s WHERE id = %s", (nuevo, usuario_id))
    registrar_bitacora(usuario_actual(), "Activacion/desactivacion de usuario", "usuarios",
                       usuario_id, f"{objetivo['nombre']}: activo {objetivo['activo']} -> {nuevo}")
    flash(f"Usuario {objetivo['nombre']} {'activado' if nuevo else 'desactivado'}.", "ok")
    return redirect(url_for("admin.usuarios"))


@bp.route("/usuarios/<int:usuario_id>/password", methods=["POST"])
@solo_admin
def reiniciar_password(usuario_id):
    objetivo = query("SELECT * FROM usuarios WHERE id = %s", (usuario_id,), one=True)
    if not objetivo:
        flash("Usuario no encontrado.", "error")
        return redirect(url_for("admin.usuarios"))

    nueva = secrets.token_urlsafe(8)
    execute("UPDATE usuarios SET password = %s WHERE id = %s",
            (hash_password(nueva), usuario_id))
    registrar_bitacora(usuario_actual(), "Reinicio de contrasena", "usuarios", usuario_id,
                       f"Contrasena nueva para {objetivo['nombre']}")
    flash(f"Contrasena de {objetivo['nombre']} reiniciada a: {nueva}", "ok")
    return redirect(url_for("admin.usuarios"))


@bp.route("/proyectos/nuevo", methods=["GET", "POST"])
@solo_admin
def nuevo_proyecto():
    if request.method == "POST":
        codigo = request.form["codigo"].strip().upper()
        nombre = request.form["nombre"].strip()
        if not codigo or not nombre:
            flash("Codigo y nombre son obligatorios.", "error")
            return redirect(url_for("admin.nuevo_proyecto"))
        if query("SELECT id FROM proyectos WHERE codigo = %s", (codigo,), one=True):
            flash(f"El codigo {codigo} ya existe.", "error")
            return redirect(url_for("admin.nuevo_proyecto"))

        nuevo_id, _ = execute(
            """INSERT INTO proyectos
               (codigo, nombre, descripcion, fecha_inicio, fecha_fin, presupuesto, creado_por)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (codigo, nombre, request.form.get("descripcion", ""),
             request.form.get("fecha_inicio") or None,
             request.form.get("fecha_fin") or None,
             request.form["presupuesto"] or 0, usuario_actual()["id"]),
        )
        registrar_bitacora(usuario_actual(), "Creacion de proyecto", "proyectos", nuevo_id,
                           f"{codigo} - {nombre}")
        flash(f"Proyecto {codigo} creado.", "ok")
        return redirect(url_for("main.proyectos"))
    return render_template("admin_proyecto_nuevo.html", usuario=usuario_actual(), es_admin=True)


@bp.route("/proyectos/<int:proyecto_id>/estado", methods=["POST"])
@solo_admin
def cambiar_estado_proyecto(proyecto_id):
    nuevo = request.form["estado"]
    if nuevo not in ("PLANIFICACION", "EN_CURSO", "PAUSADO", "FINALIZADO"):
        flash("Estado no valido.", "error")
        return redirect(url_for("main.proyectos"))
    p = query("SELECT * FROM proyectos WHERE id = %s", (proyecto_id,), one=True)
    execute("UPDATE proyectos SET estado = %s WHERE id = %s", (nuevo, proyecto_id))
    registrar_bitacora(usuario_actual(), "Cambio de estado de proyecto", "proyectos",
                       proyecto_id, f"{p['codigo']}: {p['estado']} -> {nuevo}")
    flash(f"Proyecto {p['codigo']} ahora esta {nuevo}.", "ok")
    return redirect(url_for("main.proyectos"))


@bp.route("/tareas/nueva", methods=["POST"])
@solo_admin
def nueva_tarea():
    proyecto_id = int(request.form["proyecto_id"])
    execute(
        """INSERT INTO tareas (proyecto_id, titulo, descripcion, asignado_a, prioridad, fecha_limite)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        (proyecto_id, request.form["titulo"].strip(), request.form.get("descripcion", ""),
         request.form.get("asignado_a") or None, request.form.get("prioridad", "MEDIA"),
         request.form.get("fecha_limite") or None),
    )
    registrar_bitacora(usuario_actual(), "Creacion de tarea", "tareas", None,
                       f"Tarea '{request.form['titulo']}' en proyecto {proyecto_id}")
    flash("Tarea creada.", "ok")
    return redirect(url_for("main.proyecto_detalle", proyecto_id=proyecto_id))


@bp.route("/bitacora")
@solo_admin
def bitacora():
    registros = query("SELECT * FROM bitacora ORDER BY id DESC LIMIT 100")
    return render_template("admin_bitacora.html", usuario=usuario_actual(), es_admin=True,
                           registros=registros)
