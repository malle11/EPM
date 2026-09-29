import hashlib

import mysql.connector
from flask import g
from mysql.connector import pooling

from config import Config

_pool = None


def get_pool():
    global _pool
    if _pool is None:
        _pool = pooling.MySQLConnectionPool(
            pool_name="epm_pool",
            pool_size=5,
            pool_reset_session=True,
            host=Config.MYSQL_HOST,
            port=Config.MYSQL_PORT,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB,
            charset="utf8mb4",
            autocommit=False,
        )
    return _pool


def get_db():
    if "db" not in g:
        g.db = get_pool().get_connection()
    return g.db


def close_db(_exc=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def query(sql, params=None, one=False):
    cur = get_db().cursor(dictionary=True)
    cur.execute(sql, params or ())
    rows = cur.fetchall()
    cur.close()
    return (rows[0] if rows else None) if one else rows


def execute(sql, params=None):
    db = get_db()
    cur = db.cursor()
    cur.execute(sql, params or ())
    id_insertado = cur.lastrowid
    filas = cur.rowcount
    cur.close()
    db.commit()
    return id_insertado, filas


def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def registrar_bitacora(usuario, accion, entidad, entidad_id=None, detalle=""):
    execute(
        """INSERT INTO bitacora (usuario_id, usuario, accion, entidad, entidad_id, detalle)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        (
            usuario["id"] if usuario else None,
            usuario["nombre"] if usuario else "sistema",
            accion,
            entidad,
            entidad_id,
            detalle,
        ),
    )
