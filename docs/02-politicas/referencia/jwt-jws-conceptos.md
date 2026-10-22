---
id: referencia-jwt-jws-conceptos
titulo: JWT y JWS en Apigee — algoritmos, claves y JWKS
area: politicas
tags: [jwt, jws, jwe, jwks, rs256, es256, ps256, hs256, rfc7519, rfc7515, rfc7518, claves]
aplica_a: [apigee-x, apigee-hybrid, apigee-edge]
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/jwt-policies-overview
fuente_edge: https://docs.apigee.com/api-platform/reference/policies/jwt-policies-overview
revisado: 2026-10-22
---

# JWT y JWS en Apigee — algoritmos, claves y JWKS

> [!NOTE]
> Base común de las seis políticas: [GenerateJWT](generate-jwt.md), [VerifyJWT](verify-jwt.md), [DecodeJWT](decode-jwt.md), [GenerateJWS](generate-jws.md), [VerifyJWS](verify-jws.md) y [DecodeJWS](decode-jws.md). Para la visión de seguridad de conjunto ver [JWT y JWS](../../03-seguridad/03-jwt-jws.md).

## Qué hace cada política

| Política | Firmado | Cifrado (JWE) | Verifica firma | Lee |
|---|---|---|---|---|
| GenerateJWT | Sí | Sí (solo X/hybrid) | — | — |
| VerifyJWT | Sí | Sí, descifra (solo X/hybrid) | Sí | Cabecera y claims |
| DecodeJWT | — | Solo la cabecera sin cifrar | **No** | Cabecera y claims |
| GenerateJWS | Sí | No | — | — |
| VerifyJWS | Sí | No | Sí | Cabecera y payload |
| DecodeJWS | — | No | **No** | Solo la cabecera |

**Decode no valida nada.** Sirve para leer un dato (p. ej. el `kid` o el `iss`) antes de verificar, nunca para autorizar.

## JWT frente a JWS

| | JWT (RFC 7519) | JWS (RFC 7515) |
|---|---|---|
| Payload | Siempre un objeto JSON | Cualquier formato (JSON, bytes, texto) |
| Payload adjunto | Siempre | Opcional: admite **payload separado** (`Header..Signature`) |
| `typ` | `JWT` | Libre |
| Claims registrados (`iss`, `sub`, `aud`, `exp`…) | Elementos propios en Generate y Verify | No existe el concepto: el payload es opaco |
| Claims propios | En payload y cabecera | Solo en la cabecera |
| Cifrado | Sí (JWE, 5 partes) | No |
| Serialización | Compacta (JWS o JWE) | **Solo compacta**; la serialización JSON de JWS no está soportada |

El JWS con **payload separado** (*detached*) se usa en estándares de firma de mensajes, por ejemplo la firma de peticiones en algunos perfiles de Open Banking: la firma viaja en una cabecera y el cuerpo HTTP es el payload.

Formatos:

```text
JWT/JWS firmado:  Cabecera.Payload.Firma
JWS separado:     Cabecera..Firma
JWT cifrado:      Cabecera.ClaveCifrada.VectorInicializacion.TextoCifrado.EtiquetaAutenticacion
```

## Firmar o cifrar

- **Firmar** garantiza integridad y no repudio: cualquiera puede leer el payload, pero nadie puede alterarlo sin la clave.
- **Cifrar** garantiza confidencialidad: solo quien tiene la clave lo lee.
- Con cifrado asimétrico (RSA, ECDH), la clave de cifrado es **pública**, así que no prueba quién lo generó. Para tener ambas garantías: **firmar primero y cifrar el resultado** (JWT firmado dentro de un JWT cifrado). Las políticas de Apigee pueden producir y verificar esa combinación.

## Algoritmos de firma

