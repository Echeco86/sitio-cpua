#!/usr/bin/env python3
"""
Genera el Archivo documental del sitio del CPUA.

Recorre las carpetas de ACTAS y DICTÁMENES (tal como se guardan en la oficina),
copia los PDF al sitio con nombres limpios (sin tildes ni espacios) y escribe
data/archivo.json, que la página "Archivo" usa para listar y buscar.

Uso (desde la carpeta del sitio):
    python scripts/generar_archivo.py
    python scripts/generar_archivo.py --actas "../ACTAS/ACTAS" --dictamenes "../DICTAMENES"

También extrae el texto de cada PDF (data/texto.json) para que el buscador
encuentre palabras dentro de los documentos. Usa "pdftotext" (Poppler) si está
instalado; si no, la librería de Python "pypdf" (pip install pypdf). El texto
ya extraído se guarda en scripts/.cache/ para no repetir el trabajo.
Con --ocr también se lee el texto de los PDF escaneados (requiere Tesseract).

Cada vez que se sumen actas o dictámenes nuevos a las carpetas de origen,
basta con volver a correr este script y subir los cambios a GitHub.
Las carpetas "_EDITABLES" se ignoran siempre.
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
import unicodedata
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
LIMITE_MB = 45  # GitHub rechaza archivos de más de 100 MB y advierte desde 50 MB

MESES = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
    "julio": 7, "agosto": 8, "septiembre": 9, "setiembre": 9, "octubre": 10,
    "noviembre": 11, "diciembre": 12,
}
RE_FECHA = re.compile(
    r"(?:(?<!\d)(\d{1,2})\s*(?:de\s+)?)?(?<![a-z])(" + "|".join(MESES) + r")\b(?:\s*(?:de\s*)?(\d{4}))?",
    re.I,
)
RE_NUM_ACTA = re.compile(r"acta\s*(?:n\s*[°ºo]?\.?\s*)?(\d{1,3})\b", re.I)
RE_NUM_DOC = re.compile(
    r"(?:dict\w*|resoluci\w*)\s*(?:n\s*[°ºo]?\.?\s*)?(\d{1,3})(?!\d)", re.I
)
RE_ANIO = re.compile(r"(20\d{2})")


def sin_tildes(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def slug(s, largo=70):
    s = sin_tildes(s).lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:largo].strip("-") or "documento"


def anio_de(path):
    for parte in reversed(path.parts):
        m = RE_ANIO.search(parte)
        if m:
            return int(m.group(1))
    return None


def fecha_de(textos, anio):
    """Busca '13 de marzo 2009' en el nombre y, si no, en las carpetas contenedoras."""
    for t in textos:
        m = RE_FECHA.search(t)
        if not m:
            continue
        dia, mes, a = m.group(1), MESES[m.group(2).lower()], m.group(3)
        a = int(a) if a else anio
        if not a:
            continue
        if dia and 1 <= int(dia) <= 31:
            try:
                return date(a, mes, int(dia)).isoformat()
            except ValueError:
                pass
        return f"{a}-{mes:02d}"
    return None


def limpiar_titulo(nombre):
    t = re.sub(r"\.(pdf|docx?)$", "", nombre, flags=re.I)
    t = re.sub(r"\.(pdf|docx?)$", "", t, flags=re.I)
    t = t.replace("_", " ")
    t = re.sub(r"\s*\(\d+\)\s*$", "", t)
    t = re.sub(r"\s+", " ", t).strip(" .-")
    return t


def tema_de(nombre):
    """'Dictamen Nº 001-09 Urb. altos de...' -> 'Urb. altos de'"""
    t = limpiar_titulo(nombre)
    t = re.sub(r"^(dict\w*|dirctamen|ditctamen|resoluci\w*)\s*(n\s*[°ºo]?\.?)?\s*[\d.]*\s*", "", t, flags=re.I)
    t = re.sub(r"^[-–\s.]*((19|20)?\d{2}(?!\d))?[\s.\-–]*", "", t)
    t = re.sub(r"^[-–\s.]+", "", t)
    t = re.sub(r"(?i)^(\d{1,2}\s+)?de\s+(" + "|".join(MESES) + r")\s*(de\s*)?\d{0,4}$", "", t).strip(" -–")
    return t[:1].upper() + t[1:] if t else ""


def copiar(origen, destino, avisos):
    destino.parent.mkdir(parents=True, exist_ok=True)
    tam = origen.stat().st_size / 1e6
    if destino.exists() and destino.stat().st_size > 0 and tam <= LIMITE_MB:
        if destino.stat().st_size == origen.stat().st_size:
            return True
    if tam <= LIMITE_MB:
        shutil.copy2(origen, destino)
        return True
    # PDF muy pesado: se intenta comprimir con Ghostscript
    if destino.exists() and destino.stat().st_size / 1e6 <= LIMITE_MB:
        return True
    for gs in ("gs", "gswin64c", "gswin32c"):
        try:
            subprocess.run(
                [gs, "-sDEVICE=pdfwrite", "-dCompatibilityLevel=1.5", "-dPDFSETTINGS=/ebook",
                 "-dNOPAUSE", "-dQUIET", "-dBATCH", f"-sOutputFile={destino}", str(origen)],
                check=True, timeout=900,
            )
            nuevo = destino.stat().st_size / 1e6
            if nuevo <= LIMITE_MB:
                avisos.append(f"Comprimido {origen.name}: {tam:.0f} MB -> {nuevo:.0f} MB")
                return True
            destino.unlink()
            break
        except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
            continue
    avisos.append(f"OMITIDO (pesa {tam:.0f} MB, supera {LIMITE_MB} MB): {origen}")
    return False


def es_editable(p):
    return any(x.upper().startswith("_EDITABLE") for x in p.parts)


def pdfs(carpeta):
    return sorted(p for p in carpeta.rglob("*") if p.is_file() and p.suffix.lower() == ".pdf" and not es_editable(p))


def procesar_actas(carpeta, avisos):
    items, vistos = [], {}
    for p in pdfs(carpeta):
        rel = p.relative_to(carpeta)
        anio = anio_de(rel)
        nombre = p.name
        up = sin_tildes(nombre).upper()
        m = RE_NUM_ACTA.search(nombre)
        padres = [x for x in rel.parts[:-1]]
        padre_acta = None
        for x in padres:
            mm = RE_NUM_ACTA.search(x)
            if mm:
                padre_acta = int(mm.group(1))
        fecha = fecha_de([nombre] + list(reversed(padres)), anio)

        if "FORO" in up and m and "BIS" not in up:
            tipo, num = "acta", int(m.group(1))
            titulo = f"Acta Nº {num} · Foro Urbano Ambiental"
        elif "FORO" in up:
            tipo, num = "foro", None
            resto = limpiar_titulo(nombre)
            resto = re.sub(r"(?i)^acta\s*(n\s*[°º]?\s*\d+\s*bis)?[\s\-–]*", "", resto)
            resto = re.sub(r"(?i)^foro\s*(urbano\s*ambiental)?[\s\-–]*", "", resto)
            resto = re.sub(r"(?i),?\s*\d{1,2}\s+de\s+\w+\s+de\s+\d{4}$", "", resto).strip(" -–,")
            titulo = "Foro Urbano Ambiental" + (f" — {resto[:1].upper()}{resto[1:]}" if resto else "")
        elif m and "ANEXO" not in up and "ASISTENCIA" not in up and not (padre_acta and int(m.group(1)) != padre_acta):
            tipo, num = "acta", int(m.group(1))
            titulo = f"Acta Nº {num}"
        else:
            tipo, num = "anexo", None
            titulo = limpiar_titulo(nombre)
            if m and "ANEXO" in up:
                padre_acta = int(m.group(1))

        if tipo == "acta":
            clave = (anio, num)
            prioridad = (0 if "CORREGID" in up else 1, 1 if ("DUDAS" in up or ".DOCX" in up or re.search(r"\(\d\)", nombre)) else 0, len(nombre))
            if clave in vistos:
                previo = vistos[clave]
                if prioridad < previo["_prio"]:
                    items.remove(previo)
                else:
                    continue
            base = f"acta-{num:03d}" + (f"-{fecha}" if fecha else "")
        else:
            base = slug(titulo)
        destino = Path("archivo") / "actas" / str(anio) / f"{base}.pdf"
        item = {"t": tipo, "y": anio, "n": num, "d": fecha, "titulo": titulo,
                "url": destino.as_posix(), "_src": p, "_prio": prioridad if tipo == "acta" else None}
        if padre_acta and tipo != "acta":
            item["rel"] = padre_acta
        items.append(item)
        if tipo == "acta":
            vistos[(anio, num)] = item
    return items


def procesar_dictamenes(carpeta, avisos):
    items = []
    for p in pdfs(carpeta):
        rel = p.relative_to(carpeta)
        anio = anio_de(rel)
        nombre = p.name
        up = sin_tildes(nombre).upper()
        raiz = sin_tildes(rel.parts[0]).upper()
        subcarpeta = rel.parts[1] if len(rel.parts) > 2 else None
        m = RE_NUM_DOC.search(nombre)
        es_resol = raiz.startswith("RESOLUC")
        es_principal = (
            (up.startswith("DICT") or up.startswith("DIRCT") or up.startswith("DITCT") or up.startswith("RESOLU"))
            and "ANEXO" not in up and "ANEZO" not in up and "INGRESO" not in up
        )
        if subcarpeta and not RE_NUM_DOC.search(subcarpeta) and "INGRESO" not in sin_tildes(subcarpeta).upper():
            # carpeta temática (p.ej. "Paseo de la Costa") -> documento complementario, salvo el propio dictamen
            es_principal = es_principal and "DICTAMEN" in up
        if es_principal:
            tipo = "resolucion" if es_resol else "dictamen"
            num = int(m.group(1)) if m else None
            tema = tema_de(nombre)
            titulo = ("Resolución" if es_resol else "Dictamen") + (f" Nº {num}" if num else " s/n")
        else:
            tipo, num = "complementario", None
            tema = limpiar_titulo(nombre)
            titulo = tema
            if m:
                num = int(m.group(1))
        minoria = "MINOR" in up or ("ADARSA" in up and tipo == "dictamen") or "POSTURA" in up
        base = slug(f"{tipo}-{num or ''}-{tema}")
        destino = Path("archivo") / ("resoluciones" if es_resol else "dictamenes") / str(anio) / f"{base}.pdf"
        item = {"t": tipo, "y": anio, "n": num, "d": fecha_de([nombre], anio) if RE_FECHA.search(nombre) else None,
                "titulo": titulo, "tema": tema, "url": destino.as_posix(), "_src": p}
        if subcarpeta and "INGRESO" not in sin_tildes(subcarpeta).upper():
            item["grupo"] = limpiar_titulo(subcarpeta)
        if minoria and tipo == "dictamen":
            item["minoria"] = True
        items.append(item)
    return items


MAX_CARACTERES = 60000  # por documento, para que el índice no sea enorme
CACHE = RAIZ / "scripts" / ".cache" / "texto.json"


def _pdftotext(pdf):
    try:
        r = subprocess.run(["pdftotext", "-enc", "UTF-8", "-q", str(pdf), "-"], capture_output=True, timeout=120)
        return r.stdout.decode("utf-8", "ignore")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None


def _pypdf(pdf):
    try:
        from pypdf import PdfReader
    except ImportError:
        return None
    try:
        return "\n".join((p.extract_text() or "") for p in PdfReader(str(pdf)).pages[:200])
    except Exception:
        return ""


def _ocr(pdf, paginas=12):
    import tempfile
    try:
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run(["pdftoppm", "-r", "200", "-gray", "-l", str(paginas), "-png", str(pdf), f"{tmp}/p"],
                           check=True, capture_output=True, timeout=600)
            partes = []
            for img in sorted(Path(tmp).glob("p*.png")):
                r = subprocess.run(["tesseract", str(img), "-", "-l", "spa"], capture_output=True, timeout=300)
                partes.append(r.stdout.decode("utf-8", "ignore"))
            return "\n".join(partes)
    except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None


def limpiar_texto(t):
    t = t.replace("\u00ad", "").replace("\x0c", " ")
    t = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", t)  # palabras cortadas con guion al final de línea
    t = re.sub(r"\s+", " ", t).strip()
    return t[:MAX_CARACTERES]


def extraer_textos(finales, usar_ocr, avisos):
    cache = {}
    if CACHE.exists():
        try:
            cache = json.loads(CACHE.read_text(encoding="utf-8"))
        except ValueError:
            cache = {}
    textos, sin_texto, nuevos, motor = {}, [], 0, None
    for i, d in enumerate(finales):
        pdf = RAIZ / d["url"]
        if not pdf.exists():
            continue
        firma = f"{pdf.stat().st_size}"
        c = cache.get(d["url"])
        if c and c.get("firma") == firma and (c.get("ocr") or not usar_ocr or len(c["texto"]) > 200):
            texto = c["texto"]
        else:
            bruto = _pdftotext(pdf)
            motor = motor or ("pdftotext" if bruto is not None else None)
            if bruto is None:
                bruto = _pypdf(pdf)
                motor = motor or ("pypdf" if bruto is not None else None)
            if bruto is None:
                avisos.append("No se pudo extraer texto: instalá Poppler (pdftotext) o ejecutá 'pip install pypdf'.")
                return None
            texto = limpiar_texto(bruto)
            hizo_ocr = False
            if usar_ocr and len(texto) < 200:
                o = _ocr(pdf)
                if o:
                    texto, hizo_ocr = limpiar_texto(o), True
            cache[d["url"]] = {"firma": firma, "texto": texto, "ocr": hizo_ocr}
            nuevos += 1
            if nuevos % 40 == 0:
                CACHE.parent.mkdir(parents=True, exist_ok=True)
                CACHE.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
                print(f"  … texto extraído de {i + 1}/{len(finales)} documentos", flush=True)
        if len(texto) >= 200:
            textos[d["url"]] = texto
        else:
            sin_texto.append(d["url"])
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
    if sin_texto:
        avisos.append(f"{len(sin_texto)} PDF sin texto legible (escaneados). Con --ocr se pueden leer. Ej.: {sin_texto[0]}")
    return textos


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--actas", default=str(RAIZ.parent / "ACTAS" / "ACTAS"))
    ap.add_argument("--dictamenes", default=str(RAIZ.parent / "DICTAMENES"))
    ap.add_argument("--solo-indice", action="store_true", help="No copia PDF, solo regenera el JSON")
    ap.add_argument("--sin-texto", action="store_true", help="No extrae el texto de los PDF")
    ap.add_argument("--ocr", action="store_true", help="Aplica OCR a los PDF escaneados (requiere Tesseract)")
    args = ap.parse_args()

    avisos, items = [], []
    for nombre, carpeta, fn in (("actas", args.actas, procesar_actas), ("dictámenes", args.dictamenes, procesar_dictamenes)):
        c = Path(carpeta)
        if not c.is_dir():
            avisos.append(f"No se encontró la carpeta de {nombre}: {c}")
            continue
        items += fn(c, avisos)

    # nombres de destino únicos
    usados = set()
    for it in items:
        url = it["url"]
        k = 2
        while url in usados:
            url = re.sub(r"(-\d+)?\.pdf$", f"-{k}.pdf", it["url"])
            k += 1
        it["url"] = url
        usados.add(url)

    finales = []
    for it in items:
        src = it.pop("_src")
        it.pop("_prio", None)
        destino = RAIZ / it["url"]
        if not args.solo_indice:
            if not copiar(src, destino, avisos):
                continue
        if destino.exists():
            it["kb"] = round(destino.stat().st_size / 1024)
        finales.append({k: v for k, v in it.items() if v is not None})

    orden = {"acta": 0, "foro": 1, "anexo": 2, "dictamen": 0, "resolucion": 1, "complementario": 2}
    finales.sort(key=lambda i: (-(i.get("y") or 0), orden.get(i["t"], 9), -(i.get("n") or 0), i.get("d") or "", i["titulo"]))

    # borra PDF huérfanos (que ya no están en el índice)
    if not args.solo_indice:
        vigentes = {(RAIZ / i["url"]).resolve() for i in finales}
        for f in (RAIZ / "archivo").rglob("*.pdf"):
            if f.resolve() not in vigentes:
                try:
                    f.unlink()
                except OSError:
                    avisos.append(f"Archivo que sobra (borrarlo a mano): {f.relative_to(RAIZ)}")

    salida = {"generado": date.today().isoformat(), "documentos": finales}
    (RAIZ / "data").mkdir(exist_ok=True)
    (RAIZ / "data" / "archivo.json").write_text(json.dumps(salida, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    if not args.sin_texto:
        textos = extraer_textos(finales, args.ocr, avisos)
        if textos is not None:
            (RAIZ / "data" / "texto.json").write_text(json.dumps(textos, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
            mb = (RAIZ / "data" / "texto.json").stat().st_size / 1e6
            print(f"Texto completo indexado: {len(textos)} documentos ({mb:.1f} MB)")

    from collections import Counter
    c = Counter(i["t"] for i in finales)
    print("Archivo generado:", dict(c), "total", len(finales))
    for a in avisos:
        print("  !", a)


if __name__ == "__main__":
    sys.exit(main())
