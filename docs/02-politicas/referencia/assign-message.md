---
id: politica-assign-message
titulo: AssignMessage — referencia completa
area: politicas
tags: [assignmessage, mediacion, cabeceras, payload, variables, message-template, google-auth, extensible]
aplica_a: [apigee-x, apigee-hybrid, apigee-edge]
elemento_xml: AssignMessage
tipo_politica: extensible
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/assign-message-policy
fuente_edge: https://docs.apigee.com/api-platform/reference/policies/assign-message-policy
revisado: 2026-10-22
---

# AssignMessage — referencia completa

> [!NOTE]
> **Tipo:** Extensible. **Elemento raíz:** `<AssignMessage>`.
> **Aplica a:** Apigee X, hybrid y Edge. `<Set>/<Authentication>`, `<AssignVariable>/<PropertySetRef>` y `<AssignVariable>/<ResourceURL>` son solo de X/hybrid; `<ReasonPhrase>` solo aparece en la documentación de Edge.

AssignMessage es la navaja suiza de la mediación: **modifica** la petición o la respuesta (cabeceras, parámetros, cuerpo, código de estado, verbo, ruta), **crea** mensajes nuevos (por ejemplo, la petición de un ServiceCallout) y **asigna variables** de flujo. Visión de conjunto y recetas en [Mediación](../03-mediacion.md) y [Recetas XML](../06-recetas-xml.md).

> [!IMPORTANT]
> Las operaciones se ejecutan **en el orden en que aparecen** en el XML. Para "quitar todas las cabeceras y poner solo una", `<Remove>` tiene que ir antes que `<Set>`.

## Sintaxis completa

```xml
<AssignMessage name="AM-Nombre" continueOnError="false" enabled="true">
  <DisplayName>Nombre legible</DisplayName>
  <AssignTo createNew="false" transport="http" type="request"/>
  <Remove>
    <Headers>
      <Header name="x-interna"/>
    </Headers>
    <QueryParams>
      <QueryParam name="apikey"/>
    </QueryParams>
  </Remove>
  <Copy source="request">
    <Headers>
      <Header name="x-correlation-id"/>
    </Headers>
  </Copy>
  <Add>
    <Headers>
      <Header name="x-gateway">apigee</Header>
    </Headers>
  </Add>
  <Set>
    <Headers>
      <Header name="Content-Type">application/json</Header>
    </Headers>
    <Payload contentType="application/json">{"id":"{flujo.id}"}</Payload>
    <Verb>POST</Verb>
    <Path>/v2/recursos</Path>
  </Set>
  <AssignVariable>
    <Name>flujo.pais</Name>
    <Ref>request.queryparam.pais</Ref>
    <Value>CO</Value>
  </AssignVariable>
  <IgnoreUnresolvedVariables>false</IgnoreUnresolvedVariables>
</AssignMessage>
```

## Atributos del elemento raíz

| Atributo | Obligatorio | Default | Qué hace |
|---|---|---|---|
| `name` | Sí | — | Nombre interno; da nombre a `assignmessage.{name}.failed`. |
| `continueOnError` | No | `false` | Con `true`, ignora **todos** los errores de la política (a diferencia de `<IgnoreUnresolvedVariables>`, que solo afecta a variables). |
| `enabled` | No | `true` | Con `false` no se ejecuta. |
| `async` | No | `false` | **Obsoleto.** |

## Elementos hijos

| Elemento | Qué hace |
|---|---|
| `<AssignTo>` | Sobre qué mensaje actúa (petición, respuesta o un mensaje nuevo). |
| `<Add>` | Añade cabeceras, query params o form params **nuevos** (si ya existen, añade un valor más). |
| `<Set>` | **Sobrescribe** (o crea) cabeceras, parámetros, cuerpo, ruta, verbo, versión, código de estado; genera tokens de Google. |
| `<Copy source>` | Copia partes de otro mensaje al de destino. |
| `<Remove>` | Elimina cabeceras, parámetros o el cuerpo. `<Remove/>` vacío lo elimina **todo**. |
| `<AssignVariable>` | Asigna un valor a una variable de flujo (la crea si no existe). Puede haber varios. |
| `<IgnoreUnresolvedVariables>` | Default `false`: una variable sin resolver produce error. Con `true`, se toma como vacía. |

### `<AssignTo>`: sobre qué mensaje actuar

