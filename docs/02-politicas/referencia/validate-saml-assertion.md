---
id: politica-validate-saml-assertion
titulo: ValidateSAMLAssertion — referencia completa
area: politicas
tags: [validatesamlassertion, saml, soap, ws-security, truststore, firma-xml, extensible]
aplica_a: [apigee-x, apigee-hybrid, apigee-edge]
elemento_xml: ValidateSAMLAssertion
tipo_politica: extensible
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/validate-saml-assertion-policy
fuente_edge: https://docs.apigee.com/api-platform/reference/policies/saml-assertion-policy
revisado: 2026-10-22
---

# ValidateSAMLAssertion — referencia completa

> [!NOTE]
> **Tipo:** Extensible. **Elemento raíz:** `<ValidateSAMLAssertion>`.
> **Aplica a:** Apigee X, hybrid y Edge (en Edge, en la página conjunta "SAML Assertion policies").

ValidateSAMLAssertion hace que Apigee actúe como **proveedor de servicio**: valida una aserción SAML 2.0 **firmada** que llega en una petición SOAP entrante (normalmente en `wsse:Security`), comprueba la firma contra un **truststore** y la validez temporal, y publica el emisor, el sujeto y otros datos en variables. Si algo falla, rechaza la petición.

## Sintaxis completa

```xml
<ValidateSAMLAssertion name="VSA-Nombre" ignoreContentType="false" continueOnError="false" enabled="true">
  <Source name="request">
    <Namespaces>
      <Namespace prefix="soap">http://schemas.xmlsoap.org/soap/envelope/</Namespace>
      <Namespace prefix="wsse">http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd</Namespace>
      <Namespace prefix="saml">urn:oasis:names:tc:SAML:2.0:assertion</Namespace>
    </Namespaces>
    <AssertionXPath>/soap:Envelope/soap:Header/wsse:Security/saml:Assertion</AssertionXPath>
    <SignedElementXPath>/soap:Envelope/soap:Header/wsse:Security/saml:Assertion</SignedElementXPath>
  </Source>
  <TrustStore>ts-idp-corporativo</TrustStore>
  <RemoveAssertion>true</RemoveAssertion>
</ValidateSAMLAssertion>
```

## Atributos del elemento raíz

| Atributo | Obligatorio | Default | Qué hace |
|---|---|---|---|
| `name` | Sí | — | Nombre interno; caracteres permitidos `A-Z0-9._\-$ %`. |
| `ignoreContentType` | No | `false` | Con `false`, un `Content-Type` que no sea XML hace fallar la validación. |
| `continueOnError` | No | `false` | No lo pongas en `true` en una política de autenticación. |
| `enabled` | No | `true` | Con `false` no se ejecuta. |

## Elementos hijos

| Elemento | Obligatorio | Resumen |
|---|---|---|
| `<Source name>` | **Sí** | Mensaje a validar: `request`, `response` o `message`. |
| `<Source>/<Namespaces>/<Namespace prefix>` | Sí | Prefijos usados en las XPath. |
| `<Source>/<AssertionXPath>` | **Sí** | XPath de la aserción. |
| `<Source>/<SignedElementXPath>` | **Sí** | XPath del elemento **firmado** (la propia aserción o un ancestro). |
| `<Source>/<XPath>` | — | **Obsoleto**; usa los dos anteriores. |
| `<TrustStore>` | **Sí** | Truststore con los certificados X.509 de confianza. Vacío → `TrustStoreNotConfigured`. |
| `<RemoveAssertion>` | No | Con `true`, se quita la aserción del mensaje antes de enviarlo al backend. |

## Qué comprueba, en orden

1. Que el `Content-Type` sea XML: coincide con `text/(.*+)?xml` o `application/(.*+)?xml` (salvo `ignoreContentType="true"`).
2. Que el XML se pueda parsear.
3. Que existan el elemento firmado y la aserción en sus XPath.
4. Que la aserción **sea** el elemento firmado o **esté dentro** de él. Esto evita ataques de envoltura de firma (*XML signature wrapping*), en los que se firma un elemento y se coloca otra aserción falsa en el mensaje.
5. Si hay `NotBefore` / `NotOnOrAfter`, que la hora actual esté dentro (SAML Core §2.5.1), y el resto de reglas de `Conditions` (§2.5.1.1).
6. Que la firma XML sea válida con el truststore.

