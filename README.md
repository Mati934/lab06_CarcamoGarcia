# Lab 06 — El mundo de Wumpus

## Cómo correr el juego

```
uv run python main.py
```

Se abre una ventana con una cueva de 4x4. El agente (Steeve) siempre empieza en la esquina `(0,0)`.

## Controles

| Tecla | Acción |
|---|---|
| Flechas | Mover al agente (modo manual) |
| Shift + flecha | Disparar la flecha en esa dirección |
| G | Agarrar el oro |
| C | Subir/salir de la cueva |
| A | Cambiar entre modo manual y modo automático |
| SPACE | El agente da un turno (solo en modo automático) |
| N | Cueva nueva (aleatoria) |
| R | Reiniciar la misma cueva |
| ESC | Salir |

En **modo manual** te mueves con las flechas. En **modo automático**, cada vez que apretas **SPACE** el agente decide y ejecuta un movimiento por su cuenta — así se puede ver, turno por turno, cómo va razonando.

## Cómo funciona el agente

El agente nunca ve dónde están el pozo ni el Wumpus. Esa información existe en el juego (por eso nosotros los vemos dibujados en el mapa), pero el agente solo recibe lo que percibe parado en su celda:

- **Brisa**: hay un pozo en alguna celda vecina.
- **Hedor**: hay un Wumpus en alguna celda vecina.
- **Brillo**: está parado sobre el oro.

Con eso, el agente arma su propia idea de qué celdas son seguras y decide su siguiente movimiento solo — nunca se le "avisa" dónde está el peligro.

### La base de conocimiento (deducción)

Cada vez que el agente visita una celda, guarda lo que sintió ahí. Con esas pistas va descartando posibilidades: por ejemplo, si nunca sintió brisa en ninguna celda vecina a una casilla, esa casilla no puede tener un pozo. Así arma, celda por celda, una lista de "esto es seguro", "esto es peligroso" o "todavía no lo sé".

Una regla importante: el agente **nunca adivina**. Si con las pistas que tiene no alcanza para probar que una celda es segura, la trata como desconocida y no se arriesga a entrar ahí, aunque en la práctica una celda "desconocida" no siempre sea realmente peligrosa.

### Cómo decide moverse (búsqueda)

Una vez que el agente sabe qué celdas son seguras, usa **búsqueda por anchura (BFS)** para planear el camino más corto hacia donde quiere ir: la celda segura sin explorar más cercana, el oro cuando ya lo detectó, o de vuelta a `(0,0)` para salir cuando ya lo tiene. El agente jamás pisa una celda que no haya podido demostrar segura primero.

### Prioridades del agente

1. Si está sobre el oro y no lo agarró todavía → lo agarra.
2. Si ya tiene el oro → vuelve a `(0,0)` y sube.
3. Si no → explora hacia la celda segura sin visitar más cercana.
4. Si no le queda ninguna celda segura por explorar → se queda quieto (prefiere no moverse antes que arriesgarse a entrar a una celda que no pudo probar segura).
