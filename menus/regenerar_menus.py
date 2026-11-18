"""Halo C.E Evolved: regenera las pantallas de ajustes de Halo Content Evolved
(con TRUCOS dentro de JUEGO), pone los titulos y pasa los textos al espanol.
Se ejecuta desde la raiz del codigo de Halo Content Evolved, despues de aplicar
parche/trucos.patch (tools/port_settings.py ya trae las pantallas de TRUCOS).

Los titulos dibujados, las palabras del menu principal y las traducciones de
la version de OpenCE (Halo C.E) estan en esta misma carpeta (textos_es.py,
menu_es.py, header_*.png). Los textos se cambian por coincidencia exacta
(nunca por su orden: Content Evolved agrega opciones en las listas del juego),
con las tablas de textos_es.py y las de textos_evolved.py. Lo que no esta en ninguna tabla queda en ingles y
se cuenta al final."""
import bisect
import glob
import json
import pathlib
import re
import shutil
import sys

sys.path.insert(0, "tools")
import port_settings as ps

aqui = pathlib.Path(__file__).resolve().parent
trucos = aqui
sys.path.insert(0, str(trucos))
sys.path.insert(0, str(aqui))
import textos_es
import textos_evolved

pe = ps.PE
menus = pathlib.Path("port/assets/menus")
ce = menus / "ce"

# 1) las pantallas de ajustes (incluidas TRUCOS y GAMEPLAY con su fila TRUCOS)
nuevos = []
for nombre, lineas in ps.settings_files().items():
    ruta = ce / nombre
    if not ruta.exists():
        nuevos.append(nombre)
    ruta.write_text("\n".join(lineas), encoding="utf-8", newline="")

# 2) los titulos "TRUCOS", "HUD", "AJUSTES" y "GUIA" (imagenes ya dibujadas en esta carpeta)
carpeta_png = "ce/port/main_menu/settings_select/player_setup/player_profile_edit/network_setup/cheats/"
titulos = [("header_trucos", f"{pe}/network_setup/cheats/header_trucos"),
           ("header_hud", f"{pe}/network_setup/cheats/header_hud"),
           ("header_ajustes", f"{pe}/network_setup/cheats/header_ajustes"),
           ("header_guia", f"{pe}/network_setup/cheats/header_guia")]
pngs = []
bitmaps_xml = ce / "bitmaps.xml"
texto = bitmaps_xml.read_text(encoding="utf-8")
for nombre, bitmap in titulos:
    png = f"{carpeta_png}{nombre}.png"
    pngs.append(png)
    destino = menus / png
    destino.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(trucos / f"{nombre}.png", destino)
    if f'name="{bitmap}"' not in texto:
        entrada = (f'\t<bitmap name="{bitmap}">\n'
                   f'\t\t<frame png="{png}" width="512" height="64"/>\n'
                   f'\t</bitmap>\n')
        fin = texto.rindex("</menus>")
        texto = texto[:fin] + entrada + texto[fin:]
bitmaps_xml.write_text(texto, encoding="utf-8", newline="")

# 3) menus.json: las pantallas nuevas y los titulos
mj = menus / "menus.json"
crudo = mj.read_text(encoding="utf-8")
datos = json.loads(crudo)
archivos = datos["files"]
ancla = "ce/main_menu.settings_select.player_setup.player_profile_edit.network_setup.in_game.xml"
for nombre in nuevos:
    entrada = "ce/" + nombre
    if entrada not in archivos:
        if ancla in archivos:
            archivos.insert(archivos.index(ancla), entrada)
        else:
            archivos.append(entrada)
for png in pngs:
    if png not in archivos:
        archivos.insert(bisect.bisect_left(archivos, png), png)
mj.write_text(json.dumps(datos, indent=1, ensure_ascii=False) + ("\n" if crudo.endswith("\n") else ""),
              encoding="utf-8")

# 4) el codigo: la lista de palabras de guide.mode, y los menus siempre con los
# textos de la app (en espanol), nunca los del loc.map de Custom Edition
config_c = pathlib.Path("port/linux/src/port_config.c")
fuente_c = config_c.read_text(encoding="utf-8")
palabras = '\t{ "guide.mode", { "off", "objective", "ally", "enemy", NULL }, NULL },\n'
if '"guide.mode", {' not in fuente_c:
    for punto in ('\t{ "display.hud_button_style", {', "config_words[] =\n{\n"):
        i = fuente_c.find(punto)
        if i != -1:
            if punto.startswith("config_words"):
                i += len(punto)
            fuente_c = fuente_c[:i] + palabras + fuente_c[i:]
            break
    else:
        print("AVISO: no se encontro donde poner la lista de palabras de guide.mode")
