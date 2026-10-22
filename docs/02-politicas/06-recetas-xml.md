---
id: politicas-recetas
titulo: Recetas XML listas para usar
area: politicas
tags: [recetas, snippets, ejemplos, xml, copiar-pegar]
aplica_a: [apigee-x, apigee-hybrid]
fuente: https://cloud.google.com/apigee/docs/api-platform/reference/policies/reference-overview-policy
revisado: 2026-08-20
---

# Recetas XML listas para usar

Fragmentos completos y válidos. Cada uno indica su archivo destino dentro del bundle y dónde adjuntarlo.

---

## 1. Proxy REST seguro — esqueleto mínimo de producción

### `apiproxy/proxies/default.xml`

```xml
<ProxyEndpoint name="default">
    <FaultRules>
        <FaultRule name="errores-auth">
            <Step><Name>AM-Error401</Name></Step>
            <Condition>(fault.name = "FailedToResolveAPIKey") or (fault.name = "InvalidApiKey") or (fault.name = "InvalidApiKeyForGivenResource")</Condition>
        </FaultRule>
        <FaultRule name="errores-cuota">
            <Step><Name>AM-Error429</Name></Step>
            <Condition>(fault.name = "QuotaViolation") or (fault.name = "SpikeArrestViolation")</Condition>
        </FaultRule>
    </FaultRules>
    <DefaultFaultRule name="fallback">
        <Step><Name>AM-Error500</Name></Step>
        <AlwaysEnforce>true</AlwaysEnforce>
    </DefaultFaultRule>

    <PreFlow name="PreFlow">
        <Request>
            <Step><Name>CORS-Permitir</Name></Step>
            <Step>
                <Name>VAK-VerificarApiKey</Name>
                <Condition>request.verb != "OPTIONS"</Condition>
            </Step>
            <Step>
                <Name>SA-FrenoDePicos</Name>
                <Condition>request.verb != "OPTIONS"</Condition>
            </Step>
            <Step>
                <Name>Q-CuotaProducto</Name>
                <Condition>request.verb != "OPTIONS"</Condition>
            </Step>
            <Step>
                <Name>JTP-ProtegerJson</Name>
                <Condition>(request.verb = "POST") or (request.verb = "PUT") or (request.verb = "PATCH")</Condition>
            </Step>
        </Request>
        <Response/>
    </PreFlow>

    <Flows>
        <Flow name="Health">
            <Condition>(proxy.pathsuffix MatchesPath "/health") and (request.verb = "GET")</Condition>
            <Request><Step><Name>AM-Health</Name></Step></Request>
            <Response/>
        </Flow>
        <Flow name="ListarRecursos">
            <Condition>(proxy.pathsuffix MatchesPath "/recursos") and (request.verb = "GET")</Condition>
        </Flow>
        <Flow name="ObtenerRecurso">
            <Condition>(proxy.pathsuffix MatchesPath "/recursos/*") and (request.verb = "GET")</Condition>
            <Request><Step><Name>EV-IdRuta</Name></Step></Request>
        </Flow>
        <Flow name="CrearRecurso">
            <Condition>(proxy.pathsuffix MatchesPath "/recursos") and (request.verb = "POST")</Condition>
            <Request><Step><Name>OAS-Validar</Name></Step></Request>
        </Flow>
        <Flow name="NoSoportado">
            <Request><Step><Name>RF-405</Name></Step></Request>
        </Flow>
    </Flows>

    <PostFlow name="PostFlow">
        <Request/>
        <Response>
            <Step><Name>AM-CabecerasRateLimit</Name></Step>
            <Step><Name>AM-LimpiarCabeceras</Name></Step>
        </Response>
    </PostFlow>

    <PostClientFlow>
        <Response><Step><Name>ML-Log</Name></Step></Response>
    </PostClientFlow>

    <HTTPProxyConnection>
        <BasePath>/recursos/v1</BasePath>
    </HTTPProxyConnection>

    <RouteRule name="sin-target">
        <Condition>(proxy.pathsuffix MatchesPath "/health")</Condition>
    </RouteRule>
    <RouteRule name="default">
        <TargetEndpoint>default</TargetEndpoint>
    </RouteRule>
</ProxyEndpoint>
```

