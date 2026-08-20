---
id: practicas-checklist
titulo: Checklist de producción
area: practicas
tags: [checklist, produccion, go-live, revision, auditoria]
aplica_a: [apigee-x, apigee-hybrid]
fuente: https://docs.apigee.com/api-platform/fundamentals/best-practices-api-proxy-design-and-development
revisado: 2026-08-20
---

# Checklist de producción

Revisión previa a publicar un proxy. Cada punto enlaza al documento que lo explica.

---

## Estructura

- [ ] **Un solo `<ProxyEndpoint>`** en el proxy — [antipatrones](../09-antipatrones/01-catalogo-antipatrones.md)
- [ ] **Un `<Flow>` por operación** (verbo + ruta), no condiciones colgando del PreFlow — [flujos](../01-proxies/02-flujos-y-pipeline.md)
- [ ] Existe un **flujo catch-all** al final que devuelve 404/405
- [ ] La **RouteRule por defecto va la última** (sin `<Condition>`)
- [ ] El **basepath incluye la versión** (`/pedidos/v1`)
- [ ] **No hay políticas ni recursos sin referenciar** en el bundle
- [ ] El bundle **no supera 15 MB**
- [ ] Todo `name` de política **coincide con su nombre de archivo** — [convenciones](02-convenciones-de-nombres.md)

## Seguridad

- [ ] Hay **autenticación** en el PreFlow (`VerifyAPIKey`, `OAuthV2` o `VerifyJWT`)
- [ ] `/health` y `/metrics` están **excluidos** de la autenticación y de la cuota
- [ ] Hay **threat protection** en todos los métodos con body (`JSONThreatProtection` / `XMLThreatProtection`) — [threat protection](../03-seguridad/05-threat-protection.md)
- [ ] Las **regex no usan cuantificadores greedy anidados**
- [ ] `<IgnoreValidationErrors>` está en **`false`** en todos los TargetEndpoint — [TLS](../03-seguridad/04-tls-mtls.md)
- [ ] Solo se aceptan **TLSv1.2 y TLSv1.3**
- [ ] **No hay secretos en el bundle**: viven en KVM cifrado o keystore
- [ ] Los secretos usan el prefijo **`private.`** para no aparecer en Trace
- [ ] `<AllowOrigins>` de CORS **no es `*`** si `<AllowCredentials>` es `true` — [mediación](../02-politicas/03-mediacion.md)
- [ ] `<Algorithm>` de JWT está **fijado explícitamente**, no tomado del token
- [ ] No se usa **`HS256` para tokens de terceros**
- [ ] `DecodeJWT` **nunca** se usa solo para autorizar
- [ ] Las cabeceras internas del backend se **eliminan** en la respuesta (`Server`, `X-Powered-By`)

## Tráfico y cuotas

- [ ] Hay **`SpikeArrest`** para proteger el runtime — [traffic management](../02-politicas/01-traffic-management.md)
- [ ] Hay **`Quota`** que lee los valores del **API product**, no hardcodeados
- [ ] `Quota` usa `<Distributed>true</Distributed>`
- [ ] El `<Identifier>` de `Quota` **no es de alta cardinalidad**
- [ ] Ninguna política `Quota` se **reutiliza** en flujos que deban tener contadores distintos
- [ ] Se devuelven cabeceras `X-RateLimit-*` al cliente

## Backend

- [ ] Se usa **`TargetServer`**, no URL hardcodeada — [targets](../01-proxies/05-target-endpoints-y-servidores.md)
- [ ] `connect.timeout.millis` e `io.timeout.millis` están **configurados**
- [ ] `io.timeout.millis` es **menor** que el timeout del cliente
- [ ] Con **un solo TargetServer**, `MaxFailures` es `0` o hay `HealthMonitor`
- [ ] **Keep-alive no está desactivado**
- [ ] Si hay balanceo, hay **`HealthMonitor`** configurado
- [ ] `target.url` **no se construye con datos del cliente sin validar** (SSRF)

## Errores

- [ ] Hay **`<FaultRules>`** para los errores previsibles — [manejo de errores](../05-operacion/01-manejo-de-errores.md)
- [ ] Hay **`<DefaultFaultRule>` con `<AlwaysEnforce>true</AlwaysEnforce>`**
- [ ] Las respuestas de error siguen el **formato corporativo**
- [ ] **No se filtran** `{fault.name}`, `{error.content}` ni URLs del backend al cliente
- [ ] Los mensajes de error son **legibles y sugieren la solución**
- [ ] Cada respuesta de error incluye un **`correlation_id`**
- [ ] Se distingue **401 (no autenticado)** de **403 (no autorizado)**

## Caché

