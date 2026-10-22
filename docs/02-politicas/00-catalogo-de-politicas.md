---
id: politicas-catalogo
titulo: Catálogo completo de políticas
area: politicas
tags: [politicas, catalogo, referencia, xml, indice, standard, extensible]
aplica_a: [apigee-x, apigee-hybrid]
fuente: https://cloud.google.com/apigee/docs/api-platform/reference/policies/reference-overview-policy
revisado: 2026-08-20
---

# Catálogo completo de políticas

Referencia rápida de **todas** las políticas de Apigee vigentes, con su nombre de elemento XML exacto y su tipo real (Standard / Extensible) tal como los agrupa la documentación oficial.

> [!IMPORTANT]
> El nombre del elemento raíz XML es **case-sensitive** y debe escribirse exactamente como aparece aquí. `<VerifyApiKey>` no existe; es `<VerifyAPIKey>`.

## Standard vs. Extensible: no es solo una etiqueta de calidad

> [!IMPORTANT]
> La distinción Standard/Extensible **no es "básico vs. avanzado"**. Es una frontera real con consecuencias de **coste, tipo de entorno y qué proxies pueden ir en un API product**:
>
> - **Políticas Standard**: funcionan en **cualquier tipo de entorno**. Aptas para desarrollo interno y soluciones ligeras.
> - **Políticas Extensible**: solo funcionan en entornos de tipo **Intermediate** y **Comprehensive**. Usar **una sola** política extensible convierte automáticamente el proxy en un **proxy Extensible**, con implicaciones de coste según tu licencia (Pay-as-you-go o Subscription).
> - Un **proxy Standard** (solo políticas Standard) **no puede incluirse en un API product**.
> - En **Pay-as-you-go**, un API product debe incluir **o bien** proxies extensibles con flow hooks, **o bien** políticas extensibles como `VerifyAPIKey` u `OAuthV2`.
>
> Consecuencia práctica: **`VerifyAPIKey`, `OAuthV2` y `Quota` son políticas Extensible.** Casi cualquier API real que autentique y limite tráfico —es decir, casi cualquier API en producción— acaba siendo un proxy Extensible desplegado en un entorno Intermediate o Comprehensive. `SpikeArrest` es la **única** política Standard de traffic management; el resto (`Quota`, todo el bloque de caché) es Extensible.
>
> Regla de Google: **si una política Standard y una Extensible hacen lo mismo, usa la Standard.**

## Clasificación funcional

Las políticas se agrupan en categorías funcionales; cada categoría existe tanto en el lado Standard como en el Extensible cuando aplica:

| Categoría | Propósito |
|---|---|
| **Traffic management** | Controlar el flujo de mensajes: rate limiting, cuotas, caché |
| **Security** | Autenticar, autorizar y proteger el contenido |
| **Mediation** | Manipular activamente los payloads y mensajes |
| **Extension** | Implementar comportamiento personalizado en varios lenguajes |
| **AI** | Gobernar el tráfico hacia modelos de lenguaje (siempre Extensible) |

---

## Políticas Standard (cualquier tipo de entorno)

### Traffic management

| Política | Elemento XML | Qué hace |
|---|---|---|
| SpikeArrest | `<SpikeArrest>` | Suaviza picos instantáneos de tráfico. Protege el runtime, no es contador de negocio |

### Security

| Política | Elemento XML | Qué hace |
|---|---|---|
| AccessControl | `<AccessControl>` | Lista de permitidos/denegados por dirección IP |
| HMAC | `<HMAC>` | Calcula y verifica firmas HMAC |
| DecodeJWT | `<DecodeJWT>` | Decodifica un JWT **sin** verificar la firma |
| VerifyJWT | `<VerifyJWT>` | Verifica firma y claims de un JWT |
| VerifyIAM | `<VerifyIAM>` | Verifica autorización basada en IAM de Google Cloud |

### Mediation

| Política | Elemento XML | Qué hace |
|---|---|---|
| CORS | `<CORS>` | Gestiona cabeceras de Cross-Origin Resource Sharing |
| GraphQL | `<GraphQL>` | Valida y procesa peticiones GraphQL |
| HTTPModifier | `<HTTPModifier>` | Modifica cabeceras HTTP y códigos de estado |
| JSONtoXML | `<JSONtoXML>` | Convierte JSON a XML |
| XMLtoJSON | `<XMLtoJSON>` | Convierte XML a JSON |
| OASValidation | `<OASValidation>` | Valida peticiones/respuestas contra una spec OpenAPI |
| PublishMessage | `<PublishMessage>` | Publica un mensaje en Pub/Sub |
| RaiseFault | `<RaiseFault>` | Genera un fallo explícito con respuesta personalizada |
| ReadPropertySet | `<ReadPropertySet>` | Lee valores de un PropertySet del bundle |
| SOAPMessageValidation | `<MessageValidation>` | Valida estructura de mensajes SOAP/XML contra WSDL/XSD |

### Extension

