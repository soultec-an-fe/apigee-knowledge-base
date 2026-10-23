---
id: administracion-redes
titulo: Redes y acceso — northbound, southbound, PSC, peering e IP del cliente
area: administracion
tags: [redes, psc, private-service-connect, vpc-peering, mig, shared-vpc, client-ip, x-forwarded-for, cloud-armor, ddos, pupi]
aplica_a: [apigee-x]
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/system-administration/psc-overview
revisado: 2026-10-23
---

# Redes y acceso — northbound, southbound, PSC, peering e IP del cliente

> **Fecha de corte: 23 de octubre de 2026.** La arquitectura general está en [arquitectura](../00-fundamentos/03-arquitectura.md); los fallos de red, en [troubleshooting](../14-troubleshooting/01-errores-de-runtime.md).

El runtime de Apigee X vive en una **VPC de un proyecto *tenant* de Google**. Tu tráfico llega a él y sale de él por dos caminos:

- **Northbound:** del cliente a Apigee.
- **Southbound:** de Apigee a los backends.

## Opciones de red

| Modelo | Cómo funciona | Notas |
|---|---|---|
| **VPC peering** | Tu VPC y la de Apigee se conectan con *service networking* | Requiere el **/22** (y el /28) por instancia. **No es transitivo.** Apigee usa **PUPI**: no exportes rutas de subred con IP pública, porque podrían chocar. |
| **Private Service Connect (PSC)** | *Northbound*: un NEG de PSC en tu balanceador apunta al *service attachment* de la instancia. *Southbound*: un *endpoint attachment* apunta al *service attachment* de tu backend. | No necesita peering. Compatible con VPC Service Controls. |

## Northbound

| Opción | Detalle |
|---|---|
| **MIG** (VMs proxy) + balanceador HTTPS **clásico** | Patrón antiguo. Las VMs reenvían a la IP privada de la instancia y hay que mantenerlas. |
| **PSC** + **Application Load Balancer** externo (basado en Envoy) | **Patrón recomendado:** sin VMs, con **varios NEG** (uno por región) en el mismo backend service |

**Ventajas de PSC northbound:**

- funciona con cualquier instancia existente;
- **health checking integrado** para el *failover* regional automático, sin sondas del cliente;
- **detección de outliers** en el backend service.

**Restricciones de PSC northbound:**

- **No es compatible** con el balanceador HTTP(S) externo **clásico**.
- **Lista de proyectos aceptados** (`consumerAcceptList`):
  - Un NEG solo conecta si su proyecto está en la lista.
  - Si quitas un proyecto, sus NEG ya creados **siguen funcionando**, pero los nuevos se rechazan.
  - Al quitar un proyecto, borra también sus NEG.
- **Límite de NEG:** **100 conexiones de NEG por proyecto**. Lo subieron de 20 el 10 de octubre de 2024: en instancias anteriores hay que **actualizar la lista de proyectos aceptados** para que aplique. Con más de 1000 en total, hay que contactar con soporte.
- **Borrar una instancia:** primero quita el NEG del balanceador. El borrado tarda hasta 20 minutos.

**Migración de MIG a PSC:**

1. Crea el nuevo balanceador con NEG de PSC: uno por región.
2. Pruébalo.
3. Pasa el tráfico por DNS de forma **gradual**, por ejemplo con *weighted round robin* de Cloud DNS: un 5–10 % primero y luego hasta el 100 %.
4. Retira el balanceador clásico y el MIG.

Lleva al balanceador nuevo toda la configuración del antiguo (Cloud Armor, certificados, etc.).

### Agentes de IA con acceso privado

Un agente desplegado en **Agent Runtime** (Gemini Enterprise Agent Platform) puede llamar en privado a APIs y *tools* MCP de Apigee:

1. Una **interfaz PSC** del agente conecta con un *network attachment* en tu VPC.
2. En esa VPC, un **endpoint PSC** apunta al *service attachment* de Apigee.
3. Una **zona privada de Cloud DNS** resuelve el hostname del environment group a la IP de ese endpoint.
4. El agente resuelve ese nombre mediante **DNS peering**.

## Southbound