---

## 2. Respuestas de error corporativas consistentes

### `policies/AM-Error401.xml`

```xml
<AssignMessage continueOnError="false" enabled="true" name="AM-Error401">
    <DisplayName>Error 401</DisplayName>
    <Set>
        <Headers>
            <Header name="Content-Type">application/json</Header>
            <Header name="X-Correlation-Id">{messageid}</Header>
        </Headers>
        <StatusCode>401</StatusCode>
        <Payload contentType="application/json">
{"error":{"codigo":"NO_AUTORIZADO","mensaje":"Credenciales ausentes o invalidas","correlation_id":"{messageid}","timestamp":"{system.time}"}}
        </Payload>
    </Set>
    <IgnoreUnresolvedVariables>true</IgnoreUnresolvedVariables>
    <AssignTo createNew="false" transport="http" type="response"/>
</AssignMessage>
```

### `policies/AM-Error429.xml`

```xml
<AssignMessage continueOnError="false" enabled="true" name="AM-Error429">
    <DisplayName>Error 429</DisplayName>
    <Set>
        <Headers>
            <Header name="Content-Type">application/json</Header>
            <Header name="Retry-After">60</Header>
            <Header name="X-Correlation-Id">{messageid}</Header>
        </Headers>
        <StatusCode>429</StatusCode>
        <Payload contentType="application/json">
{"error":{"codigo":"LIMITE_EXCEDIDO","mensaje":"Has superado el limite de peticiones permitido","correlation_id":"{messageid}"}}
        </Payload>
    </Set>
    <IgnoreUnresolvedVariables>true</IgnoreUnresolvedVariables>
    <AssignTo createNew="false" transport="http" type="response"/>
</AssignMessage>
```

### `policies/AM-Error500.xml` — nunca filtres detalles internos

```xml
<AssignMessage continueOnError="false" enabled="true" name="AM-Error500">
    <DisplayName>Error genérico</DisplayName>
    <Set>
        <Headers>
            <Header name="Content-Type">application/json</Header>
            <Header name="X-Correlation-Id">{messageid}</Header>
        </Headers>
        <StatusCode>500</StatusCode>
        <Payload contentType="application/json">
{"error":{"codigo":"ERROR_INTERNO","mensaje":"Se ha producido un error procesando la peticion","correlation_id":"{messageid}"}}
        </Payload>
    </Set>
    <!-- Elimina cualquier rastro del backend -->
    <Remove>
        <Headers>
            <Header name="Server"/>
            <Header name="X-Powered-By"/>
            <Header name="X-Backend-Error"/>
        </Headers>
    </Remove>
    <IgnoreUnresolvedVariables>true</IgnoreUnresolvedVariables>
    <AssignTo createNew="false" transport="http" type="response"/>
</AssignMessage>
```

> [!IMPORTANT]
> El `DefaultFaultRule` cumple un doble propósito según Google: dar información útil al desarrollador **y ofuscar las URLs y errores del backend**. Nunca devuelvas `{fault.name}` ni `{error.content}` crudos al cliente en producción: regístralos en `MessageLogging` y devuelve solo el `correlation_id`.

---

## 3. Correlación de trazas de punta a punta

### `policies/AM-Correlacion.xml` — ProxyEndpoint · PreFlow · Request

```xml
<AssignMessage continueOnError="false" enabled="true" name="AM-Correlacion">
    <DisplayName>Propagar correlation id</DisplayName>
    <AssignVariable>
        <Name>trace.correlation_id</Name>
        <Ref>request.header.x-correlation-id</Ref>
        <Value>{messageid}</Value>
    </AssignVariable>
    <Set>
        <Headers>
            <Header name="X-Correlation-Id">{trace.correlation_id}</Header>
        </Headers>
    </Set>
    <IgnoreUnresolvedVariables>true</IgnoreUnresolvedVariables>
    <AssignTo createNew="false" transport="http" type="request"/>
</AssignMessage>
```

Y en el PostFlow del response, devolverlo al cliente:

