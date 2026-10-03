#!/usr/bin/env bash
# =============================================================
#  EPM - Enterprise Project Management
#  Despliegue automatizado en VM Ubuntu (sin Docker)
#  Servicio: Apache2 + mod_wsgi + Python + MySQL
# =============================================================
#  Uso:
#    sudo bash deploy.sh                 # despliega / actualiza
#    RESET_DB=1 sudo bash deploy.sh      # ademas recrea la base
# =============================================================

set -euo pipefail

# ---------- 1. VARIABLES DE CONFIGURACION ----------
DB_NAME="epm_db"
DB_USER="epm_user"
REPO_URL="https://github.com/malle11/EPM.git"
APP_DIR="/var/www/epm"
APP_USER="www-data"
RESET_DB="${RESET_DB:-0}"

# Secretos: se generan al azar en cada ejecucion.
# Se pueden fijar por variable de entorno para despliegues repetibles.
DB_PASS="${DB_PASS:-$(head -c 24 /dev/urandom | base64 | tr -d '/+=')}"
SECRET_KEY="${SECRET_KEY:-$(head -c 48 /dev/urandom | base64)}"

log()  { echo -e "\n\033[1;34m==> $1\033[0m"; }
ok()   { echo -e "    \033[1;32m[OK] $1\033[0m"; }
info() { echo -e "    $1"; }
fail() { echo -e "    \033[1;31m[ERROR] $1\033[0m"; exit 1; }
trap 'echo -e "\n\033[1;31m[ERROR] El despliegue fallo en la linea $LINENO. Revisa el log.\033[0m"' ERR

[ "$(id -u)" -eq 0 ] || fail "Este script debe correrse como root: sudo bash deploy.sh"

# ---------- 2. ACTUALIZAR SISTEMA E INSTALAR PAQUETES ----------
log "Paso 1/8  Actualizando el sistema"
export DEBIAN_FRONTEND=noninteractive
apt update -y
apt upgrade -y

log "Paso 2/8  Instalando Apache, MySQL, Python y Git"
apt install -y \
    apache2 \
    mysql-server \
    libapache2-mod-wsgi-py3 \
    python3 python3-venv python3-pip \
    git curl ufw

systemctl enable --now apache2
systemctl enable --now mysql
ok "Apache y MySQL habilitados"

# ---------- 3. DESCARGAR CODIGO FUENTE DESDE EL REPO ----------
log "Paso 3/8  Obteniendo el codigo desde el repositorio"
if [ -d "$APP_DIR/.git" ]; then
    git -C "$APP_DIR" pull --ff-only
    ok "Codigo actualizado con git pull"
else
    if [ -d "$APP_DIR" ]; then rm -rf "$APP_DIR"; fi
    git clone "$REPO_URL" "$APP_DIR"
    ok "Repositorio clonado en $APP_DIR"
fi

# ---------- 4. ENTORNO VIRTUAL Y DEPENDENCIAS ----------
log "Paso 4/8  Creando entorno virtual e instalando dependencias"
[ -d "$APP_DIR/venv" ] || python3 -m venv "$APP_DIR/venv"
"$APP_DIR/venv/bin/pip" install --upgrade pip -q
"$APP_DIR/venv/bin/pip" install -r "$APP_DIR/requirements.txt" -q
ok "Dependencias instaladas"

# ---------- 5. BASE DE DATOS ----------
log "Paso 5/8  Configurando la base de datos MySQL"

DB_EXISTS=$(mysql -u root -N -B -e \
    "SELECT COUNT(*) FROM information_schema.schemata WHERE schema_name='${DB_NAME}';")

if [ "$DB_EXISTS" = "1" ] && [ "$RESET_DB" != "1" ]; then
    info "La base ${DB_NAME} ya existe: se conservan los datos (RESET_DB=1 para recrearla)"
else
    mysql -u root < "$APP_DIR/schema.sql"
    ok "Esquema y datos iniciales cargados"
fi

