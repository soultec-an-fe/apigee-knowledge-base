---
id: proxies-flujos
titulo: Flujos y pipeline de ejecución
area: proxies
tags: [preflow, postflow, conditional-flow, postclientflow, pipeline, orden-ejecucion]
aplica_a: [apigee-x, apigee-hybrid]
fuente: https://cloud.google.com/apigee/docs/api-platform/fundamentals/what-are-flows
revisado: 2026-08-20
---

# Flujos y pipeline de ejecución

El orden de ejecución es la parte de Apigee que más errores sutiles genera. Este documento lo fija con precisión.

## Los cuatro tipos de flujo

| Flujo | Cuándo se ejecuta | Condicional |
|---|---|---|
| **PreFlow** | Siempre, **antes** de los Conditional Flows | No |
| **Conditional Flows** (`<Flows>`) | Solo el **primero** cuya `<Condition>` sea verdadera | Sí |
| **PostFlow** | Siempre, **después** de los Conditional Flows | No |
| **PostClientFlow** | Después de enviar la respuesta al cliente | No |

> [!IMPORTANT]
> De todos los `<Flow>` dentro de `<Flows>`, **solo se ejecuta uno**: el primero que empareje. No es una cadena, es un `switch`. Un `<Flow>` sin `<Condition>` empareja siempre, por lo que sirve de catch-all — y por eso **debe ir el último**.

## Orden completo de ejecución

```
                        ── REQUEST ──►

  ┌─ ProxyEndpoint ──────────────────────────────────┐
  │  1.  PreFlow.Request                             │
  │  2.  Flows.Request      (solo el primero que empareje)
  │  3.  PostFlow.Request                            │
  └──────────────────────────────────────────────────┘
                          │
                    RouteRule  (arriba → abajo, gana la primera verdadera)
                          │
  ┌─ TargetEndpoint ─────────────────────────────────┐
  │  4.  PreFlow.Request                             │
  │  5.  Flows.Request                               │
  │  6.  PostFlow.Request                            │
  └──────────────────────────────────────────────────┘
                          │
                    ►  BACKEND  ◄
                          │
  ┌─ TargetEndpoint ─────────────────────────────────┐
  │  7.  PreFlow.Response                            │
  │  8.  Flows.Response                              │
  │  9.  PostFlow.Response                           │
  └──────────────────────────────────────────────────┘
                          │
  ┌─ ProxyEndpoint ──────────────────────────────────┐
  │ 10.  PreFlow.Response                            │
  │ 11.  Flows.Response                              │
  │ 12.  PostFlow.Response                           │
  └──────────────────────────────────────────────────┘
                          │
                ►  RESPUESTA AL CLIENTE  ◄
                          │
  ┌─ PostClientFlow ─────────────────────────────────┐
  │ 13.  MessageLogging / DataCapture únicamente     │
  └──────────────────────────────────────────────────┘

                        ◄── RESPONSE ──
```

Regla nemotécnica: **la petición va de fuera hacia dentro, la respuesta de dentro hacia fuera**. El ProxyEndpoint es la capa externa, el TargetEndpoint la interna.

## Dónde colocar cada cosa

| Necesidad | Ubicación correcta | Por qué |
|---|---|---|
| Autenticación (`VerifyAPIKey`, `OAuthV2`, `VerifyJWT`) | ProxyEndpoint → PreFlow → Request | Rechazar lo antes posible, antes de gastar recursos |
| `SpikeArrest` | ProxyEndpoint → PreFlow → Request, **después** de la auth | Proteger el runtime con el identificador ya resuelto |
| `Quota` | ProxyEndpoint → PreFlow → Request, después de auth | Necesita el contexto del API product |
| Threat protection (`JSONThreatProtection`) | ProxyEndpoint → PreFlow → Request | Antes de parsear el payload |
| `LookupCache` / `ResponseCache` (lookup) | ProxyEndpoint → PreFlow → **Request** | Lo más cerca posible del cliente, para cortocircuitar |
| Validación de negocio por operación | Conditional Flow → Request | Aísla la lógica por endpoint |
| Añadir credenciales del backend | TargetEndpoint → PreFlow → Request | El más cercano al backend; no se filtra si hay caché |
| Transformación de la respuesta | TargetEndpoint → Response o ProxyEndpoint → Response | Según si debe cachearse ya transformada |
| `PopulateCache` / `ResponseCache` (populate) | ProxyEndpoint → **PostFlow** → Response | Después de toda la mediación, cachea el resultado final |
| Quitar cabeceras internas del backend | ProxyEndpoint → PostFlow → Response | Último punto antes de salir |
| Logging y analítica | **PostClientFlow** | No añade latencia percibida por el cliente |

## PostClientFlow

