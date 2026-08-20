---
id: seguridad-tls-mtls
titulo: TLS, mTLS y keystores
area: seguridad
tags: [tls, mtls, keystore, truststore, certificados, ssl]
aplica_a: [apigee-x, apigee-hybrid]
fuente: https://cloud.google.com/apigee/docs/api-platform/system-administration/keystores-truststores
revisado: 2026-08-20
---

# TLS, mTLS y keystores

## Dos lados independientes

```
Cliente  ══TLS northbound══►  Apigee  ══TLS southbound══►  Backend
         (Cloud Load Balancer)        (SSLInfo del TargetEndpoint)
```

| Lado | Dónde se configura | Qué protege |
|---|---|---|
| **Northbound** (cliente → Apigee) | Cloud Load Balancer + certificado del environment group | El tráfico público |
| **Southbound** (Apigee → backend) | `<SSLInfo>` en `<HTTPTargetConnection>` o en el TargetServer | El tráfico interno |

Se configuran por separado y pueden tener políticas distintas.

## Keystore vs Truststore

| | Contiene | Sirve para |
|---|---|---|
| **Keystore** | Certificado **+ clave privada** | Presentar **tu** identidad (mTLS como cliente, o TLS como servidor) |
| **Truststore** | Certificados de CA (**sin** clave privada) | Verificar la identidad **del otro** |

Límites: **100 keystores** y **1.000 truststores** por entorno.

## TLS southbound — validar el certificado del backend

```xml
<HTTPTargetConnection>
    <LoadBalancer>
        <Server name="pedidos-svc"/>
    </LoadBalancer>
    <Path>/api</Path>
    <SSLInfo>
        <Enabled>true</Enabled>
        <Enforce>true</Enforce>
        <TrustStore>truststore-backends</TrustStore>
        <IgnoreValidationErrors>false</IgnoreValidationErrors>
        <Protocols>
            <Protocol>TLSv1.2</Protocol>
            <Protocol>TLSv1.3</Protocol>
        </Protocols>
        <Ciphers>
            <Cipher>TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384</Cipher>
            <Cipher>TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256</Cipher>
        </Ciphers>
    </SSLInfo>
</HTTPTargetConnection>
```

> [!CAUTION]
> **`<IgnoreValidationErrors>true</IgnoreValidationErrors>` es una vulnerabilidad, no una opción de configuración.**
> Desactiva la validación del certificado del backend: cualquier atacante en la red puede hacerse pasar por tu backend y leer o modificar el tráfico. Si un certificado interno no valida, la solución es **añadir su CA al truststore**, no ignorar el error.

### Validar el Common Name

```xml
<SSLInfo>
    <Enabled>true</Enabled>
    <Enforce>true</Enforce>
    <TrustStore>truststore-backends</TrustStore>
</SSLInfo>
```

Y en el flujo:

```xml
<AssignMessage name="AM-EsperarCN">
    <AssignVariable>
        <Name>target.expectedcn</Name>
        <Value>pedidos.interno.example.com</Value>
    </AssignVariable>
</AssignMessage>
```

Tras la conexión, `target.cn` contiene el CN real del certificado presentado.

## mTLS southbound — Apigee se autentica ante el backend

```xml
<SSLInfo>
    <Enabled>true</Enabled>
    <Enforce>true</Enforce>
    <ClientAuthEnabled>true</ClientAuthEnabled>
    <KeyStore>keystore-apigee-cliente</KeyStore>
    <KeyAlias>apigee-client-2026</KeyAlias>
    <TrustStore>truststore-backends</TrustStore>
    <IgnoreValidationErrors>false</IgnoreValidationErrors>
</SSLInfo>
```

Apigee presenta el certificado del alias `apigee-client-2026` del keystore. El backend lo valida contra su propia CA.

## mTLS northbound — el cliente se autentica ante Apigee

Se configura en el **Cloud Load Balancer**, no en el proxy. El balanceador valida el certificado del cliente y propaga la información a Apigee, donde queda disponible en variables:

