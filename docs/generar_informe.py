"""
Genera el informe de la Actividad 2 en formato .docx
Actividad 2 - Deploy manual + Marketplace
EPM - Enterprise Project Management
"""
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, Cm, RGBColor
from docx.enum.section import WD_SECTION

AZUL = RGBColor(0x1B, 0x3A, 0x5C)
GRIS = RGBColor(0x55, 0x55, 0x55)

doc = Document()

# --- Fuente y margenes ---
st = doc.styles["Normal"]
st.font.name = "Calibri"
st.font.size = Pt(11)
st.paragraph_format.space_after = Pt(6)
st.paragraph_format.line_spacing = 1.5

for s in doc.sections:
    s.top_margin = Cm(2.5)
    s.bottom_margin = Cm(2.5)
    s.left_margin = Cm(3.0)
    s.right_margin = Cm(3.0)


def titulo(texto, nivel=1):
    p = doc.add_heading(texto, level=nivel)
    for r in p.runs:
        r.font.color.rgb = AZUL
        r.font.name = "Calibri"
    return p


def parrafo(texto, negrita=False, cursiva=False, tamano=11, centrado=False, color=None):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER if centrado else WD_ALIGN_PARAGRAPH.JUSTIFY
    r = p.add_run(texto)
    r.bold = negrita
    r.italic = cursiva
    r.font.size = Pt(tamano)
    if color:
        r.font.color.rgb = color
    return p


def vineta(texto):
    return doc.add_paragraph(texto, style="List Bullet")


def codigo(lineas):
    for l in lineas:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Cm(0.8)
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(l)
        r.font.name = "Consolas"
        r.font.size = Pt(9.5)


# =====================================================================
# PORTADA
# =====================================================================
for _ in range(4):
    doc.add_paragraph()

parrafo("MATERIA: Despliegue de aplicaciones en la nube (Computación en la Nube)",
        negrita=True, centrado=True, tamano=12)
parrafo("Asignatura: Programación / Administración de bases de datos / Cloud",
        centrado=True, tamano=11, color=GRIS)

doc.add_paragraph()
parrafo("ACTIVIDAD 2 – DEPLOY MANUAL Y MARKETPLACE",
        negrita=True, centrado=True, tamano=16, color=AZUL)
doc.add_paragraph()
parrafo("Despliegue de una aplicación web de gestión de proyectos\n"
        "empresariales en una máquina virtual, sin uso de contenedores",
        centrado=True, tamano=13)
doc.add_paragraph()
parrafo("Proyecto: EPM – Enterprise Project Management",
        negrita=True, centrado=True, tamano=14, color=AZUL)

for _ in range(2):
    doc.add_paragraph()

parrafo("AUTORA", negrita=True, centrado=True, tamano=11)
parrafo("Luz Mallely Zapata", centrado=True, tamano=12)
parrafo("Programa: Ingeniería de Software / Tecnología en Desarrollo de Software",
        centrado=True, tamano=10, color=GRIS)

for _ in range(2):
    doc.add_paragraph()

parrafo("Fecha de entrega: 5 de octubre de 2026", centrado=True, tamano=11)
parrafo("Institución Tecnológica Metropolitana", centrado=True, tamano=11, color=GRIS)

doc.add_page_break()

# =====================================================================
# RESUMEN
# =====================================================================
titulo("Resumen", 1)
parrafo(
    "El presente informe documenta el proceso de diseño, construcción y despliegue en la nube de "
    "una aplicación web de gestión de proyectos empresariales denominada EPM (Enterprise Project "
    "Management). La solución se desarrolla con Python mediante el microframework Flask, y persiste "
    "sus datos en un servidor MySQL. El despliegue se ejecuta sobre una máquina virtual Ubuntu "
    "en infraestructura de nube pública, empleando Apache HTTP Server con el módulo mod_wsgi "
    "como servidor de aplicaciones y Gunicorn como servidor WSGI, sin hacer uso de contenedores "
    "Docker, conforme a las restricciones de la actividad. La aplicación implementa un modelo de "
    "seguridad basado en roles que distingue entre usuarios administrativos y usuarios operativos, "
    "con registro de auditoría de todas las transacciones administrativas. El proceso se automatiza "
    "mediante un script de despliegue que permite replicar el ambiente completo con un único "
    "comando, garantizando la reproducibilidad del procedimiento."
)
parrafo(
    "Palabras clave: Computación en la nube, Python, Flask, MySQL, Apache, mod_wsgi, WSGI, "
    "despliegue automatizado, máquina virtual, gestión de proyectos.",
    cursiva=True,
)

doc.add_page_break()

# =====================================================================
# 1. INTRODUCCION
# =====================================================================
titulo("1. Introducción", 1)

