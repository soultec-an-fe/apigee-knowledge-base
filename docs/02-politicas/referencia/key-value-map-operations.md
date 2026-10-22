---
id: politica-key-value-map-operations
titulo: KeyValueMapOperations — referencia completa
area: politicas
tags: [keyvaluemapoperations, kvm, secretos, configuracion, cache, private, extensible]
aplica_a: [apigee-x, apigee-hybrid, apigee-edge]
elemento_xml: KeyValueMapOperations
tipo_politica: extensible
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/key-value-map-operations-policy
fuente_edge: https://docs.apigee.com/api-platform/reference/policies/key-value-map-operations-policy
revisado: 2026-10-22
---

# KeyValueMapOperations — referencia completa

> [!NOTE]
> **Tipo:** Extensible. **Elemento raíz:** `<KeyValueMapOperations>`.
> **Aplica a:** Apigee X, hybrid y Edge, con diferencias en cifrado y en `<MapName>` (ver [Diferencias en Apigee Edge](#diferencias-en-apigee-edge)).

KeyValueMapOperations **lee (`Get`), escribe (`Put`) y borra (`Delete`)** entradas de un **KVM** (*key value map*): un almacén persistente de pares clave-valor con alcance de organización, entorno, proxy o revisión. Es el sitio para **secretos** (credenciales de backend, claves de firma) y configuración que cambia sin redesplegar.

| Necesidad | Mecanismo |
|---|---|
| Secretos (contraseñas, claves privadas, tokens) | **KVM** (cifrado) + variables `private.` |
| Configuración no secreta y estable por proxy o entorno | PropertySet ([ReadPropertySet](read-property-set.md)) |
| Datos efímeros con TTL (tokens de backend, resultados) | Caché ([PopulateCache](populate-cache.md)) |
| Contadores | [Quota](quota.md) |

## Cifrado y Debug

En **Apigee X y hybrid ≥ 1.4, todos los KVM se cifran** siempre. Al leer con `<Get>`, el valor se descifra y se asigna a la variable de `assignTo`.

> [!IMPORTANT]
> Para que el valor descifrado **no aparezca en claro en las sesiones de Debug**, la variable de destino debe empezar por **`private.`** (`assignTo="private.backend.password"`). En X, si no usas el prefijo, la política funciona igual pero **muestra el secreto en Debug**, sin error. Usa `private.` en todo `<Get>` de datos sensibles.

## Sintaxis completa

```xml
<KeyValueMapOperations name="KVM-Nombre" mapIdentifier="credenciales-backend" continueOnError="false" enabled="true">
  <DisplayName>Nombre legible</DisplayName>
  <Scope>environment</Scope>
  <ExpiryTimeInSecs>300</ExpiryTimeInSecs>
  <InitialEntries>
    <Entry>
      <Key><Parameter>timeout_ms</Parameter></Key>
      <Value>5000</Value>
    </Entry>
  </InitialEntries>
  <Get assignTo="private.backend.password" index="1">
    <Key>
      <Parameter>password</Parameter>
    </Key>
  </Get>
  <Put override="true">
    <Key>
      <Parameter>ultima_rotacion</Parameter>
    </Key>
    <Value ref="system.timestamp"/>
  </Put>
  <Delete>
    <Key>
      <Parameter>clave_obsoleta</Parameter>
    </Key>
  </Delete>
</KeyValueMapOperations>
```

Debe haber al menos un `<Get>`, `<Put>` o `<Delete>`. Se ejecutan **en orden**.

## Atributos del elemento raíz

| Atributo | Obligatorio | Default | Qué hace |
|---|---|---|---|
| `name` | Sí | — | Nombre interno. |
| `mapIdentifier` | No | `kvmap` | Nombre del KVM. Si faltan este atributo y `<MapName>`, se usa un KVM llamado `kvmap`. No se puede combinar con `<MapName>`. Vacío → `UnsupportedOperationException` en runtime. |
| `continueOnError` | No | `false` | Con `true`, el flujo sigue aunque falle. |
| `enabled` | No | `true` | Con `false` no se ejecuta. |
| `async` | No | `false` | **Obsoleto.** |

## Elementos hijos

| Elemento | Resumen |
|---|---|
| `<Scope>` | Alcance del KVM: `organization`, `environment` (**default**), `apiproxy`, `policy` (revisión del proxy). **Hay que usar el mismo alcance con el que se creó** al leer, escribir o borrar. |
| `<MapName ref>` (X/hybrid) | Nombre del KVM elegido en runtime (literal, variable o variable con literal de respaldo). Incompatible con `mapIdentifier` y con `<InitialEntries>`. Si el KVM no existe, error en runtime (no se crea). |
| `<ExpiryTimeInSecs>` | TTL de la **caché local** de la política. Default 300 s (también con `0` o `-1`). |
| `<Get assignTo index>` | Lee una clave. Sin `index`, asigna **todos** los valores como `java.util.List`; `index` empieza en 1 (`0` o negativo → `InvalidIndex`). |
| `<Put override>` | Escribe una clave. `override="true"` (default) sobrescribe; `false` solo escribe si la clave no existe. Con `mapIdentifier`, crea el KVM si no existe. |
| `<Delete>` | Borra una clave. |
| `<InitialEntries>/<Entry>` | Valores semilla que se escriben **al desplegar**; si difieren de los del KVM, **los sobrescriben**. Solo literales. No permitido con `<MapName>`. |
| `<Key>/<Parameter ref>` | La clave: uno o varios `<Parameter>` (literal o `ref`) unidos con `__` (`targeturl__abc1__weight`). Máximo **2 KB**. El nombre `ratelimit` está reservado. |
| `<Value ref>` | El valor (literal o `ref`); varios `<Value>` forman un valor múltiple (`v1,v2`). |
| `<ExclusiveCache>` | **Obsoleto**; usa `<Scope>`. |

> [!WARNING]
> Con `<InitialEntries>`, cada despliegue **restablece** esas claves a los valores del XML. No pongas ahí valores que se cambian luego por API o UI (los perderías en el siguiente despliegue) ni, por supuesto, secretos: el XML vive en el repositorio.

### Caché: lo que `<ExpiryTimeInSecs>` hace y lo que no

Los `Get` **siempre leen de una caché en memoria** de cada nodo de runtime, que se rellena desde el KVM la primera vez y vive `<ExpiryTimeInSecs>`.

| Acción | Efecto en la caché |
|---|---|
| `Get` | Carga la clave en la caché local del nodo; las siguientes lecturas salen de ahí hasta que vence. |
| `Put` de la misma clave | Refresca la caché **solo en el nodo que ejecutó el `Put`**, con el TTL del `Put`. Los demás nodos siguen con el valor viejo hasta que les venza. |
| Cambio por **UI o API** | **No** resetea la caché. |
| Invalidar en todos los nodos | **No existe** mecanismo: hay que esperar a que venza en cada nodo. |

> [!CAUTION]
> No intentes "caducar" un valor haciendo un `Put` con un `<ExpiryTimeInSecs>` corto: el KVM **no tiene TTL en el servidor**; el valor queda escrito para siempre y sobrescribe el anterior. `<ExpiryTimeInSecs>` solo afecta a la caché local.

Para rotar un secreto sin cortes, escribe el nuevo valor en una clave nueva, despliega la lectura de la clave nueva, y borra la antigua cuando hayan vencido las cachés.

### Claves dinámicas

Con `<Parameter ref>`, la clave se calcula en runtime. Si la variable es **nula** en un `Put`, se escribe siempre en la misma clave "vacía" y puedes sobrescribir datos sin darte cuenta: valida la variable antes.

## Variables de flujo

Las que asignes con `assignTo`.

## Errores

### En runtime

| Código | HTTP | Causa |
|---|---|---|
| `steps.keyvaluemapoperations.UnsupportedOperationException` | 500 | `mapIdentifier` vacío. |

### Al desplegar

| Error | Causa |
|---|---|
| `InvalidIndex` | `index` de `<Get>` cero o negativo. |
| `KeyIsMissing` | Falta `<Key>` o `<Parameter>` en una `<Entry>` de `<InitialEntries>`. |
| `ValueIsMissing` | Falta `<Value>` en una `<Entry>`. |

## Ejemplos

### 1. Credenciales del backend

```xml
<KeyValueMapOperations name="KVM-Credenciales" mapIdentifier="credenciales-backend">
  <Scope>environment</Scope>
  <ExpiryTimeInSecs>600</ExpiryTimeInSecs>
  <Get assignTo="private.backend.usuario" index="1">
    <Key><Parameter>usuario</Parameter></Key>
  </Get>
  <Get assignTo="private.backend.password" index="1">
    <Key><Parameter>password</Parameter></Key>
  </Get>
</KeyValueMapOperations>
```

Seguida de [BasicAuthentication](basic-authentication.md) en modo `Encode`. Para reutilizarla en varios proxies, ponla en un **shared flow**, como recomienda Google.

### 2. Configuración por cliente con clave compuesta

```xml
<KeyValueMapOperations name="KVM-Config-Cliente" mapIdentifier="config-clientes">
  <Scope>environment</Scope>
  <Get assignTo="flujo.limite_diario" index="1">
    <Key>
      <Parameter ref="client_id"/>
      <Parameter>limite_diario</Parameter>
    </Key>
  </Get>
</KeyValueMapOperations>
```

Lee la clave `{client_id}__limite_diario`.

### 3. KVM elegido por entorno o tenant (X/hybrid)

```xml
<KeyValueMapOperations name="KVM-Por-Tenant">
  <MapName ref="flujo.kvm_tenant">config-por-defecto</MapName>
  <Scope>environment</Scope>
  <Get assignTo="private.tenant.api_key" index="1">
    <Key><Parameter>api_key</Parameter></Key>
  </Get>
</KeyValueMapOperations>
```

`flujo.kvm_tenant` debe salir de una lista cerrada (no de la petición) y el KVM debe existir: con `<MapName>` no se crea.

## Gestión fuera de la política

- **UI:** solo KVM de alcance **entorno** (Apigee > Management > Environments > Key value maps).
- **API de gestión:** KVM de organización, entorno y proxy; carga masiva y scripts. Hay que **crear el KVM por API** antes de leerlo con la política (salvo el `Put` con `mapIdentifier`, que lo crea).

## Diferencias en Apigee Edge

| Aspecto | Apigee X / hybrid | Apigee Edge |
|---|---|---|
| Cifrado | Siempre (hybrid ≥ 1.4) | Opcional: KVM cifrados y no cifrados |
| `private.` en `assignTo` | Recomendado; sin él el secreto se ve en Debug | **Obligatorio** con KVM cifrados: si falta, la política falla |
| `<MapName>` | Sí | No |
| Tamaño | Clave ≤ 2 KB | Clave ≤ 2 KB (Public Cloud); en Private Cloud, el KVM entero ≤ 15 MB |

## Antipatrones

- `Get` de secretos sin `private.`.
- Secretos en `<InitialEntries>` (quedan en el repositorio).
- Usar el KVM como caché con TTL o como contador.
- Esperar que un cambio por API se vea al instante en todos los nodos.
- `<Scope>` distinto al de creación.

## Fuentes

- KeyValueMapOperations policy — Apigee X/hybrid: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/key-value-map-operations-policy> (consultada directamente, contenido completo, 2026-10-22).
- Key Value Map Operations policy — Apigee Edge: <https://docs.apigee.com/api-platform/reference/policies/key-value-map-operations-policy> (consultada directamente, 2026-10-22).
