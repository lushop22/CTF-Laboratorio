# 🚩 Laboratorio CTF Ciclo 1

**Introducción a la Ciberseguridad** · 22 retos · 2300 puntos · formato de flag `CICLO1{...}`

> 🌐 **Plataforma del curso:** https://ctf.tudominio.com
> 🔑 **Código de clase:** te lo da tu docente en clase (no lo publiques).

Este repositorio es **tu laboratorio**: lo levantas en tu PC con Docker. Dentro hay retos de
**Linux, criptografía, web, forense, OSINT y reversing**. Cada reto esconde una flag **única para ti**;
la encuentras en tu laboratorio y la envías en la plataforma del curso para sumar puntos.

| Qué | Dónde | Para qué |
|---|---|---|
| 💻 Terminal de retos (`ctf-kit`) | `docker exec -it ctf-kit bash` | Linux, criptografía, forense y reversing |
| 🌐 Web vulnerable *Café Nebulosa* | http://localhost:8080 | Retos de web y OSINT (sitio ficticio) |
| 📦 Descargas | http://localhost:8081 | Archivos de los retos para Wireshark, CyberChef… |

---

## Paso 1 · Instala Docker y Git (solo la primera vez)

<details open>
<summary><b>Windows</b></summary>

1. Instala **Docker Desktop**: https://www.docker.com/products/docker-desktop/ — acepta usar **WSL 2** y reinicia la PC.
2. Instala **Git para Windows**: https://git-scm.com/download/win (incluye **Git Bash**).
3. Abre Docker Desktop y espera a que diga **Engine running**. Debe estar abierto siempre que uses el laboratorio.

> ¿Docker Desktop no arranca? Activa la virtualización (Intel VT-x o AMD-V) en la BIOS.
</details>

<details>
<summary><b>macOS</b></summary>

1. Instala **Docker Desktop** para tu chip (**Apple Silicon** M1/M2/M3… o **Intel**): https://www.docker.com/products/docker-desktop/
2. Git ya viene en macOS. Si te pide instalar las *Command Line Tools*, acepta.
3. Abre Docker Desktop y espera a que diga **Engine running**.
</details>

<details>
<summary><b>Linux</b></summary>

1. Instala **Docker Engine** con el plugin **Compose**: https://docs.docker.com/engine/install/ y también `git`.
2. Para usar Docker sin `sudo`: `sudo usermod -aG docker $USER`, cierra e inicia sesión de nuevo.
</details>

Comprueba que todo responde (en Windows usa **PowerShell**):

```bash
docker --version
docker compose version
git --version
```

## Paso 2 · Crea tu cuenta en la plataforma

1. Entra a la **plataforma del curso** (enlace al inicio de esta página) y pulsa **Crear cuenta**.
2. Escribe el **código de clase** y elige tu usuario. Tu usuario aparecerá en el marcador público.
3. Contraseña: al menos 8 caracteres, con letras y números, sin incluir tu usuario. Usa una que no uses en otro sitio.
4. Llegarás a **Mi laboratorio**: ahí está tu **token personal** (`xxxx-xxxx-xxxx-xxxx`). Deja esa página abierta.

> Tu token es solo tuyo. Tu laboratorio genera **tus** flags a partir de él: la flag de un compañero no sirve en tu cuenta.

## Paso 3 · Descarga el laboratorio

```bash
git clone https://github.com/lushop22/CTF-Laboratorio.git
cd CTF-Laboratorio
```

Desde aquí, todos los comandos se ejecutan dentro de la carpeta `CTF-Laboratorio`.

## Paso 4 · Pon tu token en el archivo `.env`

**Windows (PowerShell):**
```powershell
copy .env.example .env
notepad .env
```

**macOS / Linux:**
```bash
cp .env.example .env
nano .env
```

Completa la línea `LAB_TOKEN=` con tu token. En **Mi laboratorio**, el botón **Copiar línea .env** te la da lista para pegar:

```
LAB_TOKEN=a1b2-c3d4-e5f6-a7b8
```

Guarda el archivo (Bloc de notas: `Ctrl+S`; nano: `Ctrl+O`, `Enter`, `Ctrl+X`). No cambies nada más.

## Paso 5 · Levanta el laboratorio

```bash
docker compose up -d --build
```

La **primera vez tarda entre 5 y 15 minutos**, porque descarga las herramientas. Después arranca en segundos.
Termina cuando ves `Container ctf-kit Started` y `Container ctf-web Started`.

## Paso 6 · Comprueba que todo funciona

**Windows:** abre **Git Bash** dentro de la carpeta (clic derecho → *Open Git Bash here*) y ejecuta `bash verificar.sh`
**macOS / Linux:** `./verificar.sh`

Revisa estas tres líneas:

```
  ✔ LAB_TOKEN configurado: a1b2-c3d4-e5f6-a7b8   ← igual al de «Mi laboratorio»
  Versión de los retos: aca22492166e            ← igual a la de «Mi laboratorio»
Resultado: 29 correctos, 0 con problemas.
```