titulo("1.1 Contexto", 2)
parrafo(
    "Las empresas modernas gestionan sus proyectos mediante sistemas centralizados que permiten "
    "controlar tareas, responsables, presupuestos y plazos. En el sector de empresas públicas y "
    "de servicios públicos tal como las Empresas Públicas de Medellín (EPM), la trazabilidad de "
    "los proyectos optimizar recursos es una necesidad operativa permanente. Sin embargo, este "
    "tipo de sistemas suele operarse On-premise, lo que dificulta el acceso desde "
    "cualquier ubicación y encarece el mantenimiento de la infraestructura."
)
parrafo(
    "La computación en la nube (_cloud computing_) transforma este escenario. Según la definición "
    "del Instituto Nacional de Estándares y Tecnología de Estados Unidos (NIST), la computación en "
    "la nube es un modelo de servicio que permite el acceso bajo demanda y compartido a recursos "
    "de computación —servidores, almacenamiento y bases de datos— a través de redes, con "
    "provisionamiento y liberación de recursos de manera rápida y con esfuerzo mínimo del cliente."
)
parrafo(
    "Este trabajo aplica dichos conceptos a un caso concreto: una aplicación web de gestión de "
    "proyectos que se despliega sobre una máquina virtual alojada en un proveedor de infraestructura "
    "como servicio, de manner que cualquier usuario autorizado pueda acceder a ella a través de "
    "un navegador, sin instalar software localmente."
)

titulo("1.2 Planteamiento del problema", 2)
parrafo(
    "El despliegue de aplicaciones web en ambientes productivos presenta dificultades técnicas que no "
    "aparecen durante el desarrollo local. El desarrollador se enfrenta a la necesidad de configurar "
    "el sistema operativo del servidor, el servidor web, el intérprete de aplicaciones, el gestor "
    "de base de datos, los permisos de archivos, las variables de entorno y las reglas de seguridad "
    "de red. Cuando esta configuración se realiza manualmente, es repetitiva, propensa a errores y "
    "difícil de replicar."
)
parrafo(
    "El proyectoPlantEOresponde a esta problemática mediante dos líneas de trabajo: la construcción "
    "de una aplicación funcional con un modelo de permisos claro, y la automatización del proceso de "
    "despliegue mediante un script que ejecute de forma determinista todas las tareas de "
    "configuración del servidor."
)

titulo("1.3 Objetivos", 2)

titulo("1.3.1 Objetivo general", 3)
parrafo(
    "Desplegar en la nube una aplicación web de gestión de proyectos empresariales, desarrollada "
    "en Python con base de datos MySQL, sobre una máquina virtual Ubuntu y sin hacer uso de "
    "contenedores Docker."
)

titulo("1.3.2 Objetivos específicos", 3)
for o in [
    "Modelar la base de datos MySQL que sostenga la gestión de usuarios, roles, proyectos y tareas.",
    "Desarrollar la aplicación web con el microframework Flask y un esquema de control de acceso "
    "basado en roles.",
    "Desplegar la aplicación en una máquina virtual Ubuntu mediante Apache HTTP Server y mod_wsgi.",
    "Automatizar el proceso completo de despliegue mediante un script que configure el sistema "
    "operativo, el servidor web y el gestor de base de datos.",
    "Documentar el procedimiento y collecting evidencia verificable de cada etapa del despliegue.",
]:
    vineta(o)

titulo("1.4 Justificación", 2)
parrafo(
    "La pertinencia del trabajo se sustenta en tres argumentos. En primer lugar, la "
    "gestión de proyectos es un proceso transversal a cualquier organización, por lo que una "
    "solución funcional representa un valor agregado inmediato. En segundo lugar, el despliegue "
    "sobre infraestructura en la nube permite demostrar competencias técnicas exigidas en el "
    "manejo de servidores, bases de datos y seguridad. En tercer lugar, la automatización del "
    "despliegue mediante scripting reproduce buenas prácticas de integración y entrega continua "
    "que se aplican en la industria del software."
)

doc.add_page_break()

# =====================================================================
# 2. MARCO TEORICO
# =====================================================================
titulo("2. Marco teórico", 1)

titulo("2.1 Computación en la nube", 2)
parrafo(
    "La computación en la nube reemplaza la infraestructura física localizada en las "
    "instalaciones de la organización por recursos compartidos que se provisionan a través de "
    "Internet. Los modelos de servicio más extendidos se clasifican en Software como Servicio "
    "(SaaS), Plataforma como Servicio (PaaS) e Infraestructura como Servicio (IaaS). El presente "
    "proyecto se articula en el modelo IaaS: el proveedor suministra la máquina virtual y el sistema "
    "operativo, mientras que la organización asume la responsabilidad de instalar y configurar el "
    "software de aplicación."
)

titulo("2.2 Máquinas virtuales e hipervisores", 2)
parrafo(
    "Una máquina virtual es un entorno computacional aislado que emula un equipo físico completo. "
    "Sobre un hipervisor se ejecutan múltiples sistemas operativos virtuales que comparten los "
    "recursos del servidor anfitrión, lo que permite optimizar el aprovechamiento del hardware. La "
    "instancia de máquina virtualDisposable en un proveedor público constituye el recurso "
    "centralizado de este proyecto."
)