| Política | Elemento XML | Qué hace |
|---|---|---|
| AssertCondition | `<AssertCondition>` | Evalúa condiciones y lanza fallo si no se cumplen |
| ExternalCallout | `<ExternalCallout>` | Invoca un servicio gRPC externo |

---

## Políticas Extensible (solo entornos Intermediate / Comprehensive)

### Traffic management

| Política | Elemento XML | Qué hace |
|---|---|---|
| Quota | `<Quota>` | Límite de negocio de nº de llamadas por intervalo, por app/producto/developer |
| ResponseCache | `<ResponseCache>` | Cachea la respuesta completa del backend, con lookup y populate integrados |
| LookupCache | `<LookupCache>` | Lee un valor de la caché de propósito general |
| PopulateCache | `<PopulateCache>` | Escribe un valor en la caché |
| InvalidateCache | `<InvalidateCache>` | Elimina entradas de la caché |
| ResetQuota | `<ResetQuota>` | Reinicia el contador de una política Quota |

### Security

| Política | Elemento XML | Qué hace |
|---|---|---|
| VerifyAPIKey | `<VerifyAPIKey>` | Valida una API key y resuelve el contexto de app/producto/developer |
| OAuthV2 | `<OAuthV2>` | Genera, refresca, verifica e invalida tokens OAuth 2.0 |
| GetOAuthV2Info | `<GetOAuthV2Info>` | Recupera metadatos de un token o cliente OAuth |
| SetOAuthV2Info | `<SetOAuthV2Info>` | Añade atributos personalizados a un token |
| DeleteOAuthV2Info | `<DeleteOAuthV2Info>` | Revoca tokens de acceso o refresco |
| RevokeOAuthV2 | `<RevokeOAuthV2>` | Revoca tokens por ID de app o de usuario final |
| GenerateJWT | `<GenerateJWT>` | Crea y firma un JWT |
| GenerateJWS | `<GenerateJWS>` | Crea y firma un JWS (detached o adjunto) |
| VerifyJWS | `<VerifyJWS>` | Verifica la firma de un JWS |
| DecodeJWS | `<DecodeJWS>` | Decodifica un JWS sin verificar |
| BasicAuthentication | `<BasicAuthentication>` | Codifica/decodifica credenciales HTTP Basic |
| JSONThreatProtection | `<JSONThreatProtection>` | Protege contra ataques estructurales en JSON |
| XMLThreatProtection | `<XMLThreatProtection>` | Protege contra ataques estructurales en XML (incl. entity expansion) |
| RegularExpressionProtection | `<RegularExpressionProtection>` | Bloquea patrones maliciosos (SQLi, XSS) mediante regex |
| SAMLAssertion | `<SAMLAssertion>` | Genera y valida aserciones SAML |

> [!NOTE]
> Nótese la asimetría JWT/JWS: para **JWT**, `VerifyJWT` y `DecodeJWT` son **Standard** pero `GenerateJWT` es **Extensible**. Para **JWS**, las tres operaciones (`GenerateJWS`, `VerifyJWS`, `DecodeJWS`) son **Extensible**. Si solo necesitas *verificar* JWT de un IdP externo, tu proxy puede seguir siendo Standard en ese aspecto — pero en la práctica casi siempre necesitarás `VerifyAPIKey` u `OAuthV2` de todos modos, que sí son Extensible.

### Mediation

| Política | Elemento XML | Qué hace |
|---|---|---|
| AssignMessage | `<AssignMessage>` | Crea y modifica mensajes, cabeceras, payloads y variables. La navaja suiza |
| ExtractVariables | `<ExtractVariables>` | Extrae datos de un mensaje a variables (JSONPath, XPath, regex, params) |
| AccessEntity | `<AccessEntity>` | Recupera entidades del perfil (app, developer, producto) como XML |
| KeyValueMapOperations | `<KeyValueMapOperations>` | Lee, escribe y borra entradas de un KVM |
| MonetizationLimitsCheck | `<MonetizationLimitsCheck>` | Aplica límites de los planes de monetización |
| ParsePayload | `<ParsePayload>` | Parsea el payload a estructuras accesibles |
| XSLTransform (`<XSL>`) | `<XSL>` | Aplica una transformación XSLT. Usa el procesador Saxon (XSLT 1.0/2.0); no soporta `<xsl:include>` ni `<xsl:import>` |
| ParseDialogflowRequest | `<ParseDialogflowRequest>` | Parsea una petición entrante de Dialogflow |
| SetDialogflowResponse | `<SetDialogflowResponse>` | Construye la respuesta hacia Dialogflow |

### Extension

| Política | Elemento XML | Qué hace |
|---|---|---|
| ServiceCallout | `<ServiceCallout>` | Llama a un servicio HTTP externo desde el flujo |
| FlowCallout | `<FlowCallout>` | Invoca un shared flow |
| JavaScript | `<Javascript>` | Ejecuta código JavaScript personalizado |
| JavaCallout | `<JavaCallout>` | Ejecuta código Java empaquetado en un JAR |
| PythonScript | `<Script>` | Ejecuta un script Python (X, hybrid y Edge; puede no estar en todos los planes) |
| MessageLogging | `<MessageLogging>` | Envía logs a syslog o Cloud Logging |
| DataCapture | `<DataCapture>` | Captura datos de petición/respuesta para analytics |
| IntegrationCallout | `<IntegrationCallout>` | Invoca un flujo de Application Integration |
| SetIntegrationRequest | `<SetIntegrationRequest>` | Configura los parámetros de la petición de integración |
| TraceCapture | `<TraceCapture>` | **(Preview / Pre-GA)** Añade variables personalizadas a los spans del trazado distribuido |

