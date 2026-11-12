"""Derivación de flags personales del laboratorio CTF Ciclo 1.

En el repositorio NO hay flags. Cada estudiante recibe un token personal al
registrarse en la plataforma y lo configura en su laboratorio (LAB_TOKEN).
Al arrancar, el ctf-kit y la web generan las flags con:

    CICLO1{<base>_<HMAC-SHA256(token, id_del_reto)[:8]>}

La plataforma guarda el token de cada usuario y recalcula la flag esperada,
así que la flag de un compañero no sirve en otra cuenta.

Este archivo lo comparten plataforma/, web/ y kit/ (se copia al construir).
"""
import hashlib
import hmac
import re
import secrets

PREFIJO = "CICLO1"
_TOKEN_RE = re.compile(r"^[0-9a-f]{16}$")


def normalizar_token(token: str) -> str:
    """Acepta el token con o sin guiones/espacios y en cualquier caso."""
    return re.sub(r"[\s\"'-]", "", token or "").lower()


def token_valido(token: str) -> bool:
    return bool(_TOKEN_RE.match(normalizar_token(token)))


def nuevo_token() -> str:
    return secrets.token_hex(8)


def mostrar_token(token: str) -> str:
    """16 hex → 'abcd-ef01-2345-6789' (más fácil de copiar y dictar)."""
    t = normalizar_token(token)
    return "-".join(t[i:i + 4] for i in range(0, len(t), 4))


def _hmac(token: str, reto_id: str) -> str:
    return hmac.new(normalizar_token(token).encode(), reto_id.encode(), hashlib.sha256).hexdigest()


def sufijo_numerico(token: str, reto_id: str) -> str:
    """4 dígitos (1000-9999) derivados del token: para retos tipo «palabra»."""
    return str(int(_hmac(token, reto_id)[:8], 16) % 9000 + 1000)


def flag_reto(token: str, reto: dict) -> str:
    """reto: entrada de config/retos.json (usa 'id', 'flag_base' y 'tipo')."""
    base = reto["flag_base"]
    if reto.get("tipo") == "palabra":
        return f"{PREFIJO}{{{base}{sufijo_numerico(token, reto['id'])}}}"
    return f"{PREFIJO}{{{base}_{_hmac(token, reto['id'])[:8]}}}"


def todas_las_flags(token: str, retos: list) -> dict:
    return {r["id"]: flag_reto(token, r) for r in retos}