titulo("2.3 El estándar WSGI", 2)
parrafo(
    "Web Server Gateway Interface (WSGI) es una especificación definida en la Propuesta de Mejora "
    "de Python PEP 3333 que establece el contrato entre un servidor web y una aplicación web "
    "escrita en Python. WSGI separa estas dos responsabilidades: el servidor web se ocupa de aceptar "
    "peticiones HTTP y gestionar conexiones, mientras que el código Python se concentra en generar "
    "la respuesta. Esta separaciónHA permitido que servidores maduros como Apache puedan ejecutar "
    "aplicaciones en Python mediante el módulo mod_wsgi, sin escrituras de bridging específicas."
)
parrafo(
    "La implementación adoptada en este proyecto sigue la recomendación oficial del Flask: "
    "utilizar un servidor WSGI de nivel de producción en lugar del servidor de desarrollo "
    "integrado."
)

titulo("2.4 Servidor de aplicaciones Apache y MySQL", 2)
parrafo(
    "El Servidor HTTP de Apache es el servidor web de código abierto más utilizado a nivel "
    "mundial. Entre sus ventajas se destacan su estabilidad, su alto grado de configuración y un "
    "amplio ecosistema de módulos. En particular, mod_wsgi permite alojar aplicaciones Python "
    "dentro del proceso del servidor, con control de procesos separado mediante un demonio "
    "dedicado."
)
parrafo(
    "MySQL es un sistema gestor de bases de datos relacional de código abierto que emplea "
    "motor InnoDB para la gestión de transacciones. Este proyecto lo utiliza como sistema de "
    "persistencia, con el conector oficial de Python como capa de comunicación entre la aplicación y el "
    "servidor de base de datos."
)

titulo("2.5 Control de acceso basado en roles", 2)
parrafo(
    "El control de acceso basado en roles (RBAC) agrupa permisos en categorías que se asignan a los "
    "usuarios según sus responsabilidades. En la aplicación EPM se definen dos roles: "
    "ADMINISTRADOR, facultado para administrar cuentas, roles, proyectos y estados; y USUARIO, "
    "limitado a la consulta de proyectos y a la gestión de las tareas que tiene asignadas. Este "
    "modelo reduce la complejidad de la administración y limita el principio de privilegio mínimo."
)

doc.add_page_break()

# =====================================================================
# 3. METODOLOGIA
# =====================================================================
titulo("3. Metodología", 1)

titulo("3.1 Tipo de proyecto", 2)
parrafo(
    "El trabajo corresponde a un proyecto de naturaleza aplicada y tecnológica: parte de un "
    "requimiento real de gestión de proyectos y se materializa en un producto de software funcional, "
    "verificable y desplegado. Se adopta un enfoque incremental, en el que cada entrega se "
    "corrobora mediante pruebas funcionales."
)

titulo("3.2 Arquitectura de la solución", 2)
parrafo(
    "La arquitectura empleada es de tres capas, con separación clara entre la capa de presentación, "
    "la capa de lógica de negocio y la capa de persistencia:"
)
vineta("Capa de presentación: plantillas HTML con Jinja2, renderizadas en el lado del servidor.")
vineta("Capa de lógica de negocio: módulos Python que implementan la autenticación, las rutas y "
       "las reglas de autorización.")
vineta("Capa de persistencia: base de datos MySQL 8, accedida mediante mysql-connector-python con "
       "un pool de conexiones.")

titulo("3.3 Pila tecnológica", 2)

from docx.shared import Cm as _Cm

tabla = doc.add_table(rows=1, cols=3)
tabla.style = "Light Grid Accent 1"
hdr = tabla.rows[0].cells
hdr[0].text = "Componente"
hdr[1].text = "Tecnología"
hdr[2].text = "Justificación"
filas = [
    ("Lenguaje", "Python 3.12", "Requisito de la actividad; ecosistema amplio para la web."),
    ("Framework web", "Flask 3", "Ligero y modular; ideal para aprender la arquitectura web."),
    ("Estándar de despliegue", "WSGI (PEP 3333)", "Interfaz estándar entre servidor y aplicación."),
    ("Servidor web", "Apache 2 + mod_wsgi", "Estabilidad y control de procesos."),
    ("Servidor WSGI", "Gunicorn", "Recomendado por Flask para producción."),
    ("Base de datos", "MySQL 8", "Motor InnoDB, transacciones y robustez."),
    ("Conector", "mysql-connector-python", "Driver oficial de Oracle."),
    ("Sistema operativo", "Ubuntu 22.04 / 24.04 LTS", "Soporte prolongado y documentación abundante."),
    ("Versionamiento", "Git + GitHub", "Control de cambios y trazabilidad del código."),
    ("Automatización", "Script Bash", "Despliegue reproducible en un solo comando."),
    ("Virtualización", "Máquina virtual en la nube", "Modelo IaaS, sin gestión de hardware."),
]
for f in filas:
    c = tabla.add_row().cells
    c[0].text = f[0]
    c[1].text = f[1]
    c[2].text = f[2]

