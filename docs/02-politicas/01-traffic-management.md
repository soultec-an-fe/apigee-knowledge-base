---
id: politicas-traffic-management
titulo: Políticas de Traffic Management
area: politicas
tags: [quota, spikearrest, responsecache, rate-limiting, cache]
aplica_a: [apigee-x, apigee-hybrid]
fuente: https://cloud.google.com/apigee/docs/api-platform/reference/policies/quota-policy
revisado: 2026-08-20
---

# Políticas de Traffic Management

## Quota vs SpikeArrest — la distinción fundamental

> [!IMPORTANT]
> **Son cosas distintas y se usan juntas, no en alternativa.**
>
> - **Quota** = límite **de negocio**. "Este plan permite 10.000 llamadas al mes." Se cuenta de forma distribuida y persistente contra Cassandra. Es lo que vendes.
> - **SpikeArrest** = límite **de protección**. "No más de 100 peticiones por segundo, para que el backend no muera." Suaviza el tráfico en ventanas muy cortas y no persiste contadores.
>
> Un cliente puede estar dentro de su cuota mensual y aun así ser frenado por SpikeArrest si lanza todo de golpe.

---

## Quota

```xml
<Quota continueOnError="false" enabled="true" name="Q-CuotaPorProducto" type="calendar">
    <DisplayName>Cuota por producto</DisplayName>

    <!-- El identificador determina CONTRA QUIÉN se cuenta -->
    <Identifier ref="client_id"/>

    <!-- Valores por defecto, sobrescritos por los del API product -->
    <Allow countRef="apiproduct.developer.quota.limit" count="1000"/>
    <Interval ref="apiproduct.developer.quota.interval">1</Interval>
    <TimeUnit ref="apiproduct.developer.quota.timeunit">hour</TimeUnit>

    <Distributed>true</Distributed>
    <Synchronous>false</Synchronous>
    <AsynchronousConfiguration>
        <SyncIntervalInSeconds>10</SyncIntervalInSeconds>
    </AsynchronousConfiguration>

    <StartTime>2026-01-01 00:00:00</StartTime>
</Quota>
```

### Tipos de Quota

| `type` | Comportamiento |
|---|---|
| `calendar` | Ventana fija anclada a `<StartTime>`. Se reinicia en límites de calendario. |
| `rollingwindow` | Ventana deslizante: cuenta las llamadas de los últimos N periodos desde *ahora*. |
| `flexi` | La ventana arranca con la primera petición de cada identificador. |
| *(sin `type`)* | Por defecto. Ventana fija que arranca en `<StartTime>`. |

### Distributed y Synchronous

| Combinación | Efecto | Cuándo |
|---|---|---|
| `Distributed=true`, `Synchronous=true` | Contador exacto entre todos los MPs. Máxima precisión, **máxima latencia**. | Facturación estricta |
| `Distributed=true`, `Synchronous=false` | Contador compartido, sincronizado cada `SyncIntervalInSeconds`. Permite sobreconsumo transitorio. | **Recomendado por defecto** |
| `Distributed=false` | Cada MP cuenta por separado. El límite efectivo es `count × número de MPs`. | Casi nunca |

> [!CAUTION]
> **Antipatrón documentado: configurar cuota no distribuida.** Con `Distributed=false` el límite real es impredecible porque depende del número de Message Processors, que Apigee escala automáticamente. Usa siempre `<Distributed>true</Distributed>` salvo que sepas exactamente por qué no.

Límites: intervalo de sincronización **≥ 10 segundos**; intervalo de cuota mínimo **1 minuto**, máximo **1 año**.

### Elegir el Identifier

```xml
<Identifier ref="client_id"/>        <!-- por app: lo habitual -->
<Identifier ref="developer.id"/>      <!-- por desarrollador -->
<Identifier ref="apiproduct.name"/>   <!-- global por producto -->
<Identifier ref="request.header.x-tenant-id"/>  <!-- por tenant -->
```

> [!CAUTION]
> **Antipatrón documentado: identificadores de alta cardinalidad en Quota.**
> Nunca uses como `Identifier` algo con cardinalidad ilimitada: `messageid`, un UUID de petición, un timestamp, o `client.ip` en una API pública masiva. Cada valor distinto crea una fila de contador en Cassandra. El resultado es explosión de almacenamiento y degradación del runtime.

> [!CAUTION]
> **Antipatrón documentado: reutilizar una política Quota.**
> Adjuntar la **misma** política `Quota` en varios flujos hace que **todos compartan el contador**, aunque conceptualmente sean límites distintos. Si necesitas cuotas separadas, crea políticas separadas (con `<Quota>` distintos), no reutilices una.

### Cuota tomada del API product

El patrón correcto: el API product define la cuota, la política solo la lee.

