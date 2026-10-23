---
id: ejemplos-openbank
titulo: Mapa de ejemplos — apigee/openbank
area: ejemplos
tags: [ejemplos, openbank, samples]
aplica_a: [apigee-edge]
fuente: https://github.com/apigee/openbank
revisado: 2026-10-23
---

<!-- Archivo generado por scripts/generar_mapa_ejemplos.py. No editar a mano. -->

# Mapa de ejemplos — apigee/openbank

> **Fecha de corte: 2026-10-23.** Ediciones: **Apigee Edge**. Repositorio: <https://github.com/apigee/openbank>.

Implementación de referencia de Open Banking (Apache 2.0, no es producto oficial). **Está hecha para Apigee Edge**: los sandboxes usan `<HostedTarget/>` (función que no existe en X), y la guía de despliegue usa la API de gestión de Edge (`api.enterprise.apigee.com`) y hosts `*.apigee.net`. Los ejemplos usan el estándar británico **OBIE** (por ejemplo `open-banking/v2.3/atms`) y la cabecera `x-fapi-financial-id`, propia de la época de FAPI 1.0.

La columna **Políticas** se extrae automáticamente de los XML de cada bundle (`scripts/mapa_ejemplos.py`); enlaza con la referencia de cada política. Una celda vacía indica que el ejemplo no trae bundles (scripts, Terraform, notebooks, portales).

## Open Banking

| Ejemplo | Qué muestra | Políticas | En este repo |
|---|---|---|---|
| [`apiproxies/identity-v1`](https://github.com/apigee/openbank/tree/main/apiproxies/identity-v1) | Servidor de identidad y autorización OAuth 2.0/OIDC de la referencia de Open Banking. | [AssignMessage](../docs/02-politicas/referencia/assign-message.md), [FlowCallout](../docs/02-politicas/referencia/flow-callout.md) | [02-oauth2](../docs/03-seguridad/02-oauth2.md) |
| [`apiproxies/mock-tpp-v1`](https://github.com/apigee/openbank/tree/main/apiproxies/mock-tpp-v1) | TPP (tercero) simulado para probar los flujos. | [AssignMessage](../docs/02-politicas/referencia/assign-message.md), [FlowCallout](../docs/02-politicas/referencia/flow-callout.md) | [02-oauth2](../docs/03-seguridad/02-oauth2.md) |
| [`apiproxies/sandboxes-v1`](https://github.com/apigee/openbank/tree/main/apiproxies/sandboxes-v1) | Sandboxes de las APIs de Open Banking generadas desde las especificaciones oficiales (OBIE). | [FlowCallout](../docs/02-politicas/referencia/flow-callout.md) | [oas-validation](../docs/02-politicas/referencia/oas-validation.md) |
| [`sharedflows/authcode-externaltoken`](https://github.com/apigee/openbank/tree/main/sharedflows/authcode-externaltoken) | Shared flow de *authorization code* con token externo. | [AssignMessage](../docs/02-politicas/referencia/assign-message.md), [BasicAuthentication](../docs/02-politicas/referencia/basic-authentication.md), [ExtractVariables](../docs/02-politicas/referencia/extract-variables.md), [OAuthV2](../docs/02-politicas/referencia/oauthv2.md), [ServiceCallout](../docs/02-politicas/referencia/service-callout.md), [VerifyAPIKey](../docs/02-politicas/referencia/verify-api-key.md) | [oauthv2](../docs/02-politicas/referencia/oauthv2.md) |
| [`sharedflows/clientcredentials-token`](https://github.com/apigee/openbank/tree/main/sharedflows/clientcredentials-token) | Shared flow de *client credentials*. | [OAuthV2](../docs/02-politicas/referencia/oauthv2.md) | [oauthv2](../docs/02-politicas/referencia/oauthv2.md) |
| [`sharedflows/cors-error-v1`](https://github.com/apigee/openbank/tree/main/sharedflows/cors-error-v1) | Cabeceras CORS en respuestas de error. | [AssignMessage](../docs/02-politicas/referencia/assign-message.md) | [cors](../docs/02-politicas/referencia/cors.md) |
| [`sharedflows/cors-headers-v1`](https://github.com/apigee/openbank/tree/main/sharedflows/cors-headers-v1) | Cabeceras CORS en respuestas normales. | [AssignMessage](../docs/02-politicas/referencia/assign-message.md) | [cors](../docs/02-politicas/referencia/cors.md) |
| [`sharedflows/cors-options-v1`](https://github.com/apigee/openbank/tree/main/sharedflows/cors-options-v1) | Respuesta a las peticiones *preflight* `OPTIONS`. | [RaiseFault](../docs/02-politicas/referencia/raise-fault.md) | [cors](../docs/02-politicas/referencia/cors.md) |
| [`sharedflows/dynamic-registration`](https://github.com/apigee/openbank/tree/main/sharedflows/dynamic-registration) | Registro dinámico de clientes (DCR) de TPP. | [AssignMessage](../docs/02-politicas/referencia/assign-message.md), [ExtractVariables](../docs/02-politicas/referencia/extract-variables.md), [Javascript](../docs/02-politicas/referencia/javascript.md), [KeyValueMapOperations](../docs/02-politicas/referencia/key-value-map-operations.md), [ServiceCallout](../docs/02-politicas/referencia/service-callout.md) | [02-developers-apps](../docs/04-publicacion/02-developers-apps.md) |
| [`sharedflows/mock-jwks`](https://github.com/apigee/openbank/tree/main/sharedflows/mock-jwks) | JWKS simulado para pruebas de firma. | [AssignMessage](../docs/02-politicas/referencia/assign-message.md) | [jwt-jws-conceptos](../docs/02-politicas/referencia/jwt-jws-conceptos.md) |
| [`sharedflows/traffic-mgmt-v1`](https://github.com/apigee/openbank/tree/main/sharedflows/traffic-mgmt-v1) | Gestión de tráfico común con SpikeArrest. | [SpikeArrest](../docs/02-politicas/referencia/spike-arrest.md) | [quota](../docs/02-politicas/referencia/quota.md) |
| [`sharedflows/verify-eidas-v1`](https://github.com/apigee/openbank/tree/main/sharedflows/verify-eidas-v1) | Verificación del certificado eIDAS del TPP con un JavaCallout; en la guía, el certificado llega en la cabecera `SSL-CLIENT-CERT`. | [JavaCallout](../docs/02-politicas/referencia/java-callout.md) | [04-tls-mtls](../docs/03-seguridad/04-tls-mtls.md) |
| [`sharedflows/verifyaccesstoken`](https://github.com/apigee/openbank/tree/main/sharedflows/verifyaccesstoken) | Verificación del access token. | [OAuthV2](../docs/02-politicas/referencia/oauthv2.md) | [oauthv2](../docs/02-politicas/referencia/oauthv2.md) |

## Fuentes

- apigee/openbank: <https://github.com/apigee/openbank> (clonado y analizado el 2026-10-23).