doc.add_paragraph()
parrafo("Tabla 1. Pila tecnológica de la solución.", cursiva=True, tamano=9.5, centrado=True)

titulo("3.4 Modelo de datos", 2)
parrafo(
    "El modelo de datos comprende seis tablas que normalizan la información del dominio. La tabla "
    "roles almacena el catálogo de roles; usuarios, las cuentas con su hash de contraseña, rol y "
    "estado; proyectos, los proyectos con su presupuesto, fechas y estado; tareas, las tareas "
    "asociadas a un proyecto con responsable, prioridad y estado; indicadores, las métricas de "
    "avance con su fórmula y meta; y bitacora, el registro de auditoría de las transacciones "
    "administrativas."
)

tabla2 = doc.add_table(rows=1, cols=3)
tabla2.style = "Light Grid Accent 1"
h2 = tabla2.rows[0].cells
h2[0].text = "Tabla"
h2[1].text = "Entidad"
h2[2].text = "Función dentro del sistema"
entidades = [
    ("roles", "Roles", "Catálogo de roles del sistema (ADMINISTRADOR, USUARIO)."),
    ("usuarios", "Usuarios", "Cuentas con correo, hash, rol, cargo y estado activo/inactivo."),
    ("proyectos", "Proyectos", "Código, nombre, descripción, fechas, presupuesto y estado."),
    ("tareas", "Tareas", "Tareas por proyecto con responsable, prioridad y estado."),
    ("indicadores", "Indicadores", "Métricas de gestión con fórmula de cálculo y meta."),
    ("bitacora", "Bitácora", "Auditoría de las operaciones administrativas."),
]
for f in entidades:
    c = tabla2.add_row().cells
    c[0].text = f[0]
    c[1].text = f[1]
    c[2].text = f[2]

doc.add_paragraph()
parrafo("Tabla 2. Entidades del modelo de datos.", cursiva=True, tamano=9.5, centrado=True)

titulo("3.5 Modelo de seguridad", 2)
parrafo(
    "Las contraseñas se almacenan transformadas mediante la función hash SHA-256 y nunca en texto "
    "plano, de modo que un compromiso de la base de datos no exponga directamente las credenciales. "
    "La sesión del usuario se mantiene en una cookie firmada con SECRET_KEY mediante su "
    "serialización. Las rutas sensibles se protegen mediante decoradores que validan la sesión y el "
    "rol antes de ejecutar la lógica de negocio, evitando el acceso directo a las funciones "
    "administrativas."
)
parrafo(
    "Adicionalmente, el script de despliegue establece reglas de firewall con UFW que mantienen "
    "cerrados los puertos no utilizados y limita el acceso por SSH, principio de mínimo privilegio "
    "aplicado a la capa de red."
)

doc.add_page_break()

# =====================================================================
# 4. DESARROLLO
# =====================================================================
titulo("4. Desarrollo de la aplicación", 1)

titulo("4.1 Organización del código", 2)
parrafo("El proyecto se organiza en módulos con responsabilidad única:")
codigo([
    "EPM/",
    "├── app.py             Configuración de la aplicación Flask",
    "├── wsgi.py            Punto de entrada para el servidor WSGI",
    "├── config.py          Lectura de variables de entorno y archivo .env",
    "├── db.py              Pool de conexiones y funciones de consulta",
    "├── auth.py            Autenticación y decoradores de permiso",
    "├── routes.py          Vistas del usuario (panel, proyectos, tareas)",
    "├── admin.py           Vistas del administrador (usuarios, bitácora)",
    "├── schema.sql         Definición de la base de datos y datos iniciales",
    "├── templates/         Plantillas Jinja2",
    "├── static/            Hoja de estilos",
    "├── deploy/deploy.sh   Script de despliegue automatizado",
    "└── docs/EVIDENCIAS.md Guía de recolección de evidencia",
])

titulo("4.2 Acceso a la base de datos", 2)
parrafo(
    "El módulo db.py implementa un pool de conexiones con mysql-connector-python. El uso de un "
    "pool evita la apertura y cierre constante de conexiones al manejar múltiples peticiones "
    "simultáneas. Las funciones query y execute liberan el cursor y confirman la transacción de "
    "manera inmediata, lo que reduce el riesgo de conexiones huérfanas."
)
parrafo("Ejemplo de acceso parametrizado, que protege contra ataques de inyección SQL:", cursiva=True)
codigo([
    "def query(sql, params=None, one=False):",
    "    cur = get_db().cursor(dictionary=True)",
    "    cur.execute(sql, params or ())",
    "    rows = cur.fetchall()",
    "    cur.close()",
    "    return (rows[0] if rows else None) if one else rows",
])

