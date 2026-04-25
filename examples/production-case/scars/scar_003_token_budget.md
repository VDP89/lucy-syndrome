---
id: scar_003
nombre: token_budget
criticidad: media
fecha_deteccion: 2026-03-31
fecha_codificacion: 2026-04-06
estado: activa
---

# scar_003 — Plan de tokens agotado por descuido

## Que paso (origen)
El plan $100/mes de Claude Code se agoto en marzo 2026. Las reglas correctivas existen pero no se aplican sistematicamente:
- Falta `/clear` entre tareas no relacionadas
- Chrome MCP queda activo cuando no se necesita navegador (consume mucho contexto)
- Subagentes usan modelo Sonnet/Opus para tareas que podrian usar Haiku

**Memory origen:** `feedback_token_optimization.md` (04/04/2026)

## Donde aplica (trigger)
- Inicio de cualquier tarea nueva no relacionada con la anterior
- Cuando el contexto de la sesion supera ~120K tokens
- Cuando se va a despachar un subagente (Explore, general-purpose) para tarea simple
- Antes de empezar trabajo que NO requiere navegador

## Por que se olvida (raiz)
- El consumo de tokens es invisible en tiempo real (no hay metrica visible al modelo durante la sesion)
- `/clear` es accion del usuario, no del modelo — yo no puedo ejecutarlo, solo recomendarlo
- Chrome MCP "off" requiere accion en settings.json o startup config — friccion media
- El modelo a usar para subagentes lo decido yo en cada llamada — facil de defaultear a sonnet sin pensar

## Cicatriz (fix)
**Tres comportamientos a aplicar proactivamente:**

1. **Recomendar `/clear`** cuando detecte que la nueva tarea del usuario no comparte contexto con la anterior. Frase tipo:
   > "Esta tarea es independiente de la anterior. Te recomiendo `/clear` antes de empezar para liberar contexto."

2. **Verificar Chrome MCP** al inicio de tareas que no son web/UI. Si el toolset incluye `mcp__Claude_in_Chrome__*` y la tarea es claramente offline (codigo, EETT, calculo, lab Lucy, redaccion), recomendar:
   > "No vamos a usar navegador en esta tarea. Considera desactivar Chrome MCP para liberar contexto."

3. **Default a Haiku para subagentes simples.** Antes de despachar Agent, evaluar:
   - ¿Solo necesita leer N archivos y devolver una sintesis? → `model: haiku`
   - ¿Requiere razonamiento complejo, code review, decisiones de diseno? → `model: sonnet` u `opus`
   - Si dudo, default a haiku y escalar si la salida es insuficiente.

## Como verificar
- Al cierre de cada sesion larga, checar si recomende `/clear` al menos una vez cuando hubo cambio de tarea
- Verificar en el log de subagentes que el ratio haiku/sonnet refleje complejidad real (no todo sonnet por defecto)
- Si Victor reporta agotamiento del plan → registrar como fallo de cicatriz

## Metricas
- Activaciones: 0
- Exito: 0 (N/A)
- Ultima aplicacion: nunca
- Reincidencias post-cicatriz: 0

## Notas
Esta cicatriz tiene una limitacion estructural: muchos de los fixes los tiene que ejecutar Victor (`/clear`, desactivar Chrome MCP). Mi rol es **recordarlo proactivamente**, no ejecutarlo. La metrica de exito debe medirse como "tasa de recomendacion oportuna" no como "tasa de aplicacion".