| Configuración | Mensaje afectado |
|---|---|
| Omitido o sin texto | `request` si la política está en el flujo de petición; `response` si está en el de respuesta. |
| `<AssignTo createNew="true" type="request"/>` | **Sustituye** la petición actual por una nueva vacía. Todo lo que tenía se pierde. |
| `<AssignTo createNew="true" type="request">miPeticion</AssignTo>` | Crea un mensaje nuevo llamado `miPeticion`, sin tocar la petición actual. Típico para un ServiceCallout. |
| `<AssignTo createNew="false">miPeticion</AssignTo>` | Usa `miPeticion` si existe y es un mensaje; si no, **error**. |
| Texto con nombre y sin `createNew` | Usa el mensaje si existe; si no existe, **lo crea** con el `type` indicado. |

`type` (`request` o `response`; por defecto según el flujo) solo importa al crear. `transport` solo admite `http`.

> [!CAUTION]
> `createNew="true"` **sin nombre** borra la petición o respuesta en curso. Es un error frecuente al copiar ejemplos: si lo que quieres es una petición para un ServiceCallout, ponle siempre nombre.

### `<Add>` y `<Set>`

| | `<Add>` | `<Set>` |
|---|---|---|
| Cabecera o parámetro que **no** existe | Lo crea | Lo crea |
| Que **ya** existe | Añade otro valor (cabeceras multivalor) | **Lo sustituye** |
| `<Payload>`, `<Path>`, `<Verb>`, `<Version>`, `<StatusCode>` | — | Sí |

Todos los hijos admiten **plantillas de mensaje** (`{variable}`, funciones como `{escapeJSON(...)}`). `<Headers/>`, `<QueryParams/>` o `<FormParams/>` vacíos no hacen nada.

Restricciones de cada parte:

| Parte | Mensaje | Verbos | Efecto secundario |
|---|---|---|---|
| `<QueryParams>` | Solo petición | `GET`, `POST`, `PATCH`, `DELETE` (en `<Set>` también `PUT`) | — |
| `<FormParams>` | Solo petición | `POST` (con cuerpo, aunque sea vacío, o `Content-Length`) | Pone `Content-Type: application/x-www-form-urlencoded` |
| `<StatusCode>` | Solo respuesta | — | Admite plantilla |
| `<Verb>`, `<Version>`, `<Path>` | Solo petición | — | Admiten plantilla |

#### `<Set>/<Payload>`

Define el cuerpo; su contenido es una **plantilla de mensaje**. Atributos:

| Atributo | Qué hace |
|---|---|
| `contentType` | Fija también la cabecera `Content-Type`. |
| `variablePrefix`, `variableSuffix` | Delimitadores de variables distintos de `{` y `}` (sintaxis antigua, anterior a la versión 16.08.17 de Edge; sigue funcionando). |

> [!WARNING]
> No incluyas el prólogo XML (`<?xml …?>`) dentro de `<Payload>`: da errores de validación. Y escapa los valores que insertes en un JSON con `{escapeJSON(variable)}`, o un valor con comillas romperá el documento (o inyectará campos).

#### `<Set>/<Path>` y `target.url`

`<Path>` cambia la ruta de la petición. Para cambiar **la URL de destino completa**, no uses `<Path>`: asigna la variable `target.url` con `<AssignVariable>` en una política adjunta al **TargetEndpoint** (en el ProxyEndpoint no funciona, porque la variable se inicializa en el TargetEndpoint).

#### `<Set>/<Authentication>` (solo X/hybrid)

Genera un **token de Google** y lo pone en `Authorization` (o en la cabecera de `<HeaderName>`), para llamar a servicios de Google o a Cloud Run / Cloud Functions. Requiere desplegar el proxy con una cuenta de servicio.

| Hijo | Uso |
|---|---|
| `<GoogleAccessToken><Scopes><Scope>…</Scope></Scopes></GoogleAccessToken>` | Access token OAuth 2.0 de Google (APIs de Google: Logging, Secret Manager…). |
| `<GoogleIDToken><Audience ref useTargetUrl>…</Audience></GoogleIDToken>` | ID token OIDC (Cloud Run, Cloud Functions, servicios propios con IAP). Con `useTargetUrl="true"` y audiencia vacía, se usa la URL del target sin query. |
| `<HeaderName>` | Cabecera donde va el token. El `Authorization` original, si existía, se mantiene. |

