---
id: practicas-rendimiento
titulo: Rendimiento
area: practicas
tags: [rendimiento, latencia, optimizacion, overhead, escalabilidad]
aplica_a: [apigee-x, apigee-hybrid]
fuente: https://docs.apigee.com/api-platform/fundamentals/best-practices-api-proxy-design-and-development
revisado: 2026-08-20
---

# Rendimiento

## La métrica que importa

```
Overhead de Apigee = Latencia total − Latencia del backend

  Latencia total   = client.sent.end.timestamp    − client.received.start.timestamp
  Latencia backend = target.received.end.timestamp − target.sent.start.timestamp
```

Si el overhead crece, el problema está en tus políticas, no en el backend. Es la primera métrica a instrumentar.

## Coste relativo de las políticas

| Coste | Políticas | Por qué |
|---|---|---|
| **Muy bajo** | `AssignMessage`, `ExtractVariables`, `HTTPModifier`, `CORS`, `ReadPropertySet` | Manipulación en memoria |
| **Bajo** | `VerifyAPIKey`, `SpikeArrest`, `LookupCache` (acierto) | Lectura cacheada o cálculo local |
| **Medio** | `Quota` asíncrona, `VerifyJWT` (JWKS cacheado), `JSONThreatProtection` | Parseo o sincronización diferida |
| **Alto** | `Quota` síncrona, `KeyValueMapOperations` sin caché, `Javascript` pesado, `XMLtoJSON` de payloads grandes | Acceso a Cassandra o CPU |
| **Muy alto** | `ServiceCallout` sin timeout, regex con backtracking, `httpClient.waitForComplete()` | Bloqueo de red o de hilo |

## Los siete arreglos de mayor impacto

### 1. Quota asíncrona

```xml
<Distributed>true</Distributed>
<Synchronous>false</Synchronous>
<AsynchronousConfiguration>
    <SyncIntervalInSeconds>10</SyncIntervalInSeconds>
</AsynchronousConfiguration>
```

`Synchronous=true` consulta Cassandra en **cada** petición. Con `false`, se sincroniza cada N segundos. El coste es permitir sobreconsumo transitorio; el beneficio es eliminar un acceso a Cassandra por petición.

Usa `Synchronous=true` solo si la cuota tiene consecuencias de facturación estrictas.

### 2. Caché en memoria para los KVM

```xml
<KeyValueMapOperations name="KVM-Config" mapIdentifier="config">
    <Scope>environment</Scope>
    <ExpiryTimeInSecs>300</ExpiryTimeInSecs>   <!-- ← no es opcional -->
    <Get assignTo="config.valor" index="1">
        <Key><Parameter>clave</Parameter></Key>
    </Get>
</KeyValueMapOperations>
```

Sin `<ExpiryTimeInSecs>`, cada petición hace una lectura a Cassandra.

### 3. PropertySet en lugar de KVM cuando el dato es estático

Coste de lectura **cero**: el valor viaja en el bundle.

```
propertyset.config.timeout_backend
```

Regla: si no es un secreto y no cambia por entorno, va en PropertySet.

### 4. ResponseCache bien diseñada

La política de mayor impacto de todas: un acierto de caché elimina **la llamada al backend completa**.

Lo que arruina el hit rate:
- Incluir `client_id` en la cache key sin necesidad.
- Incluir cabeceras variables (`User-Agent`, cabeceras de trazado).
- TTL demasiado corto.

Ver [caching](../05-operacion/04-caching-y-persistencia.md).

### 5. Sustituir JavaScript por políticas nativas

```xml
<!-- Coste alto -->
<Javascript name="JS-ExtraerYAsignar">
    <ResourceURL>jsc://extraer.js</ResourceURL>
</Javascript>

<!-- Coste bajo, mismo resultado -->
<ExtractVariables name="EV-Extraer">...</ExtractVariables>
<AssignMessage name="AM-Asignar">...</AssignMessage>
```

Recomendación explícita de Google: `AssignMessage` y `ExtractVariables` antes que JavaScript siempre que sea posible.

### 6. Timeouts en todos los ServiceCallout

```xml
<ServiceCallout name="SC-Externo">
    <Timeout>3000</Timeout>
    ...
</ServiceCallout>
```

Sin `<Timeout>`, un servicio auxiliar lento arrastra la latencia de tu API entera.

### 7. Regex sin backtracking catastrófico

```
❌  (a+)+          → backtracking exponencial
❌  .*foo.*        → greedy sin anclar
✅  ^[a-z]{1,32}$  → anclado y acotado
✅  .*?foo         → reluctante
```