| Familia | Algoritmos | Clave para firmar | Clave para verificar | Requisitos |
|---|---|---|---|---|
| HMAC | `HS256`, `HS384`, `HS512` | Secreto compartido | El mismo secreto | Mínimo **32 / 48 / 64 bytes** respectivamente; si no, error en runtime |
| RSA PKCS#1 v1.5 | `RS256`, `RS384`, `RS512` | Privada RSA | Pública RSA | Sin tamaño mínimo impuesto por Apigee |
| RSASSA-PSS | `PS256`, `PS384`, `PS512` | Privada RSA | Pública RSA | Mismas claves que RS* |
| ECDSA | `ES256`, `ES384`, `ES512` | Privada EC | Pública EC | Curva **P-256**, **P-384** y **P-521** respectivamente |

> [!WARNING]
> Que Apigee no imponga tamaño mínimo a las claves RSA no significa que cualquier tamaño sea seguro. Usa al menos 2048 bits (3072 recomendado). Esta recomendación no es de la documentación de Apigee sino de las guías criptográficas habituales (p. ej. NIST SP 800-57).

En VerifyJWT/VerifyJWS se pueden aceptar **varios algoritmos** separados por comas (`RS256, PS256`), pero no mezclar HS* con otras familias ni ES* con otras familias, porque cada una usa un tipo de clave distinto. RS* y PS* sí se combinan.

## Algoritmos de cifrado (JWE, solo X/hybrid)

| Cifrado de la clave (`<Key>`) | Elemento de clave al generar | Al verificar |
|---|---|---|
| `dir` | `<DirectKey>` | `<DirectKey>` |
| `RSA-OAEP-256` | `<PublicKey>` (RSA) | `<PrivateKey>` (RSA) |
| `ECDH-ES`, `ECDH-ES+A128KW`, `+A192KW`, `+A256KW` | `<PublicKey>` (EC) | `<PrivateKey>` (EC) |
| `A128KW`, `A192KW`, `A256KW`, `A128GCMKW`, `A192GCMKW`, `A256GCMKW` | `<SecretKey>` | `<SecretKey>` |
| `PBES2-HS256+A128KW`, `PBES2-HS384+A192KW`, `PBES2-HS512+A256KW` | `<PasswordKey>` | `<PasswordKey>` |

Cifrado del contenido (`<Content>`): `A128CBC-HS256`, `A192CBC-HS384`, `A256CBC-HS512`, `A128GCM`, `A192GCM`, `A256GCM`. Con `dir`, la clave que das **es** la de cifrado de contenido y debe tener exactamente la longitud del algoritmo: 32, 48 o 64 bytes para los CBC-HS, y 16, 24 o 32 bytes para los GCM.

## Formatos de clave

| Formato | Uso | Notas |
|---|---|---|
| **PEM** (RFC 7468) | Claves públicas, privadas (también privadas cifradas con contraseña) y certificados X.509 | Alinea el contenido a la izquierda si lo pones literal en el XML |
| **JWKS** (RFC 7517) | Conjunto de claves públicas, normalmente publicado en una URL | Cada JWK debe tener `kty` y `kid`; `alg` y `use` son opcionales pero recomendables |
| Secreto | HS* y AES | UTF-8 por defecto; en X/hybrid, atributo `encoding` con `hex`/`base16`, `base64` o `base64url` |

> [!IMPORTANT]
> **Certificados:** cuando la clave pública sale de un `<Certificate>`, Apigee **no comprueba** la cadena de confianza ni las fechas de validez del certificado: usa la clave tal cual. Si necesitas validar la cadena, hazlo aparte.

### Reglas para guardar claves

- Las variables con material secreto (secretos HMAC, claves privadas, contraseñas de claves) **deben empezar por `private.`**; si no, el despliegue falla. Las contraseñas de claves privadas no se pueden escribir en texto plano en la política.
- Guárdalas en un KVM cifrado con alcance de entorno. Las públicas pueden ir en un PropertySet.

## JWKS como fuente de claves

Al **verificar** con `<PublicKey><JWKS …/></PublicKey>`, Apigee:

