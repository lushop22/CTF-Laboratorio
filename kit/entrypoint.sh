#!/bin/bash
set -e

ESTADO=/var/lib/ctf
mkdir -p "$ESTADO"
rm -f "$ESTADO/listo"

# ------------------------------------------------------------ token personal
# El token lo entrega la plataforma al registrarse y va en .env → LAB_TOKEN.
TOKEN="$(printf '%s' "${LAB_TOKEN:-}" | tr -d '[:space:]"'"'"'-' | tr 'A-F' 'a-f')"
if [[ "$TOKEN" =~ ^[0-9a-f]{16}$ ]]; then
  echo "${TOKEN:0:4}-${TOKEN:4:4}-${TOKEN:8:4}-${TOKEN:12:4}" > "$ESTADO/token"
else
  echo "[ctf-kit] ============================================================"
  echo "[ctf-kit] AVISO: LAB_TOKEN no está configurado o no es válido."
  echo "[ctf-kit] Regístrate en la plataforma, copia tu token en el archivo .env"
  echo "[ctf-kit] (LAB_TOKEN=xxxx-xxxx-xxxx-xxxx) y ejecuta: docker compose up -d"
  echo "[ctf-kit] Mientras tanto, las flags generadas NO serán aceptadas."
  echo "[ctf-kit] ============================================================"
  TOKEN="0000000000000000"
  echo "SIN TOKEN" > "$ESTADO/token"
fi
chmod 644 "$ESTADO/token"

# ------------------------------------------------------------ retos
# Se generan al arrancar (no en la imagen). Si el token no cambió desde el
# último arranque de este contenedor, se reutilizan los archivos.
HUELLA="$(printf '%s' "$TOKEN" | sha256sum | cut -d' ' -f1)"
if [ "$(cat "$ESTADO/huella" 2>/dev/null)" != "$HUELLA" ] || [ ! -d /home/ctf/retos ]; then
  echo "[ctf-kit] generando retos personales…"
  SALIDA="$(mktemp -d)"
  python3 /opt/ctf-generador/generar_retos.py /opt/ctf-generador/retos.json "$SALIDA/out" "$TOKEN"
  rm -rf /home/ctf/retos /opt/.respaldo /srv/descargas
  mv "$SALIDA/out/retos" /home/ctf/retos
  mv "$SALIDA/out/sistema/opt/.respaldo" /opt/.respaldo
  rm -rf "$SALIDA"
  chown -R root:root /home/ctf/retos /opt/.respaldo
  find /home/ctf/retos /opt/.respaldo -type d -exec chmod 755 {} +
  find /home/ctf/retos /opt/.respaldo -type f -exec chmod 644 {} +
  chmod 755 /home/ctf/retos/reversing/01_cadenas/programa /home/ctf/retos/reversing/02_login/login
  # Descargas: los retos de Linux no se publican, se resuelven en la terminal.
  mkdir -p /srv/descargas
  cp -r /home/ctf/retos/cripto /home/ctf/retos/forense /home/ctf/retos/reversing /srv/descargas/
  chmod -R a+rX /srv/descargas
  echo "$HUELLA" > "$ESTADO/huella"
  chmod 600 "$ESTADO/huella"
fi

# ------------------------------------------------------------ servicios
# Contraseña SSH del usuario ctf (definida en .env → SSH_PASSWORD)
echo "ctf:${SSH_PASSWORD:-ctf2026}" | chpasswd

# Claves de host propias de este contenedor
ssh-keygen -A >/dev/null 2>&1
mkdir -p /run/sshd

# Servidor de descargas (solo lectura) en el puerto 8081
runuser -u nobody -- python3 -m http.server 8081 --bind 0.0.0.0 --directory /srv/descargas \
    >/var/log/descargas.log 2>&1 &

touch "$ESTADO/listo"
echo "[ctf-kit] listo (token: $(cat "$ESTADO/token")): SSH en el puerto 22 y descargas en el puerto 8081"
exec /usr/sbin/sshd -D -e
