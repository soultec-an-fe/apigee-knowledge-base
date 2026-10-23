# Procedencia del contenido

> [!IMPORTANT]
> Este documento clasifica cada parte del repositorio según su nivel de respaldo, para
> que sepas qué puedes citar como doctrina oficial de Google y qué es criterio propio.

El campo `fuente:` del frontmatter indica **el enlace canónico del tema**. Cuando la
fuente se anota como "consultada directamente, contenido completo" en la sección
`## Fuentes` de un documento, significa que se navegó la página real (no una búsqueda
ni un resumen) y su contenido se usó para escribir o corregir el documento.

---

## Historial de verificación

**Primera pasada** (redacción inicial): la mayor parte del contenido se escribió combinando
fetches a páginas oficiales que sí devolvieron contenido, con conocimiento general del
modelo cuando la página oficial solo devolvía navegación (varias páginas de
`docs.cloud.google.com` se renderizan con JavaScript y no eran accesibles por fetch simple).

**Segunda pasada** (verificación con navegador): se abrió un navegador real y se visitaron
directamente las páginas que habían fallado en la primera pasada, más varias páginas
adicionales de alto impacto. Esto permitió **confirmar, corregir o completar** un número
significativo de documentos. El resultado de esa pasada es lo que reporta este documento.

### Errores reales corregidos en la segunda pasada

| Error | Corrección |
|---|---|
| Fecha de apagado de la Classic UI de Apigee Edge dada como "2 de noviembre de 2025" | Corregida a **29 de agosto de 2025** (apagado general) / **29 de septiembre de 2025** (apagado final para clientes con excepción), verificado contra `docs.cloud.google.com/apigee/docs/deprecations/apigee-classic-ui` |
| `ConcurrentRateLimit` presentada como política de traffic management vigente | Es una **política retirada** (deprecada 15/07/2020, retirada de Private Cloud en 4.50.00, 15/07/2021). Corregido en el catálogo, en `01-traffic-management.md`, y en las dos menciones restantes en `08-mejores-practicas/03-rendimiento.md` y `09-antipatrones/01-catalogo-antipatrones.md` |
| Catálogo de políticas con categorías Standard/Extensible **inventadas** ("estándar = endurecida, extensible = más funciones") | Reescrito con la clasificación **real** de Google: Standard funciona en cualquier tipo de entorno; Extensible solo en entornos Intermediate/Comprehensive y tiene implicaciones de coste. Un proxy con una sola política Extensible se convierte en proxy Extensible completo |
| Catálogo de políticas incompleto: faltaban `TraceCapture`, `ParseDialogflowRequest`, `SetDialogflowResponse` | Añadidas, con su categoría oficial verificada |
| `MessageValidation` listada como política vigente de Apigee X | ~~Marcada como posible legacy de Edge~~. **Revertido en la tercera pasada:** `<MessageValidation>` sí existe en X/hybrid; en la UI se llama SOAPMessageValidation. Ver [message-validation.md](docs/02-politicas/referencia/message-validation.md) |
| Categorías incorrectas para `PublishMessage`, `AssertCondition`, `ExternalCallout`, `AccessEntity`, `MonetizationLimitsCheck` | Recolocadas según la categoría oficial exacta |
| "Antipatrón: un producto por proxy" presentado como si fuera doctrina de Google | Es **criterio propio**. La recomendación oficial real es mantener una relación 1:1 entre spec OpenAPI, proxy y producto para gobernar el catálogo — no prohíbe el patrón de planes (varios productos sobre el mismo proxy). Reescrito para separar ambas cosas |
| Límite de Trace "15 transacciones por sesión" sin matizar | Corregido: son **15 por Message Processor**, no un total global — el efecto real es impredecible según el propio texto de Google. Añadidos el timeout de 10 min, el retraso de activación de ~15 s y la retención de 24 h |
| Ausencia total de **MCP (Model Context Protocol) en Apigee** | Añadido como documento nuevo: [docs/07-ai-gateway/02-mcp-en-apigee.md](docs/07-ai-gateway/02-mcp-en-apigee.md), verificado íntegramente contra la documentación oficial |

