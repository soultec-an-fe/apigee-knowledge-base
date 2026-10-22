---
id: politica-parse-payload
titulo: ParsePayload — referencia completa
area: politicas
tags: [parsepayload, json-rpc, mcp, tools, routing, ia, extensible]
aplica_a: [apigee-x, apigee-hybrid]
elemento_xml: ParsePayload
tipo_politica: extensible
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/parse-payload-policy
revisado: 2026-10-22
---

# ParsePayload — referencia completa

> [!NOTE]
> **Tipo:** Extensible. **Elemento raíz:** `<ParsePayload>`.
> **Aplica a:** Apigee `1-17-0-apigee-7` o posterior y Apigee hybrid **1.16.1** o posterior. **No existe en Apigee Edge.**

ParsePayload extrae la **operación lógica** de un cuerpo estructurado y la publica en variables, para poder enrutar, autorizar o limitar por operación en lugar de por ruta. Hoy solo soporta **JSON-RPC 2.0** con el protocolo **MCP** (Model Context Protocol). En MCP todas las llamadas van a la misma URL con `POST`; la operación (`tools/call` de una herramienta concreta, `tools/list`…) va en el cuerpo. Ver [MCP en Apigee](../../07-ai-gateway/02-mcp-en-apigee.md).

> [!WARNING]
> **No funciona con streaming** del mensaje (petición o respuesta): con streaming activo provoca errores. Ver el antipatrón de payload con streaming en el [catálogo de antipatrones](../../09-antipatrones/01-catalogo-antipatrones.md).

## Sintaxis completa

```xml
<ParsePayload name="PP-Mcp" continueOnError="false" enabled="true">
  <Source>request</Source>
  <PayloadType>JSON-RPC-2.0</PayloadType>
  <Protocol>MCP</Protocol>
</ParsePayload>
```

## Elementos hijos

| Elemento | Obligatorio | Default | Valores |
|---|---|---|---|
| `<Source>` | No | `request` | `request` o `response` |
| `<PayloadType>` | **Sí** | — | `JSON-RPC-2.0` |
| `<Protocol>` | **Sí** | — | `MCP` |

## Variables de flujo

Prefijo `parsepayload.{name}.`:

| Variable | Contenido |
|---|---|
| `operation` | Identificador de la operación: `tools/call/{herramienta}` para llamadas a herramientas (`tools/call/get_weather`), `tools/list` para el listado. |
| `json-rpc.request.method` | Campo `method` (`tools/call`, `tools/list`…). |
| `json-rpc.request.id` | Campo `id`. |
| `json-rpc.request.params.name` | `params.name` (la herramienta, en `tools/call`). |
| `json-rpc.request.params.arguments.{arg}` | Cada argumento de `params.arguments`; los strings tal cual, objetos y arrays serializados como JSON. |

## Errores

La página no incluye sección de errores.

## Ejemplos

### 1. Autorizar herramientas por scope

```xml
<Step><Name>PP-Mcp</Name></Step>
<Step>
  <Name>RF-Herramienta-No-Autorizada</Name>
  <Condition>parsepayload.PP-Mcp.operation = "tools/call/transferir_fondos" and not (scope ~~ ".*pagos:escribir.*")</Condition>
</Step>
```

### 2. Cuota distinta por herramienta

```xml
<Quota name="QU-Por-Herramienta">
  <Identifier ref="flujo.cuota_clave"/>
  <Allow count="100"/>
  <Interval>1</Interval>
  <TimeUnit>hour</TimeUnit>
  <Distributed>true</Distributed>
</Quota>
```

Antes, una AssignMessage compone `flujo.cuota_clave` como `{client_id}:{parsepayload.PP-Mcp.operation}`.

> [!CAUTION]
> Los argumentos (`params.arguments.*`) vienen del cliente o del agente: no los uses como identidad ni para construir URLs o consultas sin validarlos.

## Diferencias en Apigee Edge

No existe en Edge.

## Antipatrones

- Usarla con streaming activo.
- Autorizar solo por ruta en un servidor MCP (todas las herramientas comparten URL).

## Fuentes

- ParsePayload policy — Apigee X/hybrid: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/parse-payload-policy> (consultada directamente, contenido completo, 2026-10-22).