```
client.cn
client.organization
client.organization.unit
client.country
client.locality
client.state
client.email.address
client.ssl.enabled
```

Autorización por certificado:

```xml
<Step>
    <Name>RF-CertificadoNoAutorizado</Name>
    <Condition>!(client.cn Like "*.socios.empresa.com")</Condition>
</Step>
```

> [!IMPORTANT]
> No confíes solo en el CN. Valida también la **CA emisora** y considera una lista de permitidos explícita de fingerprints o CNs almacenada en un KVM. Un CN se puede replicar; lo que no se puede es firmar con tu CA.

## Crear keystores y truststores

```bash
# Crear un keystore
apigeecli keystores create --name keystore-apigee-cliente \
  --org "$ORG" --env prod --token "$(gcloud auth print-access-token)"

# Subir cert + clave privada como alias
apigeecli keyaliases create --keystore keystore-apigee-cliente \
  --name apigee-client-2026 --format keycertfile \
  --cert-file ./cliente.crt --key-file ./cliente.key \
  --org "$ORG" --env prod --token "$(gcloud auth print-access-token)"

# Crear un truststore (misma API, sin clave privada)
apigeecli keystores create --name truststore-backends \
  --org "$ORG" --env prod --token "$(gcloud auth print-access-token)"

apigeecli keyaliases create --keystore truststore-backends \
  --name ca-interna --format keycertfile --cert-file ./ca.crt \
  --org "$ORG" --env prod --token "$(gcloud auth print-access-token)"
```

## Rotación de certificados sin corte

El patrón que evita el incidente clásico:

```
1. Añadir el alias NUEVO al keystore (el viejo sigue ahí)
2. Añadir la CA nueva al truststore del backend
3. Cambiar <KeyAlias> del TargetEndpoint al alias nuevo y desplegar
4. Verificar tráfico con el certificado nuevo
5. Eliminar el alias antiguo
```

> [!WARNING]
> **La expiración de certificados es la causa número uno de incidentes en integraciones mTLS.** Monitoriza las fechas de expiración de todos los aliases y alerta con 30 días de antelación. Apigee no te avisa por sí solo.

## TLS northbound — certificado del hostname

En Apigee X el certificado público lo gestiona el **Cloud Load Balancer**:

| Opción | Cuándo |
|---|---|
| **Google-managed certificate** | Lo habitual: Google renueva automáticamente |
| **Self-managed certificate** | Cuando necesitas una CA concreta o un certificado EV |
| **Certificate Manager** | Para muchos dominios o wildcards gestionados centralmente |

El hostname debe estar declarado en el **environment group**. Ver [organizaciones y entornos](../00-fundamentos/04-organizaciones-entornos-grupos.md).

## Límites relacionados

| Límite | Valor |
|---|---|
| Keystores por entorno | 100 |
| Truststores por entorno | 1.000 |
| Tamaño del mensaje de handshake TLS | 128 KB |
| Hostnames por environment group | 100 |

## Checklist de TLS en producción

- [ ] `<IgnoreValidationErrors>` está en `false` en **todos** los TargetEndpoints
- [ ] `<Enforce>true</Enforce>` está activo
- [ ] Solo se aceptan `TLSv1.2` y `TLSv1.3`
- [ ] La lista de ciphers excluye suites débiles
- [ ] Existe un truststore explícito, no se confía en el conjunto por defecto
- [ ] Todos los aliases tienen `kid`/nombre versionado por fecha
- [ ] Hay alertas de expiración configuradas a 30 días
- [ ] Las claves privadas viven en keystores o KVM cifrado, **nunca** en el bundle

## Fuentes

- <https://cloud.google.com/apigee/docs/api-platform/system-administration/keystores-truststores>
- <https://cloud.google.com/apigee/docs/api-platform/system-administration/tls-northbound>
- <https://cloud.google.com/apigee/docs/api-platform/reference/limits>
