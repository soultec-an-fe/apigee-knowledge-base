---
id: antipatrones-catalogo
titulo: Catálogo de antipatrones
area: antipatrones
tags: [antipatrones, errores-comunes, revision, auditoria]
aplica_a: [apigee-x, apigee-hybrid, apigee-edge]
fuente: https://docs.apigee.com/api-platform/antipatterns/intro
revisado: 2026-08-20
---

# Catálogo de antipatrones

Los **21 antipatrones documentados oficialmente por Apigee**, con explicación de por qué duelen y cuál es la alternativa.

> [!TIP]
> Esta es la lista de referencia para revisar código Apigee. Un LLM puede usarla directamente como checklist de auditoría sobre un bundle.

---

## Antipatrones de políticas

### 1. Emitir refresh tokens sin invocar el refresh flow

**Qué pasa:** generas refresh tokens pero tu API nunca expone `RefreshAccessToken`.

**Por qué duele:** acumulas tokens de refresco en Cassandra que nadie usará y que pueden vivir hasta **2 años**. Almacenamiento desperdiciado y superficie de ataque innecesaria.

**Alternativa:** emite refresh tokens **solo** si implementas realmente el flujo de refresco. Ver [OAuth 2.0](../03-seguridad/02-oauth2.md).

---

### 2. Usar `waitForComplete()` en código JavaScript

**Qué pasa:** llamas a `httpClient` en un `Javascript` y esperas con `waitForComplete()`.

**Por qué duele:** **bloquea el hilo del Message Processor**, que es un recurso compartido. Degrada **todo** el tráfico del nodo, no solo tu proxy.

**Alternativa:** usa la política **`ServiceCallout`**. Google es explícito: no hagas peticiones HTTP dentro de un script callout. Ver [políticas de extensión](../02-politicas/04-extension.md).

---

### 3. Expiración muy larga para tokens OAuth

**Qué pasa:** access tokens con días o semanas de vida.

**Por qué duele:** un token de larga duración **no se puede revocar de forma efectiva**. Si se filtra, sigue siendo válido hasta que caduque.

**Alternativa:** access tokens de 15–60 min + refresh tokens. Límites de plataforma: access ≥180 s y ≤30 días; refresh ≥1 día y ≤2 años.

---

### 4. Cuantificadores greedy en `RegularExpressionProtection`

**Qué pasa:** patrones como `.*`, `.+`, `(a+)+`.

**Por qué duele:** provocan **backtracking catastrófico**. Un payload de pocos KB puede consumir segundos de CPU de un Message Processor. **La política de seguridad se convierte en el vector de DoS.**

**Alternativa:** ancla los patrones (`^`, `$`, `\b`), usa cuantificadores reluctantes (`.*?`) o posesivos (`.*+`), nunca anides cuantificadores. Ver [threat protection](../03-seguridad/05-threat-protection.md).

---

### 5. Cachear respuestas de error

**Qué pasa:** `ResponseCache` sin `<SkipCachePopulation>`.

**Por qué duele:** un fallo transitorio del backend (un 500) se cachea y **se propaga a todos los clientes durante todo el TTL**. Un error de 2 segundos se convierte en una caída de 5 minutos.

**Alternativa:**
```xml
<SkipCachePopulation>response.status.code != 200 or request.verb != "GET"</SkipCachePopulation>
```
Ver [caching](../05-operacion/04-caching-y-persistencia.md).

---

### 6. Almacenar datos mayores de 256 KB en caché

**Qué pasa:** intentas cachear un objeto que supera el límite de valor.

**Por qué duele:** se rechaza o se trunca. El comportamiento no siempre es evidente y produce bugs intermitentes.

**Alternativa:** cachea una **referencia** (URL firmada de Cloud Storage, identificador), no el objeto. Límites: clave 2 KB, valor **256 KB**.

---

### 7. Invocar `MessageLogging` varias veces en un proxy

