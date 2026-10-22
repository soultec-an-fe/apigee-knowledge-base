---
id: politica-trace-capture
titulo: TraceCapture — referencia completa
area: politicas
tags: [tracecapture, distributed-tracing, cloud-trace, jaeger, observabilidad, preview, extensible]
aplica_a: [apigee-x, apigee-hybrid]
elemento_xml: TraceCapture
tipo_politica: extensible
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/trace-capture-policy
revisado: 2026-10-22
---

# TraceCapture — referencia completa

> [!NOTE]
> **Tipo:** Extensible. **Elemento raíz:** `<TraceCapture>`.
> **Aplica a:** Apigee X y hybrid. **No existe en Apigee Edge.**
> **Estado: Preview (Pre-GA)**, sujeta a los *Pre-GA Offerings Terms*: se ofrece «tal cual» y puede tener soporte limitado.

Si tienes habilitado el **trazado distribuido** del runtime de Apigee (Cloud Trace o Jaeger), el runtime traza por defecto un conjunto de variables predefinidas. TraceCapture **añade variables propias** (de flujo, de política o personalizadas) a esos datos de traza, para que aparezcan en el informe de trazado.

## Sintaxis completa

```xml
<TraceCapture name="TC-Nombre" continueOnError="true" enabled="true">
  <DisplayName>Nombre legible</DisplayName>
  <Variables>
    <Variable name="canal" ref="request.header.x-canal">desconocido</Variable>
    <Variable name="producto" ref="apiproduct.name">sin-producto</Variable>
  </Variables>
  <IgnoreUnresolvedVariables>true</IgnoreUnresolvedVariables>
  <ThrowExceptionOnLimit>false</ThrowExceptionOnLimit>
</TraceCapture>
```

## Elementos hijos

| Elemento | Obligatorio | Default | Resumen |
|---|---|---|---|
| `<Variables>/<Variable name ref>` | No | — | `name` es como aparece en el informe de trazado; `ref`, la variable de origen. El texto del elemento es el **valor por defecto** si `ref` no está definida. |
| `<IgnoreUnresolvedVariables>` | No | Contradictorio (ver nota) | Con `true`, sigue aunque una variable no resuelva. Es distinto de `continueOnError`, que ignora cualquier error. |
| `<ThrowExceptionOnLimit>` | No | `false` | Qué hacer si una variable supera **256 bytes**: `false` la recorta a 256 bytes; `true` lanza `VariableValueLimitExceeded`. |

**Restricciones:**

- No se pueden trazar variables `private.*` ni `policy.secret`.
- Recomendación de Google: como máximo **15 variables con Cloud Trace** y **25 con Jaeger**.

> [!NOTE]
> **Contradicciones en la documentación oficial:**
> - `<IgnoreUnresolvedVariables>`: la descripción dice que el default es `true`, y una nota debajo dice que es `false`. Declara el valor siempre de forma explícita.
> - La tabla de elementos lista un `<MergeBehavior>` («comportamiento de combinación de mensajes de respuesta») que no aparece en la sintaxis ni en la referencia de elementos. Parece arrastrado de otra política (SetDialogflowResponse); no lo uses.
> - El ejemplo de `<ThrowExceptionOnLimit>` dice que fija el valor en `true`, pero muestra `false`.

## Variables de flujo

La política no crea variables de flujo: escribe en los datos de traza.

## Errores

### En runtime

Todos devuelven `500`.

| Código | Causa |
|---|---|
| `steps.tracecapture.UnresolvedVariable` | Una variable está fuera de alcance en ese flujo o no está definida. |
| `steps.tracecapture.VariableValueLimitExceeded` | `ThrowExceptionOnLimit=true` y una variable supera 256 bytes. |

### Variables de fallo

`fault.name` y `tracecapture.{policy_name}.failed`.

## Ejemplo: correlacionar trazas por cliente y operación

```xml
<TraceCapture name="TC-Negocio" continueOnError="true">
  <Variables>
    <Variable name="app" ref="developer.app.name">anonima</Variable>
    <Variable name="operacion" ref="current.flow.name">sin-flujo</Variable>
    <Variable name="correlacion" ref="request.header.x-correlation-id">sin-id</Variable>
  </Variables>
  <IgnoreUnresolvedVariables>true</IgnoreUnresolvedVariables>
</TraceCapture>
```

`continueOnError="true"` e `IgnoreUnresolvedVariables=true` hacen que la observabilidad nunca tumbe una petición.

## Diferencias en Apigee Edge

No existe en Edge.

## Antipatrones

- **Trazar datos personales o secretos.** Las trazas se retienen y las ven equipos de operación.
- **Superar las 15 o 25 variables recomendadas.**
- **Usarla en producción como si fuera GA.** Es Preview: ten un plan B (MessageLogging, DataCapture) para lo que sea crítico.

## Fuentes

- TraceCapture policy — Apigee X/hybrid: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/trace-capture-policy> (consultada directamente, contenido completo, 2026-10-22).