```xml
<AssignMessage continueOnError="false" enabled="true" name="AM-CorrelacionRespuesta">
    <Set>
        <Headers>
            <Header name="X-Correlation-Id">{trace.correlation_id}</Header>
        </Headers>
    </Set>
    <IgnoreUnresolvedVariables>true</IgnoreUnresolvedVariables>
    <AssignTo createNew="false" transport="http" type="response"/>
</AssignMessage>
```

---

## 4. Token del backend cacheado (patrón lookup-or-fetch)

### Flujo

```xml
<PreFlow name="PreFlow">
  <Request>
    <Step><Name>LC-TokenBackend</Name></Step>
    <Step>
      <Name>AM-PeticionToken</Name>
      <Condition>backend.token is null</Condition>
    </Step>
    <Step>
      <Name>SC-ObtenerToken</Name>
      <Condition>backend.token is null</Condition>
    </Step>
    <Step>
      <Name>EV-ExtraerToken</Name>
      <Condition>backend.token is null</Condition>
    </Step>
    <Step>
      <Name>PC-TokenBackend</Name>
      <Condition>backend.token is null</Condition>
    </Step>
    <Step><Name>AM-AplicarToken</Name></Step>
  </Request>
</PreFlow>
```

### `policies/LC-TokenBackend.xml`

```xml
<LookupCache continueOnError="false" enabled="true" name="LC-TokenBackend">
    <CacheKey>
        <Prefix>oauth-backend</Prefix>
        <KeyFragment>token</KeyFragment>
    </CacheKey>
    <CacheResource>cache-tokens</CacheResource>
    <Scope>Exclusive</Scope>
    <AssignTo>backend.token</AssignTo>
</LookupCache>
```

### `policies/AM-PeticionToken.xml`

```xml
<AssignMessage continueOnError="false" enabled="true" name="AM-PeticionToken">
    <Set>
        <Headers>
            <Header name="Content-Type">application/x-www-form-urlencoded</Header>
        </Headers>
        <Verb>POST</Verb>
        <Path>/oauth/token</Path>
        <FormParams>
            <FormParam name="grant_type">client_credentials</FormParam>
            <FormParam name="client_id">{private.backend_client_id}</FormParam>
            <FormParam name="client_secret">{private.backend_client_secret}</FormParam>
        </FormParams>
    </Set>
    <AssignTo createNew="true" transport="http" type="request">peticion.token</AssignTo>
    <IgnoreUnresolvedVariables>false</IgnoreUnresolvedVariables>
</AssignMessage>
```

### `policies/SC-ObtenerToken.xml`

```xml
<ServiceCallout continueOnError="false" enabled="true" name="SC-ObtenerToken">
    <Request clearPayload="false" variable="peticion.token"/>
    <Response>respuesta.token</Response>
    <Timeout>5000</Timeout>
    <HTTPTargetConnection>
        <LoadBalancer>
            <Server name="idp-backend"/>
        </LoadBalancer>
    </HTTPTargetConnection>
</ServiceCallout>
```

### `policies/EV-ExtraerToken.xml`

```xml
<ExtractVariables continueOnError="false" enabled="true" name="EV-ExtraerToken">
    <Source>respuesta.token</Source>
    <JSONPayload>
        <Variable name="token" type="string"><JSONPath>$.access_token</JSONPath></Variable>
        <Variable name="expira" type="integer"><JSONPath>$.expires_in</JSONPath></Variable>
    </JSONPayload>
    <VariablePrefix>backend</VariablePrefix>
    <IgnoreUnresolvedVariables>false</IgnoreUnresolvedVariables>
</ExtractVariables>
```

### `policies/PC-TokenBackend.xml`

```xml
<PopulateCache continueOnError="false" enabled="true" name="PC-TokenBackend">
    <CacheKey>
        <Prefix>oauth-backend</Prefix>
        <KeyFragment>token</KeyFragment>
    </CacheKey>
    <CacheResource>cache-tokens</CacheResource>
    <Scope>Exclusive</Scope>
    <ExpirySettings>
        <!-- 60 s de margen antes de la expiración real -->
        <TimeoutInSeconds>3540</TimeoutInSeconds>
    </ExpirySettings>
    <Source>backend.token</Source>
</PopulateCache>
```

