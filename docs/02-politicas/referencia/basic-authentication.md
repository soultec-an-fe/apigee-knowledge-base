---
id: politica-basic-authentication
titulo: BasicAuthentication — referencia completa
area: politicas
tags: [basicauthentication, basic-auth, base64, credenciales, backend, extensible]
aplica_a: [apigee-x, apigee-hybrid, apigee-edge]
elemento_xml: BasicAuthentication
tipo_politica: extensible
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/basic-authentication-policy
fuente_edge: https://docs.apigee.com/api-platform/reference/policies/basic-authentication-policy
revisado: 2026-10-22
---

# BasicAuthentication — referencia completa

> [!NOTE]
> **Tipo:** Extensible. **Elemento raíz:** `<BasicAuthentication>`.
> **Aplica a:** Apigee X, hybrid y Edge, con el mismo comportamiento.

BasicAuthentication **codifica o decodifica** credenciales en el formato `Basic base64(usuario:contraseña)` de HTTP Basic. Tiene dos modos:

| `<Operation>` | Qué hace | Uso típico |
|---|---|---|
| `Encode` | Toma usuario y contraseña de variables y escribe `Basic …` en otra variable (normalmente `request.header.Authorization`). | Autenticarse contra un **backend** o un ServiceCallout que exige Basic ("última milla"). |
| `Decode` | Toma una cadena `Basic …` y escribe usuario y contraseña en variables. | Leer las credenciales que manda el cliente para **validarlas tú** después. |

> [!IMPORTANT]
> La política **no autentica** a nadie: no comprueba que la contraseña sea correcta. Para validar credenciales Basic entrantes, decodifícalas y compáralas tú (contra un KVM, un IdP con ServiceCallout, o usando el usuario como API key de una app con VerifyAPIKey). Y Basic **no cifra**: usa siempre TLS.

## Sintaxis completa

```xml
<BasicAuthentication name="BA-Nombre" continueOnError="false" enabled="true">
  <DisplayName>Nombre legible</DisplayName>
  <Operation>Encode</Operation>
  <IgnoreUnresolvedVariables>false</IgnoreUnresolvedVariables>
  <User ref="private.backend.usuario"/>
  <Password ref="private.backend.password"/>
  <AssignTo createNew="false">request.header.Authorization</AssignTo>
  <!-- Solo con Decode: -->
  <!-- <Source>request.header.Authorization</Source> -->
</BasicAuthentication>
```

## Atributos del elemento raíz

| Atributo | Obligatorio | Default | Qué hace |
|---|---|---|---|
| `name` | Sí | — | Nombre interno. |
| `continueOnError` | No | `false` | Con `true`, el flujo sigue aunque falle. |
| `enabled` | No | `true` | Con `false` no se ejecuta. |
| `async` | No | `false` | **Obsoleto.** |

## Elementos hijos

| Elemento | Obligatorio | Default | Resumen |
|---|---|---|---|
| `<Operation>` | **Sí** | — | `Encode` o `Decode`. |
| `<IgnoreUnresolvedVariables>` | No | `true` | Con `false`, una variable que no resuelve produce `UnresolvedVariable`. **Ponlo en `false`.** |
| `<User ref>` | **Sí** | — | Encode: variable de la que se **lee** el usuario. Decode: variable donde se **escribe**. |
| `<Password ref>` | **Sí** | — | Igual que `<User>`, para la contraseña. |
| `<AssignTo createNew>` | Sí con Encode | — | Variable donde se escribe `Basic …`. |
| `<Source>` | Sí con Decode | — | Variable con la cadena `Basic …` a decodificar. |

Usuario y contraseña se unen con `:` antes de codificar. Los elementos ausentes hacen fallar el despliegue: `UserNameRequired`, `PasswordRequired`, `AssignToRequired`, `SourceRequired`.

### `<AssignTo createNew>`

| `createNew` | Comportamiento |
|---|---|
| `false` (default) | Solo escribe si la variable **está vacía**. Si el cliente ya mandó una cabecera `Authorization`, **no se sobrescribe**. |
| `true` | Escribe siempre. |

> [!WARNING]
> Con el default `createNew="false"` y `request.header.Authorization`, si la petición del cliente trae su propio `Authorization` (por ejemplo su token OAuth), el backend recibirá **ese** y no las credenciales del gateway. Para credenciales hacia el backend, usa `createNew="true"` o elimina antes la cabecera del cliente con AssignMessage.

