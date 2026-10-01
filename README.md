# Sitio web del CPUA · Villa Carlos Paz

Página institucional del **Consejo de Planificación Urbano Ambiental (CPUA)**, hecha en HTML, CSS y JavaScript puro para publicarse gratis en **GitHub Pages**. No necesita compilación ni servidor: lo que está en esta carpeta es exactamente lo que se publica.

## Estructura

```
sitio-cpua/
├── index.html          Inicio (portada, accesos, últimas actas/dictámenes, contacto)
├── cpua.html           El CPUA: quiénes somos, integración, funciones, dictámenes, foro, Comisión Plenaria
├── archivo.html        Buscador de actas, dictámenes y resoluciones
├── normativa.html      Código de Edificación (Ord. 4021), documentos y mapas
├── map.html            Área Protegida · MAP · Camiare
├── acciones.html       Acciones y galería
├── assets/             Estilos, scripts e imágenes
├── data/
│   ├── archivo.json    Índice del archivo (lo genera el script, no editar a mano)
│   ├── comision.json   Integrantes de la Comisión Plenaria
│   ├── documentos.json Documentos de referencia (Carta Orgánica, etc.)
│   └── acciones.json   Acciones y fotos de la galería
├── archivo/            PDF de actas, dictámenes y resoluciones (generado)
└── scripts/generar_archivo.py
```

## Buscador

La página `archivo.html` busca en actas, dictámenes y resoluciones:

- **Palabras clave** en el título, el tema y **dentro del texto de cada PDF** (se puede desactivar). Entre comillas busca la frase exacta: `"retiro de frente"`.
- **Rango de fechas** (desde / hasta) y atajos: último año, últimos 5 años, este año.
- **Orden** por relevancia, más recientes o más antiguos. Muestra extractos con las palabras resaltadas.
- Cada búsqueda queda en la dirección de la página, así que se puede compartir el enlace.
- La pestaña **Ordenanzas** enlaza al Digesto Legislativo Municipal y da acceso directo a la Ordenanza 4021 y a la Carta Orgánica.

El texto completo se guarda en `data/texto.json` (unos 13 MB, que GitHub sirve comprimidos a ~3 MB) y solo se descarga cuando alguien busca.

## Agregar actas o dictámenes nuevos

1. Guardar el PDF en la carpeta de siempre (`ACTAS/ACTAS/ACTAS 2026/…` o `DICTAMENES/Dictámenes 2026/…`), con el nombre habitual, por ejemplo `Acta N 496 - 09 de octubre 2026.pdf` o `Dictamen N 3 - Tema.pdf`.
2. Abrir una terminal en la carpeta `sitio-cpua` y ejecutar:
   ```
   python scripts/generar_archivo.py
   ```
   El script copia los PDF nuevos con nombres limpios, actualiza `data/archivo.json`, extrae el texto para el buscador (`data/texto.json`) y avisa si algún archivo es demasiado pesado (los de más de 45 MB se comprimen con Ghostscript si está instalado).
3. En GitHub Desktop: *Commit to main* → *Push origin*.

Para extraer el texto en Windows hace falta una de estas dos cosas: `pip install pypdf` (lo más simple) o Poppler (`pdftotext`). Los PDF escaneados sin texto (hoy son 14) se pueden leer con `python scripts/generar_archivo.py --ocr`, que requiere Tesseract con el idioma español.

Reglas que usa el script para ordenar el archivo:

- Las carpetas `_EDITABLES` se ignoran.
- En actas: si el nombre dice “FORO” se clasifica como Foro Urbano Ambiental; si dice “ANEXO” o está dentro de la carpeta de un acta, como documento adjunto; si hay duplicados del mismo número, se prefiere la versión “corregida”.
- En dictámenes: los archivos que empiezan con “Dictamen”/“Resolución” son principales; los anexos, notas y archivos en subcarpetas se muestran como documentos complementarios.
- La fecha se lee del nombre del archivo (“13 de marzo 2009”); si falta el año se toma el de la carpeta.

## Editar contenidos

| Qué | Dónde |
|---|---|
| Integrantes de la Comisión | `data/comision.json` |
| Documentos (Carta Orgánica, estudios…) | `data/documentos.json` → poner el PDF en `documentos/` y completar `"url": "documentos/carta-organica.pdf"`. La Carta Orgánica también aparece en la pestaña Ordenanzas del buscador (`archivo.html`). |
| Acciones y galería | `data/acciones.json` (las fotos van en `assets/img/`) |
| Teléfono, mail, redes, horario, menú | `assets/js/sitio.js` → objeto `CONFIG` al inicio |
| Textos institucionales | directamente en cada `.html` |