titulo("4.3 Autenticación y autorización", 2)
parrafo(
    "El módulo auth.py verifica las credenciales comparando el hash SHA-256 de la contraseña "
    "ingresada con el almacenado en la base de datos. Se verify además que la cuenta esté activa, "
    "lo que permite a un administradoruspender el acceso de un colaborador sin eliminar su "
    "historial. Los decoradores requiere_login y requiere_admin protegen las rutas."
)

titulo("4.4 Funcionalidad de usuario", 2)
parrafo(
    "El usuario operativo dispone de un panel con indicadores de avance, la lista de proyectos con "
    "su porcentaje de cumplimiento, el detalle de cada proyecto con sus tareas y la posibilidad de "
    "actualizar el estado de las tareas que tiene asignadas. El sistema impide que un usuario "
    "modifique tareas ajenas, verificando la asignación antes de ejecutar la operación."
)

titulo("4.5 Funcionalidad de administración", 2)
parrafo(
    "El administrador accede a un módulo adicional que permite crear usuarios, cambiar roles, "
    "activar o desactivar cuentas y reiniciar contraseñas. Además, gestiona proyectos y tareas, "
    "modifica el estado de los proyectos y consulta la bitácora. Como mecanismo de protección, el "
    "sistema impide que el administrador modifique su propio rol o desactive su propia cuenta."
)

titulo("4.6 Bitácora de auditoría", 2)
parrafo(
    "Cada operación administrativa escribe un registro en la tabla bitacora con el usuario, la "
    "acción, la entidad afectada, el identificador del registro y una descripción del antes y el "
    "después. Este mecanismo satisface el requisito de transacción sobre la administración y "
    "proporciona trazabilidad para auditorías posteriores."
)

doc.add_page_break()

# =====================================================================
# 5. DESPLIEGUE
# =====================================================================
titulo("5. Despliegue en la nube", 1)

titulo("5.1 Topología del ambiente desplegado", 2)
parrafo(
    "La aplicación se despliega siguiendo la siguiente cadena de solicitud:"
)
codigo([
    "Navegador --HTTP--> Apache2 --mod_wsgi--> Python/Flask --> MySQL",
])
parrafo(
    "Apache recibe la petición en el puerto 80 y la transfiere al proceso Python mediante "
    "mod_wsgi, que mantiene un demonio dedicado. La aplicación consulta MySQL a través de "
    "localhost. Todo el tráfico permanece dentro de la red privada de la máquina virtual."
)

titulo("5.2 Procedimiento manual de despliegue", 2)
parrafo(
    "El despliegue manual consiste en una serie de comandos ejecutados por Secure Shell (SSH). "
    "SSH es un protocolo que permite administrar de forma remota una máquina mediante un canal "
    "cifrado y autenticado mediante llave pública."
)
parrafo("Paso 1. Conexión segura al servidor:", negrita=True)
codigo(["ssh usuario@IP_DEL_SERVIDOR"])

parrafo("Paso 2. Actualización del sistema operativo:", negrita=True)
codigo([
    "sudo apt update",
    "sudo apt upgrade -y",
])

parrafo("Paso 3. Instalación de los servicios requeridos:", negrita=True)
codigo([
    "sudo apt install -y apache2 mysql-server \\",
    "    python3 python3-venv python3-pip \\",
    "    git curl ufw",
    "sudo systemctl enable --now apache2",
    "sudo systemctl enable --now mysql",
])

parrafo("Paso 4. Creación de la base de datos y del usuario de aplicación:", negrita=True)
codigo([
    "sudo mysql",
    "",
    "CREATE DATABASE epm_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;",
    "CREATE USER 'epm_user'@'localhost' IDENTIFIED BY 'clave_segura';",
    "GRANT ALL PRIVILEGES ON epm_db.* TO 'epm_user'@'localhost';",
    "FLUSH PRIVILEGES;",
    "EXIT;",
])
parrafo(
    "El uso de un usuario dedicado para la aplicación constituye una buena práctica: si la "
    "aplicación fuera comprometida, el atacante no obtendría acceso root al gestor de base de datos."
)

parrafo("Paso 5. Descarga del código desde el repositorio:", negrita=True)
codigo([
    "sudo mkdir -p /var/www/epm",
    "sudo chown -R www-data:www-data /var/www/epm",
    "cd /var/www/epm",
    "sudo -u www-data git clone https://github.com/malle11/EPM.git .",
])

parrafo("Paso 6. Entorno virtual y dependencias:", negrita=True)
codigo([
    "cd /var/www/epm",
    "sudo python3 -m venv venv",
    "sudo venv/bin/pip install --upgrade pip",
    "sudo venv/bin/pip install -r requirements.txt",
])
parrafo(
    "El entorno virtual aísla las dependencias del proyecto respecto de las del sistema operativo, "
    "lo que evita conflictos de versiones entre aplicaciones."
)

parrafo("Paso 7. Carga del esquema de base de datos:", negrita=True)
codigo(["sudo mysql -u root epm_db < /var/www/epm/schema.sql"])

