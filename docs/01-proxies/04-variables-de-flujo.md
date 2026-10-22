---
id: proxies-variables
titulo: Variables de flujo — referencia
area: proxies
tags: [variables, flow-variables, request, response, message, target, system, error]
aplica_a: [apigee-x, apigee-hybrid]
fuente: https://docs.apigee.com/api-platform/reference/variables-reference
revisado: 2026-08-20
---

# Variables de flujo — referencia

Una variable de flujo es un par nombre/valor del contexto de ejecución. Su valor puede ser un primitivo (string, boolean, entero) o una referencia a un objeto instanciado por Apigee.

## Regla de ámbito

> [!IMPORTANT]
> **No todas las variables están disponibles en todos los puntos del flujo.**
> - En el **request PreFlow** no existe `response.*`.
> - En el **error flow** no existen `request.*` ni `response.*` — usa `message.*`.
> - `target.*` solo se puebla tras seleccionar el TargetEndpoint.

Esa es exactamente la razón de existir de `message.*`: es el único contenedor disponible en **todos** los contextos.

---

## `request.*` — petición del cliente

| Variable | Descripción | R/W |
|---|---|---|
| `request.content` | Payload | R/W |
| `request.verb` | Método HTTP (`GET`, `POST`, …) | R |
| `request.version` | Versión HTTP | R |
| `request.path` | Ruta del recurso **sin** query params | R |
| `request.uri` | Basepath + path + query params | R |
| `request.url` | URL completa hacia el target endpoint | R |
| `request.querystring` | Query string completa | R |
| `request.header.NOMBRE` | Valor de una cabecera | R/W |
| `request.header.NOMBRE.N` | Enésimo valor (índice **base 1**) de una cabecera multi-valor | R |
| `request.header.NOMBRE.values` | Todos los valores | R |
| `request.header.NOMBRE.values.count` | Número de valores | R |
| `request.headers.count` | Total de cabeceras | R |
| `request.headers.names` | Nombres de todas las cabeceras | R |
| `request.queryparam.NOMBRE` | Valor de un query param | R/W |
| `request.queryparam.NOMBRE.N` | Enésimo valor | R |
| `request.queryparam.NOMBRE.values` | Todos los valores | R |
| `request.queryparams.count` | Total de query params | R |
| `request.queryparams.names` | Nombres de todos los query params | R |
| `request.formparam.NOMBRE` | Valor de un form param | R |
| `request.formparam.NOMBRE.values` | Todos los valores | R |
| `request.formparams.count` / `.names` | Total / nombres | R |
| `request.formstring` | Cadena de formulario completa | R |
| `request.transport.message` | Objeto TransportMessage | R |
| `request.transportid` | ID del TransportMessage | R |

> [!TIP]
> Las cabeceras separadas por comas se **dividen** en valores individuales accesibles con `.N`. Acceder a una cabecera multi-valor con `request.header.NOMBRE` a secas devuelve solo el primero — es un [antipatrón documentado](../09-antipatrones/01-catalogo-antipatrones.md).

---

## `response.*` — respuesta del backend

| Variable | Descripción | R/W |
|---|---|---|
| `response.content` | Payload | R/W |
| `response.status.code` | Código HTTP (se puede **sobrescribir**) | R/W |
| `response.reason.phrase` | Frase de razón | R/W |
| `response.header.NOMBRE` | Valor de cabecera | R/W |
| `response.header.NOMBRE.N` / `.values` / `.values.count` | Acceso multi-valor | R |
| `response.headers.count` / `.names` | Total / nombres | R |
| `response.formparam.NOMBRE` | Form param | R/W |
| `response.formparams.count` / `.names` | Total / nombres | R |
| `response.transport.message` | Objeto TransportMessage | R |

---

## `message.*` — contenedor contextual

Espeja a `request` en el request flow, a `response` en el response flow, y es **el único disponible en el error flow**.

| Variable | Descripción |
|---|---|
| `message.content` | Payload (R/W) |
| `message.verb` | Método HTTP |
| `message.version` | Versión HTTP |
| `message.path` | Ruta completa sin query params |
| `message.uri` | URI completa con query params |
| `message.querystring` | Query string |
| `message.status.code` | Código HTTP del target |
| `message.reason.phrase` | Frase de razón |
| `message.header.NOMBRE` (`.N`, `.values`, `.values.count`) | Cabeceras |
| `message.headers.count` / `.names` | Total / nombres |
| `message.queryparam.NOMBRE` (`.N`, `.values`, `.values.count`) | Query params |
| `message.queryparams.count` / `.names` | Total / nombres |
| `message.formparam.NOMBRE` (`.values`, `.values.count`) | Form params |
| `message.formparams.count` / `.names` | Total / nombres |
| `message.formstring` | Cadena de formulario |
| `message.transport.message` | Objeto TransportMessage |

---

## `proxy.*` — configuración del ProxyEndpoint