- [ ] `<SkipCachePopulation>` excluye **respuestas no-200 y métodos no-GET** — [caching](../05-operacion/04-caching-y-persistencia.md)
- [ ] La **cache key es la mínima suficiente** y no incluye `client_id` sin necesidad
- [ ] El **TTL es adecuado** al dato
- [ ] La respuesta de **CORS no se cachea**
- [ ] Los valores cacheados **no superan 256 KB**
- [ ] Todos los `KeyValueMapOperations` tienen **`<ExpiryTimeInSecs>`**
- [ ] El lookup está en el **PreFlow del request**, la población en el **PostFlow del response**

## Observabilidad

- [ ] Hay **`MessageLogging` en el `PostClientFlow`** con `continueOnError="true"` — [analytics](../05-operacion/03-analytics-monitoreo.md)
- [ ] Se invoca **una sola vez** por proxy
- [ ] El log es **JSON estructurado** con `correlation_id`, producto, developer, latencias y `fault.name`
- [ ] **No se registran secretos ni PII**
- [ ] Existe un endpoint **`/health` que devuelve la revisión desplegada**
- [ ] Hay **alertas** de error rate, latencia p99 y overhead de Apigee
- [ ] Hay **alerta de expiración de certificados** a 30 días

## Rendimiento

- [ ] `Quota` es **asíncrona** salvo necesidad de facturación estricta — [rendimiento](03-rendimiento.md)
- [ ] La configuración estática está en **PropertySet**, no en KVM
- [ ] Todos los `ServiceCallout` tienen **`<Timeout>`**
- [ ] Ningún `Javascript` hace lo que haría `AssignMessage` o `ExtractVariables`
- [ ] Ningún `Javascript` usa **`httpClient`** ni **`waitForComplete()`**
- [ ] El **streaming está desactivado** salvo que sea imprescindible y ninguna política necesite el body
- [ ] El entorno tiene **menos de 3.000 basepaths**

## Publicación

- [ ] Existe el **API product** correspondiente con cuota y operaciones definidas — [API products](../04-publicacion/01-api-products.md)
- [ ] Las **operaciones del producto coinciden** con las rutas realmente implementadas
- [ ] La **spec OpenAPI está actualizada** y publicada
- [ ] Los API products están **versionados en Git**
- [ ] El `approvalType` es **`manual`** para productos de pago o con datos sensibles

## Despliegue

- [ ] El bundle está en **control de versiones** — [ciclo de vida](../06-devops/01-ciclo-de-vida.md)
- [ ] El pipeline **empaqueta una vez y promociona la misma revisión**
- [ ] El pipeline **valida el XML** y que `name` coincida con el archivo
- [ ] Producción requiere **aprobación manual**
- [ ] Hay **smoke test** post-despliegue con rollback automático
- [ ] Se conoce la **revisión anterior** para rollback
- [ ] El CI **no guarda claves JSON de service account** (usa Workload Identity Federation)
- [ ] Los `TargetServer` y KVM de cada entorno están **sincronizados desde el repositorio**

## Específico de proxies de LLM

- [ ] Hay **`LLMTokenQuota`** en patrón `EnforceOnly` + `CountOnly` con `<SharedName>` — [AI gateway](../07-ai-gateway/01-apigee-como-ai-gateway.md)
- [ ] Hay **`PromptTokenLimit`**
- [ ] Se filtra el **prompt** (`SanitizeUserPrompt`) **y la respuesta** (`SanitizeModelResponse`)
- [ ] Cada filtro de Model Armor tiene una **acción definida** para `MATCH_FOUND`
- [ ] Las claves del proveedor están en **KVM cifrado**
- [ ] La caché semántica **no se aplica a respuestas personalizadas**
- [ ] El `<Threshold>` de la caché semántica está **calibrado con tráfico real**
- [ ] Si hay streaming, **está documentado** que el filtrado de salida no aplica
- [ ] Se capturan métricas de **tokens, modelo y detecciones**

---

## Uso como prompt de revisión

Para que un LLM audite un bundle contra esta lista:

```
Revisa este bundle de Apigee contra el checklist de producción de
docs/08-mejores-practicas/04-checklist-produccion.md.

Para cada punto indica: CUMPLE / NO CUMPLE / NO APLICA, con el archivo y
la línea concreta cuando no cumpla. No inventes políticas que no existan
en el catálogo de docs/02-politicas/00-catalogo-de-politicas.md.
```

## Fuentes

- <https://docs.apigee.com/api-platform/fundamentals/best-practices-api-proxy-design-and-development>
- <https://docs.apigee.com/api-platform/antipatterns/intro>
- <https://cloud.google.com/apigee/docs/api-platform/reference/limits>
