---
id: operacion-manejo-errores
titulo: Manejo de errores y FaultRules
area: operacion
tags: [faultrule, defaultfaultrule, raisefault, error-flow, continueonerror, fault-name]
aplica_a: [apigee-x, apigee-hybrid]
fuente: https://cloud.google.com/apigee/docs/api-platform/fundamentals/fault-handling
revisado: 2026-08-20
---

# Manejo de errores y FaultRules

## De dónde vienen los errores

1. **Errores automáticos de política** — `VerifyAPIKey` con key inválida, `Quota` superada, `VerifyJWT` con token expirado.
2. **Errores del flujo de mensajes** — fallos de enrutamiento, backend caído, timeout, petición malformada.
3. **Errores personalizados** — lanzados con `RaiseFault` para condiciones que ninguna política detecta.

## Qué pasa cuando ocurre un error

El proxy **abandona el pipeline normal** y entra en el error flow:

```
Error
  │
  ├─► ¿Alguna <FaultRule> tiene condición verdadera?  → ejecutar sus <Step>
  │
  ├─► ¿Hay <DefaultFaultRule>?                        → ejecutar sus <Step>
  │
  └─► Si no hay nada: mensaje de error por defecto de Apigee
  │
  └─► PostClientFlow  (sí se ejecuta: ideal para auditoría)
```

> [!IMPORTANT]
> **En el error flow, `request` y `response` quedan fuera de alcance.** Usa `message.*`, que es el único contenedor disponible en todos los contextos. Ver [variables de flujo](../01-proxies/04-variables-de-flujo.md).

## Estructura

```xml
<ProxyEndpoint name="default">
    <FaultRules>
        <FaultRule name="apikey-invalida">
            <Step><Name>AM-Error401</Name></Step>
            <Condition>(fault.name = "FailedToResolveAPIKey")</Condition>
        </FaultRule>
        <FaultRule name="cuota-superada">
            <Step><Name>AM-Error429</Name></Step>
            <Condition>(fault.name = "QuotaViolation")</Condition>
        </FaultRule>
    </FaultRules>

    <DefaultFaultRule name="fallback">
        <Step><Name>AM-Error500</Name></Step>
        <AlwaysEnforce>true</AlwaysEnforce>
    </DefaultFaultRule>
    ...
</ProxyEndpoint>
```

- La **condición "externa"** (la del `<FaultRule>`) decide si esa regla se ejecuta.
- Las **condiciones "internas"** (las de cada `<Step>`) solo se evalúan si la regla ya se activó.
- Dentro de una regla activada, los `<Step>` se ejecutan **en secuencia**.

## Orden de evaluación — el detalle que sorprende

> [!WARNING]
> **El orden de evaluación es distinto en ProxyEndpoint y en TargetEndpoint.**
>
> - **ProxyEndpoint**: Apigee empieza por la `<FaultRule>` de **abajo** del XML y sube.
> - **TargetEndpoint**: Apigee empieza por la de **arriba** y baja.

En ambos casos:

- **Solo se ejecuta la primera** `<FaultRule>` cuya condición sea verdadera. El resto se ignora.
- Si ninguna empareja, se ejecuta la `<DefaultFaultRule>`.
- Si una `<FaultRule>` se activa pero **ninguno de sus `<Step>` internos cumple su condición**, se devuelve el error por defecto de Apigee — y la `DefaultFaultRule` **no** se ejecuta, salvo que tenga `AlwaysEnforce`.

## AlwaysEnforce

```xml
<DefaultFaultRule name="fallback">
    <Step><Name>ML-LogError</Name></Step>
    <Step><Name>AM-Error500</Name></Step>
    <AlwaysEnforce>true</AlwaysEnforce>
</DefaultFaultRule>
```

Con `<AlwaysEnforce>true</AlwaysEnforce>`, la `DefaultFaultRule` **se ejecuta siempre**, incluso si otra `FaultRule` ya se ejecutó.

> [!TIP]
> Este es el mecanismo para garantizar que **todo** error se registra y que **ninguna** respuesta de error filtra detalles internos, sin importar qué regla específica se haya disparado. Úsalo prácticamente siempre.

## fault.name — el identificador del error

```xml
<Condition>(fault.name = "QuotaViolation")</Condition>
```

Aparece en el campo `errorcode` de los mensajes de error por defecto de Apigee. Es la forma canónica de discriminar errores.

### Nombres frecuentes

