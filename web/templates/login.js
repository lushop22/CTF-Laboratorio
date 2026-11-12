// Validación del login de empleados - Café Nebulosa
// TODO: mover esta validación al servidor (¡aquí cualquiera puede leerla!)

const USUARIO_VALIDO = "barista";
const CLAVE_CODIFICADA = "{{ clave_b64 }}";   // Base64 para que "nadie" la lea
const PREMIO = "{{ flag_invertida }}";        // invertida por "seguridad"

document.getElementById("form-login").addEventListener("submit", function (e) {
  e.preventDefault();
  const usuario = document.getElementById("usuario").value.trim();
  const clave = document.getElementById("clave").value;
  const resultado = document.getElementById("resultado");

  if (usuario === USUARIO_VALIDO && clave === atob(CLAVE_CODIFICADA)) {
    const flag = PREMIO.split("").reverse().join("");
    resultado.innerHTML = '<span class="flag">' + flag + "</span>";
  } else {
    resultado.innerHTML = '<span class="error">Usuario o contraseña incorrectos.</span>';
  }
});