### `policies/AM-AplicarToken.xml`

```xml
<AssignMessage continueOnError="false" enabled="true" name="AM-AplicarToken">
    <Set>
        <Headers>
            <Header name="Authorization">Bearer {backend.token}</Header>
        </Headers>
    </Set>
    <IgnoreUnresolvedVariables>false</IgnoreUnresolvedVariables>
    <AssignTo createNew="false" transport="http" type="request"/>
</AssignMessage>
```

---

## 5. Paginación normalizada

Traducir la paginación del backend a un formato estándar del cliente.

```xml
<ExtractVariables continueOnError="false" enabled="true" name="EV-Paginacion">
    <Source>request</Source>
    <QueryParam name="page"><Pattern>{pagina}</Pattern></QueryParam>
    <QueryParam name="size"><Pattern>{tamano}</Pattern></QueryParam>
    <VariablePrefix>pag</VariablePrefix>
    <IgnoreUnresolvedVariables>true</IgnoreUnresolvedVariables>
</ExtractVariables>
```

```xml
<AssignMessage continueOnError="false" enabled="true" name="AM-TraducirPaginacion">
    <AssignVariable>
        <Name>pag.pagina</Name>
        <Ref>pag.pagina</Ref>
        <Value>1</Value>
    </AssignVariable>
    <AssignVariable>
        <Name>pag.tamano</Name>
        <Ref>pag.tamano</Ref>
        <Value>20</Value>
    </AssignVariable>
    <Remove>
        <QueryParams>
            <QueryParam name="page"/>
            <QueryParam name="size"/>
        </QueryParams>
    </Remove>
    <Set>
        <QueryParams>
            <QueryParam name="offset">{pag.pagina}</QueryParam>
            <QueryParam name="limit">{pag.tamano}</QueryParam>
        </QueryParams>
    </Set>
    <IgnoreUnresolvedVariables>true</IgnoreUnresolvedVariables>
    <AssignTo createNew="false" transport="http" type="request"/>
</AssignMessage>
```

---

## 6. Enmascarar PII en la respuesta

```xml
<Javascript continueOnError="false" enabled="true" timeLimit="200" name="JS-EnmascararPii">
    <ResourceURL>jsc://enmascarar-pii.js</ResourceURL>
</Javascript>
```

`resources/jsc/enmascarar-pii.js`:

```javascript
try {
    var cuerpo = context.getVariable('response.content');
    if (!cuerpo) { throw new Error('Respuesta vacia'); }

    var datos = JSON.parse(cuerpo);

    function enmascararEmail(e) {
        if (typeof e !== 'string' || e.indexOf('@') < 0) { return e; }
        var partes = e.split('@');
        var usuario = partes[0];
        var visible = usuario.length > 2 ? usuario.substring(0, 2) : usuario.charAt(0);
        return visible + '***@' + partes[1];
    }

    function enmascararTarjeta(t) {
        if (typeof t !== 'string' || t.length < 4) { return t; }
        return '**** **** **** ' + t.slice(-4);
    }

    function recorrer(nodo) {
        if (nodo === null || typeof nodo !== 'object') { return; }
        Object.keys(nodo).forEach(function (clave) {
            var valor = nodo[clave];
            if (typeof valor === 'object') {
                recorrer(valor);
            } else if (clave === 'email') {
                nodo[clave] = enmascararEmail(valor);
            } else if (clave === 'tarjeta' || clave === 'card_number') {
                nodo[clave] = enmascararTarjeta(valor);
            }
        });
    }

    recorrer(datos);
    context.setVariable('response.content', JSON.stringify(datos));

} catch (e) {
    throw new Error('ERROR_ENMASCARADO: ' + e.message);
}
```

---

## 7. Feature flag por API product

Activar comportamiento según un atributo personalizado del producto, sin redesplegar.

```xml
<Step>
    <Name>JS-NuevoAlgoritmo</Name>
    <Condition>verifyapikey.VAK-VerificarApiKey.apiproduct.feature_v2 = "true"</Condition>
</Step>
<Step>
    <Name>JS-AlgoritmoLegacy</Name>
    <Condition>verifyapikey.VAK-VerificarApiKey.apiproduct.feature_v2 != "true"</Condition>
</Step>
```

