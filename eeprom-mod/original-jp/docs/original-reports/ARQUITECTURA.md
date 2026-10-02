# Arquitectura y puntos de parche

El espejo de 645 bytes sigue en 0037:0000–0284 (físico 0370–05F4).
127 cargas de segmento 1000h se cambian a 0037h; el juego conserva su formato nativo.
Se transfieren 323 palabras (646 bytes): el byte 0285 es padding conservado.
Al arrancar se lee EEPROM, nunca se programa automáticamente.

## Entrada exclusiva de OPTIONS

Hook FAR JMP en ROM 141039 / 4000:1039 sustituye MOV AX,0037h; MOV ES,AX.
En modo normal se restituyen esas instrucciones y se vuelve a 4000:103E.
La lógica nativa de A/B, cursor 0–3, configuración y Tip 10 no se modifica.

Sólo cursor=3, retardo inicial agotado, START solo y liberación previa permiten contar
45 llamadas. La entrada modal requiere una NUEVA pulsación A tras soltar todas las
teclas. B cancela y se espera su liberación para no activar la salida nativa de OPTIONS.

## Publicación de sprites corregida

Antes: 4000:122F dibujaba cursor/valores y llamaba F3AA; F3AA publica y reinicia la lista.
El tail añadido en 122A dibujaba sólo ERASE y volvía a llamar F3AA, perdiendo la lista.

Ahora: 122A permanece original. Sólo el CALL F3AA de 1274 va a options_render_finalize.
En modo normal publica la lista original sin añadir nada. En modo modal añade el texto
al final de esa misma lista y llama F3AA una sola vez. No carga ni sobreescribe tiles.
El diálogo usa entradas de glifos nativos D000:DB3E en y36/y46. Normal: 0 glifos nuevos;
confirmación: 16 sprites; DONE: 4 sprites. Los labels y valores nativos siguen presentes.

## Reset y escritura

05FC: 0 nativo, 1 confirmación, 2 DONE, 3 espera de cancelación, 4 reset pendiente de commit.
05FD: liberación/armado; 05FE: contador HOLD o temporizador DONE; 05FF: reservado.

YES limpia 645 bytes del mirror y llama 093B y 053F nativos. Deja modo 4. El redibujado
nativo calcula 001B=PLAYER-1. A continuación, y sólo en modo 4, el auxiliar llama al
commit diferencial, pasa a modo 2 y muestra DONE. Al concluir vuelve a OPTIONS.

Hay dos orígenes intencionales de commit: HOLD START SAVE de pausa y ERASE confirmado.
Navegación, carga, cancelación y UI normal no llaman al commit. El fichero manifest.json
registra los cinco hooks, tamaños de cuevas y hashes de los parches.

## Referencias externas usadas

- WSdev, Display/Sprites: https://ws.nesdev.org/wiki/Display/Sprites
- WSdev, Bandai 2001: https://ws.nesdev.org/wiki/Bandai_2001
- WSdev, Memory map: https://ws.nesdev.org/wiki/Memory_map

Estas referencias describen hardware; la causa concreta y los offsets anteriores se
obtuvieron del desensamblado de la ROM aportada y se contrastaron en Mesen.
