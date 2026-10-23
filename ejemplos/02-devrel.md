---
id: ejemplos-devrel
titulo: Mapa de ejemplos — apigee/devrel
area: ejemplos
tags: [ejemplos, devrel, samples]
aplica_a: [apigee-x, apigee-hybrid]
fuente: https://github.com/apigee/devrel
revisado: 2026-10-23
---

<!-- Archivo generado por scripts/generar_mapa_ejemplos.py. No editar a mano. -->

# Mapa de ejemplos — apigee/devrel

> **Fecha de corte: 2026-10-23.** Ediciones: Apigee X y hybrid (algunas herramientas también Edge). Repositorio: <https://github.com/apigee/devrel>.

Implementaciones de referencia (`references/`), herramientas (`tools/`) y laboratorios (`labs/`) del equipo de DevRel de Apigee (Apache 2.0). Google aclara que no es un producto con soporte oficial.

La columna **Políticas** se extrae automáticamente de los XML de cada bundle (`scripts/mapa_ejemplos.py`); enlaza con la referencia de cada política. Una celda vacía indica que el ejemplo no trae bundles (scripts, Terraform, notebooks, portales).

## Arquitectura

| Ejemplo | Qué muestra | Políticas | En este repo |
|---|---|---|---|
| [`references/data-api`](https://github.com/apigee/devrel/tree/main/references/data-api) | Consumo de datos de una plataforma de datos a través de Apigee. | [AssignMessage](../docs/02-politicas/referencia/assign-message.md), [CORS](../docs/02-politicas/referencia/cors.md), [Javascript](../docs/02-politicas/referencia/javascript.md), [Quota](../docs/02-politicas/referencia/quota.md), [RaiseFault](../docs/02-politicas/referencia/raise-fault.md), [RegularExpressionProtection](../docs/02-politicas/referencia/regular-expression-protection.md), [ResponseCache](../docs/02-politicas/referencia/response-cache.md), [VerifyAPIKey](../docs/02-politicas/referencia/verify-api-key.md) | [01-anatomia-api-proxy](../docs/01-proxies/01-anatomia-api-proxy.md) |
| [`references/firestore-facade`](https://github.com/apigee/devrel/tree/main/references/firestore-facade) | Caché o almacenamiento de largo plazo con Cloud Firestore. | [AssignMessage](../docs/02-politicas/referencia/assign-message.md), [FlowCallout](../docs/02-politicas/referencia/flow-callout.md), [Javascript](../docs/02-politicas/referencia/javascript.md), [ServiceCallout](../docs/02-politicas/referencia/service-callout.md) | [04-caching-y-persistencia](../docs/05-operacion/04-caching-y-persistencia.md) |
| [`references/product-recommendations`](https://github.com/apigee/devrel/tree/main/references/product-recommendations) | API inteligente con BigQuery ML y Cloud Spanner. | [AssignMessage](../docs/02-politicas/referencia/assign-message.md), [CORS](../docs/02-politicas/referencia/cors.md), [ExtractVariables](../docs/02-politicas/referencia/extract-variables.md), [InvalidateCache](../docs/02-politicas/referencia/invalidate-cache.md), [Javascript](../docs/02-politicas/referencia/javascript.md), [LookupCache](../docs/02-politicas/referencia/lookup-cache.md), [PopulateCache](../docs/02-politicas/referencia/populate-cache.md), [Quota](../docs/02-politicas/referencia/quota.md), [RaiseFault](../docs/02-politicas/referencia/raise-fault.md), [ResponseCache](../docs/02-politicas/referencia/response-cache.md), [ServiceCallout](../docs/02-politicas/referencia/service-callout.md), [VerifyAPIKey](../docs/02-politicas/referencia/verify-api-key.md) | [01-anatomia-api-proxy](../docs/01-proxies/01-anatomia-api-proxy.md) |

## DevOps

| Ejemplo | Qué muestra | Políticas | En este repo |
|---|---|---|---|
| [`references/cicd-pipeline`](https://github.com/apigee/devrel/tree/main/references/cicd-pipeline) | Pipeline CI/CD con el plugin Maven, en Jenkins o Cloud Build. | [AssignMessage](../docs/02-politicas/referencia/assign-message.md), [Javascript](../docs/02-politicas/referencia/javascript.md), [RaiseFault](../docs/02-politicas/referencia/raise-fault.md) | [03-cicd-github-actions](../docs/06-devops/03-cicd-github-actions.md) |
| [`references/cicd-sharedflow-pipeline`](https://github.com/apigee/devrel/tree/main/references/cicd-sharedflow-pipeline) | Pipeline CI/CD para shared flows. | [AssignMessage](../docs/02-politicas/referencia/assign-message.md), [FlowCallout](../docs/02-politicas/referencia/flow-callout.md), [VerifyAPIKey](../docs/02-politicas/referencia/verify-api-key.md) | [03-cicd-github-actions](../docs/06-devops/03-cicd-github-actions.md) |
| [`references/openapi-mock`](https://github.com/apigee/devrel/tree/main/references/openapi-mock) | Proxy *mock* generado desde una especificación OpenAPI 3. | [AssignMessage](../docs/02-politicas/referencia/assign-message.md), [CORS](../docs/02-politicas/referencia/cors.md), [Javascript](../docs/02-politicas/referencia/javascript.md), [OASValidation](../docs/02-politicas/referencia/oas-validation.md) | [oas-validation](../docs/02-politicas/referencia/oas-validation.md) |
| [`references/proxy-template`](https://github.com/apigee/devrel/tree/main/references/proxy-template) | Plantillas para generar proxies con seguridad, tráfico y manejo de errores. | [FlowCallout](../docs/02-politicas/referencia/flow-callout.md), [Javascript](../docs/02-politicas/referencia/javascript.md) | [01-diseno-y-desarrollo](../docs/08-mejores-practicas/01-diseno-y-desarrollo.md) |

## Extensión

| Ejemplo | Qué muestra | Políticas | En este repo |
|---|---|---|---|
| [`references/java-callout`](https://github.com/apigee/devrel/tree/main/references/java-callout) | Proyecto de referencia de una extensión Java. | [JavaCallout](../docs/02-politicas/referencia/java-callout.md) | [java-callout](../docs/02-politicas/referencia/java-callout.md) |
| [`references/js-callout`](https://github.com/apigee/devrel/tree/main/references/js-callout) | Buenas prácticas para escribir JavaScript en Apigee. | [Javascript](../docs/02-politicas/referencia/javascript.md) | [javascript](../docs/02-politicas/referencia/javascript.md) |

## Herramientas

| Ejemplo | Qué muestra | Políticas | En este repo |
|---|---|---|---|
| [`tools/apigee-config-diff`](https://github.com/apigee/devrel/tree/main/tools/apigee-config-diff) | Detecta y despliega solo los cambios de configuración. |  | [02-herramientas-cli](../docs/06-devops/02-herramientas-cli.md) |
| [`tools/apigee-edge-to-x-migration-tool`](https://github.com/apigee/devrel/tree/main/tools/apigee-edge-to-x-migration-tool) | Acelerador de migración de Edge a X (Node.js). |  | [02-ediciones-y-comparativa](../docs/00-fundamentos/02-ediciones-y-comparativa.md) |
| [`tools/apigee-envoy-quickstart`](https://github.com/apigee/devrel/tree/main/tools/apigee-envoy-quickstart) | Despliegues de ejemplo del adapter for Envoy. |  | [04-envoy-adapter](../docs/16-adaptadores/04-envoy-adapter.md) |
| [`tools/apigee-openlegacy`](https://github.com/apigee/devrel/tree/main/tools/apigee-openlegacy) | Integración de OpenLegacy, Apigee y Cloud Run. | [AssignMessage](../docs/02-politicas/referencia/assign-message.md), [FlowCallout](../docs/02-politicas/referencia/flow-callout.md), [KeyValueMapOperations](../docs/02-politicas/referencia/key-value-map-operations.md), [SpikeArrest](../docs/02-politicas/referencia/spike-arrest.md), [VerifyAPIKey](../docs/02-politicas/referencia/verify-api-key.md) | [05-target-endpoints-y-servidores](../docs/01-proxies/05-target-endpoints-y-servidores.md) |
| [`tools/apigee-proxy-modifier-validator`](https://github.com/apigee/devrel/tree/main/tools/apigee-proxy-modifier-validator) | Modificaciones masivas de proxies al migrar a variantes nuevas de Apigee. |  | [02-ediciones-y-comparativa](../docs/00-fundamentos/02-ediciones-y-comparativa.md) |
| [`tools/apigee-sackmesser`](https://github.com/apigee/devrel/tree/main/tools/apigee-sackmesser) | Utilidad unificada de despliegue para Edge, hybrid y X. | [AssignMessage](../docs/02-politicas/referencia/assign-message.md), [OASValidation](../docs/02-politicas/referencia/oas-validation.md) | [02-herramientas-cli](../docs/06-devops/02-herramientas-cli.md) |
| [`tools/apigee-x-trial-provision`](https://github.com/apigee/devrel/tree/main/tools/apigee-x-trial-provision) | Script de aprovisionamiento de una organización de prueba de Apigee X. |  | [04-organizaciones-entornos-grupos](../docs/00-fundamentos/04-organizaciones-entornos-grupos.md) |
| [`tools/decrypt-hybrid-assets`](https://github.com/apigee/devrel/tree/main/tools/decrypt-hybrid-assets) | Utilidad de rescate para descifrar proxies y shared flows de hybrid. |  | [04-operacion-y-troubleshooting](../docs/11-hybrid/04-operacion-y-troubleshooting.md) |
| [`tools/endpoints-oas-importer`](https://github.com/apigee/devrel/tree/main/tools/endpoints-oas-importer) | Genera proxies desde especificaciones con extensiones de Cloud Endpoints. |  | [02-herramientas-cli](../docs/06-devops/02-herramientas-cli.md) |
| [`tools/grpc-http-gateway-generator`](https://github.com/apigee/devrel/tree/main/tools/grpc-http-gateway-generator) | Genera gateways HTTP para exponer servicios gRPC. | [AssignMessage](../docs/02-politicas/referencia/assign-message.md), [HTTPModifier](../docs/02-politicas/referencia/http-modifier.md), [Javascript](../docs/02-politicas/referencia/javascript.md) | [05-target-endpoints-y-servidores](../docs/01-proxies/05-target-endpoints-y-servidores.md) |
| [`tools/hybrid-quickstart`](https://github.com/apigee/devrel/tree/main/tools/hybrid-quickstart) | Configuración rápida de hybrid sobre GKE. |  | [02-instalacion](../docs/11-hybrid/02-instalacion.md) |
| [`tools/oas-apigee-mock`](https://github.com/apigee/devrel/tree/main/tools/oas-apigee-mock) | Genera un bundle con respuestas *mock* a partir de una especificación. | [AssignMessage](../docs/02-politicas/referencia/assign-message.md), [OASValidation](../docs/02-politicas/referencia/oas-validation.md), [VerifyAPIKey](../docs/02-politicas/referencia/verify-api-key.md) | [02-herramientas-cli](../docs/06-devops/02-herramientas-cli.md) |
| [`tools/pipeline-linter`](https://github.com/apigee/devrel/tree/main/tools/pipeline-linter) | *Linter* para grupos de proyectos de Apigee. |  | [03-cicd-github-actions](../docs/06-devops/03-cicd-github-actions.md) |
| [`tools/pipeline-runner`](https://github.com/apigee/devrel/tree/main/tools/pipeline-runner) | Construye y prueba grupos de proyectos de Apigee. |  | [03-cicd-github-actions](../docs/06-devops/03-cicd-github-actions.md) |
| [`tools/proxy-endpoint-unifier`](https://github.com/apigee/devrel/tree/main/tools/proxy-endpoint-unifier) | Une o separa ProxyEndpoints según el basepath. | [ExtractVariables](../docs/02-politicas/referencia/extract-variables.md), [MessageLogging](../docs/02-politicas/referencia/message-logging.md), [PopulateCache](../docs/02-politicas/referencia/populate-cache.md), [Quota](../docs/02-politicas/referencia/quota.md), [StatisticsCollector](../docs/02-politicas/referencia/statistics-collector.md) | [01-anatomia-api-proxy](../docs/01-proxies/01-anatomia-api-proxy.md) |
| [`tools/sf-dependency-list`](https://github.com/apigee/devrel/tree/main/tools/sf-dependency-list) | Ordena topológicamente las dependencias entre shared flows. | [AssignMessage](../docs/02-politicas/referencia/assign-message.md), [FlowCallout](../docs/02-politicas/referencia/flow-callout.md) | [06-shared-flows-y-flow-hooks](../docs/01-proxies/06-shared-flows-y-flow-hooks.md) |
| [`tools/target-server-validator`](https://github.com/apigee/devrel/tree/main/tools/target-server-validator) | Valida los targets de TargetServers y bundles. | [AssignMessage](../docs/02-politicas/referencia/assign-message.md), [JSONThreatProtection](../docs/02-politicas/referencia/json-threat-protection.md), [JavaCallout](../docs/02-politicas/referencia/java-callout.md) | [05-target-endpoints-y-servidores](../docs/01-proxies/05-target-endpoints-y-servidores.md) |

## Integración GCP

| Ejemplo | Qué muestra | Políticas | En este repo |
|---|---|---|---|
| [`references/cloud-run`](https://github.com/apigee/devrel/tree/main/references/cloud-run) | Exponer un servicio de Cloud Run con Apigee. |  | [05-target-endpoints-y-servidores](../docs/01-proxies/05-target-endpoints-y-servidores.md) |
| [`references/gcp-sa-auth-shared-flow`](https://github.com/apigee/devrel/tree/main/references/gcp-sa-auth-shared-flow) | Shared flow que obtiene access tokens de cuentas de servicio de GCP. | [AssignMessage](../docs/02-politicas/referencia/assign-message.md), [ExtractVariables](../docs/02-politicas/referencia/extract-variables.md), [FlowCallout](../docs/02-politicas/referencia/flow-callout.md), [GenerateJWT](../docs/02-politicas/referencia/generate-jwt.md), [Javascript](../docs/02-politicas/referencia/javascript.md), [KeyValueMapOperations](../docs/02-politicas/referencia/key-value-map-operations.md), [LookupCache](../docs/02-politicas/referencia/lookup-cache.md), [PopulateCache](../docs/02-politicas/referencia/populate-cache.md), [RaiseFault](../docs/02-politicas/referencia/raise-fault.md), [ServiceCallout](../docs/02-politicas/referencia/service-callout.md), [VerifyJWS](../docs/02-politicas/referencia/verify-jws.md) | [06-shared-flows-y-flow-hooks](../docs/01-proxies/06-shared-flows-y-flow-hooks.md) |

## Labs

| Ejemplo | Qué muestra | Políticas | En este repo |
|---|---|---|---|
| [`labs/bdd-proxy-development`](https://github.com/apigee/devrel/tree/main/labs/bdd-proxy-development) | Laboratorio de nivel 200 de desarrollo guiado por comportamiento (BDD) a partir de OpenAPI. |  | [01-ciclo-de-vida](../docs/06-devops/01-ciclo-de-vida.md) |
| [`labs/best-practices-hackathon`](https://github.com/apigee/devrel/tree/main/labs/best-practices-hackathon) | Laboratorio de nivel 300 sobre buenas prácticas. |  | [01-diseno-y-desarrollo](../docs/08-mejores-practicas/01-diseno-y-desarrollo.md) |
| [`labs/eventarc-apihub`](https://github.com/apigee/devrel/tree/main/labs/eventarc-apihub) | Despliegue automatizado de proxies con API hub y Eventarc. |  | [02-integraciones-y-funciones](../docs/12-api-hub/02-integraciones-y-funciones.md) |
| [`labs/idp-okta-integration`](https://github.com/apigee/devrel/tree/main/labs/idp-okta-integration) | Fachada de identidad con Okta (nivel 300). |  | [02-oauth2](../docs/03-seguridad/02-oauth2.md) |

## MCP y agentes

| Ejemplo | Qué muestra | Políticas | En este repo |
|---|---|---|---|
| [`references/apigee-skills-serving`](https://github.com/apigee/devrel/tree/main/references/apigee-skills-serving) | API hub como catálogo versionado y firmado de *skills* de agentes. |  | [02-integraciones-y-funciones](../docs/12-api-hub/02-integraciones-y-funciones.md) |

## Mediación

| Ejemplo | Qué muestra | Políticas | En este repo |
|---|---|---|---|
| [`references/data-converters-shared-flow`](https://github.com/apigee/devrel/tree/main/references/data-converters-shared-flow) | Shared flow de conversiones JSON habituales en respuestas. | [Javascript](../docs/02-politicas/referencia/javascript.md) | [json-xml](../docs/02-politicas/referencia/json-xml.md) |

## Operación

| Ejemplo | Qué muestra | Políticas | En este repo |
|---|---|---|---|
| [`references/cloud-logging-shared-flow`](https://github.com/apigee/devrel/tree/main/references/cloud-logging-shared-flow) | Shared flow de registro en Cloud Logging. | [FlowCallout](../docs/02-politicas/referencia/flow-callout.md), [ServiceCallout](../docs/02-politicas/referencia/service-callout.md) | [message-logging](../docs/02-politicas/referencia/message-logging.md) |

## Sectorial

| Ejemplo | Qué muestra | Políticas | En este repo |
|---|---|---|---|
| [`references/dutch-healthcare`](https://github.com/apigee/devrel/tree/main/references/dutch-healthcare) | Referencia para los estándares sanitarios de Países Bajos. | [AssignMessage](../docs/02-politicas/referencia/assign-message.md), [FlowCallout](../docs/02-politicas/referencia/flow-callout.md), [Javascript](../docs/02-politicas/referencia/javascript.md) | [02-oauth2](../docs/03-seguridad/02-oauth2.md) |

## Seguridad

| Ejemplo | Qué muestra | Políticas | En este repo |
|---|---|---|---|
| [`references/auth-schemes`](https://github.com/apigee/devrel/tree/main/references/auth-schemes) | Implementaciones de esquemas de autenticación habituales. | [BasicAuthentication](../docs/02-politicas/referencia/basic-authentication.md), [GenerateJWT](../docs/02-politicas/referencia/generate-jwt.md), [OAuthV2](../docs/02-politicas/referencia/oauthv2.md), [RaiseFault](../docs/02-politicas/referencia/raise-fault.md), [VerifyAPIKey](../docs/02-politicas/referencia/verify-api-key.md) | [01-apikeys](../docs/03-seguridad/01-apikeys.md) |
| [`references/common-shared-flows`](https://github.com/apigee/devrel/tree/main/references/common-shared-flows) | Shared flows reutilizables de seguridad, tráfico, errores y CORS. | [AssignMessage](../docs/02-politicas/referencia/assign-message.md), [Javascript](../docs/02-politicas/referencia/javascript.md), [KeyValueMapOperations](../docs/02-politicas/referencia/key-value-map-operations.md), [OAuthV2](../docs/02-politicas/referencia/oauthv2.md), [RaiseFault](../docs/02-politicas/referencia/raise-fault.md), [ServiceCallout](../docs/02-politicas/referencia/service-callout.md), [SpikeArrest](../docs/02-politicas/referencia/spike-arrest.md) | [06-shared-flows-y-flow-hooks](../docs/01-proxies/06-shared-flows-y-flow-hooks.md) |
| [`references/identity-facade`](https://github.com/apigee/devrel/tree/main/references/identity-facade) | Fachada de identidad delante de un IdP compatible con OIDC. | [AssignMessage](../docs/02-politicas/referencia/assign-message.md), [BasicAuthentication](../docs/02-politicas/referencia/basic-authentication.md), [ExtractVariables](../docs/02-politicas/referencia/extract-variables.md), [GetOAuthV2Info](../docs/02-politicas/referencia/get-oauth-v2-info.md), [Javascript](../docs/02-politicas/referencia/javascript.md), [KeyValueMapOperations](../docs/02-politicas/referencia/key-value-map-operations.md), [LookupCache](../docs/02-politicas/referencia/lookup-cache.md), [OAuthV2](../docs/02-politicas/referencia/oauthv2.md), [PopulateCache](../docs/02-politicas/referencia/populate-cache.md), [RaiseFault](../docs/02-politicas/referencia/raise-fault.md), [ServiceCallout](../docs/02-politicas/referencia/service-callout.md), [SetOAuthV2Info](../docs/02-politicas/referencia/set-oauth-v2-info.md), [VerifyAPIKey](../docs/02-politicas/referencia/verify-api-key.md), [VerifyJWT](../docs/02-politicas/referencia/verify-jwt.md) | [02-oauth2](../docs/03-seguridad/02-oauth2.md) |
| [`references/oauth-admin-api`](https://github.com/apigee/devrel/tree/main/references/oauth-admin-api) | API para revocar tokens emitidos por Apigee por app o por usuario. | [AssignMessage](../docs/02-politicas/referencia/assign-message.md), [OAuthV2](../docs/02-politicas/referencia/oauthv2.md), [RaiseFault](../docs/02-politicas/referencia/raise-fault.md), [RevokeOAuthV2](../docs/02-politicas/referencia/revoke-oauth-v2.md) | [revoke-oauth-v2](../docs/02-politicas/referencia/revoke-oauth-v2.md) |
| [`references/oidc-mock`](https://github.com/apigee/devrel/tree/main/references/oidc-mock) | Proveedor de identidad OIDC simulado. | [AssignMessage](../docs/02-politicas/referencia/assign-message.md), [BasicAuthentication](../docs/02-politicas/referencia/basic-authentication.md), [ExtractVariables](../docs/02-politicas/referencia/extract-variables.md), [Javascript](../docs/02-politicas/referencia/javascript.md), [RaiseFault](../docs/02-politicas/referencia/raise-fault.md) | [02-oauth2](../docs/03-seguridad/02-oauth2.md) |
| [`references/recaptcha-enterprise`](https://github.com/apigee/devrel/tree/main/references/recaptcha-enterprise) | Protección frente a bots con reCAPTCHA Enterprise. | [AssignMessage](../docs/02-politicas/referencia/assign-message.md), [DataCapture](../docs/02-politicas/referencia/data-capture.md), [ExtractVariables](../docs/02-politicas/referencia/extract-variables.md), [FlowCallout](../docs/02-politicas/referencia/flow-callout.md), [Javascript](../docs/02-politicas/referencia/javascript.md), [RaiseFault](../docs/02-politicas/referencia/raise-fault.md), [ServiceCallout](../docs/02-politicas/referencia/service-callout.md), [VerifyAPIKey](../docs/02-politicas/referencia/verify-api-key.md) | [02-deteccion-y-acciones](../docs/13-advanced-api-security/02-deteccion-y-acciones.md) |
| [`references/southbound-mtls`](https://github.com/apigee/devrel/tree/main/references/southbound-mtls) | mTLS de cliente hacia backends. |  | [04-tls-referencias-y-data-collectors](../docs/15-administracion/04-tls-referencias-y-data-collectors.md) |
| [`references/threat-protect`](https://github.com/apigee/devrel/tree/main/references/threat-protect) | Protección frente a amenazas XML y JSON. | [AssignMessage](../docs/02-politicas/referencia/assign-message.md), [JSONThreatProtection](../docs/02-politicas/referencia/json-threat-protection.md), [RaiseFault](../docs/02-politicas/referencia/raise-fault.md), [XMLThreatProtection](../docs/02-politicas/referencia/xml-threat-protection.md), [XMLToJSON](../docs/02-politicas/referencia/xml-json.md), [XSL](../docs/02-politicas/referencia/xsl-transform.md) | [05-threat-protection](../docs/03-seguridad/05-threat-protection.md) |

## Fuentes

- apigee/devrel: <https://github.com/apigee/devrel> (clonado y analizado el 2026-10-23).
