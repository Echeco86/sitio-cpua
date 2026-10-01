/* =========================================================
   CPUA · Encabezado, pie y utilidades comunes
   Para cambiar datos de contacto o el menú, editá CONFIG.
   ========================================================= */
const CONFIG = {
  contacto: {
    horario: "Lunes a viernes de 8:00 a 14:00 h",
    direccion: "José Hernández 299, planta alta del Registro Civil",
    ciudad: "Villa Carlos Paz, Córdoba",
    telefono: "(03541) 436434",
    telefonoLink: "+543541436434",
    email: "cpua@cpua.gov.ar",
    instagram: "https://www.instagram.com/carlospazcpua/",
    instagramTexto: "@carlospazcpua",
    facebook: "https://www.facebook.com/search/top?q=Carlos%20Paz%20Cpua",
    youtube: "https://www.youtube.com/results?search_query=Cpua+carlos+paz",
  },
  menu: [
    { href: "index.html", texto: "Inicio" },
    { href: "cpua.html", texto: "El CPUA" },
    { href: "archivo.html", texto: "Buscador" },
    { href: "normativa.html", texto: "Normativa" },
    { href: "map.html", texto: "Área Protegida" },
    { href: "acciones.html", texto: "Acciones" },
    { href: "index.html#contacto", texto: "Contacto", cta: true },
  ],
};

const ICONOS = {
  menu: '<path d="M4 7h16M4 12h16M4 17h16"/>',
  cerrar: '<path d="M6 6l12 12M18 6 6 18"/>',
  flecha: '<path d="M5 12h14M13 6l6 6-6 6"/>',
  externo: '<path d="M14 4h6v6M20 4l-9 9M18 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5"/>',
  descarga: '<path d="M12 4v11m0 0-4-4m4 4 4-4M5 20h14"/>',
  buscar: '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>',
  doc: '<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5M9 13h6M9 17h6"/>',
  personas: '<circle cx="9" cy="8" r="3.2"/><path d="M3 20c0-3.3 2.7-6 6-6s6 2.7 6 6"/><circle cx="17" cy="9" r="2.5"/><path d="M16 14.2c2.9.3 5 2.6 5 5.8"/>',
  edificio: '<path d="M4 21V5a1 1 0 0 1 1-1h9a1 1 0 0 1 1 1v16M15 10h4a1 1 0 0 1 1 1v10M3 21h18M8 8h3M8 12h3M8 16h3"/>',
  hoja: '<path d="M5 19c0-8 5-14 15-15-1 10-7 15-15 15z"/><path d="M5 19c3-4 6-7 10-9"/>',
  mapa: '<path d="m9 4-6 2v14l6-2 6 2 6-2V4l-6 2z"/><path d="M9 4v14M15 6v14"/>',
  archivo: '<rect x="3" y="4" width="18" height="5" rx="1"/><path d="M5 9v10a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V9M10 13h4"/>',
  balanza: '<path d="M12 4v16M7 20h10M5 7h14M5 7l-3 7a3 3 0 0 0 6 0zM19 7l-3 7a3 3 0 0 0 6 0z"/>',
  camara: '<path d="M4 8a2 2 0 0 1 2-2h2l1.5-2h5L16 6h2a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2z"/><circle cx="12" cy="13" r="3.5"/>',
  reloj: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
  ubicacion: '<path d="M12 21s-7-6.2-7-12a7 7 0 0 1 14 0c0 5.8-7 12-7 12z"/><circle cx="12" cy="9" r="2.5"/>',
  telefono: '<path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2"/>',
  mail: '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/>',
  instagram: '<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r=".6" fill="currentColor"/>',
  facebook: '<path d="M14 8h3V4h-3a4 4 0 0 0-4 4v3H7v4h3v6h4v-6h3l1-4h-4V8.5a.5.5 0 0 1 .5-.5z"/>',
  youtube: '<rect x="2.5" y="5.5" width="19" height="13" rx="4"/><path d="m10 9 5 3-5 3z" fill="currentColor"/>',
  info: '<circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7.5v.5"/>',
  calendario: '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/>',
};

function icono(nombre, extra = "") {
  return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" ${extra}>${ICONOS[nombre] || ""}</svg>`;
}

function paginaActual() {
  const p = location.pathname.split("/").pop() || "index.html";
  return p === "" ? "index.html" : p;
}