> [!NOTE]
> La sintaxis general de la página tiene errores tipográficos (`<GoogleIDToken>` cerrado como `</GoogleAccessToken>`, `<Audience>` cerrado como `</Scope>`) y presenta `<Audience>` como hijo de `<GoogleAccessToken>`. La estructura correcta es `<GoogleIDToken><Audience>…</Audience></GoogleIDToken>`.

#### `<ReasonPhrase>` (Edge)

La documentación de Edge incluye `<Set>/<ReasonPhrase>` y `<Copy>/<ReasonPhrase>`; la de X **no los menciona**. Con HTTP/2 la frase de estado no existe. En proxies de X/hybrid, omítelo.

### `<Copy source>`

Copia del mensaje `source` (por defecto `message`, o sea la petición o respuesta en curso) al de `<AssignTo>`. Sin hijos, copia **todo**. Hijos: `<Headers>` (vacío = todas), `<QueryParams>`, `<FormParams>`, `<Path>`, `<Payload>`, `<StatusCode>`, `<Verb>`, `<Version>` (los cinco últimos con `true`/`false`).

- Si `source` no resuelve o no es un mensaje, `<Copy>` **no hace nada** (sin error); si es una variable que no es de tipo mensaje, error `VariableOfNonMsgType`.
- Si `source` es el mismo mensaje que el destino, no hace nada.
- `<FormParams>`: ambos mensajes petición, `POST` o `PUT`, y el origen con `Content-Type: application/x-www-form-urlencoded`.
- `<StatusCode>`: ambos respuesta. `<Path>`, `<Verb>`, `<Version>`: ambos petición.
- Para cabeceras o parámetros con **varios valores**: `<Header name="h3">2</Header>` copia el segundo valor (índices desde 1; `0` o negativo → `InvalidIndex` al desplegar).

### `<Remove>`

Elimina del mensaje de `<AssignTo>`: `<Headers>` (vacío = todas), `<QueryParams>` (vacío = todos; solo petición), `<FormParams>` (vacío = todos; solo petición form-urlencoded), `<Payload>true</Payload>`. `<Remove/>` sin hijos lo borra **todo**. Mismo sistema de índices para valores repetidos.

Uso típico: quitar la API key, el `Authorization` del cliente o cabeceras internas antes de llamar al backend.

### `<AssignVariable>`

| Hijo | Valor que asigna |
|---|---|
| `<Name>` | **Obligatorio.** Variable de destino (vacía → `InvalidVariableName`). El nombre `ratelimit` está reservado. |
| `<Value>` | Literal. **Nunca** interpreta `{}`. |
| `<Ref>` | Valor de otra variable (sin llaves). |
| `<Template>` o `<Template ref>` | Plantilla de mensaje, o variable que contiene una plantilla. Con `ref` y texto, si la variable es nula se usa el texto. |
| `<PropertySetRef>` (X/hybrid) | Valor de un PropertySet elegido dinámicamente: `{nombre_set}.{clave}`, sin el prefijo `propertyset.`. |
| `<ResourceURL>` (X/hybrid) | Contenido de un recurso del proxy (XSD, XSL, WSDL, JavaScript, PropertySet, OpenAPI), p. ej. `oas://spec.yaml`. |

**Precedencia** si hay varios: `ResourceURL` > `Template` > `Ref` > `Value` > `PropertySetRef`. `<Value>` actúa como **valor por defecto** de `<Ref>`: si la variable no existe, no se puede leer o es nula, se asigna `<Value>`.

Patrón clásico de valor por defecto para un parámetro:

```xml
<AssignVariable>
  <Name>request.queryparam.w</Name>
  <Ref>request.queryparam.w</Ref>
  <Value>12797282</Value>
</AssignVariable>
```

> [!TIP]
> Para desactivar que el sufijo de ruta del proxy se añada a la URL del target, asigna `false` a `target.copy.pathsuffix` en el flujo de petición del TargetEndpoint.

## Variables de flujo

No publica variables de éxito; las variables que asignes quedan disponibles para el resto del flujo.

## Errores

### En runtime

| Código | HTTP | Causa |
|---|---|---|
| `steps.assignmessage.SetVariableFailed` | 500 | No se pudo asignar una variable (el `faultstring` dice cuál). |
| `steps.assignmessage.VariableOfNonMsgType` | 500 | `<Copy source>` apunta a una variable que no es un mensaje. |
| `steps.assignmessage.UnresolvedVariable` | 500 | Una variable no existe o está fuera de alcance (con `<IgnoreUnresolvedVariables>false`). |

