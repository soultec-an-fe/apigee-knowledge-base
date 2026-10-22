---
id: politica-reset-quota
titulo: ResetQuota — referencia completa
area: politicas
tags: [resetquota, quota, cuota, contador, trafico, extensible]
aplica_a: [apigee-x, apigee-hybrid, apigee-edge]
elemento_xml: ResetQuota
tipo_politica: extensible
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/reset-quota-policy
fuente_edge: https://docs.apigee.com/api-platform/reference/policies/reset-quota-policy
revisado: 2026-10-22
---

# ResetQuota — referencia completa

> [!NOTE]
> **Tipo:** Extensible (puede tener implicaciones de costo según la licencia). **Elemento raíz:** `<ResetQuota>`.
> **Aplica a:** Apigee X, hybrid y Edge, con el mismo comportamiento.

ResetQuota **devuelve cupo** a un contador de una política [Quota](quota.md) en mitad de su intervalo. No pone el contador a cero ni cambia el límite: resta una cantidad del consumo acumulado, de modo que el cliente puede hacer esa cantidad de peticiones adicionales antes de que el intervalo termine. Cuando el intervalo de la Quota se reinicia de forma natural, el ajuste se descarta.

Ejemplo de la idea: una Quota permite 1000 peticiones por semana; el martes la app ya consumió las 1000. Un ResetQuota con `<Allow>500</Allow>` resta 500 al contador y la app puede hacer 500 más esa semana. El lunes siguiente vuelve a tener 1000.

## Cuándo usarla (y cuándo no)

| Necesidad | Política correcta |
|---|---|
| Conceder cupo extra puntual (soporte, compensación por incidente, compra de un paquete adicional) | **ResetQuota** |
| Cambiar el límite de forma permanente | Cambiar el atributo del API product o la `<Allow>` de la Quota, no ResetQuota |
| Reiniciar el conteo cuando termina un periodo | Nada: Quota lo hace sola al acabar el `<Interval>` |
| Limitar ráfagas | [SpikeArrest](spike-arrest.md) |

ResetQuota suele vivir en un **proxy administrativo** separado (p. ej. `/admin/cuotas/{app}/recarga`), protegido con su propia autenticación, nunca en el mismo flujo que atiende al cliente: si el cliente pudiera dispararla, podría recargarse cupo a sí mismo.

## Sintaxis completa

```xml
<ResetQuota name="RQ-Nombre" continueOnError="false" enabled="true">
  <DisplayName>Nombre legible</DisplayName>
  <Quota name="NombreDeLaQuota" ref="variable.con.nombre.de.la.quota">
    <Identifier name="valorDelIdentificador" ref="variable.con.identificador">
      <Class ref="variable.con.clase">
        <Allow>200</Allow>
      </Class>
      <Allow ref="variable.con.cantidad">100</Allow>
    </Identifier>
  </Quota>
</ResetQuota>
```

## Atributos del elemento raíz

| Atributo | Obligatorio | Default | Qué hace |
|---|---|---|---|
| `name` | Sí | — | Nombre interno. Letras, números, espacios, guiones, guion bajo y punto; máximo 255 caracteres. |
| `continueOnError` | No | `false` | Con `true`, el flujo sigue aunque la política falle. |
| `enabled` | No | `true` | Con `false` la política no se ejecuta. |
| `async` | No | `false` | **Obsoleto.** No tiene efecto. |

## Elementos hijos

| Elemento | Obligatorio | Tipo | Resumen |
|---|---|---|---|
| `<DisplayName>` | No | String | Etiqueta legible en la UI. Si falta, se usa `name`. |
| `<Quota>` | **Sí** | — | Qué política Quota se ajusta. |
| `<Quota>/<Identifier>` | **Sí** | String | Qué contador de esa Quota se ajusta. |
| `<Quota>/<Identifier>/<Allow>` | **Sí** (en la práctica) | Integer | Cuánto se resta al contador. |
| `<Quota>/<Identifier>/<Class>` | No | — | Qué clase del contador se ajusta, si la Quota usa clases. |

### `<Quota>`

Identifica la política Quota objetivo por su atributo `name`. Admite dos atributos, ambos opcionales pero al menos uno necesario:

| Atributo | Qué hace |
|---|---|
| `name` | Nombre literal de la política Quota. |
| `ref` | Variable de flujo con el nombre de la política Quota. Si están los dos, **gana `ref`**; si `ref` no resuelve en runtime, se usa `name`. |

La Quota objetivo debe existir **en el mismo proxy**. Si no, la política falla con `InvalidRLPolicy`.

### `<Identifier>`

Elige el contador. Una Quota sin `<Identifier>` tiene un solo contador, que se llama `_default`. Una Quota con `<Identifier ref="client_id"/>` tiene un contador por cada `client_id`; para ajustar el de una app concreta, el ResetQuota debe pasar **el valor** de esa app.

| Atributo | Qué hace |
|---|---|
| `name` | Valor literal del identificador. Para una Quota sin `<Identifier>`, `_default`. |
| `ref` | Variable con el valor del identificador. Si están los dos, gana `ref`; si `ref` no resuelve, se usa `name`. |

