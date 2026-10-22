---
id: politica-set-oauth-v2-info
titulo: SetOAuthV2Info — referencia completa
area: politicas
tags: [setoauthv2info, oauth2, access-token, atributos-personalizados, extensible]
aplica_a: [apigee-x, apigee-hybrid, apigee-edge]
elemento_xml: SetOAuthV2Info
tipo_politica: extensible
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/set-oauth-v2-info-policy
fuente_edge: https://docs.apigee.com/api-platform/reference/policies/set-oauth-v2-info-policy
revisado: 2026-10-22
---

# SetOAuthV2Info — referencia completa

> [!NOTE]
> **Tipo:** Extensible. **Elemento raíz:** `<SetOAuthV2Info>`.
> **Aplica a:** Apigee X, hybrid y Edge, con el mismo comportamiento.

SetOAuthV2Info **añade o actualiza atributos personalizados** de un access token ya emitido: un ID de sesión, un departamento, el resultado de una verificación posterior. Si el atributo existe, lo sobrescribe; si no, lo crea.

**No** puede cambiar los campos propios del token: `scope`, `status`, `expires_in`, `developer_email`, `client_id`, `org_name`, `refresh_count`. Para cambiar el scope o la vida hay que emitir otro token.

El token debe ser **válido y estar aprobado**.

## Sintaxis completa

```xml
<SetOAuthV2Info name="SOI-Nombre" continueOnError="false" enabled="true">
  <DisplayName>Nombre legible</DisplayName>
  <AccessToken ref="variable.con.el.token"/>
  <Attributes>
    <Attribute name="nombre_atributo" ref="variable.con.el.valor"/>
    <Attribute name="otro_atributo">valor literal</Attribute>
  </Attributes>
</SetOAuthV2Info>
```

## Atributos del elemento raíz

| Atributo | Obligatorio | Default | Qué hace |
|---|---|---|---|
| `name` | Sí | — | Nombre interno; da nombre a `oauthv2accesstoken.{name}.*`. |
| `continueOnError` | No | `false` | Con `true`, el flujo sigue aunque falle. |
| `enabled` | No | `true` | Con `false` no se ejecuta. |
| `async` | No | `false` | **Obsoleto.** |

## Elementos hijos

| Elemento | Obligatorio | Resumen |
|---|---|---|
| `<DisplayName>` | No | Etiqueta en la UI. |
| `<AccessToken ref>` | **Sí** | Variable con el access token (o, raramente, el literal). |
| `<Attributes>` | **Sí** | Contenedor de los atributos a escribir. |
| `<Attributes>/<Attribute name ref>` | No | Un atributo. `name` es el nombre; el valor sale de `ref` o del literal del elemento. |

El límite de atributos personalizados por token es el mismo que al generarlo con [OAuthV2](oauthv2.md#attributes): **18**.

## Variables de flujo

Tras ejecutarse con éxito, con el prefijo `oauthv2accesstoken.{name}.`: `access_token`, `client_id`, `refresh_count`, `organization_name`, `expires_in` (s), `refresh_token_expires_in` (s), `issued_at`, `status`, `api_product_list`, `token_type` y `{atributo}`.

## Errores

### En runtime

| Código de fallo | HTTP | Causa |
|---|---|---|
| `steps.oauth.v2.access_token_expired` | 500 | Token vencido. |
| `steps.oauth.v2.invalid_access_token` | 500 | Token inválido. |
| `steps.oauth.v2.InvalidAPICallAsNoApiProductMatchFound` | 401 | El recurso no está en el API product del token. |

### Al desplegar

La página remite a los mensajes de la UI.

### Variables de fallo

| Variable | Ejemplo |
|---|---|
| `fault.name` | `fault.name = "invalid_access_token"` |
| `oauthV2.{name}.failed` | `oauthV2.SOI-Sesion.failed = true` |
| `oauthV2.{name}.fault.name` | `invalid_access_token` |
| `oauthV2.{name}.fault.cause` | `Invalid Access Token` |

## Ejemplos

### 1. Marcar el token tras una autenticación reforzada

Después de un segundo factor, se marca el token para que los recursos sensibles lo exijan con una condición sobre `accesstoken.nivel_autenticacion`.

```xml
<SetOAuthV2Info name="SOI-Nivel-Autenticacion">
  <AccessToken ref="flujo.access_token"/>
  <Attributes>
    <Attribute name="nivel_autenticacion">2</Attribute>
    <Attribute name="mfa_en" ref="system.timestamp"/>
  </Attributes>
</SetOAuthV2Info>
```

```xml
<!-- En el recurso sensible, tras OAuthV2/VerifyAccessToken -->
<Step>
  <Name>RF-Requiere-MFA</Name>
  <Condition>accesstoken.nivel_autenticacion != "2"</Condition>
</Step>
```

> [!WARNING]
> El cambio puede tardar en verse: `VerifyAccessToken` cachea el perfil del token (incluidos sus atributos) hasta **180 s**. Tras un SetOAuthV2Info, otras peticiones pueden seguir viendo el valor anterior durante ese tiempo. En X/hybrid se puede acortar con [`<CacheExpiryInSeconds>`](oauthv2.md#cacheexpiryinseconds-solo-xhybrid). Esta interacción no la menciona la página de SetOAuthV2Info; se deduce del comportamiento de caché documentado en OAuthV2.

## Diferencias en Apigee Edge

Sin diferencias documentadas: mismos elementos, variables y errores.

## Antipatrones

- Intentar cambiar `scope` o `expires_in` con esta política.
- Guardar datos sensibles (PII, secretos) como atributos del token: se pueden devolver en la respuesta de token o al refrescarlo (ver [`display`](oauthv2.md#attributes)).
- Exponer esta política en un endpoint que el propio cliente pueda invocar para "elevarse" atributos.

## Fuentes

- SetOAuthV2Info policy — Apigee X/hybrid: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/set-oauth-v2-info-policy> (consultada directamente, contenido completo, 2026-10-22).
- SetOAuthV2Info policy — Apigee Edge: <https://docs.apigee.com/api-platform/reference/policies/set-oauth-v2-info-policy> (consultada directamente, 2026-10-22).
