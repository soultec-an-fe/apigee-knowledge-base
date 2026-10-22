---
id: politica-spike-arrest
titulo: SpikeArrest — referencia completa
area: politicas
tags: [spikearrest, rate-limiting, picos, trafico, 429, useeffectivecount, standard]
aplica_a: [apigee-x, apigee-hybrid, apigee-edge]
elemento_xml: SpikeArrest
tipo_politica: standard
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/spike-arrest-policy
fuente_edge: https://docs.apigee.com/api-platform/reference/policies/spike-arrest-policy
revisado: 2026-10-22
---

# SpikeArrest — referencia completa

> [!NOTE]
> **Tipo:** Standard (funciona en cualquier tipo de entorno). **Elemento raíz:** `<SpikeArrest>`.
> **Aplica a:** Apigee X, hybrid y Edge (con diferencias de comportamiento, ver [Diferencias en Apigee Edge](#diferencias-en-apigee-edge)).

SpikeArrest frena **ráfagas** de tráfico antes de que lleguen al backend. Es una protección operativa, no un contrato comercial: limita cuántas peticiones por segundo o por minuto deja pasar el proxy, y responde `429` a las que exceden la tasa.

## Cuándo usarla (y cuándo no)

| Necesidad | Política correcta |
|---|---|
| Proteger el backend de picos o ataques de volumen | **SpikeArrest** |
| Aplicar el límite contratado a una app (por hora, día, semana, mes) | [Quota](../01-traffic-management.md#quota) |
| Límite por app/desarrollador sin contrato, solo para repartir capacidad | SpikeArrest con `<Identifier>` |
| Límite de tokens de un LLM | `LLMTokenQuota` / `PromptTokenLimit` ([políticas de IA](../05-politicas-ai.md)) |

Regla práctica: SpikeArrest va **primero** en el PreFlow del ProxyEndpoint, antes de cualquier política costosa (verificación de credenciales, callouts), para que el tráfico rechazado consuma lo mínimo.

## Sintaxis completa

```xml
<SpikeArrest name="SA-Nombre" continueOnError="false" enabled="true">
  <DisplayName>Nombre legible</DisplayName>
  <Properties/>
  <Identifier ref="variable.que.identifica.al.cliente"/>
  <MessageWeight ref="variable.con.peso.entero"/>
  <Rate ref="variable.con.tasa">100ps</Rate>
  <UseEffectiveCount>true</UseEffectiveCount>
</SpikeArrest>
```

## Atributos del elemento raíz

Son los atributos comunes a todas las políticas.

| Atributo | Obligatorio | Default | Qué hace |
|---|---|---|---|
| `name` | Sí | — | Nombre interno de la política. Letras, números, espacios, guiones, guion bajo y punto; máximo 255 caracteres. Es el que aparece en `<Step><Name>` y en las variables `ratelimit.{name}.*`. |
| `continueOnError` | No | `false` | Con `true`, el flujo sigue aunque la política falle. Con SpikeArrest casi nunca se quiere: el `429` es justamente el resultado deseado. |
| `enabled` | No | `true` | Con `false` la política no se ejecuta aunque esté adjunta a un flujo. |
| `async` | No | `false` | **Obsoleto.** No tiene efecto; no lo uses. |

## Elementos hijos

| Elemento | Obligatorio | Tipo | Default | Resumen |
|---|---|---|---|---|
| `<DisplayName>` | No | String | valor de `name` | Etiqueta legible en el editor de la UI. |
| `<Properties>` | No | — | — | Contenedor genérico; SpikeArrest no define propiedades propias. |
| `<Identifier ref>` | No | String | — | Agrupa el conteo por cliente. Sin él, **un único contador para todo el proxy**. |
| `<MessageWeight ref>` | No | Integer | 1 | Cuánto "pesa" cada petición en el conteo. |
| `<Rate>` | **Sí** | `Nps` / `Npm` | — | Tasa permitida, estática o tomada de una variable. |
| `<UseEffectiveCount>` | No | Boolean | `false` | Elige el algoritmo. **En Apigee X/hybrid ponlo en `true`.** |

### `<Identifier>`

Define la clave por la que se agrupan las peticiones: cada valor distinto de la variable tiene su propio contador. El atributo `ref` (obligatorio dentro del elemento) apunta a cualquier variable de flujo: `client_id` o `developer.id` tras `VerifyAPIKey`/`OAuthV2`, una cabecera, o una variable propia fijada con `AssignMessage` o `JavaScript`.

Si el elemento se omite, el límite es global para el proxy: un único cliente ruidoso puede consumir toda la capacidad y provocar `429` al resto.

### `<MessageWeight>`

Hace que algunas peticiones cuenten más que otras. `ref` apunta a una variable cuyo valor debe ser un **entero**. Ejemplo: con `<Rate>10pm</Rate>` y peso `2`, ese cliente solo consigue 5 peticiones por minuto. Útil para que operaciones caras (búsquedas, exportaciones) consuman más cupo que las baratas.

Si la variable resuelve a algo que no es entero, la política falla con `InvalidMessageWeight` (`500`).

### `<Rate>`

Formato del valor: un entero positivo distinto de cero seguido de `ps` (por segundo) o `pm` (por minuto). Ejemplos válidos: `50ps`, `600pm`. No hay otras unidades.

Se puede dar de dos formas, combinables:

| Forma | Ejemplo | Comportamiento |
|---|---|---|
| Valor estático | `<Rate>20ps</Rate>` | Tasa fija. |
| Variable | `<Rate ref="verifyapikey.VAK.apiproduct.spike_rate"/>` | Tasa tomada en runtime, p. ej. de un atributo personalizado del API product. |
| Ambas | `<Rate ref="request.header.x-rate">5ps</Rate>` | Si la variable tiene valor, **gana la variable**; si no está definida, se usa el valor del cuerpo. |

Si se usa solo `ref`, sin valor en el cuerpo, y la variable no existe en esa petición, la política falla con `FailedToResolveSpikeArrestRate` (`500`).

> [!WARNING]
> No dejes que el **cliente** fije su propia tasa con una cabecera en producción: es un control de seguridad que el llamante podría relajar. Toma la tasa de una fuente que el cliente no controla (atributo del API product, KVM, PropertySet).

Consulta el máximo permitido en [Límites](../../10-referencia/01-limites.md).

### `<UseEffectiveCount>`: el algoritmo

Este elemento cambia el **comportamiento**, no solo un ajuste fino.

| Valor | Algoritmo | Conteo | Efecto en ráfagas |
|---|---|---|---|
| `true` | Ventana deslizante | **Distribuido**: sincronizado entre los message processors de una región | Una ráfaga corta pasa mientras no supere la tasa total de la ventana. Comportamiento predecible. |
| `false` (default) | Token bucket con **suavizado** | Local a cada message processor | La tasa se divide en intervalos: `30pm` → 1 petición cada 2 s; `10ps` → 1 cada 100 ms. Una segunda petición dentro del mismo intervalo se rechaza aunque no se haya llegado al total. |

> [!IMPORTANT]
> Google indica que el suavizado (`false`) **no está soportado** en organizaciones de Apigee ni en organizaciones hybrid con cargas de producción, aunque `false` siga siendo el valor por defecto. En X/hybrid declara siempre `<UseEffectiveCount>true</UseEffectiveCount>`.

Detalle interno: Apigee calcula por message processor tres valores (`messagesPerPeriod`, `periodInMicroseconds` y `maxBurstMessageCount`) que dependen del número de MPs y de este elemento. Con `10ps`, 10 MPs y `true`, cada MP aplica en la práctica 1 ps. No se configuran a mano; sirven para interpretar el comportamiento en Debug.

## Variables de flujo

Se pueblan al ejecutarse la política. `{name}` es el atributo `name` de la política.

| Variable | Tipo | Acceso | Contenido |
|---|---|---|---|
| `ratelimit.{name}.available.count` | Long | Lectura | Cupo restante en el intervalo actual. |
| `ratelimit.{name}.exceed.count` | Long | Lectura | `1` si se superó el límite en la ventana actual. |
| `ratelimit.{name}.failed` | Boolean | Lectura | `true` solo si la política tuvo un **fallo interno**. |

> [!WARNING]
> Para saber si se aplicó el límite usa `ratelimit.{name}.exceed.count > 0` o `ratelimit.{name}.available.count < 1`. **No** uses `.failed`: SpikeArrest está diseñado para fallar abierto (*fail-open*), y bajo carga alta esa variable puede quedar en `true` sin que haya habido rechazo.

## Errores

### En runtime

| Código de fallo | HTTP | Causa |
|---|---|---|
| `policies.ratelimit.SpikeArrestViolation` | 429 | Se superó la tasa. Es el caso normal de rechazo. |
| `policies.ratelimit.FailedToResolveSpikeArrestRate` | 500 | `<Rate ref>` no resolvió a ningún valor y no hay valor estático de respaldo. |
| `policies.ratelimit.InvalidMessageWeight` | 500 | La variable de `<MessageWeight>` no contiene un entero. |

### Al desplegar

| Error | Causa |
|---|---|
| `InvalidAllowedRate` | El valor de `<Rate>` no es un entero o no termina en `ps`/`pm`. El despliegue del proxy falla. |

### Variables de fallo

| Variable | Ejemplo de uso |
|---|---|
| `fault.name` | `fault.name = "SpikeArrestViolation"` (es la última parte del código de fallo) |
| `ratelimit.{name}.failed` | `ratelimit.SA-Global.failed = true` |

La respuesta de error por defecto es un JSON con `fault.faultstring` (texto, puede cambiar) y `fault.detail.errorcode` (estable). **Captura siempre por `errorcode` o `fault.name`, nunca por el texto.**

## Ejemplos

### 1. Escudo global del backend

Protección básica para un proxy entero: 200 peticiones por segundo, distribuidas en la región.

```xml
<SpikeArrest name="SA-Escudo-Global">
  <Rate>200ps</Rate>
  <UseEffectiveCount>true</UseEffectiveCount>
</SpikeArrest>
```

### 2. Cupo por aplicación con tasa definida en el API product

Cada app (identificada por `client_id` tras `VerifyAPIKey`) tiene su propio contador, y la tasa sale de un atributo personalizado `spike_rate` del API product (p. ej. `30ps`). Si el producto no define el atributo, se aplica `10ps`.

```xml
<SpikeArrest name="SA-Por-App">
  <Identifier ref="client_id"/>
  <Rate ref="verifyapikey.VAK-Header.apiproduct.spike_rate">10ps</Rate>
  <UseEffectiveCount>true</UseEffectiveCount>
</SpikeArrest>
```

### 3. Operaciones caras pesan más

Una variable `costo.operacion` vale `5` para `/reportes` y `1` para lo demás, fijada antes con `AssignMessage`. Con `100pm`, un cliente puede hacer 100 llamadas baratas o 20 de reportes por minuto.

```xml
<SpikeArrest name="SA-Ponderado">
  <Identifier ref="client_id"/>
  <MessageWeight ref="costo.operacion"/>
  <Rate>100pm</Rate>
  <UseEffectiveCount>true</UseEffectiveCount>
</SpikeArrest>
```

### 4. Respuesta 429 corporativa con FaultRule

En el ProxyEndpoint, sustituye el JSON por defecto por el formato de error de la casa y añade `Retry-After`.

```xml
<FaultRules>
  <FaultRule name="fr-limite-de-tasa">
    <Condition>fault.name = "SpikeArrestViolation"</Condition>
    <Step>
      <Name>AM-Error-429</Name>
    </Step>
  </FaultRule>
</FaultRules>
```

```xml
<AssignMessage name="AM-Error-429">
  <Set>
    <StatusCode>429</StatusCode>
    <Headers>
      <Header name="Retry-After">1</Header>
    </Headers>
    <Payload contentType="application/json">{"codigo":"LIMITE_EXCEDIDO","mensaje":"Demasiadas solicitudes, reintente en un segundo."}</Payload>
  </Set>
  <IgnoreUnresolvedVariables>true</IgnoreUnresolvedVariables>
  <AssignTo createNew="false" transport="http" type="response"/>
</AssignMessage>
```

## Diferencias en Apigee Edge

| Aspecto | Apigee X / hybrid | Apigee Edge |
|---|---|---|
| `<UseEffectiveCount>` | Debe ir en `true`; el suavizado no está soportado | Disponible en Edge Public Cloud y en Private Cloud **4.18.05 o superior**. La plantilla de la UI lo incluye en `true`, pero si se omite vale `false`. |
| Conteo con `false` | — | **No distribuido**: cada message processor cuenta por su cuenta. Con N MPs en round-robin, la tasa real efectiva es aproximadamente N veces la configurada (Edge Cloud usa 2 MPs por defecto). |
| Códigos de error y variables | Iguales | Iguales |

## Antipatrones

- Usar SpikeArrest como cuota comercial (para eso está `Quota`).
- Omitir `<Identifier>` en APIs multi-cliente: un solo cliente agota el cupo de todos.
- Dejar `<UseEffectiveCount>` sin declarar en X/hybrid.
- Detectar el rechazo con `ratelimit.{name}.failed`.
- Leer la tasa de una cabecera que manda el cliente.

Ver también el [catálogo de antipatrones](../../09-antipatrones/01-catalogo-antipatrones.md).

## Fuentes

- SpikeArrest policy — Apigee X/hybrid: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/spike-arrest-policy> (consultada directamente, contenido completo, 2026-10-22).
- Spike Arrest policy — Apigee Edge: <https://docs.apigee.com/api-platform/reference/policies/spike-arrest-policy> (consultada directamente, 2026-10-22).
- Comparar Quota y SpikeArrest: <https://docs.cloud.google.com/apigee/docs/api-platform/develop/comparing-quota-spike-arrest-policies>
