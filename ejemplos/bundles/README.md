---
id: ejemplos-bundles
titulo: Bundles propios validados
area: ejemplos
tags: [bundles, apiproxy, sharedflow, apigeelint, validacion, ejemplos]
aplica_a: [apigee-x, apigee-hybrid]
fuente: https://github.com/apigee/apigeelint
revisado: 2026-10-23
---

# Bundles propios validados

> **Fecha de corte: 23 de octubre de 2026.** Bundles escritos para este repositorio y alineados con la [referencia de políticas](../../docs/02-politicas/referencia/00-indice.md). Licencia del repo: CC BY 4.0.

| Bundle | Tipo | Qué muestra | Políticas |
|---|---|---|---|
| [kb-api-key-cuota](kb-api-key-cuota/README.md) | Proxy | API key en cabecera, escudo de picos, cuota del API product, cabeceras de consumo y errores JSON por familia | SpikeArrest, VerifyAPIKey, Quota, AssignMessage |
| [kb-oauth-client-credentials](kb-oauth-client-credentials/README.md) | Proxy | Emisión de tokens (*client credentials*) sin backend y recurso protegido por scope | OAuthV2, AssignMessage, RaiseFault |
| [kb-jwt-idp](kb-jwt-idp/README.md) | Proxy | JWT de un IdP externo: JWKS, `iss`, `aud`, vida máxima, scope por verbo y propagación de identidad | VerifyJWT, AssignMessage, RaiseFault |
| [kb-cache-respuestas](kb-cache-respuestas/README.md) | Proxy | ResponseCache por recurso y query, sin cachear errores, *bypass* con `Cache-Control: no-cache` | ResponseCache, AssignMessage |
| [kb-sf-errores](kb-sf-errores/README.md) | Shared flow | Formato de error único para la plataforma, sin filtrar detalles internos | AssignMessage |

Todos usan `https://mocktarget.apigee.net`, el backend de pruebas de Google, y basepaths bajo `/kb/v1/`.

## Validación

Cada bundle pasa dos validaciones antes de cada commit:

```bash
# 1. Estructura propia: XML bien formado, nombres que coinciden con los archivos,
#    Steps que apuntan a políticas existentes, sin políticas huérfanas, RouteRules válidas
python3 scripts/validar_bundles.py

# 2. Lint oficial de buenas prácticas (perfil Apigee X)
npx apigeelint@2.85.1 -s ejemplos/bundles/kb-api-key-cuota/apiproxy -f table.js --profile apigeex
```

**Resultado del 23 de octubre de 2026:** `validar_bundles.py`, 5 bundles y 0 errores; `apigeelint` 2.85.1, **0 errores** en los 5. Los avisos que quedan son deliberados:

| Regla | Aviso | Por qué se deja |
|---|---|---|
| `TD002` | El target usa una URL fija en lugar de un TargetServer | Es un ejemplo autocontenido. En producción usa un [TargetServer](../../docs/01-proxies/05-target-endpoints-y-servidores.md) por entorno. |
| `TD012` | Falta `<SSLInfo>` en el target | En producción declara `<SSLInfo>` con `<Enforce>true</Enforce>` y un truststore por referencia (ver [TLS hacia backends](../../docs/15-administracion/04-tls-referencias-y-data-collectors.md)). |
| `PO007` | `VAK-Header` no usa los prefijos que espera apigeelint (`verifyapikey`, `apikey`, `va`, `verify`) | Este repo usa sus propias [convenciones de nombres](../../docs/08-mejores-practicas/02-convenciones-de-nombres.md) (`VAK-`). Si adoptas las de apigeelint, renombra el archivo y el `name` a la vez. |
| `CC004` | Condición con muchos términos en las FaultRules | Son listas de `fault.name` agrupadas por familia; partirlas no las hace más claras |

> [!IMPORTANT]
> **«Validado» no significa «probado en una organización».** Estos bundles pasan las comprobaciones estáticas, pero no se desplegaron en una organización de Apigee al escribirlos. Antes de usarlos:
> 1. Despliégalos en un entorno de pruebas.
> 2. Crea el API product y la app que piden.
> 3. Ejecuta las pruebas `curl` de cada README.

## Despliegue

Con `apigeecli`, usando las mismas opciones que [herramientas CLI](../../docs/06-devops/02-herramientas-cli.md):

```bash
TOKEN="$(gcloud auth print-access-token)"

# Proxy: crear la revisión desde la carpeta apiproxy/ y desplegarla
apigeecli apis create bundle --name kb-api-key-cuota \
  --proxy-folder ejemplos/bundles/kb-api-key-cuota/apiproxy --org "$ORG" --token "$TOKEN"
apigeecli apis deploy --name kb-api-key-cuota --rev 1 \
  --org "$ORG" --env "$ENV" --ovr --wait --token "$TOKEN"

# Shared flow
apigeecli sharedflows create bundle --name kb-sf-errores \
  --sf-folder ejemplos/bundles/kb-sf-errores/sharedflowbundle --org "$ORG" --token "$TOKEN"
apigeecli sharedflows deploy --name kb-sf-errores --rev 1 \
  --org "$ORG" --env "$ENV" --ovr --wait --token "$TOKEN"
```

Usa el número de revisión que devuelva `create bundle`.

## Fuentes

- apigeelint: <https://github.com/apigee/apigeelint> (versión 2.85.1, ejecutada el 2026-10-23).
- Las referencias de cada política usada, enlazadas desde el README de cada bundle.
