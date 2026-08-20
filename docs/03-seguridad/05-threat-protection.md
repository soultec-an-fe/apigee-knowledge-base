---
id: seguridad-threat-protection
titulo: Threat protection
area: seguridad
tags: [threat-protection, json, xml, regex, sqli, xss, owasp]
aplica_a: [apigee-x, apigee-hybrid]
fuente: https://cloud.google.com/apigee/docs/api-platform/reference/policies/json-threat-protection-policy
revisado: 2026-08-20
---

# Threat protection

> [!IMPORTANT]
> Recomendación explícita de Google en las mejores prácticas:
> **aplica siempre políticas de protección de contenido a los proxies de producción.**
> Las cuatro políticas relevantes son `JSONThreatProtection`, `XMLThreatProtection`, `RegularExpressionProtection` y `SOAPMessageValidation`.

## Qué protege cada capa

| Amenaza | Herramienta correcta |
|---|---|
| DDoS volumétrico, IPs maliciosas conocidas, geo-bloqueo | **Cloud Armor** (delante del balanceador) |
| Abuso por cliente autenticado | `SpikeArrest` + `Quota` |
| Payload estructuralmente malicioso (bombas JSON/XML) | `JSONThreatProtection` / `XMLThreatProtection` |
| Inyección de contenido (SQLi, XSS) | `RegularExpressionProtection` |
| Payload que no cumple el contrato | `OASValidation` / `MessageValidation` |
| Detección de anomalías y abuso de API | **Advanced API Security** |

> [!NOTE]
> Apigee **no es un WAF completo**. Para bloqueo por IP a escala, reglas OWASP gestionadas y mitigación de DDoS, la herramienta es **Cloud Armor** delante del Cloud Load Balancer. La `AccessControl` de Apigee sirve para listas pequeñas y para restringir entornos de test.

---

## JSONThreatProtection

Defiende contra payloads JSON diseñados para agotar el parser: anidamiento profundo, arrays enormes, claves gigantes.

```xml
<JSONThreatProtection continueOnError="false" enabled="true" name="JTP-ProtegerJson">
    <DisplayName>Proteger JSON</DisplayName>
    <Source>request</Source>
    <ArrayElementCount>100</ArrayElementCount>
    <ContainerDepth>10</ContainerDepth>
    <ObjectEntryCount>50</ObjectEntryCount>
    <ObjectEntryNameLength>64</ObjectEntryNameLength>
    <StringValueLength>2048</StringValueLength>
</JSONThreatProtection>
```

| Elemento | Qué limita | Valor razonable |
|---|---|---|
| `<ArrayElementCount>` | Nº máximo de elementos en un array | 100–1000 según el caso |
| `<ContainerDepth>` | Profundidad de anidamiento | 10 |
| `<ObjectEntryCount>` | Nº de propiedades en un objeto | 50 |
| `<ObjectEntryNameLength>` | Longitud del nombre de una clave | 64 |
| `<StringValueLength>` | Longitud de un valor string | 2048 (súbelo si aceptas texto largo) |

> [!TIP]
> Calibra estos valores contra tu **payload legítimo más grande**, con margen. Demasiado estricto = rechazas tráfico válido; demasiado laxo = no proteges nada.

Colocación: ProxyEndpoint → PreFlow → Request, condicionado a métodos con body.

```xml
<Step>
    <Name>JTP-ProtegerJson</Name>
    <Condition>(request.verb = "POST") or (request.verb = "PUT") or (request.verb = "PATCH")</Condition>
</Step>
```

---

## XMLThreatProtection

Además de límites estructurales, protege contra **XML entity expansion** ("billion laughs") y **XML bombs**.

```xml
<XMLThreatProtection continueOnError="false" enabled="true" name="XTP-ProtegerXml">
    <DisplayName>Proteger XML</DisplayName>
    <Source>request</Source>
    <NameLimits>
        <Element>64</Element>
        <Attribute>64</Attribute>
        <NamespacePrefix>32</NamespacePrefix>
        <ProcessingInstructionTarget>32</ProcessingInstructionTarget>
    </NameLimits>
    <StructureLimits>
        <NodeDepth>10</NodeDepth>
        <AttributeCountPerElement>10</AttributeCountPerElement>
        <NamespaceCountPerElement>5</NamespaceCountPerElement>
        <ChildCount includeComment="true"
                    includeElement="true"
                    includeProcessingInstruction="true"
                    includeText="true">20</ChildCount>
    </StructureLimits>
    <ValueLimits>
        <Text>2048</Text>
        <Attribute>256</Attribute>
        <NamespaceURI>256</NamespaceURI>
        <Comment>512</Comment>
        <ProcessingInstructionData>512</ProcessingInstructionData>
    </ValueLimits>
</XMLThreatProtection>
```

---

## RegularExpressionProtection

Bloquea patrones de inyección en la URL, en parámetros, cabeceras y payload.

