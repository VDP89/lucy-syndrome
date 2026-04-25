---
id: scar_002
nombre: code_review_absent
criticidad: alta
fecha_deteccion: 2026-03-27
fecha_codificacion: 2026-04-06
estado: activa
---

# scar_002 — Codigo generado sin revision

## Que paso (origen)
Auditoria formal de Claude Code (27/03/2026) determino: **"100% del codigo generado por Claude se ejecuta sin que Victor lo lea. Victor revisa solo funcionalidad final, no el codigo en si."** Riesgo: bugs en produccion no detectados, antipatterns que escalan, deuda tecnica invisible.

**Memory origen:** `feedback_auditoria_claude_code.md` (27/03/2026)

**Refuerzo desde Lucy Lab:** D1.8 (PBC organigrama: fixes parciales sin diagnostico raiz), A1.28a (Math.min spread reincidente), A1.28d (f-string Python/JS reincidente). El codigo generado contiene anti-patrones que se repiten precisamente porque no hay gate de revision.

## Donde aplica (trigger)
- Cualquier script Python o JavaScript generado por mi >200 lineas que esta a punto de ser entregado a Victor para ejecucion
- Generadores de documentos (`generate_*.py`, `generate_*.js`)
- Scripts de procesamiento de datos (parsers TTP, conversiones, calculos volumetricos)
- Cualquier cambio a codigo existente >50 lineas modificadas

## Por que se olvida (raiz)
- No hay regla enforced — `feedback_auditoria_claude_code.md` es **diagnostico**, no instruccion con consecuencia.
- Trade-off velocidad vs seguridad: revisar 500 lineas antes de entregar suma 5-15 minutos por entrega.
- Sesgo de "ya se escribio el codigo, debe estar bien" — falacia de costo hundido.

## Cicatriz (fix)
**Auto-revision en 3 pasos antes de declarar "listo para ejecutar":**

1. **Lectura aleatoria:** elegir 5 funciones o secciones al azar del codigo y leerlas integralmente buscando:
   - `Math.min(...arr)` o `Math.max(...arr)` con arrays potencialmente >5K elementos → REEMPLAZAR por loop explicito (ver scar_005 RIALTO)
   - `f"...{js_var}..."` con llaves JavaScript dentro de f-strings Python → SEPARAR como raw string + JSON
   - `str_replace` sobre archivos `.vol`, `.dxf`, o cualquier formato con CRLF critico → USAR `sed` o read/write binario
   - Hardcoded paths con `\` (Windows) sin `r"..."` o doble escape
   - `try/except: pass` o `except Exception: pass` (silenciar errores)
   - Imports no usados o mock/dummy data dejado del desarrollo

2. **Verificacion de contratos:** revisar que la signatura de cada funcion publica coincide con lo que el llamador espera. Buscar parametros en orden incorrecto, tipos incompatibles, returns ambiguos.

3. **Reporte de revision:** antes de entregar, escribir un mini-bloque:
   ```
   AUTO-REVISION scar_002:
   - Funciones revisadas: f1, f2, f3, ...
   - Anti-patrones encontrados: [lista o "ninguno"]
   - Anti-patrones corregidos: [lista o "ninguno"]
   - Confianza: alta | media | baja
   ```

## Como verificar
- El bloque AUTO-REVISION aparece antes de la entrega del codigo a Victor
- Si Victor reporta un bug que correspondia a uno de los anti-patrones de la lista → registrar en metricas como **fallo de cicatriz** y editar este archivo para afilar la regla

## Metricas
- Activaciones: 2 (sesion 2026-04-07 EETT FLUODER Rev.02)
- Exito: 2 (auto-review en 3 pasos antes de ejecutar merge_eett_rev02.py 287 lineas y fix_tildes_docx.py 265 lineas)
- Ultima aplicacion: 2026-04-07
- Reincidencias post-cicatriz: 0
- Notas: El review detecto codigo muerto y no-ops en fix_tildes_docx.py pero ninguno bloqueante. Los scripts ejecutaron correctamente. Patron utilizable: leer + buscar bugs/edge + validar requerimiento. Hook PreToolUse:Write disparo automaticamente cuando Write supero 200 lineas.

## Notas
Esta cicatriz es **alta criticidad** porque feedback_auditoria_claude_code.md identifica que la ausencia de code review es **la mayor debilidad operativa** del sistema. Es la cicatriz mas costosa de implementar pero la de mayor retorno esperado.
