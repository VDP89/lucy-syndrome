---
id: scar_005
nombre: validate_subagent_output
criticidad: alta
fecha_deteccion: 2026-04-06
fecha_codificacion: 2026-04-06
estado: activa
---

# scar_005 — Subagente puede omitir archivos sin alertar

## Que paso (origen)
**Caso vivo, Lucy Lab Sesion 1, 2026-04-06.** Despache un subagente Explore para procesar 8 bitacoras del lab Lucy y extraer findings categorizados. El subagente devolvio findings de 7 archivos. **Omitio integralmente el archivo RIALTO** (`RIALTO_Bitacoras_Consolidadas_Lucy_Analysis.md`, 373 lineas) sin alertar — su salida hablo de los otros 7 sin mencionar nada sobre RIALTO. Yo asumi cobertura completa del batch y cerre la sesion declarandola "completa" con RIALTO marcado como "evidencia insuficiente".

Victor pregunto socraticamente "¿hiciste el re-pase manual de RIALTO?". Tuve que reconocer que no. Al ejecutar el re-pase manual, el archivo contenia **26 casos pre-categorizados** (5 A + 8 B + 3 C + 5 D + 5 plataforma) — el doble de densidad que el promedio del dataset. RIALTO termino siendo el proyecto **con mayor densidad de findings de todo el dataset**.

Sin la pregunta de Victor, el dataset hubiera quedado incompleto en 14.8% (21 de 163 hallazgos perdidos). El estudio publicado habria carecido de la prueba empirica mas contundente del sistema RECUERDOS (RIALTO ya implementaba REGLAs numeradas exitosas).

**Memory origen:** `08_LABORATORIO_DG/00_PROYECTO_LUCY/05_META/log_sesiones_lab.md` § "Eventos meta-Lucy" Evento #5; `decisiones_metodologicas.md` D-005 actualizado.

## Donde aplica (trigger)
- Cualquier llamada al tool `Agent` que procese un batch de >=3 archivos o entidades
- Subagentes Explore con tareas de "leer N archivos y devolver sintesis"
- Subagentes general-purpose con tareas de auditoria, cobertura o extraccion masiva

## Por que se olvida (raiz)
- Los subagentes devuelven texto que **parece completo**. No hay metadata estructurado de "procese X de Y archivos".
- El instinto de "tarea cumplida" inhibe la verificacion post-hoc.
- La sintesis del subagente puede ser larga y bien escrita, lo que crea ilusion de cobertura.
- No hay tool de validacion automatica de cobertura en subagentes.

## Cicatriz (fix)
**Protocolo de validacion post-subagente en 3 pasos:**

### Paso 1 — En el prompt del subagente
Cuando despache un subagente para procesar un batch, **siempre incluir esta instruccion al final del prompt**:

```
COBERTURA OBLIGATORIA: tu output DEBE incluir una seccion al final llamada
"COBERTURA DEL BATCH" donde listas explicitamente:
- Archivo 1: <nombre> — N findings extraidos | "0 findings: <razon>"
- Archivo 2: <nombre> — N findings extraidos | "0 findings: <razon>"
- ...
Si un archivo no se proceso por completo, declarar el motivo. NO devolver
silencio sobre archivos del batch.
```

### Paso 2 — Validacion en el agente principal
Al recibir la salida del subagente, **antes de usarla**:

1. Buscar la seccion "COBERTURA DEL BATCH" en el output.
2. Verificar que **cada archivo del batch original aparece en la lista**.
3. Si algun archivo falta de la lista de cobertura → **alarma roja**: re-despachar subagente solo para ese archivo, o leerlo manualmente.
4. Si algun archivo aparece con "0 findings" sin justificacion clara → re-verificar manualmente (puede ser omision real, no ausencia de findings).

### Paso 3 — Auto-check al cierre de tarea
Antes de declarar "tarea completa":
- ¿Todos los archivos del batch fueron procesados o justificados?
- ¿Algun archivo aparece con un conteo sospechosamente bajo respecto a su tamano?
- ¿La cobertura es 100% o hay un porcentaje menor que necesite cierre?

## Como verificar
- Ratio de archivos procesados vs archivos del batch debe ser 100% (o tener justificacion explicita por exclusion)
- Si Victor descubre un archivo omitido tras declarar "tarea completa" → registrar como **fallo de cicatriz** maxima prioridad
- Auditoria post-tarea: contar cuantos batches procese sin validar cobertura

## Metricas
- Activaciones: 0
- Exito: 0 (N/A)
- Ultima aplicacion: nunca (esta cicatriz nace HOY del Evento meta-Lucy #5)
- Reincidencias post-cicatriz: 0

## Notas
Esta cicatriz es **especial** porque nace del propio laboratorio que estudia el Sindrome de Lucy. Es la primera cicatriz del sistema RECUERDOS que se origina en un caso *en vivo* de la propia ejecucion de Claude Code en este repo, no de bitacoras pasadas. Es la prueba mas pura de que el sistema funciona: un error documentado se convirtio en cicatriz funcional en cuestion de minutos.

Para el estudio Lucy (Parte V), este caso es central: un Lucy de 2do orden (Lucy operando sobre el laboratorio que estudia Lucy) fue cerrado por intervencion externa (Victor) y se materializo en una regla operativa permanente (esta cicatriz). El patron completo: **observacion → friccion → intervencion humana → cicatriz funcional**.
