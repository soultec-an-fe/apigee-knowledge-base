---
id: politica-verify-iam
titulo: VerifyIAM — referencia completa
area: politicas
tags: [verifyiam, iam, google-cloud, autorizacion, deploymentinvoker, standard]
aplica_a: [apigee-x]
elemento_xml: VerifyIAM
tipo_politica: standard
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/verify-iam-policy
revisado: 2026-10-22
---

# VerifyIAM — referencia completa

> [!NOTE]
> **Tipo:** Standard (cualquier tipo de entorno). **Elemento raíz:** `<VerifyIAM>`.
> **Aplica a:** solo Apigee X. **No disponible en Apigee hybrid** (por ahora) **ni en Edge.**

VerifyIAM autoriza las llamadas a un proxy con **Google Cloud IAM**: el cliente envía un access token de Google, y la política comprueba que su principal (usuario, cuenta de servicio, grupo…) tenga el permiso `apigee.deployments.invoke` sobre el proyecto o sobre ese despliegue concreto. Es una alternativa a [VerifyAPIKey](verify-api-key.md) y [OAuthV2](oauthv2.md) cuando los consumidores son identidades de Google Cloud, típicamente servicios internos de la misma organización.

## Cómo se configura el acceso

1. Añade VerifyIAM al flujo de petición del proxy, como **primera política** después de las de gestión de tráfico (SpikeArrest).
2. El administrador concede al principal del consumidor:
   - el rol `roles/apigee.deploymentInvoker` (o uno propio con `apigee.deployments.invoke`) **a nivel de proyecto**, que da acceso a **todos** los proxies de la organización; **o**
   - el mismo rol o permiso sobre **despliegues concretos**, con `setIamPolicy` sobre `organizations/{org}/environments/{env}/deployments/{proxy}`.
3. El consumidor obtiene un access token de Google con el scope `https://www.googleapis.com/auth/cloud-platform` y lo envía en `Authorization: Bearer`.

Para retirar el acceso, se quita el rol del proyecto o del despliegue.

| Operación de administración | Permiso necesario |
|---|---|
| `GetDeployment` | `apigee.deployments.get` |
| `ListDeployments` | `apigee.deployments.list` |
| `SetIamPolicy` (conceder acceso a un despliegue) | `apigee.deployments.setIamPolicy` |
| `GetIamPolicy` | `apigee.deployments.getIamPolicy` |
| `TestIamPermissions` | Ninguno |

## Sintaxis completa

```xml
<VerifyIAM name="VIAM-Nombre" continueOnError="false" enabled="true">
  <DisplayName>Nombre legible</DisplayName>
  <CredentialSource>request.header.x-google-token</CredentialSource>
</VerifyIAM>
```

## Atributos del elemento raíz

| Atributo | Obligatorio | Default | Qué hace |
|---|---|---|---|
| `name` | Sí | — | Nombre interno. |
| `continueOnError` | No | `false` | Con `true`, la petición **continúa aunque el permiso falle**. Casi nunca es lo que quieres en una política de autorización. |
| `enabled` | No | `true` | Con `false` no se ejecuta. |
| `async` | No | `false` | **Obsoleto.** |

## Elementos hijos

| Elemento | Obligatorio | Default | Resumen |
|---|---|---|---|
| `<DisplayName>` | No | `name` | Etiqueta en la UI. |
| `<CredentialSource>` | No | cabecera `Authorization: Bearer …` | Variable que contiene el token, **sin** prefijo `Bearer`. |

## Características y limitaciones

