---
id: proxies-anatomia
titulo: Anatomía de un API proxy
area: proxies
tags: [bundle, proxyendpoint, targetendpoint, routerule, estructura, xml]
aplica_a: [apigee-x, apigee-hybrid]
fuente: https://cloud.google.com/apigee/docs/api-platform/fundamentals/understanding-apis-and-api-proxies
revisado: 2026-08-20
---

# Anatomía de un API proxy

Un API proxy es un **directorio con estructura fija** que se empaqueta en ZIP y se sube a Apigee. Máximo **15 MB** por bundle.

## Estructura del bundle

```
apiproxy/
├── pedidos-v1.xml                  # Descriptor raíz del proxy
├── proxies/
│   └── default.xml                 # ProxyEndpoint (cara al cliente)
├── targets/
│   ├── default.xml                 # TargetEndpoint (cara al backend)
│   └── legacy.xml                  # Otro target opcional
├── policies/
│   ├── VAK-VerificarApiKey.xml     # Una política = un archivo XML
│   ├── Q-CuotaPorProducto.xml
│   ├── AM-ConstruirError.xml
│   └── JS-NormalizarPayload.xml
└── resources/
    ├── jsc/
    │   └── normalizar-payload.js   # Recursos JavaScript
    ├── java/
    │   └── mi-callout.jar          # JARs de JavaCallout
    ├── xsl/
    │   └── transformar.xsl
    ├── oas/
    │   └── pedidos.yaml            # Spec OpenAPI para OASValidation
    └── properties/
        └── config.properties       # PropertySet
```

> [!IMPORTANT]
> El atributo `name` del elemento raíz de cada política **debe coincidir con el nombre del archivo** (sin `.xml`). Si no coincide, el despliegue falla.

## 1. Descriptor raíz

`apiproxy/pedidos-v1.xml`

```xml
<APIProxy revision="1" name="pedidos-v1">
    <DisplayName>Pedidos v1</DisplayName>
    <Description>API de gestión de pedidos. Backend: pedidos-svc.</Description>
    <ProxyEndpoints>
        <ProxyEndpoint>default</ProxyEndpoint>
    </ProxyEndpoints>
    <TargetEndpoints>
        <TargetEndpoint>default</TargetEndpoint>
    </TargetEndpoints>
</APIProxy>
```

En la práctica Apigee regenera este archivo al desplegar, así que rara vez se edita a mano.

## 2. ProxyEndpoint

Define **cómo entra** la petición y qué se hace con ella antes de elegir destino.

`apiproxy/proxies/default.xml`

```xml
<ProxyEndpoint name="default">
    <Description>Entrada pública de la API de pedidos</Description>

    <!-- Manejo de errores del lado cliente -->
    <FaultRules>
        <FaultRule name="apikey-invalida">
            <Step><Name>AM-ErrorApiKey</Name></Step>
            <Condition>(fault.name = "FailedToResolveAPIKey")</Condition>
        </FaultRule>
    </FaultRules>
    <DefaultFaultRule name="fallback">
        <Step><Name>AM-ErrorGenerico</Name></Step>
        <AlwaysEnforce>true</AlwaysEnforce>
    </DefaultFaultRule>

    <PreFlow name="PreFlow">
        <Request>
            <Step><Name>VAK-VerificarApiKey</Name></Step>
            <Step><Name>Q-CuotaPorProducto</Name></Step>
            <Step><Name>SA-FrenoDePicos</Name></Step>
        </Request>
        <Response/>
    </PreFlow>

    <Flows>
        <Flow name="ListarPedidos">
            <Description>GET /pedidos</Description>
            <Condition>(proxy.pathsuffix MatchesPath "/pedidos") and (request.verb = "GET")</Condition>
            <Request>
                <Step><Name>EV-ExtraerFiltros</Name></Step>
            </Request>
            <Response/>
        </Flow>

        <Flow name="CrearPedido">
            <Description>POST /pedidos</Description>
            <Condition>(proxy.pathsuffix MatchesPath "/pedidos") and (request.verb = "POST")</Condition>
            <Request>
                <Step><Name>JTP-ProtegerJson</Name></Step>
                <Step><Name>OAS-ValidarPeticion</Name></Step>
            </Request>
            <Response/>
        </Flow>

        <!-- Catch-all: cualquier ruta no declarada arriba -->
        <Flow name="NoEncontrado">
            <Request>
                <Step><Name>RF-RutaNoSoportada</Name></Step>
            </Request>
            <Response/>
        </Flow>
    </Flows>

    <PostFlow name="PostFlow">
        <Request/>
        <Response>
            <Step><Name>HM-QuitarCabecerasBackend</Name></Step>
        </Response>
    </PostFlow>

    <PostClientFlow>
        <Response>
            <Step><Name>ML-RegistrarTransaccion</Name></Step>
        </Response>
    </PostClientFlow>

    <HTTPProxyConnection>
        <BasePath>/pedidos/v1</BasePath>
        <Properties/>
    </HTTPProxyConnection>

    <!-- Se evalúan DE ARRIBA ABAJO. La última, sin condición, es la de por defecto. -->
    <RouteRule name="a-legacy">
        <Condition>(request.header.x-canal = "legacy")</Condition>
        <TargetEndpoint>legacy</TargetEndpoint>
    </RouteRule>
    <RouteRule name="sin-target">
        <Condition>(proxy.pathsuffix MatchesPath "/health")</Condition>
        <!-- Sin <TargetEndpoint>: la respuesta se genera en el propio proxy -->
    </RouteRule>
    <RouteRule name="default">
        <TargetEndpoint>default</TargetEndpoint>
    </RouteRule>
</ProxyEndpoint>
```

