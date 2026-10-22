# Cobertura frente a la documentación oficial

> [!IMPORTANT]
> Este documento responde a una pregunta concreta: **¿qué parte de la documentación oficial de Apigee está representada en este repositorio?** Se regenera con los scripts de `scripts/`; las cifras de abajo son del **22 de octubre de 2026**.

## Respuesta corta

**No está completa.** El repositorio nació como una síntesis del *núcleo de desarrollo de proxies* (políticas, flujos, seguridad, publicación, operación básica, DevOps, IA) y lo cubre bien. Desde el 22 de octubre de 2026, además, la **referencia de políticas está completa**: un archivo por cada una de las 69 políticas (65 de X/hybrid y 4 exclusivas de Edge), verificado contra la página de X y la de Edge. Pero la documentación oficial es mucho más amplia, y hay áreas enteras sin representar: Apigee hybrid como producto, troubleshooting, administración del sistema, API hub, Advanced API Security, adaptadores (Envoy, Kubernetes), monetización y todo lo propio de Edge (Private Cloud, Microgateway, Node.js, API Monitoring).

## Cómo se mide

1. `scripts/inventario_oficial.py` recorre la navegación lateral de `docs.cloud.google.com/apigee/docs` y de `docs.apigee.com` y escribe `inventario/oficial-x-hybrid.tsv` y `inventario/oficial-edge.tsv`. No usa sitemaps porque, en la fecha de corte, los sitemaps hoja de ambos dominios devolvían HTTP 500 de forma sostenida.
2. `scripts/cobertura.py` normaliza el inventario y cruza cada URL oficial con las URLs citadas en `docs/`. La salida es `inventario/cobertura.tsv`. La normalización:
   - deja solo la última versión de hybrid y de Edge Private Cloud, porque las demás son copias de las mismas guías;
   - cuenta como un solo bloque la referencia REST autogenerada y las release notes.
3. **"Citada"** significa que la URL aparece en algún documento del repo. Es una métrica **conservadora**: un documento puede cubrir un tema sin enlazar cada página. La columna *Estado* de las tablas es la valoración cualitativa de lo que de verdad está cubierto.

```bash
python3 scripts/inventario_oficial.py   # ~10 min la primera vez; luego usa .cache/
python3 scripts/cobertura.py
```

## Tamaño del corpus oficial

| Edición | Páginas en navegación | Tras normalizar | De ellas, guías (sin API REST ni release notes) | Citadas por el repo |
|---|---|---|---|---|
| Apigee X / hybrid | 3391 | 1719 | ≈ 950 | 121 (7,0 %) |
| Apigee Edge | 2103 | 1606 | ≈ 960 | 57 (3,5 %) |

## Matriz por área — Apigee X / hybrid

Estado: ✅ cubierto · 🟡 parcial · ❌ ausente · 🔧 en curso.