Es un [antipatrón documentado](../09-antipatrones/01-catalogo-antipatrones.md) y un vector de DoS real.

## Escala y límites de arquitectura

| Aspecto | Recomendación de Google | Consecuencia de superarlo |
|---|---|---|
| **Basepaths por entorno / environment group** | **≤ 3.000** | Aumenta la latencia de **todos** los despliegues, nuevos y existentes |
| Flows por proxy | ≤ 200 (límite duro) | Rechazo del despliegue |
| ProxyEndpoints por proxy | 1 (límite duro: 10) | Complejidad y antipatrón |
| Tamaño del bundle | ≤ 15 MB | Rechazo del despliegue |
| Políticas sin usar | Eliminarlas | Despliegue lento |

## Payload y streaming

| Modo | Límite | Efecto en políticas |
|---|---|---|
| Buffered | **30 MB** | Todas funcionan |
| Streamed | **10 MB** | **Las políticas pierden acceso al contenido** |

> [!CAUTION]
> Activar streaming para "mejorar el rendimiento" sin entender la consecuencia es un error frecuente. Con streaming activo, `ExtractVariables` sobre JSONPath, `JSONThreatProtection`, `OASValidation` de body y cualquier transformación de payload **dejan de funcionar silenciosamente**. Es un [antipatrón documentado](../09-antipatrones/01-catalogo-antipatrones.md).

Actívalo solo cuando el payload realmente lo requiera y ninguna política necesite el cuerpo.

## Keep-alive

```xml
<Properties>
    <Property name="keepalive.timeout.millis">60000</Property>
</Properties>
```

> [!CAUTION]
> **Antipatrón documentado: deshabilitar las conexiones HTTP persistentes (keep-alive).**
> Sin keep-alive, cada petición al backend abre una conexión TCP nueva y repite el handshake TLS. Bajo carga esto multiplica la latencia y agota puertos efímeros. **Nunca pongas `keepalive.timeout.millis` a 0.**

## Backends lentos

> [!CAUTION]
> **Antipatrón documentado: permitir un backend lento.**
> Un backend lento no solo degrada su propia API: **mantiene ocupados hilos y conexiones del Message Processor**, que es un recurso compartido. Un backend con latencia de 30 s puede degradar el rendimiento de proxies que no tienen nada que ver.

Mitigaciones:

```xml
<Properties>
    <Property name="connect.timeout.millis">3000</Property>
    <Property name="io.timeout.millis">10000</Property>
</Properties>
```

Y por encima de eso: `ResponseCache`, `ConcurrentRateLimit` hacia el backend, y health monitors que saquen del balanceo a los nodos degradados.

## Orden del PreFlow

Coloca primero lo más barato y lo que más tráfico descarta:

```
1. CORS                    (barato, corta los preflight)
2. VerifyAPIKey            (descarta tráfico no autenticado)
3. SpikeArrest             (descarta exceso)
4. Quota                   (descarta exceso de plan)
5. Threat protection       (parseo: caro, ya con poco tráfico)
6. OASValidation           (el más caro, el último)
```

No tiene sentido parsear un payload de 5 MB para descubrir después que la API key no era válida.

## Checklist de rendimiento

- [ ] `Quota` con `Synchronous=false` salvo necesidad de facturación estricta
- [ ] Todos los `KeyValueMapOperations` tienen `<ExpiryTimeInSecs>`
- [ ] La configuración estática está en PropertySet, no en KVM
- [ ] Hay `ResponseCache` en los endpoints de lectura cacheables
- [ ] La cache key es la mínima suficiente
- [ ] Todos los `ServiceCallout` tienen `<Timeout>`
- [ ] Todos los TargetEndpoint tienen `connect.timeout.millis` e `io.timeout.millis`
- [ ] Keep-alive **no** está desactivado
- [ ] Ninguna regex usa cuantificadores greedy anidados
- [ ] Ninguna política `Javascript` hace lo que haría `AssignMessage` o `ExtractVariables`
- [ ] Ningún JavaScript usa `httpClient` ni `waitForComplete()`
- [ ] No hay políticas ni recursos sin referenciar en el bundle
- [ ] Menos de 3.000 basepaths por entorno
- [ ] El overhead de Apigee está instrumentado y monitorizado

## Fuentes

- <https://docs.apigee.com/api-platform/fundamentals/best-practices-api-proxy-design-and-development>
- <https://cloud.google.com/apigee/docs/api-platform/reference/limits>
- <https://docs.apigee.com/api-platform/antipatterns/intro>