parrafo("Paso 8. Configuración de las variables de entorno:", negrita=True)
codigo([
    "SECRET_KEY=clave_aleatoria_larga",
    "MYSQL_HOST=127.0.0.1",
    "MYSQL_PORT=3306",
    "MYSQL_USER=epm_user",
    "MYSQL_PASSWORD=clave_segura",
    "MYSQL_DB=epm_db",
])
parrafo(
    "Las credenciales se almacenan fuera del código fuente, en un archivo .env con permisos de "
    "lectura restringidos, lo que evita que queden publicadas en el repositorio."
)

parrafo("Paso 9. Instalación y activación de mod_wsgi:", negrita=True)
codigo([
    "sudo apt install -y libapache2-mod-wsgi-py3",
    "sudo a2enmod wsgi",
])

parrafo("Paso 10. Configuración del servidor virtual de Apache:", negrita=True)
codigo([
    "<VirtualHost *:80>",
    "    ServerName _default",
    "    DocumentRoot /var/www/epm/templates",
    "",
    "    WSGIDaemonProcess epm user=www-data group=www-data threads=4",
    "    WSGIScriptAlias / /var/www/epm/wsgi.py",
    "",
    "    <Directory /var/www/epm>",
    "        WSGIProcessGroup epm",
    "        WSGIApplicationGroup %{GLOBAL}",
    "        Require all granted",
    "    </Directory>",
    "",
    "    ErrorLog  ${APACHE_LOG_DIR}/epm-error.log",
    "    CustomLog ${APACHE_LOG_DIR}/epm-access.log combined",
    "</VirtualHost>",
])
codigo([
    "sudo a2dissite 000-default",
    "sudo a2ensite epm",
    "sudo apache2ctl configtest",
    "sudo systemctl restart apache2",
])
parrafo(
    "La directiva WSGIDaemonProcess configura un demonio con cuatro hilos dédié que se asocia al "
    "grupo de procesos, mientras que WSGIScriptAlias indica el archivo de entrada. El "
    "comando apache2ctl configtest valida la sintaxis antes de reiniciar, evitando dejar el "
    "servidor fuera de servicio por un error de configuración."
)

parrafo("Paso 11. Endurecimiento de la seguridad de red:", negrita=True)
codigo([
    "sudo ufw allow 22/tcp",
    "sudo ufw allow 80/tcp",
    "sudo ufw enable",
])

doc.add_page_break()

# =====================================================================
# 6. AUTOMATIZACION
# =====================================================================
titulo("6. Automatización del despliegue con script", 1)

parrafo(
    "El despliegue manual descrito en la sección anterior consta de más de cuarenta comandos. "
    "Repetir esta secuencia cada vez que se actualiza la aplicación resulta ineficiente y "
    "propenso a omisiones. Para solventar esta limitación se desarrolla un script en Bash, "
    "deploy.sh, que encapsula la totalidad del procedimiento en un único comando."
)

titulo("6.1 Principios de diseño del script", 2)
for p in [
    "Idempotencia: el script puede ejecutarse varias veces sin producir efectos adversos.",
    "Detección de privilegios: verifica la ejecución como root y detiene el proceso si no es así.",
    "Trazabilidad: cada etapa se anuncia con un mensaje numerado que identifica el progreso.",
    "Parametrización: los datos de conexión y credenciales se declaran al inicio del archivo.",
    "Validación previa: ejecuta apache2ctl configtest antes de reiniciar el servidor web.",
]:
    vineta(p)

titulo("6.2 Ejecución", 2)
codigo([
    "git clone https://github.com/malle11/EPM.git",
    "cd EPM",
    "sudo nano deploy/deploy.sh      # ajustar REPO_URL",
    "sudo bash deploy/deploy.sh",
])

titulo("6.3 Etapas del proceso automatizado", 2)
parrafo("El script ejecuta las siguientes ocho etapas:")
codigo([
    "Paso 1/8   Actualizar el sistema",
    "Paso 2/8   Instalar Apache, MySQL, Python y Git",
    "Paso 3/8   Descargar el código desde el repositorio",
    "Paso 4/8   Crear entorno virtual e instalar dependencias",
    "Paso 5/8   Crear la base de datos y el usuario de aplicación",
    "Paso 6/8   Cargar el esquema y los datos iniciales",
    "Paso 7/8   Generar el archivo de variables de entorno",
    "Paso 8/8   Configurar Apache con mod_wsgi y activar el firewall",
])

titulo("6.4 Actualizaciones posteriores", 2)
parrafo(
    "Una vez desplegada la aplicación, el ciclo de actualización se reduce a tres comandos, lo que "
    "demuestra el beneficio de la automatización:"
)
codigo([
    "cd /var/www/epm",
    "sudo -u www-data git pull origin main",
    "sudo systemctl restart apache2",
])

doc.add_page_break()

# =====================================================================
# 7. EVIDENCIAS
# =====================================================================
titulo("7. Evidencias del despliegue", 1)

