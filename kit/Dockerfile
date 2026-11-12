# ctf-kit: terminal con herramientas + retos de Linux, Cripto, Forense y Reversing.
# Se construye desde la raíz del proyecto (ver docker-compose.yml).

# Las flags NO se generan al construir la imagen: entrypoint.sh las genera al
# arrancar a partir del token personal del estudiante (LAB_TOKEN en .env).
FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive LANG=C.UTF-8 TZ=America/Lima

# Herramientas: base, Linux, red, cripto, forense y reversing
RUN echo "wireshark-common wireshark-common/install-setuid boolean false" | debconf-set-selections \
    && apt-get update && apt-get install -y --no-install-recommends \
        bash-completion ca-certificates less nano vim tree tzdata \
        file findutils grep binutils bsdmainutils coreutils procps \
        curl wget netcat-openbsd iputils-ping dnsutils openssh-server \
        python3 python3-pip \
        libimage-exiftool-perl binwalk steghide tshark unzip zip p7zip-full foremost \
        ltrace strace gdb \
        ruby \
        python3-pil python3-scapy gcc libc6-dev \
    && rm -rf /var/lib/apt/lists/*

# zsteg (estego en PNG/BMP). Si no hay acceso a rubygems.org, el resto sigue funcionando.
RUN gem install zsteg --no-document || echo "AVISO: zsteg no se pudo instalar"

# Usuario de los estudiantes y SSH
RUN useradd -m -s /bin/bash ctf \
    && mkdir -p /run/sshd \
    && rm -f /etc/ssh/ssh_host_* \
    && sed -i 's/^#\?PasswordAuthentication .*/PasswordAuthentication yes/' /etc/ssh/sshd_config \
    && sed -i 's/^#\?PermitRootLogin .*/PermitRootLogin no/' /etc/ssh/sshd_config \
    && sed -i 's/^#\?PrintMotd .*/PrintMotd no/' /etc/ssh/sshd_config \
    && echo "AllowUsers ctf" >> /etc/ssh/sshd_config

# Generador de retos (solo root). config/retos.json no contiene flags: solo la
# parte legible de cada una; el resto se deriva del token al arrancar.
COPY config/retos.json kit/generar_retos.py comun/ctf_flags.py /opt/ctf-generador/
RUN sed -i 's/\r$//' /opt/ctf-generador/* \
    && chmod 700 /opt/ctf-generador && chmod 600 /opt/ctf-generador/*

# Ayuda, banner y arranque.
# "docker exec -it ctf-kit bash" entra directamente como el usuario ctf;
# el docente entra como root con: docker exec -it -e CTF_ROOT=1 ctf-kit bash
COPY kit/ayuda.sh /usr/local/bin/ayuda
COPY kit/bienvenida.sh /etc/profile.d/zz-ctf-bienvenida.sh
COPY kit/entrypoint.sh /entrypoint.sh
# sed: por si el repositorio se clonó en Windows con fin de línea CRLF
RUN sed -i 's/\r$//' /usr/local/bin/ayuda /etc/profile.d/zz-ctf-bienvenida.sh /entrypoint.sh \
    && chmod 755 /usr/local/bin/ayuda /entrypoint.sh \
    && echo '[ -f /etc/profile.d/zz-ctf-bienvenida.sh ] && . /etc/profile.d/zz-ctf-bienvenida.sh' >> /home/ctf/.bashrc \
    && echo 'if [ -z "$CTF_ROOT" ] && [ -t 0 ]; then exec su - ctf; fi' >> /root/.bashrc

EXPOSE 22 8081
ENTRYPOINT ["/entrypoint.sh"]
