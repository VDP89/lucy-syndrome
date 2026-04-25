---
id: scar_010
nombre: definir_por_lo_que_somos
criticidad: critica
fecha_deteccion: 2026-04-11
fecha_codificacion: 2026-04-18
estado: activa
---

# scar_010 — Definir DG y sus productos por lo que SON, nunca por lo que NO son

## Que paso (origen)

**Reincidencia multiple, formalizada 2026-04-18.** Al escribir el brand sheet de ERGON v0.1, el hero y la tesis repitieron el patron de negacion que Victor ya habia corregido varias veces antes:

- Hero: "No un software con cara de construccion. No una constructora con boton de IA."
- Tesis: "ERGON no es software con cara de construccion. No es construccion con boton de IA."
- Seccion entera titulada "Lo que ERGON NO es" con 5 bullets en negativo
- "Sensacion a evitar", "Referencias a evitar", "Sin gradientes, sin sombras, sin glassmorphism", "Nunca otros colores", "En lugar de X decir Y"

Victor lo detecto leyendo el mockup y escalo la regla a cicatriz:

> "algo que esta y siempre lo definimos en comunicacion e imagen es, nunca decir lo que no somos, o lo que no hacemos. siempre comunicar y definirnos por lo que somos. este error es repetitivo. y es clave en comunicacion"

Historial de reincidencia documentado:
- 2026-04-11: `feedback_no_cerrar_puertas.md` nace en memory tras correcciones a web publica ("no ejecutamos la obra", "no somos constructora")
- 2026-04-11: `feedback_web_contenido_sectores.md` refuerza la regla para sectores
- 2026-04-11: `feedback_posicionamiento_web_cristina.md` refuerza la regla en posicionamiento
- 2026-04-18: reincide en ERGON brand sheet (hoy)

La memoria feedback existia desde hace una semana y el error se repitio igual. Eso es exactamente el umbral que define cicatriz: feedback que no se sostiene sola.

## Donde aplica (trigger)

Todo copy publico de DG y sus productos (ERGON, MARCO, y cualquier marca futura de la casa):

- Landing pages (web, home, acerca, sectores)
- Taglines, headlines, hero, covers
- Brochures, PPTX, PDFs ejecutivos
- Brand manuals (tesis, postura, voz)
- Propuestas comerciales, pitch decks
- Posts de LinkedIn, Twitter, Instagram
- Bios, firmas de email
- Descripciones de producto
- Textos en app (header, empty states, onboarding)

Tambien aplica a descripciones/labels dentro de brand sheets o documentos internos cuando esos documentos se muestran a terceros (clientes, inversores, subcontratistas).

## Por que se olvida (raiz)

- **Diferenciacion por contraste es el default del cerebro.** Cuando pienso "que diferencia a ERGON de Procore" es tentador articularlo como "ERGON no es Procore". Es analiticamente util pero comunicacionalmente toxico.
- **La negacion regala al lector la asociacion con lo negado.** "No pienses en un elefante" instala al elefante. "ERGON no es tech-hype" deja la palabra "tech-hype" pegada a ERGON en la mente del lector.
- **Cerrar puertas futuras.** DG puede manana desarrollar obras propias, hacer EPC, licenciar SaaS. Cada "no hacemos X" publicado es compromiso hacia atras.
- **Ilusion de humildad tecnica.** Frases como "sin bombo", "sin teatro", "sin excepciones" parecen sobrias pero siguen definiendo por la ausencia de algo.
- **El patron se disfraza.** No siempre aparece como "no es X". Tambien como "sin Y", "nunca Z", "en lugar de W decir Q", "lo que NO somos", "sensacion a evitar", "referencias a evitar". Son todos la misma falla.

## Cicatriz (fix)

### Regla central
**En copy publico, describir SOLO lo que DG y sus productos SON y HACEN.** Cada atributo se formula como afirmacion sobre el propio, sin referencia a lo que no se es.

### Patrones prohibidos (copy publico)

