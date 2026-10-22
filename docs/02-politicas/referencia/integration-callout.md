---
id: politica-integration-callout
titulo: IntegrationCallout — referencia completa
area: politicas
tags: [integrationcallout, application-integration, setintegrationrequest, asincrono, extensible]
aplica_a: [apigee-x, apigee-hybrid]
elemento_xml: IntegrationCallout
tipo_politica: extensible
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/integration-callout-policy
revisado: 2026-10-22
---

# IntegrationCallout — referencia completa

> [!NOTE]
> **Tipo:** Extensible. **Elemento raíz:** `<IntegrationCallout>`.
> **Aplica a:** Apigee X y hybrid. **No existe en Apigee Edge.**

IntegrationCallout **ejecuta** una integración de **Application Integration** que tenga un *API trigger*, en medio del flujo del proxy. No define qué integración ejecutar: eso lo hace antes [SetIntegrationRequest](set-integration-request.md), que deja el objeto de petición en una variable. IntegrationCallout lo envía y, opcionalmente, guarda la respuesta.

Si la integración **es** el backend, no necesitas esta política: usa un **IntegrationEndpoint** como TargetEndpoint.

## Autenticación

No hay elemento `<Authentication>`: Apigee añade el token por debajo. El proxy se **despliega con una cuenta de servicio** que tenga los roles IAM necesarios para ejecutar integraciones (ver *IAM roles for integrations* en la documentación de Application Integration).

## Sintaxis completa

```xml
<IntegrationCallout name="IC-Nombre" continueOnError="false" enabled="true">
  <DisplayName>Nombre legible</DisplayName>
  <AsyncExecution>false</AsyncExecution>
  <Request clearPayload="true">peticionIntegracion</Request>
  <Response>respuestaIntegracion</Response>
</IntegrationCallout>
```

## Elementos hijos

| Elemento | Obligatorio | Default | Resumen |
|---|---|---|---|
| `<AsyncExecution>` | No | Sin documentar | `true` = asíncrono, `false` = síncrono. Ver tabla de abajo. |
| `<Request clearPayload>` | **Sí** | `clearPayload="true"` | Variable con el objeto creado por SetIntegrationRequest. Con `clearPayload="true"`, el objeto se borra de memoria después de enviarlo. |
| `<Response>` | No | `integration.response` | Variable donde guardar la respuesta. El contenido queda en `{variable}.content`. |

> [!NOTE]
> La página oficial no indica el valor por defecto de `<AsyncExecution>`. Decláralo siempre de forma explícita.

### Modo síncrono vs. asíncrono

| | Síncrono (`false`) | Asíncrono (`true`) |
|---|---|---|
| Qué devuelve | La respuesta completa (IDs de ejecución y datos de salida) al terminar | Solo los **IDs de ejecución**, de inmediato, con `200 OK` |
| Cuándo empieza | De inmediato | En la `<ScheduleTime>` de SetIntegrationRequest; sin ella, enseguida, aunque puede tardar unos segundos |
| Tiempo máximo de ejecución | **2 minutos** | **50 minutos** |
| `<ScheduleTime>` | **No permitido**: produce `ExecutionFailed` | Permitido |

> [!WARNING]
> En modo síncrono, el proxy espera hasta **2 minutos**, más que el timeout habitual de un cliente o de un balanceador. Usa el modo síncrono solo con integraciones rápidas, y el asíncrono para procesos largos, devolviendo al cliente un `202` con el ID de ejecución.

## Variables de flujo

| Variable | Valor |
|---|---|
| `integration.response` (o la de `<Response>`) | La respuesta de la ejecución; el contenido en `.content`. |

Las variables `integration.*` de entrada (proyecto, nombre, región, trigger) las fija SetIntegrationRequest.

## Errores

### En runtime

Todos devuelven `500`.

| Código | Causa |
|---|---|
| `entities.UnresolvedVariable` | No se resuelven `integration.project.id` o `integration.name`. |
| `steps.integrationcallout.ExecutionFailed` | Application Integration devolvió 4xx o 5xx. Causas típicas: permisos de la cuenta de servicio, integración o trigger inexistentes, Application Integration no habilitado en el proyecto, o `<ScheduleTime>` con `AsyncExecution=false`. |
| `steps.integrationcallout.NullRequestVariable` | La variable de `<Request>` es nula. Normalmente falta el SetIntegrationRequest previo. |
| `steps.integrationcallout.RequestVariableNotMessageType` | La variable de `<Request>` no es un mensaje. |
| `steps.integrationcallout.RequestVariableNotRequestMessageType` | La variable de `<Request>` no es un mensaje de **petición**. |
| `messaging.adaptors.http.filter.GoogleTokenGenerationFailure` | La cuenta de servicio del despliegue no existe o está deshabilitada. |

### Variables de fallo

`fault.name` e `IntegrationCallout.{policy_name}.failed`. Ojo con la mayúscula inicial: es `IntegrationCallout.`, no `integrationcallout.`.

## Ejemplo: alta de cliente asíncrona con respuesta 202

```xml
<!-- 1. Preparar la petición -->
<SetIntegrationRequest name="SIR-Alta">
  <ProjectId>mi-proyecto</ProjectId>
  <IntegrationName>alta-cliente</IntegrationName>
  <IntegrationRegion>us-central1</IntegrationRegion>
  <ApiTrigger>api_trigger/alta-cliente</ApiTrigger>
  <Parameters>
    <Parameter name="datos" type="json" ref="request.content"/>
  </Parameters>
  <Request>peticionAlta</Request>
</SetIntegrationRequest>
```

```xml
<!-- 2. Ejecutar sin esperar -->
<IntegrationCallout name="IC-Alta">
  <AsyncExecution>true</AsyncExecution>
  <Request clearPayload="true">peticionAlta</Request>
  <Response>respuestaAlta</Response>
</IntegrationCallout>
```

Después, una política [AssignMessage](assign-message.md) construye un `202 Accepted` a partir de `respuestaAlta.content`, que trae el ID de ejecución.

## Diferencias en Apigee Edge

No existe en Edge.

## Antipatrones

- **Modo síncrono para procesos largos.** Bloquea la petición hasta 2 minutos.
- **Combinar `<ScheduleTime>` con `AsyncExecution=false`.** Es un error garantizado.
- **Desplegar sin cuenta de servicio, o con una sin roles de Application Integration.**
- **Omitir `<IntegrationName>` en SetIntegrationRequest.** Se ejecutan todas las integraciones con ese trigger.

## Fuentes

- IntegrationCallout policy — Apigee X/hybrid: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/integration-callout-policy> (consultada directamente, contenido completo, 2026-10-22).
