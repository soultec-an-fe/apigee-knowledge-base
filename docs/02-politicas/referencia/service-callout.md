---
id: politica-service-callout
titulo: ServiceCallout — referencia completa
area: politicas
tags: [servicecallout, callout, http, mashup, localtargetconnection, google-auth, extensible]
aplica_a: [apigee-x, apigee-hybrid, apigee-edge]
elemento_xml: ServiceCallout
tipo_politica: extensible
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/service-callout-policy
fuente_edge: https://docs.apigee.com/api-platform/reference/policies/service-callout-policy
revisado: 2026-10-22
---

# ServiceCallout — referencia completa

> [!NOTE]
> **Tipo:** Extensible. **Elemento raíz:** `<ServiceCallout>`.
> **Aplica a:** Apigee X, hybrid y Edge. `<Authentication>` (tokens de Google) es solo de X y hybrid ≥ 1.6.

ServiceCallout hace una **llamada HTTP/HTTPS adicional** desde el flujo del proxy, distinta de la llamada al target: a un servicio externo (enriquecer la respuesta, validar algo, obtener un token) o a **otro proxy** de la misma organización y entorno. Solo llama a servicios HTTP.

Composición habitual:

1. [AssignMessage](assign-message.md) construye la petición (o se define dentro de la propia ServiceCallout).
2. **ServiceCallout** la envía y guarda la respuesta en una variable.
3. [ExtractVariables](extract-variables.md) o JavaScript leen la respuesta (las cabeceras ya están disponibles como variables).

> [!NOTE]
> En hybrid ≥ 1.14 con la funcionalidad *Enhanced per-environment proxy limits*, hay que poner `enhanceProxyLimits: true` en `overrides.yaml` para poder usar ServiceCallout.

## Sintaxis completa

```xml
<ServiceCallout name="SC-Nombre" continueOnError="false" enabled="true">
  <DisplayName>Nombre legible</DisplayName>
  <Request clearPayload="true" variable="peticionRiesgo">
    <IgnoreUnresolvedVariables>false</IgnoreUnresolvedVariables>
    <Set>
      <Verb>POST</Verb>
      <Headers>
        <Header name="Content-Type">application/json</Header>
      </Headers>
      <Payload contentType="application/json">{"cliente":"{escapeJSON(flujo.cliente_id)}"}</Payload>
    </Set>
  </Request>
  <Response>respuestaRiesgo</Response>
  <Timeout>3000</Timeout>
  <HTTPTargetConnection>
    <URL>https://riesgo.interno.ejemplo.com/v1/evaluar</URL>
    <SSLInfo>
      <Enabled>true</Enabled>
      <TrustStore>ref://ts-interno</TrustStore>
    </SSLInfo>
    <Properties>
      <Property name="success.codes">2xx</Property>
    </Properties>
  </HTTPTargetConnection>
</ServiceCallout>
```

## Atributos del elemento raíz

| Atributo | Obligatorio | Default | Qué hace |
|---|---|---|---|
| `name` | Sí | — | Nombre interno; da nombre a `servicecallout.{name}.*`. |
| `continueOnError` | No | `false` | Con `true`, un fallo de la llamada no corta el flujo; compruébalo con `servicecallout.{name}.failed`. |
| `enabled` | No | `true` | Con `false` no se ejecuta. |
| `async` | No | `false` | **Obsoleto.** |

## Elementos hijos

| Elemento | Obligatorio | Default | Resumen |
|---|---|---|---|
| `<Request variable clearPayload>` | No | `variable` = `servicecallout.request`, `clearPayload` = `true` | Petición a enviar: una variable creada antes o definida aquí con `<Remove>`, `<Copy>`, `<Add>`, `<Set>` (misma sintaxis que AssignMessage). |
| `<Request>/<IgnoreUnresolvedVariables>` | No | — | Ignorar variables sin resolver al construir la petición. |
| `<Response>` | No | — | Variable donde guardar la respuesta. **Sin `<Response>`, no se espera respuesta** (*fire-and-forget*). |
| `<Timeout>` | No | 55000 ms | Espera máxima, en milisegundos. No se puede fijar dinámicamente. Cero o negativo → `InvalidTimeoutValue`. |
| `<HTTPTargetConnection>` | Uno de los dos | — | Destino HTTP: `<URL>`, `<SSLInfo>`, `<Properties>`, `<LoadBalancer>`, `<Authentication>`. |
| `<LocalTargetConnection>` | Uno de los dos | — | Otro proxy del mismo entorno: `<APIProxy>` + `<ProxyEndpoint>`, o `<Path>`. |

Sin ninguna de las dos conexiones → `ConnectionInfoMissing`; `<URL>` vacía → `URLMissing`.

