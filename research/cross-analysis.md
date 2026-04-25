# Analisis Cruzado — 4 Categorias del Sindrome de Lucy
## Lucy Syndrome Lab | Sesion 1 | 2026-04-06 (actualizado tras re-pase RIALTO)

> Patrones que emergen al cruzar A (errores repetidos), B (correcciones exitosas), C (falsas confianzas) y D (fricciones metacognitivas).

> **Nota v2 (post-re-pase RIALTO):** La adicion de 21 hallazgos de RIALTO refuerza todas las conclusiones de la version original sin contradecirlas. Adicionalmente, RIALTO aporta dos elementos nuevos: (a) **el sistema de REGLAs numeradas como modelo pre-existente exitoso** de cicatrices funcionales (validacion empirica del diseno propuesto en el audit § 3.4), y (b) **un caso unico de "correccion exitosa por inhibicion"** (B1.52: R5 pausado honestamente, no forzar v8) — la primera evidencia en el dataset de que una cicatriz funcional puede consistir en *no actuar*.

---

## 1. La cadena causal Lucy: D → C → A

**Hallazgo central:** las 4 categorias no son independientes. Forman una cadena causal:

```
[D] Friccion metacognitiva  →  [C] Falsa confianza  →  [A] Error repetido
       (no declarar "no se")        (output incorrecto)       (vuelve en otra sesion)
                                                                       ↓
                                                              [B] Correccion exitosa
                                                              (solo si se materializa
                                                              en archivo + binaria)
```

**Evidencia:**
- D1.6 (guarani como decoracion) → habilita C1.7-C1.10 (mitologia/idioma erroneos) → A1.8-A1.9 (proporcion 70/30 e literalidad recurrentes en THE 7).
- D1.12 (no declarar incertidumbre sobre TTP) → C1.5 (re-triangulacion como paso estandar) → A1.20 (efecto de "pull" de PBC en PY19, mismo mecanismo de generalizacion sin contexto).
- D1.7 (no consultar antes de preguntar) → C1.3 (PBC sin consultar Adenda) → A1.6 (33 vs 25 personal, repetido).

**Implicacion para el estudio:** Parte II ("La observacion desde produccion") debe presentar las 4 categorias **como una sola dinamica**, no como 4 fenomenos paralelos. La friccion metacognitiva es la condicion necesaria; el error repetido es el sintoma terminal; la correccion exitosa es la unica via de salida.

---

## 2. Mecanismos de persistencia (B) vs mecanismos de fuga (A)

**Pregunta:** ¿Por que algunas correcciones se vuelven cicatrices y otras se borran?

| Caracteristica del fix | B (persiste) | A (se fuga) |
|---|---|---|
| Forma de la regla | Binaria, numerica, estructural | Proporcional, condicional, ambigua |
| Soporte fisico | Archivo del proyecto + KB + memoria | Solo conversacion, o solo memoria difusa |
| Integracion | Cambio estructural en el output | Nota suelta o regla "ademas de" |
| Verificabilidad | Test post-hoc trivial | Requiere juicio |
| Trigger de aplicacion | Hook tecnico o consulta obligatoria | Memoria pasiva |

**Casos contrastantes:**
- B1.16 (DINAC) — dato factual binario en memoria → persiste sin esfuerzo.
- A1.8 (proporcion 70/30) — regla proporcional sin trigger tecnico → se fuga repetidamente.
- B1.41 (directriz no-citacion PBC en system prompt) — codificada en el lugar mas alto de la jerarquia → persiste perfectamente.
- B1.40 (WB-19 silo en memoria del sistema) → degradado 5 meses despues (caso A1.23). **Memoria pasiva = persistencia degradable.**

**Hallazgo:** la persistencia de una correccion es funcion de **(soporte fisico) × (binariedad) × (presencia en system prompt o hook obligatorio)**. Cualquier termino igual a cero → fuga inminente.

---

## 3. Areas mas afectadas

**Conteo cruzado de hallazgos por proyecto:**

