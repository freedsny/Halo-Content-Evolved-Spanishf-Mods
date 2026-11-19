# Notas para Claude: cómo arreglar la compilación de Halo C.E Evolved

## Cómo funciona

- Arriba está el código de Halo Content Evolved: https://github.com/Watanoge/halo-content-evolved (tags `build-N`).
- `parche/trucos.patch` se aplica sobre ese código con `patch -p1 -l` (en la carpeta del código).
- Después, en la misma carpeta, `python3 ../repo/menus/regenerar_menus.py` pasa al español los menús y los textos (`menus/textos_codigo.txt`, `menus/textos_juego.txt`, `menus/textos_evolved.py`, `menus/textos_es.py`) y hace los controles de `menus/codigo_es.py`. Si un control falla, se detiene a propósito: una traducción mal hecha ya cerró el juego una vez.
- `.github/workflows/compilar.yml` compila el APK:
  - En `main` sale la versión oficial (Release "Latest", `Halo C.E Evolved con trucos - Content Evolved build-N (#n)`, paquete `com.halo.contentevolved.trucos`).
  - En `pruebas` sale un borrador privado (`EVOLVED PRUEBA (pruebas) - ...`, paquete `com.halo.contentevolved.trucos.pruebas`). Sin versión indicada, usa el último tag de arriba.
- `.github/workflows/vigilar.yml` está programado todos los días a las 6:43 a. m. de Colombia, pero GitHub suele lanzarlo horas después (en noviembre de 2026, hacia las 2 p. m.). Si arriba hay una versión nueva, lanza `compilar.yml` en `main` con esa versión.
- Si una compilación falla, se abre el issue **"Fallo la compilacion de Evolved"**. Mientras esté abierto, el vigilante no lanza nada.

## Reglas

- Los arreglos van a la rama `pruebas`. **Nunca a `main`** hasta que Freed pruebe el APK de pruebas y diga "pásala".
- Los textos del juego en español van sin tildes ni eñes: las fuentes del juego no las tienen.
- Nada de datos de Bungie ni de Microsoft en el repositorio: ni mapas, ni la ISO, ni archivos del juego.
- Los secretos de firma (`ANDROID_KEYSTORE_*`) nunca se escriben, se muestran ni se guardan.
- Nunca quitar ni aflojar los controles de `codigo_es.py` o `regenerar_menus.py` para que algo pase.
- Mensajes de commit en español, sin tildes, explicando qué se arregló.
- GitHub GraphQL no funciona en estas sesiones: usar `gh api` (REST).
  - `gh release download` y `gh run view` no sirven.
  - Para el log: `gh api repos/freedsny/Halo-Content-Evolved-Spanishf-Mods/actions/runs/<id>/jobs` y luego `gh api repos/freedsny/Halo-Content-Evolved-Spanishf-Mods/actions/jobs/<job_id>/logs`.

## Si la compilación falla

1. **Leer el log** de la ejecución que falló (el enlace está en el issue) y ver en qué paso falló:
   - **"Aplicar los trucos", en `patch`:** el parche ya no entra en la versión nueva de arriba. Ver el paso 2.
   - **"Aplicar los trucos", en `regenerar_menus.py` o `codigo_es.py`:** un texto en inglés cambió arriba, o un control rechazó una traducción. Ver el paso 3.
   - **Al compilar (cmake, ninja, gradle):** el código del parche ya no compila con la versión nueva. Ver el paso 2 y corregir el código.
   - **Error de red o del runner:** volver a lanzar la ejecución (`gh api -X POST .../actions/runs/<id>/rerun`) antes de tocar nada.
2. **Rehacer el parche sobre la versión nueva.** VIEJA es la versión de la última Release oficial y NUEVA la de la compilación que falló:
   ```
   git clone --depth 1 --branch build-VIEJA https://github.com/Watanoge/halo-content-evolved.git vieja
   cp -r vieja vieja-trucos && (cd vieja-trucos && patch -p1 -l < ../repo/parche/trucos.patch)
   git clone --depth 1 --branch build-NUEVA https://github.com/Watanoge/halo-content-evolved.git nueva
   cp -r nueva nueva-trucos && (cd nueva-trucos && patch -p1 -l --merge < ../repo/parche/trucos.patch)
   ```
   - Resolver a mano cada conflicto: los marcadores `<<<<<<<` que deja `--merge`, o los archivos `.rej`.
   - Para cada conflicto, mirar qué cambió arriba (`diff -u vieja/ARCHIVO nueva/ARCHIVO`) y qué hacía el parche (`vieja-trucos/ARCHIVO`), y llevar la misma intención al código nuevo.
   - Si arriba ya arreglaron lo mismo que un trozo del parche, quitar ese trozo.
   - Luego: `python3 repo/herramientas/rehacer_parche.py nueva nueva-trucos repo/parche/trucos.patch`. Avisa si un archivo dejó de estar en el parche: confirmar que es a propósito.
3. **Traducciones:**
   - Si un texto en inglés cambió arriba, actualizar `menus/textos_codigo.txt`: `## archivo`, la línea en inglés, `= español`; `¶` marca un espacio al final.
   - Si no, actualizar `menus/textos_juego.txt` o `menus/textos_evolved.py`.
4. **Comprobar antes de subir:**
   - En una copia limpia de `nueva`, aplicar `patch -p1 -l < repo/parche/trucos.patch` sin errores.
   - En esa misma copia, correr `python3 ../repo/menus/regenerar_menus.py`. Necesita `pip install --break-system-packages pillow numpy scipy`. Tiene que terminar sin errores.
5. **Subir a `pruebas`** y esperar la compilación de pruebas en Actions. Si sale bien, revisar el APK del borrador:
   - Bajarlo con `gh api -H 'Accept: application/octet-stream' repos/.../releases/assets/<id>`.
   - Paquete `com.halo.contentevolved.trucos.pruebas`, por ejemplo con androguard.
   - Los textos en español (por ejemplo `MAPAS Y MODS`, `TRUCOS`) dentro de `assets/halo_guest.elf`.
6. **Comentar en el issue** qué falló y qué se cambió. **No cerrarlo:** se cierra cuando Freed diga "pásala" y la versión oficial compile bien. Si se cierra antes, el vigilante vuelve a compilar `main` con el parche viejo y falla otra vez.