> [!IMPORTANT]
> El identificador del ResetQuota tiene que coincidir **en valor** con el que la Quota calculó para ese cliente. Si la Quota cuenta por `verifyapikey.VAK.developer.cuenta_id`, el proxy administrativo debe obtener ese mismo valor (p. ej. leyéndolo de un parámetro de la petición administrativa), no la credencial del administrador que hace la llamada.

### `<Allow>`

Cantidad que se **resta** del consumo acumulado. Puede ser literal o venir de una variable con `ref`; si están los dos, gana la variable. Si se omite `<Allow>`, la política no modifica nada. Si el literal no es un entero, el despliegue falla con `InvalidCount`; si la variable no resuelve, el fallo es `FailedToResolveAllowCountRef` en runtime.

### `<Class>`

Solo aplica si la Quota objetivo usa clases (ver [Quota — `<Class>`](quota.md#class-y-allow-class)). `ref` apunta a la variable con el nombre de la clase, y dentro va el `<Allow>` de esa clase.

## Variables de flujo

La política no publica variables propias. Para ver el efecto, consulta las variables `ratelimit.{nombre-de-la-quota}.*` de la Quota en la siguiente petición (ver [Quota — Variables de flujo](quota.md#variables-de-flujo)).

## Errores

### En runtime

| Código de fallo | HTTP | Causa |
|---|---|---|
| `policies.resetquota.InvalidRLPolicy` | 500 | La Quota nombrada en `<Quota>` no existe en el proxy. |
| `policies.resetquota.FailedToResolveRLPolicy` | 500 | La variable de `<Quota ref>` no resolvió. |
| `policies.resetquota.FailedToResolveAllowCountRef` | No indicado por Google | La variable de `<Allow ref>` no resolvió. La tabla oficial deja el HTTP como "N/A". |

### Al desplegar

| Error | Causa |
|---|---|
| `InvalidCount` | El valor literal de `<Allow>` no es un entero. |

### Variables de fallo

Las comunes a toda política: `fault.name` (p. ej. `InvalidRLPolicy`) y `resetquota.{name}.failed`. Captura por `fault.name`, nunca por el texto del `faultstring`.

## Ejemplos

### 1. Recargar el contador global de una Quota

La Quota `QU-Global` no tiene `<Identifier>`, así que su único contador es `_default`. Se devuelven 100 peticiones.

```xml
<ResetQuota name="RQ-Global">
  <Quota name="QU-Global">
    <Identifier name="_default">
      <Allow>100</Allow>
    </Identifier>
  </Quota>
</ResetQuota>
```

### 2. Recarga por app desde un endpoint administrativo

La Quota cuenta por cuenta de cliente (`verifyapikey.VAK.developer.cuenta_id`). El proxy administrativo recibe `POST /admin/cuotas/{cuenta}/recarga?cantidad=500`; una `ExtractVariables` previa deja `admin.cuenta` y `admin.cantidad`. El endpoint debe estar protegido con una credencial de operador, no con la del cliente.

```xml
<ResetQuota name="RQ-Recarga-Cuenta">
  <Quota name="QU-Mensual">
    <Identifier ref="admin.cuenta">
      <Allow ref="admin.cantidad"/>
    </Identifier>
  </Quota>
</ResetQuota>
```

> [!WARNING]
> `QU-Mensual` debe estar definida **en este mismo proxy** (aunque no se ejecute en él). Los contadores de Quota se identifican por el nombre de la política y el identificador; la documentación oficial no describe cómo compartirlos entre proxies distintos, así que valídalo en tu organización antes de diseñar sobre esa suposición.

### 3. Recargar una clase concreta

La Quota usa clases `oro` y `plata`; se devuelven 200 peticiones solo a la clase indicada por la cabecera de la petición administrativa.

```xml
<ResetQuota name="RQ-Por-Clase">
  <Quota name="QU-Por-Plan">
    <Identifier name="_default">
      <Class ref="request.header.x-clase">
        <Allow>200</Allow>
      </Class>
    </Identifier>
  </Quota>
</ResetQuota>
```

## Diferencias en Apigee Edge

| Aspecto | Apigee X / hybrid | Apigee Edge |
|---|---|---|
| Elementos, atributos y errores | Iguales | Iguales |
| Tipo de política | Extensible | La documentación de Edge no usa la clasificación Standard/Extensible |

## Antipatrones

- Exponer ResetQuota en el flujo que usa el propio cliente, o tomar `<Allow>` de una cabecera que manda el cliente.
- Usarla para cambiar el límite de forma permanente: el ajuste se pierde en el siguiente intervalo.
- Pasar en `<Identifier>` un valor distinto del que calculó la Quota (el contador ajustado no será el del cliente).

## Fuentes

- ResetQuota policy — Apigee X/hybrid: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/reset-quota-policy> (consultada directamente, contenido completo, 2026-10-22).
- Reset Quota policy — Apigee Edge: <https://docs.apigee.com/api-platform/reference/policies/reset-quota-policy> (consultada directamente, 2026-10-22).