```xml
<Quota name="Q-DesdeProducto">
    <Identifier ref="client_id"/>
    <Allow countRef="apiproduct.developer.quota.limit" count="100"/>
    <Interval ref="apiproduct.developer.quota.interval">1</Interval>
    <TimeUnit ref="apiproduct.developer.quota.timeunit">hour</TimeUnit>
    <Distributed>true</Distributed>
    <Synchronous>false</Synchronous>
</Quota>
```

Así, cambiar el plan de un cliente es cambiar el producto, sin tocar ni redesplegar el proxy.

### Devolver cabeceras de rate limit

```xml
<AssignMessage name="AM-CabecerasCuota">
    <Set>
        <Headers>
            <Header name="X-RateLimit-Limit">{ratelimit.Q-DesdeProducto.allowed.count}</Header>
            <Header name="X-RateLimit-Remaining">{ratelimit.Q-DesdeProducto.available.count}</Header>
            <Header name="X-RateLimit-Reset">{ratelimit.Q-DesdeProducto.expiry.time}</Header>
        </Headers>
    </Set>
    <IgnoreUnresolvedVariables>true</IgnoreUnresolvedVariables>
    <AssignTo createNew="false" transport="http" type="response"/>
</AssignMessage>
```

---

## SpikeArrest

```xml
<SpikeArrest continueOnError="false" enabled="true" name="SA-FrenoDePicos">
    <DisplayName>Freno de picos</DisplayName>
    <Rate>100ps</Rate>
    <Identifier ref="client_id"/>
    <UseEffectiveCount>true</UseEffectiveCount>
</SpikeArrest>
```

### Cómo funciona realmente

SpikeArrest **no** es un contador por segundo. Divide el intervalo y aplica un **espaciado mínimo entre peticiones**:

- `<Rate>100ps</Rate>` → una petición cada **10 ms**. La petición 2 que llegue a los 3 ms se rechaza, aunque en ese segundo solo lleves 2.
- `<Rate>60pm</Rate>` → una petición cada **1 segundo**.

Esto sorprende a mucha gente: `100ps` **no** significa "acepto una ráfaga de 100 y luego bloqueo".

Límites de plataforma: máximo **4.000 por segundo** y **240.000 por minuto**.

### Rate dinámico

```xml
<SpikeArrest name="SA-Dinamico">
    <Rate ref="spikearrest.rate.variable">30ps</Rate>
    <Identifier ref="client_id"/>
</SpikeArrest>
```

### UseEffectiveCount

Con `true`, el rate se distribuye entre los Message Processors disponibles en lugar de aplicarse por MP. Recomendado en despliegues multi-región.

### Colocación

ProxyEndpoint → PreFlow → Request, **después** de la autenticación, para que `client_id` esté resuelto y el freno sea por cliente en lugar de global.

---

## ResponseCache

Cachea la respuesta completa. Es la política de mayor impacto en latencia y coste de backend.

```xml
<ResponseCache continueOnError="false" enabled="true" name="RC-CachearCatalogo">
    <DisplayName>Cachear catálogo</DisplayName>

    <CacheKey>
        <Prefix>catalogo</Prefix>
        <KeyFragment ref="proxy.pathsuffix" type="string"/>
        <KeyFragment ref="request.querystring" type="string"/>
    </CacheKey>

    <CacheResource>cache-catalogo</CacheResource>
    <Scope>Exclusive</Scope>

    <ExpirySettings>
        <TimeoutInSeconds>300</TimeoutInSeconds>
    </ExpirySettings>

    <!-- NO cachear errores ni métodos no idempotentes -->
    <SkipCacheLookup>request.header.cache-control = "no-cache"</SkipCacheLookup>
    <SkipCachePopulation>response.status.code != 200 or request.verb != "GET"</SkipCachePopulation>

    <UseAcceptHeader>false</UseAcceptHeader>
    <UseResponseCacheHeaders>false</UseResponseCacheHeaders>
</ResponseCache>
```

### Reglas de oro

1. **Nunca caches respuestas no exitosas ni métodos no-GET.** El `<SkipCachePopulation>` de arriba es prácticamente obligatorio.
   > **Antipatrón documentado: cachear respuestas de error.** Cachear un 500 propaga el fallo del backend a todos los clientes durante todo el TTL.

2. **La cache key debe ser suficiente.** `request.querystring` suele ser el identificador único adecuado. Si olvidas un fragmento, sirves la respuesta de un cliente a otro.

3. **No incluyas la API key (`client_id`) en la cache key** salvo que la respuesta sea realmente distinta por cliente. Incluirla multiplica las entradas y destruye el hit rate.

4. **Un solo content-type por caché.** Cachea siempre XML o siempre JSON; si mezclas, convierte antes de cachear.

5. **Coloca lookup y populate en el sitio correcto:**
   - *Lookup* → **ProxyEndpoint → PreFlow → Request** (lo más cerca del cliente, para cortocircuitar antes).
   - *Populate* → **ProxyEndpoint → PostFlow → Response** (después de toda la mediación, para cachear el resultado final).