### `<IgnoreUnresolvedVariables>`

El default es `true`, lo que significa que si la variable de la contraseña no existe (KVM mal leído, por ejemplo), la política codifica una cadena vacía **sin fallar**. Declara `false` para que el error salga en el gateway y no como un 401 confuso del backend.

## Variables de flujo

Solo `BasicAuthentication.{name}.failed` (`true` si falló). La página aclara que las variables `BasicAuthentication.{name}.fault.cause` y `.fault.name`, si aparecen, no las usa Apigee.

## Errores

### En runtime

| Código | HTTP | Causa |
|---|---|---|
| `steps.basicauthentication.InvalidBasicAuthenticationSource` | 500 | Decode: la cadena no es Base64 válido o no empieza por `Basic`. |
| `steps.basicauthentication.UnresolvedVariable` | 500 | Falta una variable de origen (solo con `<IgnoreUnresolvedVariables>false`). |

> [!TIP]
> Si decodificas credenciales del **cliente**, una cabecera mal formada es culpa del cliente: traduce `InvalidBasicAuthenticationSource` a `401` con `WWW-Authenticate: Basic`.

### Al desplegar

`UserNameRequired`, `PasswordRequired`, `AssignToRequired`, `SourceRequired`.

### Variables de fallo

| Variable | Ejemplo |
|---|---|
| `fault.name` | `fault.name = "UnresolvedVariable"` |
| `BasicAuthentication.{name}.failed` | `BasicAuthentication.BA-Backend.failed = true` |

## Ejemplos

### 1. Credenciales del backend desde un KVM cifrado

```xml
<KeyValueMapOperations name="KVM-Credenciales-Backend" mapIdentifier="credenciales-backend">
  <Scope>environment</Scope>
  <Get assignTo="private.backend.usuario">
    <Key><Parameter>usuario</Parameter></Key>
  </Get>
  <Get assignTo="private.backend.password">
    <Key><Parameter>password</Parameter></Key>
  </Get>
</KeyValueMapOperations>
```

```xml
<BasicAuthentication name="BA-Backend">
  <Operation>Encode</Operation>
  <IgnoreUnresolvedVariables>false</IgnoreUnresolvedVariables>
  <User ref="private.backend.usuario"/>
  <Password ref="private.backend.password"/>
  <AssignTo createNew="true">request.header.Authorization</AssignTo>
</BasicAuthentication>
```

Ambas en el PreFlow de petición del **TargetEndpoint**, para que solo afecten a la llamada al backend. El prefijo `private.` evita que los valores aparezcan en Debug.

### 2. Leer credenciales Basic del cliente sin reenviarlas

El ejemplo oficial de Decode escribe usuario y contraseña en `request.header.username` y `request.header.password`, es decir, en **cabeceras que se enviarían al backend**. Mejor usar variables propias y borrar la cabecera original:

```xml
<BasicAuthentication name="BA-Leer-Cliente">
  <Operation>Decode</Operation>
  <IgnoreUnresolvedVariables>false</IgnoreUnresolvedVariables>
  <User ref="private.cliente.usuario"/>
  <Password ref="private.cliente.password"/>
  <Source>request.header.Authorization</Source>
</BasicAuthentication>
```

```xml
<AssignMessage name="AM-Quitar-Authorization">
  <Remove>
    <Headers>
      <Header name="Authorization"/>
    </Headers>
  </Remove>
  <AssignTo createNew="false" transport="http" type="request"/>
</AssignMessage>
```

Después, valida `private.cliente.usuario` y `private.cliente.password` contra tu fuente de verdad.

## Diferencias en Apigee Edge

Sin diferencias funcionales documentadas.

## Antipatrones

- Usarla creyendo que autentica al cliente.
- Basic sin TLS.
- Contraseñas en el XML de la política o en PropertySets en vez de un KVM cifrado.
- Decodificar a `request.header.*`: las credenciales viajan al backend.
- `createNew="false"` cuando la petición ya trae `Authorization`.

## Fuentes

- BasicAuthentication policy — Apigee X/hybrid: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/basic-authentication-policy> (consultada directamente, contenido completo, 2026-10-22).
- Basic Authentication policy — Apigee Edge: <https://docs.apigee.com/api-platform/reference/policies/basic-authentication-policy> (consultada directamente, 2026-10-22).
