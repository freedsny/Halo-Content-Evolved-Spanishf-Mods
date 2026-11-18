# Halo C.E Evolved (Content Evolved en español, con trucos)

Versión de **[Halo Content Evolved](https://github.com/Watanoge/halo-content-evolved)** para **Android**, con sus menús traducidos **al español** y con los **trucos, la flecha guía y el HUD** de [Halo C.E con trucos](https://github.com/freedsny/Halo-CE-Android-Trucos-Mods-OpenCE).

**Creador: freddVelp ([@freedsny](https://github.com/freedsny)).**

> Proyecto no oficial de un aficionado. No tiene relación con Microsoft, Xbox Game Studios, Halo Studios, Activision ni Bungie. Halo y Halo: Combat Evolved son marcas de Microsoft Corporation. **No incluye el juego**: necesitas tu propia copia (imagen de disco de Xbox, `.iso` o `.xiso`).

## Qué es

Halo Content Evolved es un Halo CE hecho sobre [OpenCE](https://github.com/OpenCommunityEdition/OpenCE) por Watanoge, con mucho más para la campaña y el multijugador. Esta versión le suma:

- **Los menús en español** (sin tildes: la fuente del juego no las tiene).
- **TRUCOS**, en **AJUSTES > tu perfil > JUEGO > TRUCOS** (en partida: **pausa > AJUSTES > JUEGO > TRUCOS**): munición infinita, modo dios, súper salto, armas y vehículos a elección, sobrescudo infinito, camuflaje, linterna, teletransporte, forzar punto de control, sin daño por caída, no caer del vehículo y más.
- **La flecha guía** (TRUCOS > GUIA) hacia el objetivo de la misión, un aliado o un enemigo.
- **El HUD movible**, el **HUD moderno** y el **radar redondo** (TRUCOS > HUD).
- **El menú de los tres dedos en español.** Toca la pantalla con tres dedos a la vez y sale un panel a la izquierda con **Trucos**, **Bots**, **Velocidad del juego**, **HUD**, **Cámara** y **Sistema**. Sus trucos son los mismos de TRUCOS: lo que prendes o apagas en uno se ve igual en el otro, y en su carpeta Trucos también están el sobrescudo, el camuflaje, la luz infinita, la linterna amplia y el teletransporte.

Y trae todo lo de Content Evolved:

| | |
|---|---|
| **Randomizer** | Cambia los enemigos, sus armas y las armas del suelo de cada nivel. Lo que una misión no trae lo copia de las otras misiones de la campaña |
| **Calaveras** | 40 calaveras: las de Master Chief Collection y nuevas |
| **Tag Injector** | Trae armas, enemigos y equipo de mapas de Custom Edition a la campaña |
| **Firefight** | Oleadas de enemigos o defensa de generadores en cualquier mapa multijugador |
| **Forge** | Construir mapas, solo o con amigos |
| **Puntaje y medallas** | Puntaje de la campaña, medallas, reto diario y clasificaciones en línea |

Cómo funciona cada cosa de Content Evolved está explicado (en inglés) en [su README](https://github.com/Watanoge/halo-content-evolved#readme).

## Jetpack: cómo volar

Pon **JETPACK** en ON (en TRUCOS o en el menú de los tres dedos). Luego **mantén disparar y granada a la vez** (en la pantalla, los dos botones con dos dedos) y vuelas hacia donde miras; suéltalos para bajar. Con el jetpack las caídas no te hacen daño. Puede dejar la misión trabada si llegas a donde no deberías: guarda antes.

## Cómo conseguir el APK

1. Entra a **Releases** de este repositorio.
2. Descarga el APK de la versión más reciente ("Latest"). Su nombre lleva la versión de Content Evolved y el número de la versión, por ejemplo `HaloCE-Evolved-trucos-build-143-n13.apk`.
3. Instálalo. Se llama **Halo C.E Evolved** y es **otra app**: se instala al lado de Halo C.E sin reemplazarla, con su propia carpeta y sus propias partidas.

> **Desde la versión con Content Evolved build-143** la app usa el nombre interno nuevo de Content Evolved (`com.halo.contentevolved.trucos`; antes `com.halo.decomp.evolved`). Es una app nueva: **desinstala la Halo C.E Evolved anterior** e instala esta. La primera vez vuelve a sacar los mapas de la ISO, y las partidas y perfiles de la anterior no pasan.
4. La primera vez te pide tu imagen de disco de Halo y saca los mapas de ahí.

### Actualización automática
Cada día, GitHub revisa si Content Evolved publicó una versión nueva (**Actions > Vigilar versiones nuevas de Content Evolved**). Si la hay, la compila con los trucos y la traducción, y la publica sola.

Si una compilación falla (por ejemplo, porque Content Evolved cambió algo que toca el parche), se abre un aviso en **Issues**. Tu versión anterior sigue funcionando.

### Versiones de prueba
Los cambios nuevos se prueban primero en la rama **`pruebas`**. Lo que se compila desde ahí es **privado** (borrador en Releases) y es otra app más, **"Evolved PRUEBA"**.

## Cómo está hecho este repositorio

No es un fork: solo guarda los cambios, y GitHub Actions los aplica al código de Content Evolved y compila el APK.

| Archivo | Para qué sirve |
|---|---|
| `.github/workflows/compilar.yml` | Descarga Content Evolved, aplica los trucos y la traducción, compila y publica el APK |
| `.github/workflows/vigilar.yml` | Revisa cada día si hay una versión nueva de Content Evolved y la compila |
| `parche/trucos.patch` | Los cambios al código: trucos, flecha guía, HUD y la pantalla TRUCOS dentro de JUEGO |
| `menus/regenerar_menus.py` | Genera las pantallas del menú y pasa los textos al español |
| `menus/textos_evolved.py` | Las traducciones de los menús de Content Evolved |
| `menus/textos_es.py`, `menus/menu_es.py`, `menus/header_*.png` | Las traducciones y los títulos dibujados que comparte con Halo C.E |
| `LICENSE` | La licencia GNU AGPL v3, la misma de OpenCE y de Content Evolved |

## Créditos y licencia

- **Halo Content Evolved**: [Watanoge/halo-content-evolved](https://github.com/Watanoge/halo-content-evolved), basado en [OpenCE](https://github.com/OpenCommunityEdition/OpenCE) y en el fork de [thelinkin3000](https://github.com/thelinkin3000/halo-ce-universal), bajo la licencia **GNU AGPL v3**. Los cambios de este repositorio se comparten bajo esa misma licencia (ver [LICENSE](LICENSE)).
- Traducción al español, trucos, flecha guía, HUD y compilación automática: **freddVelp** ([@freedsny](https://github.com/freedsny)).
- Halo: Combat Evolved © Microsoft Corporation.