Si todo pasa, el proxy sabe que la firma es válida y de una CA de confianza, y que la aserción está vigente.

> [!IMPORTANT]
> La política **no** comprueba que el **emisor** sea el que esperas, ni que la **audiencia** (`AudienceRestriction`) sea tu servicio, ni quién es el sujeto. Cualquier aserción firmada por un certificado del truststore pasa. Comprueba después `saml.issuer` (y la audiencia, extrayéndola con ExtractVariables) con una condición. Mantén el truststore con **solo** los certificados del IdP que corresponde a este proxy.

## Variables de flujo

| Variable | Contenido |
|---|---|
| `saml.valid` | `true` o `false` |
| `saml.id` | ID de la aserción |
| `saml.issuer` | Emisor |
| `saml.subject` | Sujeto |
| `saml.subjectFormat` | Formato del sujeto |
| `saml.issueInstant` | Momento de emisión |
| `saml.scmethod` | Método de confirmación del sujeto |
| `saml.scdaddress`, `saml.scdinresponse`, `saml.scdrcpt` | Datos de confirmación del sujeto: dirección, `InResponseTo`, destinatario |
| `saml.authnInstant`, `saml.authnSessionIndex`, `saml.authnSnooa`, `saml.authnContextClassRef` | Datos del `AuthnStatement` |

Para otros atributos de la aserción, usa ExtractVariables con XPath sobre el mensaje.

## Errores

### En runtime

La página no publica tabla de errores de runtime; comparte con GenerateSAMLAssertion el ejemplo `InvalidMediaTpe`.

### Al desplegar

| Error | Causa |
|---|---|
| `SourceNotConfigured` | Falta o está vacío `<Source>`, `<XPath>`, `<Namespaces>` o `<Namespace>`. |
| `TrustStoreNotConfigured` | Falta o está vacío `<TrustStore>`. |

### Variables de fallo

| Variable | Ejemplo |
|---|---|
| `fault.name` | Nombre del fallo |
| `ValidateSAMLAssertion.failed` | `ValidateSAMLAssertion.failed = true` (la tabla oficial muestra `GenerateSAMLAssertion.failed` y aclara que para esta política el prefijo es `ValidateSAMLAssertion`) |

## Ejemplo: SOAP con aserción de un IdP corporativo

```xml
<ValidateSAMLAssertion name="VSA-IdP">
  <Source name="request">
    <Namespaces>
      <Namespace prefix="soap">http://schemas.xmlsoap.org/soap/envelope/</Namespace>
      <Namespace prefix="wsse">http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd</Namespace>
      <Namespace prefix="saml">urn:oasis:names:tc:SAML:2.0:assertion</Namespace>
    </Namespaces>
    <AssertionXPath>/soap:Envelope/soap:Header/wsse:Security/saml:Assertion</AssertionXPath>
    <SignedElementXPath>/soap:Envelope/soap:Header/wsse:Security/saml:Assertion</SignedElementXPath>
  </Source>
  <TrustStore>ts-idp-corporativo</TrustStore>
  <RemoveAssertion>true</RemoveAssertion>
</ValidateSAMLAssertion>
```

```xml
<Step>
  <Name>RF-Emisor-SAML-No-Esperado</Name>
  <Condition>saml.issuer != "https://idp.corporativo.ejemplo.com"</Condition>
</Step>
```

## Diferencias en Apigee Edge

Mismos elementos, variables y errores; documentación en la página conjunta de Edge.

## Antipatrones

- No comprobar `saml.issuer` ni la audiencia.
- Truststores compartidos entre proxies con certificados de varios IdP.
- `ignoreContentType="true"` sin necesidad.
- `<SignedElementXPath>` que apunta a un elemento no relacionado con la aserción.

## Fuentes

- ValidateSAMLAssertion policy — Apigee X/hybrid: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/validate-saml-assertion-policy> (consultada directamente, contenido completo, 2026-10-22).
- SAML policies overview: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/saml-assertion-policies-overview> (consultada directamente, 2026-10-22).
- SAML Assertion policies — Apigee Edge: <https://docs.apigee.com/api-platform/reference/policies/saml-assertion-policy> (consultada directamente, 2026-10-22).