### `<Request clearPayload>` y enmascaramiento

`clearPayload="true"` (default) crea un objeto de petición nuevo en cada ejecución y libera la memoria tras enviarlo. Ponlo en `false` solo si necesitas la petición después.

> [!IMPORTANT]
> Si no das nombre a la petición, se llama `servicecallout.request`. Para ocultar sus cabeceras sensibles en Debug, la máscara de datos debe incluir ese nombre, por ejemplo `servicecallout.request.header.Authorization`.

### `<Response>`: esperar o no

| Configuración | Comportamiento |
|---|---|
| Con `<Response>miVariable</Response>` | Se espera a leer la respuesta completa; si la llamada falla, error. |
| Sin `<Response>` | El flujo **sigue sin esperar**; no hay forma de saber si la llamada falló. Uso típico: enviar logs o eventos a un sistema externo. |

Para registrar eventos sin afectar a la latencia, considera también [MessageLogging](message-logging.md) en el PostClientFlow.

### `<Timeout>`

El default de 55 s es demasiado largo para casi cualquier llamada auxiliar: un servicio lento bloquea el hilo y el cliente espera. Ajusta `<Timeout>` a la latencia real del servicio (p. ej. 1-3 s) y decide qué hacer al expirar (fallo → `500` y flujo de error).

### Errores HTTP del servicio llamado

