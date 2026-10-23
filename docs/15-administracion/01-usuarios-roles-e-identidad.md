---
id: administracion-usuarios-roles
titulo: Usuarios, roles e identidad
area: administracion
tags: [iam, roles, usuarios, entornos, iam-conditions, workforce-identity-federation, saml, sso, minimo-privilegio]
aplica_a: [apigee-x, apigee-hybrid]
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/system-administration/users-roles-overview
revisado: 2026-10-23
---

# Usuarios, roles e identidad

> **Fecha de corte: 23 de octubre de 2026.**

En Apigee X y hybrid, el control de acceso es **IAM de Google Cloud**. No se concede un permiso directamente: se concede un **rol**, que es un conjunto de permisos, a un **principal**. Un principal puede ser:

- una cuenta de Google;
- un grupo de Google;
- una cuenta de servicio;
- un dominio de Google Workspace;
- una identidad federada.

## Dos niveles de asignación

| Dónde se asigna | Alcance |
|---|---|
| **Proyecto de Google Cloud** (consola, IAM) | **Todas** las organizaciones y **todos** los entornos del proyecto |
| **Entorno** (Apigee UI, *Environment Access*, o `SetIamPolicy` sobre el entorno) | Solo ese entorno |

> [!IMPORTANT]
> - **Los roles de entorno se suman a los del proyecto; no los restringen.** Un `API Admin` a nivel de proyecto es `API Admin` en todos los entornos, aunque en la UI le pongas *Read Only* en `prod`.
> - **Quitar a alguien de un entorno no le quita el acceso** que tenga por el proyecto. Para revocarlo del todo, quítalo del proyecto.
> - Para añadir a alguien en un entorno desde la UI, antes tiene que tener acceso al proyecto.
> - Los roles de entorno solo afectan a recursos que cuelgan del entorno en la jerarquía. Productos, developers y apps son de organización.

**Recomendación oficial:** en el proyecto, el rol con menos permisos que sirva (por ejemplo, `API Admin`). Los roles adicionales, por entorno. Los superusuarios son la excepción.

## Roles predefinidos de Apigee

| Rol | Para quién |
|---|---|
| **Org Admin** (`roles/apigee.admin`) | Superusuario: acceso total. **El único que crea, borra o actualiza organizaciones.** |
| **Read Only Admin** | Ve todo y ejecuta informes; no cambia nada |
| **API Admin** (V2) | Quien desarrolla proxies: lectura y escritura en proxies, shared flows, KVM, productos y apps. Sustituye al obsoleto *API Creator*. |
| **API Reader** (V2) | Lectura de casi todo: productos, environment groups, entornos, KVM, proxies, shared flows… |
| **Environment Admin** | Recursos del entorno: flow hooks, keystores, KVM, shared flows, target servers; y despliegue |
| **Developer Admin** | Developers, apps, keys y AppGroups; lectura de productos |
| **Analytics Editor** / **Analytics Viewer** | Crear y editar informes, o solo verlos |

Advanced API Security tiene sus propios roles (`apigee.securityAdmin` y `apigee.securityViewer`); ver [13-advanced-api-security](../13-advanced-api-security/01-vision-general.md#roles).

> [!NOTE]
> **Desplegar un proxy exige dos permisos**, que vienen de roles distintos:
> - `apigee.deployments.create`, que da *Environment Admin* a nivel de entorno;
> - `apigee.proxyrevisions.deploy`, que está **en *API Reader***, un rol de organización que hay que conceder **en el proyecto**.
>
> La página aclara que, aunque API Reader incluye ese permiso de despliegue, sigue siendo de solo lectura. Para dar a alguien permiso de desplegar solo en `dev`, combina *Environment Admin* en `dev` con *API Reader* en el proyecto.

**Roles personalizados:** si creas uno en *IAM & Admin > Roles*, incluye siempre `apigee.projectorganizations.get`.

## IAM Conditions: acceso por recurso

Las **IAM Conditions** limitan un rol a recursos concretos. Por ejemplo, un equipo solo puede editar *sus* proxies o *sus* productos. Para escribir la condición necesitas:

- la **URI del recurso**, por ejemplo `organizations/{org}/apiproducts/{producto}`;
- si hay **permisos *parent-only***;
- el **tipo de recurso**.

| Recurso | Tipo |
|---|---|
| API proxy / revisión | `apigee.googleapis.com/Proxy` / `ProxyRevision` |
| Shared flow / revisión | `apigee.googleapis.com/SharedFlow` / `SharedFlowRevision` |
| KVM y entradas (ámbito de proxy) | `apigee.googleapis.com/KeyValueMap` / `KeyValueEntry` |
| API product y sus atributos | `apigee.googleapis.com/ApiProduct` / `ApiProductAttribute` |
| Developer y sus atributos | `apigee.googleapis.com/Developer` / `DeveloperAttribute` |
| Developer app y sus atributos | `apigee.googleapis.com/DeveloperApp` / `DeveloperAppAttribute` |
| Rate plan | `apigee.googleapis.com/RatePlan` |

Para separar equipos dentro de una misma organización, la alternativa más moderna es [Apigee Spaces](05-apigee-spaces.md).

## Identidad corporativa

| Mecanismo | Uso |
|---|---|
| **Workforce Identity Federation** | Los usuarios entran con su IdP corporativo (OIDC o SAML 2.0: Entra ID/Azure AD, AD FS, Okta…) **sin sincronizar identidades** con Google Cloud. Vale para la UI y para la API, con un token de corta duración del **STS**. Disponible en organizaciones Subscription, Pay-as-you-go y hybrid. |
| **SSO con SAML para la UI** | El IdP autentica a los usuarios de la Apigee UI. **Solo autentica: la autorización sigue siendo de los roles de Apigee.** Si se da de baja a alguien en el IdP, pierde el acceso. |

**Limitaciones de Workforce Identity Federation:**

- Sin desarrollo local con **Cloud Code y VS Code**.
- Sin la **API de Apigee Connect** en hybrid.
- Algunas funciones en Preview pueden no estar disponibles; las GA de la UI sí lo están.

## Fuentes

Todas consultadas directamente el 2026-10-23:

- Users and roles overview: <https://docs.cloud.google.com/apigee/docs/api-platform/system-administration/users-roles-overview>, contenido completo.
- Apigee roles: <https://docs.cloud.google.com/apigee/docs/api-platform/system-administration/apigee-roles>, contenido completo.
- Manage users in the Apigee UI: <https://docs.cloud.google.com/apigee/docs/api-platform/system-administration/manage-users>, contenido completo.
- Add IAM Conditions: <https://docs.cloud.google.com/apigee/docs/api-platform/system-administration/add-iam-conditions>, tipos de recurso.
- Workforce Identity Federation: <https://docs.cloud.google.com/apigee/docs/api-platform/system-administration/workforce-identity-federation-apigee>, contenido completo.
- SAML overview: <https://docs.cloud.google.com/apigee/docs/api-platform/system-administration/saml-overview>, contenido completo.
