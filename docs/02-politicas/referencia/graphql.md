---
id: politica-graphql
titulo: GraphQL — referencia completa
area: politicas
tags: [graphql, parse, verify, esquema, profundidad, mediacion, standard]
aplica_a: [apigee-x, apigee-hybrid]
elemento_xml: GraphQL
tipo_politica: standard
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/graphql-policy
revisado: 2026-10-22
---

# GraphQL — referencia completa

> [!NOTE]
> **Tipo:** Standard. **Elemento raíz:** `<GraphQL>`.
> **Aplica a:** Apigee X y hybrid. **No existe como política en Apigee Edge.**

La política GraphQL **analiza** (`parse`) una petición GraphQL y la descompone en variables de flujo, la **verifica** (`verify`) contra un esquema, o ambas cosas. Con ella se aplican a GraphQL los mismos controles que a REST: límites de complejidad (profundidad, número de fragmentos, tamaño), restricción a consultas o mutaciones, y API products, VerifyAPIKey, OAuthV2 o Quota según la operación.

Formatos de petición soportados:

| Forma | Detalle |
|---|---|
| `POST` con `Content-Type: application/graphql` | El cuerpo es la consulta GraphQL. |
| `POST` con `Content-Type: application/json` | `{"query": "...", "operationName": "...", "variables": {...}}`. Apigee **ignora** `operationName` y `variables`. |
| `GET` | La consulta va en un query param. |

> [!WARNING]
> Verificar contra el esquema (`verify`) es **caro en CPU**, sobre todo con esquemas y consultas complejos, y puede añadir latencia significativa. Para limitar complejidad, Google recomienda `parse` con `<MaxDepth>` en lugar de `verify`.

## Sintaxis completa

```xml
<GraphQL name="GQL-Nombre" continueOnError="false" enabled="true">
  <Source>request</Source>
  <Action>parse</Action>
  <OperationType>query</OperationType>
  <MaxDepth>6</MaxDepth>
  <MaxCount>10</MaxCount>
  <MaxPayloadSizeInBytes>20480</MaxPayloadSizeInBytes>
  <ResourceURL>graphql://esquema.graphql</ResourceURL>
</GraphQL>
```

## Atributos del elemento raíz

| Atributo | Obligatorio | Default | Qué hace |
|---|---|---|---|
| `name` | Sí | — | Nombre interno. |
| `continueOnError` | No | `false` | Con `true`, una consulta inválida pasa. |
| `enabled` | No | `true` | Con `false` no se ejecuta. |

## Elementos hijos

| Elemento | Obligatorio | Default | Resumen |
|---|---|---|---|
| `<Source>` | Sí | `request` | Mensaje a analizar. |
| `<Action>` | No | — | `parse`, `verify` o `parse_verify`. `verify` también analiza. |
| `<OperationType>` | Sí | — | `query`, `mutation` o `query_mutation`. Si es `query` y llega una mutación, se rechaza con un `4xx`. |
| `<MaxDepth>` | No | ver nota | Profundidad máxima del árbol de la consulta. Funciona con `parse` y `parse_verify`. |
| `<MaxCount>` | No | 10 | Número máximo de consultas o fragmentos. |
| `<MaxPayloadSizeInBytes>` | No | sin límite | Tamaño máximo del cuerpo. |
| `<ResourceURL>` | Con `verify` | — | Esquema: `graphql://archivo.graphql`. **Un esquema por política**; para varios, varias políticas. |

> [!NOTE]
> **Discrepancias de la página.** El default de `<MaxDepth>` es **4** según la tabla y **10** según el texto (y la plantilla de la UI pone `10`). `<MaxPayloadSizeInBytes>` se describe "en kilobytes" pese al nombre. La sintaxis general lista `query|mutuation|all` para `<OperationType>`, mientras el detalle dice `query|mutation|query_mutation` (usa estos). Y la nota de `<Source>` dice que debe ser la consulta en bruto y no envuelta en JSON, en contradicción con el soporte de `application/json`. Declara siempre los valores y pruébalos en Debug.

> [!IMPORTANT]
> `<MaxDepth>` limita lo que Apigee **analiza** (evita variables enormes) pero, según la página, **la consulta se envía tal cual** al backend aunque supere la profundidad: comprueba en tus pruebas si la petición se rechaza o solo se trunca el análisis, y si necesitas un rechazo explícito, condiciona una RaiseFault sobre las variables `graphql.*`.

## Variables de flujo

Con `parse`, la consulta se publica con la convención `graphql.{nivel}.{definición}[.{subíndice}.{hijo}…]`:

| Variable | Ejemplo de valor |
|---|---|
| `graphql.operation.operationType` | `QUERY` |
| `graphql.operation.name` | `Characters` |
| `graphql.fragment.count` | `1` |
| `graphql.operation.selectionSet.count` | `1` |
| `graphql.operation.selectionSet.1.name` | `employee` |
| `graphql.operation.selectionSet.1.alias` | `admins` |
| `graphql.operation.selectionSet.1.argument.1.name` / `.value` | `id` / `IntValue{value=123}` |
| `graphql.operation.selectionSet.1.selectionSet.{n}.name` | `firstName` |
| `graphql.operation.selectionSet.1.directive.1.argument.1.value` | `VariableReference{name='withFriends'}` |
| `graphql.operation.variableDefinitions.{n}.name` / `.type` | `episode` / `TypeName{name='Episode'}` |

Los valores de argumentos se representan con su tipo de GraphQL (`IntValue{…}`, `EnumValue{…}`): compáralos teniendo en cuenta ese formato.

## Errores

La página no incluye sección de errores.

## Ejemplos

### 1. Solo consultas, con límites de complejidad

```xml
<GraphQL name="GQL-Solo-Lectura">
  <Source>request</Source>
  <Action>parse</Action>
  <OperationType>query</OperationType>
  <MaxDepth>5</MaxDepth>
  <MaxCount>5</MaxCount>
  <MaxPayloadSizeInBytes>10240</MaxPayloadSizeInBytes>
</GraphQL>
```

### 2. Mutaciones solo para apps con un scope concreto

```xml
<Step><Name>GQL-Parse-Todo</Name></Step>
<Step>
  <Name>RF-Mutacion-No-Permitida</Name>
  <Condition>graphql.operation.operationType = "MUTATION" and not (scope ~~ ".*escritura.*")</Condition>
</Step>
```

## Diferencias en Apigee Edge

No existe en Edge. Allí el análisis de GraphQL se hacía con JavaScript.

## Antipatrones

- `verify` en cada petición de un API de mucho tráfico sin medir el coste.
- No limitar profundidad ni fragmentos (ataques de consultas anidadas).
- Autorizar por ruta: en GraphQL todo va a `/graphql`; autoriza por operación.

## Fuentes

- GraphQL policy — Apigee X/hybrid: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/graphql-policy> (consultada directamente, contenido completo, 2026-10-22).
