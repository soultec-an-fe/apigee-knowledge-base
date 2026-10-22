---
id: politica-generate-saml-assertion
titulo: GenerateSAMLAssertion — referencia completa
area: politicas
tags: [generatesamlassertion, saml, soap, ws-security, keystore, firma-xml, extensible]
aplica_a: [apigee-x, apigee-hybrid, apigee-edge]
elemento_xml: GenerateSAMLAssertion
tipo_politica: extensible
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/generate-saml-assertion-policy
fuente_edge: https://docs.apigee.com/api-platform/reference/policies/saml-assertion-policy
revisado: 2026-10-22
---

# GenerateSAMLAssertion — referencia completa

> [!NOTE]
> **Tipo:** Extensible. **Elemento raíz:** `<GenerateSAMLAssertion>`.
> **Aplica a:** Apigee X, hybrid y Edge. En Edge, esta política y [ValidateSAMLAssertion](validate-saml-assertion.md) se documentan juntas en la página "SAML Assertion policies".

GenerateSAMLAssertion hace que Apigee actúe como **proveedor de identidad**: genera una aserción SAML 2.0, la **firma** con una clave de un keystore y la inserta en un mensaje XML saliente (normalmente la cabecera `wsse:Security` de un SOAP hacia el backend) o la deja en una variable. El backend la usa para autenticar y autorizar.

Soporta SAML Core 2.0 y el perfil de token SAML de WS-Security 1.0.

## Sintaxis completa

```xml
<GenerateSAMLAssertion name="GSA-Nombre" ignoreContentType="false" continueOnError="false" enabled="true">
  <Issuer ref="variable.emisor">https://gateway.ejemplo.com</Issuer>
  <Subject ref="variable.sujeto">usuario@ejemplo.com</Subject>
  <KeyStore>
    <Name ref="variable.keystore">ks-saml</Name>
    <Alias ref="variable.alias">firma-saml</Alias>
  </KeyStore>
  <SignatureAlgorithm>SHA256</SignatureAlgorithm>
  <CanonicalizationAlgorithm/>
  <OutputVariable>
    <Message name="request">
      <Namespaces>
        <Namespace prefix="soap">http://schemas.xmlsoap.org/soap/envelope/</Namespace>
        <Namespace prefix="wsse">http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd</Namespace>
      </Namespaces>
      <XPath>/soap:Envelope/soap:Header/wsse:Security</XPath>
    </Message>
    <!-- o bien: <FlowVariable>flujo.asercion</FlowVariable> -->
  </OutputVariable>
  <Template ignoreUnresolvedVariables="false"><![CDATA[ … aserción con {variables} … ]]></Template>
</GenerateSAMLAssertion>
```

## Atributos del elemento raíz

| Atributo | Obligatorio | Default | Qué hace |
|---|---|---|---|
| `name` | Sí | — | Nombre interno. |
| `ignoreContentType` | No | `false` | Con `false`, si el mensaje no tiene un `Content-Type` XML, **no se genera** la aserción y la política falla. Con `true`, se trata como XML sea cual sea la cabecera. |
| `continueOnError` | No | `false` | Con `true`, el flujo sigue aunque falle. |
| `enabled` | No | `true` | Con `false` no se ejecuta. |
| `async` | No | `false` | **Obsoleto.** |

## Elementos hijos

| Elemento | Obligatorio | Resumen |
|---|---|---|
| `<Issuer ref>` | **Sí** | Identificador del proveedor de identidad (Apigee). Literal o `ref`. Vacío → `NullIssuer` al desplegar. |
| `<Subject ref>` | Sí (sin `<Template>`) | Identificador del sujeto (el usuario o sistema). Literal o `ref`. |
| `<KeyStore>/<Name>` y `<Alias>` | **Sí** | Keystore y alias de la clave privada que firma. Ambos admiten `ref`. Vacíos → `NullKeyStore`, `NullKeyStoreAlias`. |
| `<SignatureAlgorithm>` | No | `SHA1` o `SHA256`. Usa **`SHA256`**. |
| `<CanonicalizationAlgorithm>` | No | Aparece en la plantilla; la página no lo describe. |
| `<OutputVariable>/<Message name>` + `<XPath>` | Uno de los dos | Inserta la aserción en el elemento del mensaje (`request`, `response` o `message`) indicado por la XPath. Los prefijos se declaran en `<Namespaces>`. |
| `<OutputVariable>/<FlowVariable>` | Uno de los dos | Deja la aserción en una variable, sin tocar ningún mensaje. |
| `<Template ignoreUnresolvedVariables>` | No | Aserción completa como plantilla (en `CDATA`) con `{variables}`; se procesa como en AssignMessage y después se firma. |