| Área oficial | Páginas | Citadas | Estado | Dónde está o estará en el repo |
|---|---|---|---|---|
| `api-platform/reference` (políticas, variables, condiciones, límites) | 102 | 72 | ✅ | [`docs/02-politicas/referencia/`](docs/02-politicas/referencia/00-indice.md): un archivo por política, **todas hechas**; variables, condiciones y límites en `docs/01-proxies/` y `docs/10-referencia/` |
| `api-platform/fundamentals` | 26 | 12 | ✅ | `docs/00-fundamentos/`, `docs/01-proxies/` |
| `api-platform/develop` | 28 | 2 | 🟡 | `docs/01-proxies/`, `docs/02-politicas/`; faltan proxies configurables, GraphQL, SSE, WebSockets, Java callout paso a paso |
| `api-platform/security` | 41 | 6 | 🟡 | `docs/03-seguridad/`; faltan OAuth en detalle por grant type, SAML, IAM, cifrado de datos y CMEK |
| `api-platform/publish` | 53 | 4 | 🟡 | `docs/04-publicacion/`; faltan portales (integrado y Drupal) |
| `api-platform/analytics` | 28 | 1 | 🟡 | `docs/05-operacion/03-analytics-monitoreo.md` |
| `api-platform/cache`, `debug`, `deploy`, `test` | 21 | 5 | 🟡 | `docs/05-operacion/`, `docs/06-devops/` |
| `api-platform/troubleshoot`, `errorcatalog` | 91 | 0 | ❌ | Nuevo `docs/14-troubleshooting/` |
| `api-platform/get-started` (aprovisionamiento, redes, PSC) | 58 | 2 | 🟡 | `docs/00-fundamentos/03-arquitectura.md`; falta aprovisionamiento paso a paso |
| `api-platform/system-administration` | 36 | 0 | ❌ | Nuevo `docs/15-administracion/` |
| `api-platform/local-development` | 25 | 1 | ❌ | `docs/06-devops/` |
| `api-platform/integration` (Apigee Integration) | 42 | 0 | ❌ | Nuevo `docs/15-administracion/` o área propia |
| `api-platform/envoy-adapter`, `apigee-kubernetes`, `service-extensions` | 58 | 0 | ❌ | Nuevo `docs/16-adaptadores/` |
| `api-platform/monetization` | 13 | 0 | ❌ | `docs/04-publicacion/` |
| `api-platform/antipatterns` | 22 | 4 | 🟡 | `docs/09-antipatrones/` |
| `api-platform/apigee-mcp` | 6 | 2 | ✅ | `docs/07-ai-gateway/02-mcp-en-apigee.md` |
| `hybrid` (v1.17 + sin versión) | 137 | 0 | ❌ | Nuevo `docs/11-hybrid/` |
| `apihub`, `api-hub` | 90 | 1 | ❌ | Nuevo `docs/12-api-hub/` |
| `api-security`, `aapi-ops`, `api-observation` | 26 | 1 | 🟡 | `docs/03-seguridad/05-threat-protection.md`; nuevo `docs/13-advanced-api-security/` |
| `api-monitoring` | 8 | 0 | ❌ | `docs/05-operacion/` |
| `reference/apis` (API REST de gestión) | 767 | 2 | 🟡 | `docs/06-devops/02-herramientas-cli.md`; nuevo mapa de recursos en `docs/10-referencia/` (sin una página por método) |
| `deprecations`, `release-notes`, `security-bulletins` | 15 | 1 | 🟡 | `docs/00-fundamentos/02-ediciones-y-comparativa.md` |

## Matriz por área — Apigee Edge

| Área oficial | Páginas | Citadas | Estado | Dónde está o estará en el repo |
|---|---|---|---|---|
| `api-platform/reference` (políticas) | 198 | 51 | ✅ | Cada archivo de `docs/02-politicas/referencia/` incluye **Diferencias en Apigee Edge**; las 4 exclusivas de Edge (ExtensionCallout, LDAP, StatisticsCollector, ConcurrentRateLimit, esta última retirada) tienen archivo propio |
| `api-platform/fundamentals`, `develop`, `get-started` | 56 | 2 | 🟡 | Los conceptos son comunes con X; faltan las diferencias de Edge |
| `api-platform/troubleshoot` | 163 | 0 | ❌ | `docs/14-troubleshooting/`, con columna por edición |
| `api-platform/publish`, `monetization` | 108 | 0 | ❌ | `docs/17-edge/` |
| `api-platform/microgateway` | 58 | 0 | ❌ | `docs/17-edge/` |
| `private-cloud` (v4.54.00 + sin versión) | 73 | 0 | ❌ | `docs/17-edge/` |
| `api-platform/system-administration` | 48 | 0 | ❌ | `docs/17-edge/` |
| `api-platform/envoy-adapter`, `istio-adapter` | 43 | 0 | ❌ | `docs/16-adaptadores/` |
| `api-platform/nodejs`, `hosted-targets`, `extensions` | 23 | 0 | ❌ | `docs/17-edge/` (funciones sin equivalente en X) |
| `api-monitoring` | 22 | 0 | ❌ | `docs/17-edge/` |
| `api-platform/antipatterns` | 29 | 2 | 🟡 | `docs/09-antipatrones/` |
| `api-platform/analytics`, `cache`, `debug`, `deploy`, `security` | 75 | 0 | 🟡 | Conceptos comunes con X; faltan diferencias |
| `api-platform/faq`, `samples`, `tutorials`, `integrations` | 60 | 0 | ❌ | Mapa de ejemplos en `ejemplos/` |
| `release` (notas) | 644 | 2 | 🟡 | Solo hitos de fin de vida en `docs/00-fundamentos/02-ediciones-y-comparativa.md` |

