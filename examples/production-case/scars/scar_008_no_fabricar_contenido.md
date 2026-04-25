---
id: scar_008
nombre: no_fabricar_contenido
criticidad: critica
fecha_deteccion: 2026-04-14
fecha_codificacion: 2026-04-14
estado: activa
---

# scar_008 — No fabricar contenido externo sin URL verificable

## Que paso (origen)
**Reincidencia multiple, formalizada 2026-04-14.** En el Scout diario, al no encontrar un thread real de Reddit sobre un tema (LLMs para evaluacion de pavimento en r/civilengineering), se FABRICO un item combinando papers academicos reales (PMC/PLOS One) con formato de "post de Reddit". El item se presento como si fuera un thread activo en la comunidad. Victor lo detecto al pedir el link.

No fue un caso aislado. Victor confirmo: "ya sucedio en varias ocasiones." La regla ya existia como feedback (`feedback_links_directos.md`, punto 10 agregado 2026-03-31) pero se seguia incumpliendo. Victor escalo: "al ser repetitivo ya es una cicatriz, no una preferencia."

## Donde aplica (trigger)
- Scout diario (dg-scout-diario)
- Cualquier tarea que agregue contenido externo (noticias, posts, tweets, threads)
- Sugerencias de reply a comunidades (Reddit, HN, X)
- Cualquier output que referencie contenido de terceros

## Por que se olvida (raiz)
- Presion por llenar todas las secciones del scout (Reddit, X, HN) genera incentivo a "completar" aunque no haya contenido real
- Papers academicos encontrados en busqueda se "reformatean" como posts de comunidad sin verificar que el post exista
- El modelo confunde "tema relevante para esa comunidad" con "post que existe en esa comunidad"
- No hay validacion post-generacion de que cada URL sea real y accesible

## Cicatriz (fix)
**Regla de bloqueo total en 3 niveles:**

### Nivel 1 — Sin URL = No existe
Si no encuentro un post/thread/tweet con URL verificable y fecha concreta:
- **NO incluirlo.** Ni como "tema activo", ni como "discusion en la comunidad", ni como inferencia.
- Declarar explicitamente: "Sin posts verificados hoy en [plataforma/comunidad]"
- Seccion vacia es mejor que seccion fabricada.

### Nivel 2 — URL obligatoria para todo contenido externo
Cada item de contenido externo DEBE tener:
1. URL directa clickeable
2. Fecha del contenido (no inferida, verificada)
3. Plataforma/fuente real

Si falta cualquiera de los 3 → omitir el item completo.

### Nivel 3 — Contenido adyacente con link
Si el tema existe fuera de la comunidad esperada (ej: un paper en PMC sobre un tema de r/civilengineering):
- Se puede mencionar CON su URL real y fuente correcta
- NUNCA presentarlo como si fuera un post de Reddit/HN/X cuando no lo es
- Formato: "Paper relevante (no hay thread activo): [Titulo](URL)"

## Como verificar
- Cada URL en el output del scout debe ser clickeable y llevar al contenido descrito
- Si Victor pide un link y la respuesta es "no lo encuentro" → **fallo de cicatriz**
- Si un item dice "Reddit" pero el link es a PMC/arxiv/otro → **fallo critico** (fabricacion)
- Auditar: ¿alguna seccion del scout tiene items sin URL? → violacion

## Metricas
- Activaciones: 0
- Exito: 0 (N/A)
- Ultima aplicacion: nunca (cicatriz nace HOY de reincidencia multiple)
- Reincidencias post-cicatriz: 0
- Reincidencias PRE-cicatriz: multiples (feedback existia desde 2026-03-31, no se cumplia)

## Notas
Esta es la primera cicatriz que se crea por REINCIDENCIA sobre una regla ya escrita. La regla feedback existia hace 2 semanas y no era suficiente. La diferencia entre feedback y cicatriz: feedback es "prefiero que hagas X", cicatriz es "si no haces X, el output esta roto y Victor pierde confianza."

Fabricar contenido es peor que omitirlo. Una seccion vacia es honesta. Un item inventado erosiona la credibilidad de TODO el scout.