```xml
<RegularExpressionProtection continueOnError="false" enabled="true" name="REP-AntiInyeccion">
    <DisplayName>Protección contra inyección</DisplayName>
    <Source>request</Source>
    <IgnoreUnresolvedVariables>false</IgnoreUnresolvedVariables>

    <URIPath>
        <Pattern>(?i)\b(drop\s+table|truncate\s+table|exec\s*\()</Pattern>
    </URIPath>

    <QueryParam name="q">
        <Pattern>(?i)\b(union\s+select|insert\s+into)\b</Pattern>
        <Pattern>(?i)&lt;\s*script</Pattern>
    </QueryParam>

    <Header name="X-Filtro">
        <Pattern>(?i)&lt;\s*script</Pattern>
    </Header>

    <JSONPayload>
        <JSONPath JSONPath="$.comentario">
            <Pattern>(?i)&lt;\s*script</Pattern>
            <Pattern>(?i)javascript\s*:</Pattern>
        </JSONPath>
    </JSONPayload>
</RegularExpressionProtection>
```

> [!CAUTION]
> **Antipatrón documentado: cuantificadores greedy en RegularExpressionProtection.**
>
> Patrones como `.*`, `.+`, o anidamientos tipo `(a+)+` provocan **backtracking catastrófico**. Un payload de pocos KB cuidadosamente construido puede consumir segundos de CPU de un Message Processor. El resultado es que la política de seguridad **se convierte en el vector de DoS**.
>
> Reglas:
> - Ancla los patrones (`^`, `$`, `\b`).
> - Usa cuantificadores reluctantes (`.*?`) o posesivos (`.*+`) en lugar de greedy.
> - Nunca anides cuantificadores: `(x+)+`, `(x*)*`.
> - Mide el coste del patrón antes de desplegarlo.

> [!WARNING]
> `RegularExpressionProtection` es una **defensa en profundidad, no la defensa principal**. La protección real contra SQLi es que el backend use consultas parametrizadas; contra XSS, que el frontend escape la salida. Una regex en el gateway detiene ataques oportunistas, no a un atacante determinado. No la uses como excusa para no arreglar el backend.

---

## OASValidation como control de seguridad

Con frecuencia la mejor protección no es una lista de patrones prohibidos sino una **lista de permitidos**: valida contra el contrato OpenAPI y rechaza cualquier cosa que no encaje.

```xml
<OASValidation continueOnError="false" enabled="true" name="OAS-Validar">
    <OASResource>oas://pedidos.yaml</OASResource>
    <Source>request</Source>
    <Options>
        <ValidateMessageBody>true</ValidateMessageBody>
        <AllowUnspecifiedParameters>
            <Header>false</Header>
            <Query>false</Query>
            <Cookie>false</Cookie>
        </AllowUnspecifiedParameters>
    </Options>
</OASValidation>
```

Con `AllowUnspecifiedParameters` en `false`, cualquier parámetro no declarado en la spec se rechaza. Es un control de superficie de ataque muy efectivo y de mantenimiento casi nulo.

---

## Advanced API Security

Complemento de pago de Apigee que aporta lo que las políticas no pueden:

- **Detección de abuso**: identifica patrones de tráfico anómalo por cliente (scraping, credential stuffing, enumeración).
- **Security scores**: puntúa la configuración de cada proxy contra buenas prácticas y señala carencias.
- **Detección de APIs no gestionadas** ("shadow APIs") en el tráfico.
- **Acciones de seguridad**: bloquear o marcar clientes automáticamente según reglas.

Disponibilidad según el tipo de environment. Verifica el catálogo vigente antes de asumir que está incluido.

---

## Orden recomendado en el PreFlow

```xml
<PreFlow name="PreFlow">
    <Request>
        <!-- 1. CORS antes de todo, para que el preflight no requiera credenciales -->
        <Step><Name>CORS-Permitir</Name></Step>

        <!-- 2. Identidad: rechazar lo antes posible -->
        <Step>
            <Name>VAK-VerificarApiKey</Name>
            <Condition>request.verb != "OPTIONS"</Condition>
        </Step>

        <!-- 3. Protección del runtime -->
        <Step>
            <Name>SA-FrenoDePicos</Name>
            <Condition>request.verb != "OPTIONS"</Condition>
        </Step>

        <!-- 4. Plan de negocio -->
        <Step>
            <Name>Q-CuotaProducto</Name>
            <Condition>request.verb != "OPTIONS"</Condition>
        </Step>

        <!-- 5. Estructura del payload, antes de parsearlo -->
        <Step>
            <Name>JTP-ProtegerJson</Name>
            <Condition>(request.verb = "POST") or (request.verb = "PUT") or (request.verb = "PATCH")</Condition>
        </Step>

        <!-- 6. Contenido del payload -->
        <Step>
            <Name>REP-AntiInyeccion</Name>
            <Condition>(request.verb = "POST") or (request.verb = "PUT") or (request.verb = "PATCH")</Condition>
        </Step>

        <!-- 7. Contrato -->
        <Step>
            <Name>OAS-Validar</Name>
            <Condition>request.verb != "OPTIONS"</Condition>
        </Step>
    </Request>
</PreFlow>
```

La lógica del orden: **lo más barato y lo que descarta más tráfico va primero**. No tiene sentido parsear un payload de 5 MB para descubrir después que la API key no era válida.

## Fuentes

- <https://cloud.google.com/apigee/docs/api-platform/reference/policies/json-threat-protection-policy>
- <https://cloud.google.com/apigee/docs/api-platform/reference/policies/xml-threat-protection-policy>
- <https://cloud.google.com/apigee/docs/api-platform/reference/policies/regular-expression-protection>
- <https://docs.apigee.com/api-platform/antipatterns/greedy-quantifiers>