function pintarEncabezado() {
  const actual = paginaActual();
  const items = CONFIG.menu.map((m) => {
    const activo = m.href === actual ? ' aria-current="page"' : "";
    return `<li${m.cta ? ' class="cta"' : ""}><a href="${m.href}"${activo}>${m.texto}</a></li>`;
  }).join("");
  const header = document.createElement("header");
  header.className = "encabezado";
  header.innerHTML = `
    <div class="contenedor">
      <a class="marca" href="index.html" aria-label="CPUA — Inicio">
        <img src="assets/img/isotipo.png" alt="" width="96" height="40">
        <span><b>CPUA</b><small>Consejo de Planificación Urbano Ambiental</small></span>
      </a>
      <button class="boton-menu" aria-expanded="false" aria-controls="navegacion" aria-label="Abrir menú">${icono("menu")}</button>
      <nav class="navegacion" id="navegacion" aria-label="Principal"><ul class="menu">${items}</ul></nav>
    </div>`;
  document.body.prepend(header);
  const saltar = document.createElement("a");
  saltar.className = "saltar"; saltar.href = "#contenido"; saltar.textContent = "Saltar al contenido";
  document.body.prepend(saltar);

  const boton = header.querySelector(".boton-menu");
  const nav = header.querySelector(".navegacion");
  boton.addEventListener("click", () => {
    const abierto = nav.classList.toggle("abierta");
    boton.setAttribute("aria-expanded", abierto);
    boton.innerHTML = icono(abierto ? "cerrar" : "menu");
  });
  nav.addEventListener("click", (e) => { if (e.target.closest("a")) { nav.classList.remove("abierta"); boton.setAttribute("aria-expanded", false); boton.innerHTML = icono("menu"); } });
  const sombra = () => header.classList.toggle("con-sombra", scrollY > 8);
  addEventListener("scroll", sombra, { passive: true }); sombra();
}

function pintarPie() {
  const c = CONFIG.contacto;
  const footer = document.createElement("footer");
  footer.className = "pie";
  footer.innerHTML = `
    <div class="contenedor">
      <div class="cols">
        <div>
          <img src="assets/img/logo-cpua-blanco.png" alt="CPUA — Consejo de Planificación Urbano Ambiental" width="110" height="64">
          <p>Órgano consultivo del Concejo de Representantes de Villa Carlos Paz. Creado por la Carta Orgánica Municipal y reglamentado por la Ordenanza Nº 4951.</p>
          <div class="redes">
            <a href="${c.instagram}" target="_blank" rel="noopener" aria-label="Instagram">${icono("instagram")}</a>
            <a href="${c.facebook}" target="_blank" rel="noopener" aria-label="Facebook">${icono("facebook")}</a>
            <a href="${c.youtube}" target="_blank" rel="noopener" aria-label="YouTube">${icono("youtube")}</a>
          </div>
        </div>
        <div>
          <h4>El Consejo</h4>
          <ul>
            <li><a href="cpua.html#quienes-somos">¿Quiénes somos?</a></li>
            <li><a href="cpua.html#integrantes">Integración</a></li>
            <li><a href="cpua.html#funciones">Funciones</a></li>
            <li><a href="cpua.html#comision">Comisión Plenaria</a></li>
            <li><a href="map.html">Área Protegida · MAP</a></li>
          </ul>
        </div>
        <div>
          <h4>Documentación</h4>
          <ul>
            <li><a href="archivo.html#actas">Actas</a></li>
            <li><a href="archivo.html#dictamenes">Dictámenes</a></li>
            <li><a href="archivo.html#ordenanzas">Ordenanzas</a></li>
            <li><a href="normativa.html#codigo">Código de Edificación</a></li>
            <li><a href="normativa.html#documentos">Documentos</a></li>
            <li><a href="normativa.html#mapas">Mapas y enlaces</a></li>
          </ul>
        </div>
        <div>
          <h4>Contacto</h4>
          <ul>
            <li>${c.horario}</li>
            <li>${c.direccion}</li>
            <li><a href="tel:${c.telefonoLink}">${c.telefono}</a></li>
            <li><a href="mailto:${c.email}">${c.email}</a></li>
          </ul>
        </div>
      </div>
      <div class="legal">
        <span>© ${new Date().getFullYear()} CPUA · Municipalidad de Villa Carlos Paz</span>
        <span>Consejo de Planificación Urbano Ambiental</span>
      </div>
    </div>`;
  document.body.append(footer);
}

