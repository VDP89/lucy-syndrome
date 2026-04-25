---
id: scar_007
nombre: memory_update_session_close
criticidad: alta
fecha_deteccion: 2026-04-14
fecha_codificacion: 2026-04-14
estado: activa
---

# scar_007 — Memorias no se actualizan al cierre sin pedido explicito

## Que paso (origen)
**Caso vivo, sesion 2026-04-14.** Se reorganizo el calendario editorial completo (19 operaciones: 4 deletes + 14 moves + 1 update), se descubrio el calendario dual "Linkedin DG", y se actualizo el estado de Lucy Syndrome (Reddit, HN, X, Minttu). Al cerrar sesion, NO actualice memorias proactivamente. Victor tuvo que preguntar "guardaste y actualizaste las memorias?" para que lo hiciera.

Resultado: 5 memorias pendientes (2 nuevas + 3 updates) que se hubieran perdido entre sesiones. La proxima sesion habria repetido el error de buscar solo en el calendario principal, y no habria tenido contexto de la reorganizacion.

## Donde aplica (trigger)
- Cualquier cierre de sesion (Victor dice "cerramos", "listo por hoy", "nos vemos", etc.)
- Sesiones donde se descubrio algo nuevo sobre el entorno, herramientas o flujos de trabajo
- Sesiones donde se tomaron decisiones que afectan sesiones futuras
- Sesiones donde se actualizo estado de proyectos en curso

## Por que se olvida (raiz)
- El cierre de sesion genera presion de "responder rapido y despedir"
- El resumen final se enfoca en lo HECHO, no en lo que falta PERSISTIR
- Las memorias no se sienten urgentes porque "ya estan en contexto" — pero ese contexto muere con la sesion
- No hay trigger automatico que fuerce revision de memorias al cierre

## Cicatriz (fix)
**Protocolo de cierre de sesion en 3 pasos:**

### Paso 1 — Deteccion de cierre
Cuando Victor indica cierre ("cerramos", "listo", "nos vemos", "corto aca"), ANTES de responder con el resumen:

### Paso 2 — Checklist de memorias
Preguntarse internamente:
1. ¿Descubri algo sobre el entorno/herramientas que una sesion futura necesita saber? → **reference** memory
2. ¿Cometi un error que no debo repetir? → **feedback** memory
3. ¿Cambio el estado de algun proyecto en curso? → **project** memory update
4. ¿Victor me corrigio o confirmo un approach no obvio? → **feedback** memory
5. ¿Hay decisiones tomadas que afectan trabajo futuro? → **project** o **feedback** memory

### Paso 3 — Guardar ANTES de despedir
Si hay memorias pendientes, guardarlas ANTES del mensaje de cierre. No esperar a que Victor pregunte. Incluir en el resumen final: "Memorias actualizadas: [lista breve]".

## Como verificar
- Si Victor pregunta "guardaste las memorias?" despues de un cierre → **fallo de cicatriz**
- Si la sesion siguiente repite un error que se descubrio en esta sesion → **fallo grave**
- Auto-check: en el mensaje de cierre, ¿aparece mencion a memorias actualizadas?

## Metricas
- Activaciones: 0
- Exito: 0 (N/A)
- Ultima aplicacion: nunca (cicatriz nace HOY del olvido en sesion 2026-04-14)
- Reincidencias post-cicatriz: 0

## Notas
Cicatriz simple pero de alto impacto. Las memorias son el unico mecanismo de continuidad entre sesiones. Olvidar actualizarlas equivale a perder el trabajo de la sesion para el futuro. El costo de guardar es bajo (2-5 minutos), el costo de no guardar es alto (repetir errores, perder contexto, frustrar al usuario).
