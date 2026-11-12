#!/usr/bin/env python3
"""Genera los archivos de los retos del ctf-kit a partir de config/retos.json.

Se ejecuta al ARRANCAR el contenedor (entrypoint.sh), no al construir la
imagen: las flags se derivan del token personal del estudiante (LAB_TOKEN)
con comun/ctf_flags.py, así que no existen en el repositorio ni en la imagen.

Uso: generar_retos.py <retos.json> <carpeta_salida> <token>
Requiere: python3-pil, python3-scapy, exiftool, steghide, gcc.
"""
import base64
import codecs
import hashlib
import io
import json
import os
import random
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

from ctf_flags import normalizar_token, todas_las_flags

CONFIG, SALIDA, TOKEN = Path(sys.argv[1]), Path(sys.argv[2]), normalizar_token(sys.argv[3])
FLAGS = todas_las_flags(TOKEN, json.loads(CONFIG.read_text(encoding="utf-8"))["retos"])

# Reproducible para un mismo token (si se reinicia el contenedor, los archivos
# quedan iguales) y distinto entre estudiantes (p. ej. dónde está la aguja).
random.seed(TOKEN)
RETOS = SALIDA / "retos"
SISTEMA = SALIDA / "sistema"


def escribir(ruta: Path, contenido, binario=False):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    if binario:
        ruta.write_bytes(contenido)
    else:
        ruta.write_text(contenido, encoding="utf-8")
    return ruta


def ejecutar(*cmd, **kw):
    subprocess.run(cmd, check=True, **kw)


def cesar(texto: str, n: int) -> str:
    def mover(c):
        if "a" <= c <= "z":
            return chr((ord(c) - 97 + n) % 26 + 97)
        if "A" <= c <= "Z":
            return chr((ord(c) - 65 + n) % 26 + 65)
        return c
    return "".join(mover(c) for c in texto)


def zip_en_memoria(archivos: dict) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for nombre, contenido in archivos.items():
            z.writestr(nombre, contenido)
    return buf.getvalue()


def ruido(img: Image.Image, intensidad=18) -> Image.Image:
    """Agrega textura para que la imagen parezca una foto y tenga capacidad
    suficiente para esconder datos con steghide."""
    pix = img.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            r, g, b = pix[x, y]
            d = random.randint(-intensidad, intensidad)
            pix[x, y] = (max(0, min(255, r + d)), max(0, min(255, g + d)), max(0, min(255, b + d)))
    return img


# ============================================================== LINUX
def linux():
    base = RETOS / "linux"
    escribir(base / "01_bienvenida" / "bienvenida.txt", f"""\
¡Bienvenido al CTF Ciclo 1!

Si estás leyendo esto, ya sabes usar cd y cat. ¡Buen comienzo!

Recuerda la metodología:
  1. Leer y observar
  2. Investigar y probar
  3. Documentar

Tu primera flag es:

    {FLAGS['linux_bienvenida']}

Cópiala en la plataforma, en el reto «Bienvenida».
""")

    escribir(base / "02_ocultos" / "nota.txt",
             "Aquí no hay nada interesante. Solo esta nota aburrida.\n¿Seguro que listaste TODO?\n")
    escribir(base / "02_ocultos" / ".secreto",
             f"Los archivos que empiezan con punto no aparecen con un ls normal.\n{FLAGS['linux_ocultos']}\n")

    niveles = ["INFO", "INFO", "INFO", "WARN", "DEBUG", "ERROR"]
    eventos = ["conexión aceptada", "copia de seguridad iniciada", "usuario autenticado",
               "cache limpiada", "tiempo de espera agotado", "servicio reiniciado",
               "solicitud procesada", "disco al 63%", "sincronización completa"]
    elegido = (random.randint(1, 30), random.randint(1, 20))
    for s in range(1, 31):
        for a in range(1, 21):
            lineas = []
            for _ in range(random.randint(15, 40)):
                hora = f"2026-03-{random.randint(1, 28):02d} {random.randint(0, 23):02d}:" \
                       f"{random.randint(0, 59):02d}:{random.randint(0, 59):02d}"
                lineas.append(f"{hora} [{random.choice(niveles)}] {random.choice(eventos)}")
            if (s, a) == elegido:
                lineas.insert(random.randint(3, 12),
                              f"2026-03-14 03:12:44 [INFO] nota del administrador: {FLAGS['linux_pajar']}")
            escribir(base / "03_pajar" / f"servidor_{s:02d}" / f"registro_{a:02d}.log", "\n".join(lineas) + "\n")

    escribir(base / "04_perdido" / "LEEME.txt", """\
Un administrador guardó un archivo llamado flag_perdida.txt en algún lugar
del sistema y no recuerda dónde.

No está en esta carpeta. Busca en todo el sistema de archivos.
Consejo: 2>/dev/null oculta los mensajes de «Permiso denegado».
""")
    escribir(SISTEMA / "opt" / ".respaldo" / "2019" / "config_vieja" / "flag_perdida.txt",
             f"¡Lo encontraste! find es tu amigo.\n{FLAGS['linux_perdido']}\n")


