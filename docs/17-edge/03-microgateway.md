---
id: edge-microgateway
titulo: Edge Microgateway
area: edge
tags: [edge, microgateway, edgemicro, plugins, edgemicro-auth, oauth, quota, spikearrest, nodejs]
aplica_a: [apigee-edge]
fuente: https://docs.apigee.com/api-platform/microgateway/latest/overview-edge-microgateway
revisado: 2026-10-23
---

# Edge Microgateway

> **Fecha de corte: 23 de octubre de 2026.** ⚠️ **Solo Apigee Edge**, Public o Private Cloud (Private Cloud 4.18.01 o posterior). Versión documentada: **3.3.x**, la `latest` del sitio.

**Edge Microgateway** (`edgemicro`) es un procesador de mensajes HTTP ligero, escrito en **Node.js**, que se instala **cerca de los backends**: en la misma máquina, subred o centro de datos. Procesa las peticiones localmente y envía los datos de Analytics a Edge **de forma asíncrona**, sin añadir latencia. No ofrece todas las capacidades de Edge: solo las de sus **plugins**.

## Cuándo se usaba

- Para **reducir la latencia** cuando consumidores y backends están cerca y no tiene sentido pasar por un gateway central.
- Para **mantener el tráfico dentro del perímetro** por seguridad o cumplimiento.
- Para **seguir procesando** si se corta temporalmente la conexión a internet.
- Para gestionar con Apigee servicios de **Kubernetes**.
- Se ejecuta como proceso independiente o en **Docker**.

## Cómo funciona

| Pieza | Papel |
|---|---|
| **Proxies «Microgateway-aware»** en Edge | Proxies con prefijo **`edgemicro_`** que solo aportan **basepath y URL de target**. Deben usar `HTTPTargetConnection`: no valen ni `ScriptTarget` (Node.js) ni `LocalTargetConnection`. **Sus políticas y flujos condicionales se ignoran**, porque nunca se ejecutan en Edge. |
| Proxy **`edgemicro-auth`** | Lo despliega `edgemicro configure`. Emite y valida los tokens de Microgateway, y necesita el *virtual host* `secure`. **Debe estar en el API product** para usar API key u OAuth. |
| API products, developers y apps | Los de Edge, como siempre |
| Arranque | Al iniciar, Microgateway descarga de Edge la lista de proxies `edgemicro_*` y de API products. La configuración queda en `~/.edgemicro/{org}-{env}-config.yaml`. |
| Analytics | Se envían a Edge de forma asíncrona y aparecen en Edge Analytics |

> [!IMPORTANT]
> - **Los tokens de Microgateway y los de los proxies de Edge no son intercambiables.** Un access token emitido para Microgateway no sirve en un proxy de Edge con OAuthV2, ni al revés.
> - **API Monitoring no está disponible para Microgateway.**

## Plugins incluidos

| Plugin | Activo por defecto | Función |
|---|---|---|
| `analytics` | Sí | Envía Analytics a Edge |
| `oauth` | Sí | Valida access tokens OAuth y API keys |
| `quota` | No | Cuota almacenada en Edge. **Debe ir después de `oauth`** en la secuencia. |
| `quota-memory` | No | Cuota en memoria local |
| `spikearrest` | No | Protección frente a picos y DoS |
| `json2xml` | No | Transformación según `Accept` y `Content-Type` |
| `accumulate-request` / `accumulate-response` | No | Acumulan el cuerpo para plugins de transformación |
| `transform-uppercase`, `header-uppercase` | No | Plugins de muestra para escribir los propios |
| `healthcheck` | No | Expone `/healthcheck` con memoria y CPU del proceso |

También se pueden escribir **plugins propios** en Node.js.

## Instalación y operación

- **Requisitos:** una versión de Node.js en fase **Active LTS o Maintenance LTS** (Windows, macOS o Linux). En Windows, además, OpenSSL en el `PATH`.
- **Instalación:** `npm install -g edgemicro`.
- **Primeros pasos:**
  1. `edgemicro init` crea la configuración por defecto.
  2. `edgemicro configure` vincula Microgateway con una organización y un entorno, y despliega `edgemicro-auth`.
  3. `edgemicro verify` comprueba la instalación.
  4. `edgemicro start` arranca el proceso.
- **Otros comandos de la CLI:**
  - `stop`, `reload` y `status`;
  - `token`: obtener access tokens;
  - `genkeys`, `rotatekey` y `revokekeys`: claves de firma;
  - `cert`, `private` (Private Cloud), `upgradekvm`, `upgradeauth` y `version`.

> [!NOTE]
> La documentación conserva varias versiones (2.5.x, 3.0.x, 3.1.x, 3.2.x, 3.3.x). Sigue siempre la de tu versión instalada: CLI y configuración cambian entre ellas.

## Equivalente en Apigee X

Microgateway es específico de Edge. En X/hybrid, para gestionar APIs cerca de los backends o fuera de un proxy central, las alternativas son:

- el [Apigee Adapter for Envoy](../16-adaptadores/04-envoy-adapter.md), con la misma idea de un gateway ligero que consulta a Apigee de forma asíncrona;
- el [Extension Processor](../16-adaptadores/02-extension-processor.md);
- el [Operator for Kubernetes](../16-adaptadores/03-apim-operator-kubernetes.md).

Ver el [panorama](../16-adaptadores/01-panorama.md).

## Fuentes

Todas consultadas directamente el 2026-10-23:

- Edge Microgateway overview (3.3.x/latest): <https://docs.apigee.com/api-platform/microgateway/latest/overview-edge-microgateway>, contenido completo.
- Installing Edge Microgateway: <https://docs.apigee.com/api-platform/microgateway/latest/installing-edge-microgateway>, requisitos.
- Setting up and configuring Edge Microgateway: <https://docs.apigee.com/api-platform/microgateway/latest/setting-and-configuring-edge-microgateway>, estructura y notas.
- Use plugins: <https://docs.apigee.com/api-platform/microgateway/latest/use-plugins>, tabla de plugins.
- CLI reference: <https://docs.apigee.com/api-platform/microgateway/latest/cli-reference-edge-microgateway>, lista de comandos.
