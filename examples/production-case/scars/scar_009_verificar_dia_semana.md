---
id: scar_009
nombre: verificar_dia_semana
criticidad: critica
fecha_deteccion: 2026-04-14
fecha_codificacion: 2026-04-14
estado: activa
---

# scar_009 — Dia de la semana incorrecto en fechas

## Que paso (origen)
**Reincidencia cronica, multiples sesiones.** El modelo asigna dias de la semana incorrectos a fechas. Errores documentados en sesion 2026-04-14:

| Fecha | Dije | Real |
|-------|------|------|
| Apr 14 | Lunes | **Martes** |
| Apr 16 | Miercoles | **Jueves** |
| Apr 18 | Viernes | **Sabado** |

Feedback `feedback_verificar_fechas.md` existe desde marzo 2026 y dice "SIEMPRE verificar dia de semana con WebSearch antes de actuar sobre fechas." Se sigue incumpliendo. Victor escalo: "seguimos con problemas con las fechas, es muy repetitivo."

El impacto es alto: al reagendar eventos en Google Calendar, un dia incorrecto puede mover una reunion al dia equivocado, crear conflictos con eventos reales, o dar instrucciones incorrectas a Victor.

## Donde aplica (trigger)
- Cualquier output que mencione una fecha con su dia de la semana
- Reagendamiento de eventos en Google Calendar
- Scout diario (encabezado con fecha + dia)
- Comunicaciones a Telegram (agenda)
- Cualquier planificacion semanal o mensual

## Por que se olvida (raiz)
- El modelo CREE saber que dia es cada fecha y no verifica
- La confianza en el calculo mental de dias es incorrecta — el modelo se equivoca frecuentemente
- No hay friccion antes de escribir "Lunes 14/04" — sale automatico
- El feedback existente se lee pero no genera un STOP antes de actuar

## Cicatriz (fix)
**Protocolo de verificacion OBLIGATORIO:**

### Regla unica — NUNCA calcular mentalmente
Antes de asociar un dia de la semana a una fecha:

1. **Usar la fecha del sistema** (`currentDate` en contexto) como ancla conocida
2. **Contar desde ahi** con aritmetica simple: si hoy es Martes 14/04, entonces 15=Mie, 16=Jue, 17=Vie, 18=Sab, etc.
3. **Si la fecha esta lejos (>7 dias):** usar WebSearch o `date -d` en Bash para confirmar
4. **NUNCA escribir un dia de la semana sin haberlo verificado**

### Autocheck rapido
Antes de enviar output con fechas:
- ¿Cada fecha tiene su dia correcto?
- ¿Verifique contando desde la fecha ancla del sistema?
- ¿Alguna fecha cae en fin de semana cuando deberia ser laboral (o viceversa)?

## Como verificar
- Si Victor corrige un dia de la semana → **fallo de cicatriz**
- Si un evento de calendario queda en dia incorrecto por error de dia → **fallo critico**
- Self-check: ¿use el ancla del sistema o "lo supe de memoria"? Si fue memoria → sospechoso

## Metricas
- Activaciones: 0
- Exito: 0 (N/A)
- Ultima aplicacion: nunca (cicatriz nace HOY de reincidencia cronica)
- Reincidencias PRE-cicatriz: 3+ (documentadas en sesion 2026-04-14, reportadas como "muy repetitivo")

## Notas
Esta cicatriz nace de la misma raiz que el Sindrome de Lucy: el modelo CREE que sabe algo y no lo verifica. En este caso no es conocimiento tecnico sino algo mas basico — que dia de la semana es una fecha. La solucion no es "recordar mejor" sino "no confiar en la memoria y verificar siempre."