# ============================================================== CRIPTO
def cripto():
    base = RETOS / "cripto"
    escribir(base / "01_base64" / "mensaje.txt",
             base64.b64encode(FLAGS["cripto_base64"].encode()).decode() + "\n")

    escribir(base / "02_hex" / "mensaje.txt", FLAGS["cripto_hex"].encode().hex() + "\n")

    escribir(base / "03_cesar" / "interceptado.txt",
             "Mensaje interceptado (desplazamiento desconocido):\n\n"
             f"    {cesar(FLAGS['cripto_cesar'], 7)}\n\n"
             "Observa: los números y los símbolos no cambian, solo las letras.\n")

    capa = base64.b64encode(FLAGS["cripto_capas"].encode()).decode()
    capa = capa.encode().hex()
    capa = base64.b64encode(capa.encode()).decode()
    escribir(base / "04_capas" / "capas.txt", capa + "\n")

    palabra = FLAGS["cripto_huella"][len("CICLO1{"):-1]          # p. ej. valquiria4821
    raiz, numero = palabra[:-4], palabra[-4:]
    otros = random.sample([str(n) for n in range(1000, 10000) if str(n) != numero], 6)
    # Variantes parecidas: muestran que un solo carácter cambia todo el hash
    variantes = [raiz + n for n in otros] + [
        raiz, "valkiria" + numero, "walquiria" + numero, raiz + numero[:3], raiz.capitalize() + numero]
    candidatas = [
        "123456", "password", "qwerty", "admin", "iloveyou", "dragon", "monkey", "football",
        "letmein", "shadow", "master", "sunshine", "princess", "superman", "batman", "trustno1",
        "peru2026", "lima1234", "contraseña", "clave123", "futbol", "barcelona", "realmadrid",
        "alianza", "universitario", "cristal", "machupicchu", "cusco2025", "arequipa", "ceviche",
        "lomo_saltado", "pisco_sour", "chicha", "inca_kola", "llama2024", "vicuña", "condor",
        "amazonas", "titicaca", "nazca", *variantes,
        "odin2026", "thor2026", "loki", "freya", "asgard", "midgard", "ragnarok", "mjolnir",
        "minecraft", "fortnite", "pokemon", "pikachu", "zelda", "mario", "luigi", "kirby",
        "naruto", "goku", "vegeta", "onepiece", "luffy", "zoro", "itachi", "sasuke",
        "hacker", "ciberseguridad", "ctf2026", "ciclo1", "utec2026", "estudiante", "profesor",
        "matematica", "fisica", "quimica", "laboratorio", "docker", "linux", "ubuntu", "kali",
        "python", "java", "javascript", "html5", "mysql", "root", "toor", "changeme",
        "welcome", "bienvenido", "hola123", "verano", "invierno", "primavera", "otoño",
        palabra, "nebulosa", "galaxia", "estrella", "cometa", "planeta", "saturno", "jupiter",
    ]
    random.shuffle(candidatas)
    escribir(base / "05_huella" / "palabras.txt", "\n".join(candidatas) + "\n")
    escribir(base / "05_huella" / "hash.txt", hashlib.sha256(palabra.encode()).hexdigest() + "\n")
    escribir(base / "05_huella" / "LEEME.txt",
             "hash.txt contiene el hash de una contraseña que está en palabras.txt.\n"
             "La flag es CICLO1{contraseña_encontrada}.\n")


