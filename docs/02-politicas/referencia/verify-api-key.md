---
id: politica-verify-api-key
titulo: VerifyAPIKey — referencia completa
area: politicas
tags: [verifyapikey, api-key, consumer-key, client_id, autenticacion, api-product, appgroup, extensible]
aplica_a: [apigee-x, apigee-hybrid, apigee-edge]
elemento_xml: VerifyAPIKey
tipo_politica: extensible
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/verify-api-key-policy
fuente_edge: https://docs.apigee.com/api-platform/reference/policies/verify-api-key-policy
revisado: 2026-10-22
---

# VerifyAPIKey — referencia completa

> [!NOTE]
> **Tipo:** Extensible. **Elemento raíz:** `<VerifyAPIKey>`.
> **Aplica a:** Apigee X, hybrid y Edge. `<CacheExpiryInSeconds>` y las variables de AppGroup y de monetización son de X/hybrid; Edge usa variables de *Company*.

VerifyAPIKey comprueba en runtime que la petición trae una API key (también llamada *consumer key*, *app key* o, en OAuth, `client_id`) que:

1. existe,
2. pertenece a una app aprobada cuyo propietario (desarrollador o AppGroup) está activo, y
3. está asociada a un **API product** que incluye el recurso solicitado en este entorno.

Si todo cuadra, puebla decenas de variables con el contexto de la app, el desarrollador y el producto, que luego consumen Quota, SpikeArrest, AssignMessage o el backend. Contexto conceptual en [API keys](../../03-seguridad/01-apikeys.md).

## Sintaxis completa

```xml
<VerifyAPIKey name="VAK-Header" continueOnError="false" enabled="true">
  <DisplayName>Verificar API key</DisplayName>
  <APIKey ref="request.header.x-api-key"/>
  <CacheExpiryInSeconds ref="variable.con.ttl">180</CacheExpiryInSeconds>
</VerifyAPIKey>
```

## Atributos del elemento raíz

| Atributo | Obligatorio | Default | Qué hace |
|---|---|---|---|
| `name` | Sí | — | Nombre interno. Forma el prefijo de las variables: `verifyapikey.{name}.*`. Máximo 255 caracteres. |
| `continueOnError` | No | `false` | Con `true` la petición sigue aunque la key sea inválida. Solo tiene sentido si después decides tú qué hacer, p. ej. aceptar también un JWT. |
| `enabled` | No | `true` | Con `false` la política no se ejecuta. |
| `async` | No | `false` | **Obsoleto.** |

## Elementos hijos

| Elemento | Obligatorio | Tipo | Default | Resumen |
|---|---|---|---|---|
| `<DisplayName>` | No | String | valor de `name` | Etiqueta en la UI. |
| `<APIKey ref>` | **Sí** | String | — | Variable donde viene la key. **Solo una ubicación por política.** |
| `<CacheExpiryInSeconds>` | No | Integer 1–180 | 180 | Solo X/hybrid. TTL de la caché de keys verificadas. |

### `<APIKey>`

`ref` apunta a la variable que contiene la key:

| Ubicación | `ref` | Recomendación |
|---|---|---|
| Cabecera | `request.header.x-api-key` | **Preferida.** No queda en el historial del navegador ni en logs de acceso. |
| Parámetro de formulario | `request.formparam.apikey` | Aceptable. |
| Query param | `request.queryparam.apikey` | Evítala: la URL queda registrada en historiales, proxies y logs. |
| Variable propia | `credencial.key` | Cuando la key viene en otro sitio (p. ej. dentro de un `Authorization: ApiKey ...`), extráela antes con `ExtractVariables`. |

Si quieres aceptar la key en dos lugares, normalízala antes en una sola variable con `AssignMessage` o `JavaScript`; la política solo lee una.

Sin `ref` ni valor, el despliegue falla con `SpecifyValueOrRefApiKey`.

### `<CacheExpiryInSeconds>` (solo X/hybrid)

Apigee cachea el resultado de la verificación para no consultar el almacén de keys en cada petición. Este elemento fija ese TTL.

| Aspecto | Valor |
|---|---|
| Rango válido | Entero de 1 a 180 segundos |
| Si se omite | 180 s |
| `ref` | Variable con el TTL; si resuelve, tiene prioridad sobre el valor literal |
| Coste | Bajar el TTL reduce el rendimiento |

