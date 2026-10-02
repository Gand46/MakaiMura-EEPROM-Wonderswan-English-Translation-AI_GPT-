# Ejecución de pruebas

Los Lua usan OUT como carpeta de resultados, no rutas de un chat anterior.
run_validation.py prepara una copia aislada del ejecutable Mesen y de cada save.
Requiere el dump avanzado de prueba 95285ceb…9bdfe aportado en la conversación;
no está incluido para no distribuir tus partidas. Sus aserciones de 96 comandos
son específicas de ese fixture. Se necesita también la ROM original y la r2.

```text
python3 validation/run_validation.py --mesen /ruta/Mesen --original original.ws --rom r2.ws --seed avanzado.dmp --out resultados_nuevos --timeout 30 --total-timeout 540
python3 validation/compare_pixels.py resultados_nuevos
```

Pillow se requiere sólo para la comparación PNG. El código de compilación/aplicación
BPS usa la biblioteca estándar de Python. La batería preserva resultados parciales,
falla sin reintentar y no acepta una carpeta de salida ya existente. El driver ROM
no se instrumenta ni se modifica para estas pruebas; las entradas se simulan con Lua.
La prueba Tip 10 documenta la única excepción de fixture: un bit de desbloqueo en una
copia del save; no se altera el fichero de entrada ni la ROM.

Los logs incluidos se generaron con el supervisor utilizado en esta iteración;
las órdenes, los hashes del binario y los límites constan en cada run.json.