### AI (siempre Extensible)

| Política | Elemento XML | Qué hace |
|---|---|---|
| SemanticCacheLookup | `<SemanticCacheLookup>` | Busca en caché respuestas semánticamente similares mediante embeddings |
| SemanticCachePopulate | `<SemanticCachePopulate>` | Almacena la respuesta del modelo en la caché semántica |
| LLMTokenQuota | `<LLMTokenQuota>` | Aplica cuota sobre el consumo de **tokens** de LLM, no de llamadas |
| PromptTokenLimit | `<PromptTokenLimit>` | Limita el número de tokens del prompt de entrada |
| SanitizeUserPrompt | `<SanitizeUserPrompt>` | Filtra el prompt del usuario vía Model Armor (prompt injection, jailbreak, datos sensibles) |
| SanitizeModelResponse | `<SanitizeModelResponse>` | Sanea la salida del modelo antes de devolverla |

Detalle: [Traffic Management](01-traffic-management.md) · [Seguridad](02-seguridad.md) · [Mediación](03-mediacion.md) · [Extensión](04-extension.md) · [Políticas de IA](05-politicas-ai.md)

---

## Políticas retiradas o exclusivas de Apigee Edge

> [!CAUTION]
> Estas políticas **no existen o están retiradas en Apigee X**. Si las ves en un ejemplo o tutorial antiguo, no las uses en un proxy nuevo.

| Política | Estado | Alternativa |
|---|---|---|
| `ConcurrentRateLimit` | **Deprecada** el 15/07/2020, **retirada** de Private Cloud en la versión 4.50.00 (15/07/2021). Su arquitectura afectaba al rendimiento de las APIs | `SpikeArrest` y/o `Quota`, combinadas con encadenamiento de proxies o shared flows |
| `StatisticsCollector` | Predecesora de `DataCapture` en Edge | `DataCapture` |
| `OAuthv1.0a`, `GetOAuthV1Info`, `DeleteOAuthV1Info` | Deprecadas y retiradas en Edge (Cloud y Private Cloud v4.50.00). ⚠️ Fechas pendientes de verificación: la versión anterior de esta tabla daba una retirada (15/11/2018) anterior a la deprecación (15/07/2020) | Políticas `OAuthV2` |

> [!NOTE]
> **Correcciones (2026-10-22).** Esta tabla incluía antes `MessageValidation` y `Script` (Python) como políticas ausentes de Apigee X. Las dos **existen** en X/hybrid: `<MessageValidation>` (en la UI, "SOAPMessageValidation"; ver [referencia](referencia/message-validation.md)) y `<Script>` (PythonScript, con Jython 2.5.2, que puede no estar en todos los planes; ver [referencia](referencia/python-script.md)).

---

## Cómo elegir: política vs. código

Regla de Google, en orden de preferencia:

```
1. ¿Existe una política que lo haga?            → úsala
2. ¿Standard y Extensible hacen lo mismo?       → usa la Standard
3. ¿AssignMessage + ExtractVariables bastan?    → úsalas
4. ¿Necesitas lógica real?                      → JavaScript
5. ¿El rendimiento es crítico?                  → JavaCallout
6. Python                                        → evitar (y no existe en X)
```

Las políticas nativas están **endurecidas, optimizadas y soportadas**. El código personalizado no.

## Atributos comunes

Todas las políticas aceptan:

```xml
<NombrePolitica name="XX-Nombre" enabled="true" continueOnError="false">
    <DisplayName>Descripción legible</DisplayName>
    ...
</NombrePolitica>
```

| Atributo | Efecto |
|---|---|
| `name` | Identificador. **Debe coincidir con el nombre del archivo `.xml`** |
| `enabled` | `false` desactiva sin borrar |
| `continueOnError` | `true` evita el error flow; deja `<prefijo>.<name>.failed = true` |

Convención de prefijos recomendada en [convenciones de nombres](../08-mejores-practicas/02-convenciones-de-nombres.md).

## Fuentes

- <https://cloud.google.com/apigee/docs/api-platform/reference/policies/reference-overview-policy> (consultada directamente, contenido completo)
- <https://cloud.google.com/apigee/docs/api-platform/reference/policies/xsl-transform-policy>
- <https://cloud.google.com/apigee/docs/api-platform/reference/policies/trace-capture-policy>
- <https://cloud.google.com/apigee/docs/api-platform/develop/policy-attachment-and-enforcement>
- <https://docs.apigee.com/release/deprecated-features> (ConcurrentRateLimit y OAuth v1)
