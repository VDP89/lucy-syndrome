---
id: scar_006
name: pre_deploy_audit
severity: alta
trigger: antes de git push o vercel deploy de sitio web
created: 2026-04-10
---

# SCAR 006: Auditoria pre-deploy obligatoria

## Que paso
Se deployaron multiples versiones del sitio web sin hacer un barrido completo de consistencia. El numero de telefono privado de Victor quedo publicado en la pagina de contacto mientras se habia cambiado en el footer y sticky CTA. Tambien quedaron frases "no ejecutamos" en paginas de sectores que ya se habian corregido en otras.

## Regla
Antes de CADA deploy a produccion, ejecutar auditoria de consistencia:

1. **Grep datos sensibles**: telefono privado, emails incorrectos, nombres que no deben aparecer
2. **Grep frases prohibidas**: "no ejecutamos", "no hacemos", "no somos" (regla no-cerrar-puertas)
3. **Grep textos desactualizados**: nombres de sectores viejos, tags viejos, alianzas viejas
4. **Verificar concordancia**: home cards ↔ sectores index ↔ paginas individuales ↔ footer
5. **Build test**: `npm run build` sin errores

## Comando rapido de auditoria
```bash
# En el directorio del sitio web
grep -rn "REDACTED_PHONE\|no ejecutamos\|no hacemos\|Solicitar consulta\|AEROPAR\|Grimaux\|Bioceánico\|suelo.cemento\|muelles.*dragado" src/
```

## Aplica a
Todo deploy de dgingenieriapy.com o cualquier sitio web publico de DG.
