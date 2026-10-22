---
id: politica-ldap
titulo: LDAP — referencia completa, solo Edge for Private Cloud
area: politicas
tags: [ldap, autenticacion, directorio, private-cloud, edge]
aplica_a: [apigee-edge]
elemento_xml: Ldap
tipo_politica: solo-edge
fuente: https://docs.apigee.com/api-platform/reference/policies/ldap-policy
revisado: 2026-10-22
---

# LDAP — referencia completa, solo Edge for Private Cloud

> [!NOTE]
> **Solo Apigee Edge for Private Cloud.** **Elemento raíz:** `<Ldap>`, no `<LDAP>`.
> En Apigee X y hybrid no existe. Para autenticar contra un directorio desde X, expón el directorio detrás de un servicio de identidad (OIDC o SAML) y valida sus tokens con [VerifyJWT](verify-jwt.md) u [OAuthV2](oauthv2.md), o llama a un servicio propio con [ServiceCallout](service-callout.md). Esta sugerencia es de este repositorio.

La política LDAP hace dos cosas contra un proveedor LDAP:

1. **Autenticación:** valida las credenciales de la petición contra el directorio. Admite usar como identificador cualquier atributo del DN, no solo el usuario. Por ejemplo, busca el DN por email y autentica con la contraseña.
2. **Búsqueda de DN:** identifica al usuario por un atributo (por ejemplo `mail`) y recupera otros atributos (dirección, teléfono, cargo) en variables.

Google la propone para limitar recursos a usuarios del directorio (administradores, usuarios internos, desarrolladores) cuando OAuth es innecesario o demasiado pesado.

## Sintaxis completa

```xml
<Ldap name="LDAP-Nombre">
  <LdapConnectorClass>com.empresa.ldap.MiProveedor</LdapConnectorClass>
  <LdapResource>ldap-corporativo</LdapResource>
  <Authentication>
    <UserName ref="request.header.username"/>
    <Password ref="request.header.password"/>
    <Scope>subtree</Scope>
    <BaseDN ref="apigee.baseDN">dc=empresa,dc=com</BaseDN>
  </Authentication>
</Ldap>
```

```xml
<Ldap name="LDAP-Buscar">
  <LdapResource>ldap-corporativo</LdapResource>
  <Search>
    <BaseDN>dc=empresa,dc=com</BaseDN>
    <SearchQuery>mail={request.header.mail}</SearchQuery>
    <Attributes>
      <Attribute>telephoneNumber</Attribute>
      <Attribute>title</Attribute>
    </Attributes>
    <Scope>subtree</Scope>
  </Search>
</Ldap>
```

## Elementos

| Elemento | Resumen |
|---|---|
| `<LdapResource>` | Nombre del **recurso LDAP del entorno** con los datos de conexión (ver abajo). |
| `<LdapConnectorClass>` | Solo con un proveedor LDAP **propio**: clase completa que implementa `ExternalLdapConProvider`. |
| `<BaseDN ref>` | Base del árbol, por ejemplo `dc=empresa,dc=com`. `ref` tiene prioridad sobre el literal; si no resuelve, se usa el literal. |
| `<Scope>` | `object` (solo la base), `onelevel` (un nivel por debajo) o `subtree` (recursivo, el default). |
| `<Authentication>` | Bloque de autenticación. |
| `.../<UserName ref value>` | Usuario. |
| `.../<Password ref value>` | Contraseña. |
| `.../<SearchQuery>` | Autentica con otro atributo: busca el DN con la consulta (por ejemplo `mail={request.header.mail}`) y luego valida la contraseña. Admite plantillas. |
| `<Search>` | Bloque de búsqueda. |
| `.../<SearchQuery>` | Filtro que identifica al usuario. |
| `.../<Attributes>/<Attribute>` | Atributos a recuperar. **Al menos uno.** |

> [!NOTE]
> **Contradicción en la documentación oficial:**
> - La descripción de `<UserName>` dice que, si quieres autenticar con otro atributo, puedes incluir una `<SearchQuery>` y la política usará el usuario para buscar ese atributo.
> - El ejemplo de autenticación por atributo y el error `SearchQueryAndUserNameCannotBePresent` dicen lo contrario: **no** pueden ir juntos.
>
> Sigue el error: con `<SearchQuery>` en `<Authentication>`, omite `<UserName>`.

> [!IMPORTANT]
> Según la página, para buscar y recuperar atributos con `<Search>` la petición debe incluir **credenciales de administrador** del directorio.

