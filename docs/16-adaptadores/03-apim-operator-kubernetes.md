---
id: adaptadores-apim-operator
titulo: Apigee Operator for Kubernetes (APIM Operator)
area: adaptadores
tags: [apim-operator, kubernetes, gke, gateway-api, crd, helm, apimextensionpolicy, apigeebackendservice, gitops]
aplica_a: [apigee-x, apigee-hybrid]
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/apigee-kubernetes/apigee-apim-operator-overview
revisado: 2026-10-23
---

# Apigee Operator for Kubernetes (APIM Operator)

> **Fecha de corte: 23 de octubre de 2026.**

El **Apigee Operator for Kubernetes** permite gestionar APIs con herramientas de Kubernetes (`kubectl`, Helm, CRDs) en lugar de la UI o la API de gestión de Apigee. Productos, operaciones y políticas se declaran como recursos de Kubernetes, que el operador traduce a configuración de Apigee.

Por debajo:

- el **GKE Gateway** (un Application Load Balancer) con una *traffic extension* actúa como **PEP**;
- la extensión llama a Apigee mediante el [Extension Processor](02-extension-processor.md);
- **Apigee actúa como PDP**.

Las políticas se aplican **a nivel de balanceador**, y el RBAC de Kubernetes controla quién puede crear cada recurso.

## Requisitos y límites

| Aspecto | Valor |
|---|---|
| GKE | **≥ 1.27**, con Workload Identity Federation for GKE y GKE Gateway habilitados (vienen por defecto en Autopilot) |
| Instancia de Apigee | **≥ `1-15-0-apigee-4`**; organizaciones Subscription o Pay-as-you-go |
| Helm | ≥ 3.13.3 según la página general, ≥ v3.14.3 según *Before you begin* (ver nota) |
| Protocolos | **Solo REST**: ni gRPC ni GraphQL |
| GKE Gateways con políticas | Máximo 25 (regionales o globales) |
| APIMExtensionPolicy por entorno | Máximo 50; para más, otro entorno |
| Dónde se adjuntan las políticas | **Solo a recursos `Gateway`**, no a `HTTPRoute`. Para segmentar por ruta, usa las condiciones de `ApimTemplate` (por basepath o cabecera). |
| Expansión de región | **No soportada** una vez configurado |
| Con `ApigeeBackendService` | GKE **≥ 1.34.x**, y todos los Gateways en el namespace `default` |
| Versión de API | `apim.googleapis.com/v1`; la GA **no es compatible ni actualizable** desde la Preview pública |

> [!NOTE]
> **Contradicciones en las páginas oficiales:**
> - **Helm:** la página general pide 3.13.3 y *Before you begin*, v3.14.3. Usa la más alta.
> - **hybrid:** la página general dice que el operador «no se puede usar con Apigee hybrid por ahora», pero existe una guía de instalación para hybrid ≥ 1.15.0, marcada como **Preview (Pre-GA)**, que usa **Istio Gateway** en lugar del GKE Gateway.

## Dos formas de crear la extensión

| Recurso | Cuándo usarlo |
|---|---|
| **`APIMExtensionPolicy`** | Recomendado si no tienes otras traffic extensions: el operador crea la extensión en el Gateway. No lo uses si la extensión de Apigee debe convivir con otras. |
| **`ApigeeBackendService`** + **`GCPTrafficExtension`** | Obligatorio si la extensión de Apigee debe trabajar junto a otras traffic extensions que gestionas tú. El operador crea además un `APIMExtensionPolicy` «de respaldo» con el mismo nombre. |

`APIMExtensionPolicy`:

```yaml
apiVersion: apim.googleapis.com/v1
kind: APIMExtensionPolicy
metadata:
  name: gw-apim-policy
  namespace: apim
spec:
  apigeeenv: ENV_NAME          # opcional si se instaló con generateEnv=TRUE
  location: global
  failOpen: false
  timeout: 1000ms
  defaultSecurityEnabled: true
  targetRef:                    # el Gateway al que se aplica
    name: global-ext-lb1
    kind: Gateway
    namespace: default
```

- Equivale a un *flow hook* a nivel de entorno: gobierna **todo** el tráfico del Gateway y de sus `HTTPRoute`.
- Puede tardar hasta **5 minutos** en propagarse.
- Con `defaultSecurityEnabled: true`, una petición sin credenciales falla con `RF-insufficient-request-raise-fault`.

En `ApigeeBackendService` se declaran `apigeeEnv` (opcional en X, **obligatorio en hybrid**), `defaultSecurityEnabled` (default `true`) y `locations` (región, red y subred donde se crean los NEG de PSC).

En `GCPTrafficExtension` se declara `supportedEvents`, que puede incluir `RequestHeaders`, `RequestBody`, `RequestTrailers`, `ResponseHeaders`, `ResponseBody` y `ResponseTrailers`. **Las políticas que leen el cuerpo** (JSONThreatProtection, por ejemplo) necesitan `RequestBody` y `ResponseBody`.

> [!WARNING]
> **Qué activa `defaultSecurityEnabled`, según la página:**
> - La de `APIMExtensionPolicy` dice que activa la **verificación de API key y de access token**.
> - La de `ApigeeBackendService` dice que activa la **validación de API key y las comprobaciones de Quota**.
>
> En ambos casos, para que las peticiones pasen tienes que crear un `APIProduct` y un `APIOperationSet` (ver abajo).

