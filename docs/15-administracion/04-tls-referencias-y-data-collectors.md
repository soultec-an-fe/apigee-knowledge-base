---
id: administracion-tls-referencias
titulo: TLS hacia backends, referencias a keystores y data collectors
area: administracion
tags: [tls, sslinfo, keystore, truststore, referencias, rotacion-certificados, enforce, data-collectors]
aplica_a: [apigee-x, apigee-hybrid]
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/system-administration/options-configuring-tls
revisado: 2026-10-23
---

# TLS hacia backends, referencias a keystores y data collectors

> **Fecha de corte: 23 de octubre de 2026.** La configuración de TLS y mTLS de entrada está en [TLS/mTLS](../03-seguridad/04-tls-mtls.md).

## `<SSLInfo>` hacia el backend

El mismo bloque `<SSLInfo>` sirve para un TargetEndpoint y para un TargetServer.

> **Apigee no admite TLS 1.0 ni TLS 1.1** en los targets.

| Elemento | Comportamiento |
|---|---|
| `<Enabled>` | Default: `true` si la URL es `https`, `false` si es `http` |
| **`<Enforce>`** | Con `true`, falla la conexión si el certificado es inválido, ha caducado, es autofirmado, no coincide con el hostname o tiene una raíz no confiable. Con `false` o sin definir, depende de `<IgnoreValidationErrors>`. |
| `<IgnoreValidationErrors>` | Ignora errores de validación. **Se ignora si `<Enforce>` es `true`.** No puede saltarse el error de un servidor con **SNI** que devuelve un DN distinto del hostname. |
| `<ClientAuthEnabled>` | mTLS hacia el backend |
| `<KeyStore>` / `<KeyAlias>` | Clave privada y certificado de cliente para el mTLS |
| `<TrustStore>` | Certificados de servidor de confianza |
| `<Ciphers>` / `<Protocols>` | Restringen las suites y los protocolos. Sin ellos, se permiten todos los que tenga la JVM. |

> [!WARNING]
> - **Sin `<Enforce>true</Enforce>`**, un backend con un certificado problemático **puede responder con éxito**: TLS sin validar no protege frente a un *man-in-the-middle*. Activa `Enforce` y configura el truststore.
> - **Contradicción sobre TLS 1.3.** Esta página dice que, sin `<Protocols>`, «se permiten todos los protocolos de la JVM». Sin embargo, el [catálogo de errores de runtime](../10-referencia/02-codigos-de-error.md#backend-y-transporte) dice, para `SslHandshakeFailed`, que sin versión declarada Apigee **no usa TLS 1.3 por defecto**. Si el backend solo acepta 1.3, declara `<Protocols><Protocol>TLSv1.3</Protocol></Protocols>`.

```xml
<HTTPTargetConnection>
  <SSLInfo>
    <Enabled>true</Enabled>
    <Enforce>true</Enforce>
    <ClientAuthEnabled>true</ClientAuthEnabled>
    <KeyStore>ref://ks-cliente-backend</KeyStore>
    <KeyAlias>cliente</KeyAlias>
    <TrustStore>ref://ts-backend</TrustStore>
    <Protocols>
      <Protocol>TLSv1.2</Protocol>
      <Protocol>TLSv1.3</Protocol>
    </Protocols>
  </SSLInfo>
  <URL>https://backend.ejemplo.com/v1</URL>
</HTTPTargetConnection>
```

## Referencias (`ref://`)

Una **referencia** es una variable con el **nombre** del keystore o del truststore. Usarla en lugar del nombre directo permite **rotar certificados sin redesplegar**:

1. Crea un keystore nuevo con el certificado nuevo, **con el mismo alias**.
2. Actualiza la referencia para que apunte al keystore nuevo.

Las referencias se crean por entorno, en *Management > Environments > References*, o con la API.

**Restricciones:**

- Solo hay referencias para **keystores y truststores**, **no para el alias**. Por eso el alias debe ser el mismo en el keystore viejo y en el nuevo.
- Si el **TLS termina en un balanceador**, no se pueden usar referencias en el TargetServer.

## Data collectors

Un **data collector** es el recurso que define una dimensión o métrica personalizada de Analytics. Los valores los rellena la política [DataCapture](../02-politicas/referencia/data-capture.md).

- **Nombre:** con el prefijo **`dc_`** obligatorio.
- **Tipo:** `Integer`, `String`, etc.
- **Descripción.**

> [!CAUTION]
> - No crees dos data collectors que solo se diferencien en mayúsculas (`dc_mi_dato` y `dc_Mi_Dato`): la exportación de datos falla con *duplicate column names*.
> - Si varias políticas DataCapture escriben el mismo collector, **gana la última que se ejecuta**.

## Fuentes

Todas consultadas directamente el 2026-10-23:

- Options for configuring TLS: <https://docs.cloud.google.com/apigee/docs/api-platform/system-administration/options-configuring-tls>, contenido completo.
- Working with references: <https://docs.cloud.google.com/apigee/docs/api-platform/system-administration/working-references>, contenido completo.
- Data collectors: <https://docs.cloud.google.com/apigee/docs/api-platform/system-administration/data-collectors>, contenido completo.
- Runtime error catalog (`SslHandshakeFailed`): <https://docs.cloud.google.com/apigee/docs/api-platform/errorcatalog/mp-runtime-errorcatalog>.
