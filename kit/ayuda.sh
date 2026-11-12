#!/bin/bash
# Hoja de referencia rápida del ctf-kit
cat <<'EOF'

 ================================ AYUDA CTF ================================

 LINUX
   pwd · cd carpeta · ls -la              dónde estoy · moverme · listar TODO
   cat archivo · less archivo             ver contenido
   grep -r "CICLO1{" .                    buscar texto en todas las carpetas
   find / -name "*texto*" 2>/dev/null     buscar archivos por nombre
   file archivo                           ¿qué tipo de archivo es realmente?
   strings archivo | grep CICLO1          texto legible dentro de un archivo

 CRIPTO / CODIFICACIÓN
   echo 'texto' | base64 -d               decodificar Base64
   echo '4349...' | xxd -r -p             decodificar hexadecimal
   echo 'texto' | tr 'A-Za-z' 'N-ZA-Mn-za-m'   ROT13
   echo -n 'palabra' | sha256sum          calcular un hash
   CyberChef (navegador): https://gchq.github.io/CyberChef/

 FORENSE   (copia el archivo a tu carpeta en /tmp antes de extraer)
   exiftool imagen.jpg                    metadatos
   binwalk imagen.jpg · binwalk -e ...    archivos escondidos / extraerlos
   steghide extract -sf imagen.jpg        datos ocultos (pide contraseña)
   zsteg imagen.png                       estego en PNG/BMP
   tshark -r captura.pcap -Y ftp          ver tráfico filtrado
   xxd archivo | head                     ver los primeros bytes (magic bytes)

 REVERSING
   file programa · strings programa       identificar · leer textos
   ltrace ./programa                      ver llamadas (strcmp, etc.)

 WEB (desde el ctf-kit)
   curl http://web:8080/                  ver el HTML de una página
   curl -i http://web:8080/perfil         ver también las cabeceras (cookies)
   curl -b "rol=VALOR" http://web:8080/perfil   enviar una cookie

 Si te atascas más de 30 min: relee el enunciado, abre la pista o pide ayuda.
 ===========================================================================

EOF