### Con y sin `<Template>`

| Caso | Resultado |
|---|---|
| Sin `<Template>` | Apigee construye una aserción con `Subject` e `Issuer`. |
| Con `<Template>` | Se sustituyen las `{variables}`, se firma el resultado. Si falta una variable y `ignoreUnresolvedVariables` no está en `true`, la política falla. |

> [!CAUTION]
> Como en GenerateJWT/GenerateJWS, no metas en la plantilla variables con datos que controla el cliente sin limpiarlas: una aserción firmada por el gateway con datos inyectados es una aserción **en la que el backend confiará**. Ver [Inyección de plantillas](jwt-jws-conceptos.md#inyección-de-plantillas).

### Claves y keystore

La clave privada y su certificado viven en un **keystore** del entorno (no en el proxy). El backend debe confiar en ese certificado. Planifica la rotación: el alias puede tomarse de una variable para cambiarlo sin redesplegar.

## Flujo de procesamiento

1. Si el mensaje no es XML y `ignoreContentType` no es `true` → error.
2. Si hay `<Template>`, se procesa (como AssignMessage).
3. Si no, se construye la aserción con `Subject` e `Issuer`.
4. Se firma con la clave del keystore.
5. Se inserta en la XPath indicada (o se guarda en la variable).

## Variables de flujo

No publica variables de éxito, salvo la aserción en `<FlowVariable>` si se usa.

## Errores

### En runtime

La página no tiene tabla de errores de runtime. Su ejemplo de respuesta muestra `steps.saml.generate.InvalidMediaTpe` (así, con la errata), que se produce cuando el mensaje no es XML.

### Al desplegar

| Error | Causa |
|---|---|
| `NullIssuer` | `<Issuer>` vacío o ausente. |
| `NullKeyStore` | `<KeyStore>/<Name>` vacío o ausente. |
| `NullKeyStoreAlias` | `<KeyStore>/<Alias>` vacío o ausente. |

La tabla oficial lista además `SourceNotConfigured` y `TrustStoreNotConfigured`, que son de ValidateSAMLAssertion: la página de cada política comparte la misma tabla.

### Variables de fallo

| Variable | Ejemplo |
|---|---|
| `fault.name` | `fault.name = "InvalidMediaTpe"` |
| `GenerateSAMLAssertion.failed` | `GenerateSAMLAssertion.failed = true` |

## Ejemplo: aserción hacia un backend SOAP heredado

```xml
<GenerateSAMLAssertion name="GSA-Backend-Soap">
  <Issuer>https://gateway.ejemplo.com</Issuer>
  <Subject ref="flujo.usuario_autenticado"/>
  <KeyStore>
    <Name>ks-saml</Name>
    <Alias ref="propertyset.saml.alias_activo"/>
  </KeyStore>
  <SignatureAlgorithm>SHA256</SignatureAlgorithm>
  <OutputVariable>
    <Message name="request">
      <Namespaces>
        <Namespace prefix="soap">http://schemas.xmlsoap.org/soap/envelope/</Namespace>
        <Namespace prefix="wsse">http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd</Namespace>
      </Namespaces>
      <XPath>/soap:Envelope/soap:Header/wsse:Security</XPath>
    </Message>
  </OutputVariable>
</GenerateSAMLAssertion>
```

La petición debe tener ya la cabecera `wsse:Security` (añádela antes con AssignMessage si el cliente no la manda) y `flujo.usuario_autenticado` debe venir de una verificación previa (OAuth, JWT…).

## Diferencias en Apigee Edge

Mismos elementos y comportamiento; en Edge la documentación está en la página conjunta "SAML Assertion policies".

## Antipatrones

- `SignatureAlgorithm` `SHA1`.
- Plantillas con datos del cliente sin limpiar.
- Sujeto tomado de una cabecera del cliente en lugar de una identidad ya verificada.

## Fuentes

- GenerateSAMLAssertion policy — Apigee X/hybrid: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/generate-saml-assertion-policy> (consultada directamente, contenido completo, 2026-10-22).
- SAML policies overview: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/saml-assertion-policies-overview> (consultada directamente, 2026-10-22).
- SAML Assertion policies — Apigee Edge: <https://docs.apigee.com/api-platform/reference/policies/saml-assertion-policy> (consultada directamente, 2026-10-22).