function pintarContacto() {
  const el = document.getElementById("datos-contacto");
  if (!el) return;
  const c = CONFIG.contacto;
  el.innerHTML = `
    <li><div><span class="ic">${icono("telefono")}</span><span><small>Teléfono</small><a href="tel:${c.telefonoLink}" style="color:inherit;text-decoration:none">${c.telefono}</a></span></div></li>
    <li><a href="mailto:${c.email}"><span class="ic">${icono("mail")}</span><span><small>Correo electrónico</small>${c.email}</span></a></li>
    <li><a href="${c.instagram}" target="_blank" rel="noopener"><span class="ic">${icono("instagram")}</span><span><small>Instagram</small>${c.instagramTexto}</span></a></li>
    <li><a href="${c.facebook}" target="_blank" rel="noopener"><span class="ic">${icono("facebook")}</span><span><small>Facebook</small>Carlos Paz Cpua</span></a></li>`;
  document.querySelectorAll("[data-contacto]").forEach((n) => { n.textContent = c[n.dataset.contacto]; });
}

function activarAparicion() {
  const els = document.querySelectorAll(".aparecer");
  if (!("IntersectionObserver" in window)) { els.forEach((e) => e.classList.add("visible")); return; }
  const io = new IntersectionObserver((ents) => ents.forEach((en) => {
    if (en.isIntersecting) { en.target.classList.add("visible"); io.unobserve(en.target); }
  }), { rootMargin: "0px 0px -60px 0px" });
  els.forEach((e) => io.observe(e));
}

function pintarIconos() {
  document.querySelectorAll("[data-icono]").forEach((n) => { n.innerHTML = icono(n.dataset.icono); });
}

/* ---- utilidades de formato compartidas ---- */
const MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"];
function fechaLarga(d) {
  if (!d) return "";
  const [a, m, dia] = d.split("-").map(Number);
  return dia ? `${dia} de ${MESES[m - 1]} de ${a}` : `${MESES[m - 1][0].toUpperCase()}${MESES[m - 1].slice(1)} de ${a}`;
}
function tamano(kb) {
  if (!kb) return "";
  return kb >= 1024 ? `${(kb / 1024).toFixed(1).replace(".", ",")} MB` : `${kb} KB`;
}
function escapar(s) {
  return String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}
const ETIQUETAS_TIPO = {
  acta: ["ACTA", "Acta"], foro: ["FORO", "Foro Urbano Ambiental"], anexo: ["ANEXO", "Documento adjunto"],
  dictamen: ["DICT", "Dictamen"], resolucion: ["RES", "Resolución"], complementario: ["ANEXO", "Documento complementario"],
};
function filaDocumento(d, extra = "") {
  const [corto, largo] = ETIQUETAS_TIPO[d.t] || ["DOC", "Documento"];
  const tema = d.tema && d.tema !== d.titulo ? `<span class="tema">${escapar(d.tema)}</span>` : "";
  const chips = [];
  if (d.minoria) chips.push('<span class="chip min">Postura / minoría</span>');
  if (d.rel) chips.push(`<span class="chip">Adjunto al Acta Nº ${d.rel}</span>`);
  if (d.grupo) chips.push(`<span class="chip">${escapar(d.grupo)}</span>`);
  const meta = [d.d ? fechaLarga(d.d) : String(d.y), largo, tamano(d.kb)].filter(Boolean).map((x) => `<span>${x}</span>`).join("");
  return `<li class="doc"><a href="${encodeURI(d.url)}" target="_blank" rel="noopener">
      <span class="tipo t-${d.t}" aria-hidden="true">${corto}</span>
      <span><span class="titulo">${escapar(d.titulo)}</span>${tema}<span class="meta">${meta}${chips.join("")}</span>${extra}</span>
      <span class="ver">Ver PDF ${icono("externo")}</span></a></li>`;
}

let _archivo;
function cargarArchivo() {
  if (!_archivo) _archivo = fetch("data/archivo.json").then((r) => r.json()).then((j) => j.documentos || []);
  return _archivo;
}

document.addEventListener("DOMContentLoaded", () => {
  pintarEncabezado();
  pintarPie();
  pintarContacto();
  pintarIconos();
  activarAparicion();
});
