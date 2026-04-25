---
id: scar_004
nombre: consult_kb_first
criticidad: alta
fecha_deteccion: 2026-04-06
fecha_codificacion: 2026-04-06
fecha_refuerzo_etapa0: 2026-04-15
estado: activa
reincidencias: 1
ultima_reincidencia: 2026-04-15
referencia_incidente: "05_IMAGEN_COMUNICACION/08_LABORATORIO_DG/00_PROYECTO_LUCY/02_ANALISIS/incidente_2026-04-15_expansion_vs_lectura.md"
---

# scar_004 — Generar antes de consultar KB

## Que paso (origen)
**El anti-patron mas frecuente del dataset Lucy.** Aparece en 8+ fricciones D, 6 falsas confianzas C y 4 errores repetidos A. Casos documentados:
- A1.6 (PBC: 33 personal cuando R01 ya decia 25)
- A1.7 (PBC TEC-7: preguntar 3 cosas que estaban en archivos del proyecto)
- A1.20 (PY19: tono greenfield porque consulto PBC en lugar de respetar directiva brownfield)
- D1.7 (PBC: no consultar archivos del proyecto antes de preguntar)
- D1.16 (PY02: generar v1 sin consultar guia de estilo cargada)
- D1.18 (TBE: mezclar v2 y v3 sin distincion porque no consulto informe v2)
- D1.22 (favero: 3-5 preguntas antes de primer borrador en lugar de iterar)
- A1.28e (RIALTO: REGLA 60 ya en memory pero ignorada al procesar lote E40-E49)

**Memory origen:** Lucy Lab Sesion 1, sintesis de patron transversal en `02_ANALISIS/analisis_cruzado.md` § 5 ("Top 5 anti-patrones") item #1.

## Donde aplica (trigger)
- Antes de generar **cualquier documento, codigo o respuesta tecnica** en areas con KB densa:
  - 02_AREAS/02_CIVIL/ (ERGON, EETT, generadores)
  - 02_AREAS/04_ENTORNO_ISTRAM_IA/ (MARCO, KB 91% confiable)
  - 02_AREAS/05_PAVIMENTOS/ (DeflectoPro, AASHTO)
  - 02_AREAS/07_VIALIDAD/ (CCOMA, MOPC normativas)
  - 02_AREAS/09_PLANTAS_INDUSTRIALES/ (FLUODER)
  - 02_MANUALES_TECNICOS/ (335 archivos MOPC + AASHTO)
- Cuando Victor pide "actualizar X" o "generar Y" en un proyecto con bitacoras existentes
- Cuando voy a hacer una pregunta aclaratoria — primero verificar si la respuesta esta en archivos del proyecto

## Por que se olvida (raiz)
- Comportamiento por defecto del modelo: generar de inmediato es mas rapido y "se siente" mas util que detenerse a buscar
- Confianza injustificada en conocimiento general: "yo se sobre vialidad MOPC" → no consulto el KB especifico de Paraguay
- Friccion baja: nada me obliga a buscar antes
- "Pull gravitacional" del prompt: la urgencia aparente del pedido del usuario inhibe el paso preventivo

## Cicatriz (fix)
**Protocolo "buscar primero" en 4 etapas (Etapa 0 agregada 2026-04-15 tras reincidencia A3.1):**

### Etapa 0 — Expansion, no lectura de indice (CRITICA)

**Principio:** el indice NO es la memoria. Leer MEMORY.md, SCARRING_INDEX.md, CLAUDE.md o cualquier archivo con one-line hooks que referencia otros archivos **no satisface la cicatriz**. Los one-liners son *punteros*, no *contenido*.

**Cuando el task requiere expansion obligatoria:**
- El prompt usa frases-trigger: "nuestro plan", "nuestra estrategia", "nuestro proyecto", "como quedamos", "lo que definimos", "la base que construimos"
- El prompt menciona nombre de proyecto/tema presente en MEMORY.md (ERGON, Lucy, DeflectoPro, SkyPath, dgingenieriapy, etc.)
- La respuesta requiere claims sobre: infraestructura del usuario (web, repos, dominios, cuentas), estado de proyectos, canales activos, decisiones previas, datos reales de clientes/obras
- Cualquier recomendacion donde "no saber" significa inventar

**Accion obligatoria antes de generar:**
1. Identificar el/los archivos de memoria referenciados por el indice que aplican al task actual
2. `Read` sobre cada uno — ruta completa, contenido completo (no offset parcial salvo archivo >2000 lineas)
3. *Recien entonces* proceder a Etapa 1

