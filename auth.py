import functools
import hashlib

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from db import execute, query

bp = Blueprint("auth", __name__)


def usuario_actual():
    if "usuario" not in session:
        return None
    return query(
        """SELECT u.id, u.nombre, u.email, u.cargo, u.activo, r.nombre AS rol
           FROM usuarios u JOIN roles r ON r.id = u.rol_id
           WHERE u.id = %s""",
        (session["usuario"],),
        one=True,
    )


def es_admin():
    u = usuario_actual()
    return bool(u and u["rol"] == "ADMINISTRADOR")


def requiere_login(f):
    @functools.wraps(f)
    def envoltura(*args, **kwargs):
        if not usuario_actual():
            flash("Debes iniciar sesion para continuar.", "aviso")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)

    return envoltura


def requiere_admin(f):
    @functools.wraps(f)
    def envoltura(*args, **kwargs):
        if not usuario_actual():
            flash("Debes iniciar sesion para continuar.", "aviso")
            return redirect(url_for("auth.login"))
        if not es_admin():
            flash("Acceso restringido: se requiere rol ADMINISTRADOR.", "error")
            return redirect(url_for("main.dashboard"))
        return f(*args, **kwargs)

    return envoltura


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        usuario = query(
            """SELECT u.*, r.nombre AS rol FROM usuarios u
               JOIN roles r ON r.id = u.rol_id WHERE u.email = %s""",
            (email,),
            one=True,
        )
        if not usuario or hashlib.sha256(password.encode()).hexdigest() != usuario["password"]:
            flash("Correo o contrasena incorrectos.", "error")
        elif not usuario["activo"]:
            flash("Tu usuario esta inactivo. Contacta al administrador.", "error")
        else:
            session.clear()
            session["usuario"] = usuario["id"]
            flash(f"Bienvenido/a {usuario['nombre']} ({usuario['rol']}).", "ok")
            return redirect(url_for("main.dashboard"))
    return render_template("login.html")


@bp.route("/logout")
def logout():
    session.clear()
    flash("Sesion cerrada correctamente.", "ok")
    return redirect(url_for("auth.login"))
