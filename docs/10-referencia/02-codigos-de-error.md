---
id: referencia-codigos-error
titulo: Códigos de error
area: referencia
tags: [errores, fault-name, troubleshooting, diagnostico, codigos]
aplica_a: [apigee-x, apigee-hybrid]
fuente: https://cloud.google.com/apigee/docs/api-platform/fundamentals/fault-handling
revisado: 2026-08-20
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

| `fault.name` | Causa | HTTP sugerido |
|---|---|---|
| `FailedToResolveAPIKey` | La variable de `<APIKey ref>` no existe: no se envió la key | 401 |
| `InvalidApiKey` | La key no existe | 401 |
| `InvalidApiKeyForGivenResource` | La key existe, pero ningún producto cubre esta operación | 403 |
| `DeveloperStatusNotActive` | Developer inactivo | 403 |
| `ApplicationNotApproved` | App revocada | 403 |
| `keymanagement.service.CompanyStatusNotActive` | Empresa / AppGroup inactivo | 403 |
| `invalid_access_token` | Token OAuth inválido | 401 |
| `access_token_expired` | Token OAuth expirado | 401 |
| `invalid_request` | Petición OAuth malformada | 400 |
| `insufficient_scope` | El token no tiene el scope requerido | 403 |
| `invalid_client` | Credenciales de cliente inválidas | 401 |
| `unsupported_grant_type` | Grant type no soportado | 400 |

## JWT y JWS

| `fault.name` | Causa | HTTP sugerido |
|---|---|---|
| `TokenExpired` | Claim `exp` en el pasado | 401 |
| `InvalidToken` | Firma inválida o token malformado | 401 |
| `IssuerMismatch` | El `iss` no coincide con `<Issuer>` | 401 |
| `AudienceMismatch` | El `aud` no coincide con `<Audience>` | 401 |
| `AlgorithmMismatch` | El `alg` del token no coincide con `<Algorithm>` | 401 |
| `NoMatchingPublicKey` | El `kid` del token no existe en el JWKS | 401 |
| `KeyIdMissing` | El token no lleva `kid` y el JWKS tiene varias claves | 401 |
| `InvalidJsonFormat` | El payload no es JSON válido tras decodificar | 400 |
| `TokenNotYetValid` | Claim `nbf` en el futuro | 401 |

## Cuota y rate limiting

| `fault.name` | Causa | HTTP sugerido |
|---|---|---|
| `QuotaViolation` | Cuota superada | 429 |
| `SpikeArrestViolation` | Pico de tráfico frenado | 429 |
| `InvalidQuotaInterval` | Intervalo fuera del rango permitido | 500 (config) |
| `InvalidQuotaTimeUnit` | Unidad de tiempo no válida | 500 (config) |
| `FailedToResolveQuotaIntervalReference` | La variable de `<Interval ref>` no resuelve | 500 (config) |
| `ConcurrentRatelimtViolation` | Límite de conexiones concurrentes superado | 429 |

## Threat protection y validación

| `fault.name` | Causa | HTTP sugerido |
|---|---|---|
| `ExecutionFailed` (JSONThreatProtection) | El JSON excede algún límite configurado | 400 |
| `SourceUnavailable` | La variable de `<Source>` no existe | 500 |
| `NonMessageVariable` | `<Source>` apunta a algo que no es un mensaje | 500 |
| `ThreatDetected` (RegularExpressionProtection) | El patrón malicioso emparejó | 400 |
| `Failed` (OASValidation) | La petición no cumple la spec OpenAPI | 400 |

## Backend y transporte

| `fault.name` | Causa | HTTP sugerido |
|---|---|---|
| `ErrorResponseCode` | El backend devolvió un código fuera de `success.codes` | 502 |
| `messaging.adaptors.http.flow.GatewayTimeout` | Timeout esperando al backend | 504 |
| `messaging.adaptors.http.flow.ServiceUnavailable` | Backend no disponible | 503 |
| `protocol.http.TooBigBody` | El payload supera el límite (30 MB buffered / 10 MB streamed) | 413 |
| `protocol.http.TooBigHeaders` | Cabeceras superan 60 KB | 431 |
| `messaging.adaptors.http.flow.NoActiveTargets` | Todos los TargetServers están marcados como no saludables | 503 |
| `messaging.adaptors.http.flow.SslHandshakeFailed` | Fallo de handshake TLS con el backend | 502 |

## Callouts y código personalizado

| `fault.name` | Causa | HTTP sugerido |
|---|---|---|
| `steps.servicecallout.ExecutionFailed` | El ServiceCallout falló | 502 |
| `steps.servicecallout.RequestVariableNotMessage` | La variable de `<Request>` no es un mensaje | 500 |
| `ExecutionFailed` (Javascript) | Excepción no capturada en el JS, o timeout | 500 |
| `ScriptExecutionFailed` | Fallo en el script | 500 |
| `ExecutionFailed` (JavaCallout) | El callout devolvió `ExecutionResult.ABORT` o lanzó excepción | 500 |

## Enrutamiento y flujo

| `fault.name` | Causa | HTTP sugerido |
|---|---|---|
| `RaiseFault` | Lanzado por una política `RaiseFault` | El que definas |
| `messaging.runtime.RouteFailed` | Ninguna RouteRule emparejó y no hay ruta por defecto | 500 |
| `NoRoutesMatched` | Sin RouteRule aplicable | 404 |

## Caché y KVM

| `fault.name` | Causa | HTTP sugerido |
|---|---|---|
| `InvalidCacheResourceReference` | El `<CacheResource>` no existe en el entorno | 500 |
| `CacheNotFound` | Recurso de caché inexistente | 500 |
| `SetVariableFailed` | No se pudo asignar el valor recuperado | 500 |
| `InvalidIndex` | Índice fuera de rango en `KeyValueMapOperations` | 500 |

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
                or (fault.name = "insufficient_scope")
                or (fault.name = "ApplicationNotApproved")
                or (fault.name = "DeveloperStatusNotActive")</Condition>
    </FaultRule>

    <FaultRule name="errores-limite">
        <Step><Name>AM-Error429</Name></Step>
        <Condition>(fault.name = "QuotaViolation")
                or (fault.name = "SpikeArrestViolation")
                or (fault.name = "ConcurrentRatelimtViolation")</Condition>
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
| **502 intermitente** | `MaxFailures` con un solo TargetServer y sin HealthMonitor |
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
