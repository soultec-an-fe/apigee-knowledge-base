---
id: politicas-referencia-indice
titulo: Referencia de políticas — índice
area: politicas
tags: [indice, politicas, referencia, standard, extensible, edge]
aplica_a: [apigee-x, apigee-hybrid, apigee-edge]
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/reference-overview-policy
revisado: 2026-10-22
---

# Referencia de políticas — índice

Un archivo por política, todos con la misma estructura:

- tipo y ediciones;
- sintaxis completa;
- atributos y elementos;
- variables de flujo;
- errores de runtime y de despliegue;
- ejemplos propios;
- diferencias en Apigee Edge;
- antipatrones;
- fuentes consultadas.

Para elegir política por caso de uso, empieza por el [catálogo](../00-catalogo-de-politicas.md). Este índice sirve para ir directo a la referencia.

**Columnas:**

- **Tipo:** **S** = Standard, se despliega en cualquier tipo de entorno. **E** = Extensible, puede tener coste o requisitos de licencia. Esta clasificación solo existe en Apigee X y hybrid. **—** = política solo de Edge.
- **Ediciones:** **X** = Apigee X · **H** = hybrid · **Edge** = Apigee Edge.

## Gestión de tráfico

| Política | Elemento XML | Tipo | Ediciones |
|---|---|---|---|
| [SpikeArrest](spike-arrest.md) | `<SpikeArrest>` | S | X · H · Edge |
| [Quota](quota.md) | `<Quota>` | E | X · H · Edge |
| [ResetQuota](reset-quota.md) | `<ResetQuota>` | E | X · H · Edge |
| [ResponseCache](response-cache.md) | `<ResponseCache>` | E | X · H · Edge |
| [PopulateCache](populate-cache.md) | `<PopulateCache>` | E | X · H · Edge |
| [LookupCache](lookup-cache.md) | `<LookupCache>` | E | X · H · Edge |
| [InvalidateCache](invalidate-cache.md) | `<InvalidateCache>` | E | X · H · Edge |
| [MonetizationLimitsCheck](monetization-limits-check.md) | `<MonetizationLimitsCheck>` | E | X · H · Edge |

Concepto compartido por las cuatro políticas de caché: [claves de caché](claves-de-cache.md).

## Seguridad

| Política | Elemento XML | Tipo | Ediciones |
|---|---|---|---|
| [VerifyAPIKey](verify-api-key.md) | `<VerifyAPIKey>` | E | X · H · Edge |
| [OAuthV2](oauthv2.md) | `<OAuthV2>` | E | X · H · Edge |
| [GetOAuthV2Info](get-oauth-v2-info.md) | `<GetOAuthV2Info>` | E | X · H · Edge |
| [SetOAuthV2Info](set-oauth-v2-info.md) | `<SetOAuthV2Info>` | E | X · H · Edge |
| [DeleteOAuthV2Info](delete-oauth-v2-info.md) | `<DeleteOAuthV2Info>` | E | X · H · Edge |
| [RevokeOAuthV2](revoke-oauth-v2.md) | `<RevokeOAuthV2>` | E | X · H · Edge |
| [VerifyIAM](verify-iam.md) | `<VerifyIAM>` | S | X |
| [GenerateJWT](generate-jwt.md) | `<GenerateJWT>` | E | X · H · Edge |
| [VerifyJWT](verify-jwt.md) | `<VerifyJWT>` | S | X · H · Edge |
| [DecodeJWT](decode-jwt.md) | `<DecodeJWT>` | S | X · H · Edge |
| [GenerateJWS](generate-jws.md) | `<GenerateJWS>` | E | X · H · Edge |
| [VerifyJWS](verify-jws.md) | `<VerifyJWS>` | E | X · H · Edge |
| [DecodeJWS](decode-jws.md) | `<DecodeJWS>` | E | X · H · Edge |
| [BasicAuthentication](basic-authentication.md) | `<BasicAuthentication>` | E | X · H · Edge |
| [AccessControl](access-control.md) | `<AccessControl>` | S | X · H · Edge |
| [AccessEntity](access-entity.md) | `<AccessEntity>` | E | X · H · Edge |
| [HMAC](hmac.md) | `<HMAC>` | S | X · H · Edge |
| [JSONThreatProtection](json-threat-protection.md) | `<JSONThreatProtection>` | E | X · H · Edge |
| [XMLThreatProtection](xml-threat-protection.md) | `<XMLThreatProtection>` | E | X · H · Edge |
| [RegularExpressionProtection](regular-expression-protection.md) | `<RegularExpressionProtection>` | E | X · H · Edge |
| [GenerateSAMLAssertion](generate-saml-assertion.md) | `<GenerateSAMLAssertion>` | E | X · H · Edge |
| [ValidateSAMLAssertion](validate-saml-assertion.md) | `<ValidateSAMLAssertion>` | E | X · H · Edge |

Concepto compartido por las seis políticas JWT/JWS: [JWT y JWS](jwt-jws-conceptos.md).

## Mediación

