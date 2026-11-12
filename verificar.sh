#!/usr/bin/env bash
# Comprueba que tu laboratorio personal está funcionando. Uso: ./verificar.sh
# (ejecutar después de: docker compose up -d --build)

set -u
# Git Bash (Windows) convierte rutas como /home/ctf en C:/Program Files/Git/home/ctf
# al pasarlas a docker exec; esto lo desactiva. En Linux/macOS no tiene efecto.
export MSYS_NO_PATHCONV=1
HOST="${LAB_HOST:-localhost}"
OK=0; FALLOS=0
pasa()  { echo "  ✔ $1"; OK=$((OK+1)); }
falla() { echo "  ✘ $1"; FALLOS=$((FALLOS+1)); }
probar() { local desc="$1"; shift; if "$@" >/dev/null 2>&1; then pasa "$desc"; else falla "$desc"; fi; }

echo "== Contenedores"
for c in ctf-web ctf-kit; do
  probar "$c en ejecución" sh -c "docker ps --format '{{.Names}}' | grep -qx $c"
done
# El kit genera los retos al arrancar: esperar hasta 2 minutos
for _ in $(seq 1 60); do docker exec ctf-kit test -f /var/lib/ctf/listo 2>/dev/null && break; sleep 2; done
probar "ctf-kit terminó de generar los retos" docker exec ctf-kit test -f /var/lib/ctf/listo

echo "== Token personal"
TOKEN_KIT="$(docker exec ctf-kit cat /var/lib/ctf/token 2>/dev/null)"
if [ -n "$TOKEN_KIT" ] && [ "$TOKEN_KIT" != "SIN TOKEN" ]; then
  pasa "LAB_TOKEN configurado: $TOKEN_KIT (debe coincidir con «Mi laboratorio» en la plataforma)"
else
  falla "LAB_TOKEN NO configurado: copia tu token en .env y ejecuta docker compose up -d"
fi
probar "La web usa el mismo token" sh -c "! curl -fsS http://$HOST:${PUERTO_WEB:-8080}/ | grep -q 'Laboratorio sin'"

echo "== Servicios"
probar "Web Café Nebulosa responde (http://$HOST:8080)" curl -fsS "http://$HOST:8080/"
probar "robots.txt publicado" sh -c "curl -fsS http://$HOST:8080/robots.txt | grep -q panel-secreto"
probar "Descargas responden (http://$HOST:8081)" curl -fsS "http://$HOST:8081/forense/"
probar "SSH escucha en el puerto 2222" bash -c "exec 3<>/dev/tcp/$HOST/${PUERTO_SSH:-2222}"

echo "== Herramientas en ctf-kit"
for h in file strings grep find exiftool binwalk steghide tshark ltrace xxd curl base64 sha256sum; do
  probar "$h" docker exec ctf-kit sh -c "command -v $h"
done
if docker exec ctf-kit sh -c "command -v zsteg" >/dev/null 2>&1; then pasa "zsteg"; else echo "  ! zsteg no instalado (opcional)"; fi

echo "== Retos en ctf-kit"
probar "Carpeta de retos presente" docker exec ctf-kit test -d /home/ctf/retos/forense
probar "El kit alcanza la web interna (http://web:8080)" docker exec ctf-kit curl -fsS http://web:8080/
probar "steghide extrae el reto Capas de cebolla" docker exec ctf-kit sh -c \
  "steghide extract -sf /home/ctf/retos/forense/03_cebolla/cebolla.jpg -p cebolla -xf /tmp/.verif -f -q && test -s /tmp/.verif && rm -f /tmp/.verif"
probar "ltrace muestra strcmp en el reto Login" docker exec ctf-kit sh -c \
  "echo x | ltrace /home/ctf/retos/reversing/02_login/login 2>&1 | grep -q strcmp"
probar "tshark lee la captura FTP" docker exec ctf-kit sh -c \
  "tshark -r /home/ctf/retos/forense/05_trafico/captura.pcap -Y ftp 2>/dev/null | grep -q PASS"
probar "El usuario ctf no puede leer el generador de retos" sh -c "! docker exec -u ctf ctf-kit ls /opt/ctf-generador"

echo "== Versión de los retos"
RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VERSION="$(cat "$RAIZ/config/retos.json" "$RAIZ/comun/ctf_flags.py" | sha256sum | cut -c1-12)"
echo "  Versión de los retos: $VERSION  (debe coincidir con la que muestra «Mi laboratorio» en la plataforma)"

echo
echo "Resultado: $OK correctos, $FALLOS con problemas."
[ "$FALLOS" -eq 0 ] && echo "🚩 ¡Laboratorio listo! Envía tus flags en la plataforma del curso."
exit "$FALLOS"