| Patron | Ejemplo prohibido |
|---|---|
| `\bno\s+(es\|somos\|hacemos\|ejecutamos)` | "ERGON no es software con cara de construccion" |
| `\bNo\s+un\|No\s+una` | "No una constructora con boton de IA" |
| `[Ss]in\s+(bombo\|teatro\|excepciones\|gradientes\|sombras)` | "Sin gradientes, sin sombras" |
| `Lo que\s+(NO\|no)` | "Lo que ERGON NO es" |
| `a evitar` | "Sensacion a evitar", "Referencias a evitar" |
| `En lugar de [A-Z]` | "En lugar de X decir Y" |
| `Nunca otros` | "crema o grafito, nunca otros colores" |

### Patrones correctos

- "ERGON es la plataforma de fiscalizacion y gestion de obra civil con inteligencia integrada"
- "DG controla, revisa, acompana, gestiona"
- "Servicio profesional + plataforma con memoria"
- Listas: "Lo que ERGON ES" con atributos positivos
- Voz: "Vocabulario ERGON" con una sola columna de frases aprobadas

### Pre-publicacion: grep obligatorio
Antes de dar por cerrado cualquier copy publico, ejecutar busqueda de los patrones prohibidos en el archivo editado. Si hay matches, reformular.

Patron regex combinado para grep rapido:

```
\bno\s+(es|somos|hacemos|ejecutamos)\b|\bNo\s+(un|una)\b|[Ss]in\s+(bombo|teatro|excepciones|gradientes|sombras|glassmorphism)|Lo que\s+(NO|no)|a evitar\b|En lugar de [A-Z]|Nunca otros
```

### Excepciones legitimas
Reglas operativas internas (manuales de marca, checklists de cumplimiento) PUEDEN usar negacion cuando son boundary de aplicacion y el documento es solo para uso interno del equipo. Ejemplo aceptable: "mantener proporcion original" es preferible a "nunca distorsionar", pero "nunca distorsionar" es aceptable si no se publica.

Si un boundary se puede reformular en positivo (de "no inclinar" a "usar siempre en horizontal") preferir positivo aun en uso interno.

## Como verificar

- Grep de los patrones prohibidos en el archivo editado no devuelve matches en secciones de copy publico
- El documento se lee completo sin encontrar una sola frase que defina DG/ERGON/MARCO por lo que no es o no hace
- Cada atributo positivo tiene un verbo propio ("controla", "aprende", "anticipa", "aplica") en lugar de una negacion encadenada
- Si Victor vuelve a sacar el tema "este error es repetitivo" tras la fecha de esta cicatriz → fallo critico

## Metricas

- Activaciones: 0
- Exito: 0 (N/A)
- Ultima aplicacion: nunca (cicatriz nace 2026-04-18)
- Reincidencias post-cicatriz: 0
- Reincidencias PRE-cicatriz documentadas: al menos 3 (correccion a web publica, correccion a posicionamiento Cristina, correccion a ERGON brand sheet)

## Notas

Cicatriz de criticidad critica por tres razones:

1. **Reincidencia documentada multiple** con feedback preexistente insuficiente.
2. **Dano estrategico compuesto.** Cada copy con negacion publica le regala al lector la asociacion con lo que negamos Y cierra una puerta futura. El dano se acumula en cada pieza publicada.
3. **Es una regla de identidad de marca**, no de formato. Pertenece al mismo nivel que "no hablar de Fortaleza Carmelitas" o "firma nacional Ley 4727" — violarla rompe la postura que sostiene toda la comunicacion.

Relacion con otras cicatrices:
- **scar_008 (no_fabricar_contenido)** es sobre honestidad epistemica en contenido externo. scar_010 es sobre honestidad posicional en contenido propio.
- Ambas comparten la logica: feedback preexistente + reincidencia = cicatriz.

Sugerencia para Fase 2 posterior: agregar hook `PostToolUse` en Write/Edit que, cuando el path sea `05_IMAGEN_COMUNICACION/**` o `07_MARCA/**` o `04_COMERCIAL/**` o `*BRAND*` o `*MARCA*`, ejecute el grep de patrones y emita warning si hay matches. Pendiente de aprobacion de Victor antes de codificar.
