---
id: politicas-catalogo
titulo: Catálogo completo de políticas
area: politicas
tags: [politicas, catalogo, referencia, xml, indice]
aplica_a: [apigee-x, apigee-hybrid]
fuente: https://cloud.google.com/apigee/docs/api-platform/reference/policies/reference-overview-policy
revisado: 2026-08-20
---

# Catálogo completo de políticas

Referencia rápida de **todas** las políticas de Apigee, con su nombre de elemento XML exacto.

> [!IMPORTANT]
> El nombre del elemento raíz XML es **case-sensitive** y debe escribirse exactamente como aparece aquí. `<VerifyApiKey>` no existe; es `<VerifyAPIKey>`.

## Clasificación funcional

Apigee agrupa las políticas en cuatro categorías funcionales, más una categoría de IA:

| Categoría | Propósito |
|---|---|
| **Traffic management** | Controlar el flujo de mensajes: rate limiting, cuotas, caché |
| **Security** | Autenticar, autorizar y proteger el contenido |
| **Mediation** | Manipular activamente los payloads y mensajes |
| **Extension** | Implementar comportamiento personalizado en varios lenguajes |
| **AI** | Gobernar el tráfico hacia modelos de lenguaje |

Ortogonalmente, Apigee distingue entre políticas **estándar** y **extensibles** (estas últimas ofrecen más funcionalidad y pueden tener implicaciones de coste o rendimiento distintas).

---

## Traffic management

| Política | Elemento XML | Qué hace |
|---|---|---|
| Quota | `<Quota>` | Límite de negocio de nº de llamadas por intervalo, por app/producto/developer |
| SpikeArrest | `<SpikeArrest>` | Suaviza picos instantáneos de tráfico. Protege el runtime, no es contador de negocio |
| ResponseCache | `<ResponseCache>` | Cachea la respuesta completa del backend, con lookup y populate integrados |
| LookupCache | `<LookupCache>` | Lee un valor de la caché de propósito general |
| PopulateCache | `<PopulateCache>` | Escribe un valor en la caché |
| InvalidateCache | `<InvalidateCache>` | Elimina entradas de la caché |
| ConcurrentRateLimit | `<ConcurrentRateLimit>` | Limita conexiones concurrentes hacia el backend |
| ResetQuota | `<ResetQuota>` | Reinicia el contador de una política Quota |
| MonetizationLimitsCheck | `<MonetizationLimitsCheck>` | Aplica límites de los planes de monetización |

Detalle: [Traffic Management](01-traffic-management.md)

---

## Security

| Política | Elemento XML | Qué hace |
|---|---|---|
| VerifyAPIKey | `<VerifyAPIKey>` | Valida una API key y resuelve el contexto de app/producto/developer |
| OAuthV2 | `<OAuthV2>` | Genera, refresca, verifica e invalida tokens OAuth 2.0 |
| GetOAuthV2Info | `<GetOAuthV2Info>` | Recupera metadatos de un token o cliente OAuth |
| SetOAuthV2Info | `<SetOAuthV2Info>` | Añade atributos personalizados a un token |
| DeleteOAuthV2Info | `<DeleteOAuthV2Info>` | Revoca tokens de acceso o refresco |
| RevokeOAuthV2 | `<RevokeOAuthV2>` | Revoca tokens por ID de app o de usuario final |
| GenerateJWT | `<GenerateJWT>` | Crea y firma un JWT |
| VerifyJWT | `<VerifyJWT>` | Verifica firma y claims de un JWT |
| DecodeJWT | `<DecodeJWT>` | Decodifica un JWT **sin** verificar la firma |
| GenerateJWS | `<GenerateJWS>` | Crea y firma un JWS (detached o adjunto) |
| VerifyJWS | `<VerifyJWS>` | Verifica la firma de un JWS |
| DecodeJWS | `<DecodeJWS>` | Decodifica un JWS sin verificar |
| BasicAuthentication | `<BasicAuthentication>` | Codifica/decodifica credenciales HTTP Basic |
| HMAC | `<HMAC>` | Calcula y verifica firmas HMAC |
| AccessControl | `<AccessControl>` | Lista de permitidos/denegados por dirección IP |
| AccessEntity | `<AccessEntity>` | Recupera entidades del perfil (app, developer, producto) como XML |
| VerifyIAM | `<VerifyIAM>` | Verifica autorización basada en IAM de Google Cloud |
| JSONThreatProtection | `<JSONThreatProtection>` | Protege contra ataques estructurales en JSON |
| XMLThreatProtection | `<XMLThreatProtection>` | Protege contra ataques estructurales en XML (incl. entity expansion) |
| RegularExpressionProtection | `<RegularExpressionProtection>` | Bloquea patrones maliciosos (SQLi, XSS) mediante regex |
| SAMLAssertion | `<SAMLAssertion>` | Genera y valida aserciones SAML |

