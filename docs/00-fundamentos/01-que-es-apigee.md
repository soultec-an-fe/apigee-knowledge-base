---
id: fundamentos-que-es-apigee
titulo: Qué es Apigee
area: fundamentos
tags: [apigee, api-management, gateway, conceptos]
aplica_a: [apigee-x, apigee-hybrid]
fuente: https://cloud.google.com/apigee/docs/api-platform/get-started/what-apigee
revisado: 2026-08-20
---

# Qué es Apigee

**Apigee** es la plataforma de gestión de APIs de Google Cloud. Funciona como una capa de **proxy inverso gestionado** que se coloca entre los consumidores de una API y los servicios backend que la implementan.

## El modelo mental en una frase

> Tú no expones tu backend. Expones un **API proxy** de Apigee, y Apigee aplica políticas antes y después de hablar con tu backend.

```
Cliente  ──►  Apigee (API proxy)  ──►  Backend
             │                    │
             ├ autenticación      ├ transformación
             ├ cuotas             ├ caché
             ├ rate limiting      ├ logging
             └ validación         └ analytics
```

## Qué problema resuelve

| Problema | Cómo lo resuelve Apigee |
|---|---|
| El backend no debe llevar lógica de autenticación de terceros | Políticas `VerifyAPIKey`, `OAuthV2`, `VerifyJWT` en el proxy |
| Un consumidor abusivo tumba el servicio | `SpikeArrest` (protección de picos) y `Quota` (límite de negocio) |
| El backend habla XML y el cliente quiere JSON | `XMLtoJSON`, `JSONtoXML`, `AssignMessage` |
| No sé quién consume qué ni cuánto | Analytics integrado, `DataCapture`, `MessageLogging` |
| Cambiar la URL del backend obliga a redeploy de clientes | `TargetServer` + basepath estable en el proxy |
| Quiero monetizar o dar acceso escalonado | **API products** + apps de desarrollador + cuotas por producto |
| El backend es lento o frágil | `ResponseCache`, timeouts, load balancing con failover |

## Componentes conceptuales

1. **API proxy** — la unidad desplegable. Un bundle XML con endpoints, flujos, políticas y recursos.
2. **Políticas** — módulos de configuración declarativa (XML) que hacen el trabajo: validar, transformar, limitar, registrar. Ver [catálogo](../02-politicas/00-catalogo-de-politicas.md).
3. **Shared flows** — colecciones de políticas reutilizables entre proxies. Ver [shared flows](../01-proxies/06-shared-flows-y-flow-hooks.md).
4. **API products** — el paquete comercial: agrupa proxies/operaciones y define cuotas y scopes. Es lo que un desarrollador "consume". Ver [API products](../04-publicacion/01-api-products.md).
5. **Developers y apps** — quién consume y con qué credenciales (API key / client_id + secret).
6. **Environments y environment groups** — dónde se despliega y por qué hostname entra el tráfico. Ver [organizaciones y entornos](04-organizaciones-entornos-grupos.md).
7. **Analytics** — métricas de tráfico, latencia y errores, con retención y APIs de consulta.

## La separación clave: proxy ≠ product

Es el punto que más confusión genera:

- El **API proxy** es *técnico*: define cómo se procesa una petición HTTP.
- El **API product** es *comercial/de acceso*: define qué operaciones puede llamar un app, con qué cuota y con qué scopes.

Un mismo proxy puede estar en varios products con cuotas distintas. Una API key no da acceso a "un proxy", da acceso a **los products que la contienen**.

## Qué NO es Apigee

- **No es un servidor de aplicaciones.** No pongas lógica de negocio pesada en el proxy.
- **No es un ESB.** Puede mediar, pero orquestaciones complejas van en Application Integration o en el backend.
- **No es una base de datos.** Los KVM y las cachés tienen límites duros (ver [límites](../10-referencia/01-limites.md)) y no son almacenamiento persistente de propósito general.
- **No es un WAF completo.** Tiene threat protection, pero el WAF de red vive en Cloud Armor.

## Modos de despliegue

| Edición | Runtime | Estado |
|---|---|---|
| **Apigee X** | Gestionado 100% por Google en Google Cloud | Recomendado para proyectos nuevos |
| **Apigee hybrid** | Plano de control en Google, runtime en tu Kubernetes | Para requisitos de residencia de datos o on-prem |
| **Apigee Edge** (Public/Private Cloud) | Plataforma legacy anterior a X | En fin de vida; no usar para proyectos nuevos |

Detalle en [ediciones y comparativa](02-ediciones-y-comparativa.md).

## Fuentes

- <https://cloud.google.com/apigee/docs/api-platform/get-started/what-apigee>
- <https://cloud.google.com/apigee>
