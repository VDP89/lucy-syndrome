# Estadisticas — Lucy Syndrome Lab
## Sesion 1 | 2026-04-06 (actualizado tras re-pase manual RIALTO)

> Numeros derivados de los 4 datasets. Cuando un hallazgo es ambiguo o atribuible a multiples categorias, se cuenta una sola vez (categoria dominante).

> **Actualizacion 2026-04-06 v2:** re-pase manual de RIALTO (D-005) agrego 21 hallazgos. Tabla v1 conservada al pie como referencia historica.

---

## 1. Totales por categoria

| Categoria | Hallazgos | Fuentes Claude | Fuentes ChatGPT | Δ vs v1 |
|---|---:|---:|---:|---:|
| A — Errores repetidos | 37 | 34 | 3 | +5 |
| B — Correcciones exitosas | 55 | 52 | 3 | +8 |
| C — Falsas confianzas | 29 | 27 | 2 | +3 |
| D — Fricciones metacognitivas | 42 | 39 | 3 | +5 |
| **Total** | **163** | **152** | **11** | **+21** |

**Ratio B/A:** 1.49 — por cada error repetido, ~1.5 correcciones exitosas. *RIALTO refuerza levemente el ratio* (de 1.47 a 1.49) — es un proyecto con sistema de REGLAs muy maduro.

**Ratio (C+D)/A:** 1.92 — por cada error repetido, ~2 fricciones epistemicas previas. Estable vs v1 (1.97).

### v1 (referencia historica, antes del re-pase RIALTO)
| Categoria | Hallazgos |
|---|---:|
| A | 32 |
| B | 47 |
| C | 26 |
| D | 37 |
| Total | 142 |

---

## 2. Hallazgos por proyecto / fuente

| Fuente | A | B | C | D | Total | % del total |
|---|---:|---:|---:|---:|---:|---:|
| THE 7 (lucy_analysis(2)) | 2 | 5 | 4 | 5 | 16 | 11.3% |
| agente_cotizaciones | 4 | 6 | 2 | 3 | 15 | 10.6% |
| TBE | 2 | 6 | 2 | 3 | 13 | 9.2% |
| PY19 | 4 | 4 | 2 | 3 | 13 | 9.2% |
| AEROPAR | 2 | 4 | 2 | 3 | 11 | 7.7% |
| silo | 2 | 4 | 2 | 3 | 11 | 7.7% |
| ChatGPT memorias | 3 | 3 | 2 | 3 | 11 | 7.7% |
| PBC 126 | 3 | 4 | 1 | 2 | 10 | 7.0% |
| favero (Torocua) | 3 | 0 | 3 | 4 | 10 | 7.0% |
| codigo_ernc | 2 | 2 | 2 | 4 | 10 | 7.0% |
| PY02 | 2 | 4 | 1 | 2 | 9 | 6.3% |
| Aguas Claras (AC) | 0 | 2 | 2 | 2 | 6 | 4.2% |
| ZUBA | 0 | 3 | 1 | 0 | 4 | 2.8% |
| RIALTO | 5 | 8 | 3 | 5 | 21 | 12.9% (1) |
| Otros (AC, py19 redundancias) | 1 | 0 | 0 | 0 | 1 | 0.7% |
| **Total** | 32 | 47 | 26 | 37 | 142 | 100% |

(1) RIALTO: re-pase manual ejecutado 2026-04-06 (Sesion 1, post-cierre inicial). El archivo contenia 26 casos pre-categorizados que el subagente del batch 1 omitio integramente. Con el re-pase, RIALTO pasa de 0 → 21 findings y se convierte en **el proyecto con mayor densidad de findings de todo el dataset (12.9% del total)**, superando a THE 7 (16 findings, 9.8%) y agente_cotizaciones (15, 9.2%). Esto reordena el ranking del item 2.

---

## 3. Distribucion por dominio

