---
id: politica-access-entity
titulo: AccessEntity — referencia completa
area: politicas
tags: [accessentity, app, api-product, developer, appgroup, perfil, extensible]
aplica_a: [apigee-x, apigee-hybrid, apigee-edge]
elemento_xml: AccessEntity
tipo_politica: extensible
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/access-entity-policy
fuente_edge: https://docs.apigee.com/api-platform/reference/policies/access-entity-policy
revisado: 2026-10-22
---

# AccessEntity — referencia completa

> [!NOTE]
> **Tipo:** Extensible. **Elemento raíz:** `<AccessEntity>`.
> **Aplica a:** Apigee X, hybrid y Edge. En Edge, las *companies* ocupan el lugar de los AppGroups.

AccessEntity **consulta en tiempo de ejecución** el perfil completo de una entidad del almacén de Apigee (app, API product, credencial, desarrollador, AppGroup, código de autorización…) y lo deja como **XML** en la variable `AccessEntity.{name}`. Luego se extraen los campos con [ExtractVariables](../03-mediacion.md) (XPath) o JavaScript.

Cuándo tiene sentido: necesitas un dato que **no** publican ya `VerifyAPIKey` u `OAuthV2/VerifyAccessToken`. Esas dos políticas ya exponen los atributos de la app, del desarrollador y del producto (ver [VerifyAPIKey — Variables de flujo](verify-api-key.md#variables-de-flujo)); si te basta con eso, no añadas un AccessEntity.

> [!NOTE]
> Apigee cachea las entidades al menos **180 s** desde su último acceso: un cambio en un atributo de la app puede tardar ese tiempo en verse.

## Sintaxis completa

```xml
<AccessEntity name="AE-Nombre" continueOnError="false" enabled="true">
  <DisplayName>Nombre legible</DisplayName>
  <EntityType value="apiproduct"/>
  <EntityIdentifier ref="developer.app.name" type="appname"/>
  <SecondaryIdentifier ref="developer.email" type="developeremail"/>
  <OutputFormat>XML</OutputFormat>
</AccessEntity>
```

Varias entidades del mismo tipo:

```xml
<AccessEntity name="AE-Varias">
  <EntityType value="developer"/>
  <Identifiers>
    <Identifier>
      <EntityIdentifier ref="flujo.email_1" type="developeremail"/>
    </Identifier>
    <Identifier>
      <EntityIdentifier ref="flujo.email_2" type="developeremail"/>
    </Identifier>
  </Identifiers>
</AccessEntity>
```

## Atributos del elemento raíz

| Atributo | Obligatorio | Default | Qué hace |
|---|---|---|---|
| `name` | Sí | — | Nombre interno; la salida queda en `AccessEntity.{name}`. |
| `continueOnError` | No | `false` | Con `true`, el flujo sigue aunque falle. |
| `enabled` | No | `true` | Con `false` no se ejecuta. |
| `async` | No | `false` | **Obsoleto.** |

## Elementos hijos

| Elemento | Obligatorio | Resumen |
|---|---|---|
| `<EntityType value>` | **Sí** | Tipo de entidad. Un tipo inválido hace fallar el despliegue (`InvalidEntityType`). |
| `<EntityIdentifier ref type>` | **Sí** | Qué entidad: `ref` es la variable con el valor y `type` qué clase de identificador es. |
| `<SecondaryIdentifier ref type>` | No | Afina la búsqueda cuando el primario no basta. Solo **uno**. |
| `<Identifiers>/<Identifier>` | No | Agrupa varios pares primario/secundario para varias entidades. |
| `<OutputFormat>` | No | `XML` (default) o `JSON`. **Solo hybrid ≥ 1.4** según la página. |

### Tipos e identificadores soportados

| `EntityType` | `EntityIdentifier type` | `SecondaryIdentifier type` |
|---|---|---|
| `apiproduct` | `appid` | `apiresource` |
| | `apiproductname` | — |
| | `appname` | `apiresource`, `developeremail`, `developerid`, `appgroupname` |
| | `consumerkey` | `apiresource` |
| `app` | `appid` | — |
| | `appname` | `developeremail`, `developerid`, `appgroupname` |
| | `consumerkey` | — |
| `authorizationcode` | `authorizationcode` | — |
| `appgroupname` (ver nota) | `appid`, `appgroupname`, `consumerkey` | — |
| `consumerkey` | `consumerkey` | — |
| `consumerkey_scope` | `consumerkey` | — |
| `developer` | `appid`, `consumerkey`, `developeremail`, `developerid` | — |
| `requesttoken` | `requesttoken` | `consumerkey` |
| `verifier` | `verifier` | — |

> [!NOTE]
> La fila de AppGroup de la tabla oficial de X está mal formada: muestra `appgroupname` como tipo de entidad, con los identificadores `appid`, `appgroupname` y `consumerkey`. En Edge, la fila equivalente es `company` con `appid`, `company` y `consumerkey`. Antes de usarla, comprueba en Debug qué valor de `EntityType` acepta tu organización.

### Resultados múltiples

Si el par de identificadores coincide con varias entidades (p. ej. un API product buscado por `appname`, cuando la app tiene varios productos), se devuelve **la primera** coincidencia. Usa `<SecondaryIdentifier>` para desambiguar.

## Variables de flujo

| Variable | Contenido |
|---|---|
| `AccessEntity.{name}` | El perfil de la entidad, en XML (o JSON con `<OutputFormat>JSON</OutputFormat>` en hybrid). |

La estructura del XML es la misma que devuelve la API de gestión con `Accept: text/xml`. Raíces habituales: `/App`, `/ApiProduct`, `/Credential`, `/Developer`. XPath de ejemplo:

| Dato | XPath |
|---|---|
| Email del desarrollador | `/Developer/Email/text()` |
| Atributo del desarrollador | `/Developer/Attributes/Attribute[Name='segmento']/Value/text()` |
| Estado de un producto en la credencial | `/Credential/ApiProducts/ApiProduct[Name='pagos']/Status/text()` |
| Callback URL de la app | `/App/CallbackUrl/text()` |

> [!CAUTION]
> Los perfiles de **app** y de **credencial** incluyen el **`ConsumerSecret`** en claro. No devuelvas `AccessEntity.{name}` en respuestas ni lo registres; extrae solo los campos que necesitas.

## Errores

### En runtime

La página dice que no hay errores de runtime propios.

### Al desplegar

| Error | Causa |
|---|---|
| `InvalidEntityType` | `<EntityType>` no es uno de los tipos soportados. |

## Ejemplos

### 1. Leer un atributo del API product que no publica VerifyAPIKey

```xml
<AccessEntity name="AE-Producto">
  <EntityType value="apiproduct"/>
  <EntityIdentifier ref="client_id" type="consumerkey"/>
  <SecondaryIdentifier ref="proxy.pathsuffix" type="apiresource"/>
</AccessEntity>
```

```xml
<ExtractVariables name="EV-Producto">
  <Source>AccessEntity.AE-Producto</Source>
  <VariablePrefix>producto</VariablePrefix>
  <XMLPayload>
    <Variable name="sla" type="string">
      <XPath>/ApiProduct/Attributes/Attribute[Name='sla']/Value/text()</XPath>
    </Variable>
  </XMLPayload>
</ExtractVariables>
```

### 2. Datos del desarrollador por email

```xml
<AccessEntity name="AE-Desarrollador">
  <EntityType value="developer"/>
  <EntityIdentifier ref="developer.email" type="developeremail"/>
</AccessEntity>
```

> [!WARNING]
> El ejemplo oficial combina `EntityIdentifier` de tipo `appname` con `SecondaryIdentifier ref="developer.id"` de tipo `developerid`. Recuerda que `developer.id` no es estable (ver [VerifyAPIKey](verify-api-key.md#variables-de-flujo)): para identificar al propietario, prefiere `developeremail` o `appgroupname`.

## Diferencias en Apigee Edge

| Aspecto | Apigee X / hybrid | Apigee Edge |
|---|---|---|
| Propietario de apps alternativo | AppGroup (`appgroupname`) | Company (`company`, `companyname`, `companydeveloper`) |
| `<OutputFormat>` JSON | Solo hybrid ≥ 1.4 | No |
| Caché de entidades | ≥ 180 s | ≥ 180 s |

## Antipatrones

- Usar AccessEntity para datos que ya publican VerifyAPIKey u OAuthV2.
- Exponer el perfil completo (incluye secretos).
- Llamarla en cada petición de un API de mucho tráfico sin necesidad: es una consulta al almacén (mitigada por la caché de 180 s).

## Fuentes

- AccessEntity policy — Apigee X/hybrid: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/access-entity-policy> (consultada directamente, contenido completo, 2026-10-22). La tabla de tipos se reconstruyó desde el HTML original.
- Access Entity policy — Apigee Edge: <https://docs.apigee.com/api-platform/reference/policies/access-entity-policy> (consultada directamente, 2026-10-22).