Consecuencia operativa: **revocar una app o una key puede tardar hasta el TTL en tener efecto** en el runtime. Si necesitas que una revocación surta efecto rápido, baja el TTL en las APIs sensibles.

## Variables de flujo

Se pueblan **solo cuando la key es válida**. Todas llevan el prefijo `verifyapikey.{name}.`; en las tablas se omite.

### Generales

| Variable | Contenido |
|---|---|
| `client_id` | La key recibida. |
| `client_secret` | El secreto asociado a la key. **No lo propagues** al backend ni a logs. |
| `redirection_uris` | URIs de redirección de la petición. |
| `developer.app.name` | Nombre de la app (de desarrollador o de AppGroup). |
| `developer.app.id` | ID interno de la app. **No es estable**: no lo uses como identificador de Quota, clave de KVM ni identificador hacia el backend. |
| `developer.id` | ID interno del propietario (desarrollador o AppGroup). **No es estable**: mismas restricciones. |
| `developer.{atributo}` | Atributos personalizados del perfil de la key. |
| `{atributo_de_app}` | Atributos personalizados de la app. Si una app y su key tienen un atributo con el mismo nombre, **gana el de la key**. |
| `DisplayName` | El `<DisplayName>` de la política. |
| `failed` | `true` si la verificación falló. |
| `apiproduct.name` | Producto con el que se autorizó la petición. |
| `apiproduct.{atributo}` | Atributos personalizados del producto. Así se implementan *feature flags* y tasas por plan. |
| `apiproduct.developer.quota.limit` | Límite de cuota del producto, si lo tiene. |
| `apiproduct.developer.quota.interval` | Intervalo de cuota del producto. |
| `apiproduct.developer.quota.timeunit` | Unidad de cuota del producto. |

Las variables `apiproduct.*` solo se pueblan si el producto está bien configurado: entorno, proxies y recursos que casen con `proxy.pathsuffix`.

### De la app (`app.`)

| Variable | Contenido |
|---|---|
| `app.name`, `app.id`, `app.DisplayName` | Identidad de la app. |
| `app.status` | `approved`, `revoked`… |
| `app.apiproducts` | Array con los productos de la app. |
| `app.appFamily` | Familia de la app o `default`. |
| `app.appType` | `Developer` o `AppGroup` (en Edge, `Developer` o `Company`). |
| `app.appParentId`, `app.appParentStatus` | Propietario y su estado (`active`, `inactive`). |
| `app.callbackUrl` | URL de callback (uso típico: OAuth). |
| `app.accessType` | No lo usa Apigee. |
| `app.created_at`, `app.created_by`, `app.last_modified_at`, `app.last_modified_by` | Auditoría. |
| `app.{atributo}` | Atributos personalizados de la app. |

### Del desarrollador (`developer.`)

| Variable | Contenido |
|---|---|
| `developer.id` | `{org}@@@{developer_id}` (ver advertencia de estabilidad). |
| `developer.userName`, `developer.firstName`, `developer.lastName`, `developer.email` | Datos del desarrollador. |
| `developer.status` | `active`, `inactive` o `login_lock`. |
| `developer.apps` | Array de apps. **Leerla es lento si el desarrollador tiene más de 10 apps.** |
| `developer.created_at`, `developer.created_by`, `developer.last_modified_at`, `developer.last_modified_by` | Auditoría. |
| `developer.{atributo}` | Atributos personalizados. |

### De AppGroup (`appgroup.`, solo X/hybrid)

Se pueblan solo si `app.appType` es `AppGroup`.

| Variable | Contenido |
|---|---|
| `appgroup.name`, `appgroup.displayName` | Identidad del AppGroup. |
| `appgroup.id` | ID interno. **No es estable**: mismas restricciones que `developer.id`. |
| `appgroup.appOwnerStatus` | `active`, `inactive` o `login_lock`. |
| `appgroup.created_at`, `appgroup.created_by`, `appgroup.last_modified_at`, `appgroup.last_modified_by` | Auditoría. |
| `appgroup.{atributo}` | Atributos personalizados. |

Al migrar desde Edge, las variables de *Company* quedan disponibles automáticamente como las de AppGroup, sin cambiar los bundles.