**Qué pasa:** adjuntas `MessageLogging` en varios puntos del flujo (PreFlow de petición, de respuesta, una FaultRule…) o registras "por partes" fuera del `PostClientFlow`.

**Por qué duele:**

- Cada invocación abre una conexión al destino de logs; con syslog sobre TCP/TLS, además, un handshake TLS. Son dos o más conexiones por petición.
- Si el servidor syslog va lento, genera **contrapresión** en el Message Processor: latencia alta e incluso `504 Gateway Timeout`.
- **Se pierden logs:** si una política anterior falla o el target devuelve 4xx/5xx, el log del flujo de respuesta no se ejecuta.

**Alternativa:** guarda en variables lo que quieras registrar (con `ExtractVariables` o `JavaScript`) a lo largo del flujo, y haz **una sola invocación** en el `PostClientFlow`, que se ejecuta siempre. Como `response.*` no está disponible ahí tras un error, usa `message.*` o las variables que guardaste. Si no necesitas entrega garantizada ni TLS, Google sugiere syslog por UDP. Ver [MessageLogging](../02-politicas/referencia/message-logging.md) y [analytics](../05-operacion/03-analytics-monitoreo.md).

Fuente: <https://docs.cloud.google.com/apigee/docs/api-platform/antipatterns/messagelogging-multiple-times> (consultada directamente, 2026-10-22).

---

### 8. Identificadores de alta cardinalidad en `Quota`

**Qué pasa:** usas como `<Identifier>` algo con cardinalidad ilimitada: `messageid`, un UUID de petición, un timestamp, o `client.ip` en una API pública masiva.

**Por qué duele:** **cada valor distinto crea una fila de contador en Cassandra**. Explosión de almacenamiento y degradación del runtime.