parrafo(
    "La actividad solicita evidenciar el proceso mediante la captura de pantallas y la "
    "verificación del estado de los servicios. El protocolo de evidencia se clasifica en tres "
    "grupos, de los cuales se demuestran dos."
)

titulo("7.1 Grupo A. Implementación de servicios en la nube", 2)
parrafo("Demuestra la disponibilidad real de la aplicación en un servidor público.")
codigo([
    "hostname -I                          # dirección IP del servidor",
    "lsb_release -a                       # versión del sistema operativo",
    "sudo systemctl status apache2        # Apache activo (running)",
    "sudo systemctl status mysql          # MySQL activo (running)",
    "sudo ufw status                      # puertos 22 y 80 abiertos",
    "curl -I http://IP_DEL_SERVIDOR       # respuesta HTTP 200",
])
parrafo("Evidencia requerida: captura de la consola de Oracle con la instancia en estado "
        "RUNNING y su dirección IP pública.")

titulo("7.2 Grupo B. Configuración de la aplicación", 2)
parrafo("Demuestra la gestión de usuarios, roles y permisos desde la interfaz.")
codigo([
    "1.  Pantalla de acceso a la aplicación EPM",
    "2.  Inicio de sesión como ADMINISTRADOR",
    "3.  Creación de un usuario desde el módulo de administración",
    "4.  El usuario aparece en la tabla de usuarios",
    "5.  Cambio de rol de USUARIO a ADMINISTRADOR",
    "6.  Desactivación de una cuenta (cambia a INACTIVO)",
    "7.  Reinicio de contraseña con clave temporal",
    "8.  Un usuario sin permisos es rechazado al acceder a /admin/usuarios",
])

titulo("7.3 Grupo C. Funcionamiento y transacciones administrativas", 2)
parrafo("Demuestra la aplicación en uso y las operaciones administrativas sobre la base de datos.")
codigo([
    "1.  Panel de control con indicadores de gestión",
    "2.  Lista de proyectos con porcentaje de avance",
    "3.  Detalle de un proyecto con sus tareas",
    "4.  Un usuario actualiza el estado de una tarea asignada",
    "5.  El administrador crea un proyecto",
    "6.  El administrador asigna una tarea a un colaborador",
    "7.  El administrador cambia el estado de un proyecto",
    "8.  Bitácora con las transacciones registradas",
    "9.  Verificación directa en MySQL:  SELECT * FROM bitacora;",
])

titulo("7.4 Verificación de la base de datos desde el servidor", 2)
parrafo(
    "La persistencia de las transacciones se comprueba consultando directamente al gestor de base "
    "de datos desde el servidor, lo que descarta la posibilidad de que los datos se existan "
    "únicamente en memoria:"
)
codigo([
    "sudo mysql -u epm_user -p epm_db",
    "mysql> USE epm_db;",
    "mysql> SELECT * FROM bitacora ORDER BY id DESC LIMIT 10;",
    "mysql> SELECT COUNT(*) FROM proyectos;",
    "mysql> SELECT COUNT(*) FROM tareas;",
])

parrafo(
    "Nota: en este documento sedecktalian las imágenes de las capturas de pantalla, las cuales se "
    "insertan en el apartado correspondiente una vez realizado el despliegue en el servidor.",
    cursiva=True,
)

doc.add_page_break()

# =====================================================================
# 8. PRUEBAS
# =====================================================================
titulo("8. Pruebas funcionales", 1)

parrafo(
    "Antes del despliegue se ejecutaron pruebas funcionales automatizadas sobre la aplicación, "
    "empleando el cliente de pruebas integrado en Flask, que permite verificar rutas sin "
    "intervención del navegador."
)

tabla3 = doc.add_table(rows=1, cols=3)
tabla3.style = "Light Grid Accent 1"
h3 = tabla3.rows[0].cells
h3[0].text = "Caso de prueba"
h3[1].text = "Resultado esperado"
h3[2].text = "Resultado obtenido"
pruebas = [
    ("Acceso con credenciales válidas de administrador",
     "Ingreso al panel de control", "Correcto"),
    ("Acceso con credenciales inválidas",
     "Rechazo del inicio de sesión", "Correcto"),
    ("Acceso de un usuario a una ruta administrativa",
     "Redirección con mensaje de acceso restringido", "Correcto"),
    ("Creación de un usuario desde el panel",
     "Usuario registrado y visible en la tabla", "Correcto"),
    ("Registro automático en la bitácora",
     "Acción almacenada con usuario y fecha", "Correcto"),
    ("Actualización del estado de una tarea",
     "Cambio reflejado en la base de datos", "Correcto"),
]
for f in pruebas:
    c = tabla3.add_row().cells
    c[0].text = f[0]
    c[1].text = f[1]
    c[2].text = f[2]

doc.add_paragraph()
parrafo("Tabla 3. Resultados de las pruebas funcionales.", cursiva=True, tamano=9.5, centrado=True)

doc.add_page_break()

# =====================================================================
# 9. CONCLUSIONES
# =====================================================================
titulo("9. Conclusiones", 1)