## Instalación en Apigee X (resumen)

1. **APIs:** habilitar `apigee`, `compute`, `networkservices` y `container`.
2. **Cuenta de servicio de Google** `apigee-apim-gsa`, con estos roles:
   - `roles/apigee.admin`;
   - `roles/networkservices.serviceExtensionsAdmin`;
   - `roles/compute.networkAdmin`;
   - `roles/compute.loadBalancerAdmin`;
   - `roles/iam.workloadIdentityUser`.
3. **Workload Identity:** enlazar la cuenta de Kubernetes `apim/apim-ksa` (la crea Helm) con la cuenta de Google. La propagación puede tardar **7 minutos o más**.
4. **Helm:** instalar en el namespace `apim`, desde `oci://us-docker.pkg.dev/apigee-release/apigee-k8s-tooling-helm-charts/`:
   - el chart de CRDs (`apigee-apim-operator-crds`);
   - el chart del operador (`apigee-apim-operator-helm`), con `--set projectId`, `serviceAccount`, `apigeeOrg` y `generateEnv`.

   La guía de X usa la versión **1.1.1**; la de hybrid, **1.1.0**.
5. **Entorno:**
   - Con `generateEnv=TRUE`, el operador crea un entorno con prefijo `apim-enabled-dep…` al aplicar la primera política.
   - Con `FALSE`, lo creas tú por API y lo adjuntas a la instancia.
   - En los dos casos, el entorno es **Intermediate o Comprehensive**, porque admite proxies Extensible.

**En hybrid (Preview):**

- Istio Gateway en lugar de GKE Gateway.
- Clave JSON de la cuenta de servicio en lugar de Workload Identity.
- Entorno creado con un flag de service extension.
- Un `Secret` con el certificado del environment group, que se referencia desde `ingressCertSecret`.
- Los campos `apigeeAuthority` y `apigeeIngressIP` en la `APIMExtensionPolicy`.

## Productos, operaciones y políticas como recursos

| Recurso (`apim.googleapis.com/v1`) | Equivale en Apigee a |
|---|---|
| `APIProduct` | API product (con `approvalType`, `enforcementRefs` hacia la `APIMExtensionPolicy`, atributos) |
| `APIOperationSet` | Operaciones REST del producto, con su **Quota** |
| `SpikeArrest`, `Javascript`, `KVM`, `OASValidation`, `ServiceCallout`, `GenerateJWT`, `OAuthV2`, `ResponseCache`, `VerifyAPIKey`, `AssignMessage` (inyección de token de Google) | La política del mismo nombre |
| `ApimTemplateRule` | Regla de gobierno: `allowList`, `requiredList` y `denyList` de políticas |
| `ApimTemplate` | Plantilla (un *shared flow*) que usa una regla, con flujos condicionales |
| `ApigeeGatewayPolicy` | Despliega una plantilla en el Gateway, con la cuenta de servicio indicada |

Para añadir políticas con inyección de token de Google, la cuenta de servicio necesita además `roles/iam.serviceAccountTokenCreator` y `roles/iam.serviceAccountUser`.

## Diagnóstico

- **Estado de cada recurso:** campos `STATE` (`running`, `created`) y `ERRORMESSAGE`, que se ven con `kubectl -n NS get KIND NOMBRE`.
- **Logs de los callouts `ext-proc`:** habilita el logging del backend service del Gateway (su ID contiene `apigee-service-extension-backend-service`) y busca la entrada `service_extension_info`. Un callout fallido muestra `grpcStatus: ABORTED`.
- **Logs del operador:** en Logs Explorer.

## Fuentes

Todas consultadas directamente, contenido completo, el 2026-10-23:

- Apigee Operator for Kubernetes overview: <https://docs.cloud.google.com/apigee/docs/api-platform/apigee-kubernetes/apigee-apim-operator-overview>.
- Before you begin: <https://docs.cloud.google.com/apigee/docs/api-platform/apigee-kubernetes/apigee-apim-operator-before-you-begin>.
- Install: <https://docs.cloud.google.com/apigee/docs/api-platform/apigee-kubernetes/apigee-apim-operator-install>.
- Install for hybrid (Preview): <https://docs.cloud.google.com/apigee/docs/api-platform/apigee-kubernetes/apigee-apim-operator-install-hybrid>.
- Create an APIMExtensionPolicy: <https://docs.cloud.google.com/apigee/docs/api-platform/apigee-kubernetes/apigee-apim-operator-apimextension>.
- Create an ApigeeBackendService: <https://docs.cloud.google.com/apigee/docs/api-platform/apigee-kubernetes/apigee-apim-operator-apigeebackendservice>.
- Add policies: <https://docs.cloud.google.com/apigee/docs/api-platform/apigee-kubernetes/apigee-apim-operator-add-policies>.
- Security and quota: <https://docs.cloud.google.com/apigee/docs/api-platform/apigee-kubernetes/apigee-apim-operator-security-quota>.
- Resource reference: <https://docs.cloud.google.com/apigee/docs/api-platform/apigee-kubernetes/apigee-apim-operator-reference>.
- Troubleshoot: <https://docs.cloud.google.com/apigee/docs/api-platform/apigee-kubernetes/apigee-apim-operator-troubleshoot>.