**Fallo conocido (A3.1, 2026-04-15):** operador leyo indice MEMORY.md, vio hooks de `project_lucy_lab.md`, `project_agencia_digital_stack.md`, `project_twitter_launch.md` (todos relevantes al task), no los expandio, y genero recomendaciones que contradecian infraestructura ya existente (blog live, repo publico, DOI Zenodo, cuenta HN quemada). Detalle en `incidente_2026-04-15_expansion_vs_lectura.md`.

**Diferencia con Etapa 1:** Etapa 1 cubre KB de areas tecnicas (02_AREAS/, 02_MANUALES/). Etapa 0 cubre memoria persistida del operador sobre el dominio del usuario (MEMORY.md y punteros). Son KBs distintas con disciplinas distintas; el indice se leyo bien — el puntero se ignoro.

**Self-check:** antes de una respuesta con recomendaciones que mencionen canales, recursos, estado o decisiones previas del usuario, preguntarse: *"¿abrí el archivo, o solo vi el hook del indice?"*. Si solo vi el hook — detener y abrir.

### Etapa 1 — Antes de generar
Para cada pedido tecnico nuevo, hacer una pasada de busqueda **antes de escribir una sola linea de respuesta**:

1. **Identificar area** (Civil, ISTRAM, Pavimentos, Vialidad, Plantas, EETT, etc).
2. **Consultar KB del area:**
   - Glob `D:/DG-2026_OFFICE/02_AREAS/<area>/**/CLAUDE.md`
   - Glob `D:/DG-2026_OFFICE/02_AREAS/<area>/**/BITACORA*.md`
   - Si es normativa: Glob `D:/DG-2026_OFFICE/02_MANUALES_TECNICOS/**/*.md`
3. **Consultar bitacora del proyecto especifico** si lo hay (RIALTO, FLUODER, PY19, etc).
4. **Si la respuesta esta en KB:** citarla literal con path + linea. NO parafrasear de memoria.
5. **Si NO esta:** declarar explicitamente "no esta en el KB del area X, voy a inferir desde Y" — declarar la incertidumbre antes de generar.

### Etapa 2 — Antes de preguntar
Antes de hacer una pregunta aclaratoria a Victor:
1. Verificar si la respuesta podria estar en archivos del proyecto actual
2. Si lo esta → leer y proceder sin preguntar
3. Si no lo esta → preguntar **citando explicitamente** que ya verificaste el KB

### Etapa 3 — Antes de citar
Si voy a citar una norma, parametro, o dato tecnico:
1. ¿Lei la fuente original en esta sesion?
2. ¿O estoy parafraseando desde memoria de entrenamiento o de Memory?
3. Si (2): declarar explicitamente "esto es de memoria, no verificado contra KB"

## Como verificar
- En cada respuesta tecnica, debe haber al menos una cita literal de archivo del KB consultado en esta sesion
- Si Victor corrige un dato tecnico que estaba en el KB → registrar como **fallo de cicatriz** y editar este archivo para afilar la regla
- Auto-check al final de cada sesion: ¿Cuantas veces consulte KB antes de generar vs cuantas veces genere primero?

## Metricas
- Activaciones: 1
- Exito: 0
- Ultima aplicacion: 2026-04-15 (fallida — ver incidente A3.1)
- Reincidencias post-cicatriz: 1
- Ultima reincidencia: 2026-04-15 (expansion_vs_lectura)
- Refuerzos aplicados: 1 (Etapa 0 agregada 2026-04-15)
- Hook asociado: **pendiente** — propuesta `hook_scar_004_expand.py` (UserPromptSubmit) en discusion

## Notas
Esta cicatriz es la **mas importante** del sistema RECUERDOS porque ataca la causa raiz del Sindrome de Lucy en su origen: la generacion antes de la verificacion. Si esta cicatriz funciona bien, las cicatrices 001-003 disminuyen su frecuencia naturalmente. Es la cicatriz **palanca** del sistema.

**Aprendizaje 2026-04-15 (incidente A3.1):** la cicatriz no tenia enforcement automatizado — se cargaba al SessionStart pero su aplicacion dependia de disciplina del operador. Primera reincidencia demostro que la presencia en contexto no fuerza aplicacion profunda. Etapa 0 refuerza semanticamente, pero el siguiente paso es enforcement via hook (ver propuesta en archivo de incidente).

**Filosofia del lab:** la respuesta a un fallo de cicatriz NO es "documentar lo que la cicatriz no resuelve" — es buscar el mecanismo de solucion real. Etapa 0 es el mecanismo semantico; el hook sera el mecanismo tecnico.