| `fault.name` | Origen | HTTP sugerido |
|---|---|---|
| `FailedToResolveAPIKey` | No se envió la API key | 401 |
| `InvalidApiKey` | Key inexistente | 401 |
| `InvalidApiKeyForGivenResource` | Key sin acceso a esa operación | 403 |
| `DeveloperStatusNotActive` | Developer inactivo | 403 |
| `ApplicationNotApproved` | App revocada | 403 |
| `QuotaViolation` | Cuota superada | 429 |
| `SpikeArrestViolation` | Pico de tráfico frenado | 429 |
| `invalid_access_token` | Token OAuth inválido | 401 |
| `access_token_expired` | Token OAuth expirado | 401 |
| `insufficient_scope` | Scope insuficiente | 403 |
| `TokenExpired` | JWT expirado | 401 |
| `InvalidToken` | Firma JWT inválida | 401 |
| `ExecutionFailed` | Fallo en JavaScript / JavaCallout | 500 |
| `ErrorResponseCode` | El backend devolvió un código de error | 502 |
| `RaiseFault` | Lanzado por una política `RaiseFault` | El que definas |
| `protocol.http.TooBigBody` | Payload supera el límite | 413 |
| `messaging.adaptors.http.flow.GatewayTimeout` | Timeout hacia el backend | 504 |
| `steps.servicecallout.ExecutionFailed` | Fallo en un ServiceCallout | 502 |

> [!NOTE]
> La lista completa de `fault.name` por política está en la documentación de referencia de cada política, sección "Error reference". Ver [códigos de error](../10-referencia/02-codigos-de-error.md).

## Variables `.failed` por política

Además de `fault.name`, cada política deja una variable de fallo:

```xml
<Condition>(oauthV2.VAK-VerificarApiKey.failed = "true")</Condition>
```

| Política | Espacio de nombres |
|---|---|
| `VerifyAPIKey`, `OAuthV2` | `oauthV2.<nombre>.failed` |
| `Quota`, `SpikeArrest` | `ratelimit.<nombre>.failed` |
| `VerifyJWT`, `GenerateJWT` | `jwt.<nombre>.failed` |
| `ServiceCallout` | `servicecallout.<nombre>.failed` |

## continueOnError — manejar el error sin salir del flujo

```xml
<VerifyAPIKey continueOnError="true" enabled="true" name="VAK-Opcional">
    <APIKey ref="request.queryparam.apikey"/>
</VerifyAPIKey>
```

Con `continueOnError="true"`, un fallo **no** entra en error flow. La política deja su variable `.failed = true` y el flujo continúa normalmente. Después puedes decidir qué hacer:

```xml
<Step>
    <Name>AM-ModoAnonimo</Name>
    <Condition>(oauthV2.VAK-Opcional.failed = "true")</Condition>
</Step>
<Step>
    <Name>AM-ModoAutenticado</Name>
    <Condition>(oauthV2.VAK-Opcional.failed != "true")</Condition>
</Step>
```

Casos de uso: autenticación opcional, degradación elegante, enriquecimiento no crítico, y **siempre en `MessageLogging`** (un fallo de logging nunca debe tumbar una petición).

## RaiseFault y su relación con FaultRules

- **`RaiseFault` *inicia*** el estado de error.
- **Las `FaultRules` *lo manejan*.**

Si ambos definen datos de respuesta:

1. El código de estado, la reason phrase y el payload de la **FaultRule tienen prioridad**.
2. Los valores del `RaiseFault` rellenan los huecos que la FaultRule no fije.
3. Las **cabeceras HTTP se acumulan** de ambas fuentes.

Detectar un error lanzado por `RaiseFault`:

```xml
<FaultRule name="fallo-personalizado">
    <Step><Name>AM-ErrorNegocio</Name></Step>
    <Condition>(fault.name = "RaiseFault")</Condition>
</FaultRule>
```

## Tratar códigos del backend como éxito

Por defecto un 4xx/5xx del backend entra en error flow. Para manejarlos en el flujo normal:

```xml
<HTTPTargetConnection>
    <Properties>
        <Property name="success.codes">1xx,2xx,3xx,400,500</Property>
    </Properties>
    <LoadBalancer><Server name="backend"/></LoadBalancer>
</HTTPTargetConnection>
```

Y luego traducirlos:

```xml
<Response>
    <Step>
        <Name>AM-TraducirErrorBackend</Name>
        <Condition>(response.status.code = 400) or (response.status.code = 500)</Condition>
    </Step>
</Response>
```

## Taxonomía de fallos

Apigee organiza los fallos en cuatro familias:

