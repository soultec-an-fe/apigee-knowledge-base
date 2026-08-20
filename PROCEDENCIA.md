# Procedencia del contenido

> [!IMPORTANT]
> **No todo este repositorio procede de la documentación oficial de Google.**
> Este documento clasifica cada parte según su nivel de respaldo, para que puedas
> saber qué puedes citar como doctrina oficial y qué debes verificar tú.

El campo `fuente:` del frontmatter indica **el enlace canónico del tema**, no que ese
documento sea una transcripción de esa página. Usa la clasificación de abajo para
saber el nivel real de verificación.

---

## Nivel A — Verificado contra fuente oficial

Contenido extraído de páginas oficiales de Google que se consultaron directamente y
devolvieron contenido sustantivo, o de código publicado por Google.

| Contenido | Fuente consultada |
|---|---|
| **Todos los valores numéricos** de [límites](docs/10-referencia/01-limites.md) | `cloud.google.com/apigee/docs/api-platform/reference/limits` |
| **Lista completa de mejores prácticas** de [diseño y desarrollo](docs/08-mejores-practicas/01-diseno-y-desarrollo.md) | `docs.apigee.com/api-platform/fundamentals/best-practices-api-proxy-design-and-development` |
| **Referencia de [variables de flujo](docs/01-proxies/04-variables-de-flujo.md)** por prefijo | `docs.apigee.com/api-platform/reference/variables-reference` |
| **Tabla de operadores** de [condiciones](docs/01-proxies/03-condiciones.md) | `docs.apigee.com/api-platform/reference/conditions-reference` |
| **Mecánica de FaultRules**: orden de evaluación invertido Proxy/Target, `AlwaysEnforce`, precedencia RaiseFault/FaultRule, `continueOnError` | `docs.apigee.com/api-platform/fundamentals/fault-handling` |
| **Los 21 [antipatrones](docs/09-antipatrones/01-catalogo-antipatrones.md)**: títulos y agrupación | `cloud.google.com/apigee/docs/api-platform/antipatterns/intro` |
| **XML de las [políticas de IA](docs/02-politicas/05-politicas-ai.md)**: `SemanticCacheLookup`, `SemanticCachePopulate`, `LLMTokenQuota`, `SanitizeUserPrompt`, `SanitizeModelResponse`, variables `matchState` de Model Armor | [`GoogleCloudPlatform/apigee-samples`](https://github.com/GoogleCloudPlatform/apigee-samples) (Apache 2.0) |
| Parte del [catálogo de políticas](docs/02-politicas/00-catalogo-de-politicas.md) | `cloud.google.com/apigee/docs/api-platform/reference/policies/reference-overview-policy` |
| Organizaciones (paid/eval), environment groups como mecanismo de enrutamiento por hostname | Búsqueda restringida a `cloud.google.com` |

---

## Nivel B — Fuente oficial no accesible; escrito desde conocimiento del modelo

Varias páginas de la documentación de Google **se renderizan con JavaScript** y al
consultarlas solo devolvieron el menú de navegación, sin contenido. En esos casos el
documento se escribió desde conocimiento general del modelo y **no se pudo verificar
página por página**.

| Documento | Qué pasó |
|---|---|
| [API products](docs/04-publicacion/01-api-products.md) | `what-api-product` devolvió contenido genérico, no la referencia real |
| [Shared flows y flow hooks](docs/01-proxies/06-shared-flows-y-flow-hooks.md) | `shared-flows` devolvió contenido parcial |
| [Ciclo de vida](docs/06-devops/01-ciclo-de-vida.md) | `api-development-lifecycle` devolvió sobre todo navegación |
| [Anatomía de un API proxy](docs/01-proxies/01-anatomia-api-proxy.md) | `what-api-proxy` devolvió **HTTP 404** |
| [Apigee como AI Gateway](docs/07-ai-gateway/01-apigee-como-ai-gateway.md) | `ai-capabilities` devolvió solo navegación |
| [Developers y apps](docs/04-publicacion/02-developers-apps.md) | No se consultó la página específica |
| [Debug y Trace](docs/05-operacion/02-debug-trace.md) | No se consultó; los límites sí son de Nivel A |
| [OAuth 2.0](docs/03-seguridad/02-oauth2.md), [JWT/JWS](docs/03-seguridad/03-jwt-jws.md), [TLS/mTLS](docs/03-seguridad/04-tls-mtls.md) | No se consultaron las páginas de referencia de esas políticas |

> [!WARNING]
> **El [catálogo de políticas](docs/02-politicas/00-catalogo-de-politicas.md) es una fusión.**
> El listado que devolvió la página oficial estaba incompleto: no incluía `Quota`,
> `ConcurrentRateLimit`, `ResetQuota`, `XMLThreatProtection`,
> `RegularExpressionProtection`, `SAMLAssertion`, `XSL` ni `StatisticsCollector`.
> Esas entradas se añadieron desde conocimiento del modelo. Verifica el nombre exacto
> del elemento XML en su página de referencia antes de usarlo en producción.

---

## Nivel C — Derivado de resúmenes de búsqueda con fuentes mixtas

| Contenido | Advertencia |
|---|---|
| **Fechas de fin de vida de Apigee Edge** en [ediciones](docs/00-fundamentos/02-ediciones-y-comparativa.md): Private Cloud 4.53 → 11 abril 2026; 4.53.01 → 26 febrero 2027; Classic UI → 2 noviembre 2025 | Proceden de un **resumen de búsqueda** que mezclaba documentación de Apigee con blogs de terceros. **No se verificaron con un acceso directo** a `docs.apigee.com/release/deprecated-features`. Verifícalas antes de planificar una migración. |

---

## Nivel D — Autoría propia (criterio técnico, no doctrina oficial)

Una parte sustancial del repositorio es **síntesis y criterio técnico originales**.
Es contenido razonado y coherente con la documentación oficial, pero **Google no lo
dice así**. Trátalo como recomendación, no como norma.

Incluye:

- **Casi todos los ejemplos XML**, salvo los de políticas de IA: las 10 [recetas](docs/02-politicas/06-recetas-xml.md), y la mayoría de configuraciones de política de los documentos de `02-politicas/` y `03-seguridad/`.
- El **[pipeline de CI/CD](docs/06-devops/03-cicd-github-actions.md)** completo con Workload Identity Federation, validaciones y rollback.
- La **[arquitectura de referencia del AI gateway](docs/07-ai-gateway/01-apigee-como-ai-gateway.md)** y su composición de proxy.
- Los **[checklists](docs/08-mejores-practicas/04-checklist-produccion.md)** de producción y de rendimiento.
- La **tabla de prefijos de nombres** de [convenciones](docs/08-mejores-practicas/02-convenciones-de-nombres.md) — Google solo documenta el principio ("usa prefijos consistentes") y el ejemplo `AM-xxx`.
- Las **tablas de diagnóstico por síntoma** de [códigos de error](docs/10-referencia/02-codigos-de-error.md).
- El ranking de **"los 15 límites que más veces te van a morder"**.
- La comparativa **KVM vs PropertySet** y las tablas de coste relativo de políticas.
- Las recomendaciones de **orden del PreFlow** y de colocación de políticas.
- Las tablas de **"cuándo usar cada cosa"** repartidas por todo el repositorio.
- Los **códigos de error**: la agrupación y los HTTP sugeridos son criterio propio. Los `fault.name` concretos son conocimiento del modelo, **no** una transcripción de la referencia por política.

---

## Cómo verificar

Cada documento lleva su enlace canónico en el frontmatter:

```yaml
fuente: https://cloud.google.com/apigee/docs/...
revisado: 2026-08-20
```

Antes de llevar algo de aquí a producción:

1. **Nombres de elemento XML y atributos** → verifica en la página de referencia de esa política.
2. **Valores numéricos de límites** → verifica en <https://cloud.google.com/apigee/docs/api-platform/reference/limits>.
3. **Fechas de EOL y deprecaciones** → verifica en <https://docs.apigee.com/release/deprecated-features>.
4. **Todo lo de Nivel D** → es criterio, no norma. Adáptalo.

Si encuentras una discrepancia, **gana la documentación oficial**. Abre un PR: ver [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Nota sobre `docs.apigee.com`

Varias de las extracciones de Nivel A proceden de `docs.apigee.com`, que es la
documentación de **Apigee Edge**, la plataforma legacy en fin de vida.

Esas páginas de referencia (variables de flujo, condiciones, manejo de fallos,
mejores prácticas) siguen siendo **conceptualmente válidas para Apigee X** y son la
versión más completa disponible en texto plano. Pero contienen elementos que **no
existen en Apigee X**: virtual hosts, Node.js/Trireme, la política `Script` de Python,
`apigeetool`, propiedades de Private Cloud como `HTTPResponse.body.buffer.limit`.

En este repositorio esos elementos están marcados con **⚠️ Solo Edge**. Si encuentras
alguno sin marcar, es un error: abre un issue.