# ============================================================== FORENSE
def imagen_gato(ruta: Path):
    img = Image.new("RGB", (800, 600), (182, 214, 230))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 430, 800, 600], fill=(150, 112, 80))                     # mesa
    d.ellipse([250, 260, 560, 520], fill=(235, 150, 60))                     # cuerpo
    d.ellipse([290, 120, 510, 330], fill=(240, 160, 70))                     # cabeza
    d.polygon([(300, 170), (320, 70), (380, 140)], fill=(240, 160, 70))      # oreja izq
    d.polygon([(500, 170), (480, 70), (420, 140)], fill=(240, 160, 70))      # oreja der
    d.ellipse([345, 190, 380, 230], fill=(40, 90, 40))                       # ojos
    d.ellipse([420, 190, 455, 230], fill=(40, 90, 40))
    d.polygon([(390, 250), (410, 250), (400, 262)], fill=(220, 90, 110))     # nariz
    for dy in (-8, 4, 16):                                                   # bigotes
        d.line([(330, 262 + dy), (385, 258)], fill=(60, 40, 30), width=2)
        d.line([(470, 262 + dy), (415, 258)], fill=(60, 40, 30), width=2)
    d.arc([520, 380, 700, 520], 180, 300, fill=(235, 150, 60), width=22)     # cola
    ruido(img, 10).filter(ImageFilter.SMOOTH).save(ruta, "JPEG", quality=90)


def imagen_cebolla(ruta: Path):
    img = Image.new("RGB", (900, 700), (245, 235, 220))
    d = ImageDraw.Draw(img)
    for i, color in enumerate([(120, 40, 90), (150, 60, 115), (175, 85, 140),
                               (200, 115, 165), (220, 150, 190), (238, 190, 215)]):
        m = i * 38
        d.ellipse([220 + m, 140 + m, 680 - m, 620 - m], fill=color)
    d.polygon([(430, 150), (450, 40), (470, 150)], fill=(90, 140, 60))
    ruido(img, 22).save(ruta, "JPEG", quality=92)