| Proyecto | A | B | C | D | Total | Caracter dominante |
|---|---|---|---|---|---|---|
| agente_cotizaciones | 4 | 6 | 2 | 3 | 15 | Procedural — alcance contractual |
| THE 7 (lucy_analysis(2)) | 2 | 5 | 4 | 5 | 16 | Creativo — proporciones culturales |
| PBC 126 | 3 | 4 | 1 | 2 | 10 | Documental — adenda vs principal |
| AEROPAR | 2 | 4 | 2 | 3 | 11 | Tecnico — terminologia regulada |
| Aguas Claras (AC) | 0 | 2 | 2 | 2 | 6 | Tecnico — formatos propietarios |
| TBE | 2 | 6 | 2 | 3 | 13 | Multi-stakeholder — VMT/BAUEN |
| favero (Torocua) | 3 | 0 | 3 | 4 | 10 | Numerico — sistemas de referencia |
| PY02 | 2 | 4 | 1 | 2 | 9 | Formato — guias de estilo |
| PY19 | 4 | 4 | 2 | 3 | 13 | Documental — pull gravitacional PBC |
| silo | 2 | 4 | 2 | 3 | 11 | Normativo — mezcla norma/recomendacion |
| ZUBA | 0 | 3 | 1 | 0 | 4 | Comercial — limpio |
| codigo_ernc | 2 | 2 | 2 | 4 | 10 | Estrategico — capacidad/posicionamiento |
| RIALTO | 0 | 0 | 0 | 0 | 0 | Sin findings extraidos (revisar pase 2) |
| ChatGPT memorias | 3 | 3 | 2 | 3 | 11 | Meta — sobre la propia memoria |

**Observaciones:**
- **THE 7** (proyecto creativo) tiene el ratio mas alto de C/D (9 sobre 16) — los dominios creativos exponen al modelo a su falsa confianza cultural.
- **favero** (proyecto numerico) es el unico sin correcciones exitosas registradas. La complejidad de sistemas de referencia (≥3 superpuestos) excede capacidad de mantener consistencia.
- **agente_cotizaciones, PY19, TBE** son los mas balanceados: muchos errores Y muchas correcciones — proyectos donde Victor invirtio en documentar.
- **ZUBA** es el proyecto mas limpio: pocos errores, sin fricciones graves. Hipotesis: proyectos cortos con scope claro tienen menos exposicion al sindrome.

---

## 4. Diferencias Claude vs ChatGPT

**Claude (KB-based):**
- Errores tipicos: no consultar archivos disponibles, transcripcion literal del PBC, "pull gravitacional" de documentos consultados.
- Correcciones efectivas: archivos en el proyecto, system prompt, redundancia.
- Limitacion estructural: archivos subidos en sesion N no persisten en sesion N+1; conversation_search devuelve fragmentos.

**ChatGPT (memoria persistida):**
- Errores tipicos: instrucciones que requieren ser repetidas multiples veces, terminologia operativa que vuelve.
- Correcciones efectivas: reglas binarias (idioma), patrones de trabajo abstractos (modular).
- Limitacion estructural: la memoria es declarativa, no conductual. Almacena "que se dijo" pero no "como cambiar la conducta".

**Convergencia:** ambas arquitecturas padecen el mismo Sindrome Lucy. La diferencia es la **detectabilidad**:
- ChatGPT puede declarar honestamente "no puedo determinar si lo aplique" porque tiene reflexion limitada sobre su memoria.
- Claude opera sin sistema de memoria persistida visible al usuario, lo que hace el sindrome **mas silencioso pero potencialmente mas profundo**.

**Implicacion para Parte III ("La tesis"):** la solucion no es "mas memoria" ni "mejor KB". Es un mecanismo de **conversion correccion → modificacion conductual observable** (cicatriz funcional). Sin ese mecanismo, ambas arquitecturas son equivalentes en profundidad del sindrome, solo distintas en su superficie.

---

## 5. Anti-patrones recurrentes

**Top 5 anti-patrones (frecuencia transversal):**