## Recurso LDAP del entorno

La conexión se define aparte, como recurso del entorno, con la API de gestión:

- `POST` y `GET` sobre `/v1/organizations/{org}/environments/{env}/ldapresources` para crear y listar.
- `GET`, `POST` y `DELETE` sobre `/ldapresources/{nombre}` para leer, actualizar y borrar.

| Elemento del recurso | Default | Resumen |
|---|---|---|
| `<Hosts>/<Host port>` | Puerto 389 (`ldap://`) o 636 (`ldaps://`) | Servidores. |
| `<SSLEnabled>` | `false` | LDAPS. |
| `<Version>` | `3` | Versión de LDAP. |
| `<Authentication>` | `simple` | Solo se admite `simple`. |
| `<ConnectionProvider>` | Obligatorio | `jndi` o `unboundid`. |
| `<ServerSetType>` | — | `single`, `round robin` o `failover`; no aplica con `jndi`. |
| `<ConnectPool enabled>/<Timeout>` | Pool activo, sin timeout | Pool de conexiones; el timeout va en ms. |

> [!WARNING]
> `<SSLEnabled>` viene en `false` por defecto: credenciales y datos del directorio viajan **en claro** en ese caso. Actívalo siempre (LDAPS, puerto 636).

### Proveedor propio o UnboundID

- **Proveedor propio:** implementa `ExternalLdapConProvider` (`doAuthentication`, `doSearchAndAuthentication`, `doSearch`, `closeConnections`). Añade al classpath del entorno el JAR que distribuye Google, indica la clase en `<LdapConnectorClass>` y crea el recurso del entorno.
- **UnboundID LDAP SDK:** se usa la **versión 2.3.1** (edición SE). El JAR se copia en `/opt/apigee/edge-gateway/lib/thirdparty` de **cada Message Processor**, y luego se reinicia el MP.

## Variables de flujo

| Variable | Valor |
|---|---|
| `ldap.{policyName}.execution.success` | `true` o `false`. |
| `ldap.{policyName}.search.result[i].attribute.{attr}[j]` | Atributo `attr` del resultado `i`, valor `j`. Los índices empiezan en 1, y sin índice se toma el 1. Por ejemplo `ldap.LDAP-Buscar.search.result.attribute.title`. |

**Respuesta:** `200` si la operación tiene éxito, `401` si falla.

## Errores

| Código | Mensaje (resumido) |
|---|---|
| `InvalidAttributeName` | Nombre de atributo no válido. |
| `InvalidSearchBase` / `BaseDNRequired` | Falta la base de búsqueda. |
| `InvalidValueForPassword` | Contraseña vacía. |
| `InvalidSearchScope` | Ámbito no permitido. |
| `InvalidUserCredentials` | Credenciales incorrectas. |
| `InvalidExternalLdapReference` | Referencia al proveedor externo no válida. |
| `LdapResourceNotFound` | No existe el recurso LDAP. |
| `OnlyReferenceOrValueIsAllowed` | Se usaron `ref` y `value` a la vez. |
| `AttributesRequired` | `<Search>` sin atributos. |
| `UserNameIsNull` | Usuario nulo. |
| `SearchQueryAndUserNameCannotBePresent` | `<UserName>` y `<SearchQuery>` juntos en `<Authentication>`. |

## Antipatrones

- **Credenciales en cabeceras propias** (`username` y `password`, como en los ejemplos oficiales) sin TLS extremo a extremo. Como mínimo, usa HTTPS y la cabecera `Authorization: Basic`, con [BasicAuthentication](basic-authentication.md) para decodificarla.
- **`<SSLEnabled>false</SSLEnabled>` hacia el directorio.**
- **Inyección en `<SearchQuery>`.** `mail={request.header.mail}` inserta la entrada del cliente en un filtro LDAP: un valor como `*)(uid=*` cambia la consulta. Valida el formato antes, por ejemplo con [RegularExpressionProtection](regular-expression-protection.md) o un patrón estricto. Esta advertencia es de este repositorio, no de la página.
- **Autenticar en cada llamada contra LDAP con mucho tráfico.** Convierte el directorio en cuello de botella; mejor emitir un token tras el primer login.

## Fuentes

- LDAP policy — Apigee Edge: <https://docs.apigee.com/api-platform/reference/policies/ldap-policy> (consultada directamente, contenido completo, 2026-10-22).
