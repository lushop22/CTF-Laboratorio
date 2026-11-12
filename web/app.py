"""Café Nebulosa — sitio web ficticio e intencionalmente vulnerable.

Retos de Web (comentarios, robots.txt, validación en JavaScript, cookie
manipulable) y OSINT (blog con información personal y archivo histórico).
Solo para uso educativo dentro del laboratorio CTF Ciclo 1.
"""
import base64
import binascii
import json
import os

from flask import Flask, Response, make_response, render_template, request

from ctf_flags import normalizar_token, todas_las_flags, token_valido

RETOS_PATH = os.environ.get("RETOS_PATH", "/app/retos.json")

# Las flags se derivan del token personal del estudiante (LAB_TOKEN en .env).
# En el repositorio solo está la parte legible de cada flag.
_token = normalizar_token(os.environ.get("LAB_TOKEN", ""))
TOKEN_OK = token_valido(_token)
if not TOKEN_OK:
    print("[web] AVISO: LAB_TOKEN no configurado o inválido: las flags no serán aceptadas.", flush=True)
    _token = "0" * 16

with open(RETOS_PATH, encoding="utf-8") as f:
    FLAGS = todas_las_flags(_token, json.load(f)["retos"])

app = Flask(__name__)


@app.context_processor
def estado_token():
    return {"sin_token": not TOKEN_OK}


def b64(texto: str) -> str:
    return base64.b64encode(texto.encode()).decode()


POSTS = [
    {
        "id": 1,
        "fecha": "03/02/2026",
        "titulo": "¡Abrimos una nueva sede!",
        "texto": "Después de dos años de trabajo, Café Nebulosa abre su segunda sede. "
                 "Gracias a todos los clientes que nos acompañaron desde el primer día.",
    },
    {
        "id": 2,
        "fecha": "18/03/2026",
        "titulo": "Mi método para un V60 perfecto",
        "texto": "Molienda media, agua a 92 °C y una proporción 1:15. El secreto está en "
                 "la paciencia durante el florecimiento: 30 segundos, ni uno menos.",
    },
    {
        "id": 3,
        "fecha": "09/05/2026",
        "titulo": "Un día especial en casa 🐶",
        "texto": "Hoy no hablo de café. Hoy cumple 9 años Canelo, mi primera mascota y el "
                 "mejor compañero de mañanas que he tenido. Llegó a casa cuando yo tenía "
                 "15 años y desde entonces me espera en la puerta cada tarde.",
    },
    {
        "id": 4,
        "fecha": "21/08/2026",
        "titulo": "Nuevo menú de temporada",
        "texto": "Llegó el invierno y con él nuestro chocolate caliente con canela y el "
                 "cold brew de naranja. ¡Los esperamos!",
    },
]


# ------------------------------------------------------------------ Web
@app.route("/")
def inicio():
    # Reto web_comentarios: la flag está en un comentario HTML de esta página.
    return render_template("inicio.html", flag_comentario=FLAGS["web_comentarios"])


@app.route("/menu")
def menu():
    return render_template("menu.html")


@app.route("/robots.txt")
def robots():
    contenido = (
        "# Café Nebulosa\n"
        "User-agent: *\n"
        "Disallow: /panel-secreto/\n"
        "Disallow: /archivo/\n"
    )
    return Response(contenido, mimetype="text/plain")


@app.route("/panel-secreto/")
def panel_secreto():
    return render_template("panel_secreto.html", flag=FLAGS["web_robots"])


@app.route("/empleados")
def empleados():
    return render_template("empleados.html")


@app.route("/js/login.js")
def login_js():
    # Reto web_js: la "validación" ocurre en el cliente. La contraseña va en
    # Base64 y la flag invertida: ambas son visibles para quien lea el script.
    clave_b64 = b64("Nebulosa#2026")
    flag_invertida = FLAGS["web_js"][::-1]
    js = render_template("login.js", clave_b64=clave_b64, flag_invertida=flag_invertida)
    return Response(js, mimetype="application/javascript")


@app.route("/perfil")
def perfil():
    # Reto web_cookie: el rol se guarda en una cookie en Base64 y el servidor
    # confía en ella sin validarla (control de acceso roto).
    valor = request.cookies.get("rol")
    rol = None
    if valor:
        try:
            rol = base64.b64decode(valor, validate=True).decode().strip()
        except (binascii.Error, UnicodeDecodeError):
            rol = None
    if rol is None:
        rol = "user"
        respuesta = make_response(render_template("perfil.html", rol=rol, flag=None))
        respuesta.set_cookie("rol", b64("user"))
        return respuesta
    flag = FLAGS["web_cookie"] if rol == "admin" else None
    return render_template("perfil.html", rol=rol, flag=flag)


# ------------------------------------------------------------------ OSINT
@app.route("/blog")
def blog():
    return render_template("blog.html", posts=POSTS)


@app.route("/blog/<int:post_id>")
def post(post_id):
    p = next((p for p in POSTS if p["id"] == post_id), None)
    if not p:
        return render_template("404.html"), 404
    return render_template("post.html", post=p)


@app.route("/recuperar", methods=["GET", "POST"])
def recuperar():
    mensaje, flag = None, None
    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip().lower()
        respuesta = request.form.get("respuesta", "").strip().lower()
        if usuario != "mtello":
            mensaje = "Ese usuario no existe."
        elif respuesta != "canelo":
            mensaje = "Respuesta incorrecta a la pregunta de seguridad."
        else:
            flag = FLAGS["osint_perfil"]
    return render_template("recuperar.html", mensaje=mensaje, flag=flag)


@app.route("/contacto")
def contacto():
    return render_template("contacto.html", antiguo=False, flag=None)


@app.route("/archivo/")
def archivo():
    return render_template("archivo.html")


@app.route("/archivo/2023-06-14/contacto")
def archivo_contacto_2023():
    return render_template("contacto.html", antiguo=True, flag=FLAGS["osint_archivo"])


@app.route("/archivo/2024-11-02/contacto")
def archivo_contacto_2024():
    return render_template("contacto.html", antiguo=True, flag=None)


@app.errorhandler(404)
def no_encontrado(_e):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
