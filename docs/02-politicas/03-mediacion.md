---
id: politicas-mediacion
titulo: Políticas de Mediación
area: politicas
tags: [assignmessage, extractvariables, xmltojson, jsontoxml, cors, oasvalidation, kvm]
aplica_a: [apigee-x, apigee-hybrid]
fuente: https://cloud.google.com/apigee/docs/api-platform/reference/policies/assign-message-policy
revisado: 2026-08-20
---

# Políticas de Mediación

## AssignMessage — la navaja suiza

Crea y modifica mensajes, cabeceras, payloads y variables. Es la política que más vas a escribir.

### Estructura completa

```xml
<AssignMessage continueOnError="false" enabled="true" name="AM-Ejemplo">
    <DisplayName>Ejemplo completo</DisplayName>

    <!-- 1. Crear variables -->
    <AssignVariable>
        <Name>peticion.canal</Name>
        <Ref>request.header.x-canal</Ref>
        <Value>web</Value>              <!-- valor por defecto si Ref no resuelve -->
    </AssignVariable>
    <AssignVariable>
        <Name>peticion.trace_id</Name>
        <Template>{messageid}-{system.timestamp}</Template>
    </AssignVariable>

    <!-- 2. Añadir sin sobrescribir lo existente -->
    <Add>
        <Headers>
            <Header name="X-Correlation-Id">{messageid}</Header>
        </Headers>
        <QueryParams>
            <QueryParam name="source">apigee</QueryParam>
        </QueryParams>
        <FormParams>
            <FormParam name="origen">gateway</FormParam>
        </FormParams>
    </Add>

    <!-- 3. Establecer, sobrescribiendo -->
    <Set>
        <Headers>
            <Header name="Content-Type">application/json</Header>
        </Headers>
        <QueryParams>
            <QueryParam name="version">v1</QueryParam>
        </QueryParams>
        <Payload contentType="application/json">
            {"pedido_id":"{peticion.id}","canal":"{peticion.canal}"}
        </Payload>
        <Verb>POST</Verb>
        <Path>/api/v2/pedidos</Path>
        <StatusCode>200</StatusCode>
        <ReasonPhrase>OK</ReasonPhrase>
    </Set>

    <!-- 4. Eliminar -->
    <Remove>
        <Headers>
            <Header name="X-Interno-Debug"/>
            <Header name="Server"/>
        </Headers>
        <QueryParams>
            <QueryParam name="apikey"/>
        </QueryParams>
    </Remove>

    <!-- 5. Copiar de otro mensaje -->
    <Copy source="request">
        <Headers>
            <Header name="X-Request-Id"/>
        </Headers>
        <Payload>true</Payload>
    </Copy>

    <!-- 6. A qué mensaje se aplica todo lo anterior -->
    <AssignTo createNew="false" transport="http" type="request"/>

    <IgnoreUnresolvedVariables>true</IgnoreUnresolvedVariables>
</AssignMessage>
```

### AssignTo — el elemento que más confunde

```xml
<AssignTo createNew="false" transport="http" type="request"/>
```

| `createNew` | `type` | Efecto |
|---|---|---|
| `false` | `request` | Modifica la petición **actual** |
| `false` | `response` | Modifica la respuesta **actual** |
| `true` | `request` | Crea un **mensaje nuevo** (para pasárselo a un `ServiceCallout`) |

Con `createNew="true"` se debe dar un nombre:

```xml
<AssignTo createNew="true" transport="http" type="request">peticion.callout</AssignTo>
```

### Casos de uso frecuentes

**Devolver una respuesta sin llamar al backend (mock / health):**

```xml
<AssignMessage name="AM-Health">
    <Set>
        <StatusCode>200</StatusCode>
        <ReasonPhrase>OK</ReasonPhrase>
        <Payload contentType="application/json">{"estado":"ok","proxy":"{apiproxy.name}","rev":"{apiproxy.revision}"}</Payload>
    </Set>
    <AssignTo createNew="true" transport="http" type="response"/>
    <IgnoreUnresolvedVariables>true</IgnoreUnresolvedVariables>
</AssignMessage>
```

**Limpiar cabeceras internas antes de responder:**

```xml
<AssignMessage name="AM-LimpiarCabeceras">
    <Remove>
        <Headers>
            <Header name="Server"/>
            <Header name="X-Powered-By"/>
            <Header name="X-AspNet-Version"/>
            <Header name="X-Backend-Server"/>
        </Headers>
    </Remove>
    <AssignTo createNew="false" transport="http" type="response"/>
    <IgnoreUnresolvedVariables>true</IgnoreUnresolvedVariables>
</AssignMessage>
```

**Reescribir la ruta hacia el backend:**