| Familia | Contenido |
|---|---|
| **Messaging** | Fallos personalizados, errores HTTP 4xx/5xx, fallos de enrutamiento y clasificación |
| **Transport** | Conectividad, validación, SSL/TLS, timeouts, errores de E/S |
| **System** | Memoria, hilos |
| **Policy** | Errores específicos de cada política |

## Buenas prácticas

1. **Da siempre una condición "externa"** a cada `<FaultRule>`. Sin ella, la regla se activa con cualquier error.
2. **Una FaultRule por escenario de error único.** No metas cinco `fault.name` distintos en una sola con `or`, salvo que la respuesta sea idéntica.
3. **Usa las condiciones internas de `<Step>`** para diferenciar dentro de una misma familia de errores.
4. **Coloca las FaultRules donde corresponde**: en el ProxyEndpoint las de cliente, en el TargetEndpoint las de backend.
5. **Registra en las FaultRules** con `MessageLogging`, y con `continueOnError="true"`.
6. **Ten siempre una `DefaultFaultRule` con `AlwaysEnforce`.** Google señala que cumple un doble propósito: informar al desarrollador **y ofuscar las URLs y errores del backend**.
7. **Nunca devuelvas `{fault.name}` ni `{error.content}` crudos al cliente.** Regístralos y devuelve solo un `correlation_id`.
8. **Considera el `PostClientFlow`**: solo `MessageLogging` se ejecuta ahí, después de enviar la respuesta de error. Es el sitio ideal para auditoría completa.
9. **Usa mensajes legibles que sugieran la solución**, no solo el código. `"Falta la cabecera X-Api-Key"` vale más que `"Unauthorized"`.
10. **Verifica con Trace** qué FaultRule se ejecuta y qué variables hay disponibles.

## Plantilla de manejo de errores

`policies/ML-LogError.xml` — registro estructurado del error:

```xml
<MessageLogging continueOnError="true" enabled="true" name="ML-LogError">
    <CloudLogging>
        <LogName>projects/{organization.name}/logs/apigee-errores</LogName>
        <Message contentType="application/json">
{
  "severity": "ERROR",
  "proxy": "{apiproxy.name}",
  "revision": "{apiproxy.revision}",
  "correlation_id": "{messageid}",
  "fault_name": "{fault.name}",
  "error_message": "{error.message}",
  "error_status": "{error.status.code}",
  "flow": "{current.flow.name}",
  "verbo": "{message.verb}",
  "ruta": "{proxy.pathsuffix}",
  "producto": "{apiproduct.name}",
  "developer": "{developer.email}",
  "target_host": "{target.host}"
}
        </Message>
    </CloudLogging>
</MessageLogging>
```

`ProxyEndpoint`:

```xml
<FaultRules>
    <FaultRule name="errores-autenticacion">
        <Step><Name>AM-Error401</Name></Step>
        <Condition>(fault.name = "FailedToResolveAPIKey") or (fault.name = "InvalidApiKey") or (fault.name = "invalid_access_token") or (fault.name = "TokenExpired")</Condition>
    </FaultRule>
    <FaultRule name="errores-autorizacion">
        <Step><Name>AM-Error403</Name></Step>
        <Condition>(fault.name = "InvalidApiKeyForGivenResource") or (fault.name = "insufficient_scope") or (fault.name = "ApplicationNotApproved")</Condition>
    </FaultRule>
    <FaultRule name="errores-limite">
        <Step><Name>AM-Error429</Name></Step>
        <Condition>(fault.name = "QuotaViolation") or (fault.name = "SpikeArrestViolation")</Condition>
    </FaultRule>
    <FaultRule name="errores-validacion">
        <Step><Name>AM-Error400</Name></Step>
        <Condition>(fault.name Matches "*ThreatProtection*") or (fault.name Matches "*OASValidation*")</Condition>
    </FaultRule>
</FaultRules>

<DefaultFaultRule name="fallback">
    <Step><Name>ML-LogError</Name></Step>
    <Step><Name>AM-Error500</Name></Step>
    <AlwaysEnforce>true</AlwaysEnforce>
</DefaultFaultRule>
```

> [!NOTE]
> Recuerda que en el **ProxyEndpoint** la evaluación va **de abajo hacia arriba**. Si dos reglas pudieran emparejar el mismo error, la que está más abajo en el XML gana. Ordena de lo más genérico (arriba) a lo más específico (abajo).

## Fuentes

- <https://cloud.google.com/apigee/docs/api-platform/fundamentals/fault-handling>
- <https://docs.apigee.com/api-platform/fundamentals/fault-handling>
- <https://docs.apigee.com/api-platform/fundamentals/best-practices-api-proxy-design-and-development>
