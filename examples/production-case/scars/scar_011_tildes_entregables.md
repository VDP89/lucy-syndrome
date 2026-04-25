---
id: scar_011
nombre: tildes_entregables
criticidad: alta
fecha_deteccion: 2026-04-04
fecha_codificacion: 2026-04-18
estado: activa
---

# scar_011 — Ortografía española completa en entregables

## Que paso (origen)

**Reincidencia documentada multiple. Formalizada 2026-04-18.**

Al generar el brand sheet ERGON v0.1 (HTML + manual MD), todo el texto salio sin tildes — funcion, fiscalizacion, gestion, ingenieria, Asuncion, tecnologia, tambien, pagina, economico, fisico — sin una sola tilde en todo el documento. Victor lo detecto:

> "No tiene tildes. En ningun solo lugar. Y es algo que ya me llamo la atencion tambien de la presentacion powerpoint que habiamos hecho. Lo que no entiendo es por que a veces si usas tildes y a veces no usas. Por ejemplo, todo el documento esta escrito sin tildes, y es superllamativo eso."

Historial de reincidencia:
- **Sesion DOCX 2026-04-04:** `feedback_docx_tildes.md` nace porque los DOCX generados via JS salian sin tildes. Solucion: `fix_tildes.py` post-generacion. Esta regla era para DOCX especificamente.
- **PPTX corporativo (pre-abril):** Victor tambien detecto tildes faltantes en una presentacion PowerPoint. No quedo memorizado formalmente.
- **Sesion brand ERGON 2026-04-18:** reincide en HTML + MD del brand sheet. Todo el documento sin una sola tilde.

Causa raiz identificada hoy: el habito defensivo de escribir sin tildes en archivos internos (`.claude/`, memoria, scripts) — justificado por corrupcion por encoding en el pipeline Windows/Git Bash — se filtra por inercia a entregables. El modelo no distingue entre los dos niveles.

## Donde aplica (trigger)

**Aplica** — entregables publicos donde la ortografia completa es obligatoria:

- Paths:
  - `05_IMAGEN_COMUNICACION/**`
  - `07_MARCA/**` (cualquier area)
  - `**/07_MARCA/**`
  - `04_COMERCIAL/**`
  - `04_LEADS/**`
  - `08_PROYECTOS/**/08_COMPENDIO_FINAL/**`
  - `02_AREAS/**/04_COMERCIAL/**`
  - Nombres con `brand`, `marca`, `landing`, `brochure`, `web`, `pptx`, `pdf`
- Extensiones: `.html` (si no es tool interno), `.md` (si es entregable no-interno), `.pptx`, `.pdf`, `.docx`
- Copy de landing, posts, emails firmados, bios, tarjetas

**NO aplica** — archivos internos donde el habito sin-tildes es justificado:

- `.claude/` completo
- `C:/.../memory/*.md`
- Scripts Python/JS internos
- Logs, bitacoras internas
- Scar files, hook scripts

## Por que se olvida (raiz)

- **Hábito defensivo justificado** en un ambito (interno) se filtra a otro (entregables) por inercia.
- Python y Git Bash en Windows **si** corrompen UTF-8 cuando se pasa por encodings mixtos — el habito tiene origen real, no paranoico.
- Al escribir rapido, la ortografia completa exige mas attencion activa — las tildes se omiten por economia cognitiva.
- El feedback original `feedback_docx_tildes.md` era muy especifico (DOCX via JS) y no generalizaba a "todo entregable en español".

## Cicatriz (fix)

### Regla central

**Dos niveles de escritura, no mezclar:**
- **Nivel 1 (interno):** sin tildes aceptado. `.claude/`, memoria, scripts, logs.
- **Nivel 2 (entregable):** ortografia española completa obligatoria. Todo lo que sale a cliente, web, PPTX, PDF, landing, firma email.

### Enforcement tecnico

Hook `hook_scar_011_tildes_entregables.py` en `PreToolUse Write|Edit`:
- Filtra por path (deliverable paths whitelisted arriba)
- Filtra por extension (`.html`, `.md`, `.pptx` no aplica directamente — se escribe via generator, pero el generator .py si detecta contenido con strings sin tildes)
- Grepea palabras comunes sin tilde en el contenido a escribir
- Si hay matches → emite warning con lista de palabras detectadas + recordatorio de usar fix_tildes

### Palabras-trigger del grep (no exhaustivo, cubre los tipicos)

```
-cion/-sion: funcion gestion fiscalizacion prediccion aplicacion seccion revision decision accion
             direccion dimension version construccion comunicacion regulacion informacion
             implementacion relacion navegacion
-ia hiato:   ingenieria tecnologia tipografia fotografia energia ergonomia teoria categoria
             filosofia geometria jerarquia
-ico/-ica:   fisico economico tecnico tecnologico tipografico grafico critico clasico
             historico mecanico publico semantico estrategico estetico logico
adverbios:   tambien despues ademas aqui alli ahi asi segun
sustantivos: pagina linea nucleo raiz pais titulo numero codigo proposito
ñ:           ano anos dueno diseno pequeno acompanado senal
propios:     Asuncion Aristoteles Etica Nicomaco Ingenieria
```

### Pipeline reutilizable

Para generadores (Python/JS que escriben entregables):
1. Escribir el script sin tildes (mas facil de editar sin encoding issues)
2. Ejecutar `fix_tildes.py` (DOCX) o `_fix_tildes_brand.py` (HTML/MD) post-generacion
3. Verificar visualmente antes de entregar

## Como verificar

- Grep de palabras-trigger en el archivo de entregable no devuelve matches
- Pre-entrega: ejecutar
  ```bash
  grep -nE '\b(funcion|gestion|fiscalizacion|prediccion|tambien|ingenieria|Asuncion|tecnico|economico|fisico|pagina|linea|ano|anos|dueno|diseno)\b' <archivo>
  ```
  → 0 matches = listo; >0 matches = aplicar fix_tildes
- Si Victor vuelve a decir "no tiene tildes" sobre un entregable post-cicatriz → fallo critico

## Metricas

- Activaciones: 0
- Exito: 0 (N/A)
- Ultima aplicacion: nunca (cicatriz nace 2026-04-18)
- Reincidencias post-cicatriz: 0
- Reincidencias PRE-cicatriz documentadas: 2 (PPTX, brand sheet ERGON)

## Notas

Cicatriz de criticidad **alta** (no critica): un entregable sin tildes se lee, no bloquea negocio, pero proyecta amateurismo — inconsistente con la postura editorial de las marcas DG/ERGON/MARCO.

Relacion con `scar_001_docx_tildes`: scar_001 es sobre el artifact especifico de DOCX generados via python-docx y JS (bug tecnico del encoding). scar_011 es la regla general: ortografia completa en todo entregable, sin importar la tecnologia de generacion. Juntas cubren el problema completo — scar_001 resuelve el mecanismo post-hoc (fix_tildes), scar_011 lo previene pre-hoc (no escribir sin tildes en primer lugar cuando es entregable).

Filosofia aplicada (`feedback_filosofia_lab_mecanismo.md`): ante la reincidencia, no catalogar "limitaciones" del sistema de tildes. Extender el mecanismo — hook + regla de dos niveles + pipeline de verificacion.