def imagen_paisaje(ruta: Path):
    img = Image.new("RGB", (1024, 640))
    d = ImageDraw.Draw(img)
    for y in range(640):                                                     # cielo
        d.line([(0, y), (1024, y)], fill=(90 + y // 8, 150 + y // 10, 230 - y // 12))
    d.ellipse([760, 70, 880, 190], fill=(255, 220, 120))                     # sol
    d.polygon([(0, 520), (220, 220), (430, 520)], fill=(90, 100, 120))       # montañas
    d.polygon([(280, 520), (560, 160), (840, 520)], fill=(70, 80, 100))
    d.polygon([(520, 160), (560, 160), (600, 215), (500, 215)], fill=(240, 240, 250))
    d.polygon([(640, 520), (860, 270), (1024, 520)], fill=(100, 110, 130))
    d.rectangle([0, 500, 1024, 640], fill=(70, 140, 70))                     # pradera
    ruido(img, 12).save(ruta, "JPEG", quality=90)


def captura_ftp(ruta: Path):
    from scapy.all import DNS, DNSQR, DNSRR, IP, TCP, UDP, Ether, Raw, wrpcap

    paquetes = []
    t = [1773820800.0]  # marca de tiempo inicial (fija)
    mac_cli, mac_srv = "02:00:00:00:00:23", "02:00:00:00:00:05"

    def agregar(p, dt=0.02):
        t[0] += dt
        p.time = t[0]
        paquetes.append(p)

    def sesion_tcp(cli, srv, sport, dport, intercambio):
        sc, ss = random.randint(10**6, 10**9), random.randint(10**6, 10**9)
        e_cs = Ether(src=mac_cli, dst=mac_srv) / IP(src=cli, dst=srv)
        e_sc = Ether(src=mac_srv, dst=mac_cli) / IP(src=srv, dst=cli)
        agregar(e_cs / TCP(sport=sport, dport=dport, flags="S", seq=sc))
        agregar(e_sc / TCP(sport=dport, dport=sport, flags="SA", seq=ss, ack=sc + 1))
        sc += 1
        ss += 1
        agregar(e_cs / TCP(sport=sport, dport=dport, flags="A", seq=sc, ack=ss))
        for quien, datos in intercambio:
            datos = datos.encode()
            if quien == "c":
                agregar(e_cs / TCP(sport=sport, dport=dport, flags="PA", seq=sc, ack=ss) / Raw(datos), 0.3)
                sc += len(datos)
                agregar(e_sc / TCP(sport=dport, dport=sport, flags="A", seq=ss, ack=sc))
            else:
                agregar(e_sc / TCP(sport=dport, dport=sport, flags="PA", seq=ss, ack=sc) / Raw(datos), 0.1)
                ss += len(datos)
                agregar(e_cs / TCP(sport=sport, dport=dport, flags="A", seq=sc, ack=ss))
        agregar(e_cs / TCP(sport=sport, dport=dport, flags="FA", seq=sc, ack=ss))
        agregar(e_sc / TCP(sport=dport, dport=sport, flags="FA", seq=ss, ack=sc + 1))
        agregar(e_cs / TCP(sport=sport, dport=dport, flags="A", seq=sc + 1, ack=ss + 1))

    cli, srv, dns = "10.10.0.23", "10.10.0.5", "10.10.0.1"
    for nombre in ("cafenebulosa.test", "ftp.cafenebulosa.test"):
        tid = random.randint(1, 65000)
        agregar(Ether(src=mac_cli, dst=mac_srv) / IP(src=cli, dst=dns) / UDP(sport=random.randint(40000, 60000), dport=53)
                / DNS(id=tid, rd=1, qd=DNSQR(qname=nombre)), 0.5)
        agregar(Ether(src=mac_srv, dst=mac_cli) / IP(src=dns, dst=cli) / UDP(sport=53, dport=paquetes[-1][UDP].sport)
                / DNS(id=tid, qr=1, aa=1, rd=1, ra=1, qd=DNSQR(qname=nombre), an=DNSRR(rrname=nombre, rdata=srv)))

    sesion_tcp(cli, srv, 51544, 80, [
        ("c", "GET /menu HTTP/1.1\r\nHost: cafenebulosa.test\r\nUser-Agent: Mozilla/5.0\r\nAccept: */*\r\n\r\n"),
        ("s", "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: 46\r\n\r\n"
              "<html><body><h1>Menu del dia</h1></body></html>"),
    ])
    sesion_tcp(cli, srv, 51560, 21, [
        ("s", "220 Servidor FTP de Cafe Nebulosa listo\r\n"),
        ("c", "USER empleado01\r\n"),
        ("s", "331 Password required for empleado01\r\n"),
        ("c", f"PASS {FLAGS['forense_trafico']}\r\n"),
        ("s", "230 User empleado01 logged in\r\n"),
        ("c", "SYST\r\n"),
        ("s", "215 UNIX Type: L8\r\n"),
        ("c", "PWD\r\n"),
        ("s", "257 \"/home/empleado01\" is the current directory\r\n"),
        ("c", "QUIT\r\n"),
        ("s", "221 Goodbye.\r\n"),
    ])
    sesion_tcp(cli, srv, 51577, 80, [
        ("c", "GET /contacto HTTP/1.1\r\nHost: cafenebulosa.test\r\nUser-Agent: Mozilla/5.0\r\n\r\n"),
        ("s", "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: 44\r\n\r\n"
              "<html><body><p>hola@cafenebulosa</p></body>"),
    ])
    wrpcap(str(ruta), paquetes)


def forense():
    base = RETOS / "forense"

    gato = base / "01_metadatos" / "gato.jpg"
    gato.parent.mkdir(parents=True, exist_ok=True)
    imagen_gato(gato)
    ejecutar("exiftool", "-q", "-overwrite_original",
             "-Artist=Agente K", "-ImageDescription=Mi gato Michi tomando sol",
             "-Make=NebulaCam", "-Model=NC-2026", f"-Comment={FLAGS['forense_metadatos']}", str(gato))

    escribir(base / "02_extension" / "foto_vacaciones.png",
             zip_en_memoria({"flag.txt": f"La extensión mentía: esto era un ZIP.\n{FLAGS['forense_extension']}\n"}),
             binario=True)

    cebolla = base / "03_cebolla" / "cebolla.jpg"
    cebolla.parent.mkdir(parents=True, exist_ok=True)
    imagen_cebolla(cebolla)
    trabajo = SALIDA / "_tmp"
    trabajo.mkdir(exist_ok=True)
    escribir(trabajo / "mensaje.txt", base64.b64encode(FLAGS["forense_cebolla"].encode()).decode() + "\n")
    ejecutar("steghide", "embed", "-cf", str(cebolla), "-ef", "mensaje.txt",
             "-p", "cebolla", "-f", "-q", cwd=trabajo)
    ejecutar("exiftool", "-q", "-overwrite_original", "-Comment=la clave es cebolla", str(cebolla))
    # Verificación: la extracción debe funcionar después de editar los metadatos
    ejecutar("steghide", "extract", "-sf", str(cebolla), "-p", "cebolla",
             "-xf", str(trabajo / "verificacion.txt"), "-f", "-q")
    assert (trabajo / "verificacion.txt").read_text() == (trabajo / "mensaje.txt").read_text()
    shutil.rmtree(trabajo)

    paisaje = base / "04_paisaje" / "paisaje.jpg"
    paisaje.parent.mkdir(parents=True, exist_ok=True)
    imagen_paisaje(paisaje)
    with open(paisaje, "ab") as f:
        f.write(zip_en_memoria({"secreto/flag.txt": f"¡binwalk lo encontró!\n{FLAGS['forense_paisaje']}\n"}))

    pcap = base / "05_trafico" / "captura.pcap"
    pcap.parent.mkdir(parents=True, exist_ok=True)
    captura_ftp(pcap)


# ============================================================== REVERSING
def c_bytes(texto: str, clave: int) -> str:
    return ", ".join(f"0x{ord(c) ^ clave:02x}" for c in texto) + f", 0x{clave:02x}"


def reversing():
    base = RETOS / "reversing"
    fuentes = SALIDA / "_fuentes"
    fuentes.mkdir(exist_ok=True)
    opciones = ["gcc", "-O0", "-no-pie", "-fcf-protection=none", "-Wl,-z,lazy"]

    (fuentes / "programa.c").write_text(f"""\
#include <stdio.h>
static const char *mensaje_oculto = "{FLAGS['rev_cadenas']}";
int main(int argc, char **argv) {{
    (void)argv;
    if (argc == 4242) puts(mensaje_oculto);
    puts("Este programa no tiene secretos... ¿o sí?");
    return 0;
}}
""")
    (base / "01_cadenas").mkdir(parents=True, exist_ok=True)
    ejecutar(*opciones, "-o", str(base / "01_cadenas" / "programa"), str(fuentes / "programa.c"))

    clave, flag = "sup3r_cl4v3", FLAGS["rev_login"]
    (fuentes / "login.c").write_text(f"""\
#include <stdio.h>
#include <string.h>

/* La clave y la flag van ofuscadas con XOR para que strings no las muestre.
   Se decodifican en memoria: ltrace puede ver la comparación con strcmp. */
static const unsigned char CLAVE[] = {{ {c_bytes(clave, 0x5A)} }};
static const unsigned char FLAG[]  = {{ {c_bytes(flag, 0x3C)} }};

static void decodificar(const unsigned char *in, char *out, size_t n, unsigned char k) {{
    for (size_t i = 0; i < n; i++) out[i] = (char)(in[i] ^ k);
    out[n] = '\\0';
}}

int main(void) {{
    char entrada[128], clave[64], flag[96];
    printf("Ingresa la clave: ");
    fflush(stdout);
    if (!fgets(entrada, sizeof entrada, stdin)) return 1;
    entrada[strcspn(entrada, "\\n")] = '\\0';
    decodificar(CLAVE, clave, sizeof CLAVE - 1, 0x5A);
    if (strcmp(entrada, clave) == 0) {{
        decodificar(FLAG, flag, sizeof FLAG - 1, 0x3C);
        printf("Acceso concedido. %s\\n", flag);
    }} else {{
        puts("Clave incorrecta");
    }}
    return 0;
}}
""")
    (base / "02_login").mkdir(parents=True, exist_ok=True)
    ejecutar(*opciones, "-o", str(base / "02_login" / "login"), str(fuentes / "login.c"))
    ejecutar("strip", str(base / "02_login" / "login"))
    shutil.rmtree(fuentes)


if __name__ == "__main__":
    if SALIDA.exists():
        shutil.rmtree(SALIDA)
    for paso in (linux, cripto, forense, reversing):
        paso()
        print(f"[ok] retos de {paso.__name__} generados")
