# Guia de despliegue en VM Ubuntu (sin Docker)

Este es el procedimiento exacto que se debe evidenciar en la actividad.
Todo se ejecuta por SSH en una VM Ubuntu 22.04 con una IP publica.

---

## 0. Que se va a construir

```
Navegador  --HTTP-->  Apache2  --mod_wsgi-->  Python / Flask  -->  MySQL
```

- **Apache2** publica el sitio en el puerto 80.
- **mod_wsgi** conecta Apache con Python (no se usa Gunicorn ni Docker).
- **MySQL** guarda la base de datos `epm_db`.

---

## 1. Conectarse a la VM

```bash
ssh usuario@IP_DEL_SERVIDOR
# Example: ssh ubuntu@129.80.0.25
```

Captura de pantalla: terminal mostrando la conexion y el `hostname -I`.

---

## 2. Ejecucion automatizada (un solo comando)

El repositorio incluye el script `deploy/deploy.sh`, que instala todo, crea la base de datos,
descarga el codigo y configura Apache. Es la forma mas rapida y es la que demuestra el punto
**"Deploy con Script inicial en VM, sin Docker"**.

```bash
git clone https://github.com/TU_USUARIO/EPM.git
cd EPM
sudo nano deploy/deploy.sh      # cambiar REPO_URL
sudo bash deploy/deploy.sh
```

Capturas que hay que tomar:

1. Consola mostrando la ejecucion completa del script hasta `DESPLIEGUE COMPLETADO`.
2. `sudo systemctl status apache2` -&gt; `active (running)`.
3. `sudo systemctl status mysql` -&gt; `active (running)`.

---

## 3. Despliegue manual, paso a paso

Si el profesor pide el despliegue manual (sin script), estos son los comandos uno por uno.

### 3.1 Actualizar el sistema

```bash
sudo apt update
sudo apt upgrade -y
```

### 3.2 Instalar los servicios

```bash
sudo apt install -y apache2 mysql-server python3 python3-venv python3-pip git curl
sudo systemctl enable --now apache2
sudo systemctl enable --now mysql
```

Comprobar:

```bash
sudo systemctl status apache2
sudo systemctl status mysql
```

### 3.3 Crear la base de datos y el usuario

```bash
sudo mysql
```

```sql
CREATE DATABASE epm_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'epm_user'@'localhost' IDENTIFIED BY 'EpM_2026_Seguro';
GRANT ALL PRIVILEGES ON epm_db.* TO 'epm_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 3.4 Descargar el codigo desde el repositorio

```bash
sudo mkdir -p /var/www/epm
sudo chown -R www-data:www-data /var/www/epm
cd /var/www/epm
sudo -u www-data git clone https://github.com/TU_USUARIO/EPM.git .
ls -la
```

### 3.5 Entorno virtual y dependencias

```bash
cd /var/www/epm
sudo python3 -m venv venv
sudo venv/bin/pip install --upgrade pip
sudo venv/bin/pip install -r requirements.txt
sudo chown -R www-data:www-data /var/www/epm
```

### 3.6 Cargar el esquema de datos

```bash
sudo mysql -u root epm_db < /var/www/epm/schema.sql
sudo mysql -u root -e "USE epm_db; SHOW TABLES;"
```

### 3.7 Variables de entorno

```bash
sudo tee /var/www/epm/.env > /dev/null <<'EOF'
SECRET_KEY=cambia_esto_por_una_clave_aleatoria
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=epm_user
MYSQL_PASSWORD=EpM_2026_Seguro
MYSQL_DB=epm_db
EOF

sudo chmod 600 /var/www/epm/.env
sudo chown www-data:www-data /var/www/epm/.env
```

### 3.8 Instalar mod_wsgi

```bash
sudo apt install -y libapache2-mod-wsgi-py3
sudo a2enmod wsgi
```

### 3.9 Configurar el VirtualHost de Apache

```bash
sudo tee /etc/apache2/sites-available/epm.conf > /dev/null <<'EOF'
<VirtualHost *:80>
    ServerName _default
    DocumentRoot /var/www/epm/templates

    WSGIDaemonProcess epm user=www-data group=www-data threads=4
    WSGIScriptAlias / /var/www/epm/wsgi.py

    <Directory /var/www/epm>
        WSGIProcessGroup epm
        WSGIApplicationGroup %{GLOBAL}
        Require all granted
    </Directory>

    Alias /static/ /var/www/epm/static/
    <Directory /var/www/epm/static>
        Require all granted
    </Directory>

    ErrorLog  ${APACHE_LOG_DIR}/epm-error.log
    CustomLog ${APACHE_LOG_DIR}/epm-access.log combined
</VirtualHost>
EOF

sudo a2dissite 000-default
sudo a2ensite epm
sudo apache2ctl configtest
sudo systemctl restart apache2
```

### 3.10 Abrir el firewall

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw enable
sudo ufw status
```

---

## 4. Verificacion

Desde el navegador, en otra maquina:

```
http://IP_DEL_SERVIDOR
```

| Verificar | Como |
|---|---|
| La pagina carga | Pantalla de login de EPM |
| El servidor responde | `curl -I http://IP_DEL_SERVIDOR` desde la terminal |
| Apache sirve el trafico | `sudo tail -n 20 /var/log/apache2/epm-access.log` |
| La base de datos responde | `sudo mysql -u epm_user -p epm_db` |

---

## 5. Actualizar la aplicacion (redeploy)

```bash
cd /var/www/epm
sudo -u www-data git pull origin main
sudo systemctl restart apache2
```

---

## 6. Problemas frecuentes

| Sintoma | Causa | Solucion |
|---|---|---|
| `Internal Server Error` | Permisos o mod_wsgi | `sudo tail -n 50 /var/log/apache2/epm-error.log` |
| `Can't connect to MySQL` | MySQL detenido o puerto | `sudo systemctl status mysql` |
| `Access denied for user` | Contrasena del `.env` | Repetir el paso 3.7 con la misma contrasena |
| Cambia la IP del servidor | IP dinamica del proveedor | Crear una IP fija en el panel del proveedor |
| Cambia la contrasena de MySQL | `validate_password` activo | `SET PASSWORD VALIDATION_POLICY=LOW;` antes de crear el usuario |
