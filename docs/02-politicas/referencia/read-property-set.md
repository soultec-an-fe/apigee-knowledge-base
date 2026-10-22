---
id: politica-read-property-set
titulo: ReadPropertySet — referencia completa
area: politicas
tags: [readpropertyset, propertyset, configuracion, variables, standard]
aplica_a: [apigee-x, apigee-hybrid]
elemento_xml: ReadPropertySet
tipo_politica: standard
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/read-property-set-policy
revisado: 2026-10-22
---

# ReadPropertySet — referencia completa

> [!NOTE]
> **Tipo:** Standard. **Elemento raíz:** `<ReadPropertySet>`.
> **Aplica a:** Apigee X y hybrid. **No existe en Apigee Edge** (Edge no tiene PropertySets).

Un **PropertySet** es un archivo `.properties` (pares `clave=valor`) asociado a un proxy o a un entorno, cuyas claves están disponibles como variables `propertyset.{set}.{clave}`. Para leer una clave **fija** basta con referenciar esa variable directamente (`{propertyset.config.timeout}`). ReadPropertySet sirve cuando el **set o la clave se deciden en runtime**: los calcula a partir de variables, permite un valor por defecto y deja el resultado en la variable que elijas.

Para secretos, usa un KVM cifrado ([KeyValueMapOperations](key-value-map-operations.md)), no un PropertySet. Alternativa equivalente: `<AssignVariable>/<PropertySetRef>` de [AssignMessage](assign-message.md#assignvariable).

## Sintaxis completa

```xml
<ReadPropertySet name="RPS-Nombre" continueOnError="false" enabled="true">
  <Read>
    <Name ref="flujo.nombre_set">config</Name>
    <Key ref="flujo.clave">timeout_ms</Key>
    <AssignTo>flujo.timeout</AssignTo>
    <DefaultValue>5000</DefaultValue>
  </Read>
  <IgnoreUnresolvedVariables>false</IgnoreUnresolvedVariables>
</ReadPropertySet>
```

Puede haber varios `<Read>`.

## Atributos del elemento raíz

| Atributo | Obligatorio | Default | Qué hace |
|---|---|---|---|
| `name` | Sí | — | Nombre interno; da nombre a `readpropertyset.{name}.failed`. |
| `continueOnError` | No | `false` | Con `true`, el flujo sigue aunque falle. |
| `enabled` | No | `true` | Con `false` no se ejecuta. |

## Elementos hijos

| Elemento | Obligatorio | Resumen |
|---|---|---|
| `<Read>` | **Sí** (al menos uno) | Una lectura. Sin ninguno → `EmptyReads` al desplegar. |
| `<Read>/<Name ref>` | **Sí** | Nombre del PropertySet: se intenta primero `ref`, luego el literal. |
| `<Read>/<Key ref>` | **Sí** | Clave dentro del set: primero `ref`, luego el literal. |
| `<Read>/<AssignTo>` | **Sí** | Variable de destino. |
| `<Read>/<DefaultValue>` | No | Valor si no se puede resolver. |
| `<IgnoreUnresolvedVariables>` | No | Con `true`, continúa si no se resuelve. **No aplica** si hay `<DefaultValue>`. |

La variable resuelta es `propertyset.{valor_de_Name}.{valor_de_Key}`. Si falta el nombre o la clave (ni `ref` ni literal), o `<AssignTo>`, el despliegue falla con `FieldUnset`.

> [!NOTE]
> El primer ejemplo de la página usa `ref="set-ref"` con literal `environment.name`; el segundo, al revés (`ref="environment.name"` con literal). El sentido correcto es el del segundo: `ref` apunta a la **variable** cuyo valor es el nombre; el literal es el nombre fijo de respaldo.

## Variables de flujo

Las de `<AssignTo>`.

## Errores

### En runtime

| Código | HTTP | Causa |
|---|---|---|
| `steps.readpropertyset.UnresolvedVariable` | 500 | Una variable no existe o está fuera de alcance, con `<IgnoreUnresolvedVariables>false` y sin `<DefaultValue>`. |

### Al desplegar

| Error | Causa |
|---|---|
| `steps.readpropertyset.EmptyReads` | No hay `<Read>`. |
| `steps.readpropertyset.FieldUnset` | Falta `<Name>`, `<Key>` o `<AssignTo>`. |

### Variables de fallo

`fault.name` y `readpropertyset.{name}.failed`.

## Ejemplo: URL del backend por versión de API

`backends.properties` (en el entorno):

```text
v1=https://backend-v1.interno.ejemplo.com
v2=https://backend-v2.interno.ejemplo.com
```

```xml
<ReadPropertySet name="RPS-Backend-Por-Version">
  <Read>
    <Name>backends</Name>
    <Key ref="flujo.version_api">v1</Key>
    <AssignTo>flujo.url_backend</AssignTo>
    <DefaultValue>https://backend-v1.interno.ejemplo.com</DefaultValue>
  </Read>
</ReadPropertySet>
```

Después, en el TargetEndpoint, una AssignMessage asigna `target.url` a partir de `flujo.url_backend`. Una versión desconocida cae en el valor por defecto en lugar de construir una URL con datos del cliente.

## Diferencias en Apigee Edge

No existen PropertySets ni esta política en Edge; el equivalente habitual es un KVM.

## Antipatrones

- Guardar secretos en PropertySets.
- Usarla para leer una clave fija (basta con `{propertyset.set.clave}`).

## Fuentes

- ReadPropertySet policy — Apigee X/hybrid: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/read-property-set-policy> (consultada directamente, contenido completo, 2026-10-22).