### Al desplegar

| Error | Causa |
|---|---|
| `InvalidIndex` | Índice `0` o negativo en `<Copy>` o `<Remove>`. |
| `InvalidVariableName` | `<AssignVariable>/<Name>` vacío o ausente. |
| `InvalidPayload` | `<Payload>` inválido. |

### Variables de fallo

| Variable | Ejemplo |
|---|---|
| `fault.name` | `fault.name = "UnresolvedVariable"` |
| `assignmessage.{name}.failed` | `assignmessage.AM-Respuesta.failed = true` |

## Ejemplos

### 1. Limpiar la petición antes del backend

```xml
<AssignMessage name="AM-Limpiar-Peticion">
  <Remove>
    <Headers>
      <Header name="Authorization"/>
      <Header name="x-apikey"/>
    </Headers>
    <QueryParams>
      <QueryParam name="apikey"/>
    </QueryParams>
  </Remove>
  <Set>
    <Headers>
      <Header name="x-cliente-id">{client_id}</Header>
      <Header name="x-request-id">{messageid}</Header>
    </Headers>
  </Set>
</AssignMessage>
```

### 2. Respuesta de error con JSON seguro

```xml
<AssignMessage name="AM-Error-400">
  <Set>
    <StatusCode>400</StatusCode>
    <Payload contentType="application/json">{"codigo":"PETICION_INVALIDA","detalle":"{escapeJSON(flujo.detalle)}","traza":"{messageid}"}</Payload>
  </Set>
  <IgnoreUnresolvedVariables>true</IgnoreUnresolvedVariables>
  <AssignTo createNew="false" transport="http" type="response"/>
</AssignMessage>
```

### 3. Petición nueva para un ServiceCallout

```xml
<AssignMessage name="AM-Peticion-Riesgo">
  <AssignTo createNew="true" transport="http" type="request">peticionRiesgo</AssignTo>
  <Set>
    <Verb>POST</Verb>
    <Headers>
      <Header name="Content-Type">application/json</Header>
    </Headers>
    <Payload contentType="application/json">{"cliente":"{escapeJSON(flujo.cliente_id)}","monto":{flujo.monto}}</Payload>
  </Set>
</AssignMessage>
```

Después, `<ServiceCallout><Request variable="peticionRiesgo"/>…</ServiceCallout>`.

### 4. Llamar a Cloud Run con un ID token de Google (X/hybrid)

```xml
<AssignMessage name="AM-Token-Cloud-Run">
  <Set>
    <Authentication>
      <GoogleIDToken>
        <Audience useTargetUrl="true"/>
      </GoogleIDToken>
    </Authentication>
  </Set>
</AssignMessage>
```

### 5. Cambiar el destino según una variable (en el TargetEndpoint)

```xml
<AssignMessage name="AM-Destino-Por-Region">
  <AssignVariable>
    <Name>target.url</Name>
    <Template>https://{flujo.region}.backend.ejemplo.com{proxy.pathsuffix}</Template>
  </AssignVariable>
</AssignMessage>
```

> [!WARNING]
> Si `flujo.region` sale de la petición, valídala contra una lista cerrada antes: una URL de destino construida con datos del cliente es una vía de SSRF.

## Diferencias en Apigee Edge

| Aspecto | Apigee X / hybrid | Apigee Edge |
|---|---|---|
| `<Set>/<Authentication>` (tokens de Google) | Sí | No |
| `<AssignVariable>/<PropertySetRef>`, `<ResourceURL>` | Sí | No |
| `<ReasonPhrase>` en `<Set>` y `<Copy>` | No documentado | Sí |
| Resto de elementos y errores | Iguales | Iguales |

## Antipatrones

- `createNew="true"` sin nombre cuando querías un mensaje auxiliar.
- Insertar variables en JSON sin `escapeJSON`.
- Construir `target.url` con datos del cliente sin validar.
- Un único AssignMessage gigante que hace de todo: dificulta el Debug; separa limpieza, enriquecimiento y respuesta.
- `<IgnoreUnresolvedVariables>true</IgnoreUnresolvedVariables>` en todas partes, que oculta errores reales.

## Fuentes

- AssignMessage policy — Apigee X/hybrid: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/assign-message-policy> (consultada directamente, contenido completo, 2026-10-22).
- Assign Message policy — Apigee Edge: <https://docs.apigee.com/api-platform/reference/policies/assign-message-policy> (consultada directamente, 2026-10-22).