Activar el flag para un cliente = editar el atributo del API product. Cero despliegues.

---

## 8. Enrutado canary por porcentaje

```xml
<Javascript continueOnError="false" enabled="true" timeLimit="100" name="JS-Canary">
    <ResourceURL>jsc://canary.js</ResourceURL>
    <Properties>
        <Property name="porcentaje">10</Property>
    </Properties>
</Javascript>
```

`resources/jsc/canary.js`:

```javascript
var porcentaje = parseInt(properties.porcentaje, 10) || 0;
var sorteo = Math.floor(Math.random() * 100);
context.setVariable('canary.activo', (sorteo < porcentaje) ? 'true' : 'false');
```

```xml
<RouteRule name="canary">
    <Condition>canary.activo = "true"</Condition>
    <TargetEndpoint>v2</TargetEndpoint>
</RouteRule>
<RouteRule name="default">
    <TargetEndpoint>v1</TargetEndpoint>
</RouteRule>
```

> [!TIP]
> Para canary **estable por cliente** (que el mismo cliente caiga siempre en la misma versión), sustituye `Math.random()` por un hash de `client_id`.

---

## 9. Mock completo sin backend

```xml
<AssignMessage continueOnError="false" enabled="true" name="AM-MockListado">
    <Set>
        <Headers>
            <Header name="Content-Type">application/json</Header>
            <Header name="X-Mock">true</Header>
        </Headers>
        <StatusCode>200</StatusCode>
        <Payload contentType="application/json">
{"datos":[{"id":"1","nombre":"Ejemplo A"},{"id":"2","nombre":"Ejemplo B"}],"total":2,"pagina":1}
        </Payload>
    </Set>
    <AssignTo createNew="true" transport="http" type="response"/>
    <IgnoreUnresolvedVariables>true</IgnoreUnresolvedVariables>
</AssignMessage>
```

Con una RouteRule sin `<TargetEndpoint>`, el proxy responde sin backend. Útil para desbloquear al equipo frontend antes de que exista el servicio.

---

## 10. Validar un JWT de un IdP externo

```xml
<ExtractVariables continueOnError="false" enabled="true" name="EV-Bearer">
    <Source>request</Source>
    <Header name="Authorization">
        <Pattern ignoreCase="true">Bearer {token}</Pattern>
    </Header>
    <VariablePrefix>auth</VariablePrefix>
    <IgnoreUnresolvedVariables>false</IgnoreUnresolvedVariables>
</ExtractVariables>
```

```xml
<VerifyJWT continueOnError="false" enabled="true" name="VJWT-IdP">
    <DisplayName>Verificar JWT del IdP</DisplayName>
    <Algorithm>RS256</Algorithm>
    <Source>auth.token</Source>
    <PublicKey>
        <JWKS uri="https://idp.example.com/.well-known/jwks.json"/>
    </PublicKey>
    <Issuer>https://idp.example.com/</Issuer>
    <Audience>https://api.empresa.com</Audience>
    <TimeAllowance>30s</TimeAllowance>
</VerifyJWT>
```

Autorización por scope, después de verificar:

```xml
<RaiseFault continueOnError="false" enabled="true" name="RF-ScopeInsuficiente">
    <IgnoreUnresolvedVariables>true</IgnoreUnresolvedVariables>
    <FaultResponse>
        <Set>
            <StatusCode>403</StatusCode>
            <Payload contentType="application/json">{"error":{"codigo":"SCOPE_INSUFICIENTE"}}</Payload>
        </Set>
    </FaultResponse>
</RaiseFault>
```

```xml
<Step>
    <Name>RF-ScopeInsuficiente</Name>
    <Condition>!(jwt.VJWT-IdP.claim.scope Like "*pedidos.write*")</Condition>
</Step>
```

## Fuentes

- <https://cloud.google.com/apigee/docs/api-platform/reference/policies/reference-overview-policy>
- <https://docs.apigee.com/api-platform/fundamentals/best-practices-api-proxy-design-and-development>