6. **Si usas CORS, asegúrate de que la respuesta de CORS no se cachea.** Es una advertencia explícita de Google.

7. **Con varias políticas de caché en el mismo proxy**, usa condiciones mutuamente excluyentes y **recursos de caché distintos**.

### Límites de caché

| Límite | Valor |
|---|---|
| Cachés con scope de entorno | 100 |
| Tamaño de la clave | 2 KB |
| Tamaño del valor | **256 KB** |
| Expiración | ≥ 1 segundo, ≤ 30 días |
| Elementos por caché | 10 millones |

> [!CAUTION]
> **Antipatrón documentado: almacenar datos mayores de 256 KB en caché.** Se rechaza o se trunca. Para objetos grandes, cachea una referencia (por ejemplo una URL de Cloud Storage), no el objeto.

---

## LookupCache / PopulateCache / InvalidateCache

Caché de propósito general para valores arbitrarios, no respuestas HTTP completas. Uso típico: cachear un token del backend.

```xml
<!-- Buscar -->
<LookupCache continueOnError="false" enabled="true" name="LC-TokenBackend">
    <CacheKey>
        <Prefix>token-backend</Prefix>
        <KeyFragment>global</KeyFragment>
    </CacheKey>
    <CacheResource>cache-tokens</CacheResource>
    <Scope>Exclusive</Scope>
    <AssignTo>token.backend.cacheado</AssignTo>
</LookupCache>

<!-- Guardar -->
<PopulateCache continueOnError="false" enabled="true" name="PC-TokenBackend">
    <CacheKey>
        <Prefix>token-backend</Prefix>
        <KeyFragment>global</KeyFragment>
    </CacheKey>
    <CacheResource>cache-tokens</CacheResource>
    <Scope>Exclusive</Scope>
    <ExpirySettings>
        <TimeoutInSeconds>3000</TimeoutInSeconds>
    </ExpirySettings>
    <Source>token.backend.nuevo</Source>
</PopulateCache>

<!-- Invalidar -->
<InvalidateCache continueOnError="false" enabled="true" name="IC-TokenBackend">
    <CacheKey>
        <Prefix>token-backend</Prefix>
        <KeyFragment>global</KeyFragment>
    </CacheKey>
    <CacheResource>cache-tokens</CacheResource>
    <Scope>Exclusive</Scope>
    <PurgeChildEntries>true</PurgeChildEntries>
</InvalidateCache>
```

Patrón completo:

```xml
<PreFlow>
  <Request>
    <Step><Name>LC-TokenBackend</Name></Step>
    <Step>
      <Name>SC-ObtenerTokenNuevo</Name>
      <Condition>token.backend.cacheado is null</Condition>
    </Step>
    <Step>
      <Name>PC-TokenBackend</Name>
      <Condition>token.backend.cacheado is null</Condition>
    </Step>
  </Request>
</PreFlow>
```

### Scope

| Valor | Ámbito de la clave |
|---|---|
| `Global` | Todos los proxies del entorno |
| `Application` | El proxy actual |
| `Proxy` | El ProxyEndpoint actual |
| `Target` | El TargetEndpoint actual |
| `Exclusive` | Proxy + endpoint. El más específico. **Por defecto** |

---

## ResetQuota

Reinicia el contador de una Quota, típicamente en un endpoint administrativo protegido.

```xml
<ResetQuota name="RQ-ReiniciarCuota">
    <Quota name="Q-DesdeProducto">
        <Identifier ref="request.queryparam.client_id">
            <Allow>0</Allow>
        </Identifier>
    </Quota>
</ResetQuota>
```

---

## ConcurrentRateLimit — retirada, no usar

> [!CAUTION]
> **`ConcurrentRateLimit` está retirada.** Se deprecó el 15/07/2020 y se retiró de Private Cloud en la versión 4.50.00 (15/07/2021). Google explica el motivo: su arquitectura afectaba al rendimiento de las APIs que la usaban. **No existe en Apigee X.** Si ves este XML en un ejemplo o tutorial antiguo, es de Apigee Edge legacy.
>
> Para limitar la carga hacia un backend con pool de conexiones fijo, usa **`SpikeArrest`** combinada con **`Quota`**, o considera encadenar proxies y shared flows según recomienda la propia nota de deprecación de Google.

## Fuentes

- <https://cloud.google.com/apigee/docs/api-platform/reference/policies/quota-policy>
- <https://cloud.google.com/apigee/docs/api-platform/reference/policies/spike-arrest-policy>
- <https://cloud.google.com/apigee/docs/api-platform/reference/policies/response-cache-policy>
- <https://cloud.google.com/apigee/docs/api-platform/reference/limits>
- <https://docs.apigee.com/release/deprecated-features> (retirada de ConcurrentRateLimit)
