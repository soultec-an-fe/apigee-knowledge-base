---
id: referencia-codigos-error
titulo: Códigos de error
area: referencia
tags: [errores, fault-name, troubleshooting, diagnostico, codigos]
aplica_a: [apigee-x, apigee-hybrid]
fuente: https://cloud.google.com/apigee/docs/api-platform/fundamentals/fault-handling
revisado: 2026-10-23
---

# Códigos de error

Referencia de `fault.name` para usar en las condiciones de `<FaultRule>`.

```xml
<Condition>(fault.name = "QuotaViolation")</Condition>
```

> [!NOTE]
> La lista completa y autoritativa de errores por política está en la sección **"Error reference"** de la página de referencia de cada política en la documentación oficial. Esta tabla recoge los más frecuentes.

---

## Autenticación y autorización

`fault.name` es la **última parte** del código de fallo: `oauth.v2.InvalidApiKey` da `fault.name = "InvalidApiKey"`. El código completo y su HTTP están en la referencia de cada política.

| `fault.name` | Política | Causa | HTTP de Apigee |
|---|---|---|---|
| `FailedToResolveAPIKey` | VerifyAPIKey | No llegó la key (la variable de `<APIKey ref>` no existe). **También** se lanza con keys `revoked` o `pending`. | 401 |
| `InvalidApiKey` | VerifyAPIKey | La key no existe | 401 |
| `InvalidApiKeyForGivenResource` | VerifyAPIKey | La key es válida, pero ningún producto aprobado cubre este proxy, recurso o entorno | 401 |
| `invalid_client-app_not_approved` | VerifyAPIKey | App revocada | 401 |
| `DeveloperStatusNotActive` | VerifyAPIKey | Desarrollador inactivo | 401 |
| `consumer_key_missing_api_product_association` | VerifyAPIKey (X/hybrid) | La credencial no tiene ningún producto | 400 |
| `CompanyStatusNotActive` | VerifyAPIKey (Edge) | *Company* inactiva | 401 |
| `access_token_expired` | OAuthV2 | Token vencido | 401 |
| `access_token_not_approved` | OAuthV2 | Token revocado | 401 |
| `InvalidAccessToken` | OAuthV2 | Falta `Bearer` en `Authorization` | 401 |
| `invalid_access_token` | OAuthV2 `VerifyAccessToken` | Token inexistente o inválido (con el prefijo `keymanagement.service.`) | 401 |
| `InvalidAPICallAsNoApiProductMatchFound` | OAuthV2 | El recurso no está en el producto del token | 401 |
| `InsufficientScope` | OAuthV2 | El token no tiene ninguno de los scopes exigidos | 403 |
| `invalid_client` / `InvalidClientIdentifier` | OAuthV2 | `client_id` inválido. El nombre depende de `<GenerateResponse>`: captura los dos. | 401 / 500 |
| `InvalidRequest` | OAuthV2 | Parámetros faltantes o incorrectos | 400 |
| `UnSupportedGrantType` | OAuthV2 | Grant type no listado en `<SupportedGrantTypes>` | 500 |