viejo = '{ "display.menu_language", _config_string, "\\"maps\\""'
if viejo in fuente_c:
    fuente_c = fuente_c.replace(viejo, '{ "display.menu_language", _config_string, "\\"english\\""')
else:
    print("AVISO: no se encontro display.menu_language en port_config.c")
config_c.write_text(fuente_c, encoding="utf-8", newline="")
tags_c = pathlib.Path("port/linux/game/menu_tags.c")
fuente_c = tags_c.read_text(encoding="utf-8")
viejo = '\tif (!csstrcasecmp(value, "maps"))\n\t\treturn TRUE;\n'
if viejo in fuente_c:
    tags_c.write_text(fuente_c.replace(viejo,
        '\t/* port (trucos): los menus en espanol de la app, nunca los textos del loc.map */\n'
        '\tif (!csstrcasecmp(value, "maps"))\n\t\treturn FALSE;\n'), encoding="utf-8", newline="")
else:
    print("AVISO: no se encontro menus_language_maps en menu_tags.c")

# 5) los textos al espanol, por coincidencia exacta
# (los bloques de la version de OpenCE van por orden: se usan solo los que aqui
# tienen los mismos textos que alla, contados; los demas estan en textos_evolved)
pares = {}
original = (ce / "strings.xml").read_text(encoding="utf-8")
for nombre, (_, traducidos) in textos_es.BLOQUES.items():
    if f'<strings name="{nombre}"' not in original:
        continue
    i = original.index(f'<strings name="{nombre}"')
    ingles = re.findall(r'<string text="([^"]*)"', original[i:original.index("</strings>", i)])
    if len(ingles) != len(traducidos):
        continue
    for en, es in zip(ingles, traducidos):
        if es is not None:
            pares[en] = es.replace("\n", "\\n")
pares.update(textos_es.AJUSTES)
pares.update(textos_evolved.TEXTOS)
valores = dict(textos_es.VALORES)
valores.update(textos_evolved.VALORES)


def _texto(m):
    return m.group(1) + pares.get(m.group(2), m.group(2)) + '"'


def _valores(m):
    return 'strings="' + "|".join(valores.get(p, pares.get(p, p)) for p in m.group(1).split("|")) + '"'


pendientes = set()
for archivo in sorted(glob.glob(str(ce / "*.xml"))):
    if "network_setup.cheats" in archivo:
        continue
    ruta = pathlib.Path(archivo)
    contenido = ruta.read_text(encoding="utf-8")
    nuevo = re.sub(r'(<string text="|\stext=")([^"]*)"', _texto, contenido)
    nuevo = re.sub(r'strings="([^"]*)"', _valores, nuevo)
    if nuevo != contenido:
        ruta.write_text(nuevo, encoding="utf-8", newline="")
    for t in re.findall(r'(?:<string text="|\stext=")([^"]*)"', nuevo):
        if re.search(r"[a-z]{3}", t) and t not in pares.values():
            pendientes.add(t)

