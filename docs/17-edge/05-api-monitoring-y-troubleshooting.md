---
id: edge-api-monitoring-troubleshooting
titulo: Edge — API Monitoring y troubleshooting
area: edge
tags: [edge, api-monitoring, alertas, collections, troubleshooting, timeouts, router, message-processor, logs, private-cloud]
aplica_a: [apigee-edge]
fuente: https://docs.apigee.com/api-monitoring
revisado: 2026-10-23
---

# Edge — API Monitoring y troubleshooting

> **Fecha de corte: 23 de octubre de 2026.** ⚠️ **Solo Apigee Edge.** Los equivalentes en X son Cloud Monitoring, [AAPI Ops](../13-advanced-api-security/01-vision-general.md#aapi-ops-anomalías-operativas) y los [playbooks de X](../14-troubleshooting/01-errores-de-runtime.md).

## API Monitoring

**API Monitoring** da a los equipos de operación una visión **casi en tiempo real** de la disponibilidad y la latencia de las APIs, para detectar y diagnosticar problemas antes de que los noten los consumidores.

| Aspecto | Detalle |
|---|---|
| Disponibilidad | Solo **Edge for Public Cloud Enterprise**. **No** en Private Cloud ni en Edge Microgateway. |
| Diferencia con Edge Analytics | API Monitoring busca **mantener las APIs funcionando**: datos recientes y alertas. Analytics busca **tendencias a largo plazo**. Los datos de Monitoring son un subconjunto de los de Analytics y pueden ser algo menos completos. |
| Dashboards | **Recent** (lo último), **Timeline** (histórico: tráfico, tasa de 4xx y 5xx, latencia p50, p95 y p99) e **Investigate** (diagnóstico por código de fallo) |
| Retención | Los logs incluyen query parameters y *user agent*, que pueden contener PII; se conservan **55 días** |

**Roles:**

| Rol | Acceso |
|---|---|
| API Monitoring Administrator | CRUD completo de alertas, *collections* e informes |
| API Monitoring User | Solo lectura |
| Organization Administrator | CRUD completo |
| Read-only Organization Administrator | Solo lectura |
| Operations Administrator | Alertas y *collections*; no crea informes personalizados |

**Alertas:**

- **Condiciones:** por código de estado (404, 502, 2xx, 4xx, 5xx…), latencia o código de fallo, durante un periodo.
- **Ámbito:** sobre proxy, target, región o *collection*.
- **Notificaciones:** email, Slack, PagerDuty o webhooks.
- **Ejemplo:** «tasa de 5xx por encima del 23 % durante 5 minutos en `orders-prod`».
- **Límite: 20 alertas por organización**, compartidas por todos los usuarios.
- **Tipos:**
  - fijas (por umbral);
  - de **anomalías** (Beta);
  - de **caducidad de certificados TLS** (Beta).
- Cada notificación enlaza con el detalle de la alerta, su historial, un *playbook* y un informe personalizado.

**Collections:** agrupan proxies, targets o apps (**hasta 20 elementos**) para filtrar y crear alertas comunes. Por ejemplo, los proxies de mucho tráfico o las apps de un mismo socio.

> [!NOTE]
> La página de deprecaciones de Edge anuncia (julio de 2025) la retirada en **Edge Cloud**, para **julio de 2026**, de *security reporting*, *traffic alerts* y *advanced security reporting*. La documentación consultada no aclara si las alertas de API Monitoring forman parte de esas *traffic alerts*. **Pendiente de verificación** con el soporte de Apigee antes de depender de ellas.

## Timeouts por defecto en Edge

Muchos 504, 502 y 499 se explican por la cadena de timeouts:

| Componente | Timeout por defecto | Qué cubre |
|---|---|---|
| Cliente | El que tenga (navegador, SO, app) | Si es menor que el de Edge, el cliente corta antes: **499** en los logs |
| **Router** | **57 s** | Toda la ejecución del proxy, desde que entra la petición hasta la respuesta |
| **Message Processor** | **55 s** | Lo que tarda el backend en responder (`io.timeout.millis`) |

Si un timeout más alto se configura solo en el MP, el **Router corta antes**. Ajústalos de forma coherente: **cliente > Router > MP > backend**.

## Errores frecuentes y causa probable

| Error | Causas documentadas |
|---|---|
| **504 Gateway Timeout** (`GatewayTimeout`) | Backend lento (más de 55 s en el MP); Router que expira antes que el MP; timeout del Router mal configurado |
| **502 tras 55 s** | Timeout en el *handshake* TLS con el backend, a menudo por un firewall del backend que bloquea a Apigee |
| **503 Service Unavailable** | DNS que resuelve a IPs incorrectas (Private Cloud); errores de red; host de target mal escrito o con espacios; *handshake* TLS fallido |
| **404 «Unable to identify proxy for host»** | Proxy no asociado al *virtual host*; *virtual host* eliminado en la revisión nueva mientras los clientes lo siguen usando; ruta sin proxy; proxy no desplegado en el entorno; entorno no cargado en los MP (Private Cloud) |
| **499** | El cliente cerró la conexión antes de recibir la respuesta |
| 400, 413, 414, 431, 415, 500 y 502 por cabeceras, cuerpo o ruta | Los del [catálogo de runtime](../10-referencia/02-codigos-de-error.md#backend-y-transporte), comunes con X |

## Diagnóstico en Private Cloud

- **Logs de cada componente:** en `/opt/apigee/var/log/{componente}/`. Por ejemplo, `edge-message-processor/`, `edge-management-server/logs/` (`system`, `transactions`, `startupruntimeerror`), `apigee-cassandra/`, `apigee-zookeeper/`, `apigee-postgresql/` y `apigee-qpidd/`. Los del Router son los de Nginx.
- **Herramientas que propone Google:**
  - `tcpdump` para capturar el tráfico con un host;
  - **heap dumps** y **thread dumps** de los procesos Java.
- **Guías específicas** de problemas de:
  - ZooKeeper: pérdida de conexión, arranque, datos;
  - Cassandra;
  - despliegue: `configuration failed`, errores de acceso al *datastore*, *timeouts*;
  - Analytics;
  - LDAP;
  - SSO y SAML;
  - Postgres.

## Fuentes

Todas consultadas directamente el 2026-10-23:

- API Monitoring overview: <https://docs.apigee.com/api-monitoring>, contenido completo.
- Access API Monitoring (roles): <https://docs.apigee.com/api-monitoring/access>, contenido completo.
- Alerts and notifications: <https://docs.apigee.com/api-monitoring/alerts-notifications>, contenido completo.
- Collections: <https://docs.apigee.com/api-monitoring/collections>, contenido completo.
- Compare API Monitoring and Analytics: <https://docs.apigee.com/api-monitoring/compare>, contenido completo.
- Timeline dashboard: <https://docs.apigee.com/api-monitoring/timeline>, contenido completo.
- Playbooks de runtime de Edge (`504-gateway-timeout`, `504-gateway-timeout-router-timing-out`, `502-bad-gateway-timeout`, `503-service-unavailable`, `404-unable-identify-proxy-host`, `499-client-closed-connection`): <https://docs.apigee.com/api-platform/troubleshoot/runtime/504-gateway-timeout> y relacionadas.
- Diagnostic tools and logs: <https://docs.apigee.com/api-platform/troubleshoot/diagnostic-tools-and-logs>; guías de *diagnostic logs*.
- Apigee deprecations and retirements: <https://docs.apigee.com/release/deprecated-features>.
