---
id: troubleshooting-runtime
titulo: Troubleshooting de errores de runtime y de red
area: troubleshooting
tags: [troubleshooting, playbooks, 502, 503, 504, target-read-timeout, target-connect-timeout, unexpected-eof, keepalive, psc, vpc-peering, dns-peering, nat]
aplica_a: [apigee-x, apigee-hybrid]
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/troubleshoot/playbooks/introduction
revisado: 2026-10-23
---

# Troubleshooting de errores de runtime y de red

> **Fecha de corte: 23 de octubre de 2026.**

Google publica **playbooks** de diagnóstico elaborados con su equipo de soporte. Este documento sintetiza los de runtime y de red de Apigee X (la mayoría aplica también a hybrid). Los exclusivos de hybrid (Cassandra, ingress, *Automated Issue Surfacing*) están en [11-hybrid](../11-hybrid/04-operacion-y-troubleshooting.md). Los códigos de error, con su HTTP, están en la [referencia de códigos](../10-referencia/02-codigos-de-error.md#backend-y-transporte).

## Método general

1. **Identifica el código y el motivo.**
   - El HTTP solo no basta: dos `503` pueden tener causas opuestas.
   - Busca `fault-code`, `fault-source` y el motivo (por ejemplo `TARGET_READ_TIMEOUT`) en la respuesta, en **Debug** o en **API Monitoring**.
2. **Mira la duración total** de la transacción en Debug. A menudo delata la causa:
   - **~3 s:** el default de `connect.timeout.millis`; apunta a un problema de conexión.
   - **~55 s:** el default de `io.timeout.millis`; apunta a un backend lento.
   - **Otro valor:** reintentos, o un timeout configurado en el proxy.
3. **Reproduce fuera de Apigee** (`curl` desde una VM en la misma red) para separar los problemas de Apigee de los del backend.
4. **Datos a reunir antes de abrir caso con soporte:**
   - proyecto y organización;
   - proxy y entorno;
   - franja horaria y frecuencia del fallo;
   - host del target;
   - una sesión de Debug con el error.

## 504 `TARGET_READ_TIMEOUT` (`GatewayTimeout`)

El backend no respondió dentro de `io.timeout.millis` (**default 55 s**).

| Causa | Diagnóstico | Solución |
|---|---|---|
| **Backend lento** | En Debug, *Target Request* dura lo mismo que el timeout | Investiga el backend: si su latencia normal es de 50 ms y ahora tarda 55 s, el problema está ahí. Solo si es necesario, sube `io.timeout.millis` en `<HTTPTargetConnection>`; el **máximo es 300 s**. |
| **Conectividad con `<LoadBalancer>`** | La duración **no** coincide con el timeout (por ejemplo, 9 s). Con `<LoadBalancer>`, Apigee **reintenta la conexión dos veces más** y **oculta la causa real**. | Quita temporalmente `<LoadBalancer>` para ver el error real. Si es un timeout de conexión, ve a la sección de 503. |

## 503 `TARGET_CONNECT_TIMEOUT` (targets por internet o por VPC peering)

No se pudo establecer la conexión TCP. Si el target va por **Private Service Connect** (endpoint attachment), ve a la sección de PSC.

| Causa | Diagnóstico y solución |
|---|---|
| **Rutas no exportadas al peering** | Si el fallo es persistente, revisa las rutas importadas en el peering con Apigee: la del rango del target debe aparecer. Exporta las rutas estáticas o dinámicas que falten. **El peering no es transitivo**: si N1 está conectado a N2 y a N3, N2 no llega a N3. |
| **El target no acepta conexiones** | Prueba con *Connectivity Tests* o con `curl` en bucle (timeout de 3 s) desde una VM, en el momento en que falla. Si el timeout se reproduce, el problema está fuera de Apigee. |
| **IPs NAT de Apigee no permitidas** | El backend debe permitir **todas** las IPs NAT de la instancia, no solo algunas. |
| **Agotamiento de puertos NAT** | Hay pocos puertos NAT para el tráfico. Reserva más IPs NAT. |
| **`connect.timeout.millis` demasiado bajo** | Si la duración es menor de 3 s, revisa la configuración del TargetEndpoint. |

## 503 `TARGET_CONNECT_HOST_NOT_REACHABLE` y `NoResolvedHost`

| Causa | Solución |
|---|---|
| Host del target mal escrito o con caracteres no válidos (por ejemplo, espacios) | Corrige el TargetEndpoint o el TargetServer |
| **Falta el DNS peering** para un dominio privado | Crea un *peered DNS domain* para el sufijo, **con punto final** (`corp.example.com.`): con `gcloud services peered-dns-domains create` si la organización tiene VPC peering, o con la API de Apigee si no lo tiene |

## 502 `UnexpectedEOFAtTarget`

El backend cerró la conexión mientras Apigee enviaba o esperaba datos.

| Causa | Detalle |
|---|---|
| TargetServer sin TLS bien configurado | Por ejemplo, el puerto es HTTPS pero falta `<SSLInfo>`, o al revés |
| El backend corta la conexión | Reinicios, *timeouts* propios, límites de conexiones |
| **Keep-alive mal ajustado** | Ver abajo |
| NAT con AWS NLB (*cross-zone* y preservación de IP), solo en X | Colisión de conexiones con el balanceador de AWS |

### El caso del keep-alive

Apigee X reutiliza conexiones persistentes (HTTP/1.1) con el backend, y por defecto las cierra tras **60 s** sin actividad (`keepalive.timeout.millis`). Si el keep-alive del backend es **igual o menor**, se produce una carrera:

1. En el segundo 59, Apigee reutiliza la conexión y envía una petición.
2. Antes de que llegue, al backend le vence su keep-alive y envía un `FIN`.
3. Apigee recibe un EOF inesperado y responde `502`.

**Solución:** `keepalive.timeout.millis` en Apigee **por debajo** del keep-alive del backend. No desactives el keep-alive: es un [antipatrón](../09-antipatrones/01-catalogo-antipatrones.md).

## Errores de entrada (*northbound*)

| Causa | Síntoma |
|---|---|
| Errores TLS en el balanceador HTTPS (lo gestionas tú) | Fallos de *handshake* en sus logs |
| **Cloud Armor** bloqueando | 403, 404 o 502, según la regla |
| VMs proxy (MIG) que no reenvían a la instancia | `502` |
| Red equivocada en el peering con Apigee | `502` |
| **Instancia nueva sin entornos adjuntos** (después de una expansión de región) | `503`: una instancia sin entornos no responde |
| **PSC northbound:** el proyecto del endpoint no está en la *consumer accept list* de la instancia | Sin conexión. Añade el proyecto a `consumerAcceptList`. |

## Targets por Private Service Connect (*southbound*)

| Causa | Comprobación |
|---|---|
| *Service attachment* e instancia de Apigee **en regiones distintas** | El acceso global depende del tipo de balanceador productor |
| Falta la regla de firewall de entrada para la **subred de PSC** en el proyecto del target | Permite la IP y el puerto de esa subred |
| *Service attachment* mal configurado | Revísalo en el proyecto del target |
| *Endpoint attachment* en mal estado en Apigee | Comprueba su estado |
| Puerto distinto entre el TargetEndpoint y el ILB | El proxy debe usar el puerto que expone el ILB |

## Aprovisionamiento: «couldn't find a free ip space of /22»

Cada instancia de Apigee necesita un rango **/22 que no se solape** con nada del peering (`servicenetworking-googleapis-com`). Elige otro rango, o libera el que está en conflicto.

## MessageLogging hacia Cloud Logging sin logs

No aparece ningún error: simplemente no llegan los logs. Comprueba:

1. La **Cloud Logging API** está habilitada en el proyecto.
2. La **IAM Service Account Credentials API** también lo está.
3. La **cuenta de servicio del proxy** existe y tiene permisos. En X es la que se indica al desplegar; en hybrid, la de la configuración de runtime.
4. El **proyecto del `LogName`** coincide con el de la organización.

Ver [MessageLogging](../02-politicas/referencia/message-logging.md).

## Errores de políticas

Google mantiene playbooks por política, separados en **runtime** y **despliegue**. Hay playbooks para AssignMessage, BasicAuthentication, Decode/Generate/VerifyJWT, ExtractVariables, InvalidateCache, JavaCallout, JavaScript, KeyValueMapOperations, LookupCache, MessageLogging, PopulateCache, PythonScript, Quota, RegularExpressionProtection, ResetQuota, ResponseCache, SAML, ServiceCallout, SOAPMessageValidation, SpikeArrest, XMLToJSON, XSLTransform, AccessControl, FlowCallout, JSONThreatProtection, JSONToXML y XMLThreatProtection.

El catálogo de errores de cada política, con sus causas, está en su archivo de [referencia de políticas](../02-politicas/referencia/00-indice.md), en la sección **Errores**.

## Fuentes

Todas consultadas directamente el 2026-10-23:

- Troubleshooting playbooks introduction: <https://docs.cloud.google.com/apigee/docs/api-platform/troubleshoot/playbooks/introduction>, contenido completo.
- 504 TARGET_READ_TIMEOUT: <https://docs.cloud.google.com/apigee/docs/api-platform/troubleshoot/playbooks/runtime/504-target-read-timeout>, contenido completo.
- 503 TARGET_CONNECT_TIMEOUT (VPC): <https://docs.cloud.google.com/apigee/docs/api-platform/troubleshoot/playbooks/runtime/vpc-503-target-connect-timeout>, contenido completo.
- TARGET_CONNECT_HOST_NOT_REACHABLE: <https://docs.cloud.google.com/apigee/docs/api-platform/troubleshoot/playbooks/runtime/target-connect-host-not-reachable>, contenido completo.
- 502 Unexpected EOF: <https://docs.cloud.google.com/apigee/docs/api-platform/troubleshoot/playbooks/runtime/unexpected-eof-at-target>, contenido completo.
- Access routing issues: <https://docs.cloud.google.com/apigee/docs/api-platform/troubleshoot/playbooks/network-configuration/access-routing-issues>, causas.
- PSC (northbound): <https://docs.cloud.google.com/apigee/docs/api-platform/troubleshoot/playbooks/network-configuration/psc>, contenido completo.
- Connectivity with southbound PSC targets: <https://docs.cloud.google.com/apigee/docs/api-platform/troubleshoot/playbooks/network-configuration/connectivity-with-sb-psc-targets>, causas.
- No free IP address space: <https://docs.cloud.google.com/apigee/docs/api-platform/troubleshoot/playbooks/network-configuration/no-free-ip-address-space>, contenido completo.
- Cloud Logging issues: <https://docs.cloud.google.com/apigee/docs/api-platform/troubleshoot/playbooks/cloud-logging-issues>, causas.
