# Lab 06 — El mundo de Wumpus

Proyecto en pareja. La estructura separa **interfaz/mecánica del mundo** (ya
implementada) de **lógica del agente** (por implementar), para que ambas
partes se puedan trabajar en paralelo sin pisarse.

## Cómo correr

```
uv run python main.py
```

Con seed explícita (reproducible):

```
uv run python main.py --seed 123
```

## Controles

| Tecla | Acción |
|---|---|
| flechas | mover (modo manual) |
| shift + flecha | disparar en esa dirección (modo manual) |
| G | agarrar oro |
| C | subir/salir por (0,0) |
| A | alternar modo manual / auto |
| SPACE | un turno del agente (solo en modo auto) — ejecución paso a paso |
| N | cueva nueva (seed aleatoria) |
| R | reiniciar (misma seed, reproducible) |
| ESC | salir |

## Quién es dueño de qué archivo

**Interfaz / mecánica del mundo (ya implementado, no debería hacer falta tocarlo):**

- [wumpus/config.py](wumpus/config.py) — constantes: tamaño de grilla, colores, timing.
- [wumpus/environment.py](wumpus/environment.py) — la "verdad" del mundo: genera la cueva
  (aleatoria pero reproducible por seed), calcula percepciones (brisa, hedor,
  brillo), ejecuta acciones (`move`, `grab`, `shoot`, `climb`) y lleva el
  puntaje. No sabe nada de inferencia ni de decisiones del agente.
- [wumpus/view_state.py](wumpus/view_state.py) — structs `CellView` / `HudInfo` que conectan
  game.py con renderer.py.
- [wumpus/renderer.py](wumpus/renderer.py) — dibuja la grilla y la consola inferior con PyGame.
- [wumpus/game.py](wumpus/game.py) — loop principal, manejo de teclado, modo manual/auto,
  ejecución paso a paso. Instancia `KnowledgeBase` y `Agent` y los llama de
  forma defensiva (ver más abajo).

**Lógica del agente (a implementar por el equipo, esto es lo que califica la rúbrica):**

- [wumpus/knowledge_base.py](wumpus/knowledge_base.py) — clase `KnowledgeBase`: reglas de brisa/hedor
  como cláusulas lógicas e inferencia **por enumeración** para probar si una
  casilla es segura, tiene pozo o tiene Wumpus. Rúbrica ítems 2 y 4.
- [wumpus/agent.py](wumpus/agent.py) — clase `Agent`: decide la siguiente acción usando la
  KB y `search.py`, evitando casillas peligrosas y priorizando el oro.
  Rúbrica ítem 3.
- [wumpus/search.py](wumpus/search.py) — `find_path(start, goal, safe_cells, size)`: algoritmo
  de búsqueda (BFS/A\*) que planifica el camino solo por casillas
  demostradas seguras. Rúbrica ítems 4 y 5.

Cada uno de esos tres archivos tiene el contrato exacto (firmas de métodos,
qué debe devolver, qué no debe hacer) documentado en su docstring. Mientras
no estén implementados, sus métodos lanzan `NotImplementedError` a propósito
— `game.py` lo captura y muestra "?" / un mensaje en vez de crashear, así el
juego corre desde el día uno en modo manual mientras ustedes trabajan en la
IA.

## Contrato entre las dos partes

```python
kb = KnowledgeBase(size)
kb.tell_percept(cell, breeze=bool, stench=bool)   # game.py la llama tras cada movimiento
kb.infer_safe(cell)    -> True / False / None
kb.infer_pit(cell)     -> True / False / None
kb.infer_wumpus(cell)  -> True / False / None
kb.known_safe_cells()  -> set[(col, row)]

agent = Agent(environment, kb)
agent.decide_next_action() -> "up"|"down"|"left"|"right"|"grab"|"climb"
                               |"shoot_up"|"shoot_down"|"shoot_left"|"shoot_right"
                               | None

find_path(start, goal, safe_cells, size) -> list[str] | None
```

`environment.py` expone solo percepciones (`environment.last_percept`,
`environment.cell_percepts`, `environment.visited`, `environment.agent_pos`)
— el agente no debe leer `environment.pits` / `.wumpus` / `.gold`
directamente, eso sería hacer trampa respecto al objetivo del laboratorio
(demostrar seguridad por inferencia, no por conocer la verdad del mundo).

## Coordenadas

`(col, row)` con `(0, 0)` arriba-izquierda. `"up"` resta fila, `"down"` suma
fila, `"left"` resta columna, `"right"` suma columna.

## Entrega

Comprimir el proyecto `uv` como `lab06-apellido.tar` y subirlo a Blackboard.
Debe correr con `uv run python main.py`.
