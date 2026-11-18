"""Pasa al espanol los textos que el codigo de Content Evolved escribe en
pantalla, con la tabla de textos_codigo.txt (ver su encabezado). Lo usa
regenerar_menus.py; tambien se puede correr solo, desde la carpeta del codigo:
python3 menus/codigo_es.py [--revisar]"""
import pathlib
import re
import sys

AQUI = pathlib.Path(__file__).resolve().parent

# "a" "b" (literales seguidos de C) quedan en "ab", con el mismo sentido, para
# que una frase partida en varias comillas se traduzca entera
_SEGUIDOS = re.compile(r'(L?)"((?:[^"\\\n]|\\.)*)"(\s+)(L?)"((?:[^"\\\n]|\\.)*)"')


def unir(fuente):
    def juntar(m):
        izquierda = m.group(2)
        # (un \x o un \ octal al final se comeria lo que sigue)
        if re.search(r'\\x[0-9A-Fa-f]+$|\\[0-7]{1,2}$', izquierda):
            return m.group(0)
        if m.group(1) != m.group(4) and m.group(4) != "":
            return m.group(0)
        return f'{m.group(1)}"{izquierda}{m.group(5)}"'

    antes = None
    while antes != fuente:
        antes = fuente
        fuente = _SEGUIDOS.sub(juntar, fuente)
    return fuente


def leer_tabla(ruta=AQUI / "textos_codigo.txt"):
    """{archivo: ([(ingles, espanol)], [(codigo, codigo nuevo)])}"""
    tabla = {}
    archivo = None
    pendiente = None
    crudo = None
    for numero, linea in enumerate(ruta.read_text(encoding="utf-8").split("\n"), 1):
        # (un texto que acaba en espacio se marca con un ¶ al final)
        linea = linea[:-1] if linea.endswith("\u00b6") else linea
        if linea.startswith("## "):
            archivo = linea[3:].strip()
            tabla.setdefault(archivo, ([], []))
        elif linea.startswith("~= "):
            tabla[archivo][1].append((crudo, linea[3:]))
            crudo = None
        elif linea.startswith("~ "):
            crudo = linea[2:]
        elif linea.startswith("= ") or linea == "=":
            if pendiente is None:
                sys.exit(f"textos_codigo.txt:{numero}: una traduccion sin su texto en ingles")
            tabla[archivo][0].append((pendiente, linea[2:]))
            pendiente = None
        elif linea.startswith("#") or not linea.strip():
            continue
        else:
            if pendiente is not None:
                sys.exit(f"textos_codigo.txt:{numero}: falta la traduccion de: {pendiente}")
            pendiente = linea
    return tabla


def aplicar(raiz=".", revisar=False):
    """cambia los archivos; devuelve (traducidos, no encontrados)"""
    raiz = pathlib.Path(raiz)
    hechos, faltan = 0, []
    for archivo, (pares, crudos) in leer_tabla().items():
        ruta = raiz / archivo
        if not ruta.exists():
            faltan.append(f"{archivo} (no esta)")
            continue
        fuente = ruta.read_text(encoding="utf-8")
        if ruta.suffix in (".c", ".h"):
            fuente = unir(fuente)
        for viejo, nuevo in crudos:
            if viejo in fuente:
                fuente = fuente.replace(viejo, nuevo)
            else:
                faltan.append(f"{archivo}: codigo: {viejo.strip()}")
        for ingles, espanol in pares:
            patron = re.compile(r'(?<!\\)"' + re.escape(ingles) + '"')
            veces = len(patron.findall(fuente))
            if not veces:
                faltan.append(f"{archivo}: {ingles}")
                continue
            if revisar and veces > 1:
                print(f"  {veces} veces en {archivo}: {ingles}")
            fuente = patron.sub(lambda m: '"' + espanol + '"', fuente)
            hechos += 1
        ruta.write_text(fuente, encoding="utf-8", newline="")
    return hechos, faltan


if __name__ == "__main__":
    hechos, faltan = aplicar(revisar="--revisar" in sys.argv)
    print(f"textos del codigo en espanol: {hechos}, no encontrados: {len(faltan)}")
    for falta in faltan:
        print("  no encontrado:", falta)