| Backend | Conexión |
|---|---|
| En internet | Salida por las **IPs NAT** de la instancia. El backend debe permitirlas **todas**. Si hay mucho tráfico, puede haber **agotamiento de puertos NAT**. |
| En tu VPC (con peering) | Rutas exportadas al peering; **DNS peering** para dominios privados |
| En otra VPC u otro proyecto | **PSC** (*endpoint attachment*), o **Shared VPC** |

**Shared VPC:**

- Separa el proyecto de Apigee y los de backends en **proyectos de servicio** de un mismo **proyecto host**.
- Resuelve el problema de que el peering no es transitivo: el proyecto *tenant* de Apigee solo ve la VPC con la que está conectado.
- Google publica un script de aprovisionamiento.

## IP real del cliente

Analytics, la [detección de abuso](../13-advanced-api-security/02-deteccion-y-acciones.md) y las *security actions* necesitan la IP real del cliente. Entre el cliente y Apigee suele haber balanceadores que la ocultan.

Para eso existe la **resolución de la IP del cliente por entorno** (`client_ip_resolution_config`):

| Campo | Significado |
|---|---|
| `ipHeaderName` | Cabecera de la que leer la IP: `X-Forwarded-For`, `True-Client-Ip`… |
| `ipHeaderIndex` | Posición en la lista. **Positivo**: desde la izquierda, empezando en `0`. **Negativo**: desde la derecha, empezando en `-1`. |

- **Dónde queda la IP:** en la variable `client.resolved.ip` y en la dimensión *Resolved Client IP* (`ax_resolved_client_ip`).
- **Si no se configura**, o la cabecera no trae una IP en esa posición, se usa el algoritmo por defecto.
- **Para probarlo:** espera **5 minutos** después de guardar la configuración, y usa Debug con *Show all FlowInfos*.

> [!CAUTION]
> **`X-Forwarded-For` se puede falsificar.** Un atacante puede enviar la cabecera ya rellena con lo que quiera. Por eso:
> - Usa un **índice negativo**, contando los saltos que **tú** controlas entre el cliente y el balanceador de Apigee.
> - No uses el `0` de la izquierda.
> - Las llamadas de Apigee a Apigee no tienen tratamiento especial: cuenta también esos saltos.
> - Cambiar esta configuración puede afectar a las *security actions* que ya existen: revísalas.

## Protección DoS

- **Cloud Load Balancing:**
  - La infraestructura Google Front End absorbe ataques como los *SYN floods*.
  - Con **anycast**, una sola IP reparte el tráfico entre las instancias de todas las regiones.
- **Cloud Armor:**
  - reglas por IP o rango CIDR y por geografía;
  - **reglas WAF preconfiguradas** (ModSecurity CRS: XSS, inyección SQL…);
  - listas de IPs con nombre;
  - visibilidad en Cloud Monitoring y en Security Command Center.

## Logs de acceso del ingress (Preview)

Los clientes de Subscription y Pay-as-you-go pueden habilitar, **por instancia**, los **logs de acceso de los gateways de ingress** en Cloud Logging:

- Requiere `roles/apigee.admin`, o los permisos `apigee.instances.create` y `apigee.instances.update`.
- **Se facturan** los logs que se envían a tu proyecto.

## Fuentes

Todas consultadas directamente el 2026-10-23:

- Private Service Connect overview (northbound): <https://docs.cloud.google.com/apigee/docs/api-platform/system-administration/psc-overview>, contenido completo.
- Migrate northbound routing to PSC: <https://docs.cloud.google.com/apigee/docs/api-platform/system-administration/migrate-from-mig-to-psc>, contenido completo.
- Peering ranges / network sizing: <https://docs.cloud.google.com/apigee/docs/api-platform/system-administration/peering-ranges>, contenido completo.
- Shared VPC: <https://docs.cloud.google.com/apigee/docs/api-platform/system-administration/shared-vpcs>, contexto y prerrequisitos.
- Client IP resolution: <https://docs.cloud.google.com/apigee/docs/api-platform/system-administration/client-ip-resolution>, contenido completo.
- Preventing DoS attacks: <https://docs.cloud.google.com/apigee/docs/api-platform/system-administration/preventing-dos>, contenido completo.
- Cloud Logging ingress access logs: <https://docs.cloud.google.com/apigee/docs/api-platform/system-administration/cloud-logging-ingress-access>, requisitos.
- Private access from Agent Runtime: <https://docs.cloud.google.com/apigee/docs/api-platform/system-administration/private-access-from-agent-runtime>, patrón.
