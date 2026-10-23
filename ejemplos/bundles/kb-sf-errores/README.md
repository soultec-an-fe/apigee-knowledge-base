---
id: bundle-kb-sf-errores
titulo: Shared flow kb-sf-errores
area: ejemplos
tags: [bundle, sharedflow, flowcallout, errores, defaultfaultrule]
aplica_a: [apigee-x, apigee-hybrid]
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/fundamentals/shared-flows
revisado: 2026-10-23
---

# Shared flow kb-sf-errores

Formato de error **único** para toda la plataforma, invocado desde la `DefaultFaultRule` de cada proxy. Garantiza que cualquier fallo no previsto devuelve el mismo JSON, con el identificador de la petición para soporte, y **sin filtrar detalles internos**.

## Qué hace

| Paso | Política | Efecto |
|---|---|---|
| 1 | `AM-Clasificar-Error` | `kb.error.estado` toma `message.status.code`, o 500 si no hay |
| 2 | `AM-Error-JSON` | Cuerpo `{"error":"error_de_plataforma","estado":…,"peticion":"{messageid}"}`, cabecera `X-Request-Id` y elimina `X-Powered-By` y `Server` |

> [!IMPORTANT]
> El cuerpo **no incluye `fault.name`** a propósito: nombres como `ScriptExecutionFailed` o `SslHandshakeFailed` revelan cómo está construida la API. El detalle se consulta en Debug o en los logs, buscando por `messageid`. Los errores que el cliente sí debe distinguir (401, 403, 429) se tratan en FaultRules específicas **antes** de llegar aquí; ver [kb-api-key-cuota](../kb-api-key-cuota/README.md).

## Uso desde un proxy

Despliega el shared flow y añade en el proxy:

```xml
<FlowCallout name="FC-Errores">
  <SharedFlowBundle>kb-sf-errores</SharedFlowBundle>
</FlowCallout>
```

```xml
<DefaultFaultRule name="por-defecto">
  <AlwaysEnforce>false</AlwaysEnforce>
  <Step>
    <Name>FC-Errores</Name>
  </Step>
</DefaultFaultRule>
```

Ver [FlowCallout](../../../docs/02-politicas/referencia/flow-callout.md) y [manejo de errores](../../../docs/05-operacion/01-manejo-de-errores.md).

## Fuentes

- FlowCallout y AssignMessage: ver sus referencias en este repositorio, con las páginas oficiales consultadas el 2026-10-22.