```xml
<AssignMessage name="AM-ReescribirRuta">
    <Set>
        <Path>/internal/v3{proxy.pathsuffix}</Path>
    </Set>
    <AssignTo createNew="false" transport="http" type="request"/>
    <IgnoreUnresolvedVariables>true</IgnoreUnresolvedVariables>
</AssignMessage>
```

---

## ExtractVariables

Extrae datos del mensaje a variables. Soporta JSONPath, XPath, regex, cabeceras, query params y form params.

```xml
<ExtractVariables continueOnError="false" enabled="true" name="EV-ExtraerPedido">
    <DisplayName>Extraer datos del pedido</DisplayName>
    <Source>request</Source>
    <VariablePrefix>pedido</VariablePrefix>

    <JSONPayload>
        <Variable name="id"       type="string">
            <JSONPath>$.pedido.id</JSONPath>
        </Variable>
        <Variable name="total"    type="double">
            <JSONPath>$.pedido.total</JSONPath>
        </Variable>
        <Variable name="cliente"  type="string">
            <JSONPath>$.pedido.cliente.email</JSONPath>
        </Variable>
        <Variable name="n_lineas" type="integer">
            <JSONPath>$.pedido.lineas.length()</JSONPath>
        </Variable>
    </JSONPayload>

    <Header name="X-Tenant-Id">
        <Pattern ignoreCase="true">{tenant}</Pattern>
    </Header>

    <QueryParam name="page">
        <Pattern>{pagina}</Pattern>
    </QueryParam>

    <URIPath>
        <Pattern ignoreCase="true">/pedidos/{id_ruta}</Pattern>
    </URIPath>

    <IgnoreUnresolvedVariables>true</IgnoreUnresolvedVariables>
</ExtractVariables>
```

Con `<VariablePrefix>pedido</VariablePrefix>`, las variables resultantes son `pedido.id`, `pedido.total`, `pedido.tenant`, `pedido.id_ruta`, etc.

**Extraer un path param** (el uso más común):

```xml
<ExtractVariables name="EV-IdRuta">
    <Source>request</Source>
    <URIPath>
        <Pattern ignoreCase="true">/pedidos/{pedido_id}</Pattern>
        <Pattern ignoreCase="true">/pedidos/{pedido_id}/lineas/{linea_id}</Pattern>
    </URIPath>
    <VariablePrefix>ruta</VariablePrefix>
    <IgnoreUnresolvedVariables>true</IgnoreUnresolvedVariables>
</ExtractVariables>
```

**Con XPath sobre XML:**

```xml
<XMLPayload stopPayloadProcessing="false">
    <Namespaces>
        <Namespace prefix="ns">http://example.com/pedidos</Namespace>
    </Namespaces>
    <Variable name="id" type="string">
        <XPath>/ns:pedido/ns:id/text()</XPath>
    </Variable>
</XMLPayload>
```

> [!TIP]
> Google recomienda **`ExtractVariables` + `AssignMessage` antes que JavaScript** siempre que sea posible. Son nativas, más rápidas y soportadas.

---

## Conversión JSON ↔ XML

```xml
<XMLtoJSON continueOnError="false" enabled="true" name="X2J-RespuestaBackend">
    <Source>response</Source>
    <OutputVariable>response</OutputVariable>
    <Options>
        <RecognizeNumber>true</RecognizeNumber>
        <RecognizeBoolean>true</RecognizeBoolean>
        <RecognizeNull>true</RecognizeNull>
        <NamespaceBlockName>#namespaces</NamespaceBlockName>
        <DefaultNamespaceNodeName>&amp;</DefaultNamespaceNodeName>
        <NamespaceSeparator>:</NamespaceSeparator>
        <TextNodeName>#text</TextNodeName>
        <AttributePrefix>@</AttributePrefix>
        <StripLevels>0</StripLevels>
        <TreatAsArray>
            <Path unwrap="true">pedido/lineas/linea</Path>
        </TreatAsArray>
    </Options>
</XMLtoJSON>
```

```xml
<JSONtoXML continueOnError="false" enabled="true" name="J2X-PeticionBackend">
    <Source>request</Source>
    <OutputVariable>request</OutputVariable>
    <Options>
        <NullValue>NULL</NullValue>
        <NamespaceBlockName>#namespaces</NamespaceBlockName>
        <DefaultNamespaceNodeName>$default</DefaultNamespaceNodeName>
        <NamespaceSeparator>:</NamespaceSeparator>
        <TextNodeName>#text</TextNodeName>
        <AttributePrefix>@</AttributePrefix>
        <InvalidCharsReplacement>_</InvalidCharsReplacement>
        <ObjectRootElementName>Root</ObjectRootElementName>
        <ArrayRootElementName>Array</ArrayRootElementName>
        <ArrayItemElementName>Item</ArrayItemElementName>
    </Options>
</JSONtoXML>
```