### Puntos críticos del ProxyEndpoint

- **`<BasePath>`** es lo que empareja con la URL entrante. `proxy.pathsuffix` es lo que queda **después** del basepath.
- **Las RouteRules se evalúan de arriba abajo.** La primera cuya condición sea verdadera gana. **La regla por defecto (sin `<Condition>`) debe ir la última**; si la pones primera, el resto nunca se evalúa.
- Una **RouteRule sin `<TargetEndpoint>`** produce un *no-target proxy*: la respuesta se construye íntegramente en el proxy (útil para health checks, mocks y respuestas estáticas).
- Google recomienda **un solo ProxyEndpoint por proxy**. Ver [antipatrones](../09-antipatrones/01-catalogo-antipatrones.md). El límite duro es 10.

## 3. TargetEndpoint

Define **a dónde va** la petición y cómo se conecta.

`apiproxy/targets/default.xml`

```xml
<TargetEndpoint name="default">
    <Description>Backend de pedidos</Description>

    <FaultRules>
        <FaultRule name="backend-caido">
            <Step><Name>AM-Error503</Name></Step>
            <Condition>(fault.name = "ErrorResponseCode") or (fault.name Matches "*timeout*")</Condition>
        </FaultRule>
    </FaultRules>

    <PreFlow name="PreFlow">
        <Request>
            <Step><Name>AM-AnadirAuthBackend</Name></Step>
        </Request>
        <Response/>
    </PreFlow>

    <Flows/>

    <PostFlow name="PostFlow">
        <Request/>
        <Response/>
    </PostFlow>

    <HTTPTargetConnection>
        <!-- Opción A: URL directa (evitar en producción) -->
        <!-- <URL>https://pedidos-svc.interno.example.com/api</URL> -->

        <!-- Opción B: TargetServer con balanceo (recomendado) -->
        <LoadBalancer>
            <Algorithm>RoundRobin</Algorithm>
            <Server name="pedidos-svc-a"/>
            <Server name="pedidos-svc-b"/>
            <MaxFailures>3</MaxFailures>
        </LoadBalancer>
        <Path>/api</Path>

        <Properties>
            <Property name="connect.timeout.millis">5000</Property>
            <Property name="io.timeout.millis">30000</Property>
            <Property name="supports.http10">false</Property>
            <Property name="success.codes">1xx,2xx,3xx</Property>
        </Properties>

        <SSLInfo>
            <Enabled>true</Enabled>
            <Enforce>true</Enforce>
            <TrustStore>truststore-backends</TrustStore>
        </SSLInfo>
    </HTTPTargetConnection>
</TargetEndpoint>
```

Detalle completo en [TargetEndpoints y servidores](05-target-endpoints-y-servidores.md).

## 4. Política

Cada política es un archivo independiente. Ejemplo `apiproxy/policies/VAK-VerificarApiKey.xml`:

```xml
<VerifyAPIKey continueOnError="false" enabled="true" name="VAK-VerificarApiKey">
    <DisplayName>Verificar API key</DisplayName>
    <APIKey ref="request.header.x-api-key"/>
</VerifyAPIKey>
```

Atributos comunes a todas las políticas:

| Atributo | Valores | Efecto |
|---|---|---|
| `name` | string | **Debe** coincidir con el nombre del archivo. Es el ID usado en `<Step><Name>`. |
| `enabled` | `true` / `false` | `false` desactiva la política sin borrarla. |
| `continueOnError` | `true` / `false` | `true` evita entrar en error flow ante un fallo; deja `<prefijo>.<nombre>.failed = true`. |
| `async` | `true` / `false` | Obsoleto; no usar. |

## 5. Recursos

Archivos de apoyo referenciados por las políticas de extensión:

| Carpeta | Contenido | Consumido por |
|---|---|---|
| `resources/jsc/` | `.js` | `JavaScript` |
| `resources/java/` | `.jar` | `JavaCallout` |
| `resources/xsl/` | `.xsl` | `XSL` |
| `resources/oas/` | `.yaml` / `.json` | `OASValidation` |
| `resources/graphql/` | `.graphql` | `GraphQL` |
| `resources/properties/` | `.properties` | `ReadPropertySet` / `propertyset.*` |

Los recursos también pueden subirse con scope de **environment** u **organización** para compartirlos entre proxies. Para JARs de Java, Google recomienda **importarlos vía la API de recursos** en lugar de meterlos en el bundle.

## Reglas de oro

1. **Un ProxyEndpoint por proxy.**
2. **Un `<Flow>` por operación** (verbo + ruta), no condiciones múltiples colgando del PreFlow.
3. **La RouteRule por defecto va la última.**
4. **Nunca hardcodees la URL del backend**: usa `TargetServer`.
5. **Elimina políticas y recursos sin usar**: ralentizan el despliegue.
6. **Crea un proxy por defecto** con `<BasePath>/</BasePath>` como red de seguridad para peticiones a rutas no mapeadas.

## Fuentes

- <https://cloud.google.com/apigee/docs/api-platform/fundamentals/understanding-apis-and-api-proxies>
- <https://docs.apigee.com/api-platform/fundamentals/best-practices-api-proxy-design-and-development>