1. **Generar antes de consultar** — aparece en 8 fricciones D + 6 falsas confianzas C + 4 errores repetidos A. Es el anti-patron mas extendido.
   - **Sub-patron 1.a (detectado post-publicacion, incidente 2026-04-15 / A3.1):** *Lectura de indice contada como consulta completa*. Variante en que la cicatriz se cumple formalmente (KB esta en contexto, indice leido) y falla funcionalmente (los archivos puntero del task actual no se expanden). Demuestra que el loop D→C→A sigue activo despues de la codificacion del sistema RECUERDOS si la cicatriz no distingue "leer indice" de "expandir puntero". Motiva sub-invariante I4.b — enforcement de expansion de memoria indexada — y propuesta de hook `hook_scar_004_expand.py`. Ver `incidente_2026-04-15_expansion_vs_lectura.md`.
2. **Adopcion acritica de input del usuario en dominio donde el modelo tiene knowledge** — D1.11 (franja AEROPAR), D1.6 (guarani), C1.18 (IVA ZUBA). Cuando el usuario aporta un termino, el modelo lo absorbe sin verificar contra su propio KB.
3. **Confundir completitud con calidad** — D1.1, D1.2, D1.26, A1.4 (LRT expansion), A1.21 (BID vs CAF transcripcion). El default "no omitir nada" es contraproducente en consultoria contractual.
4. **Pull gravitacional de documentos consultados repetidamente** — A1.20 (PBC PY19 → tono greenfield), A1.21 (BID transcrito literal), D1.25 (transcripcion PBC). Cuanto mas se consulta una fuente, mas pesa en el output, sobreescribiendo correcciones puntuales.
5. **No diferenciar normativo vs recomendacion** — D1.30 (silo), C1.21 (radio 60 m), D1.28 (formula deceleracion). Mezcla peligrosa en dominios regulados donde MOPC revisa cumplimiento.

---

## 6. Lecciones de diseno para la Parte IV (laboratorio)

**Principios derivados del cruce de categorias:**

1. **El protocolo Filtro Epistemico de 4 niveles necesita un quinto: "No declaro confianza hasta haber consultado fuentes en KB"** — porque el problema mas grave es la falsa confianza *previa* a la consulta.

2. **Las cicatrices funcionales deben tener dos componentes:** (a) un trigger tecnico (hook) que se dispara, (b) una metrica de activacion que permite refinar la regla con el tiempo.

3. **Las correcciones binarias deben preferirse a las proporcionales.** Si una regla suena como "70/30" o "calibrar segun contexto", refactorizarla como una serie de reglas binarias enumeradas.

4. **El "pull gravitacional" de documentos de referencia es un riesgo subestimado.** Cualquier doc >100K caracteres consultado repetidamente termina sobreescribiendo el system prompt en el comportamiento del modelo. Solucion posible: prohibir consulta directa al PBC y obligar consulta a un "extracto curado".

5. **El sindrome es mas severo en dominios donde el operador no tiene como verificar trivialmente.** Mitologia guarani, factor capacidad solar local, costos de roca en mercado paraguayo — todas son areas donde Victor tiene que asumir confianza porque no tiene tiempo de verificar. Las cicatrices deben priorizar estos dominios.

6. **Los proyectos cortos y simples (ZUBA) tienen menos sindrome que los largos y complejos.** Implicacion: el sindrome escala con la duracion y complejidad del proyecto. La unidad de medida del "Lucy Quotient" deberia ser **errores por sesion x sesiones por proyecto x meses transcurridos**.

---

## 7. Hipotesis para validar en Parte IV

**H1:** Implementar el sistema de cicatrices "RECUERDOS" reduce errores repetidos en dominios fragiles en >40% en 4 semanas.

**H2:** Reglas binarias persisten >90% del tiempo; reglas proporcionales <40% del tiempo, independientemente del soporte.

**H3:** Hay correlacion negativa entre **tamaño del documento de referencia consultado** y **fidelidad a las correcciones del system prompt**. El "pull gravitacional" es medible.

**H4:** La friccion metacognitiva (D) explica >70% de los errores repetidos (A). Es decir: si fuerzas al modelo a declarar incertidumbre antes de generar, el ciclo Lucy se rompe en su origen.

**H5:** Claude y ChatGPT tienen tasas similares de Sindrome Lucy en dominios comparables, pero distinta detectabilidad por el usuario.

---

## 7-bis. Hallazgos adicionales del re-pase RIALTO

