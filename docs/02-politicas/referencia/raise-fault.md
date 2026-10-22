---
id: politica-raise-fault
titulo: RaiseFault — referencia completa
area: politicas
tags: [raisefault, errores, faultrules, faultresponse, mediacion, standard]
aplica_a: [apigee-x, apigee-hybrid, apigee-edge]
elemento_xml: RaiseFault
tipo_politica: standard
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/raise-fault-policy
fuente_edge: https://docs.apigee.com/api-platform/reference/policies/raise-fault-policy
revisado: 2026-10-22
---

# RaiseFault — referencia completa

> [!NOTE]
> **Tipo:** Standard. **Elemento raíz:** `<RaiseFault>`.
> **Aplica a:** Apigee X, hybrid y Edge. `<ReasonPhrase>` solo aparece en la documentación de Edge.

RaiseFault **provoca un error a propósito**: pasa el control al **flujo de error**, construye una respuesta de fallo (cabeceras, cuerpo, código) y se salta el resto de pasos. Después, Apigee evalúa las FaultRules; si no hay ninguna aplicable, devuelve la respuesta de la política. Normalmente lleva una `<Condition>` en el `<Step>` que la adjunta.

| Necesidad | Política |
|---|---|
| Cortar el flujo y responder con un error (validación, recurso no encontrado, regla de negocio) | **RaiseFault** |
| Construir la respuesta dentro de una FaultRule, ya en el flujo de error | [AssignMessage](assign-message.md) |
| Modificar la respuesta normal sin entrar en error | AssignMessage |

Visión general del manejo de errores en [Flujos y pipeline](../../01-proxies/02-flujos-y-pipeline.md).

## Sintaxis completa

```xml
<RaiseFault name="RF-Nombre" continueOnError="false" enabled="true">
  <DisplayName>Nombre legible</DisplayName>
  <IgnoreUnresolvedVariables>true</IgnoreUnresolvedVariables>
  <ShortFaultReason>false</ShortFaultReason>
  <FaultResponse>
    <AssignVariable>
      <Name>flujo.codigo_error</Name>
      <Value>PARAMETRO_FALTANTE</Value>
    </AssignVariable>
    <Copy source="request">
      <Headers>
        <Header name="x-request-id"/>
      </Headers>
    </Copy>
    <Remove>
      <Headers>
        <Header name="x-interna"/>
      </Headers>
    </Remove>
    <Add>
      <Headers>
        <Header name="x-error">{flujo.codigo_error}</Header>
      </Headers>
    </Add>
    <Set>
      <StatusCode>400</StatusCode>
      <Payload contentType="application/json">{"codigo":"{flujo.codigo_error}"}</Payload>
    </Set>
  </FaultResponse>
</RaiseFault>
```

## Atributos del elemento raíz

| Atributo | Obligatorio | Default | Qué hace |
|---|---|---|---|
| `name` | Sí | — | Nombre interno; aparece en el `faultstring` y en `raisefault.{name}.failed`. |
| `continueOnError` | No | `false` | Sin sentido aquí: el objetivo de la política es fallar. |
| `enabled` | No | `true` | Con `false` no se ejecuta. |
| `async` | No | `false` | **Obsoleto.** |

## Elementos hijos

| Elemento | Default | Resumen |
|---|---|---|
| `<IgnoreUnresolvedVariables>` | **`true`** | A diferencia de AssignMessage (`false`), aquí por defecto las variables sin resolver **no** dan error. |
| `<ShortFaultReason>` | `false` | `true` acorta el `faultstring` por defecto a solo el nombre de la política. |
| `<FaultResponse>` | — | La respuesta de error. Usa los **mismos** elementos que AssignMessage: `<AssignVariable>`, `<Copy source>`, `<Remove>`, `<Add>`, `<Set>` (`<Headers>`, `<Payload>`, `<StatusCode>`). |