## Ejemplos oficiales

| Repositorio | Edición | Ejemplos | Estado |
|---|---|---|---|
| [GoogleCloudPlatform/apigee-samples](https://github.com/GoogleCloudPlatform/apigee-samples) | X / hybrid | 57 | ❌ Por mapear en `ejemplos/` |
| [apigee/devrel](https://github.com/apigee/devrel) (`references/`, `labs/`, `tools/`) | X / hybrid | 44 | ❌ Por mapear |
| [apigee/api-platform-samples](https://github.com/apigee/api-platform-samples) (archivado) | Edge | 34 | ❌ Por mapear |
| [apigee/openbank](https://github.com/apigee/openbank) | X / Edge | 1 implementación de referencia | ❌ Por mapear |

## Plan de trabajo

| Fase | Contenido | Estado |
|---|---|---|
| 1 | Inventario oficial, scripts y esta matriz | ✅ |
| 2 | Referencia por política: 65 de X/hybrid + 4 exclusivas de Edge | ✅ 69 hechas, más 2 documentos de conceptos y el [índice](docs/02-politicas/referencia/00-indice.md) |
| 3 | Áreas ausentes de X/hybrid: hybrid, troubleshooting, administración, API hub, Advanced API Security, adaptadores, monetización | Pendiente |
| 4 | Edge (`docs/17-edge/`): Private Cloud, Microgateway, Node.js, API Monitoring, monetización, diferencias por área | Pendiente |
| 5 | Mapa de ejemplos oficiales y bundles propios validados | Pendiente |
| 6 | Índices (`README.md`, `llms.txt`), `PROCEDENCIA.md` y esta matriz actualizados | Continuo |

## Discrepancias encontradas en la documentación oficial

Contradicciones internas de las páginas de Google, documentadas en el archivo afectado en vez de resolverlas por suposición:

| Tema | Discrepancia | Documentado en |
|---|---|---|
| HTTP de `QuotaViolation` | La tabla de errores de X dice 500; la nota de la misma página dice 429. Edge: 500, o 429 con una propiedad de organización | [quota.md](docs/02-politicas/referencia/quota.md#errores) |
| `TimeUnit` `year` en Quota | Aparece en el texto de X pero no en el error de despliegue `InvalidQuotaTimeUnit` | [quota.md](docs/02-politicas/referencia/quota.md#interval-y-timeunit) |
| `<StartTime>` ausente con `calendar` | Una sección dice que da error; otra, que arranca el primer día del mes | [quota.md](docs/02-politicas/referencia/quota.md#starttime) |
| `developer.id` como identificador de Quota | La página de Quota lo usa de ejemplo; la de VerifyAPIKey prohíbe usarlo | [quota.md](docs/02-politicas/referencia/quota.md#identifier), [verify-api-key.md](docs/02-politicas/referencia/verify-api-key.md#variables-de-flujo) |
| `Exclusive` en el `<Scope>` de caché | En X, la guía de claves de caché incluye la revisión en el prefijo, pero las cuatro páginas de políticas de caché la omiten. En Edge, todas la incluyen | [claves-de-cache.md](docs/02-politicas/referencia/claves-de-cache.md#scope-el-prefijo-automático) |
| Default de `<ExcludeErrorResponse>` | `true` en X/hybrid, `false` en Edge | [response-cache.md](docs/02-politicas/referencia/response-cache.md) |
| `<PurgeChildEntries>` en InvalidateCache | X: mismo prefijo; Edge: mismo valor de fragmento | [invalidate-cache.md](docs/02-politicas/referencia/invalidate-cache.md) |
| `<MaxDepth>` en GraphQL | Default 4 en la tabla, 10 en el texto y en la plantilla de la UI | [graphql.md](docs/02-politicas/referencia/graphql.md) |
| `SHA-384` en HMAC | En el texto, pero no en la lista del error de despliegue | [hmac.md](docs/02-politicas/referencia/hmac.md) |
| `<PrivateKey>` en OAuthV2 | Descrito para RSA, pero la fila *Presence* lo exige con HS* | [oauthv2.md](docs/02-politicas/referencia/oauthv2.md) |
| `<Claim>` en VerifyJWT | La página de la política dice que admite plantillas; la general, que las Verify no las aplican | [verify-jwt.md](docs/02-politicas/referencia/verify-jwt.md) |
| `<TimeUnit>` y `<StartTime>` en LLMTokenQuota | Mismas contradicciones que en Quota | [llm-token-quota.md](docs/02-politicas/referencia/llm-token-quota.md) |
| Default de `<UserPromptSource>` en PromptTokenLimit | Sin default según la tabla; la UI inserta la ruta de Gemini | [prompt-token-limit.md](docs/02-politicas/referencia/prompt-token-limit.md) |
| `<TTLInSeconds>` en SemanticCachePopulate | Default 60 en el texto, «N/A» en la tabla | [semantic-cache-populate.md](docs/02-politicas/referencia/semantic-cache-populate.md) |
| `<TemplateName>` en SanitizeModelResponse | La tabla lo pone en la raíz; la sintaxis, dentro de otro elemento | [sanitize-llm-response.md](docs/02-politicas/referencia/sanitize-llm-response.md) |
| `<Port>` en MessageLogging | Opcional con default 514, pero `InvalidPort` salta «si no se especifica» | [message-logging.md](docs/02-politicas/referencia/message-logging.md) |
| `<ResourceURL>` en JavaScript | Basta con `<Source>`, pero `NoResourceURLOrSource` dice que `<ResourceURL>` es obligatorio | [javascript.md](docs/02-politicas/referencia/javascript.md) |
| Versión de Java en JavaCallout | JDK 11 en la página; «JDK 7/8» en la fila de `IncompatibleJavaVersion` | [java-callout.md](docs/02-politicas/referencia/java-callout.md) |
| `<IgnoreUnresolvedVariables>` en TraceCapture | Default `true` en la descripción y `false` en la nota; además lista un `<MergeBehavior>` ajeno | [trace-capture.md](docs/02-politicas/referencia/trace-capture.md) |
| Inactividad del wallet en MonetizationLimitsCheck | 1,5 años en la tabla de errores, un año en `status_message` | [monetization-limits-check.md](docs/02-politicas/referencia/monetization-limits-check.md) |
| `default` en DataCapture | Marcado «Required», pero se describe qué pasa si se omite | [data-capture.md](docs/02-politicas/referencia/data-capture.md) |
| `<UserName>` + `<SearchQuery>` en LDAP | La descripción los combina; el error `SearchQueryAndUserNameCannotBePresent` lo prohíbe | [ldap.md](docs/02-politicas/referencia/ldap.md) |
| `type` en StatisticsCollector | Opcional con default `string`, pero existe el error de despliegue `DatatypeMissing` | [statistics-collector.md](docs/02-politicas/referencia/statistics-collector.md) |