Por defecto, una respuesta `4xx` o `5xx` del servicio hace **fallar** la política (`ExecutionFailed`). Para tratar esos códigos tú mismo, amplía los códigos de éxito con la propiedad `success.codes` en `<HTTPTargetConnection>/<Properties>` (ver [success.codes](../../01-proxies/05-target-endpoints-y-servidores.md#successcodes)), o usa `continueOnError="true"` y revisa el código de estado de la respuesta.

### `<HTTPTargetConnection>`

| Hijo | Uso |
|---|---|
| `<URL>` | Admite plantillas. El **protocolo** (`https://`) no puede venir de una variable. Si la variable incluye host y puerto, usa una variable para host:puerto y otra para el resto de la ruta. |
| `<SSLInfo>` | TLS hacia el servicio. Referencia keystores y truststores como `ref://nombre` (recomendado frente al nombre directo). |
| `<Properties>` | Propiedades de transporte HTTP (timeouts de conexión, `success.codes`…). |
| `<LoadBalancer>` | Reparte entre TargetServers, igual que en un TargetEndpoint. |
| `<Authentication>` (X, hybrid ≥ 1.6) | Tokens de Google; ver abajo. |

> [!CAUTION]
> Construir la `<URL>` con datos que controla el cliente abre la puerta a **SSRF** (llamadas a servicios internos). Valida esos datos contra una lista cerrada.

### `<Authentication>`: tokens de Google

| Hijo | Uso |
|---|---|
| `<GoogleAccessToken><Scopes><Scope>…</Scope></Scopes><LifetimeInSeconds>3600</LifetimeInSeconds></GoogleAccessToken>` | APIs de Google (Secret Manager, Logging…). `LifetimeInSeconds` default 3600. |
| `<GoogleIDToken><Audience ref useTargetUrl>…</Audience><IncludeEmail>…</IncludeEmail></GoogleIDToken>` | Cloud Run, Cloud Functions, servicios con IAP. `useTargetUrl` (hybrid ≥ 1.8) usa la URL del target como audiencia; `IncludeEmail` añade `email` y `email_verified`. |
| `<HeaderName>` | Otra cabecera para el token (p. ej. `X-Serverless-Authorization` de Cloud Run); el `Authorization` original se mantiene. |

Requiere desplegar el proxy con una cuenta de servicio y, en hybrid, el rol `roles/iam.serviceAccountTokenCreator` sobre la cuenta `apigee-runtime`.

### `<LocalTargetConnection>`

Llama a otro proxy **sin salir de Apigee** (sin red ni TLS). Se indica `<APIProxy>` + `<ProxyEndpoint>`, o un `<Path>` cuando no conoces o no quieres depender del nombre del proxy. El proxy llamado ejecuta todas sus políticas (autenticación incluida). Ver [tipos de conexión alternativos](../../01-proxies/05-target-endpoints-y-servidores.md#tipos-de-conexión-alternativos).

## Variables de flujo

| Variable | Contenido |
|---|---|
| `{respuesta}.content`, `{respuesta}.header.{h}`, `{respuesta}.status.code` | Cuerpo, cabeceras y código de la respuesta (con el nombre de `<Response>`). |
| `{peticion}.header.{h}` | Cabeceras de la petición enviada. |
| `servicecallout.requesturi` | URI llamada, sin protocolo ni dominio. |
| `servicecallout.{name}.target.url` | URL llamada. |
| `servicecallout.{name}.expectedcn` | Common Name esperado del certificado (con TLS). |
| `servicecallout.{name}.failed` | `true` si falló. |

## Errores

### En runtime

| Código | HTTP | Causa |
|---|---|---|
| `steps.servicecallout.ExecutionFailed` | 500 | Entrada inválida, o el servicio respondió `4xx`/`5xx` (por defecto), o timeout. |
| `steps.servicecallout.RequestVariableNotMessageType` | 500 | La variable de `<Request>` no es un mensaje. |
| `steps.servicecallout.RequestVariableNotRequestMessageType` | 500 | La variable de `<Request>` es una respuesta. |
| `googletoken.EmptyIDTokenAudience` | 500 | `<GoogleIDToken>` sin audiencia y sin `useTargetUrl`. |
| `messaging.adaptors.http.filter.GoogleTokenGenerationFailure` | 500 | No se pudo generar el token de Google (cuenta de servicio inexistente o deshabilitada, API IAMCredentials deshabilitada, scopes inválidos…). |

### Al desplegar

`URLMissing`, `ConnectionInfoMissing`, `InvalidTimeoutValue`, y con `<Authentication>`: `FAILED_PRECONDITION` (falta la cuenta de servicio) y `PERMISSION_DENIED` (la cuenta no existe, es de otro proyecto o el que despliega no tiene `iam.serviceAccounts.actAs`).

### Variables de fallo

`fault.name` y `servicecallout.{name}.failed`.

## Ejemplos

### 1. Enriquecer con un servicio interno y timeout corto

```xml
<ServiceCallout name="SC-Perfil-Riesgo" continueOnError="true">
  <Request variable="peticionRiesgo"/>
  <Response>respuestaRiesgo</Response>
  <Timeout>2000</Timeout>
  <HTTPTargetConnection>
    <URL>https://riesgo.interno.ejemplo.com/v1/perfil</URL>
  </HTTPTargetConnection>
</ServiceCallout>
```

```xml
<Step>
  <Name>AM-Riesgo-Por-Defecto</Name>
  <Condition>servicecallout.SC-Perfil-Riesgo.failed = true</Condition>
</Step>
```

Si el servicio de riesgo no responde, se sigue con un valor por defecto prudente en vez de fallar la petición del cliente.

### 2. Leer un secreto de Secret Manager (X/hybrid)

```xml
<ServiceCallout name="SC-Secret-Manager">
  <Request>
    <Set>
      <Verb>GET</Verb>
    </Set>
  </Request>
  <Response>respuestaSecreto</Response>
  <HTTPTargetConnection>
    <Authentication>
      <GoogleAccessToken>
        <Scopes>
          <Scope>https://www.googleapis.com/auth/cloud-platform</Scope>
        </Scopes>
      </GoogleAccessToken>
    </Authentication>
    <URL>https://secretmanager.googleapis.com/v1/projects/mi-proyecto/secrets/clave-socio/versions/latest:access</URL>
  </HTTPTargetConnection>
</ServiceCallout>
```

Cachea el resultado con [PopulateCache](populate-cache.md) para no llamar en cada petición.

### 3. Llamar a otro proxy (proxy chaining)

```xml
<ServiceCallout name="SC-Proxy-Clientes">
  <Request variable="peticionClientes"/>
  <Response>respuestaClientes</Response>
  <LocalTargetConnection>
    <APIProxy>clientes-interno</APIProxy>
    <ProxyEndpoint>default</ProxyEndpoint>
  </LocalTargetConnection>
</ServiceCallout>
```

## Diferencias en Apigee Edge

| Aspecto | Apigee X / hybrid | Apigee Edge |
|---|---|---|
| `<Authentication>` (tokens de Google) | Sí | No |
| Timeout por defecto | 55 s | 55 s |
| `<LocalTargetConnection>`, `<LoadBalancer>` | Sí | Sí |

## Antipatrones

- Timeout por defecto (55 s) en llamadas auxiliares.
- Llamadas en cadena en cada petición sin caché.
- URL construida con datos del cliente.
- Omitir `<Response>` cuando el resultado importa.
- ServiceCallout a otro proxy por URL pública en vez de `<LocalTargetConnection>`.

## Fuentes

- ServiceCallout policy — Apigee X/hybrid: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/service-callout-policy> (consultada directamente, contenido completo, 2026-10-22).
- Service Callout policy — Apigee Edge: <https://docs.apigee.com/api-platform/reference/policies/service-callout-policy> (consultada directamente, 2026-10-22).