### De monetización (solo X/hybrid)

Tras autenticar, la política busca un *rate plan* publicado y activo para el producto. Si lo encuentra:

| Variable | Contenido |
|---|---|
| `mint.mintng_is_apiproduct_monetized` | `true` si hay un plan activo. |
| `mint.mintng_rate_plan_id` | ID del plan. |
| `mint.rateplan_start_time_ms`, `mint.rateplan_end_time_ms` | Vigencia del plan (epoch en ms). |

Estas variables no llevan el prefijo `verifyapikey.{name}.`.

### Dimensiones de Analytics

VerifyAPIKey (y las políticas OAuth) son las únicas que alimentan estas dimensiones de Analytics: `apiproduct.name`, `developer.app.name`, `client_id` y `developer.id`. Sin una de ellas en el proxy, los informes por app o por producto salen vacíos.

## Errores

### En runtime

| Código de fallo | HTTP | Causa |
|---|---|---|
| `oauth.v2.FailedToResolveAPIKey` | 401 | La variable de `<APIKey ref>` no existe: el cliente no mandó la key. **También** aparece cuando la key está en estado `revoked` o `pending` (ver nota). |
| `oauth.v2.InvalidApiKey` | 401 | La key no existe, por ejemplo porque se regeneró y el cliente sigue usando la vieja. |
| `oauth.v2.InvalidApiKeyForGivenResource` | 401 | La key es válida, pero ninguno de sus productos aprobados cubre este proxy, recurso o entorno. |
| `keymanagement.service.invalid_client-app_not_approved` | 401 | La app está revocada. |
| `keymanagement.service.DeveloperStatusNotActive` | 401 | El desarrollador propietario está inactivo, lo que desactiva todas sus apps. |
| `keymanagement.service.consumer_key_missing_api_product_association` | 400 | Solo X/hybrid. La credencial no tiene ningún API product asociado. |
| `keymanagement.service.CompanyStatusNotActive` | 401 | Solo Edge. La *Company* propietaria está inactiva. |

> [!WARNING]
> Una key **no aprobada** (`revoked` o `pending`) no produce un error propio: Apigee la reporta como `FailedToResolveAPIKey`, el mismo error que cuando falta la key. Si tu FaultRule responde "falta la API key" para ese código, el mensaje será engañoso para esos clientes. Usa un texto neutro, del tipo "credencial ausente o no válida".

### Al desplegar

| Error | Causa |
|---|---|
| `SpecifyValueOrRefApiKey` | `<APIKey>` sin `ref` ni valor. |

### Variables de fallo

| Variable | Ejemplo |
|---|---|
| `fault.name` | `fault.name = "InvalidApiKey"` |
| `oauthV2.{name}.failed` | `oauthV2.VAK-Header.failed = true` |

> [!NOTE]
> La variable de fallo usa el prefijo **`oauthV2.`**, no `verifyapikey.`, porque la política se implementa sobre el mismo motor que OAuthV2. En la tabla de variables generales aparece además `verifyapikey.{name}.failed`. Para condiciones de FaultRule usa `fault.name`, que es lo que la documentación recomienda.

## Ejemplos

### 1. Verificación estándar por cabecera, sin filtrar la key al backend

```xml
<VerifyAPIKey name="VAK-Header">
  <APIKey ref="request.header.x-api-key"/>
</VerifyAPIKey>
```

```xml
<AssignMessage name="AM-Quitar-Key">
  <Remove>
    <Headers>
      <Header name="x-api-key"/>
    </Headers>
  </Remove>
  <IgnoreUnresolvedVariables>true</IgnoreUnresolvedVariables>
  <AssignTo createNew="false" transport="http" type="request"/>
</AssignMessage>
```

Orden en el PreFlow del ProxyEndpoint: `SpikeArrest` → `VAK-Header` → `Quota` → `AM-Quitar-Key`.

### 2. Key dentro de `Authorization: ApiKey <valor>`

```xml
<ExtractVariables name="EV-Key-De-Authorization">
  <Source>request</Source>
  <Header name="Authorization">
    <Pattern ignoreCase="true">ApiKey {key}</Pattern>
  </Header>
  <VariablePrefix>credencial</VariablePrefix>
  <IgnoreUnresolvedVariables>true</IgnoreUnresolvedVariables>
</ExtractVariables>
```