Detalle: [Seguridad](02-seguridad.md)

---

## Mediation

| Política | Elemento XML | Qué hace |
|---|---|---|
| AssignMessage | `<AssignMessage>` | Crea y modifica mensajes, cabeceras, payloads y variables. La navaja suiza |
| ExtractVariables | `<ExtractVariables>` | Extrae datos de un mensaje a variables (JSONPath, XPath, regex, params) |
| JSONtoXML | `<JSONtoXML>` | Convierte JSON a XML |
| XMLtoJSON | `<XMLtoJSON>` | Convierte XML a JSON |
| XSL / XSLTransform | `<XSL>` | Aplica una transformación XSLT |
| CORS | `<CORS>` | Gestiona cabeceras de Cross-Origin Resource Sharing |
| HTTPModifier | `<HTTPModifier>` | Modifica cabeceras HTTP y códigos de estado |
| OASValidation | `<OASValidation>` | Valida peticiones/respuestas contra una spec OpenAPI |
| SOAPMessageValidation | `<SOAPMessageValidation>` | Valida estructura de mensajes SOAP contra WSDL/XSD |
| GraphQL | `<GraphQL>` | Valida y procesa peticiones GraphQL |
| RaiseFault | `<RaiseFault>` | Genera un fallo explícito con respuesta personalizada |
| AssertCondition | `<AssertCondition>` | Evalúa condiciones y lanza fallo si no se cumplen |
| ParsePayload | `<ParsePayload>` | Parsea el payload a estructuras accesibles |
| KeyValueMapOperations | `<KeyValueMapOperations>` | Lee, escribe y borra entradas de un KVM |
| ReadPropertySet | `<ReadPropertySet>` | Lee valores de un PropertySet del bundle |
| MessageValidation | `<MessageValidation>` | Validación genérica de mensajes (XSD/WSDL/JSON schema) |

Detalle: [Mediación](03-mediacion.md)

---

## Extension

| Política | Elemento XML | Qué hace |
|---|---|---|
| ServiceCallout | `<ServiceCallout>` | Llama a un servicio HTTP externo desde el flujo |
| ExternalCallout | `<ExternalCallout>` | Invoca un servicio gRPC externo |
| FlowCallout | `<FlowCallout>` | Invoca un shared flow |
| JavaScript | `<Javascript>` | Ejecuta código JavaScript personalizado |
| JavaCallout | `<JavaCallout>` | Ejecuta código Java empaquetado en un JAR |
| PythonScript | `<Script>` | ⚠️ **Solo Edge.** Ejecuta Python. No disponible en Apigee X |
| MessageLogging | `<MessageLogging>` | Envía logs a syslog o Cloud Logging |
| DataCapture | `<DataCapture>` | Captura datos de petición/respuesta para analytics |
| StatisticsCollector | `<StatisticsCollector>` | Recoge datos personalizados para analytics (predecesor de DataCapture) |
| IntegrationCallout | `<IntegrationCallout>` | Invoca un flujo de Application Integration |
| SetIntegrationRequest | `<SetIntegrationRequest>` | Configura los parámetros de la petición de integración |
| PublishMessage | `<PublishMessage>` | Publica un mensaje en Pub/Sub |

Detalle: [Extensión](04-extension.md)

---

## Políticas de IA

| Política | Elemento XML | Qué hace |
|---|---|---|
| SemanticCacheLookup | `<SemanticCacheLookup>` | Busca en caché respuestas semánticamente similares mediante embeddings |
| SemanticCachePopulate | `<SemanticCachePopulate>` | Almacena la respuesta del modelo en la caché semántica |
| LLMTokenQuota | `<LLMTokenQuota>` | Aplica cuota sobre el consumo de **tokens** de LLM, no de llamadas |
| PromptTokenLimit | `<PromptTokenLimit>` | Limita el número de tokens del prompt de entrada |
| SanitizeUserPrompt | `<SanitizeUserPrompt>` | Filtra el prompt del usuario vía Model Armor (prompt injection, jailbreak, datos sensibles) |
| SanitizeModelResponse | `<SanitizeModelResponse>` | Sanea la salida del modelo antes de devolverla |

Detalle: [Políticas de IA](05-politicas-ai.md) y [Apigee como AI Gateway](../07-ai-gateway/01-apigee-como-ai-gateway.md)

---

## Cómo elegir: política vs. código

Regla de Google, en orden de preferencia:

```
1. ¿Existe una política que lo haga?            → úsala
2. ¿AssignMessage + ExtractVariables bastan?    → úsalas
3. ¿Necesitas lógica real?                      → JavaScript
4. ¿El rendimiento es crítico?                  → JavaCallout
5. Python                                        → evitar (y no existe en X)
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

- <https://cloud.google.com/apigee/docs/api-platform/reference/policies/reference-overview-policy>
- <https://cloud.google.com/apigee/docs/api-platform/develop/policy-attachment-and-enforcement>
