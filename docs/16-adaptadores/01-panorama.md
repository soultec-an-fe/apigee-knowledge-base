---
id: adaptadores-panorama
titulo: Gestionar APIs fuera de un proxy de Apigee — panorama
area: adaptadores
tags: [adaptadores, extension-processor, service-extensions, apim-operator, envoy, kubernetes, gke-gateway, pep, pdp]
aplica_a: [apigee-x, apigee-hybrid]
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/service-extensions/extension-processor-overview
revisado: 2026-10-23
---

# Gestionar APIs fuera de un proxy de Apigee — panorama

> **Fecha de corte: 23 de octubre de 2026.**

El modelo clásico de Apigee pone un **API proxy** delante del backend: el cliente llama al proxy y el proxy llama al backend. Hay tres formas oficiales de aplicar políticas de Apigee **sin** que el tráfico atraviese un proxy convencional. En las tres, el componente que recibe el tráfico actúa como **punto de aplicación** (*PEP*, *policy enforcement point*) y Apigee actúa como **punto de decisión** (*PDP*, *policy decision point*).

| Opción | PEP (quién recibe el tráfico) | Cómo se configura | Ediciones | Documento |
|---|---|---|---|---|
| **Apigee Extension Processor** | Application Load Balancer de Google Cloud (traffic extension) o Agent Gateway (authorization extension) | API de aprovisionamiento + proxy sin target en un entorno dedicado | X | [02-extension-processor.md](02-extension-processor.md) |
| **Apigee Operator for Kubernetes** | GKE Gateway (o Istio Gateway en hybrid) | Recursos de Kubernetes (CRDs) con `kubectl` y Helm | X (GA); hybrid ≥ 1.15 (**Preview**) | [03-apim-operator-kubernetes.md](03-apim-operator-kubernetes.md) |
| **Apigee Adapter for Envoy** | Envoy, nativo o como sidecar de Istio | CLI `apigee-remote-service-cli` + servicio *Apigee Remote Service* | X y hybrid (y Edge) | [04-envoy-adapter.md](04-envoy-adapter.md) |

## Cómo elegir

| Situación | Opción recomendada |
|---|---|
| El backend ya está detrás de un **Application Load Balancer** de Google Cloud y quieres API keys, cuotas, OAuth o políticas de IA sin cambiar URLs | Extension Processor |
| Gobernar las llamadas **salientes** de un agente de IA (al modelo, a herramientas, a servidores MCP) | Extension Processor con **Agent Gateway** |
| El equipo trabaja con **GKE y GitOps** y quiere declarar productos, operaciones y políticas como recursos de Kubernetes | Operator for Kubernetes (que usa el Extension Processor por debajo) |
| Servicios en una **service mesh** o fuera de Google Cloud (on-premises, otra nube) con Envoy | Adapter for Envoy |
| Necesitas mediación completa (transformaciones complejas, ServiceCallout, MessageLogging, encadenar backends) | Un **API proxy** normal: los tres mecanismos tienen limitaciones de políticas |

Esta tabla es una síntesis de este repositorio a partir de las páginas oficiales de cada opción; Google no publica una matriz de decisión conjunta.

> [!IMPORTANT]
> En el Extension Processor y en el Operator, **todo el tráfico que selecciona la extensión pasa por el mismo proxy**, sin distinción de base path. La segmentación por host o ruta se hace en la condición de la extensión (CEL) y en condiciones dentro del proxy, no con varios proxies.

## Lo que no es esto

- **Service Extensions** es un producto de Cloud Load Balancing (callouts desde el balanceador). El Extension Processor es la implementación de Apigee de una *traffic extension*.
- **ExternalCallout** es lo contrario: un proxy de Apigee que llama a un servidor gRPC propio. Ver [external-callout.md](../02-politicas/referencia/external-callout.md).
- La **Apigee Adapter for Istio** basada en Mixer está retirada (2021); su sustituto es el adapter for Envoy.

## Fuentes

- Apigee Extension Processor overview: <https://docs.cloud.google.com/apigee/docs/api-platform/service-extensions/extension-processor-overview> (consultada directamente, contenido completo, 2026-10-23).
- Apigee Operator for Kubernetes overview: <https://docs.cloud.google.com/apigee/docs/api-platform/apigee-kubernetes/apigee-apim-operator-overview> (consultada directamente, contenido completo, 2026-10-23).
- Apigee Adapter for Envoy concepts (v2.0.x): <https://docs.cloud.google.com/apigee/docs/api-platform/envoy-adapter/v2.0.x/concepts> (consultada directamente, contenido completo, 2026-10-23).
- Apigee deprecations and retirements (Edge), para la retirada de la integración con Istio Mixer: <https://docs.apigee.com/release/deprecated-features> (consultada directamente, 2026-10-22).
