---
id: politica-set-integration-request
titulo: SetIntegrationRequest — referencia completa
area: politicas
tags: [setintegrationrequest, application-integration, apigee-integration, api-trigger, integrationcallout, extensible]
aplica_a: [apigee-x, apigee-hybrid]
elemento_xml: SetIntegrationRequest
tipo_politica: extensible
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/set-integration-request-policy
revisado: 2026-10-22
---

# SetIntegrationRequest — referencia completa

> [!NOTE]
> **Tipo:** Extensible. **Elemento raíz:** `<SetIntegrationRequest>`.
> **Aplica a:** Apigee X y hybrid. **No existe en Apigee Edge.**

SetIntegrationRequest **prepara la petición** para ejecutar una integración de **Application Integration** (Apigee Integration) desde un proxy: proyecto, región, integración, *API trigger*, parámetros de entrada y, opcionalmente, hora programada. El objeto de petición queda en una variable; quien la ejecuta es la política [IntegrationCallout](integration-callout.md) o un **IntegrationEndpoint** (un TargetEndpoint de tipo integración).

Solo se pueden ejecutar integraciones que tengan un **API trigger**.

## Sintaxis completa

```xml
<SetIntegrationRequest name="SIR-Nombre" continueOnError="false" enabled="true">
  <DisplayName>Nombre legible</DisplayName>
  <ProjectId ref="flujo.proyecto">mi-proyecto</ProjectId>
  <IntegrationName ref="flujo.integracion">alta-cliente</IntegrationName>
  <IntegrationRegion ref="flujo.region">us-central1</IntegrationRegion>
  <ApiTrigger>api_trigger/alta-cliente</ApiTrigger>
  <ScheduleTime>2026-10-23T01:30:00Z</ScheduleTime>
  <Parameters substitutionVariableChar="#">
    <Parameter name="clienteId" type="string" ref="flujo.cliente_id">desconocido</Parameter>
    <Parameter name="monto" type="double" ref="transferencia.monto"/>
    <Parameter name="payload" type="json">#request.content#</Parameter>
    <ParameterArray name="productos" type="string" ref="flujo.productos">
      <Value>cuenta-ahorros</Value>
    </ParameterArray>
  </Parameters>
  <Request>peticionIntegracion</Request>
</SetIntegrationRequest>
```

## Elementos hijos

| Elemento | Obligatorio | Variable que fija | Resumen |
|---|---|---|---|
| `<ProjectId ref>` | No | `integration.project.id` | Proyecto de Google Cloud de la integración. |
| `<IntegrationName ref>` | No | `integration.name` | Integración a ejecutar. Empieza y termina con letra o número, sin espacios ni `--`/`__` seguidos. |
| `<IntegrationRegion ref>` | **Sí** | `integration.region` y `integration.target.url` | Región; genera la URL `https://{region}-integrations.googleapis.com`. Debe ser una región soportada por Application Integration. |
| `<ApiTrigger ref>` | **Sí** | `integration.api.trigger` | Formato `api_trigger/{nombre}`. |
| `<ScheduleTime>` | No | — | `yyyy-mm-ddThh:mm:ssZ` (UTC) o con desfase. Si es ahora o pasado, se ejecuta de inmediato. |
| `<Parameters substitutionVariableChar>` | No | — | Parámetros de entrada. |
| `<Request>` | No | — | Variable donde guardar la petición. **No** lo uses si ejecutas con un IntegrationEndpoint. |

En los elementos con `ref`: literal solo → se usa el literal; `ref` solo → si no resuelve o no es válido, error; ambos → si `ref` no resuelve se usa el literal (si resuelve pero es inválido, error).

> [!CAUTION]
> Si omites `<IntegrationName>`, se ejecutan **todas** las integraciones del proyecto que tengan ese API trigger. Declara siempre la integración.

### `<Parameter>` y `<ParameterArray>`

| | `<Parameter>` | `<ParameterArray>` |
|---|---|---|
| Atributos | `name`, `type`, `ref` | `name`, `type`, `ref` |
| Tipos | `integer`, `string`, `boolean`, `double`, `json` | `integer`, `string`, `boolean`, `double` (la tabla no incluye `json`, aunque un ejemplo lo usa) |
| Valor | Literal, `ref` o ambos | `<Value>` hijos (literal o `ref`, nunca vacíos) o `ref` a una variable array |

- Un `<Parameter>` o `<ParameterArray>` vacío se envía como `null`.
- Los valores JSON deben ser JSON válido.
- `substitutionVariableChar` define un delimitador para insertar variables dentro del valor (`#request.content#`). Solo funciona con parámetros `json` o `string` y arrays de `string`. Si la variable no resuelve, error.

## Variables de flujo

`integration.project.id`, `integration.name`, `integration.region`, `integration.target.url`, `integration.api.trigger`, más la petición en la variable de `<Request>`.

## Errores

### En runtime

Todos `500`, prefijo `steps.setintegrationrequest.`:

| Código | Causa |
|---|---|
| `EmptyParameterArray`, `EmptyParameterArrayValue` | Array o valor de array vacío. |
| `InvalidResolvedFlowVariable` | Una variable resolvió a un valor no válido (proyecto, nombre, región o trigger). |
| `MismatchedTypeAndResolvedRef`, `…OfParameterArray`, `…OfParameterArrayValue` | El valor resuelto no es del `type` declarado. |
| `RequestVariableNotMessageType`, `RequestVariableNotRequestMessageType` | La variable de `<Request>` existe y no es un mensaje de petición. |
| `UnresolvedVariable` | Variable sin resolver. |

### Variables de fallo

`fault.name` y `SetIntegrationRequest.{name}.failed`.

## Ejemplo: alta de cliente asíncrona

```xml
<SetIntegrationRequest name="SIR-Alta-Cliente">
  <ProjectId>mi-proyecto</ProjectId>
  <IntegrationName>alta-cliente</IntegrationName>
  <IntegrationRegion>us-central1</IntegrationRegion>
  <ApiTrigger>api_trigger/alta-cliente</ApiTrigger>
  <Parameters>
    <Parameter name="clienteId" type="string" ref="flujo.cliente_id"/>
    <Parameter name="datos" type="json" ref="request.content"/>
  </Parameters>
  <Request>peticionAlta</Request>
</SetIntegrationRequest>
```

Seguida de un IntegrationCallout que use `peticionAlta`.

## Diferencias en Apigee Edge

No existe en Edge.

## Antipatrones

- Omitir `<IntegrationName>`.
- Tomar proyecto, integración o trigger de la petición del cliente sin validarlos.
- Pasar el cuerpo completo del cliente a la integración sin validarlo antes.

## Fuentes

- SetIntegrationRequest policy — Apigee X/hybrid: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/set-integration-request-policy> (consultada directamente, contenido completo, 2026-10-22).
