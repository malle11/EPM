from flask import Flask, render_template

import admin
import auth
import routes
from config import Config
from db import close_db


def crear_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.teardown_appcontext(close_db)

    app.register_blueprint(auth.bp)
    app.register_blueprint(routes.bp)
    app.register_blueprint(admin.bp)

    @app.errorhandler(404)
    def no_encontrado(_e):
        return render_template("error.html", codigo=404,
                               mensaje="La pagina que buscas no existe."), 404

    return app


app = crear_app()