> [!IMPORTANT]
> `<TreatAsArray>` es esencial: sin él, un XML con **un solo** elemento repetible produce un objeto JSON, y con **dos** produce un array. El cliente recibe estructuras distintas según los datos. Declara explícitamente qué caminos son arrays.

---

## CORS

```xml
<CORS continueOnError="false" enabled="true" name="CORS-Permitir">
    <DisplayName>CORS</DisplayName>
    <AllowOrigins>https://app.empresa.com,https://admin.empresa.com</AllowOrigins>
    <AllowMethods>GET,POST,PUT,PATCH,DELETE,OPTIONS</AllowMethods>
    <AllowHeaders>Origin,Content-Type,Accept,Authorization,X-Api-Key</AllowHeaders>
    <ExposeHeaders>X-RateLimit-Remaining,X-Correlation-Id</ExposeHeaders>
    <MaxAge>3628800</MaxAge>
    <AllowCredentials>true</AllowCredentials>
    <GeneratePreflightResponse>true</GeneratePreflightResponse>
    <IgnoreUnresolvedVariables>true</IgnoreUnresolvedVariables>
</CORS>
```

> [!WARNING]
> **Nunca uses `<AllowOrigins>*</AllowOrigins>` junto con `<AllowCredentials>true</AllowCredentials>`.** Los navegadores rechazan esa combinación, y conceptualmente es una brecha: expone credenciales a cualquier origen.

> [!CAUTION]
> Advertencia explícita de Google: **si usas una política de caché, asegúrate de que la respuesta de CORS no se cachea.** Cachear una respuesta con `Access-Control-Allow-Origin` de un origen la sirve a otro origen distinto, rompiendo CORS de forma intermitente y muy difícil de diagnosticar.

Colocación: `<CORS>` con `GeneratePreflightResponse=true` va en el **PreFlow del ProxyEndpoint**, antes de la autenticación, para que el preflight `OPTIONS` no requiera credenciales.

```xml
<PreFlow name="PreFlow">
    <Request>
        <Step><Name>CORS-Permitir</Name></Step>
        <Step>
            <Name>VAK-VerificarApiKey</Name>
            <Condition>request.verb != "OPTIONS"</Condition>
        </Step>
    </Request>
</PreFlow>
```

---

## OASValidation

Valida peticiones y respuestas contra una spec OpenAPI incluida en `resources/oas/`.

```xml
<OASValidation continueOnError="false" enabled="true" name="OAS-Validar">
    <DisplayName>Validar contra OpenAPI</DisplayName>
    <OASResource>oas://pedidos.yaml</OASResource>
    <Source>request</Source>
    <Options>
        <ValidateMessageBody>true</ValidateMessageBody>
        <AllowUnspecifiedParameters>
            <Header>false</Header>
            <Query>false</Query>
            <Cookie>true</Cookie>
        </AllowUnspecifiedParameters>
    </Options>
</OASValidation>
```

Ventaja: la spec es la única fuente de verdad. Si el contrato cambia, la validación cambia sin tocar políticas.

> [!NOTE]
> `OASValidation` requiere el payload **bufferizado**. No funciona con streaming activo.

---

## SOAPMessageValidation / MessageValidation

```xml
<MessageValidation continueOnError="false" enabled="true" name="MV-ValidarSoap">
    <Source>request</Source>
    <ResourceURL>wsdl://pedidos.wsdl</ResourceURL>
    <SOAPMessage version="1.1"/>
    <Element namespace="http://example.com/pedidos">CrearPedido</Element>
</MessageValidation>
```

También valida contra XSD (`xsd://esquema.xsd`) y JSON Schema.

---

## RaiseFault

Genera un fallo explícito con respuesta personalizada.

```xml
<RaiseFault continueOnError="false" enabled="true" name="RF-Prohibido">
    <DisplayName>403 Prohibido</DisplayName>
    <IgnoreUnresolvedVariables>true</IgnoreUnresolvedVariables>
    <FaultResponse>
        <Set>
            <Headers>
                <Header name="Content-Type">application/json</Header>
                <Header name="X-Correlation-Id">{messageid}</Header>
            </Headers>
            <StatusCode>403</StatusCode>
            <ReasonPhrase>Forbidden</ReasonPhrase>
            <Payload contentType="application/json">
                {"error":{"codigo":"CANAL_NO_PERMITIDO","mensaje":"Este canal no tiene acceso a la operación","correlation_id":"{messageid}"}}
            </Payload>
        </Set>
    </FaultResponse>
</RaiseFault>
```

