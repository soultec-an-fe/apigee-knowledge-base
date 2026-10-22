---
id: politica-access-control
titulo: AccessControl — referencia completa
area: politicas
tags: [accesscontrol, ip, allowlist, denylist, cidr, x-forwarded-for, client-ip, standard]
aplica_a: [apigee-x, apigee-hybrid, apigee-edge]
elemento_xml: AccessControl
tipo_politica: standard
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/access-control-policy
fuente_edge: https://docs.apigee.com/api-platform/reference/policies/access-control-policy
revisado: 2026-10-22
---

# AccessControl — referencia completa

> [!NOTE]
> **Tipo:** Standard. **Elemento raíz:** `<AccessControl>`.
> **Aplica a:** Apigee X, hybrid y Edge, con diferencias importantes en **qué IP evalúa** (ver [Diferencias en Apigee Edge](#diferencias-en-apigee-edge)).

AccessControl **permite o deniega** peticiones según la IP de origen, con reglas en notación CIDR. Va al principio del flujo (PreFlow de petición del ProxyEndpoint), antes de autenticar o contar cuota, para que una IP bloqueada consuma lo mínimo.

Como alternativa o complemento a nivel de red, en X se puede poner **Google Cloud Armor** delante de Apigee.

## Lo difícil: qué IP se evalúa

Entre el cliente y Apigee suele haber balanceadores. La IP "del cliente" que llega a la política puede salir de tres sitios, y elegir mal anula el control:

| Fuente | Cómo se configura | Fiabilidad |
|---|---|---|
| **`<ClientIPVariable>`** con `client.resolved.ip` (X/hybrid) | Variable que Apigee calcula según la **resolución de IP del cliente** configurada en el entorno | **La recomendada**. Coherente con Analytics y Advanced API Security. |
| `X-Forwarded-For` con `<ValidateBasedOn>` | Primer IP, último IP o todos | Depende de la topología; el primero lo puede falsificar el cliente. |
| `True-Client-IP` | Edge lo evalúa primero salvo `<IgnoreTrueClientIPHeader>` | Solo si confías plenamente en quien pone la cabecera. |

### `X-Forwarded-For` en Apigee X

En X, con los balanceadores de Google Cloud, la cabecera tiene normalmente la forma:

```text
X-Forwarded-For: <ip_cliente>, <ip_GCLB>, <ip_ingress_interno>
```

| `<ValidateBasedOn>` | Evalúa | Problema |
|---|---|---|
| `X_FORWARDED_FOR_ALL_IP` (default) | Todas | Una IP falsificada al principio puede coincidir con una regla. |
| `X_FORWARDED_FOR_FIRST_IP` | La del cliente | **El cliente la puede falsificar** enviando su propio `X-Forwarded-For`. |
| `X_FORWARDED_FOR_LAST_IP` | La interna del segundo balanceador | **No es el cliente**: la política se comporta de forma inesperada. |

> [!IMPORTANT]
> Ninguna de las tres opciones sirve bien en X para listas de bloqueo o de permiso fiables. Configura la **resolución de IP del cliente** del entorno (`clientIpResolutionConfig`: cabecera y posición contando desde la derecha según los saltos de tu red) y usa `<ClientIPVariable>client.resolved.ip</ClientIPVariable>`. Los cambios de esa configuración tardan unos 5 minutos en aplicarse.

En **hybrid**, Google recomienda un balanceador delante del clúster: si es L7, que añada la IP a `X-Forwarded-For`; si es L4, que use el **protocolo PROXY**.

### IPs inválidas

| Fuente | Valor no IP (p. ej. `pwned`) |
|---|---|
| `X-Forwarded-For` (sin `<ClientIPVariable>`) | Se **ignora en silencio** y se aplica `noRuleMatchAction`. Con `ALLOW`, un atacante puede **saltarse una lista de bloqueo**. |
| `<ClientIPVariable>` | Error explícito `InvalidIPAddressInVariable` (`500`). |

## Sintaxis completa

```xml
<AccessControl name="AC-Nombre" continueOnError="false" enabled="true">
  <DisplayName>Nombre legible</DisplayName>
  <ClientIPVariable>client.resolved.ip</ClientIPVariable>
  <IPRules noRuleMatchAction="DENY">
    <MatchRule action="ALLOW">
      <SourceAddress mask="24">198.51.100.0</SourceAddress>
      <SourceAddress mask="{flujo.mascara}">{flujo.ip_socio}</SourceAddress>
    </MatchRule>
    <MatchRule action="DENY">
      <SourceAddress mask="32">203.0.113.7</SourceAddress>
    </MatchRule>
  </IPRules>
  <!-- Alternativas a ClientIPVariable: -->
  <!-- <IgnoreTrueClientIPHeader>true</IgnoreTrueClientIPHeader> -->
  <!-- <ValidateBasedOn>X_FORWARDED_FOR_ALL_IP</ValidateBasedOn> -->
</AccessControl>
```

## Atributos del elemento raíz

| Atributo | Obligatorio | Default | Qué hace |
|---|---|---|---|
| `name` | Sí | — | Nombre interno; da nombre a `acl.{name}.failed`. |
| `continueOnError` | No | `false` | Con `true`, una IP denegada **pasa**. No lo uses aquí. |
| `enabled` | No | `true` | Con `false` no se ejecuta. |
| `async` | No | `false` | **Obsoleto.** |

## Elementos hijos

| Elemento | Obligatorio | Default | Resumen |
|---|---|---|---|
| `<ClientIPVariable>` | No | — | Variable con la IP a evaluar (X/hybrid). |
| `<IPRules noRuleMatchAction>` | **Sí** | `ALLOW` | Contenedor de reglas; qué hacer si ninguna coincide. |
| `<IPRules>/<MatchRule action>` | Sí | — | `ALLOW` o `DENY` si la IP coincide con alguna `<SourceAddress>`. |
| `<MatchRule>/<SourceAddress mask>` | Sí | — | IP y máscara CIDR; ambas admiten plantillas (`{variable}`). |
| `<ValidateBasedOn>` | No | `X_FORWARDED_FOR_ALL_IP` | Qué IPs de `X-Forwarded-For` evaluar. |
| `<IgnoreTrueClientIPHeader>` | No | — | Ignorar `True-Client-IP` (ver nota). |

### Orden de evaluación

Las `<MatchRule>` se evalúan **en orden**; la primera que coincide decide y las demás se saltan. Por eso, para "permitir una red salvo algunas IPs", pon primero el `DENY` concreto y después el `ALLOW` amplio:

```xml
<IPRules noRuleMatchAction="DENY">
  <MatchRule action="DENY">
    <SourceAddress mask="32">198.51.100.66</SourceAddress>
  </MatchRule>
  <MatchRule action="ALLOW">
    <SourceAddress mask="24">198.51.100.0</SourceAddress>
  </MatchRule>
</IPRules>
```

> [!TIP]
> Para APIs internas o de socios, usa una lista de permiso: `noRuleMatchAction="DENY"` con `MatchRule action="ALLOW"`. Una lista de bloqueo (`ALLOW` por defecto) protege poco: el atacante cambia de IP.

### `<SourceAddress mask>`

`mask` equivale al sufijo CIDR: IPv4 `1`-`32`, IPv6 `1`-`128` (`0` solo tiene sentido con `0.0.0.0`). Ejemplos: `mask="32"` → una IP; `mask="24"` → `198.51.100.*`; `mask="30"` → 4 direcciones. La IP y la máscara pueden venir de variables con plantillas (`{kvm.ip}`), por ejemplo leídas de un KVM, para cambiar reglas **sin redesplegar**.

### `<IgnoreTrueClientIPHeader>` (nota de X)

La página de X advierte que **omitirlo o ponerlo en `false` no hace que Apigee X evalúe correctamente `True-Client-IP`**, y que para evaluar varias IPs de `X-Forwarded-For` con `<ValidateBasedOn>` hay que ponerlo en `true`. En X, si no usas `<ClientIPVariable>`, declara `<IgnoreTrueClientIPHeader>true</IgnoreTrueClientIPHeader>`.

### Interacción con Advanced API Security

Si usas *security actions* de Advanced API Security que filtran por IP, se ejecutan **antes** que AccessControl, y una no influye en la otra.

## Variables de flujo

La política no publica variables de éxito. En Analytics, la IP resuelta está en la dimensión `ax_resolved_client_ip`; `x_forwarded_for_ip` guarda la cabecera tal cual. `ax_true_client_ip` no se admite con esta política.

## Errores

### En runtime

| Código | HTTP | Causa |
|---|---|---|
| `accesscontrol.IPDeniedAccess` | 403 | La IP coincide con una regla `DENY` (o con ninguna, con `noRuleMatchAction="DENY"`). |
| `accesscontrol.InvalidIPAddressInVariable` | 500 | La variable de `<ClientIPVariable>` no contiene una IP válida. |

### Variables de fallo

| Variable | Ejemplo |
|---|---|
| `fault.name` | `fault.name = "IPDeniedAccess"` |
| `acl.{name}.failed` | `acl.AC-Socios.failed = true` |

> [!NOTE]
> La respuesta de error de ejemplo trae el `errorcode` `steps.accesscontrol.IPDeniedAccess` (con prefijo `steps.`), mientras la tabla dice `accesscontrol.IPDeniedAccess`. Y el `faultstring` incluye la IP del cliente: si no quieres revelarla, sustituye la respuesta en una FaultRule.

## Ejemplos

### 1. API de socios solo desde sus redes (X)

```xml
<AccessControl name="AC-Socios">
  <ClientIPVariable>client.resolved.ip</ClientIPVariable>
  <IPRules noRuleMatchAction="DENY">
    <MatchRule action="ALLOW">
      <SourceAddress mask="28">198.51.100.16</SourceAddress>
      <SourceAddress mask="32">192.0.2.10</SourceAddress>
    </MatchRule>
  </IPRules>
</AccessControl>
```

### 2. Red del socio leída de un KVM por app

El atributo de la app indica qué entrada del KVM usar; la red se cambia en el KVM sin redesplegar.

```xml
<AccessControl name="AC-Red-De-La-App">
  <ClientIPVariable>client.resolved.ip</ClientIPVariable>
  <IPRules noRuleMatchAction="DENY">
    <MatchRule action="ALLOW">
      <SourceAddress mask="{flujo.mascara_app}">{flujo.red_app}</SourceAddress>
    </MatchRule>
  </IPRules>
</AccessControl>
```

### 3. Respuesta 403 genérica

```xml
<FaultRule name="fr-ip-denegada">
  <Condition>fault.name = "IPDeniedAccess"</Condition>
  <Step>
    <Name>AM-Error-403</Name>
  </Step>
</FaultRule>
```

## Diferencias en Apigee Edge

| Aspecto | Apigee X / hybrid | Apigee Edge |
|---|---|---|
| `<ClientIPVariable>` / `client.resolved.ip` | Sí (recomendado) | No |
| `True-Client-IP` | Ver nota: no se evalúa bien | Se evalúa **primero** si existe; `<IgnoreTrueClientIPHeader>` (Edge ≥ 4.19.06.10) lo desactiva |
| IP de `X-Forwarded-For` por defecto | Todas (`ALL_IP`) | Solo la **última** (la del último salto TCP), salvo que la organización tenga `feature.enableMultipleXForwardCheckForACL=true` |
| `<ValidateBasedOn>` | Siempre disponible | Requiere esa propiedad de organización (en Public Cloud, además, reinicio de los MPs por soporte) |
| `X-Forwarded-For` en Private Cloud | — | ≥ 4.18.05: una sola IP; ≤ 4.18.01: la primera |
| Cloud Armor, security actions | Sí | No |

## Antipatrones

- Lista de bloqueo con `noRuleMatchAction="ALLOW"` evaluando `X-Forwarded-For`: se salta mandando basura en la cabecera.
- `X_FORWARDED_FOR_FIRST_IP` como control de seguridad.
- Ponerla después de políticas costosas.
- `continueOnError="true"`.
- Reglas en el XML que cambian a menudo (usa variables desde un KVM).

## Fuentes

- AccessControl policy — Apigee X/hybrid: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/access-control-policy> (consultada directamente, contenido completo, 2026-10-22).
- Access Control policy — Apigee Edge: <https://docs.apigee.com/api-platform/reference/policies/access-control-policy> (consultada directamente, 2026-10-22).
- Client IP resolution: <https://docs.cloud.google.com/apigee/docs/api-platform/system-administration/client-ip-resolution> (consultada directamente, 2026-10-22).