**(a) RIALTO valida empiricamente el sistema RECUERDOS propuesto.** El sistema de REGLAs numeradas (1-67+) que Victor construyo para RIALTO es **exactamente** el patron que el audit § 3.4 propuso como "cicatrices funcionales": cada REGLA tiene (i) numero unico, (ii) descripcion del error, (iii) workflow correcto, (iv) almacenamiento en memory_user_edits + bitacora .md. Resultado documentado en el propio archivo RIALTO: las REGLAs con triple soporte (memory + bitacora + checklist en workflow) tienen tasa de persistencia ~100%; las correcciones verbales sin REGLA tienen ~0%. **El laboratorio Lucy ya tenia su prueba de concepto andando, sin saberlo.**

**(b) RIALTO confirma el "pull" de patrones idiomaticos de training data.** Los errores repetidos de RIALTO se concentran en JS/HTML rendering (3 de 5 errores repetidos: Math.min spread, Y invertida, f-string). El propio archivo lo diagnostica: *"el patron `Math.min(...array)` es el idiomatico en JS moderno y aparece en los datos de entrenamiento con mucha mas frecuencia que la alternativa loop. Sin una regla explicita en el contexto, Claude revierte al patron idiomatico"*. Esto es **el mismo mecanismo** que el "pull gravitacional" del PBC en PY19 (A1.20), pero a nivel de training data en lugar de documento del proyecto. La generalizacion: **cualquier "fuente con peso suficiente" sobreescribe correcciones puntuales**, ya sea un PDF de 550K caracteres o un patron idiomatico de billones de tokens.

**(c) Caso unico: cicatriz por inhibicion (B1.52).** Hasta este re-pase, todas las correcciones exitosas del dataset eran *acciones* (escribir correcto, generar bien). RIALTO aporta el primer caso de cicatriz que consiste en *no actuar*: R5 pausado tras 7 versiones fallidas. Victor: "no aprobado, volveremos luego". Claude registro en memory sin intentar v8. Para Parte III "cicatrices funcionales" esto es un componente importante: el sistema RECUERDOS debe poder codificar tambien **inhibiciones aprendidas** ("aqui no insistir") y no solo **acciones correctivas** ("hacer X en lugar de Y").

**(d) RIALTO confirma H4 (friccion D explica >70% de A).** De los 5 errores repetidos de RIALTO, 4 tienen friccion metacognitiva clara como antecedente: A1.28a (no consultar regla idiomatica) ↔ patron general de no declarar incertidumbre; A1.28b (Y invertida multi-causal en sesion larga) ↔ degradacion de coherencia que el modelo no detecta; A1.28e (REGLA 60 ignorada) ↔ no consulta proactiva al KB. Solo A1.28c (CRLF) fue genuinamente "descubrimiento empirico" sin friccion previa. **4/5 = 80%, consistente con H4.**

**(e) Caso pedagogico para Parte II:** la sesion larga "Analisis visual del barrio 3 con carga de archivos" (>100 intercambios, ~500 KB contexto) concentra Math.min/max + Y invertida + f-string + diagnostico prolongado de Y invertida. Es el caso individual mas denso del dataset. Candidato natural para el capitulo 5 ("El error que vuelve") como ejemplo de **degradacion intra-sesion observada empiricamente**.

---

## 8. Conclusion del cruce

El Sindrome de Lucy no es "el modelo se olvida". Es:

1. **El modelo nunca declara incertidumbre** (D) →
2. **Genera output con confianza injustificada** (C) →
3. **El output incorrecto se documenta como problema** (operador interviene) →
4. **La correccion se materializa con soporte debil** (memoria, conversacion, no archivo) →
5. **La proxima sesion regresa al estado original** (A) →
6. **Solo cuando la correccion alcanza forma binaria + soporte fisico + integracion estructural** se convierte en cicatriz funcional (B).

**El estudio puede ahora afirmar con datos:** la solucion del sindrome no es "memoria mas grande" — es **una arquitectura que fuerza la declaracion de incertidumbre antes de la generacion** y **una pipeline que materializa cada correccion en cicatriz binaria con trigger tecnico**.