---

## Tercera pasada (22 de octubre de 2026): referencia por política

Se escribió un archivo por política en [`docs/02-politicas/referencia/`](docs/02-politicas/referencia/00-indice.md): 65 de Apigee X/hybrid (con su sección de diferencias en Edge) y 4 exclusivas de Edge, más dos documentos de conceptos compartidos (claves de caché y JWT/JWS).

**Método:** cada página oficial se descargó con `scripts/extraer_pagina.py` y se leyó completa, tanto la versión de X como la de Edge. Las tablas que el extractor aplanaba se reconstruyeron desde el HTML crudo. Las contradicciones internas de Google se documentan en el archivo afectado en lugar de elegir una versión; la lista está en [COBERTURA.md](COBERTURA.md#discrepancias-encontradas-en-la-documentación-oficial).

### Errores corregidos en la tercera pasada

| Error | Corrección |
|---|---|
| PromptTokenLimit descrito como tope de tamaño por petición | Es una **tasa** de tokens por segundo o minuto |
| `llmQuota.*` atribuido a un atributo personalizado | Sale de la configuración de cuota LLM del API product |
| Políticas de Model Armor descritas como no bloqueantes por defecto | **Sí bloquean** por defecto (`FilterMatched`, 400); solo dejan de hacerlo con `continueOnError="true"` |
| DeleteOAuthV2Info presentada como revocación | **Borra** el token; revocar es RevokeOAuthV2 |
| JSONThreatProtection con `<Expression>` como atributo | Es un elemento hijo |
| XMLThreatProtection presentada como defensa contra *billion laughs* y XXE | La página oficial no lo afirma; se eliminó la afirmación y se añadió la dependencia del `Content-Type` |
| MessageValidation y PythonScript como inexistentes en X | Existen en X/hybrid (`<MessageValidation>`, `<Script>`) |
| `<ReasonPhrase>` en 13 ejemplos de X | X no lo documenta en AssignMessage ni RaiseFault (solo Edge); eliminado |
| Parámetros de FlowCallout leídos como `flowcallout.{política}.{param}` | Se leen por el **nombre exacto** del parámetro, sin prefijo |
| «Límite de 11 MB» de MessageLogging como límite exigido | Aplicación «planificada»; con Cloud Logging el tope real es 256 KB por entrada |
| Impacto del antipatrón «MessageLogging varias veces» descrito como logs desordenados | Conexiones y handshakes TLS extra, contrapresión en el MP (504) y logs perdidos en errores |
| `waitForComplete()`: «usa ServiceCallout, lo dice el antipatrón» | El antipatrón recomienda **callbacks** (tope del 30 % de hilos JavaScript); ServiceCallout lo recomienda la guía de buenas prácticas |
| ExternalCallout con `<Timeout>` | Es `<TimeoutMs>` |
| DataCapture con `<Source>` directamente bajo `<Capture>` | Es `<Collect ref>` o un hijo de extracción de `<Collect>` |
| SetIntegrationRequest con `<TriggerName>`, sin región y con `clearPayload` | Es `<ApiTrigger>`, `<IntegrationRegion>` es obligatorio y `clearPayload` pertenece al `<Request>` de IntegrationCallout |
| Catálogo: SOAPMessageValidation con elemento `<SOAPMessageValidation>` | El elemento es `<MessageValidation>` |
| Catálogo: fechas de OAuthV1 aparentemente contradictorias | Dos anuncios distintos: Edge Cloud (2018) y Private Cloud (2020) |
| Ejemplos de logging con `response.status.code` y timestamps etiquetados como latencias | `message.status.code` (válido también tras un error) y nombres `*_ts` |

### Cuarta pasada (23 de octubre de 2026): áreas que faltaban en X/hybrid

Se escribieron **23 documentos nuevos**, en `docs/11-hybrid/`, `12-api-hub/`, `13-advanced-api-security/`, `14-troubleshooting/`, `15-administracion/`, `16-adaptadores/` y `04-publicacion/03-monetizacion.md`. Se usó el mismo método de la tercera pasada: se descargaron con `scripts/extraer_pagina.py` unas 360 páginas oficiales, todas leídas, y en cada documento se dejan las fuentes con su fecha de consulta.

Estos documentos son **síntesis**, no copias página a página. Los procedimientos paso a paso (comandos completos de instalación de hybrid, pantallas de la UI de API hub) remiten a la guía oficial de cada versión.

**Errores corregidos en documentos previos:**

| Error | Corrección |
|---|---|
| Varios códigos de error inexistentes en `10-referencia/02-codigos-de-error.md`: `IssuerMismatch`, `AudienceMismatch`, `ApplicationNotApproved`, `insufficient_scope`, `NoRoutesMatched` y `ExecutionFailed` para JavaScript y JavaCallout | Reemplazados por los oficiales: `JwtIssuerMismatch`, `JwtAudienceMismatch`, `invalid_client-app_not_approved`, `InsufficientScope`, `ScriptExecutionFailed` y `ExecutionError`. `NoRoutesMatched` se eliminó. |
| `SslHandshakeFailed` documentado con HTTP 502 | Es **503**, según el catálogo oficial de runtime |
| `ConcurrentRatelimtViolation` en la plantilla de FaultRules | Eliminado: la política está retirada y nunca existió en X |
| Propiedades de TargetEndpoint sin defaults | Defaults verificados: `connect.timeout.millis` 3 s, `io.timeout.millis` 55 s, `keepalive.timeout.millis` 60 s en X. Se añade la regla de que el keep-alive de Apigee debe ser menor que el del backend. |

### Quinta pasada (23 de octubre de 2026): ejemplos

- **Mapa de ejemplos:** los cuatro repositorios oficiales se clonaron en un directorio temporal y **solo se leyeron**, sin ejecutar nada. Las políticas de cada ejemplo se extrajeron de sus XML con `scripts/mapa_ejemplos.py`. Las descripciones son síntesis propias, a partir de los README de cada repositorio.
- **Bundles propios:** se escribieron a partir de las referencias de política de este repo y se validaron con `scripts/validar_bundles.py` y con `apigeelint` 2.85.1 (0 errores). **No se desplegaron** en una organización: es una validación estática.
- **Correcciones:**
  - `apigee/openbank` está hecho para Edge, no para X (`HostedTarget`, API de gestión de Edge).
  - En OAuthV2, un token pedido sin `scope` recibe todos los scopes de la app. Se añadió a la referencia.

---

## Nivel A — Verificado contra fuente oficial

Contenido extraído de páginas oficiales de Google consultadas directamente (fetch o
navegador) que devolvieron contenido sustantivo, o de código publicado por Google.

| Contenido | Cómo se verificó |
|---|---|
| Todos los valores numéricos de [límites](docs/10-referencia/01-limites.md) | Fetch directo a la página de límites |
| Lista completa de mejores prácticas de [diseño y desarrollo](docs/08-mejores-practicas/01-diseno-y-desarrollo.md) | Fetch directo |
| Referencia de [variables de flujo](docs/01-proxies/04-variables-de-flujo.md) | Fetch directo |
| Tabla de operadores de [condiciones](docs/01-proxies/03-condiciones.md) | Fetch directo |
| Mecánica de [FaultRules](docs/05-operacion/01-manejo-de-errores.md) | Fetch directo |
| Los 21 [antipatrones](docs/09-antipatrones/01-catalogo-antipatrones.md): títulos y agrupación | Fetch directo |
| XML de las [políticas de IA](docs/02-politicas/05-politicas-ai.md) | Código real de `GoogleCloudPlatform/apigee-samples` (Apache 2.0) |
| **[Catálogo completo de políticas](docs/02-politicas/00-catalogo-de-politicas.md)**, con clasificación Standard/Extensible | Navegador — página completa, incluida la nota sobre implicaciones de coste y tipo de entorno |
| **[API products](docs/04-publicacion/01-api-products.md)**: modelo completo, requisito Pay-as-you-go, tabla de operaciones, pasos de verificación de credenciales, niveles de acceso | Navegador — página completa |
| **[Shared flows](docs/01-proxies/06-shared-flows-y-flow-hooks.md)** y **flow hooks**: desarrollo, despliegue, manejo de fallos, permisos de administrador, límite de un shared flow por hook | Navegador — dos páginas completas |
| **[Anatomía de un API proxy](docs/01-proxies/01-anatomia-api-proxy.md)**: ProxyEndpoint/TargetEndpoint, tipos de proxy Standard/Extensible, revisiones | Navegador — página completa (la URL original daba 404; se encontró la correcta) |
| **[Ciclo de vida de la API](docs/06-devops/01-ciclo-de-vida.md)**: desarrollo cloud/local, tipos de despliegue, keys por entorno, `environment.name` | Navegador — página completa |
| **[Debug y Trace](docs/05-operacion/02-debug-trace.md)**: timeout, count por Message Processor, retraso de activación, retención | Navegador — página completa |
| **[MCP en Apigee](docs/07-ai-gateway/02-mcp-en-apigee.md)**: documento nuevo, íntegramente verificado | Navegador — dos páginas completas (overview y quickstart) |
| Fechas de EOL de Apigee Edge Private Cloud (4.53, 4.53.01, 4.52.x) y fecha de apagado de la Classic UI | Navegador — dos páginas completas de `docs.apigee.com` y `docs.cloud.google.com/apigee/docs/deprecations` |
| Introducción a OAuth 2.0: roles, los cuatro grant types | Navegador — página completa (confirma el contenido ya escrito) |
| `XSLTransform` (`<XSL>`) y `TraceCapture`: elemento XML, tipo Extensible, procesador Saxon | Navegador — páginas de referencia de cada política |
| **Áreas 11 a 16 y monetización**: hybrid, API hub, Advanced API Security, troubleshooting, administración, adaptadores | Páginas oficiales leídas completas (cuarta pasada); las fuentes están en cada documento |
| **[Referencia por política](docs/02-politicas/referencia/00-indice.md)**: los 71 archivos | Página oficial de X y de Edge leída completa, descargada con `scripts/extraer_pagina.py` (tercera pasada) |

---

## Nivel B — Fuente oficial no accesible; escrito desde conocimiento del modelo

Documentos que **no** se pudieron verificar en la segunda pasada, por no formar parte del
alcance revisado. Siguen sin confirmación directa página por página.

| Documento | Nota |
|---|---|
| [Developers y apps](docs/04-publicacion/02-developers-apps.md) | No revisado en la segunda pasada |
| [OAuth 2.0](docs/03-seguridad/02-oauth2.md) — más allá de la introducción general | La prosa general sigue siendo de nivel B, pero las operaciones de la política ya están verificadas en [oauthv2.md](docs/02-politicas/referencia/oauthv2.md) y en las referencias de Get/Set/Delete/RevokeOAuthV2 (tercera pasada). Ante una diferencia, manda la referencia |
| [JWT/JWS](docs/03-seguridad/03-jwt-jws.md) | La prosa general sigue siendo de nivel B; las seis políticas ya están verificadas en `docs/02-politicas/referencia/` (tercera pasada). Ante una diferencia, manda la referencia |
| [TLS/mTLS](docs/03-seguridad/04-tls-mtls.md) | No se consultó `keystores-truststores` en esta pasada |
| [Analytics y monitoreo](docs/05-operacion/03-analytics-monitoreo.md) | No revisado en la segunda pasada, salvo los límites (Nivel A) |

---

## Nivel C — Derivado de resúmenes de búsqueda con fuentes mixtas

Ya no queda contenido en este nivel: el único elemento que lo ocupaba (las fechas de EOL
de Apigee Edge) se verificó directamente en la segunda pasada y ascendió a Nivel A.

---

## Nivel D — Autoría propia (criterio técnico, no doctrina oficial)

Una parte sustancial del repositorio sigue siendo **síntesis y criterio técnico
originales**: coherente con la documentación oficial, pero Google no lo dice así.
Trátalo como recomendación, no como norma.

Incluye:

- Casi todos los **ejemplos XML** salvo los de políticas de IA: las 10 [recetas](docs/02-politicas/06-recetas-xml.md), y la mayoría de configuraciones de política de `02-politicas/` y `03-seguridad/`.
- El **[pipeline de CI/CD](docs/06-devops/03-cicd-github-actions.md)** completo con Workload Identity Federation.
- La arquitectura de referencia del **[AI gateway "clásico"](docs/07-ai-gateway/01-apigee-como-ai-gateway.md)** (gobierno de tráfico saliente hacia un LLM) — distinto de MCP, que sí es Nivel A.
- Los **[checklists](docs/08-mejores-practicas/04-checklist-produccion.md)** de producción y de rendimiento.
- La **tabla de prefijos de nombres** de [convenciones](docs/08-mejores-practicas/02-convenciones-de-nombres.md).
- Las **tablas de diagnóstico por síntoma** de [códigos de error](docs/10-referencia/02-codigos-de-error.md).
- El ranking de **"los 15 límites que más veces te van a morder"**.
- La comparativa **KVM vs PropertySet**, las tablas de coste relativo de políticas, y el matiz sobre "un producto por proxy" (ver tabla de correcciones arriba).

---

## Cómo verificar

Cada documento lleva su enlace canónico en el frontmatter. Antes de llevar algo de aquí
a producción:

1. **Nombres de elemento XML y atributos** → verifica en la página de referencia de esa política. El [catálogo](docs/02-politicas/00-catalogo-de-politicas.md) ahora distingue Standard/Extensible con la clasificación oficial, pero cada política individual conserva su propio nivel de detalle sin verificar salvo las listadas arriba en Nivel A.
2. **Valores numéricos de límites** → Nivel A, pero verifica igualmente si tu decisión depende de un número exacto: los límites cambian.
3. **Fechas de EOL y deprecaciones** → Nivel A a fecha de esta revisión (2026-08-20). Vuelve a comprobar si ha pasado tiempo.
4. **Todo lo de Nivel D** → es criterio, no norma. Adáptalo.

Si encuentras una discrepancia, **gana la documentación oficial**. Abre un PR: ver [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Nota sobre `docs.apigee.com`

Varias de las extracciones de Nivel A proceden de `docs.apigee.com`, que es la
documentación de **Apigee Edge**, la plataforma legacy en fin de vida.

Esas páginas de referencia (variables de flujo, condiciones, manejo de fallos, mejores
prácticas, fechas de EOL) siguen siendo **conceptualmente válidas para Apigee X** o son
la fuente correcta para el propio ciclo de vida de Edge. Pero contienen elementos que
**no existen en Apigee X**: virtual hosts, Node.js/Trireme, la política `Script` de
Python, `apigeetool`, `ConcurrentRateLimit`, propiedades de Private Cloud como
`HTTPResponse.body.buffer.limit`.

En este repositorio esos elementos están marcados con **⚠️ Solo Edge** o en la tabla de
[políticas retiradas](docs/02-politicas/00-catalogo-de-politicas.md#políticas-retiradas-o-exclusivas-de-apigee-edge).
Si encuentras alguno sin marcar, es un error: abre un issue.
