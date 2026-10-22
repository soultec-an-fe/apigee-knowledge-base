---
id: politica-http-modifier
titulo: HTTPModifier — referencia completa
area: politicas
tags: [httpmodifier, cabeceras, parametros, mediacion, assignmessage, standard]
aplica_a: [apigee-x, apigee-hybrid]
elemento_xml: HTTPModifier
tipo_politica: standard
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/http-modifier-policy
revisado: 2026-10-22
---

# HTTPModifier — referencia completa

> [!NOTE]
> **Tipo:** Standard. **Elemento raíz:** `<HTTPModifier>`.
> **Aplica a:** Apigee X y hybrid. **No existe en Apigee Edge.**

HTTPModifier es un **subconjunto de [AssignMessage](assign-message.md)** para tocar la parte HTTP de un mensaje: añadir, cambiar o quitar cabeceras, query params y form params, y fijar ruta, verbo, versión o código de estado. **No** puede modificar el cuerpo, copiar de otro mensaje ni asignar variables.

| | HTTPModifier | AssignMessage |
|---|---|---|
| Tipo | **Standard** (cualquier tipo de entorno) | **Extensible** (puede tener costo según la licencia) |
| `<Add>`, `<Set>`, `<Remove>`, `<AssignTo>` | Sí | Sí |
| `<Set>/<Payload>` | **No** | Sí |
| `<Copy>`, `<AssignVariable>`, `<Set>/<Authentication>` | **No** | Sí |

> [!TIP]
> Si solo necesitas cabeceras o parámetros (limpiar la API key, añadir un `x-request-id`, poner `Cache-Control`), usa HTTPModifier: al ser Standard, funciona en cualquier tipo de entorno y no consume el cupo de políticas Extensible.

Las operaciones se ejecutan **en el orden del XML**: `<Remove>` antes que `<Set>` si quieres vaciar y luego poner.

## Sintaxis completa

```xml
<HTTPModifier name="HM-Nombre" continueOnError="false" enabled="true">
  <DisplayName>Nombre legible</DisplayName>
  <AssignTo createNew="false" transport="http" type="request"/>
  <Remove>
    <Headers>
      <Header name="x-apikey"/>
    </Headers>
    <QueryParams>
      <QueryParam name="apikey"/>
    </QueryParams>
  </Remove>
  <Add>
    <Headers>
      <Header name="x-cliente">{client_id}</Header>
    </Headers>
  </Add>
  <Set>
    <Headers>
      <Header name="x-request-id">{messageid}</Header>
    </Headers>
    <Path>/v2/recurso</Path>
    <Verb>POST</Verb>
  </Set>
  <IgnoreUnresolvedVariables>false</IgnoreUnresolvedVariables>
</HTTPModifier>
```

## Atributos del elemento raíz

| Atributo | Obligatorio | Default | Qué hace |
|---|---|---|---|
| `name` | Sí | — | Nombre interno; da nombre a `httpmodifier.{name}.failed`. |
| `continueOnError` | No | `false` | Con `true`, ignora todos los errores (no solo los de variables). |
| `enabled` | No | `true` | Con `false` no se ejecuta. |

## Elementos hijos

| Elemento | Qué hace |
|---|---|
| `<AssignTo createNew transport type>` | Igual que en [AssignMessage](assign-message.md#assignto-sobre-qué-mensaje-actuar), con el mismo riesgo de `createNew="true"` sin nombre. |
| `<Add>` | `<Headers>`, `<QueryParams>`, `<FormParams>`. |
| `<Set>` | `<Headers>`, `<QueryParams>`, `<FormParams>`, `<Path>`, `<StatusCode>`, `<Verb>`, `<Version>`. |
| `<Remove>` | `<Headers>`, `<QueryParams>`, `<FormParams>`. Vacío = elimina todo. Índices para valores repetidos (`0` o negativo → `InvalidIndex`). |
| `<IgnoreUnresolvedVariables>` | Default `false`. |

Todos los hijos de `<Add>` y `<Set>` admiten plantillas de mensaje.

> [!NOTE]
> **Diferencia con AssignMessage en los verbos.** La página de HTTPModifier dice que `<QueryParams>` y `<FormParams>` funcionan solo con **`GET` y `POST`**, mientras que la de AssignMessage incluye también `PATCH`, `DELETE` (y `PUT` en `<Set>`). Si necesitas tocar query params en un `PUT`, `PATCH` o `DELETE`, compruébalo en Debug o usa AssignMessage.

## Variables de flujo

No publica variables de éxito.

## Errores

### En runtime

| Código | HTTP | Causa |
|---|---|---|
| `entities.UnresolvedVariable` | 500 | Una variable de plantilla no existe o está fuera de alcance. |
| `steps.httpmodifier.InvalidStatusCode` | 500 | El código de estado resuelto no es válido. |

### Al desplegar

| Error | Causa |
|---|---|
| `InvalidIndex` | Índice `0` o negativo en `<Remove>`. |

### Variables de fallo

`fault.name` y `httpmodifier.{name}.failed`.

## Ejemplo: no reenviar la API key y marcar la petición

```xml
<HTTPModifier name="HM-Limpiar-Y-Marcar">
  <Remove>
    <QueryParams>
      <QueryParam name="apikey"/>
    </QueryParams>
    <Headers>
      <Header name="x-apikey"/>
    </Headers>
  </Remove>
  <Set>
    <Headers>
      <Header name="x-request-id">{messageid}</Header>
      <Header name="x-app">{developer.app.name}</Header>
    </Headers>
  </Set>
</HTTPModifier>
```

## Diferencias en Apigee Edge

No existe en Edge; usa AssignMessage.

## Antipatrones

- Usar AssignMessage (Extensible) para cambios que HTTPModifier (Standard) cubre.
- `createNew="true"` sin nombre.

## Fuentes

- HTTPModifier policy — Apigee X/hybrid: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/http-modifier-policy> (consultada directamente, contenido completo, 2026-10-22).
