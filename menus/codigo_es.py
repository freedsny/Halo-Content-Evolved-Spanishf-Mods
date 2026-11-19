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
        elif linea in ("#", "") or linea.startswith("# ") or linea.startswith("## ") or not linea.strip():
            # (un comentario es "#" o "# ..."; un texto que empieza por #,
            # como "#%d - NOT LINKED", es un texto)
            continue
        else:
            if pendiente is not None:
                sys.exit(f"textos_codigo.txt:{numero}: falta la traduccion de: {pendiente}")
            pendiente = linea
    return tabla


# ---------- los controles: una traduccion que no los pasa detiene la compilacion

# (las conversiones de printf: %s, %ld, %.*s, %08lX, %hs, %%...)
_FORMATO = re.compile(r"%[-+ #0]*(?:\*|\d+)?(?:\.(?:\*|\d+))?(?:hh|h|ll|l|L|z|j|t|I64)?[diouxXeEfgGcspnS%]")
# (una llamada que compara o busca un texto, o lee un ajuste: un texto en ella
# es una clave, no algo que se ve)
_COMPARA = re.compile(r"\b(?:\w*cmp\w*|\w*casecmp|strstr|wcsstr|config_\w+|\w+_option)\s*\(|\.equals(?:IgnoreCase)?\(")


def literales(fuente):
    """los literales de verdad de un codigo C o Java, en orden: (inicio, fin,
    prefijo, contenido), sin los comentarios ni los caracteres"""
    i, n = 0, len(fuente)
    while i < n:
        c = fuente[i]
        if fuente.startswith("//", i):
            fin = fuente.find("\n", i)
            i = n if fin < 0 else fin
        elif fuente.startswith("/*", i):
            fin = fuente.find("*/", i + 2)
            i = n if fin < 0 else fin + 2
        elif c == "'":
            j = i + 1
            while j < n and fuente[j] != "'" and fuente[j] != "\n":
                j += 2 if fuente[j] == "\\" else 1
            i = j + 1
        elif (c == '"' or (c == "L" and fuente.startswith('L"', i))) and _literal(fuente, i):
            fin, prefijo, contenido = _literal(fuente, i)
            yield i, fin, prefijo, contenido
            i = fin
        else:
            i += 1


def esqueleto(fuente):
    """el codigo sin sus textos: cada literal (o literales seguidos) un S, sin
    comentarios ni espacios. Una traduccion lo deja igual"""
    partes, ultimo, antes = [], 0, None
    for inicio, fin, _prefijo, _contenido in literales(fuente):
        medio = fuente[ultimo:inicio]
        medio = re.sub(r"//[^\n]*|/\*.*?\*/", " ", medio, flags=re.S)
        if antes == "S" and not medio.strip():
            ultimo = fin
            continue
        partes.append(medio)
        partes.append(" S ")
        antes, ultimo = "S", fin
    partes.append(re.sub(r"//[^\n]*|/\*.*?\*/", " ", fuente[ultimo:], flags=re.S))
    return "".join(partes).split()


def revisar_par(archivo, ingles, espanol):
    """lo que esta mal de una traduccion, o None"""
    if _FORMATO.findall(ingles) != _FORMATO.findall(espanol):
        return f"otros %: {_FORMATO.findall(ingles)} y {_FORMATO.findall(espanol)}"
    if re.search(r'(?<!\\)(?:\\\\)*"', espanol):
        return "unas comillas sin \\ (cortarian el texto)"
    if re.search(r"(?<!\\)(?:\\\\)*\\$", espanol):
        return "termina en \\ (se comeria las comillas)"
    if any(ord(letra) > 126 for letra in espanol):
        return "letras que la fuente del juego no tiene (tildes, enes...)"
    return None