1. comprueba que el `alg` de la cabecera esté entre los permitidos por la política;
2. obtiene el JWKS (de la caché si ya lo tiene);
3. busca el `kid` de la cabecera; **si el token no trae `kid`, falla** (`KeyIdMissing`);
4. toma el JWK con ese `kid`; si no existe, falla (`NoMatchingPublicKey`);
5. comprueba que el algoritmo del JWK coincide con el de la política;
6. verifica la firma.

| Forma | Ejemplo | Cuándo |
|---|---|---|
| URI fija | `<JWKS uri="https://idp.example.com/.well-known/jwks.json"/>` | Lo habitual con un proveedor de identidad. |
| URI en variable (solo X/hybrid) | `<JWKS uriRef="flujo.jwks_uri"/>` | Varios emisores de confianza. |
| Contenido en variable | `<JWKS ref="flujo.jwks"/>` | JWKS cargado de un KVM, PropertySet o ServiceCallout (cachéalo). |
| Literal | `<JWKS>{"keys":[…]}</JWKS>` | Pruebas. |

El JWKS obtenido por URL se **cachea 300 segundos** (5 minutos). Tras rotar claves en el proveedor, Apigee puede tardar hasta ese tiempo en ver la nueva.

> [!CAUTION]
> Con `uriRef`, **nunca** tomes la URL del propio token (cabeceras `jku`/`x5u`) sin compararla antes con una lista de emisores de confianza: un atacante firmaría con su clave y apuntaría a su propio JWKS.

En Edge for Private Cloud, si el endpoint JWKS exige SNI, hay que activar SNI en los message processors (no viene activado por defecto).

## Inyección de plantillas

GenerateJWT y GenerateJWS aplican **plantillas de mensaje** en algunos casos (por ejemplo, `<Claim … type="map">`). Si el valor viene de la petición, un atacante puede mandar algo como `{private.secret}` y hacer que el claim incluya un secreto del contexto.

- No uses entradas no confiables (`request.header.*`, `request.queryparam.*`…) directamente en un `ref` que admita plantillas.
- Si no queda más remedio, limpia antes las llaves `{ }` con AssignMessage o JavaScript.
- Para claims de texto simples usa el `type="string"` por defecto, no `map`.
- Ojo con la asimetría: las políticas **Verify** no aplican plantillas al resolver `ref`; las **Generate**, sí en ciertas configuraciones.

## Variables de fallo comunes

Todas las políticas JWT ponen `JWT.failed = true` al fallar (las JWS, `JWS.failed`). Captura por `fault.name` (p. ej. `TokenExpired`) o por el `errorcode`, nunca por `faultstring`. Casi todos los errores JWT devuelven **401**, incluso los de **generación**: si un GenerateJWT falla por configuración, el cliente recibe un 401 que no es culpa suya. Corrígelo en la FaultRule.

## Diferencias en Apigee Edge

| Aspecto | Apigee X / hybrid | Apigee Edge |
|---|---|---|
| JWT cifrado (JWE) | Sí | No |
| Algoritmos de firma | HS, RS, PS, ES | HS, RS, PS, ES |
| `uriRef` en JWKS | Sí | No |
| Atributo `encoding` en `<SecretKey>` | Generate y Verify | Solo documentado en VerifyJWT |
| Advertencia de inyección de plantillas | Sí | Sí |

## Fuentes

- JWS and JWT policies overview — Apigee X/hybrid: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/jwt-policies-overview> (consultada directamente, contenido completo, 2026-10-22).
- JWS and JWT policies overview — Apigee Edge: <https://docs.apigee.com/api-platform/reference/policies/jwt-policies-overview> (consultada directamente, 2026-10-22).
- RFC 7515 (JWS), RFC 7516 (JWE), RFC 7517 (JWK), RFC 7518 (JWA), RFC 7519 (JWT): <https://www.rfc-editor.org/>