> [!CAUTION]
> **Antipatrón documentado: usar RaiseFault en condiciones inapropiadas.**
> `RaiseFault` **aborta el pipeline**. Si solo quieres modificar la respuesta o registrar algo, usa `AssignMessage` o `MessageLogging`. Reserva `RaiseFault` para cortar de verdad la ejecución.

---

## AssertCondition

Alternativa declarativa a `RaiseFault` con condición:

```xml
<AssertCondition name="AC-TenantObligatorio">
    <Condition>request.header.x-tenant-id != null</Condition>
    <FaultResponse>
        <Set>
            <StatusCode>400</StatusCode>
            <Payload contentType="application/json">{"error":"falta_tenant"}</Payload>
        </Set>
    </FaultResponse>
</AssertCondition>
```

---

## HTTPModifier

Modificación ligera de cabeceras y códigos de estado. Más simple y barata que `AssignMessage` cuando solo necesitas eso.

```xml
<HTTPModifier name="HM-QuitarCabeceras">
    <Remove>
        <Headers>
            <Header name="Server"/>
            <Header name="X-Powered-By"/>
        </Headers>
    </Remove>
    <AssignTo type="response"/>
</HTTPModifier>
```

---

## KeyValueMapOperations

Lectura y escritura en un KVM. Uso principal: **configuración por entorno** y **secretos**.

```xml
<KeyValueMapOperations continueOnError="false" enabled="true"
                       name="KVM-LeerConfig" mapIdentifier="config-backends">
    <DisplayName>Leer configuración</DisplayName>
    <Scope>environment</Scope>
    <ExpiryTimeInSecs>300</ExpiryTimeInSecs>
    <Get assignTo="private.api_key_backend" index="1">
        <Key>
            <Parameter>backend_api_key</Parameter>
        </Key>
    </Get>
    <Get assignTo="config.timeout" index="1">
        <Key>
            <Parameter ref="apiproduct.name"/>
            <Parameter>timeout</Parameter>
        </Key>
    </Get>
</KeyValueMapOperations>
```

Escritura:

```xml
<KeyValueMapOperations name="KVM-Escribir" mapIdentifier="estado-sync">
    <Scope>environment</Scope>
    <Put override="true">
        <Key><Parameter>ultima_sync</Parameter></Key>
        <Value ref="system.timestamp"/>
    </Put>
</KeyValueMapOperations>
```

> [!IMPORTANT]
> - Usa el prefijo `private.` en `assignTo` para **secretos**: no aparecen en Trace.
> - Los KVM de Apigee X son **cifrados por defecto**.
> - `<ExpiryTimeInSecs>` cachea la lectura en memoria y evita pegar a Cassandra en cada petición. **Ponlo siempre**; sin él, cada llamada es un acceso a Cassandra.

Límites: clave ≤ **2 KB**, valor ≤ **10 KB**, **5 millones de entradas por org**, **100 KVMs con scope org** y **900 con scope environment**.

> [!WARNING]
> Los KVM **no son una base de datos**. Google es explícito: úsalos solo para conjuntos de datos limitados, no para almacenamiento a largo plazo. Los datos viven en Cassandra y el impacto en rendimiento es real.

---

## ReadPropertySet

Alternativa **sin coste de runtime** al KVM para configuración estática que va versionada con el bundle.

`resources/properties/config.properties`:
```properties
timeout_backend=30000
version_api=v1
feature_nuevo_flujo=true
```

Lo habitual es leerlas **directamente como variables**, sin ninguna política:

```
propertyset.config.timeout_backend
propertyset.config.version_api
propertyset.config.feature_nuevo_flujo
```

```xml
<AssignMessage name="AM-AplicarConfig">
    <AssignVariable>
        <Name>target.url</Name>
        <Template>https://backend.example.com/{propertyset.config.version_api}{proxy.pathsuffix}</Template>
    </AssignVariable>
    <IgnoreUnresolvedVariables>false</IgnoreUnresolvedVariables>
</AssignMessage>
```

Y usarlas en condiciones:

```xml
<Condition>propertyset.config.feature_nuevo_flujo = "true"</Condition>
```

| Elegir | Cuándo |
|---|---|
| **PropertySet** | Configuración **estática**, igual para todos los despliegues del bundle, versionada en Git |
| **KVM** | Configuración **por entorno**, secretos, o valores que cambian sin redesplegar |

## Fuentes

- <https://cloud.google.com/apigee/docs/api-platform/reference/policies/assign-message-policy>
- <https://cloud.google.com/apigee/docs/api-platform/reference/policies/extract-variables-policy>
- <https://cloud.google.com/apigee/docs/api-platform/reference/policies/cors-policy>
- <https://cloud.google.com/apigee/docs/api-platform/reference/policies/key-value-map-operations-policy>