mysql -u root <<SQL
CREATE USER IF NOT EXISTS '${DB_USER}'@'localhost' IDENTIFIED BY '${DB_PASS}';
ALTER USER '${DB_USER}'@'localhost' IDENTIFIED BY '${DB_PASS}';
GRANT ALL PRIVILEGES ON ${DB_NAME}.* TO '${DB_USER}'@'localhost';
FLUSH PRIVILEGES;
SQL
ok "Usuario ${DB_USER} con permisos sobre ${DB_NAME}"

# ---------- 6. VARIABLES DE ENTORNO ----------
log "Paso 6/8  Escribiendo la configuracion en .env"
cat > "$APP_DIR/.env" <<ENV
SECRET_KEY=${SECRET_KEY}
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=${DB_USER}
MYSQL_PASSWORD=${DB_PASS}
MYSQL_DB=${DB_NAME}
ENV
chmod 640 "$APP_DIR/.env"
chown "$APP_USER:$APP_USER" "$APP_DIR/.env"
ok ".env creado con permisos 640 (config.py lo carga con python-dotenv)"

# ---------- 7. APACHE + WSGI ----------
log "Paso 7/8  Configurando Apache con mod_wsgi"
cat > /etc/apache2/sites-available/epm.conf <<APACHE
<VirtualHost *:80>
    ServerName _default
    DocumentRoot ${APP_DIR}/templates

    WSGIDaemonProcess epm user=${APP_USER} group=${APP_USER} threads=4
    WSGIScriptAlias / ${APP_DIR}/wsgi.py
    WSGIPassAuthorization On

    <Directory ${APP_DIR}>
        WSGIProcessGroup epm
        WSGIApplicationGroup %{GLOBAL}
        Require all granted
    </Directory>

    Alias /static/ ${APP_DIR}/static/
    <Directory ${APP_DIR}/static>
        Require all granted
    </Directory>

    ErrorLog  \${APACHE_LOG_DIR}/epm-error.log
    CustomLog \${APACHE_LOG_DIR}/epm-access.log combined
</VirtualHost>
APACHE

a2enmod wsgi > /dev/null
a2dissite 000-default > /dev/null 2>&1 || true
a2ensite epm > /dev/null

log "Paso 8/8  Validando la configuracion de Apache"
if ! apache2ctl configtest; then
    a2dissite epm > /dev/null 2>&1 || true
    a2ensite 000-default > /dev/null 2>&1 || true
    systemctl restart apache2
    fail "configtest fallo: se revirtio el sitio anterior. Apache no fue modificado."
fi
systemctl restart apache2
ok "Apache configurado con mod_wsgi"

# ---------- 8. FIREWALL ----------
log "Abriendo puertos en el firewall"
ufw allow 22/tcp > /dev/null
ufw allow 80/tcp > /dev/null
ufw --force enable > /dev/null
ok "Puertos 22 (SSH) y 80 (HTTP) abiertos"

# ---------- 9. COMPROBACION FINAL ----------
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1/login || echo 000)
[ "$HTTP_CODE" = "200" ] || fail "La app no responde 200 en /login (obtuvo ${HTTP_CODE}). Revisa /var/log/apache2/epm-error.log"

IP=$(hostname -I | awk '{print $1}')

echo ""
echo "============================================================"
echo "  DESPLIEGUE COMPLETADO SIN DOCKER"
echo "============================================================"
echo "  Aplicacion : http://${IP}"
echo "  Servidor   : Apache2 + mod_wsgi + Python (venv)"
echo "  Base datos : MySQL / ${DB_NAME}"
echo "  Usuario BD : ${DB_USER}"
echo "  Verificacion: HTTP 200 en /login"
echo ""
echo "  Cuentas de prueba:"
echo "    Administrador -> admin@epm.com / admin123"
echo "    Usuario       -> malle@epm.com  / admin123"
echo ""
echo -e "  \033[1;33m[AVISO] Cambia esas contrasenas si el servidor queda publico.\033[0m"
echo ""
echo "  La contrasena de MySQL quedo en: ${APP_DIR}/.env"
echo ""
echo "  Comandos utiles:"
echo "    sudo systemctl status apache2"
echo "    sudo tail -f /var/log/apache2/epm-error.log"
echo "    sudo mysql -u ${DB_USER} -p ${DB_NAME}"
echo "============================================================"