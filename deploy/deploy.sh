#!/usr/bin/env bash
# =============================================================
#  EPM - Enterprise Project Management
#  Despliegue automatizado en VM Ubuntu (sin Docker)
#  Servicio: Apache2 + mod_wsgi + Gunicorn + MySQL
# =============================================================
#  Uso:  sudo bash deploy.sh
# =============================================================

set -euo pipefail

# ---------- 1. VARIABLES DE CONFIGURACION ----------
DB_NAME="epm_db"
DB_USER="epm_user"
DB_PASS="EpM_2026_Seguro"
REPO_URL="https://github.com/TU_USUARIO/EPM.git"
APP_DIR="/var/www/epm"
APP_USER="www-data"
SECRET_KEY="$(head -c 48 /dev/urandom | base64)"

log()  { echo -e "\n\033[1;34m==> $1\033[0m"; }
ok()   { echo -e "    \033[1;32m[OK] $1\033[0m"; }
fail() { echo -e "    \033[1;31m[ERROR] $1\033[0m"; exit 1; }

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
    python3 python3-venv python3-pip \
    git curl ufw

systemctl enable --now apache2
systemctl enable --now mysql
ok "Apache y MySQL habilitados"

# ---------- 3. DESCARGAR CODIGO FUENTE DESDE EL REPO ----------
log "Paso 3/8  Descargando el codigo desde el repositorio"
if [ -d "$APP_DIR" ]; then
    rm -rf "$APP_DIR"
fi
mkdir -p "$APP_DIR"
git clone "$REPO_URL" "$APP_DIR"
chown -R "$APP_USER:$APP_USER" "$APP_DIR"
ok "Codigo descargado en $APP_DIR"

# ---------- 4. ENTORNO VIRTUAL Y DEPENDENCIAS ----------
log "Paso 4/8  Creando entorno virtual e instalando dependencias"
python3 -m venv "$APP_DIR/venv"
"$APP_DIR/venv/bin/pip" install --upgrade pip
"$APP_DIR/venv/bin/pip" install -r "$APP_DIR/requirements.txt"
ok "Dependencias instaladas"

# ---------- 5. BASE DE DATOS ----------
log "Paso 5/8  Creando la base de datos MySQL"
mysql -u root <<SQL
DROP DATABASE IF EXISTS ${DB_NAME};
CREATE DATABASE ${DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '${DB_USER}'@'localhost' IDENTIFIED BY '${DB_PASS}';
GRANT ALL PRIVILEGES ON ${DB_NAME}.* TO '${DB_USER}'@'localhost';
FLUSH PRIVILEGES;
SQL
ok "Base ${DB_NAME} y usuario ${DB_USER} creados"

log "Paso 6/8  Cargando el esquema y los datos"
mysql -u root "$DB_NAME" < "$APP_DIR/schema.sql"
mysql -u root <<SQL
CREATE USER IF NOT EXISTS '${DB_USER}'@'localhost' IDENTIFIED BY '${DB_PASS}';
GRANT ALL PRIVILEGES ON ${DB_NAME}.* TO '${DB_USER}'@'localhost';
FLUSH PRIVILEGES;
SQL
ok "Esquema cargado"

# ---------- 6. VARIABLES DE ENTORNO ----------
log "Paso 7/8  Configurando variables de entorno"
cat > "$APP_DIR/.env" <<ENV
SECRET_KEY=${SECRET_KEY}
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=${DB_USER}
MYSQL_PASSWORD=${DB_PASS}
MYSQL_DB=${DB_NAME}
ENV
chmod 600 "$APP_DIR/.env"
chown "$APP_USER:$APP_USER" "$APP_DIR/.env"
ok "Archivo .env creado (solo lectura para www-data)"

# ---------- 7. APACHE + WSGI ----------
log "Paso 8/8  Configurando Apache con mod_wsgi"
cat > /etc/apache2/sites-available/epm.conf <<APACHE
<VirtualHost *:80>
    ServerName _default
    DocumentRoot ${APP_DIR}/templates

    WSGIDaemonProcess epm user=${APP_USER} group=${APP_USER} threads=4
    WSGIScriptAlias / /var/www/epm/wsgi.py
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

    ErrorLog  ${APACHE_LOG_DIR}/epm-error.log
    CustomLog ${APACHE_LOG_DIR}/epm-access.log combined
</VirtualHost>
APACHE

# Cargar variables de entorno al arrancar Apache
mkdir -p /etc/apache2/conf-enabled
cat > /etc/apache2/conf-available/epm-env.conf <<ENVCONF
export SECRET_KEY=${SECRET_KEY}
export MYSQL_HOST=127.0.0.1
export MYSQL_PORT=3306
export MYSQL_USER=${DB_USER}
export MYSQL_PASSWORD=${DB_PASS}
export MYSQL_DB=${DB_NAME}
ENVCONF
a2enconf epm-env > /dev/null

a2dissite 000-default > /dev/null 2>&1 || true
a2ensite epm > /dev/null

if [ ! -f /etc/apache2/mods-available/wsgi.load ]; then
    apt install -y libapache2-mod-wsgi-py3
fi
a2enmod wsgi > /dev/null
systemctl restart apache2
ok "Apache configurado con mod_wsgi"

# ---------- 8. FIREWALL ----------
log "Abriendo puertos en el firewall"
ufw allow 22/tcp    > /dev/null
ufw allow 80/tcp    > /dev/null
ufw allow 'Apache Full' > /dev/null 2>&1 || true
ufw --force enable > /dev/null
ok "Puertos 22 (SSH) y 80 (HTTP) abiertos"

IP=$(hostname -I | awk '{print $1}')

echo ""
echo "============================================================"
echo "  DESPLIEGUE COMPLETADO SIN DOCKER"
echo "============================================================"
echo "  Aplicacion : http://${IP}"
echo "  Servidor   : Apache2 + mod_wsgi + Python"
echo "  Base datos : MySQL / ${DB_NAME}"
echo "  Usuario BD : ${DB_USER}"
echo ""
echo "  Cuentas de prueba:"
echo "    Administrador -> admin@epm.com / admin123"
echo "    Usuario       -> sara@epm.com  / admin123"
echo ""
echo "  Comandos utiles:"
echo "    sudo systemctl status apache2"
echo "    sudo tail -f /var/log/apache2/epm-error.log"
echo "    sudo mysql -u ${DB_USER} -p ${DB_NAME}"
echo "============================================================"