| Variable | Descripción |
|---|---|
| `proxy.basepath` | Basepath configurado |
| `proxy.pathsuffix` | Lo que queda **después** del basepath |
| `proxy.name` | Atributo `name` del ProxyEndpoint |
| `proxy.url` | URL completa de la petición con query params |
| `proxy.client.ip` | Dirección `X-Forwarded-For` del handshake externo |

---

## `target.*` — conexión con el backend

| Variable | Descripción | R/W |
|---|---|---|
| `target.url` | URL configurada del TargetEndpoint | R/W |
| `target.host` | Nombre de dominio del backend | R |
| `target.ip` | IP del backend | R |
| `target.port` | Puerto | R |
| `target.basepath` | Ruta del recurso en la URL del target | R |
| `target.scheme` | `http` o `https` | R/W |
| `target.name` | Nombre del target que recibe el mensaje | R |
| `target.copy.pathsuffix` | Si se propaga el pathsuffix al backend | R/W |
| `target.copy.queryparams` | Si se propagan los query params | R/W |
| `target.ssl.enabled` | TLS activo | R |
| `target.expectedcn` | Common Name esperado en el certificado | R/W |
| `target.cn` / `target.country` / `target.locality` / `target.state` / `target.organization` / `target.organization.unit` / `target.email.address` | Campos del certificado TLS del backend | R |
| `target.sent.start.timestamp` / `.end.timestamp` | Envío al backend (ms epoch) | R |
| `target.received.start.timestamp` / `.end.timestamp` | Recepción del backend (ms epoch) | R |

**Latencia del backend** = `target.received.end.timestamp - target.sent.start.timestamp`.

---

## `client.*` — conexión con el cliente

| Variable | Descripción |
|---|---|
| `client.ip` | IP del cliente (o del balanceador) |
| `client.host` | IP del host HTTP de la petición entrante |
| `client.port` | Puerto de origen |
| `client.scheme` | `http` o `https` |
| `client.ssl.enabled` | `true` si hay TLS |
| `client.cn` / `client.country` / `client.locality` / `client.state` / `client.organization` / `client.organization.unit` / `client.email.address` | Campos del certificado TLS del cliente (mTLS) |
| `client.received.start.timestamp` / `.end.timestamp` | Recepción de la petición (ms epoch) |
| `client.sent.start.timestamp` / `.end.timestamp` | Envío de la respuesta (ms epoch) |

**Latencia total** = `client.sent.end.timestamp - client.received.start.timestamp`.
**Overhead de Apigee** = latencia total − latencia del backend.

---

## `error.*` y `fault.*` — solo en error flow

| Variable | Descripción |
|---|---|
| `fault.name` | Código del error de runtime, específico de la política. **Es el que usas en las condiciones de FaultRule.** |
| `error.content` | Contenido del error |
| `error.message` | Mensaje asociado (solo lectura) |
| `error.status.code` | Código HTTP del error |
| `error.reason.phrase` | Frase de razón (p. ej. `Bad Request`) |
| `error.state` | Estado del flujo donde ocurrió el error |
| `error.transport.message` | Objeto TransportMessage |
| `error.header.NOMBRE` | Cabecera de la respuesta de error (R/W) |
| `is.error` | Boolean: hay error activo |

Además, cada política deja `<espacio_de_nombres>.<nombre_politica>.failed`:

| Política | Variable de fallo |
|---|---|
| `VerifyAPIKey`, `OAuthV2` | `oauthV2.NOMBRE.failed` |
| `Quota`, `SpikeArrest` | `ratelimit.NOMBRE.failed` |
| `VerifyJWT`, `GenerateJWT` | `jwt.NOMBRE.failed` |
| `ServiceCallout` | `servicecallout.NOMBRE.failed` |

---

## `ratelimit.*` — contadores de Quota y SpikeArrest

Sustituye `NOMBRE` por el nombre de la política:

| Variable | Descripción |
|---|---|
| `ratelimit.NOMBRE.allowed.count` | Cuota permitida |
| `ratelimit.NOMBRE.used.count` | Consumida en el intervalo |
| `ratelimit.NOMBRE.available.count` | Restante |
| `ratelimit.NOMBRE.exceed.count` | Exceso en el intervalo actual |
| `ratelimit.NOMBRE.total.exceed.count` | Exceso acumulado |
| `ratelimit.NOMBRE.expiry.time` | Milisegundos UTC en que se reinicia la cuota |
| `ratelimit.NOMBRE.identifier` | Identificador del cliente |
| `ratelimit.NOMBRE.class.*` | Equivalentes a nivel de clase de cuota |
| `ratelimit.NOMBRE.failed` | Boolean de fallo |

Uso típico — devolver cabeceras estándar de rate limit:

```xml
<AssignMessage name="AM-CabecerasRateLimit">
    <Set>
        <Headers>
            <Header name="X-RateLimit-Limit">{ratelimit.Q-Cuota.allowed.count}</Header>
            <Header name="X-RateLimit-Remaining">{ratelimit.Q-Cuota.available.count}</Header>
            <Header name="X-RateLimit-Reset">{ratelimit.Q-Cuota.expiry.time}</Header>
        </Headers>
    </Set>
    <IgnoreUnresolvedVariables>true</IgnoreUnresolvedVariables>
    <AssignTo createNew="false" transport="http" type="response"/>
</AssignMessage>
```