| Política | Elemento XML | Tipo | Ediciones |
|---|---|---|---|
| [AssignMessage](assign-message.md) | `<AssignMessage>` | E | X · H · Edge |
| [ExtractVariables](extract-variables.md) | `<ExtractVariables>` | E | X · H · Edge |
| [JSONToXML](json-xml.md) | `<JSONToXML>` | S | X · H · Edge |
| [XMLToJSON](xml-json.md) | `<XMLToJSON>` | S | X · H · Edge |
| [XSLTransform](xsl-transform.md) | `<XSL>` | E | X · H · Edge |
| [SOAPMessageValidation](message-validation.md) | `<MessageValidation>` | S | X · H · Edge |
| [OASValidation](oas-validation.md) | `<OASValidation>` | S | X · H · Edge |
| [CORS](cors.md) | `<CORS>` | S | X · H |
| [RaiseFault](raise-fault.md) | `<RaiseFault>` | S | X · H · Edge |
| [AssertCondition](assert-condition.md) | `<AssertCondition>` | S | X · H |
| [HTTPModifier](http-modifier.md) | `<HTTPModifier>` | S | X · H |
| [GraphQL](graphql.md) | `<GraphQL>` | S | X · H |
| [KeyValueMapOperations](key-value-map-operations.md) | `<KeyValueMapOperations>` | E | X · H · Edge |
| [ReadPropertySet](read-property-set.md) | `<ReadPropertySet>` | S | X · H |
| [ParsePayload](parse-payload.md) | `<ParsePayload>` | E | X · H |

## Extensión y código propio

| Política | Elemento XML | Tipo | Ediciones |
|---|---|---|---|
| [ServiceCallout](service-callout.md) | `<ServiceCallout>` | E | X · H · Edge |
| [ExternalCallout](external-callout.md) | `<ExternalCallout>` | S | X · H |
| [FlowCallout](flow-callout.md) | `<FlowCallout>` | E | X · H · Edge |
| [JavaScript](javascript.md) | `<Javascript>` | E | X · H · Edge |
| [JavaCallout](java-callout.md) | `<JavaCallout>` | E | X · H · Edge |
| [PythonScript](python-script.md) | `<Script>` | E | X · H · Edge |
| [MessageLogging](message-logging.md) | `<MessageLogging>` | E | X · H · Edge |
| [DataCapture](data-capture.md) | `<DataCapture>` | E | X · H |
| [PublishMessage](publish-message.md) | `<PublishMessage>` | S | X · H |
| [TraceCapture](trace-capture.md) (Preview) | `<TraceCapture>` | E | X · H |

## Integraciones de Google Cloud

| Política | Elemento XML | Tipo | Ediciones |
|---|---|---|---|
| [SetIntegrationRequest](set-integration-request.md) | `<SetIntegrationRequest>` | E | X · H |
| [IntegrationCallout](integration-callout.md) | `<IntegrationCallout>` | E | X · H |
| [ParseDialogflowRequest](parse-dialogflow-request.md) | `<ParseDialogflowRequest>` | E | X · H |
| [SetDialogflowResponse](set-dialogflow-response.md) | `<SetDialogflowResponse>` | E | X · H |

## IA (AI Gateway)

| Política | Elemento XML | Tipo | Ediciones |
|---|---|---|---|
| [LLMTokenQuota](llm-token-quota.md) | `<LLMTokenQuota>` | E | X · H |
| [PromptTokenLimit](prompt-token-limit.md) | `<PromptTokenLimit>` | E | X · H |
| [SemanticCacheLookup](semantic-cache-lookup.md) | `<SemanticCacheLookup>` | E | X · H |
| [SemanticCachePopulate](semantic-cache-populate.md) | `<SemanticCachePopulate>` | E | X · H |
| [SanitizeUserPrompt](sanitize-user-prompt.md) | `<SanitizeUserPrompt>` | E | X · H |
| [SanitizeModelResponse](sanitize-llm-response.md) | `<SanitizeModelResponse>` | E | X · H |

## Solo Apigee Edge

| Política | Elemento XML | Estado | Sustituta en X |
|---|---|---|---|
| [ExtensionCallout](extension-callout.md) | `<ConnectorCallout>` | Vigente en Edge | ServiceCallout, ExternalCallout, PublishMessage, MessageLogging |
| [LDAP](ldap.md) | `<Ldap>` | Solo Private Cloud | Identidad externa (OIDC/SAML) + VerifyJWT u OAuthV2 |
| [StatisticsCollector](statistics-collector.md) | `<StatisticsCollector>` | Vigente en Edge | DataCapture |
| [ConcurrentRateLimit](concurrent-rate-limit.md) | `<ConcurrentRatelimit>` | **Retirada** (2021) | SpikeArrest + Quota |

Las políticas OAuth v1.0a (`OAuthV1`, `GetOAuthV1Info`, `DeleteOAuthV1Info`) están retiradas y no tienen archivo propio. Ver el [catálogo](../00-catalogo-de-politicas.md).

## Fuentes

- Policy reference overview — Apigee X/hybrid: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/reference-overview-policy>.
- Cada archivo enlazado cita sus propias páginas oficiales, con la fecha de consulta.
