---
id: proxies-targets
titulo: TargetEndpoints, TargetServers y balanceo
area: proxies
tags: [targetendpoint, targetserver, loadbalancer, healthmonitor, timeout, ssl]
aplica_a: [apigee-x, apigee-hybrid]
fuente: https://cloud.google.com/apigee/docs/api-platform/deploy/load-balancing-across-backend-servers
revisado: 2026-08-20
---

# TargetEndpoints, TargetServers y balanceo

## Por qué no hardcodear la URL

```xml
<!-- MAL: acopla el proxy a un entorno concreto -->
<HTTPTargetConnection>
    <URL>https://pedidos-svc.prod.interno.example.com/api</URL>
</HTTPTargetConnection>
```

Con esto, promover de `dev` a `prod` obliga a **editar el bundle**, lo que rompe la trazabilidad: la revisión que probaste no es la que despliegas.

```xml
<!-- BIEN: el TargetServer se resuelve por entorno -->
<HTTPTargetConnection>
    <LoadBalancer>
        <Server name="pedidos-svc"/>
    </LoadBalancer>
    <Path>/api</Path>
</HTTPTargetConnection>
```

`pedidos-svc` se define **una vez por entorno**. El mismo bundle funciona en dev, test y prod sin cambios.

## TargetServer

Recurso con scope de **environment**. Hasta **8.000 por entorno**.

```json
{
  "name": "pedidos-svc",
  "host": "pedidos.interno.example.com",
  "port": 443,
  "isEnabled": true,
  "protocol": "HTTP",
  "sSLInfo": {
    "enabled": "true",
    "clientAuthEnabled": "false",
    "trustStore": "truststore-backends",
    "ignoreValidationErrors": "false"
  }
}
```

Creación:

```bash
apigeecli targetservers create \
  --name pedidos-svc \
  --host pedidos.interno.example.com \
  --port 443 --enable \
  --org "$ORG" --env prod \
  --token "$(gcloud auth print-access-token)"
```

## LoadBalancer

```xml
<HTTPTargetConnection>
    <LoadBalancer>
        <Algorithm>RoundRobin</Algorithm>
        <Server name="pedidos-svc-a"/>
        <Server name="pedidos-svc-b"/>
        <MaxFailures>5</MaxFailures>
        <ServerUnhealthyResponse>
            <ResponseCode>500</ResponseCode>
            <ResponseCode>502</ResponseCode>
            <ResponseCode>503</ResponseCode>
        </ServerUnhealthyResponse>
    </LoadBalancer>
    <Path>/api</Path>
</HTTPTargetConnection>
```

### Algoritmos

| Algoritmo | Comportamiento |
|---|---|
| `RoundRobin` | Reparto cíclico. Por defecto. |
| `Weighted` | Reparto proporcional a `<Weight>` por servidor. |
| `LeastConnections` | Al servidor con menos conexiones activas. |

Ejemplo ponderado (canary 90/10):

```xml
<LoadBalancer>
    <Algorithm>Weighted</Algorithm>
    <Server name="pedidos-v1"><Weight>9</Weight></Server>
    <Server name="pedidos-v2"><Weight>1</Weight></Server>
</LoadBalancer>
```

### MaxFailures — la trampa clásica

> [!CAUTION]
> **Antipatrón documentado:** balancear con **un solo TargetServer** y `MaxFailures` distinto de cero.
>
> Con un único servidor, al alcanzar `MaxFailures` Apigee lo marca como no saludable y **deja de enviarle tráfico**. Como no hay alternativa, **todas** las peticiones fallan hasta que un health monitor lo recupere. Si no hay health monitor configurado, no se recupera nunca.
>
> Regla: con un solo servidor, usa `<MaxFailures>0</MaxFailures>` (desactivado) o configura siempre un `HealthMonitor`.

## HealthMonitor

Marca servidores como saludables o no de forma activa, en lugar de esperar a fallos de tráfico real.

```xml
<HTTPTargetConnection>
    <LoadBalancer>
        <Algorithm>RoundRobin</Algorithm>
        <Server name="pedidos-svc-a"/>
        <Server name="pedidos-svc-b"/>
        <MaxFailures>3</MaxFailures>
    </LoadBalancer>
    <Path>/api</Path>
    <HealthMonitor>
        <IsEnabled>true</IsEnabled>
        <IntervalInSec>10</IntervalInSec>
        <HTTPMonitor>
            <Request>
                <ConnectTimeoutInSec>2</ConnectTimeoutInSec>
                <SocketReadTimeoutInSec>5</SocketReadTimeoutInSec>
                <Port>443</Port>
                <Verb>GET</Verb>
                <Path>/health</Path>
                <Header name="User-Agent">Apigee-HealthMonitor</Header>
            </Request>
            <SuccessResponse>
                <ResponseCode>200</ResponseCode>
            </SuccessResponse>
        </HTTPMonitor>
    </HealthMonitor>
</HTTPTargetConnection>
```

También existe `<TCPMonitor>` para comprobar solo la apertura del socket.

## Propiedades del TargetEndpoint

```xml
<Properties>
    <Property name="connect.timeout.millis">5000</Property>
    <Property name="io.timeout.millis">30000</Property>
    <Property name="supports.http10">false</Property>
    <Property name="request.retain.headers">User-Agent,Referer,Accept-Language</Property>
    <Property name="request.streaming.enabled">false</Property>
    <Property name="response.streaming.enabled">false</Property>
    <Property name="success.codes">1xx,2xx,3xx</Property>
    <Property name="keepalive.timeout.millis">60000</Property>
    <Property name="retain.queryparams">apikey</Property>
</Properties>
```