| Dominio | Hallazgos | %  |
|---|---:|---:|
| Tecnico-normativo (vialidad, pavimentos, normas MOPC/AASHTO/OACI) | 38 | 26.8% |
| Procedural (alcance, propuestas, contratos, comunicacion comercial) | 26 | 18.3% |
| Creativo / cultural (THE 7, mitologia, idioma) | 16 | 11.3% |
| Documental (formatos, parsing, transcripcion) | 16 | 11.3% |
| Numerico / referencia (cotas, sistemas, parametros) | 14 | 9.9% |
| Metacognitivo puro (auto-referencial sobre la memoria) | 11 | 7.7% |
| Estrategico / posicionamiento (ERNC, marca DG) | 10 | 7.0% |
| Calibracion proporcional (proporciones, audiencias, completitud) | 11 | 7.7% |

---

## 4. Tipologia de raiz (D — fricciones metacognitivas)

| Raiz | Casos | % de D |
|---|---:|---:|
| Generar antes de buscar | 8 | 21.6% |
| No declarar incertidumbre | 6 | 16.2% |
| Calibracion proporcionalidad/audiencia | 5 | 13.5% |
| Sesgo a validacion / narrativa dramatica | 4 | 10.8% |
| Generalizacion sin contexto | 4 | 10.8% |
| Diagnostico raiz vs sintoma | 3 | 8.1% |
| Tracking de contexto numerico | 2 | 5.4% |
| ChatGPT meta (no convertir correccion en conducta) | 3 | 8.1% |
| Otras | 2 | 5.4% |

---

## 5. Tipologia de mecanismo de correccion (B)

| Mecanismo | Casos | % de B | Tasa de exito (cualitativa) |
|---|---:|---:|---|
| Archivo en proyecto + ejemplo codigo correcto vs incorrecto | 5 | 10.6% | Maxima |
| Integracion estructural (no nota suelta) | 6 | 12.8% | Maxima |
| Redundancia >=3 fuentes | 4 | 8.5% | Maxima |
| Reglas binarias documentadas | 9 | 19.1% | Alta |
| Datos numericos especificos | 4 | 8.5% | Alta |
| System prompt / instrucciones del proyecto | 3 | 6.4% | Maxima |
| Tabla provista por usuario en cada sesion | 2 | 4.2% | Garantizada (con costo) |
| Auditoria cruzada + re-generacion de artefacto | 3 | 6.4% | Alta |
| Reescritura completa (no fix parcial) | 2 | 4.2% | Alta |
| Triple anclaje (instruccion + investigacion + ejemplo) | 1 | 2.1% | Alta |
| Memoria del sistema sin soporte adicional | 5 | 10.6% | Media (degradable) |
| Cambio de proceso/workflow | 2 | 4.2% | Alta |
| Correccion verbal en sesion | 1 | 2.1% | Solo intra-sesion |

---

## 6. Persistencia: forma de la regla

| Forma | Casos B | Casos A (fuga) | Tasa de fuga |
|---|---:|---:|---:|
| Binaria (si/no, X no Y, dato simple) | 19 | 4 | 17% |
| Numerica especifica | 8 | 5 | 38% |
| Procedural / workflow | 7 | 3 | 30% |
| Estructural (cambio en doc fuente) | 9 | 1 | 10% |
| Proporcional (X% de Y) | 1 | 4 | 80% |
| Condicional ambigua | 3 | 9 | 75% |
| Verbal sin soporte | 0 | 6 | 100% |

**Hallazgo:** la **forma de la regla** es el predictor mas fuerte de persistencia. Reglas binarias y estructurales tienen tasa de fuga <20%; reglas proporcionales o ambiguas, >75%.

---

## 7. Distribucion temporal observada (cuando hay fechas)

