---
id: apihub-modelo
titulo: API hub — modelo de datos, aprovisionamiento y límites
area: api-hub
tags: [api-hub, catalogo, gobierno, api-resource, versiones, specs, deployments, attributes, mcp, cmek, roles]
aplica_a: [apigee-x, apigee-hybrid]
fuente: https://docs.cloud.google.com/apigee/docs/apihub/apis-intro
revisado: 2026-10-23
---

# API hub — modelo de datos, aprovisionamiento y límites

> **Fecha de corte: 23 de octubre de 2026.**

**Apigee API hub** es el **catálogo central** de las APIs de una organización. Registra APIs de Apigee, de otros gateways (Apigee Edge, AWS API Gateway, Azure API Management) y APIs sin gateway, con sus versiones, especificaciones, despliegues, dependencias y metadatos de gobierno. No ejecuta tráfico: es un registro.

## Modelo de datos

| Entidad | Qué representa |
|---|---|
| **API (API resource)** | El registro central de una API, con sus metadatos |
| **Version** | El estado de la API en un momento dado; una API tiene varias |
| **Specification** | Documento legible por máquina asociado a una versión: **OpenAPI** (REST), **Protocol Buffers** (gRPC), **WSDL** (SOAP), **esquema MCP** |
| **Operation** / **MCP tool** | Cada función de la API: operaciones HTTP en REST y SOAP, *tools* en MCP |
| **Deployment** | Dónde se ejecuta una versión: tipo (Apigee, hybrid, Edge Private Cloud…), *Resource URI* y endpoints. Una versión puede tener varios despliegues (dev, UAT, prod) y un despliegue, varias versiones. |
| **Attribute** | Pares clave/valor. Los de **sistema** son predefinidos (API style, Target users, Maturity level…); los **adicionales** los defines tú. |
| **Dependency** | Relación dirigida **consumidor → proveedor** entre operaciones o APIs externas (*API supply chain*) |

**Análisis de especificaciones:**

- Solo se analizan **OpenAPI 2.0, 3.0 y 3.1, en JSON o YAML**, para extraer operaciones de APIs de estilo `REST`, y **esquemas MCP**, para extraer *tools*.
- Los WSDL y proto se guardan, pero no generan operaciones.

**Para despliegues de Apigee**, Google recomienda que el *Resource URI* siga el formato `organizations/{org}/environments/{env}/apis/{proxy}`.

> [!IMPORTANT]
> En proxies de Apigee con varias revisiones, API hub **solo usa la especificación de la última revisión desplegada** para generar operaciones y *tools*. Lo mismo ocurre con los proxies MCP.

## Cómo entran las APIs

1. **Auto-registro al adjuntar un proyecto de runtime** (Apigee, hybrid o API Gateway). Ver [integraciones](02-integraciones-y-funciones.md).
2. **Plugins** para otros gateways (Edge, AWS, Azure) o **plugins propios**.
3. **Registro manual**, en la UI o por API, con metadatos y especificación.

## MCP como estilo de API

API hub trata **MCP** como un estilo de API de primera clase:

- Importa automáticamente los **proxies MCP** de la organización de Apigee asociada (ver [MCP en Apigee](../07-ai-gateway/02-mcp-en-apigee.md)).
- Analiza sus especificaciones para extraer *tools*.

Limitaciones:

- El tipo de especificación cambia a MCP, pero el archivo OAS subyacente **no se convierte** al esquema MCP.
- Las *tools* MCP **no se pueden crear desde la consola**: solo por API.
- No hay análisis de dependencias entre *tools* MCP.

## Aprovisionamiento

- **Una instancia de API hub por *host project*.** El *host project* es un proyecto de tu organización de Apigee que actúa como consumidor de todos los recursos de API hub.
- **Métodos:** consola (el recomendado), CLI o Terraform. Si aprovisionas API hub junto con Apigee, adjunta automáticamente los proyectos de runtime asociados.
- **Roles para aprovisionar:**
  - `roles/serviceusage.serviceUsageAdmin`;
  - `roles/serviceusage.serviceUsageViewer`;
  - `roles/cloudkms.admin`;
  - `roles/apihub.provisioningAdmin`;
  - `roles/resourcemanager.projectIamAdmin`.
- **Ubicación y residencia de datos:**
  - Se elige la **región de la instancia** y, si activas la búsqueda semántica, la **multirregión de los datos de búsqueda**, donde se aprovisiona Vertex AI.
  - Si el proyecto ya tiene una organización de Apigee, esta no debe tener la restricción de política *Resource Location Restriction*.
  - API hub usa Cloud Scheduler: donde no está disponible, se usa una región de respaldo.
- **Cifrado:** clave gestionada por Google o **CMEK**.

> [!CAUTION]
> **Con CMEK:** si la clave se deshabilita o deja de estar disponible durante **más de 7 días**, **todos los datos de la instancia se borran de forma permanente** y la instancia queda inutilizable. Vigila la rotación y los permisos de la clave como un servicio crítico.

## Límites

| Recurso | Límite |
|---|---|
| Tamaño máximo de un recurso indexable para búsqueda | 2,5 MB |
| Valores de un atributo de tipo enum | 1000 |
| Valores de un atributo | 20 |
| Tamaño de un archivo de especificación | **10 MB** |

## Roles de API hub

| Rol | Uso |
|---|---|
| `roles/apihub.admin` | Administración completa |
| `roles/apihub.editor` | Crear y editar APIs, versiones, especificaciones… |
| `roles/apihub.viewer` | Solo lectura |
| `roles/apihub.attributeAdmin` | Gestionar atributos |
| `roles/apihub.pluginAdmin` | Gestionar plugins e instancias |
| `roles/apihub.runTimeProjectAttachmentsEditor` | Adjuntar proyectos de runtime |
| `roles/apihub.addonsAdmin` | Gestionar add-ons (búsqueda semántica, *spec boost*…) |
| `roles/apihub.apiInsightsViewer` | Ver API insights |
| `roles/apihub.provisioningAdmin` | Aprovisionar la instancia |
| `roles/apihub.runtimeProjectServiceAgent` | Rol del agente de servicio del proyecto de runtime |

## Fuentes

Todas consultadas directamente el 2026-10-23:

- API resources overview: <https://docs.cloud.google.com/apigee/docs/apihub/apis-intro>, contenido completo.
- Specifications overview: <https://docs.cloud.google.com/apigee/docs/apihub/specs-intro>, contenido completo.
- Deployments overview: <https://docs.cloud.google.com/apigee/docs/apihub/deployments-intro>, contenido completo.
- Operations and MCP tools: <https://docs.cloud.google.com/apigee/docs/apihub/operations-intro>, contenido completo.
- Register MCP APIs: <https://docs.cloud.google.com/apigee/docs/apihub/register-mcp-apis>, contenido completo.
- Provision API hub: <https://docs.cloud.google.com/apigee/docs/apihub/provision>, requisitos, *host project* y CMEK.
- Locations: <https://docs.cloud.google.com/apigee/docs/apihub/locations>, residencia de datos.
- Limits: <https://docs.cloud.google.com/apigee/docs/apihub/limits>, contenido completo.
- IAM roles: <https://docs.cloud.google.com/apigee/docs/apihub/iam-roles>, lista de roles.