**Alternativa:** usa `client_id`, `apiproduct.name` o un atributo personalizado estable del desarrollador. **No** uses `developer.id` ni `developer.app.id`: Google advierte que son IDs internos que pueden cambiar. Ver [Quota — `<Identifier>`](../02-politicas/referencia/quota.md#identifier).

---

### 9. Configurar cuota no distribuida

**Qué pasa:** `<Distributed>false</Distributed>`.

**Por qué duele:** cada Message Processor cuenta por separado. El límite real es `count × número de MPs`, y Apigee escala los MPs automáticamente: **el límite efectivo es impredecible**.

**Alternativa:** `<Distributed>true</Distributed>` siempre, salvo que sepas exactamente por qué no.

---

### 10. Reutilizar una política `Quota`

**Qué pasa:** adjuntas la **misma** política `Quota` en varios flujos que conceptualmente tienen límites distintos.

**Por qué duele:** **todos comparten el contador**. Consumir cuota en `/pedidos` reduce la disponible en `/clientes`, aunque quisieras límites independientes.

**Alternativa:** una política `Quota` distinta por cada contador que deba ser independiente.

---

### 11. Usar `RaiseFault` en condiciones inapropiadas

**Qué pasa:** usas `RaiseFault` para modificar la respuesta o registrar algo.

**Por qué duele:** `RaiseFault` **aborta el pipeline** y entra en error flow. Si solo querías cambiar una cabecera, has convertido una respuesta normal en un error.

**Alternativa:** `AssignMessage` para modificar, `MessageLogging` para registrar. Reserva `RaiseFault` para cortar de verdad. Ver [mediación](../02-politicas/03-mediacion.md).

---

### 12. Acceder incorrectamente a cabeceras HTTP multi-valor

**Qué pasa:** lees `request.header.NOMBRE` en una cabecera que tiene varios valores.

**Por qué duele:** **devuelve solo el primero**. Cabeceras como `Accept`, `Cache-Control` o `X-Forwarded-For` se dividen en valores individuales y pierdes el resto silenciosamente.

**Alternativa:**
```
request.header.NOMBRE.values          → todos los valores
request.header.NOMBRE.values.count    → cuántos hay
request.header.NOMBRE.1               → el primero (índice base 1)
request.header.NOMBRE.2               → el segundo
```
Ver [variables de flujo](../01-proxies/04-variables-de-flujo.md).

---

### 13. Usar `ServiceCallout` para invocar el backend en un proxy sin target

**Qué pasa:** el proxy no tiene `TargetEndpoint` y llamas al backend con `ServiceCallout`.

**Por qué duele:** `ServiceCallout` **no participa** en el load balancing, los health monitors, los reintentos ni las métricas de target. Pierdes toda la funcionalidad de gestión de backends.

**Alternativa:** usa un `TargetEndpoint`. Reserva `ServiceCallout` para llamadas **auxiliares** (enriquecimiento, autorización externa). Ver [extensión](../02-politicas/04-extension.md).

---

## Antipatrones genéricos

### 14. Invocar la API de gestión desde un API proxy

**Qué pasa:** llamas a `apigee.googleapis.com` desde un `ServiceCallout` en el camino del tráfico.

**Por qué duele:** la API de gestión es **lenta**, tiene **cuotas propias** y **acopla el plano de datos al plano de control**. Un incidente en el plano de control tumba tu tráfico.

**Alternativa:** carga los datos de configuración en un **KVM** o **PropertySet**. Ver [herramientas CLI](../06-devops/02-herramientas-cli.md).

---

### 15. Invocar un proxy dentro de otro con código personalizado o como target

**Qué pasa:** encadenas proxies llamando por HTTP a tu propio hostname.

**Por qué duele:** añade un **salto de red completo** (DNS, TLS, balanceador, ingress), duplica el consumo de cuota y de analytics, y multiplica la latencia.

**Alternativa:** usa **`LocalTargetConnection`** para proxies de la misma org y entorno:
```xml
<LocalTargetConnection>
    <APIProxy>comun-auth-v1</APIProxy>
    <ProxyEndpoint>default</ProxyEndpoint>
</LocalTargetConnection>
```
Ver [targets](../01-proxies/05-target-endpoints-y-servidores.md).

---

### 16. Gestionar recursos de Apigee sin control de versiones

**Qué pasa:** editas proxies, productos y KVMs directamente en la consola.

**Por qué duele:** no hay historial, ni revisión por pares, ni forma de reproducir un despliegue, ni de saber quién cambió qué ni cuándo. La recuperación ante un error es manual y propensa a fallos.

**Alternativa:** todo en Git, despliegue por pipeline. Ver [ciclo de vida](../06-devops/01-ciclo-de-vida.md).

---

### 17. Balancear con un solo TargetServer y `MaxFailures` distinto de cero

**Qué pasa:** `<LoadBalancer>` con un único `<Server>` y `<MaxFailures>3</MaxFailures>`.

**Por qué duele:** al alcanzar `MaxFailures`, Apigee marca el servidor como no saludable y **deja de enviarle tráfico**. Como no hay alternativa, **todas** las peticiones fallan. Sin `HealthMonitor`, no se recupera nunca.

**Alternativa:** con un solo servidor, `<MaxFailures>0</MaxFailures>`, o configura siempre un `HealthMonitor`.

---

### 18. Acceder al payload con streaming activo

**Qué pasa:** `request.streaming.enabled=true` o `response.streaming.enabled=true`, y luego políticas que leen el body.

**Por qué duele:** con streaming Apigee **no bufferiza** el mensaje. `ExtractVariables` sobre JSONPath, `JSONThreatProtection`, `JSONtoXML` y `OASValidation` de body **dejan de funcionar**, a menudo de forma silenciosa.

**Alternativa:** activa streaming **solo** cuando el payload lo exija y ninguna política necesite el contenido. Ver [rendimiento](../08-mejores-practicas/03-rendimiento.md).

---

### 19. Definir múltiples `ProxyEndpoint` en un API proxy

**Qué pasa:** el proxy tiene varios `<ProxyEndpoint>`.

**Por qué duele:** complejidad innecesaria, enrutamiento difícil de razonar y de depurar.

**Alternativa:** **un proxy = un ProxyEndpoint**. Si varias APIs comparten el mismo backend o necesitan la misma lógica antes o después de invocarlo, extrae esa lógica a **shared flows** y crea proxies separados. Ver [shared flows](../01-proxies/06-shared-flows-y-flow-hooks.md).

---

## Antipatrones de backend

### 20. Permitir un backend lento

**Qué pasa:** el backend tarda decenas de segundos y no hay timeouts.

**Por qué duele:** un backend lento **mantiene ocupados hilos y conexiones del Message Processor**, que es un recurso compartido. Puede degradar el rendimiento de proxies que no tienen ninguna relación con él.

**Alternativa:** timeouts agresivos (`connect.timeout.millis`, `io.timeout.millis`), `ResponseCache`, `SpikeArrest`/`Quota` hacia el backend (`ConcurrentRateLimit` está retirada) y health monitors.

---

### 21. Deshabilitar las conexiones HTTP persistentes (keep-alive reutilizable)

**Qué pasa:** `keepalive.timeout.millis` a 0.

**Por qué duele:** cada petición al backend abre una **conexión TCP nueva** y repite el **handshake TLS**. Bajo carga, multiplica la latencia y agota puertos efímeros.

**Alternativa:** deja keep-alive activo, con un timeout razonable (60.000 ms es un valor habitual).

---

## Tabla resumen para auditoría

| # | Antipatrón | Grep / señal a buscar |
|---|---|---|
| 1 | Refresh tokens sin refresh flow | `RefreshTokenExpiresIn` sin `Operation>RefreshAccessToken` |
| 2 | `waitForComplete()` en JS | `waitForComplete` en `resources/jsc/` |
| 3 | Tokens OAuth de larga vida | `<ExpiresIn>` > 3600000 |
| 4 | Regex greedy | `\.\*` o `\.\+` o `\)\+\)\+` en `RegularExpressionProtection` |
| 5 | Cachear errores | `ResponseCache` sin `SkipCachePopulation` |
| 6 | Caché > 256 KB | Revisión manual del tamaño del dato |
| 7 | `MessageLogging` múltiple | Más de un `<Name>` de política `MessageLogging` en los flujos |
| 8 | Identificador de alta cardinalidad | `Identifier ref="messageid"` o `="client.ip"` |
| 9 | Cuota no distribuida | `<Distributed>false</Distributed>` |
| 10 | Quota reutilizada | El mismo `<Name>` de `Quota` en varios `<Flow>` |
| 11 | `RaiseFault` inapropiado | `RaiseFault` sin `<FaultResponse>` que corte de verdad |
| 12 | Cabeceras multi-valor | `request.header.accept` sin `.values` |
| 13 | `ServiceCallout` como target | `ServiceCallout` en un proxy sin `<TargetEndpoint>` |
| 14 | API de gestión desde el proxy | `apigee.googleapis.com` en `ServiceCallout` |
| 15 | Proxy dentro de proxy por HTTP | URL del propio hostname en un `TargetEndpoint` |
| 16 | Sin control de versiones | Ausencia de repositorio |
| 17 | LB con 1 server y MaxFailures | `<Server>` único + `<MaxFailures>` > 0 sin `<HealthMonitor>` |
| 18 | Payload con streaming | `streaming.enabled">true` + políticas que leen el body |
| 19 | Múltiples ProxyEndpoint | Más de un archivo en `apiproxy/proxies/` |
| 20 | Backend lento | Ausencia de `io.timeout.millis` |
| 21 | Keep-alive desactivado | `keepalive.timeout.millis">0` |

## Fuentes

- <https://docs.apigee.com/api-platform/antipatterns/intro>
- <https://cloud.google.com/apigee/docs/api-platform/antipatterns/multiple-proxyendpoints>
- <https://docs.apigee.com/api-platform/fundamentals/best-practices-api-proxy-design-and-development>