---

## `system.*` — contexto del runtime

| Variable | Descripción |
|---|---|
| `system.timestamp` | Entero de 64 bits: momento de lectura (ms epoch) |
| `system.time` | Cadena de tiempo (p. ej. `Wed, 21 Aug 2013 19:16:47 UTC`) |
| `system.time.year` / `.month` / `.day` / `.dayofweek` / `.hour` / `.minute` / `.second` / `.millisecond` / `.zone` | Componentes de la fecha |
| `system.uuid` | UUID del Message Processor |
| `system.pod.name` | Nombre del pod |
| `system.region.name` | Región del centro de datos |
| `system.interface.NOMBRE` | IP del sistema |

---

## Otros prefijos

| Variable | Descripción |
|---|---|
| `apiproxy.name` | Nombre del proxy |
| `apiproxy.revision` | Número de revisión |
| `organization.name` | Nombre de la organización |
| `environment.name` | Nombre del entorno |
| `current.flow.name` | Nombre del flujo en ejecución |
| `current.flow.description` | Descripción del flujo |
| `messageid` | ID único global de la petición (incluye el hostname del router) |
| `route.name` | Nombre de la RouteRule ejecutada |
| `route.target` | Nombre del TargetEndpoint ejecutado |
| `loadbalancing.targetserver` | TargetServer invocado |
| `loadbalancing.failedservers` | TargetServers fallidos |
| `loadbalancing.isfallback` | Boolean: se usó el fallback |
| `servicecallout.NOMBRE.target.url` | URL del target del ServiceCallout |
| `servicecallout.requesturi` | URI sin protocolo ni dominio |
| `virtualhost.name` / `.aliases.values` / `.ssl.enabled` | ⚠️ Solo Edge |
| `router.uuid` | Obsoleto, devuelve null |

## Variables de contexto de producto (tras VerifyAPIKey / OAuthV2)

Estas las puebla la política de autenticación y son la base de la autorización:

| Variable | Descripción |
|---|---|
| `apiproduct.name` | Nombre del API product que autorizó la llamada |
| `apiproduct.developer.quota.limit` | Límite de cuota definido en el producto |
| `apiproduct.developer.quota.interval` | Intervalo de cuota |
| `apiproduct.developer.quota.timeunit` | Unidad de tiempo de la cuota |
| `developer.id` | ID interno del desarrollador. **No es estable**: no lo uses como identificador de Quota, clave de KVM ni identidad hacia el backend ([VerifyAPIKey](../02-politicas/referencia/verify-api-key.md#variables-de-flujo)) |
| `developer.email` | Email del desarrollador |
| `developer.app.name` | Nombre de la app |
| `client_id` | Consumer key de la app |
| `app.name` | Nombre de la app |

---

## Trabajar con variables

### Referenciar en XML — message templating

Se usan llaves: `{nombre.de.variable}`.

```xml
<Header name="X-Request-Id">{messageid}</Header>
<Payload contentType="application/json">{"producto":"{apiproduct.name}","ts":{system.timestamp}}</Payload>
```

### Referenciar como `ref`

```xml
<APIKey ref="request.header.x-api-key"/>
```

### Crear y leer desde JavaScript

```javascript
// Leer
var verbo = context.getVariable('request.verb');
var apiKey = context.getVariable('request.header.x-api-key');

// Escribir
context.setVariable('mi.variable.custom', 'valor');

// Eliminar
context.removeVariable('mi.variable.custom');

// El objeto message funciona en cualquier contexto
var payload = context.getVariable('message.content');
```

### Crear con AssignMessage

```xml
<AssignMessage name="AM-CrearVariables">
    <AssignVariable>
        <Name>peticion.canal</Name>
        <Ref>request.header.x-canal</Ref>
        <Value>web</Value>   <!-- valor por defecto si Ref no resuelve -->
    </AssignVariable>
    <IgnoreUnresolvedVariables>true</IgnoreUnresolvedVariables>
</AssignMessage>
```

## Notas finales

- Los **timestamps** son milisegundos desde el 1 de enero de 1970 UTC.
- Los índices de cabeceras y parámetros son **base 1** (`.1`, `.2`), no base 0.
- La mayoría de variables son de solo lectura; la tabla marca las escribibles.
- Usa siempre `<IgnoreUnresolvedVariables>true</IgnoreUnresolvedVariables>` cuando una variable pueda no existir, o la política fallará.

## Fuentes

- <https://docs.apigee.com/api-platform/reference/variables-reference>
- <https://cloud.google.com/apigee/docs/api-platform/fundamentals/message-variables>
- <https://cloud.google.com/apigee/docs/api-platform/fundamentals/introduction-flow-variables>
