# Reversibilidad — Sistema RECUERDOS Fase 2 hooks

> Como deshacer la Fase 2 si los hooks rompen workflows o generan ruido excesivo.

## Estado pre-Fase-2 (backup)
- Archivo: `D:/DG-2026_OFFICE/.claude/settings.json.bak.2026-04-06`
- Tamano: 412 bytes, 18 lineas
- SHA256 (primeros 16): `82270f9671654895`
- Contenido: `env.MAX_THINKING_TOKENS=8000` + un solo hook `PostToolUse` con matcher `Bash` (warning de output >150 lineas).

## Estado post-Fase-2
- Archivo: `D:/DG-2026_OFFICE/.claude/settings.json`
- Tamano: 1365 bytes, 52 lineas
- SHA256 (primeros 16): `6d90764ea6cfc635`
- Cambios: agregados eventos `SessionStart` (1 hook) y `PreToolUse` (2 entries: `Write|Edit` con 2 commands, `Task` con 1 command). PostToolUse Bash preservado intacto.

## Rollback completo (volver a estado pre-Fase-2)
```bash
cp "D:/DG-2026_OFFICE/.claude/settings.json.bak.2026-04-06" "D:/DG-2026_OFFICE/.claude/settings.json"
```
Tras ejecutar, abrir `/hooks` o reiniciar Claude Code para que el watcher recargue. Los scripts de hook quedan en `.claude/scarring/hooks/` pero nadie los invoca — pueden borrarse o dejarse como artefacto historico.

## Rollback parcial (deshabilitar SOLO un hook)
Editar `settings.json` y quitar la entry problematica. Ejemplos:

- **Quitar solo SessionStart** → eliminar la clave `"SessionStart"` y su array completo.
- **Quitar solo scar_001 docx** → en `PreToolUse` → entry `Write|Edit` → `hooks` array, quitar el item cuyo command apunta a `hook_scar_001_docx.py`.
- **Quitar solo scar_005 subagent** → eliminar la entry `PreToolUse` con matcher `Task` (entry completo, no la lista).

## Rollback nuclear (sin tocar settings.json)
Si el usuario no puede editar settings.json por alguna razon, tambien sirve:
```bash
rm -rf "D:/DG-2026_OFFICE/.claude/scarring/hooks/*.py"
```
Los hooks fallarian silenciosamente porque cada command termina con `2>/dev/null || true`. La sesion seguiria funcionando, los hooks no harian nada. **No recomendado** porque deja la config "muerta" en settings.json y confunde futuras sesiones.

## Verificacion post-rollback
```bash
python -c "
import json
with open('D:/DG-2026_OFFICE/.claude/settings.json', encoding='utf-8') as f:
    s = json.load(f)
print('hook events activos:', list(s.get('hooks', {}).keys()))
"
```

## Notas
- **Backup append-only:** no sobreescribir el .bak. Si se necesita un backup nuevo, crear `settings.json.bak.YYYY-MM-DD-N`.
- **El watcher de Claude Code recarga settings.json en vivo** (verificado en Sesion 2 — los hooks empezaron a disparar inmediatamente despues del Write a settings.json sin necesitar `/hooks` ni reinicio). Esto significa que un rollback tambien tomara efecto en vivo.
- Severity de los 4 hooks Fase 2 es `warn` (solo `additionalContext` + `systemMessage`, ningun `permissionDecision: deny`). **Ningun hook bloquea trabajo legitimo.** El peor caso de ruido es texto extra inyectado en el contexto.

---

## Fase C (2026-04-15) — Hook scar_004 expand_kb

### Motivacion
Incidente 2026-04-15 (A3.1, expansion_vs_lectura) — primera reincidencia registrada de scar_004 tras Fase 2. El operador cumplio la cicatriz formalmente (leyo indice MEMORY.md) y fallo funcionalmente (no expandio archivos puntero). Ver `05_IMAGEN_COMUNICACION/08_LABORATORIO_DG/00_PROYECTO_LUCY/02_ANALISIS/incidente_2026-04-15_expansion_vs_lectura.md`.

### Estado pre-Fase-C (backup)
- Archivo: `D:/DG-2026_OFFICE/.claude/settings.json.bak.2026-04-15`
- Tamano: 1365 bytes, 52 lineas
- Contenido: snapshot Fase 2 (SessionStart + PreToolUse Write|Edit + PreToolUse Task + PostToolUse Bash).

### Estado post-Fase-C
- Archivo: `D:/DG-2026_OFFICE/.claude/settings.json`
- Cambio: agregado evento `UserPromptSubmit` (1 hook) que dispara `hook_scar_004_expand.py`.
- Nuevo script: `hook_scar_004_expand.py` (~240 lineas) — parsea MEMORY.md, detecta frases-trigger y keywords de proyectos, inyecta `additionalContext` listando archivos a expandir con Read.

### Rollback Fase C solo (conservando Fase 2)
```bash
cp "D:/DG-2026_OFFICE/.claude/settings.json.bak.2026-04-15" "D:/DG-2026_OFFICE/.claude/settings.json"
```
El watcher de Claude Code recarga en vivo. El script `hook_scar_004_expand.py` queda en disco sin ser invocado — puede borrarse o conservarse.

### Rollback parcial Fase C
Editar `settings.json` y eliminar la clave `"UserPromptSubmit"` completa con su array. El resto de la configuracion Fase 2 sigue funcionando.

### Severity y blast radius
- Severity: **warn** (solo inyecta `additionalContext` + `systemMessage`, no bloquea, no modifica tools).
- Peor caso de ruido: texto extra en contexto cuando el prompt matchea falsos positivos (ej. keyword generica como "plan" que matchea proyectos civiles no relevantes).
- Falla silenciosa: `2>/dev/null || true` + `try/except` en el script → si MEMORY.md no existe o parsing falla, el hook sale sin output y la sesion continua normal.

### Verificacion post-activacion
Primer prompt con frase-trigger ("nuestro plan" / "nuestra estrategia") o keyword de proyecto (lucy, ergon, deflectopro, skypath, etc.) debe mostrar un systemMessage tipo:
`scar_004 Etapa 0: expandir N archivo(s) de memoria`
y el assistant debe ver en su contexto el listado de archivos a leer antes de responder.

### Rollout
- Semana 1 (2026-04-15 a 2026-04-22): **soft** — observar falsos positivos, afinar frases-trigger y stopwords si hace falta.
- Semana 2+: evaluar metricas reales (¿reincidencias A3.x bajan a 0? ¿ruido aceptable?). Si persiste falla, endurecer a bloqueo PreToolUse.

---
Documento creado 2026-04-07 al cierre de Sesion 2 Fase 2. Extension Fase C 2026-04-15.