⚠️ Si el token o la versión **no coinciden**, la plataforma rechazará tus flags. Corrige el `.env` o actualiza el laboratorio (ver [Problemas frecuentes](#problemas-frecuentes)).

## Paso 7 · Entra y resuelve

Terminal de retos (en Windows usa **PowerShell**, no Git Bash):

```bash
docker exec -it ctf-kit bash
```

Dentro verás un banner con tu token. Para empezar:

```bash
ayuda                  # hoja de comandos (grep, find, base64, exiftool, binwalk, steghide, tshark…)
cd ~/retos && ls       # linux · cripto · forense · reversing
mkdir -p /tmp/trabajo  # los retos son de solo lectura: copia aquí lo que vayas a extraer
exit                   # salir
```

- 🌐 **Web Café Nebulosa:** http://localhost:8080
- 📦 **Descargas:** http://localhost:8081

Estos enlaces solo funcionan en tu PC, con el laboratorio encendido.

## Paso 8 · Envía tus flags

En la plataforma, abre **Retos**, despliega el reto que resolviste, pega la flag completa (`CICLO1{...}`) y pulsa **Enviar**.

💡 Empieza por **«Bienvenida»** (Linux, 50 pts), en `~/retos/linux/01_bienvenida`: te confirma que todo funciona de punta a punta.

---

## Los 22 retos

| Categoría | Reto | Pts | Dónde |
|---|---|---|---|
| Linux | Bienvenida | 50 | ctf-kit `~/retos/linux/01_bienvenida` |
| Linux | Lo que no se ve | 50 | ctf-kit `~/retos/linux/02_ocultos` |
| Linux | Aguja en el pajar | 100 | ctf-kit `~/retos/linux/03_pajar` |
| Linux | Perdido en el sistema | 100 | ctf-kit (todo el sistema) |
| Criptografía | Primer contacto | 50 | ctf-kit `~/retos/cripto/01_base64` |
| Criptografía | Solo números y letras de la a a la f | 50 | ctf-kit `~/retos/cripto/02_hex` |
| Criptografía | El César perdió la cuenta | 100 | ctf-kit `~/retos/cripto/03_cesar` |
| Criptografía | Capa sobre capa | 150 | ctf-kit `~/retos/cripto/04_capas` |
| Criptografía | Huella digital | 150 | ctf-kit `~/retos/cripto/05_huella` |
| Web | Comentarios olvidados | 50 | http://localhost:8080 |
| Web | Los robots no deben entrar | 100 | http://localhost:8080 |
| Web | Login de mentira | 100 | http://localhost:8080/empleados |
| Web | Galleta con permisos | 150 | http://localhost:8080/perfil |
| Forense | La foto habla | 100 | ctf-kit `~/retos/forense/01_metadatos` |
| Forense | Extensión mentirosa | 100 | ctf-kit `~/retos/forense/02_extension` |
| Forense | Capas de cebolla | 150 | ctf-kit `~/retos/forense/03_cebolla` |
| Forense | Un paisaje muy pesado | 150 | ctf-kit `~/retos/forense/04_paisaje` |
| Forense | Tráfico sin cifrar | 150 | ctf-kit `~/retos/forense/05_trafico` |
| OSINT | Pregunta de seguridad | 100 | http://localhost:8080/blog |
| OSINT | Internet no olvida | 100 | http://localhost:8080/contacto |
| Reversing | Cadenas sueltas | 100 | ctf-kit `~/retos/reversing/01_cadenas` |
| Reversing | Login | 150 | ctf-kit `~/retos/reversing/02_login` |

Las descripciones y las pistas de cada reto están en el tablero de la plataforma.

## En las siguientes clases

| Para | Comando (dentro de `CTF-Laboratorio`) |
|---|---|
| Encender el laboratorio | Abre Docker Desktop y ejecuta `docker compose up -d`. Tus flags siguen siendo las mismas. |
| Apagarlo al terminar | `docker compose stop` |
| Actualizarlo (si el docente lo pide) | `git pull` y luego `docker compose up -d --build` |
| Ver si está encendido | `docker compose ps` |

## Problemas frecuentes

| Mensaje o síntoma | Qué hacer |
|---|---|
| «Esa flag no corresponde a TU token» | El `LAB_TOKEN` de tu `.env` no es el de tu cuenta. Corrígelo y ejecuta `docker compose up -d`: tus flags se regeneran. |
| «Esa flag viene de un laboratorio SIN token» | Tu `.env` no tiene el token o no se guardó. Repite el paso 4 y ejecuta `docker compose up -d`. |
| Rechaza todas tus flags y el token está bien | Tu laboratorio está desactualizado: la versión de los retos no coincide con «Mi laboratorio». Ejecuta `git pull` y `docker compose up -d --build`. |
| `Cannot connect to the Docker daemon` | Docker Desktop no está abierto. Ábrelo, espera *Engine running* y repite. |
| `port is already allocated` | Otro programa usa ese puerto. Agrega al `.env` `PUERTO_WEB=8180` (o `PUERTO_DESCARGAS=8181`, `PUERTO_SSH=2223`) y ejecuta `docker compose up -d`. |
| `the input device is not a TTY` | Usaste `docker exec -it` en Git Bash. Hazlo en PowerShell, o antepón `winpty`. |
| «Permission denied» con `binwalk -e` o `steghide` | Estás dentro de `~/retos`, que es de solo lectura. Copia el archivo a `/tmp/trabajo` y trabaja ahí. |
| «Demasiados intentos» | La plataforma frena los envíos masivos. Espera un minuto (5 si fue al iniciar sesión). |
| Mac con chip M1/M2/M3: la construcción es lenta | Es normal la primera vez. |
| Olvidé mi contraseña de la plataforma | Pídele a tu docente que la restablezca y luego cámbiala en **Mi cuenta**. |

## Reglas

- Solo atacas **tu laboratorio**: el ctf-kit, la web Café Nebulosa y los archivos de los retos. **Nunca** la plataforma, ni equipos o redes de otras personas.
- Las flags no se comparten. Las ideas, las herramientas y las dudas, sí.
- Anota los pasos de cada reto que resuelvas: los necesitarás para tu **write-up** (reto, análisis, pasos, flag y lecciones aprendidas).
- La web Café Nebulosa es **vulnerable a propósito**: no la expongas a Internet.
- Fuera del laboratorio y sin autorización, estas técnicas son delito (en Perú, Ley N.° 30096).
