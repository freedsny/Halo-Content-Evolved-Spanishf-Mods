"""Pasa al espanol los textos que el codigo de Content Evolved escribe en
pantalla, con la tabla de textos_codigo.txt (ver su encabezado). Lo usa
regenerar_menus.py; tambien se puede correr solo, desde la carpeta del codigo:
python3 menus/codigo_es.py [--revisar]"""
import pathlib
import re
import sys

AQUI = pathlib.Path(__file__).resolve().parent

# "a" "b" (literales seguidos de C) quedan en "ab", con el mismo sentido, para
# que una frase partida en varias comillas se traduzca entera. El codigo se lee
# pieza por pieza (comentarios, caracteres '"', literales): solo se juntan dos
# literales de verdad con nada mas que espacios entre ellos. (Una expresion
# regular sola tomaba lo de entre dos literales, ") ? " de c ? " " : "", por
# otro literal, y se comia unas comillas: el juego se cerraba)
def _literal(fuente, i):
    """el literal que empieza en i (su prefijo L incluido): (fin, prefijo,
    contenido), o None si ahi no empieza uno"""
    prefijo = ""
    if fuente.startswith('L"', i) and (i == 0 or not (fuente[i - 1].isalnum() or fuente[i - 1] == "_")):
        prefijo, i = "L", i + 1
    if i >= len(fuente) or fuente[i] != '"':
        return None
    j = i + 1
    while j < len(fuente) and fuente[j] != '"':
        if fuente[j] == "\\":
            j += 1
        elif fuente[j] == "\n":
            return None
        j += 1
    if j >= len(fuente):
        return None
    return j + 1, prefijo, fuente[i + 1:j]


def unir(fuente):
    salida = []
    i, n = 0, len(fuente)
    while i < n:
        c = fuente[i]
        if fuente.startswith("//", i):
            fin = fuente.find("\n", i)
            fin = n if fin < 0 else fin
            salida.append(fuente[i:fin])
            i = fin
        elif fuente.startswith("/*", i):
            fin = fuente.find("*/", i + 2)
            fin = n if fin < 0 else fin + 2
            salida.append(fuente[i:fin])
            i = fin
        elif c == "'":
            j = i + 1
            while j < n and fuente[j] != "'" and fuente[j] != "\n":
                j += 2 if fuente[j] == "\\" else 1
            salida.append(fuente[i:j + 1])
            i = j + 1
        elif (c == '"' or (c == "L" and fuente.startswith('L"', i))) and _literal(fuente, i):
            fin, prefijo, contenido = _literal(fuente, i)
            # (los que le siguen con solo espacios en medio)
            while True:
                k = fin
                while k < n and fuente[k] in " \t\r\n":
                    k += 1
                siguiente = _literal(fuente, k) if k > fin else None
                if not siguiente:
                    break
                # (un \x o un \ octal al final se comeria lo que sigue; otro
                # prefijo no se junta)
                if re.search(r'\\x[0-9A-Fa-f]+$|\\[0-7]{1,2}$', contenido):
                    break
                if siguiente[1] != prefijo and siguiente[1] != "":
                    break
                fin, contenido = siguiente[0], contenido + siguiente[2]
            salida.append(f'{prefijo}"{contenido}"')
            i = fin
        else:
            j = i + 1
            while j < n and fuente[j] not in "/'\"L":
                j += 1
            salida.append(fuente[i:j])
            i = j
    return "".join(salida)


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