# 7) el menu de los tres dedos (overlay_menu.c): sus textos al espanol, sus
# trucos con el mismo ajuste que TRUCOS (lo que se cambia en uno se ve en el
# otro; si no, el de TRUCOS en ON lo vuelve a prender) y los trucos de TRUCOS
# que no tenia
overlay_c = pathlib.Path("port/linux/game/overlay_menu.c")
if overlay_c.exists():
    fuente_c = overlay_c.read_text(encoding="utf-8")
    sincronizados = 0
    def _truco(m):
        global sincronizados
        sincronizados += 1
        ajuste = "cheats." + m.group(2)
        if m.group(2) == "jetpack":
            # (con una nota abajo: como se vuela)
            return ('OVERLAY_TOGGLE_NOTE("%s", _overlay_state_config, "config %s true", "config %s false", "%s", '
                    '"Manten disparar y granada a la vez para volar")' % (m.group(1), ajuste, ajuste, ajuste))
        return ('OVERLAY_TOGGLE("%s", _overlay_state_config, "config %s true", "config %s false", "%s", 0.0f, FALSE)'
                % (m.group(1), ajuste, ajuste, ajuste))
    fuente_c = re.sub(r'OVERLAY_GLOBAL\("([^"]+)", "cheat_(deathless_player|omnipotent|infinite_ammo|bottomless_clip|'
                      r'super_jump|jetpack|medusa|bump_possession)"\)', _truco, fuente_c)
    fuente_c, cambios = re.subn(r'OVERLAY_TOGGLE\("Easy Rider", _overlay_state_global_inverted, "rider_ejection false", '
                                r'"rider_ejection true",\s*"rider_ejection", 0\.0f, FALSE\)',
                                'OVERLAY_TOGGLE("Easy Rider", _overlay_state_config, "config cheats.easy_rider true", '
                                '"config cheats.easy_rider false", "cheats.easy_rider", 0.0f, FALSE)', fuente_c)
    sincronizados += cambios
    ultimo = 'OVERLAY_COMMAND("Spawn All Vehicles", "cheat_all_vehicles"),\n'
    if ultimo in fuente_c:
        fuente_c = fuente_c.replace(ultimo, ultimo + "".join(
            '\tOVERLAY_TOGGLE("%s", _overlay_state_config, "config %s true", "config %s false", "%s", 0.0f, FALSE),\n'
            % (texto, ajuste, ajuste, ajuste) for texto, ajuste in textos_evolved.OVERLAY_TRUCOS))
    else:
        print("AVISO: no se encontro donde poner los trucos en el menu de los tres dedos")
    traducidos = 0
    for ingles, espanol in textos_evolved.OVERLAY.items():
        literal = '"%s"' % ingles.replace("\\", "\\\\")
        if literal in fuente_c:
            traducidos += 1
            fuente_c = fuente_c.replace(literal, '"%s"' % espanol)
    overlay_c.write_text(fuente_c, encoding="utf-8", newline="")
    print("menu de los tres dedos: %d trucos con TRUCOS, %d de %d textos en espanol"
          % (sincronizados, traducidos, len(textos_evolved.OVERLAY)))
else:
    print("AVISO: no esta overlay_menu.c (menu de los tres dedos)")

# 8) los textos que el codigo escribe en pantalla (textos_codigo.txt)
import codigo_es
hechos, faltan = codigo_es.aplicar()
print(f"textos del codigo en espanol: {hechos}, no encontrados: {len(faltan)}")
for falta in faltan:
    print("  no encontrado:", falta)

# 6) las palabras del menu principal y los titulos, dibujados en espanol
# (si faltan pillow, numpy o scipy, quedan en ingles y solo se avisa)
try:
    sys.path.insert(0, str(trucos))
    import menu_es
    fuente = "port/assets/fonts/OpenCE-Regular.ttf"
    principal = ce / "shell/main_menu"
    for archivo, palabra in (("load_campaign", "CAMPAÑA"), ("multiplayer", "MULTIJUGADOR"),
                             ("profile", "PERFILES"), ("settings", "AJUSTES"), ("quit", "SALIR")):
        for estado in (0, 1):
            menu_es.item(palabra, estado, fuente).save(principal / f"menu_{archivo}__{estado}.png", optimize=True)
    menu_es.header("AJUSTES DEL PERFIL", fuente).save(
        ce / "shell/main_menu/settings_select/player_setup/player_profile_edit/header_edit_profile_settings__0.png",
        optimize=True)
    for carpeta, nombre, palabra in textos_es.ITEMS:
        if (principal / carpeta).is_dir():
            for estado in (0, 1):
                menu_es.item(palabra, estado, fuente).save(principal / carpeta / f"{nombre}__{estado}.png",
                                                           optimize=True)
    for ruta, titulo in textos_es.TITULOS + textos_es.TITULOS_AJUSTES:
        if (principal / ruta).parent.is_dir():
            menu_es.header(titulo, fuente).save(principal / ruta, optimize=True)
    # (las de Content Evolved: en ce/port/main_menu, cada una de su ancho)
    propias = ce / "port/main_menu"
    for nombre, palabra in textos_evolved.ITEMS_EVOLVED:
        for estado in (0, 1):
            archivo = propias / f"{nombre}__{estado}.png"
            if archivo.exists():
                from PIL import Image
                ancho = Image.open(archivo).size[0]
                menu_es.item(palabra, estado, fuente, ancho).save(archivo, optimize=True)
            else:
                print("AVISO: no esta", archivo)
    for ruta, titulo in textos_evolved.TITULOS_EVOLVED:
        if (propias / ruta).exists():
            menu_es.header(titulo, fuente).save(propias / ruta, optimize=True)
        else:
            print("AVISO: no esta", propias / ruta)
    print("menu en espanol: dibujado")
except ImportError as error:
    print("AVISO: el menu queda en ingles, falta:", error)
print("pantallas nuevas:", nuevos)
print("textos de menu que siguen en ingles:", len(pendientes))
