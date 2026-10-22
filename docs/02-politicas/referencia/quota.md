---
id: politica-quota
titulo: Quota — referencia completa
area: politicas
tags: [quota, cuota, rate-limiting, api-product, rollingwindow, calendar, flexi, sharedname, llm, extensible]
aplica_a: [apigee-x, apigee-hybrid, apigee-edge]
elemento_xml: Quota
tipo_politica: extensible
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/quota-policy
fuente_edge: https://docs.apigee.com/api-platform/reference/policies/quota-policy
revisado: 2026-10-22
---

# Quota — referencia completa

> [!NOTE]
> **Tipo:** Extensible (solo entornos Intermediate y Comprehensive; puede tener implicaciones de coste según la licencia). **Elemento raíz:** `<Quota>`.
> **Aplica a:** Apigee X, hybrid y Edge. `<SharedName>`, `<CountOnly>` y `<EnforceOnly>` solo existen en X/hybrid.

Quota cuenta peticiones dentro de un periodo (minuto, hora, día, semana, mes) y rechaza las que superan el cupo hasta que el contador se reinicia, o hasta que una política [ResetQuota](../01-traffic-management.md#resetquota) lo reinicia antes. Es la herramienta para **contratos de consumo**: planes, SLAs, niveles de suscripción.

## Cuándo usarla (y cuándo no)

| Necesidad | Política |
|---|---|
| Límite contratado por app, desarrollador o plan (10 000/mes, 500/hora) | **Quota** |
| Proteger el backend de un pico de tráfico | [SpikeArrest](spike-arrest.md) |
| Cupo de tokens de LLM | `LLMTokenQuota`, o Quota con `<SharedName>` y peso por tokens ([ver ejemplo 5](#5-cupo-de-tokens-de-un-llm-con-contador-compartido)) |
| Límites por segundo | SpikeArrest; Quota solo admite `second` con contadores no distribuidos |

## Modelo de contadores

Entender **cuántos contadores** mantiene la política es lo que evita sorpresas.

| Situación | Contadores |
|---|---|
| Proxy sin API product | **Uno por política**, identificado por su `name`. Si la misma política se adjunta en tres flujos, los tres incrementan el mismo contador. |
| Varias políticas Quota con distinto `name` | Un contador por política. |
| `<Identifier ref>` | Un contador por cada valor distinto de la variable (p. ej. por `client_id`). |
| `<Class ref>` | Un contador por cada clase (`<Allow class>`) definida. |
| Proxy dentro de un API product con cuota | Por defecto, **un contador por operación** del producto (ver abajo). |

Los contadores tienen siempre **alcance de proxy**: dos proxies con políticas Quota del mismo nombre mantienen contadores separados, y un API product con tres proxies no comparte un único cupo entre los tres.

> [!WARNING]
> Adjuntar la misma política Quota en varios flujos de un proxy es un antipatrón: el cupo se agota más rápido de lo esperado porque todas las ejecuciones cuentan contra el mismo contador.

### Cuotas definidas en el API product

Fijar cuota en un API product **no la aplica**: hace falta una política Quota en el proxy que lea esos valores. Requisitos:

1. Una `VerifyAPIKey`, o una `OAuthV2` con operación `VerifyAccessToken`, **antes** de la Quota en el flujo de request. Es la que identifica el producto; sin ella la Quota no sabe qué configuración aplicar y el contador del producto no se actualiza.
2. La Quota con `<UseQuotaConfigInAPIProduct stepName="...">` o con referencias explícitas a las variables `verifyapikey.{politica}.apiproduct.developer.quota.*`.

Reglas de precedencia dentro del producto:

| Configuración del producto | Qué se aplica |
|---|---|
| La operación tiene cuota propia | La de la operación (contador propio). |
| La operación no tiene cuota, el producto sí | La del producto. |
| Ni producto ni operación tienen cuota | La definida en la política Quota. |

El atributo `quotaCounterScope` del API product cambia el agrupamiento. Se fija con la API de gestión `/apiproducts`:

| `quotaCounterScope` | Efecto |
|---|---|
| `PRODUCT` | La cuota se aplica a nivel de producto. |
| `PROXY` | Las operaciones **sin cuota propia** asociadas a un mismo proxy comparten un contador por proxy. Las operaciones con cuota propia siguen teniendo su contador. |

## Tipos de cuota (atributo `type`)

| `type` | Cuándo arranca | Cuándo se reinicia |
|---|---|---|
| *(omitido)* | Al inicio de la unidad de tiempo en curso | Al empezar la siguiente unidad: el próximo minuto, la próxima hora en punto, la medianoche GMT, el domingo a medianoche GMT, o el último día del mes a medianoche GMT. |
| `calendar` | En la fecha y hora de `<StartTime>` | Cada `<Interval>` × `<TimeUnit>` contados desde `<StartTime>`. Un "mes" equivale a 28 días. |
| `flexi` | Con la **primera petición** de cada app | Cada `<Interval>` × `<TimeUnit>` contados desde esa primera petición. Un "mes" equivale a 28 días. |
| `rollingwindow` | — | **Nunca**: en cada petición se recalcula cuántas hubo en la ventana inmediatamente anterior (p. ej. las últimas 2 horas). |

Todas las horas se expresan en **UTC/GMT** con formato ISO 8601 `yyyy-MM-dd HH:mm:ss`. `24:00:00` de un día equivale a `00:00:00` del siguiente; se prefiere la segunda forma.

## Sintaxis completa

```xml
<Quota name="Q-Nombre" type="calendar" continueOnError="false" enabled="true">
  <DisplayName>Nombre legible</DisplayName>
  <Allow count="1000" countRef="variable.con.limite"/>
  <Interval ref="variable.con.intervalo">1</Interval>
  <TimeUnit ref="variable.con.unidad">month</TimeUnit>
  <StartTime>2026-01-01 00:00:00</StartTime>
  <Distributed>true</Distributed>
  <Synchronous>false</Synchronous>
  <AsynchronousConfiguration>
    <SyncIntervalInSeconds>20</SyncIntervalInSeconds>
    <SyncMessageCount>5</SyncMessageCount>
  </AsynchronousConfiguration>
  <Identifier ref="client_id"/>
  <MessageWeight ref="variable.con.peso"/>
</Quota>
```

Las variantes con `<Class>`, `<UseQuotaConfigInAPIProduct>` y contadores compartidos están en sus secciones. Combinaciones excluyentes:

- `<Class>` e `<Identifier>` **no pueden ir juntos**.
- `<UseQuotaConfigInAPIProduct>` hace que se ignoren `<Allow>`, `<Interval>` y `<TimeUnit>` del nivel raíz.
- `<CountOnly>` y `<EnforceOnly>` son excluyentes, y ambos exigen `<SharedName>`.
- `<StartTime>` solo se admite con `type="calendar"`.

## Atributos del elemento raíz

| Atributo | Obligatorio | Default | Qué hace |
|---|---|---|---|
| `name` | Sí | — | Nombre interno; también nombra el contador y las variables `ratelimit.{name}.*`. Máximo 255 caracteres. |
| `type` | No | *(omitido)* | `calendar`, `flexi` o `rollingwindow`. Ver [Tipos de cuota](#tipos-de-cuota-atributo-type). |
| `continueOnError` | No | `false` | Con `true`, el flujo sigue aunque la cuota se haya superado. |
| `enabled` | No | `true` | Con `false` la política no se ejecuta. |
| `async` | No | `false` | **Obsoleto.** |

## Elementos hijos

| Elemento | Obligatorio | Tipo | Default | Resumen |
|---|---|---|---|---|
| `<DisplayName>` | No | String | valor de `name` | Etiqueta en la UI. |
| `<Allow>` | No | Integer o complejo | `count="2000"` | Límite del contador. |
| `<Class ref>` (dentro de `<Allow>`) | No | Complejo | — | Elige el límite según el valor de una variable. |
| `<Interval>` | **Sí** | Integer | — | Cuántas unidades de tiempo dura el periodo. |
| `<TimeUnit>` | **Sí** | String | — | `minute`, `hour`, `day`, `week`, `month` (ver nota sobre `second` y `year`). |
| `<StartTime>` | Con `calendar` | ISO 8601 | — | Inicio del primer periodo. |
| `<Distributed>` | No | Boolean | `false` | Contador central compartido entre nodos. |
| `<Synchronous>` | No | Boolean | `false` | Actualizar el contador central en cada petición. |
| `<AsynchronousConfiguration>` | No | Complejo | cada 10 s | Cadencia de sincronización asíncrona. |
| `<Identifier ref>` | No | String | — | Un contador por valor de la variable. |
| `<MessageWeight ref>` | No | Integer | 1 | Peso de cada petición. |
| `<UseQuotaConfigInAPIProduct stepName>` | No | Complejo | — | Tomar la cuota del API product. |
| `<SharedName>` | No | String | — | Solo X/hybrid. Contador compartido entre políticas del mismo proxy. |
| `<CountOnly>` | No | Boolean | `false` | Solo X/hybrid. Cuenta sin rechazar. |
| `<EnforceOnly>` | No | Boolean | `false` | Solo X/hybrid. Rechaza sin contar. |

### `<Allow>`

| Atributo | Default | Qué hace |
|---|---|---|
| `count` | `2000` | Límite estático. Con `<Interval>1</Interval>` y `<TimeUnit>month</TimeUnit>`, `count="100"` significa 100 peticiones al mes. |
| `countRef` | — | Variable con el límite. **Tiene prioridad** sobre `count`; si no resuelve en runtime, se usa `count`. |

Esta regla de "la referencia gana y el valor literal es el respaldo" se aplica igual a `<Interval ref>` y a `<TimeUnit ref>`.

### `<Class>` y `<Allow class>`

`<Class ref="variable">` dentro de `<Allow>` elige el límite según el valor de la variable. Cada `<Allow class="X" count="N"/>` hijo es **un contador distinto**.

| Elemento | Atributo | Obligatorio | Qué hace |
|---|---|---|---|
| `<Class>` | `ref` | Sí | Variable cuyo valor selecciona la clase. |
| `<Allow>` (hijo de `<Class>`) | `class` | Sí | Valor que debe tener la variable para usar este límite; también nombra el contador. |
| `<Allow>` (hijo de `<Class>`) | `count` | Sí | Límite para esa clase. |

Si la variable trae un valor que no coincide con ninguna clase, la política responde con **violación de cuota**, no con un error de configuración. Conviene normalizar el valor antes, por ejemplo con un `AssignMessage` que fije una clase por defecto.

### `<Interval>` y `<TimeUnit>`

`<Interval>` es un entero que se multiplica por `<TimeUnit>`: `24` + `hour` es un periodo de 24 horas. Ambos admiten `ref`.

> [!WARNING]
> **Unidades de tiempo: la documentación oficial es inconsistente.**
> - El texto del elemento en X/hybrid menciona `minute`, `hour`, `day`, `week`, `month` **y `year`**, pero el error de despliegue `InvalidQuotaTimeUnit` solo reconoce de `minute` a `month`. Usa `year` solo después de probarlo en tu entorno.
> - `second` existe pero **solo con `<Distributed>false</Distributed>`**. En Edge, combinarlo con `true` falla al desplegar (`InvalidTimeUnitForDistributedQuota`). Para límites por segundo usa SpikeArrest.

### `<StartTime>`

Fecha y hora UTC de inicio con formato `yyyy-MM-dd HH:mm:ss`. Solo con `type="calendar"`; con otro tipo el despliegue falla (`StartTimeNotSupported`). Un formato inválido también falla al desplegar (`InvalidStartTime`).

> [!WARNING]
> La página oficial se contradice sobre qué pasa si falta `<StartTime>` con `type="calendar"`. En un punto dice que Apigee devuelve un error, y en otro que el periodo arranca el primer día del mes en curso. Decláralo siempre que uses `calendar`.

### `<Distributed>`, `<Synchronous>` y `<AsynchronousConfiguration>`

| Configuración | Precisión | Coste |
|---|---|---|
| `Distributed=false` (default) | Cada nodo cuenta por su cuenta: con N nodos el cupo real puede llegar a ser N veces el configurado | Mínimo |
| `Distributed=true`, `Synchronous=false` | Contador central actualizado de forma asíncrona (cada 10 s por defecto): pueden colarse algunas peticiones de más | Bajo |
| `Distributed=true`, `Synchronous=true` | Exacto: el contador se actualiza al comprobar cada petición | Mayor latencia y menor throughput; bajo mucha carga algunas transacciones pueden fallar |

Para contratos de consumo usa al menos `Distributed=true`.

`<AsynchronousConfiguration>` solo actúa con `Synchronous=false`; con `true` se ignora.

| Hijos presentes | Sincroniza cada… |
|---|---|
| Ninguno (o elemento ausente) | 10 segundos |
| Solo `<SyncIntervalInSeconds>N` | N segundos (mínimo 10, ver [Límites](../../10-referencia/01-limites.md)) |
| Solo `<SyncMessageCount>M` | M mensajes o 10 segundos, lo que ocurra primero |
| Ambos | M mensajes o N segundos, lo que ocurra primero |

### `<Identifier>`

Reparte el conteo en "cubetas" según el valor de una variable. Las más habituales son `client_id` (por app) y `developer.id` (por desarrollador, sumando todas sus apps), ambas pobladas por `VerifyAPIKey` u `OAuthV2`. También sirve cualquier variable propia.

Sin `<Identifier>` (ni `<Class>`), **un único contador** para todos los llamantes.

> [!NOTE]
> Google advierte que `developer.id` y `developer.app.id` podrían cambiar de valor en alguna ventana de mantenimiento, algo raro pero posible. Si ocurre, la cuota no se aplica estrictamente mientras dura el cambio.

### `<MessageWeight>`

Peso entero de cada petición, siempre leído de una variable: una cabecera, un parámetro, un campo extraído del payload o un valor calculado. Casos típicos: `POST` pesa 2 y `GET` pesa 1, o el peso es el número de tokens de un LLM. **Peso `0` = la petición no cuenta.** Un valor no entero produce `InvalidMessageWeight` (`500`).

### `<UseQuotaConfigInAPIProduct>` y `<DefaultConfig>`

```xml
<Quota name="Q-Del-Producto">
  <UseQuotaConfigInAPIProduct stepName="VAK-Header">
    <DefaultConfig>
      <Allow>5000</Allow>
      <Interval>1</Interval>
      <TimeUnit>day</TimeUnit>
    </DefaultConfig>
  </UseQuotaConfigInAPIProduct>
  <Distributed>true</Distributed>
</Quota>
```

| Elemento / atributo | Obligatorio | Qué hace |
|---|---|---|
| `stepName` | Sí | Nombre de la política `VerifyAPIKey` u `OAuthV2` (operación de validación de token) que identificó el producto. |
| `<DefaultConfig>` | No | Valores de respaldo si el producto no define cuota. Si se declara, sus tres hijos (`<Allow>`, `<Interval>`, `<TimeUnit>`) son obligatorios. |

Si el producto o la operación definen cuota, **ganan sobre `<DefaultConfig>`**.

### `<SharedName>`, `<CountOnly>` y `<EnforceOnly>` (solo X/hybrid)

Sirven para **comprobar el cupo en la petición pero cobrar en la respuesta**, cuando el coste real solo se conoce después: tokens de un LLM, `total_slot_ms` de BigQuery, filas devueltas.

| Elemento | Dónde va | Qué hace |
|---|---|---|
| `<SharedName>nombre</SharedName>` | En todas las políticas que comparten contador | Las Quota del mismo proxy con el mismo valor usan **un único contador**. |
| `<EnforceOnly>true</EnforceOnly>` | Request del ProxyEndpoint | Rechaza si ya no hay cupo, **sin incrementar** el contador. |
| `<CountOnly>true</CountOnly>` | Response del ProxyEndpoint | **Incrementa** el contador con el peso real, sin devolver error aunque se pase del límite. |

Ver el [ejemplo 5](#5-cupo-de-tokens-de-un-llm-con-contador-compartido).

## Variables de flujo

`{name}` es el atributo `name` de la política.

| Variable | Tipo | Contenido |
|---|---|---|
| `ratelimit.{name}.allowed.count` | Long | Límite aplicado. |
| `ratelimit.{name}.used.count` | Long | Consumo en el periodo actual. |
| `ratelimit.{name}.available.count` | Long | Cupo restante en el periodo actual. |
| `ratelimit.{name}.exceed.count` | Long | `1` una vez superada la cuota. |
| `ratelimit.{name}.total.exceed.count` | Long | `1` una vez superada la cuota. |
| `ratelimit.{name}.expiry.time` | Long | Momento UTC (ms) en que se reinicia el contador. **No es válida con `rollingwindow`**, porque ese tipo no se reinicia. |
| `ratelimit.{name}.identifier` | String | Valor del identificador usado. |
| `ratelimit.{name}.class` | String | Clase aplicada. |
| `ratelimit.{name}.class.allowed.count` | Long | Límite de la clase. |
| `ratelimit.{name}.class.used.count` | Long | Consumo de la clase. |
| `ratelimit.{name}.class.available.count` | Long | Cupo restante de la clase. |
| `ratelimit.{name}.class.exceed.count` | Long | Peticiones por encima del límite de la clase en el periodo actual. |
| `ratelimit.{name}.class.total.exceed.count` | Long | Suma de `class.exceed.count` de todos los periodos. |
| `ratelimit.{name}.failed` | Boolean | Si la política falló. |

Todas son de solo lectura.

## Errores

### En runtime

| Código de fallo | HTTP | Causa |
|---|---|---|
| `policies.ratelimit.QuotaViolation` | 429 en X/hybrid · 500 en Edge (ver nota) | Se superó la cuota. |
| `policies.ratelimit.FailedToResolveQuotaIntervalReference` | 500 | `<Interval>` no está definido o su `ref` no resolvió. |
| `policies.ratelimit.FailedToResolveQuotaIntervalTimeUnitReference` | 500 | `<TimeUnit>` no está definido o su `ref` no resolvió. |
| `policies.ratelimit.InvalidMessageWeight` | 500 | El peso no es un entero. |

> [!IMPORTANT]
> **El código HTTP de `QuotaViolation` difiere por edición, y la propia documentación se contradice.**
> - **X/hybrid:** la tabla de errores de la página dice `500`, pero la nota final de la misma página dice que al superar los umbrales de Quota o SpikeArrest el sistema devuelve `429 Too Many Requests`.
> - **Edge:** devuelve `500` por defecto. Pasa a `429` activando la propiedad de organización `features.isHTTPStatusTooManyRequestEnabled`: en Edge Cloud lo hace soporte, y en Private Cloud se fija tú mismo con la API de gestión.
>
> En cualquier edición, **no dependas del código de estado**: detecta el caso con `fault.name = "QuotaViolation"` y fija tú el `429` en la FaultRule (ver [ejemplo 4](#4-cabeceras-de-consumo-y-429-explícito)).

### Al desplegar

| Error | Causa |
|---|---|
| `InvalidQuotaInterval` | `<Interval>` no es entero (p. ej. `0.1`). |
| `InvalidQuotaTimeUnit` | Unidad no soportada. |
| `InvalidQuotaType` | `type` distinto de `calendar`, `flexi`, `rollingwindow` (o *default*). |
| `InvalidStartTime` | `<StartTime>` no tiene formato `yyyy-MM-dd HH:mm:ss`. |
| `StartTimeNotSupported` | `<StartTime>` con un `type` que no es `calendar`. |
| `InvalidSynchronizeIntervalForAsyncConfiguration` | `<SyncIntervalInSeconds>` menor que cero. |
| `InvalidAsynchronizeConfigurationForSynchronousQuota` | `<AsynchronousConfiguration>` junto con `<Synchronous>true</Synchronous>`. |
| `InvalidTimeUnitForDistributedQuota` | (Documentado en Edge) `second` con `<Distributed>true</Distributed>`. |

### Variables de fallo

| Variable | Ejemplo |
|---|---|
| `fault.name` | `fault.name = "QuotaViolation"` |
| `ratelimit.{name}.failed` | `ratelimit.Q-Por-App.failed = true` |

Captura por `fault.detail.errorcode` o `fault.name`, nunca por el texto de `faultstring`.

## Ejemplos

### 1. Cupo mensual por app tomado del API product

La forma recomendada: el negocio cambia el cupo en el producto sin redesplegar el proxy.

```xml
<Quota name="Q-Mensual-Producto">
  <UseQuotaConfigInAPIProduct stepName="VAK-Header">
    <DefaultConfig>
      <Allow>1000</Allow>
      <Interval>1</Interval>
      <TimeUnit>month</TimeUnit>
    </DefaultConfig>
  </UseQuotaConfigInAPIProduct>
  <Identifier ref="client_id"/>
  <Distributed>true</Distributed>
</Quota>
```

### 2. Ventana deslizante de una hora por desarrollador

Cuenta todas las apps del mismo desarrollador y evita el "efecto reinicio" de las cuotas de calendario, en el que todo el mundo vuelve a llamar justo a la hora en punto.

```xml
<Quota name="Q-Hora-Desarrollador" type="rollingwindow">
  <Allow count="3000"/>
  <Interval>1</Interval>
  <TimeUnit>hour</TimeUnit>
  <Identifier ref="developer.id"/>
  <Distributed>true</Distributed>
</Quota>
```

### 3. Planes por nivel con `<Class>`

El nivel se guarda como atributo personalizado `plan` de la app y se normaliza antes en una variable `plan.normalizado` (con `basico` como valor por defecto), para que un valor inesperado no se convierta en violación de cuota.

```xml
<Quota name="Q-Por-Plan">
  <Allow>
    <Class ref="plan.normalizado">
      <Allow class="basico" count="1000"/>
      <Allow class="pro" count="50000"/>
      <Allow class="empresa" count="1000000"/>
    </Class>
  </Allow>
  <Interval>1</Interval>
  <TimeUnit>day</TimeUnit>
  <Distributed>true</Distributed>
</Quota>
```

> [!NOTE]
> `<Class>` no se combina con `<Identifier>`. Si necesitas "un cupo por app según su plan", toma el límite de una variable con `countRef` y usa `<Identifier ref="client_id"/>` en vez de `<Class>`.

### 4. Cabeceras de consumo y 429 explícito

Después de la Quota, en la respuesta, se exponen el límite, el consumo y el reinicio. En la FaultRule se fija el `429` sin depender de la edición.

```xml
<AssignMessage name="AM-Cabeceras-Cuota">
  <Set>
    <Headers>
      <Header name="X-RateLimit-Limit">{ratelimit.Q-Mensual-Producto.allowed.count}</Header>
      <Header name="X-RateLimit-Remaining">{ratelimit.Q-Mensual-Producto.available.count}</Header>
      <Header name="X-RateLimit-Reset">{ratelimit.Q-Mensual-Producto.expiry.time}</Header>
    </Headers>
  </Set>
  <IgnoreUnresolvedVariables>true</IgnoreUnresolvedVariables>
  <AssignTo createNew="false" transport="http" type="response"/>
</AssignMessage>
```

```xml
<FaultRules>
  <FaultRule name="fr-cuota-agotada">
    <Condition>fault.name = "QuotaViolation"</Condition>
    <Step>
      <Name>AM-Error-Cuota-429</Name>
    </Step>
  </FaultRule>
</FaultRules>
```

```xml
<AssignMessage name="AM-Error-Cuota-429">
  <Set>
    <StatusCode>429</StatusCode>
    <ReasonPhrase>Too Many Requests</ReasonPhrase>
    <Payload contentType="application/json">{"codigo":"CUOTA_AGOTADA","mensaje":"Se alcanzó el cupo del plan."}</Payload>
  </Set>
  <IgnoreUnresolvedVariables>true</IgnoreUnresolvedVariables>
  <AssignTo createNew="false" transport="http" type="response"/>
</AssignMessage>
```

### 5. Cupo de tokens de un LLM con contador compartido

Objetivo: 200 000 tokens por hora y por app, contando los tokens reales que informa el modelo en la respuesta.

ProxyEndpoint:

```xml
<ProxyEndpoint name="default">
  <PreFlow name="PreFlow">
    <Request>
      <Step>
        <Name>VAK-Header</Name>
      </Step>
      <Step>
        <Name>Q-Tokens-Comprobar</Name>
      </Step>
    </Request>
    <Response>
      <Step>
        <Name>EV-Tokens-Usados</Name>
      </Step>
      <Step>
        <Name>Q-Tokens-Cobrar</Name>
      </Step>
    </Response>
  </PreFlow>
  <HTTPProxyConnection>
    <BasePath>/v1/llm</BasePath>
  </HTTPProxyConnection>
  <RouteRule name="default">
    <TargetEndpoint>default</TargetEndpoint>
  </RouteRule>
</ProxyEndpoint>
```

Comprobación en la petición, sin contar:

```xml
<Quota name="Q-Tokens-Comprobar" type="rollingwindow">
  <SharedName>tokens-por-app</SharedName>
  <EnforceOnly>true</EnforceOnly>
  <Identifier ref="client_id"/>
  <Allow count="200000"/>
  <Interval>1</Interval>
  <TimeUnit>hour</TimeUnit>
  <Distributed>true</Distributed>
</Quota>
```

Extracción del consumo real. La ruta JSON depende del proveedor; esta corresponde a una respuesta tipo Gemini con `usageMetadata.totalTokenCount`:

```xml
<ExtractVariables name="EV-Tokens-Usados">
  <Source>response</Source>
  <VariablePrefix>llm</VariablePrefix>
  <JSONPayload>
    <Variable name="tokens" type="integer">
      <JSONPath>$.usageMetadata.totalTokenCount</JSONPath>
    </Variable>
  </JSONPayload>
</ExtractVariables>
```

Cobro en la respuesta, sin rechazar:

```xml
<Quota name="Q-Tokens-Cobrar" type="rollingwindow">
  <SharedName>tokens-por-app</SharedName>
  <CountOnly>true</CountOnly>
  <Identifier ref="client_id"/>
  <Allow count="200000"/>
  <Interval>1</Interval>
  <TimeUnit>hour</TimeUnit>
  <Distributed>true</Distributed>
  <MessageWeight ref="llm.tokens"/>
</Quota>
```

Las dos políticas deben tener el mismo `<SharedName>`, `<Identifier>`, `<Allow>`, `<Interval>`, `<TimeUnit>` y `type`, o estarán leyendo contadores distintos.

## Diferencias en Apigee Edge

| Aspecto | Apigee X / hybrid | Apigee Edge |
|---|---|---|
| Tipo de política | Extensible | No aplica (Edge no tiene la distinción Standard/Extensible) |
| `<SharedName>`, `<CountOnly>`, `<EnforceOnly>` | Sí | **No existen** |
| HTTP de `QuotaViolation` | 429 según la nota de la página (la tabla dice 500) | 500 por defecto; 429 con `features.isHTTPStatusTooManyRequestEnabled` |
| `second` con `Distributed=true` | No soportado | Error de despliegue `InvalidTimeUnitForDistributedQuota` |
| `quotaCounterScope` en API products | Documentado | No documentado en la página de la política |
| Resto de elementos, tipos y variables | Iguales | Iguales |

## Antipatrones

- Reusar la misma política Quota en varios flujos sin querer compartir el contador.
- Usar Quota para frenar picos (para eso está SpikeArrest).
- Dejar `<Distributed>` en `false` para un límite contractual.
- Poner cuota en el API product y no poner la política Quota en el proxy (el cupo no se aplica).
- Poner la Quota **antes** de la `VerifyAPIKey`/`OAuthV2` cuando depende del producto.
- Usar `<Class>` con un valor de clase controlado por el cliente sin normalizarlo.

## Fuentes

- Quota policy — Apigee X/hybrid: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/quota-policy> (consultada directamente, contenido completo, 2026-10-22).
- Quota policy — Apigee Edge: <https://docs.apigee.com/api-platform/reference/policies/quota-policy> (consultada directamente, 2026-10-22).
- Comparar Quota y SpikeArrest: <https://docs.cloud.google.com/apigee/docs/api-platform/develop/comparing-quota-spike-arrest-policies>
- Gestión de API products: <https://docs.cloud.google.com/apigee/docs/api-platform/publish/create-api-products>