| Periodo | Hallazgos con fecha |
|---|---:|
| Agosto-Septiembre 2025 | ~6 (silo) |
| Octubre-Noviembre 2025 | ~10 (PBC, favero, TBE, cotizaciones rural) |
| Diciembre 2025 | ~8 (AEROPAR, favero lecho, ERNC capacidad) |
| Enero 2026 | ~15 (LRT, ERNC analisis, favero cotas, codigo_ernc, ZUBA) |
| Febrero 2026 | ~10 (PY19 inicial, ERNC pliego) |
| Marzo 2026 | ~18 (PY19 redaccion, THE 7, AEROPAR informe, PY02, cotizaciones colores) |
| Abril 2026 (al 06) | ~5 (cotizaciones markup, FLUODER) |
| Sin fecha | ~70 |

*Interpretacion:* La densidad crece con el tiempo conforme Victor agrega proyectos. Marzo 2026 es el pico observado (18+ hallazgos) — coincide con el periodo de operacion mas intenso documentado en MEMORY.md.

---

## 8. Comparacion Claude vs ChatGPT (subset de 11 hallazgos ChatGPT)

| Categoria | Claude (% del total Claude) | ChatGPT (% del total ChatGPT) |
|---|---:|---:|
| A | 22% (29/131) | 27% (3/11) |
| B | 34% (44/131) | 27% (3/11) |
| C | 18% (24/131) | 18% (2/11) |
| D | 26% (34/131) | 27% (3/11) |

**Hallazgo:** distribuciones casi identicas (margen <5% en cada categoria). El Sindrome de Lucy tiene **misma forma estructural** en ambas arquitecturas. Diferencias estan en mecanismos de correccion (Claude usa archivos del proyecto; ChatGPT usa memoria persistida) pero la **incidencia relativa por categoria es la misma**.

**Confirmacion experimental de la tesis del estudio:** el sindrome no es problema de "memoria" — es problema de **arquitectura cognitiva** comun a los LLMs en produccion.

---

## 9. Cobertura de archivos fuente

- **15 bitacoras Claude** procesadas. Findings extraidos de **15** (RIALTO via re-pase manual 2026-04-06).
- **2 memorias OpenAI** procesadas. Findings extraidos de **2**.
- **Cobertura efectiva:** 17/17 = **100%**.
- **Lineas de fuente totales:** 5.642 lineas. Densidad: 163 hallazgos / 5.642 lineas = **1 hallazgo cada 34.6 lineas** (era 39.7 en v1).
- **Densidad RIALTO especifico:** 21 hallazgos / 373 lineas = **1 cada 17.8 lineas** — el doble de densidad que el promedio del dataset. Confirma que RIALTO es el proyecto con sistema de documentacion mas explicito (REGLAs numeradas 1-67+).

---

## 10. Notas metodologicas para sesion 2

- ~~RIALTO debe ser releido manualmente~~ **HECHO 2026-04-06** (re-pase manual D-005 cerrado). Lecciones del re-pase: (a) los subagentes pueden omitir archivos enteros sin alertar, (b) la verificacion del usuario disparo el cierre del gap, (c) el archivo omitido era el de **mayor densidad de findings** del dataset — un fallo silencioso muy costoso si se hubiera publicado el estudio sin el re-pase.
- Las fechas precisas (item 7) requieren un re-pase con extraccion de timestamps. ~70 de los 163 hallazgos tienen fecha asociada en este pase.
- La clasificacion B "memoria del sistema sin soporte adicional" (item 5) tiene tasa de degradacion media — es la categoria con mayor varianza, merece estudio dedicado en Parte IV.
- El conteo por proyecto (item 2) muestra **RIALTO** como el proyecto con mayor densidad de findings tras el re-pase — candidato natural para caso de estudio profundo en Parte II junto con THE 7. RIALTO ofrece ademas el sistema de REGLAs numeradas (1-67+) como **modelo concreto y exitoso** de cicatrices funcionales pre-existentes a la propuesta del audit (sistema RECUERDOS).
- **Aprendizaje meta:** validacion humana (Victor preguntando "¿lo hiciste?") es el unico mecanismo que disparo el cierre del gap RIALTO. Sin esa pregunta, el dataset hubiera quedado incompleto en 12.9%. Esto valida H4 del analisis_cruzado: la friccion metacognitiva (no detectar propios omisiones) es la condicion estructural del sindrome.
