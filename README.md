# Apigee Knowledge Base

> Base de conocimiento estructurada sobre **Google Apigee** (API Management), escrita en Markdown y optimizada para que un **LLM** la consuma como contexto.

[![Docs](https://img.shields.io/badge/docs-markdown-blue)](docs/)
[![Apigee](https://img.shields.io/badge/Apigee-X%20%7C%20hybrid-4285F4)](https://cloud.google.com/apigee)
[![License](https://img.shields.io/badge/license-CC--BY--4.0-green)](LICENSE)

---

## Qué es esto

Un corpus de documentación técnica sobre Apigee organizado para **RAG, agentes y asistentes de código**:

- **Un tema por archivo**, con frontmatter YAML (`id`, `tags`, `fuentes`) para filtrar y citar.
- **Rutas predecibles y numeradas** (`docs/NN-area/NN-tema.md`) para que la navegación sea determinista.
- **XML bien formado y validado** en todos los ejemplos, listo para copiar en un bundle `apiproxy/`.
- **Sin imágenes ni diagramas** que carguen información esencial: todo es texto, tablas y código.
- **Enlace al tema canónico** de Google en cada documento — no todo el contenido procede de ahí, ver [PROCEDENCIA.md](PROCEDENCIA.md).

> [!IMPORTANT]
> Este repositorio es material **derivado y sintetizado**, no una copia de la documentación de Google.
> La fuente de verdad siempre es <https://cloud.google.com/apigee/docs>. Ver [Fuentes oficiales](docs/10-referencia/03-fuentes-oficiales.md).
>
> **No todo el contenido está verificado contra la documentación oficial en el mismo grado.** Antes de citar algo como norma de Google, consulta [PROCEDENCIA.md](PROCEDENCIA.md), que clasifica cada sección por nivel de respaldo (verificado / no accesible en el momento de escribirlo / criterio propio).

---

## Cómo lo usa un LLM

| Escenario | Qué cargar |
|---|---|
| Contexto mínimo | [`llms.txt`](llms.txt) + [`docs/00-fundamentos/`](docs/00-fundamentos/) |
| Escribir un proxy | [`01-proxies/`](docs/01-proxies/) + [`02-politicas/00-catalogo-de-politicas.md`](docs/02-politicas/00-catalogo-de-politicas.md) |
| Revisar código Apigee | [`08-mejores-practicas/`](docs/08-mejores-practicas/) + [`09-antipatrones/`](docs/09-antipatrones/) |
| Diseñar seguridad | [`03-seguridad/`](docs/03-seguridad/) |
| CI/CD | [`06-devops/`](docs/06-devops/) |
| Gateway de IA / LLM | [`07-ai-gateway/`](docs/07-ai-gateway/) |
| Diagnosticar un error | [`05-operacion/01-manejo-de-errores.md`](docs/05-operacion/01-manejo-de-errores.md) + [`10-referencia/01-limites.md`](docs/10-referencia/01-limites.md) |

Clonado completo como contexto:

```bash
git clone https://github.com/festem200/apigee-knowledge-base.git
cat apigee-knowledge-base/docs/**/*.md > contexto-apigee.md
```

---

## Índice

### 00 · Fundamentos
- [Qué es Apigee](docs/00-fundamentos/01-que-es-apigee.md)
- [Ediciones: X, hybrid y Edge (EOL)](docs/00-fundamentos/02-ediciones-y-comparativa.md)
- [Arquitectura del runtime](docs/00-fundamentos/03-arquitectura.md)
- [Organizaciones, entornos y grupos de entorno](docs/00-fundamentos/04-organizaciones-entornos-grupos.md)
- [Glosario](docs/00-fundamentos/05-glosario.md)

### 01 · Proxies de API
- [Anatomía de un API proxy](docs/01-proxies/01-anatomia-api-proxy.md)
- [Flujos y pipeline de ejecución](docs/01-proxies/02-flujos-y-pipeline.md)
- [Condiciones y pattern matching](docs/01-proxies/03-condiciones.md)
- [Variables de flujo](docs/01-proxies/04-variables-de-flujo.md)
- [TargetEndpoints, TargetServers y balanceo](docs/01-proxies/05-target-endpoints-y-servidores.md)
- [Shared flows y flow hooks](docs/01-proxies/06-shared-flows-y-flow-hooks.md)

### 02 · Políticas
- [Catálogo completo de políticas](docs/02-politicas/00-catalogo-de-politicas.md)
- [Traffic Management](docs/02-politicas/01-traffic-management.md)
- [Seguridad](docs/02-politicas/02-seguridad.md)
- [Mediación](docs/02-politicas/03-mediacion.md)
- [Extensión y código personalizado](docs/02-politicas/04-extension.md)
- [Políticas de IA](docs/02-politicas/05-politicas-ai.md)
- [Recetas XML listas para usar](docs/02-politicas/06-recetas-xml.md)

### 03 · Seguridad
- [API keys y VerifyAPIKey](docs/03-seguridad/01-apikeys.md)
- [OAuth 2.0](docs/03-seguridad/02-oauth2.md)
- [JWT y JWS](docs/03-seguridad/03-jwt-jws.md)
- [TLS, mTLS y keystores](docs/03-seguridad/04-tls-mtls.md)
- [Threat protection](docs/03-seguridad/05-threat-protection.md)

### 04 · Publicación
- [API products](docs/04-publicacion/01-api-products.md)
- [Developers, apps y AppGroups](docs/04-publicacion/02-developers-apps.md)

### 05 · Operación
- [Manejo de errores y FaultRules](docs/05-operacion/01-manejo-de-errores.md)
- [Debug y Trace](docs/05-operacion/02-debug-trace.md)
- [Analytics y monitoreo](docs/05-operacion/03-analytics-monitoreo.md)
- [Caching y persistencia](docs/05-operacion/04-caching-y-persistencia.md)

### 06 · DevOps
- [Ciclo de vida de la API](docs/06-devops/01-ciclo-de-vida.md)
- [apigeecli y herramientas](docs/06-devops/02-herramientas-cli.md)
- [CI/CD con GitHub Actions](docs/06-devops/03-cicd-github-actions.md)

### 07 · AI Gateway
- [Apigee como gateway de LLM](docs/07-ai-gateway/01-apigee-como-ai-gateway.md)
- [Model Context Protocol (MCP) en Apigee](docs/07-ai-gateway/02-mcp-en-apigee.md)

### 08 · Mejores prácticas
- [Diseño y desarrollo](docs/08-mejores-practicas/01-diseno-y-desarrollo.md)
- [Convenciones de nombres](docs/08-mejores-practicas/02-convenciones-de-nombres.md)
- [Rendimiento](docs/08-mejores-practicas/03-rendimiento.md)
- [Checklist de producción](docs/08-mejores-practicas/04-checklist-produccion.md)

### 09 · Antipatrones
- [Catálogo de antipatrones](docs/09-antipatrones/01-catalogo-antipatrones.md)

### 10 · Referencia
- [Límites de la plataforma](docs/10-referencia/01-limites.md)
- [Códigos de error](docs/10-referencia/02-codigos-de-error.md)
- [Fuentes oficiales](docs/10-referencia/03-fuentes-oficiales.md)

---

## Convenciones del repositorio

Cada documento empieza con frontmatter YAML:

```yaml
---
id: politicas-traffic-management
titulo: Políticas de Traffic Management
area: politicas
tags: [quota, spikearrest, rate-limiting]
aplica_a: [apigee-x, apigee-hybrid]
fuente: https://cloud.google.com/apigee/docs/...
revisado: 2026-08-20
---
```

- `aplica_a` distingue **Apigee X / hybrid** de **Apigee Edge** (legacy, en EOL).
- Los bloques marcados `⚠️ Solo Edge` no aplican a instalaciones nuevas.

## Licencia

Contenido bajo [CC BY 4.0](LICENSE). Apigee y Google Cloud son marcas de Google LLC; este proyecto no está afiliado a Google.