Detalle: [VerifyAPIKey](../02-politicas/referencia/verify-api-key.md#errores), [OAuthV2](../02-politicas/referencia/oauthv2.md#errores).

## JWT y JWS

| `fault.name` | Causa | HTTP de Apigee |
|---|---|---|
| `InvalidToken` | Firma inválida | 401 |
| `TokenExpired` | Vencido, fuera del `<TimeAllowance>` | 401 |
| `TokenNotYetValid` | `nbf` en el futuro | 401 |
| `JwtIssuerMismatch` / `JwtAudienceMismatch` / `JwtSubjectMismatch` | `iss`, `aud` o `sub` no coinciden con lo configurado | 401 |
| `AlgorithmMismatch` | El `alg` del token no está permitido | 401 |
| `KeyIdMissing` / `NoMatchingPublicKey` | Con JWKS: el token no trae `kid`, o el `kid` no está en el JWKS | 401 |
| `FailedToDecode` / `InvalidJsonFormat` | Token corrupto | 401 |

Lista completa por política: [VerifyJWT](../02-politicas/referencia/verify-jwt.md), [VerifyJWS](../02-politicas/referencia/verify-jws.md) y [conceptos JWT/JWS](../02-politicas/referencia/jwt-jws-conceptos.md).

## Cuota y rate limiting

| `fault.name` | Causa | HTTP |
|---|---|---|
| `QuotaViolation` | Cuota superada | La documentación se contradice entre 500 y 429; ver [Quota](../02-politicas/referencia/quota.md#errores) |
| `SpikeArrestViolation` | Pico frenado | 429 (ver [SpikeArrest](../02-politicas/referencia/spike-arrest.md)) |
| `InvalidQuotaInterval` / `InvalidQuotaTimeUnit` | Configuración de cuota no válida | Error de despliegue o 500 |
| `FailedToResolveQuotaIntervalReference` | La variable de `<Interval ref>` no resuelve | 500 |

## Threat protection y validación

| `fault.name` | Política | Causa | HTTP |
|---|---|---|---|
| `ExecutionFailed` | JSONThreatProtection | El JSON supera un límite configurado | 500 por defecto; ver [la referencia](../02-politicas/referencia/json-threat-protection.md) |
| `ThreatDetected` | RegularExpressionProtection | El patrón emparejó | Ver [la referencia](../02-politicas/referencia/regular-expression-protection.md) |
| `SourceUnavailable` / `NonMessageVariable` | Varias | `<Source>` no existe o no es un mensaje | 500 |
| `Failed` | OASValidation | La petición (400) o la respuesta (500) no cumple la especificación | 400 / 500 |

## Backend y transporte

Fuente: el [catálogo oficial de errores de runtime](https://docs.cloud.google.com/apigee/docs/api-platform/errorcatalog/mp-runtime-errorcatalog). La columna HTTP es lo que **devuelve Apigee**. Los *playbooks* de diagnóstico están en [troubleshooting](../14-troubleshooting/01-errores-de-runtime.md).

| Código de fallo | HTTP | Causa |
|---|---|---|
| `flow.APITimedOut` | 504 | Se superó `api.timeout` del proxy, o una política tardó demasiado |
| `messaging.adaptors.http.flow.GatewayTimeout` | 504 | El backend no respondió dentro de `io.timeout.millis` (default 55 s) |
| `messaging.adaptors.http.flow.ServiceUnavailable` | 503 | Fallo de conexión: timeout de conexión, DNS mal resuelto… (motivo `TARGET_CONNECT_TIMEOUT` y similares) |
| `messaging.adaptors.http.flow.NoActiveTargets` | 503 | Con TargetServers: ninguno disponible |
| `messaging.adaptors.http.flow.SslHandshakeFailed` | **503** | Truststore sin la cadena completa del backend, FQDN distinto o versión TLS rechazada (por ejemplo, el backend solo acepta 1.3 y el TargetServer no la declara) |
| `messaging.adaptors.http.flow.UnexpectedEOFAtTarget` | 502 | TargetServer sin TLS bien configurado, el backend cortó la conexión o keep-alive mal ajustado |
| `messaging.adaptors.http.flow.BadGateway` | 502 | Respuesta HTTP malformada del backend |
| `messaging.adaptors.http.flow.ErrorResponseCode` | Según el backend | El backend respondió con un código de error (el catálogo pone el ejemplo de un `500`) |
| `messaging.adaptors.http.flow.InternalServerError` | 500 | Excepción no controlada en el backend |
| `messaging.adaptors.http.flow.DecompressionFailureAtRequest` / `AtResponse` | 400 / 502 | El cuerpo no corresponde al `Content-Encoding` declarado |
| `messaging.adaptors.http.flow.LengthRequired` | 411 | POST o PUT del cliente sin `Content-Length`. **No se ve en Trace.** |
| `messaging.adaptors.http.flow.RequestTimeOut` | 408 | El cliente no envió el cuerpo a tiempo |
| `protocol.http.NoResolvedHost` | 503 | Host del target incorrecto o con caracteres no válidos (por ejemplo, espacios) |
| `protocol.http.TooBigBody` | 413 (petición) / 502 (respuesta) | Cuerpo por encima del límite (ver [límites](01-limites.md)) |
| `protocol.http.TooBigHeaders` | 431 (petición) / 502 (respuesta) | Cabeceras por encima del límite |
| `protocol.http.TooBigLine` | 414 (petición) / 502 (respuesta) | Línea de petición o de respuesta demasiado larga |
| `protocol.http.DuplicateHeader`, `EmptyHeaderName`, `HeaderWithInvalidChar`, `HeaderNameWithNonAsciiChar` | 400 (petición) / 502 (respuesta) | Cabeceras no válidas |
| `protocol.http.InvalidPath` | 400 | Ruta de la petición con caracteres no permitidos por la RFC 3986 |
| `protocol.http.BadPath` / `EmptyPath` | 500 | `target.url` con ruta que empieza por `?`, o vacía |
| `protocol.http.ResponseWithBody` | 502 | El backend respondió `204` o `205` con cuerpo |
| `protocol.http.Response405WithoutAllowHeader` | 502 | `405` del backend sin la cabecera `Allow` |
| `protocol.http.ProxyTunnelCreationFailed` | 503 | El proxy de salida no pudo crear el túnel hacia el backend |
| `security.util.KeyAliasNotFound` / `TrustStoreWithNoCertificates` | 500 | Alias inexistente en el keystore, o truststore vacío |

> [!NOTE]
> **Errores del catálogo oficial:**
> - Describe `ErrorResponseCode` solo para el caso del `500`.
> - En la variante de respuesta de `TooBigBody` (502) repite la causa de la de petición.

## Callouts y código personalizado

| `fault.name` | Política | Causa | HTTP |
|---|---|---|---|
| `ExecutionFailed` | ServiceCallout | Fallo de la llamada, **incluida una respuesta 4xx o 5xx** fuera de `success.codes` | 500 |
| `RequestVariableNotMessageType` / `RequestVariableNotRequestMessageType` | ServiceCallout | `<Request>` no es un mensaje de petición | 500 |
| `ScriptExecutionFailed` | JavaScript | Excepción en el script | 500 |
| `ScriptExecutionFailedLineNumber` / `ScriptSecurityError` | JavaScript | Error con número de línea, o acción prohibida por el *sandbox* | 500 |
| `ExecutionError` | JavaCallout | Excepción, o `null`, devuelto por el código Java | 500 |
| `ExecutionError` | ExternalCallout | Fallo de la llamada gRPC | 500 |
| `SharedFlowNotFound` | FlowCallout | Shared flow inexistente o no desplegado | 500 |

## Enrutamiento y flujo

| `fault.name` | Causa | HTTP |
|---|---|---|
| `RaiseFault` | Lanzado por [RaiseFault](../02-politicas/referencia/raise-fault.md) | El que definas |
| `RouteFailed` (`messaging.runtime.RouteFailed`) | Ninguna `<RouteRule>` emparejó y no hay ruta por defecto | 500 |

## Caché y KVM

| `fault.name` | Causa | HTTP |
|---|---|---|
| `InvalidCacheResourceReference` | El `<CacheResource>` no existe en el entorno | Despliegue o 500 |
| `CacheNotFound` | Recurso de caché inexistente | 500 |
| `SetVariableFailed` | No se pudo asignar el valor recuperado | 500 |
| `UnsupportedOperationException` | Operación no soportada en KeyValueMapOperations | 500 |

> [!NOTE]
> **Correcciones de 2026-10-23:** se verificó esta tabla contra las 69 referencias de política y el catálogo oficial de runtime.
> - `IssuerMismatch` y `AudienceMismatch` pasan a `JwtIssuerMismatch` y `JwtAudienceMismatch`.
> - `ApplicationNotApproved` pasa a `invalid_client-app_not_approved`.
> - `insufficient_scope` pasa a `InsufficientScope`.
> - `SslHandshakeFailed` devuelve **503**, no 502.
> - En JavaScript y JavaCallout, `ExecutionFailed` pasa a `ScriptExecutionFailed` y `ExecutionError`, respectivamente.
> - Se eliminan `NoRoutesMatched`, que no aparece en ninguna fuente oficial consultada, y `ConcurrentRatelimtViolation`, de una política retirada que nunca existió en X.

---

## Mapeo a FaultRules

Plantilla de agrupación por familia:

```xml
<FaultRules>
    <FaultRule name="errores-autenticacion">
        <Step><Name>AM-Error401</Name></Step>
        <Condition>(fault.name = "FailedToResolveAPIKey")
                or (fault.name = "InvalidApiKey")
                or (fault.name = "invalid_access_token")
                or (fault.name = "access_token_expired")
                or (fault.name = "TokenExpired")
                or (fault.name = "InvalidToken")</Condition>
    </FaultRule>

    <FaultRule name="errores-autorizacion">
        <Step><Name>AM-Error403</Name></Step>
        <Condition>(fault.name = "InvalidApiKeyForGivenResource")
                or (fault.name = "InsufficientScope")
                or (fault.name = "invalid_client-app_not_approved")
                or (fault.name = "DeveloperStatusNotActive")</Condition>
    </FaultRule>

    <FaultRule name="errores-limite">
        <Step><Name>AM-Error429</Name></Step>
        <Condition>(fault.name = "QuotaViolation")
                or (fault.name = "SpikeArrestViolation")</Condition>
    </FaultRule>

    <FaultRule name="errores-validacion">
        <Step><Name>AM-Error400</Name></Step>
        <Condition>(fault.name = "ThreatDetected")
                or (fault.name Matches "*ThreatProtection*")
                or (fault.name = "protocol.http.TooBigBody")</Condition>
    </FaultRule>

    <FaultRule name="errores-backend">
        <Step><Name>AM-Error502</Name></Step>
        <Condition>(fault.name = "ErrorResponseCode")
                or (fault.name Matches "*GatewayTimeout*")
                or (fault.name Matches "*ServiceUnavailable*")
                or (fault.name Matches "*NoActiveTargets*")</Condition>
    </FaultRule>
</FaultRules>

<DefaultFaultRule name="fallback">
    <Step><Name>ML-LogError</Name></Step>
    <Step><Name>AM-Error500</Name></Step>
    <AlwaysEnforce>true</AlwaysEnforce>
</DefaultFaultRule>
```

> [!IMPORTANT]
> Recuerda que en el **ProxyEndpoint** las FaultRules se evalúan **de abajo hacia arriba**, y en el **TargetEndpoint** de arriba hacia abajo. Ordena de lo más genérico (arriba) a lo más específico (abajo) en el ProxyEndpoint. Ver [manejo de errores](../05-operacion/01-manejo-de-errores.md).

---

## Diagnóstico rápido por síntoma

| Síntoma | Causas probables |
|---|---|
| **401 en todas las peticiones** | La cabecera de la key no coincide con `<APIKey ref>`; hay un flow hook con `VerifyAPIKey` que no conocías |
| **403 con una key válida** | El API product no incluye esa operación (verbo + ruta) o ese entorno |
| **404 inesperado** | Basepath mal escrito; hostname no declarado en el environment group; el proxy no está desplegado en ese entorno |
| **429 sin haber consumido la cuota** | `SpikeArrest` frenando por espaciado: `100ps` = 1 petición cada 10 ms |
| **502 intermitente** | `UnexpectedEOFAtTarget`: keep-alive de Apigee mayor o igual que el del backend; o `MaxFailures` con un solo TargetServer y sin HealthMonitor |
| **503 a los ~3 s** | `TARGET_CONNECT_TIMEOUT`: rutas no exportadas al peering, IPs NAT de Apigee no permitidas en el backend o agotamiento de puertos NAT |
| **504 constante** | `io.timeout.millis` menor que la latencia real del backend |
| **413 en payloads grandes** | Límite de 30 MB buffered / 10 MB streamed |
| **Una política "no hace nada"** | Streaming activo: la política perdió acceso al body |
| **La condición nunca dispara** | Ámbito de la variable, mayúsculas, o `proxy.pathsuffix` vs `request.path` |
| **500 sin explicación** | Excepción no capturada en `Javascript`; revisa el Trace |
| **Latencia alta y constante** | `Quota` síncrona, o KVM sin `<ExpiryTimeInSecs>` |
| **Latencia con picos esporádicos** | `ServiceCallout` sin `<Timeout>`, o regex con backtracking |
| **El despliegue falla sin motivo claro** | `name` de política no coincide con el nombre del archivo |

## Fuentes

- <https://cloud.google.com/apigee/docs/api-platform/fundamentals/fault-handling>
- <https://cloud.google.com/apigee/docs/api-platform/reference/policies/reference-overview-policy>
- <https://cloud.google.com/apigee/docs/api-platform/reference/limits>
- Runtime error catalog: <https://docs.cloud.google.com/apigee/docs/api-platform/errorcatalog/mp-runtime-errorcatalog> (consultada directamente, contenido completo, 2026-10-23).