- **Latencia:** normalmente 10-50 ms por ejecución; en algunas regiones (p. ej. `asia-east2`) la media sube a 50 ms y algunas llamadas tardan unos 100 ms. Google no garantiza estas cifras.
- **Es un sí/no:** solo comprueba el permiso de invocar. Los roles del consumidor **no** quedan disponibles para el resto del flujo; si necesitas autorización fina, tendrás que hacerla tú.
- Conceder `apigee.deployments.invoke` a nivel de **entorno** **no** da acceso a los despliegues de ese entorno.
- Permisos sobre un **shared flow** no tienen efecto: concédelos sobre el proxy. En proxy chaining, sobre el proxy que tiene la política.
- **No** admite condiciones de IAM sobre el recurso de despliegue.
- Máximo 1.500 *role bindings* por política de IAM, con el resto de cuotas de IAM.
- Hay **retraso de propagación** de IAM al conceder o quitar acceso.
- Gestionar otras operaciones (`apigee.deployments.delete`…) con el `setIamPolicy` del despliegue no tiene efecto ni da error: solo cuenta `invoke`.
- Al **replegar o borrar** el proxy se pierden los permisos del despliegue; hay que volver a concederlos al redesplegar.

> [!IMPORTANT]
> Ese último punto es fácil de olvidar en CI/CD: si tu pipeline repliega antes de desplegar, añade a ese pipeline la llamada a `setIamPolicy`, o concede el acceso a nivel de proyecto.

## Variables de flujo

La página no documenta variables de éxito (ni la identidad del principal).

## Errores

### En runtime

| Código de fallo | HTTP | Causa |
|---|---|---|
| `steps.verifyiam.CredentialSourceRefUnresolved` | 400 | La variable de `<CredentialSource>` no resolvió. |
| `steps.verifyiam.CredentialValueNotProvided` | 400 | No hay credencial (en la variable o en `Authorization`). |
| `steps.verifyiam.Unauthorized` | 401 | Token inválido o vencido. |
| `steps.verifyiam.Forbidden` | 403 | Falta el permiso, faltan scopes o algo similar. |
| `steps.verifyiam.MiscellaneousAuthorizationConfigurationError` | 500 | Problema en la petición de autorización a IAM; lo corrige el productor del API según el detalle del error. |
| `steps.verifyiam.UnexpectedAuthorizationInfrastructureError` | 500 | Error interno. |

### Al desplegar

No tiene errores de despliegue propios.

### Variables de fallo

| Variable | Ejemplo |
|---|---|
| `fault.name` | `fault.name = "Forbidden"` |
| `verifyiam.{name}.failed` | `verifyiam.VIAM-Interno.failed = true` |

## Ejemplos

### 1. API interna para servicios de Google Cloud

```xml
<VerifyIAM name="VIAM-Interno"/>
```

```xml
<PreFlow name="PreFlow">
  <Request>
    <Step><Name>SA-Escudo</Name></Step>
    <Step><Name>VIAM-Interno</Name></Step>
  </Request>
</PreFlow>
```

```bash
gcloud projects add-iam-policy-binding MI_PROYECTO \
  --member="serviceAccount:facturacion@MI_PROYECTO.iam.gserviceaccount.com" \
  --role="roles/apigee.deploymentInvoker"
```

### 2. Token en una cabecera propia

Útil cuando `Authorization` ya lo usa otro esquema y el token de Google viaja aparte.

```xml
<VerifyIAM name="VIAM-Cabecera">
  <CredentialSource>request.header.x-goog-token</CredentialSource>
</VerifyIAM>
```

## Diferencias en Apigee Edge

No existe en Edge (ni en hybrid). En esas ediciones, la alternativa es validar el token de Google como JWT (ID token) con VerifyJWT (ver [JWT y JWS](../../03-seguridad/03-jwt-jws.md)) contra las claves públicas de Google, y llevar tú la lista de identidades autorizadas.

## Antipatrones

- `continueOnError="true"` en una política de autorización.
- Ponerla después de políticas costosas: debe ir justo detrás de las de tráfico.
- Conceder `deploymentInvoker` a nivel de proyecto cuando solo hace falta un proxy.
- Esperar que los roles del consumidor estén disponibles en variables.

## Fuentes

- VerifyIAM policy — Apigee: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/verify-iam-policy> (consultada directamente, contenido completo, 2026-10-22).
- IAM-based API authentication overview: <https://docs.cloud.google.com/apigee/docs/api-platform/security/iam/iam-overview> (consultada directamente, 2026-10-22).
