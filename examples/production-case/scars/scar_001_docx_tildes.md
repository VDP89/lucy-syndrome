---
id: scar_001
nombre: docx_tildes
criticidad: media
fecha_deteccion: 2026-04-04
fecha_codificacion: 2026-04-06
estado: activa
---

# scar_001 — DOCX generados sin tildes

## Que paso (origen)
Los DOCX generados via scripts JS (libreria docx-js) salen sistematicamente sin tildes a menos que se usen Unicode escapes manuales en headings MAYUSCULA. Caso documentado: EETT FLUODER SAECA Rev.01, donde "CAPITULO" aparecio en lugar de "CAPITULO" hasta correr `fix_tildes.py`.

**Memory origen:** `feedback_docx_tildes.md` (04/04/2026)

## Donde aplica (trigger)
- Edicion de cualquier `.py` que contenga `from docx` o `docx-js` en imports
- Edicion de `*generate*.py` o `*generador*.py` en el area EETT (`07_HERRAMIENTAS_GENERALES/01_EETT/`)
- Edicion de scripts en `02_AREAS/02_CIVIL/` que generan documentos Word
- Inmediatamente despues de regenerar un DOCX, **antes** de entregar al cliente

## Por que se olvida (raiz)
- Friccion tecnica baja: nada en el sistema impide generar el DOCX sin tildes. El error solo es visible al abrirlo.
- Regla "ejecutar fix_tildes.py despues" es post-hoc, no esta integrada al pipeline de generacion.
- El error es cosmetico, no funcional → no rompe nada → facil de pasar por alto.

## Cicatriz (fix)
1. Despues de regenerar cualquier DOCX, ejecutar:
   ```bash
   python "D:/DG-2026_OFFICE/07_HERRAMIENTAS_GENERALES/01_EETT/fix_tildes.py" <ruta_al_docx>
   ```
2. Verificar visualmente que las palabras en MAYUSCULA con tildes (CAPITULO, ESPECIFICACION, etc) quedaron correctas.
3. Si el script no existe en esa ruta o falla, **PARAR** y avisar a Victor antes de entregar.

## Como verificar
- Buscar en el DOCX la palabra "CAPITULO" o "ESPECIFICACION" — debe aparecer con tildes correctos
- Si se uso `python-docx` para abrir el archivo: `doc.paragraphs[i].text` debe contener `\u00cd` (I tildada) y similares

## Metricas
- Activaciones: 4 (sesion 2026-04-07 EETT FLUODER Rev.02)
- Exito: 4 (todas las generaciones de docx pasaron por fix de tildes adaptado)
- Ultima aplicacion: 2026-04-07
- Reincidencias post-cicatriz: 0
- Notas: Hook PreToolUse:Write disparo en cada Write de script Python relacionado con docx (merge_eett_rev02.py, fix_tildes_docx.py, align_titles_rev02.py, qa_fixes_rev02.py). Resultado: cero tildes residuales en docx final.