def _dentro_de_comparaciones(fuente):
    """los tramos (inicio, fin) de los argumentos de cada llamada que compara o
    lee un ajuste (_COMPARA): un literal en uno es una clave"""
    tramos = []
    for m in _COMPARA.finditer(fuente):
        abre = fuente.find("(", m.end() - 1)
        profundidad, k, n = 0, abre, len(fuente)
        while k < n:
            c = fuente[k]
            if c == '"' or (c == "L" and fuente.startswith('L"', k)):
                lit = _literal(fuente, k)
                if lit:
                    k = lit[0]
                    continue
            elif c == "'":
                k += 1
                while k < n and fuente[k] != "'" and fuente[k] != "\n":
                    k += 2 if fuente[k] == "\\" else 1
            elif c == "(":
                profundidad += 1
            elif c == ")":
                profundidad -= 1
                if profundidad == 0:
                    break
            k += 1
        tramos.append((abre, k))
    return tramos


def aplicar(raiz=".", revisar=False):
    """cambia los archivos; devuelve (traducidos, no encontrados). Una
    traduccion que no pasa los controles (revisar_par, el esqueleto del codigo,
    un texto que el codigo compara) detiene todo con un error: mejor sin
    compilar que un juego que se cierra"""
    raiz = pathlib.Path(raiz)
    hechos, faltan, errores = 0, [], []
    for archivo, (pares, crudos) in leer_tabla().items():
        ruta = raiz / archivo
        if not ruta.exists():
            faltan.append(f"{archivo} (no esta)")
            continue
        original = ruta.read_text(encoding="utf-8")
        codigo = ruta.suffix in (".c", ".h", ".java")
        fuente = unir(original) if ruta.suffix in (".c", ".h") else original
        if codigo and esqueleto(fuente) != esqueleto(original):
            errores.append(f"{archivo}: juntar los literales cambio el codigo")
        for viejo, nuevo in crudos:
            if viejo in fuente:
                fuente = fuente.replace(viejo, nuevo)
            else:
                faltan.append(f"{archivo}: codigo: {viejo.strip()}")
        base = fuente
        if codigo:
            donde = {}
            for inicio, fin, prefijo, contenido in literales(base):
                donde.setdefault(contenido, []).append((inicio, fin, prefijo))
            tramos = _dentro_de_comparaciones(base)
            cambios = []
        for ingles, espanol in pares:
            problema = revisar_par(archivo, ingles, espanol)
            if problema:
                errores.append(f"{archivo}: {ingles!r}: {problema}")
                continue
            if codigo:
                # (solo literales enteros de verdad; y ninguno que el codigo
                # compare o use de clave)
                lugares = donde.get(ingles, [])
                for inicio, fin, prefijo in lugares:
                    if any(a < inicio < b for a, b in tramos):
                        linea = base.count("\n", 0, inicio) + 1
                        errores.append(f"{archivo}:{linea}: {ingles!r} se compara o es una clave")
                    cambios.append((inicio, fin, prefijo, espanol))
                veces = len(lugares)
            else:
                patron = re.compile(r'(?<!\\)"' + re.escape(ingles) + '"')
                veces = len(patron.findall(fuente))
                fuente = patron.sub(lambda m: '"' + espanol + '"', fuente)
            if not veces:
                faltan.append(f"{archivo}: {ingles}")
                continue
            if revisar and veces > 1:
                print(f"  {veces} veces en {archivo}: {ingles}")
            hechos += 1
        if codigo:
            for inicio, fin, prefijo, espanol in sorted(cambios, reverse=True):
                fuente = fuente[:inicio] + f'{prefijo}"{espanol}"' + fuente[fin:]
            if esqueleto(fuente) != esqueleto(base):
                errores.append(f"{archivo}: la traduccion cambio el codigo, no solo los textos")
        ruta.write_text(fuente, encoding="utf-8", newline="")
    if errores:
        print("ERROR: la traduccion del codigo no pasa los controles (no se compila asi):")
        for error in errores:
            print("  " + error)
        sys.exit(1)
    return hechos, faltan


if __name__ == "__main__":
    hechos, faltan = aplicar(revisar="--revisar" in sys.argv)
    print(f"textos del codigo en espanol: {hechos}, no encontrados: {len(faltan)}")
    for falta in faltan:
        print("  no encontrado:", falta)