Único flujo que se ejecuta **después** de que el cliente ya recibió la respuesta.

```xml
<PostClientFlow>
    <Request/>
    <Response>
        <Step><Name>ML-LogCloudLogging</Name></Step>
        <Step><Name>DC-CapturarMetricas</Name></Step>
    </Response>
</PostClientFlow>
```

Restricciones:

- **Solo admite `MessageLogging` y `DataCapture`.** Cualquier otra política se ignora o falla el despliegue.
- Se ejecuta **también cuando hubo error**, lo que lo hace ideal para auditoría completa.
- Como el cliente ya recibió la respuesta, **no puede modificarla**.
- Las variables `client.sent.end.timestamp` y la latencia total solo están completas aquí.

## Cortocircuitar el pipeline

Tres formas de terminar antes de llegar al backend:

### 1. RaiseFault
Entra en error flow inmediatamente.

```xml
<RaiseFault name="RF-Prohibido">
    <IgnoreUnresolvedVariables>true</IgnoreUnresolvedVariables>
    <FaultResponse>
        <Set>
            <StatusCode>403</StatusCode>
            <ReasonPhrase>Forbidden</ReasonPhrase>
            <Payload contentType="application/json">{"error":"canal_no_permitido"}</Payload>
        </Set>
    </FaultResponse>
</RaiseFault>
```

### 2. ResponseCache con acierto
Si `LookupCache` acierta, Apigee **salta el resto del request pipeline y el backend** y devuelve la respuesta cacheada.

### 3. RouteRule sin TargetEndpoint
La petición nunca sale del proxy. Se responde con `AssignMessage`.

```xml
<RouteRule name="health">
    <Condition>(proxy.pathsuffix MatchesPath "/health")</Condition>
</RouteRule>
```

## El error flow

Cuando ocurre un error, el pipeline normal **se abandona**:

```
Error en cualquier punto
   │
   ├─► ¿Hay <FaultRules> que emparejen?  →  ejecutar sus Steps
   ├─► ¿Hay <DefaultFaultRule>?          →  ejecutar sus Steps
   └─► Si no: mensaje de error por defecto de Apigee
   │
   └─► PostClientFlow (sí se ejecuta)
```

En el error flow **`request` y `response` quedan fuera de alcance**. Usa `message.*` en su lugar. Detalle en [manejo de errores](../05-operacion/01-manejo-de-errores.md).

## Buenas prácticas de estructura

> Múltiples `<Flow>` cada uno con **una** condición es preferible a múltiples `<Step>` con condición colgando del mismo PreFlow.

**Mal** — todo en el PreFlow con condiciones:

```xml
<PreFlow name="PreFlow">
    <Request>
        <Step>
            <Name>EV-ExtraerId</Name>
            <Condition>(request.verb = "GET") and (proxy.pathsuffix MatchesPath "/pedidos/*")</Condition>
        </Step>
        <Step>
            <Name>JTP-Proteger</Name>
            <Condition>(request.verb = "POST")</Condition>
        </Step>
        <Step>
            <Name>EV-ExtraerBody</Name>
            <Condition>(request.verb = "POST")</Condition>
        </Step>
    </Request>
</PreFlow>
```

**Bien** — un flujo por operación:

```xml
<PreFlow name="PreFlow">
    <Request>
        <Step><Name>VAK-VerificarApiKey</Name></Step>
    </Request>
</PreFlow>

<Flows>
    <Flow name="ObtenerPedido">
        <Condition>(request.verb = "GET") and (proxy.pathsuffix MatchesPath "/pedidos/*")</Condition>
        <Request><Step><Name>EV-ExtraerId</Name></Step></Request>
    </Flow>
    <Flow name="CrearPedido">
        <Condition>(request.verb = "POST") and (proxy.pathsuffix MatchesPath "/pedidos")</Condition>
        <Request>
            <Step><Name>JTP-Proteger</Name></Step>
            <Step><Name>EV-ExtraerBody</Name></Step>
        </Request>
    </Flow>
    <Flow name="NoSoportado">
        <Request><Step><Name>RF-405</Name></Step></Request>
    </Flow>
</Flows>
```

Ventajas: legible en Trace, cada operación tiene su nombre en analytics, y añadir una operación no toca las existentes.

## Límites

- **200 flows por proxy** (contando ProxyEndpoint y TargetEndpoint).
- **10 ProxyEndpoints por proxy** (recomendado: 1).
- **1.000 TargetEndpoints por proxy**.

## Fuentes

- <https://cloud.google.com/apigee/docs/api-platform/fundamentals/what-are-flows>
- <https://docs.apigee.com/api-platform/fundamentals/best-practices-api-proxy-design-and-development>
- <https://cloud.google.com/apigee/docs/api-platform/reference/limits>
