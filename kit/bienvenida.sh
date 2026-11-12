# Banner del ctf-kit (se muestra una vez por sesión interactiva)
if [ -n "$PS1" ] && [ -z "$CTF_BANNER_MOSTRADO" ] && [ "$(id -un)" = "ctf" ]; then
  export CTF_BANNER_MOSTRADO=1
  cat <<'EOF'

  ██████ ████████ ███████      ██████ ██  ██████ ██       ██████      ██
 ██         ██    ██          ██      ██ ██      ██      ██    ██    ███
 ██         ██    █████       ██      ██ ██      ██      ██    ██     ██
 ██         ██    ██          ██      ██ ██      ██      ██    ██     ██
  ██████    ██    ██           ██████ ██  ██████ ███████  ██████      ██

  Bienvenido al ctf-kit · Formato de flag: CICLO1{...}
EOF
  printf '  Tu token de laboratorio: %s\n' "$(cat /var/lib/ctf/token 2>/dev/null || echo '?')"
  if [ "$(cat /var/lib/ctf/token 2>/dev/null)" = "SIN TOKEN" ]; then
    printf '\n  ⚠  NO configuraste LAB_TOKEN: tus flags NO serán aceptadas en la plataforma.\n'
    printf '     Copia tu token de la plataforma en .env y ejecuta: docker compose up -d\n'
  fi
  cat <<'EOF'

  Retos:        cd ~/retos && ls
  Ayuda rápida: ayuda
  Web del lab:  curl http://web:8080   (o en tu navegador)

  IMPORTANTE: los retos son de solo lectura. Trabaja en tu propia carpeta:
      mkdir -p /tmp/tu_nombre && cd /tmp/tu_nombre

EOF
fi