```xml
<VerifyAPIKey name="VAK-Authorization">
  <APIKey ref="credencial.key"/>
</VerifyAPIKey>
```

### 3. Pasar al backend la identidad de la app, no IDs internos

Se reenvía el nombre de la app y un atributo estable del desarrollador, nunca `developer.id` ni `developer.app.id`.

```xml
<AssignMessage name="AM-Identidad-Al-Backend">
  <Set>
    <Headers>
      <Header name="X-Consumidor-App">{verifyapikey.VAK-Header.developer.app.name}</Header>
      <Header name="X-Consumidor-Cuenta">{verifyapikey.VAK-Header.developer.cuenta_id}</Header>
      <Header name="X-Producto">{verifyapikey.VAK-Header.apiproduct.name}</Header>
    </Headers>
  </Set>
  <IgnoreUnresolvedVariables>true</IgnoreUnresolvedVariables>
  <AssignTo createNew="false" transport="http" type="request"/>
</AssignMessage>
```

### 4. Respuesta 401 uniforme

```xml
<FaultRules>
  <FaultRule name="fr-credencial-invalida">
    <Condition>fault.name = "FailedToResolveAPIKey" or fault.name = "InvalidApiKey" or fault.name = "InvalidApiKeyForGivenResource" or fault.name = "invalid_client-app_not_approved" or fault.name = "DeveloperStatusNotActive"</Condition>
    <Step>
      <Name>AM-Error-401</Name>
    </Step>
  </FaultRule>
</FaultRules>
```

```xml
<AssignMessage name="AM-Error-401">
  <Set>
    <StatusCode>401</StatusCode>
    <Headers>
      <Header name="WWW-Authenticate">ApiKey realm="api"</Header>
    </Headers>
    <Payload contentType="application/json">{"codigo":"CREDENCIAL_INVALIDA","mensaje":"Credencial ausente o no valida."}</Payload>
  </Set>
  <IgnoreUnresolvedVariables>true</IgnoreUnresolvedVariables>
  <AssignTo createNew="false" transport="http" type="response"/>
</AssignMessage>
```

### 5. Revocación con efecto rápido en un API sensible (X/hybrid)

```xml
<VerifyAPIKey name="VAK-Pagos">
  <APIKey ref="request.header.x-api-key"/>
  <CacheExpiryInSeconds>30</CacheExpiryInSeconds>
</VerifyAPIKey>
```

## Diferencias en Apigee Edge

| Aspecto | Apigee X / hybrid | Apigee Edge |
|---|---|---|
| `<CacheExpiryInSeconds>` | Sí (1–180 s, default 180) | No documentado |
| Propietario B2B de la app | AppGroup (`appgroup.*`) | Company (`company.*`) |
| `app.appType` | `Developer` o `AppGroup` | `Developer` o `Company` |
| Variables `mint.*` de monetización | Sí | No en esta política |
| Error por producto ausente | `consumer_key_missing_api_product_association` (400) | No documentado |
| Error por propietario B2B inactivo | No documentado | `CompanyStatusNotActive` (401) |
| `ApiKeyNotApproved` reportado como `FailedToResolveAPIKey` | Sí | Sí |

## Antipatrones

- Key en query param en APIs públicas.
- Reenviar la cabecera con la key al backend.
- Usar `developer.id`, `developer.app.id` o `appgroup.id` como identificador de cuota, clave de KVM o identidad hacia el backend.
- Poner la `Quota` antes de la `VerifyAPIKey` cuando la cuota depende del producto.
- Usar API key como **única** protección de operaciones sensibles: una key identifica a la app, no autentica al usuario (ver [OAuth 2.0](../../03-seguridad/02-oauth2.md)).

## Fuentes

- VerifyAPIKey policy — Apigee X/hybrid: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/verify-api-key-policy> (consultada directamente, contenido completo, 2026-10-22).
- Verify API Key policy — Apigee Edge: <https://docs.apigee.com/api-platform/reference/policies/verify-api-key-policy> (consultada directamente, 2026-10-22).
- Proteger un API con API keys (tutorial): <https://docs.cloud.google.com/apigee/docs/api-platform/tutorials/secure-calls-your-api-through-api-key-validation>
