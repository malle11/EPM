from datetime import date

from flask import Blueprint, flash, redirect, render_template, request, url_for

from auth import es_admin, requiere_login, usuario_actual
from db import execute, query, registrar_bitacora

bp = Blueprint("main", __name__)


@bp.route("/")
def inicio():
    return redirect(url_for("auth.login"))


@bp.route("/dashboard")
@requiere_login
def dashboard():
    u = usuario_actual()
    es_admin_actual = es_admin()

    resumen = query(
        """SELECT
             (SELECT COUNT(*) FROM proyectos)                          AS total_proyectos,
             (SELECT COUNT(*) FROM proyectos WHERE estado='EN_CURSO')   AS en_curso,
             (SELECT COUNT(*) FROM proyectos WHERE estado='FINALIZADO') AS finalizados,
             (SELECT COUNT(*) FROM tareas)                             AS total_tareas,
             (SELECT COUNT(*) FROM tareas WHERE estado='COMPLETADA')   AS tareas_ok,
             (SELECT COALESCE(SUM(presupuesto),0) FROM proyectos)      AS presupuesto_total,
             (SELECT COUNT(*) FROM usuarios WHERE activo = 1)          AS usuarios_activos""",
        one=True,
    )

    tareas = query(
        """SELECT t.*, p.nombre AS proyecto, u.nombre AS responsable
           FROM tareas t
           JOIN proyectos p ON p.id = t.proyecto_id
           LEFT JOIN usuarios u ON u.id = t.asignado_a
           WHERE (%s = 1 OR t.asignado_a = %s)
           ORDER BY FIELD(t.estado,'BLOQUEADA','EN_PROGRESO','PENDIENTE','COMPLETADA'),
                    FIELD(t.prioridad,'ALTA','MEDIA','BAJA')
           LIMIT 12""",
        (1 if es_admin_actual else 0, u["id"]),
    )

    indicadores = query(
        """SELECT i.nombre, i.meta, i.formula, p.nombre AS proyecto,
                  (SELECT COUNT(*) FROM tareas WHERE proyecto_id = p.id) AS total,
                  (SELECT COUNT(*) FROM tareas WHERE proyecto_id = p.id
                     AND estado='COMPLETADA') AS completadas
           FROM indicadores i JOIN proyectos p ON p.id = i.proyecto_id
           ORDER BY i.id"""
    )
    for ind in indicadores:
        ind["avance"] = round(ind["completadas"] / ind["total"] * 100, 1) if ind["total"] else 0

    return render_template(
        "dashboard.html", usuario=u, es_admin=es_admin_actual,
        resumen=resumen, tareas=tareas, indicadores=indicadores,
    )


@bp.route("/proyectos")
@requiere_login
def proyectos():
    lista = query(
        """SELECT p.*, u.nombre AS autor,
                  (SELECT COUNT(*) FROM tareas WHERE proyecto_id = p.id) AS total_tareas,
                  (SELECT COUNT(*) FROM tareas WHERE proyecto_id = p.id
                     AND estado='COMPLETADA') AS tareas_ok
           FROM proyectos p JOIN usuarios u ON u.id = p.creado_por
           ORDER BY p.id DESC"""
    )
    for p in lista:
        p["avance"] = round(p["tareas_ok"] / p["total_tareas"] * 100) if p["total_tareas"] else 0
    return render_template("proyectos.html", usuario=usuario_actual(), es_admin=es_admin(),
                           proyectos=lista, hoy=date.today())


@bp.route("/proyectos/<int:proyecto_id>")
@requiere_login
def proyecto_detalle(proyecto_id):
    p = query(
        """SELECT p.*, u.nombre AS autor FROM proyectos p
           JOIN usuarios u ON u.id = p.creado_por WHERE p.id = %s""",
        (proyecto_id,),
        one=True,
    )
    if not p:
        flash("El proyecto no existe.", "error")
        return redirect(url_for("main.proyectos"))

    tareas = query(
        """SELECT t.*, u.nombre AS responsable FROM tareas t
           LEFT JOIN usuarios u ON u.id = t.asignado_a
           WHERE t.proyecto_id = %s ORDER BY t.id DESC""",
        (proyecto_id,),
    )
    return render_template("proyecto_detalle.html", usuario=usuario_actual(), es_admin=es_admin(),
                           p=p, tareas=tareas,
                           usuarios=query("SELECT id, nombre FROM usuarios WHERE activo = 1"))


@bp.route("/tareas/<int:tarea_id>/estado", methods=["POST"])
@requiere_login
def cambiar_estado(tarea_id):
    tarea = query("SELECT * FROM tareas WHERE id = %s", (tarea_id,), one=True)
    if not tarea:
        flash("La tarea no existe.", "error")
        return redirect(url_for("main.dashboard"))

    nuevo = request.form["estado"]
    validos = ("PENDIENTE", "EN_PROGRESO", "BLOQUEADA", "COMPLETADA")
    if nuevo not in validos:
        flash("Estado no valido.", "error")
        return redirect(url_for("main.dashboard"))

    if not es_admin() and tarea["asignado_a"] != usuario_actual()["id"]:
        flash("Solo puedes cambiar el estado de tus propias tareas.", "error")
        return redirect(url_for("main.dashboard"))

    execute("UPDATE tareas SET estado = %s WHERE id = %s", (nuevo, tarea_id))
    registrar_bitacora(usuario_actual(), "Cambio de estado de tarea", "tareas", tarea_id,
                       f"{tarea['titulo']}: {tarea['estado']} -> {nuevo}")
    flash("Estado de la tarea actualizado.", "ok")
    return redirect(request.referrer or url_for("main.dashboard"))