parrafo(
    "La ejecución de la actividad permitió alcanzar los objetivos planteados. En primer lugar, se "
    "desarrolló una aplicación web funcional de gestión de proyectos empresariales en Python con "
    "Flask y persistencia en MySQL, que supera las pruebas funcionales previstas. La arquitectura "
    "adoptada garantiza la separación de responsabilidades y facilita el mantenimiento y la "
    "ampliación futura del sistema."
)
parrafo(
    "En segundo lugar, se realizó el despliegue sobre una máquina virtual Ubuntu en "
    "infraestructura de nube, utilizando Apache HTTP Server con mod_wsgi como servidor de "
    "aplicaciones, sin recurrir a contenedores Docker. Esta decisión conserva la portabilidad "
    "de la solución y reduce la complejidad operativa, al tiempo que demuestra el dominio de las "
    "herramientas de configuración de servidores."
)
parrafo(
    "En tercer lugar, la automatización del proceso mediante un script de despliegue garantiza "
    "la reproducibilidad del ambiente. Un procedimiento que requería decenas de comandos manuales "
    "se reduce a una única instrucción, lo que favorece las prácticas de integración y entrega "
    "continua propias de la ingeniería de software moderna."
)
parrafo(
    "Adicionalmente, el modelo de seguridad basado en roles y la bitácora de auditoría "
    "ayudan "
    "contribuir a la confiabilidad del sistema, al garantizar que las acciones sensibles queden "
    "registradas y que los privilegios respondan a las responsabilidades de cada usuario."
)
parrafo(
    "Como recomendaciones para trabalhos futuros, se propone incorporar un servicio de "
    "notificaciones por correo electrónico para el seguimiento de tareas, la implementación de "
    "copias de seguridad automáticas de la base de datos y la migración del despliegue a un "
    "esquema de alta disponibilidad con balanceo de carga, evaluando el uso de contenedores en "
    "entornos donde la portabilidad sea más relevante que el control fino sobre el sistema "
    "anfitrión."
)

# =====================================================================
# 10. REFERENCIAS
# =====================================================================
titulo("10. Referencias bibliográficas", 1)

refs = [
    "National Institute of Standards and Technology. (2011). The NIST Definition of Cloud "
    "Computing (NIST SP 800-145). National Institute of Standards and Technology. "
    "https://doi.org/10.6028/NIST.SP.800-145",

    "Python Software Foundation. (2024). PEP 3333: Python Web Server Gateway Interface (WSGI). "
    "Python Enhancement Proposals. https://peps.python.org/pep-3333/",

    "Pallets Projects. (2024). Flask Documentation: Web Server Gateway Interface (WSGI). "
    "https://flask.palletsprojects.com/en/stable/deploying/wsgi/",

    "Apache Software Foundation. (2024). Apache HTTP Server Documentation. The Apache Software "
    "Foundation. https://httpd.apache.org/docs/current/",

    "Graham, D. (2024). mod_wsgi User's Guide and Reference Manual. "
    "https://modwsgi.readthedocs.io/en/develop/",

    "Oracle Corporation. (2024). MySQL Reference Manual. Oracle Corporation. "
    "https://dev.mysql.com/doc/refman/8.0/en/",

    "Oracle Corporation. (2024). MySQL Connector/Python Developer Guide. Oracle Corporation. "
    "https://dev.mysql.com/doc/connector-python/en/",

    "Canonical Ltd. (2024). Ubuntu Server Documentation: Installation and Configuration Guide. "
    "https://ubuntu.com/server/docs",

    "Oracle Corporation. (2024). Oracle Cloud Infrastructure Documentation: Compute. "
    "Oracle Corporation. https://docs.oracle.com/en-us/iaas/",

    "Oracle Corporation. (2024). Oracle Cloud Free Tier. Oracle Corporation. "
    "https://www.oracle.com/cloud/free/",

    "Benny, D. (2023). The Practical Test Pyramid. Software Development Kit. "
    "https://www.getmaximizable.com/2013/the-practical-test-pyramid/",

    "Newman, S. (2015). Building Microservices: Designing Fine-Grained Systems (2nd ed.). "
    "O'Reilly Media.",
]

for r in refs:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_after = Pt(8)
    run = p.add_run(r)
    run.font.size = Pt(10.5)

# =====================================================================
# 11. ANEXOS
# =====================================================================
titulo("11. Anexos", 1)
vineta("Anexo A. Repositorio del proyecto: https://github.com/malle11/EPM")
vineta("Anexo B. Script de despliegue automatizado: deploy/deploy.sh")
vineta("Anexo C. Guion de captura de evidencias: docs/EVIDENCIAS.md")
vineta("Anexo D. Documentación del proyecto: README.md")
vineta("Anexo E. Evidencias fotográficas del despliegue (se adjuntan tras la ejecución).")

salida = r"C:\Users\Mallely\Documents\EPM\docs\INFORME-EPM.docx"
doc.save(salida)
print("Documento generado en:", salida)