| Propiedad | Efecto | Recomendación |
|---|---|---|
| `connect.timeout.millis` | Timeout de establecimiento de conexión TCP | 3.000–5.000 ms |
| `io.timeout.millis` | Timeout de lectura de la respuesta | Menor que el timeout del cliente. Máximo de plataforma: **300 s** |
| `success.codes` | Qué códigos se consideran éxito | Amplíalo solo si el backend usa 4xx como flujo normal |
| `request.streaming.enabled` | Streaming de la petición | `true` solo si el payload supera los límites de buffer |
| `response.streaming.enabled` | Streaming de la respuesta | Ídem |
| `supports.http10` | Compatibilidad HTTP/1.0 | Dejar en `false` |
| `keepalive.timeout.millis` | Reutilización de conexión | **No lo pongas a 0**: desactivar keep-alive es un antipatrón |

### success.codes

Por defecto, un 4xx o 5xx del backend hace que Apigee entre en error flow. Para tratarlos como respuestas normales:

```xml
<Properties>
    <Property name="success.codes">1xx,2xx,3xx,400,500</Property>
</Properties>
```

Y luego manejarlos explícitamente en el response flow:

```xml
<Response>
    <Step>
        <Name>AM-TraducirErrorBackend</Name>
        <Condition>(response.status.code = 400) or (response.status.code = 500)</Condition>
    </Step>
</Response>
```

## Streaming

Con streaming activo, Apigee **no bufferiza** el mensaje. Consecuencia crítica:

> [!WARNING]
> **Con streaming activo, las políticas pierden acceso al contenido del mensaje.**
> `request.content`, `response.content` y cualquier política que parsee el payload (`ExtractVariables` sobre JSONPath, `JSONtoXML`, `JSONThreatProtection`, `OASValidation` de body) **dejan de funcionar**. Acceder al payload con streaming activo es un [antipatrón documentado](../09-antipatrones/01-catalogo-antipatrones.md).

Límites de payload:

| Modo | Límite |
|---|---|
| Buffered | **30 MB** |
| Streamed | **10 MB** (con salvedades de rendimiento) |
| Payload de MessageLogging | **11 MB** |

Superar el límite produce `protocol.http.TooBigBody`.

## SSLInfo — TLS hacia el backend

```xml
<SSLInfo>
    <Enabled>true</Enabled>
    <Enforce>true</Enforce>
    <ClientAuthEnabled>true</ClientAuthEnabled>
    <KeyStore>keystore-cliente</KeyStore>
    <KeyAlias>apigee-client</KeyAlias>
    <TrustStore>truststore-backends</TrustStore>
    <IgnoreValidationErrors>false</IgnoreValidationErrors>
    <Ciphers>
        <Cipher>TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384</Cipher>
    </Ciphers>
    <Protocols>
        <Protocol>TLSv1.2</Protocol>
        <Protocol>TLSv1.3</Protocol>
    </Protocols>
</SSLInfo>
```

> [!CAUTION]
> **Nunca uses `<IgnoreValidationErrors>true</IgnoreValidationErrors>` en producción.** Desactiva la validación del certificado del backend y abre la puerta a MITM.

Detalle en [TLS y mTLS](../03-seguridad/04-tls-mtls.md).

## Target dinámico

Se puede sobrescribir el destino en runtime asignando `target.url`:

```xml
<AssignMessage name="AM-TargetDinamico">
    <AssignVariable>
        <Name>target.url</Name>
        <Template>https://{region}.backend.example.com/api{proxy.pathsuffix}</Template>
    </AssignVariable>
    <IgnoreUnresolvedVariables>false</IgnoreUnresolvedVariables>
</AssignMessage>
```

Debe ejecutarse en el **TargetEndpoint → PreFlow → Request**.

> [!WARNING]
> Construir `target.url` con datos que vienen del cliente sin validar es una vulnerabilidad de **SSRF**. Valida siempre contra una lista de permitidos, idealmente almacenada en un KVM o PropertySet.

## Tipos de conexión alternativos

| Elemento | Uso |
|---|---|
| `<HTTPTargetConnection>` | HTTP/HTTPS. El habitual. |
| `<LocalTargetConnection>` | Encadenar proxies **dentro de la misma org/entorno** sin salir a la red. Mucho más eficiente que llamar por HTTP. |
| `<ScriptTarget>` | ⚠️ Solo Edge (Node.js/Trireme). Retirado. |

Encadenamiento local:

```xml
<LocalTargetConnection>
    <APIProxy>comun-auth-v1</APIProxy>
    <ProxyEndpoint>default</ProxyEndpoint>
</LocalTargetConnection>
```

> [!TIP]
> Para encadenar proxies, **usa `LocalTargetConnection`, no ServiceCallout ni una URL HTTP a tu propio hostname**. Llamar a tu propio proxy por HTTP añade un salto de red completo, duplica el consumo de cuota y es un antipatrón.

## Fuentes

- <https://cloud.google.com/apigee/docs/api-platform/deploy/load-balancing-across-backend-servers>
- <https://cloud.google.com/apigee/docs/api-platform/reference/limits>
- <https://docs.apigee.com/api-platform/antipatterns/load-balancer-single-target>
