---
id: apihub-integraciones
titulo: API hub — auto-registro, plugins, curación y funciones avanzadas
area: api-hub
tags: [api-hub, auto-registro, plugins, curation, fingerprint, api-observations, shadow-apis, api-insights, spec-boost, supply-chain, multi-gateway]
aplica_a: [apigee-x, apigee-hybrid, apigee-edge]
fuente: https://docs.cloud.google.com/apigee/docs/apihub/plugins
revisado: 2026-10-23
---

# API hub — auto-registro, plugins, curación y funciones avanzadas

> **Fecha de corte: 23 de octubre de 2026.** Modelo de datos y aprovisionamiento en [01](01-modelo-y-aprovisionamiento.md).

## Auto-registro desde proyectos de Google Cloud

Al **adjuntar un proyecto de runtime** se crea una *project association*, y API hub descubre y registra sus APIs automáticamente:

| Servicio | Qué se ingiere |
|---|---|
| **Apigee y Apigee hybrid** | Proxies **desplegados**, con sus especificaciones OpenAPI |
| **API Gateway** | Definiciones de gateways y endpoints gestionados |

**Reglas del auto-registro con Apigee:**

- Solo se importan proxies **desplegados en un entorno que pertenezca a un environment group**.
- La **API de Apigee** debe estar habilitada en el proyecto de runtime.
- A todos los endpoints importados se les antepone `https://`.
- Si un proxy lleva una **especificación OpenAPI válida en su carpeta de recursos**, API hub la detecta, la analiza, le pasa el *linter* y la usa para documentar la API.
- **Con residencia de datos** habilitada en la organización de Apigee, **no se pueden crear instancias de plugin**.

> [!NOTE]
> Desde el **31 de julio de 2025**, la **ingestión por *pull*** ya no se admite para los plugins de Apigee y hybrid. Las instancias *pull* que ya existían siguen funcionando y se migran a *push* de forma automática. El planificador que sincronizaba cada **6 horas** solo aplica a esas instancias *pull*.

## Plugins

Un **plugin** define cómo conectarse a un tipo de fuente; una **instancia de plugin** es una conexión configurada y activa, con credenciales, curación y calendario.

| Tipo | Fuentes |
|---|---|
| **Google Cloud** (se crean al adjuntar un proyecto) | Apigee, hybrid, API Gateway |
| **Terceros** (se crean desde *Settings > Plugins*) | **Apigee Edge Public Cloud**, **Apigee Edge Private Cloud (OPDK)**, **AWS API Gateway** (Preview), **Azure API Management** (Preview) |
| **Propios** | Gateways on-premises o multinube propios |

**Ingestión:**

| Método | Dónde se usa |
|---|---|
| **Push**: la fuente envía los cambios casi en tiempo real | Todos los plugins nuevos de Apigee, hybrid y Edge (Public y Private Cloud). En AWS y Azure es opcional: requiere desplegar una Lambda o una Azure Function que reenvíe los eventos. |
| **Pull**: API hub consulta la fuente periódicamente | AWS y Azure por defecto: sincronización completa cada **6 horas** |

## Curación y *fingerprint*

La **curación** transforma y enriquece los metadatos ingeridos. También genera el **fingerprint**, el identificador único con el que se reconoce una misma API entre varios proyectos.

| Tipo | Comportamiento |
|---|---|
| **Por defecto** | Fusiona en una sola API las que tienen el **mismo *display name***. Por ejemplo, `Orders` en `project-alpha` (prod) y en `project-beta` (dev) se convierten en una API con dos despliegues. |
| **Personalizada** | Lógica propia en **Application Integration**: lee los metadatos con la API *Collect*, decide qué es duplicado, añade metadatos y transforma campos |

> [!WARNING]
> La curación por defecto **fusiona por nombre**. Si dos equipos tienen APIs distintas con el mismo nombre, o si quieres separar dev y prod como APIs diferentes, necesitas una curación personalizada (por ejemplo, prefijando el entorno).

## API observations (APIs en la sombra)

**Preview.** Es la evolución de *Shadow API Discovery* de Apigee. Analiza el tráfico de las fuentes asociadas para encontrar **APIs no documentadas o no gestionadas** y las compara con las registradas en API hub: si hay coincidencia, la API se cataloga; si no, se marca como desconocida.

- **Requisito:** el add-on [Advanced API Security](../13-advanced-api-security/01-vision-general.md).
  - En Subscription, con la organización.
  - En Pay-as-you-go, en al menos un entorno.
  - Para proyectos sin Apigee, se contrata con ventas.
- **No disponible** en entornos de evaluación.
- **Fuente soportada:** Apigee. Al adjuntar el proyecto de runtime se importan sus trabajos de observación.
- **Datos de cada observación:** hostname, número de operaciones (conocidas y desconocidas), IPs de servidor y tipo de fuente.

## API insights

Ofrece una vista unificada del tráfico y el rendimiento **de todos los gateways conectados**, con varios dashboards:

- rendimiento por gateway, por API y por target;
- análisis de errores;
- latencia por percentiles;
- **rendimiento de los LLM** (consumo de tokens);
- **rendimiento de las *tools* MCP**.

Requiere el rol `roles/apihub.apiInsightsViewer`.

## API supply chain

Modela **dependencias** dirigidas entre operaciones o APIs externas: el **consumidor** depende del **proveedor**. Por ejemplo, `Payment /debit` consume `Fraud Detection /detect`. Se ven como lista o como grafo interactivo, y sirven para análisis de impacto y para *troubleshooting*. No se admiten dependencias entre *tools* MCP.

## Add-ons de API hub

| Add-on | Qué hace |
|---|---|
| **Búsqueda semántica** | Búsqueda en lenguaje natural sobre APIs, operaciones y *tools*, con Vertex AI |
| **Specification boost** (Preview) | Genera con IA versiones **enriquecidas** de las especificaciones: más ejemplos y descripciones más claras, para que estén «listas para agentes». La habilitación tarda unos 10 minutos y procesa todas las especificaciones de forma asíncrona. **Revisa el resultado: la IA puede equivocarse.** |
| **Advanced API Security multi-gateway** | *Risk assessment*, perfiles de seguridad y condiciones de monitoreo sobre **varias organizaciones y gateways, incluido Edge**. El precio depende de la licencia de Apigee existente. |

## Fuentes

Todas consultadas directamente el 2026-10-23:

- Auto-register APIs from Google Cloud projects: <https://docs.cloud.google.com/apigee/docs/apihub/auto-register-apigee-proxies>, contenido completo.
- Plugins overview: <https://docs.cloud.google.com/apigee/docs/apihub/plugins>, contenido completo.
- Curations overview: <https://docs.cloud.google.com/apigee/docs/apihub/curations>, contenido completo.
- API observations overview: <https://docs.cloud.google.com/apigee/docs/apihub/api-observation-overview>, contenido completo.
- API insights overview: <https://docs.cloud.google.com/apigee/docs/apihub/api-insights-overview>, contenido completo.
- API supply chain: <https://docs.cloud.google.com/apigee/docs/apihub/api-supply-chain>, contenido completo.
- Specification boost: <https://docs.cloud.google.com/apigee/docs/apihub/spec-boost>, contenido completo.
- Advanced API Security for multi-gateway projects: <https://docs.cloud.google.com/apigee/docs/apihub/advanced-api-security-multi-gateway>, contenido completo.
