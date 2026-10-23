---
id: administracion-spaces
titulo: Apigee Spaces — aislamiento por equipo dentro de una organización
area: administracion
tags: [spaces, iam, multi-equipo, aislamiento, setiampolicy, spacecontenteditor, gobierno]
aplica_a: [apigee-x, apigee-hybrid]
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/system-administration/spaces/apigee-spaces-overview
revisado: 2026-10-23
---

# Apigee Spaces — aislamiento por equipo dentro de una organización

> **Fecha de corte: 23 de octubre de 2026.**

**Apigee Spaces** agrupa y aísla, por identidad, **API proxies, shared flows y API products** dentro de una misma organización. Cada Space tiene su política IAM, y los recursos creados en él la **heredan**. Así, varios equipos comparten una organización sin ver ni tocar lo de los demás, y se pueden conceder accesos puntuales (lectura, escritura o trace/debug) a recursos de otro equipo.

**Disponible en:**

- organizaciones Subscription y Pay-as-you-go;
- organizaciones con residencia de datos;
- **hybrid ≥ 1.13**.

## Límites

| Límite | Valor |
|---|---|
| Spaces por organización | **20** |
| Operaciones `list` de proxies, productos y shared flows | **10 QPS** |

## Cómo cambia la jerarquía de permisos

- **Sin Spaces:** los permisos se conceden en el proyecto y valen para toda la organización.
- **Con Spaces:**
  - La **ruta** del recurso no cambia (`organizations/{org}/apis/{proxy}`, con un atributo de Space).
  - IAM comprueba los permisos **como si el recurso fuera hijo del Space** (`organizations/{org}/spaces/{space}/apis/{proxy}`).
  - Esto se aplica también a los subrecursos, como los atributos de un producto.
- **Los entornos no pertenecen a ningún Space.** Algunas operaciones de despliegue y de debug aceptan el permiso en el entorno **o** en el recurso del Space. Por ejemplo, desplegar exige `apigee.deployments.create` sobre el entorno, mientras que listar los despliegues de un proxy acepta `apigee.deployments.list` sobre `spaces/{space}/apis/{api}`.

## Roles

| Rol | Ámbito | Uso |
|---|---|---|
| `apigee.spaceContentEditor` | **Space** | Acceso completo a los recursos del Space |
| `apigee.spaceContentViewer` | **Space** | Solo lectura |
| `apigee.spaceConsoleUser` | **Proyecto** | El mínimo necesario para gestionar los recursos del Space **desde la consola** |
| `apigee.admin` | Proyecto | Crear, editar y borrar Spaces, y gestionar su IAM |

Los miembros se añaden con `setIamPolicy` sobre el recurso Space.

**Permisos propios de los Spaces:** `apigee.spaces.create`, `update`, `delete`, `get`, `list`, `getIamPolicy` y `setIamPolicy`.

> [!NOTE]
> La página de roles presenta `apigee.spaceConsoleUser` como rol predefinido. La sección *View Space resources* de la misma página lo llama **rol personalizado**, y pide al administrador que lo cree si no existe. Comprueba en IAM si ya está disponible en tu organización.

## Mover recursos

Los proxies, shared flows y productos se pueden mover de la organización a un Space, entre Spaces, o de un Space a la organización. Al moverlos, **heredan la política del destino**.

Para mover un recurso se necesitan dos permisos:

- `apigee.{apis|sharedflows|apiproducts}.move` en el **origen**;
- `apigee.{tipo}.create` en el **destino**.

`spaceContentEditor` en los dos Spaces basta para mover entre ellos.

Un usuario que intenta acceder a un recurso movido sin permisos en su Space recibe un error de permisos, **aunque antes lo viera a nivel de organización**.

## Cuándo usar Spaces y cuándo varias organizaciones

| Necesidad | Spaces | Organizaciones separadas |
|---|---|---|
| Separar quién edita qué proxies o productos | ✅ | ✅ |
| Compartir entornos, instancias, Analytics y facturación | ✅ | ❌ |
| Aislar entornos, KVM de entorno, keystores o target servers | ❌ (los entornos no son de un Space) | ✅ |
| Más de 20 equipos | ❌ | ✅ |

Esta tabla es una síntesis de este repositorio.

## Fuentes

Todas consultadas directamente el 2026-10-23:

- Apigee Spaces overview: <https://docs.cloud.google.com/apigee/docs/api-platform/system-administration/spaces/apigee-spaces-overview>, contenido completo.
- IAM permission hierarchy in Apigee Spaces: <https://docs.cloud.google.com/apigee/docs/api-platform/system-administration/spaces/iam-permission-hierarchy-spaces>, contenido completo.
- Spaces roles and permissions: <https://docs.cloud.google.com/apigee/docs/api-platform/system-administration/spaces/spaces-roles-permissions>, contenido completo.
- Move API resources between Spaces: <https://docs.cloud.google.com/apigee/docs/api-platform/system-administration/spaces/move-space-resources>, contenido completo.