Detalle de cada subelemento en [AssignMessage](assign-message.md#elementos-hijos). Todos admiten plantillas de mensaje. `<Payload>` admite `contentType`, y `variablePrefix`/`variableSuffix` para la sintaxis antigua de variables.

> [!WARNING]
> El default `<IgnoreUnresolvedVariables>true</IgnoreUnresolvedVariables>` hace que un `{variable}` mal escrito produzca un cuerpo con un hueco vacío **sin avisar**. Y si insertas datos en un JSON, escápalos con `{escapeJSON(…)}`.

Sin `<FaultResponse>`, la respuesta es el error genérico de Apigee:

```json
{"fault":{"faultstring":"Raising fault. Fault name : RF-Nombre","detail":{"errorcode":"steps.raisefault.RaiseFault"}}}
```

## Variables de flujo

| Variable | Contenido |
|---|---|
| `fault.name` | Siempre `RaiseFault` tras ejecutarse esta política. |
| `fault.type` | Tipo del fallo, o vacío. |
| `fault.category` | Categoría del fallo, o vacío. |

> [!TIP]
> Como `fault.name` vale siempre `RaiseFault`, en una FaultRule no puedes distinguir **qué** RaiseFault se disparó por `fault.name`. Usa `raisefault.{name}.failed` o una variable propia fijada con `<AssignVariable>` dentro de `<FaultResponse>`.

## Errores

### En runtime

| Código | HTTP | Causa |
|---|---|---|
| `steps.raisefault.RaiseFault` | 500 | La propia política (el código HTTP real es el que pongas en `<StatusCode>`). |

### Al desplegar

Ninguno propio.

### Variables de fallo

`fault.name = "RaiseFault"` y `raisefault.{name}.failed`.

## Ejemplos

### 1. Parámetro obligatorio

```xml
<Step>
  <Name>RF-Falta-Codigo-Postal</Name>
  <Condition>request.queryparam.codigo_postal = null</Condition>
</Step>
```

```xml
<RaiseFault name="RF-Falta-Codigo-Postal">
  <IgnoreUnresolvedVariables>false</IgnoreUnresolvedVariables>
  <FaultResponse>
    <Set>
      <StatusCode>400</StatusCode>
      <Payload contentType="application/json">{"codigo":"PARAMETRO_FALTANTE","detalle":"Falta el parámetro codigo_postal","traza":"{messageid}"}</Payload>
    </Set>
  </FaultResponse>
</RaiseFault>
```

### 2. Recurso no encontrado sin llamar al backend

```xml
<RaiseFault name="RF-404">
  <FaultResponse>
    <Set>
      <StatusCode>404</StatusCode>
      <Payload contentType="application/json">{"codigo":"NO_ENCONTRADO"}</Payload>
    </Set>
  </FaultResponse>
</RaiseFault>
```

Muy útil como último `<Flow>` sin condición del ProxyEndpoint: cualquier ruta no declarada devuelve 404 en vez de llegar al backend.

## Diferencias en Apigee Edge

| Aspecto | Apigee X / hybrid | Apigee Edge |
|---|---|---|
| `<Set>/<ReasonPhrase>`, `<Copy>/<ReasonPhrase>` | No documentado | Sí |
| `<FaultResponse>/<AssignVariable>` | Sí | No disponible en Edge for Private Cloud |
| Resto | Igual | Igual |

## Antipatrones

- Usar RaiseFault dentro de una FaultRule para construir la respuesta (usa AssignMessage: ya estás en el flujo de error).
- Confiar en `fault.name` para saber qué RaiseFault se ejecutó.
- Dejar el `faultstring` por defecto en errores públicos.

## Fuentes

- RaiseFault policy — Apigee X/hybrid: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/raise-fault-policy> (consultada directamente, contenido completo, 2026-10-22).
- Raise Fault policy — Apigee Edge: <https://docs.apigee.com/api-platform/reference/policies/raise-fault-policy> (consultada directamente, 2026-10-22).
