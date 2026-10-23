---
id: administracion-instancias
titulo: Instancias, multirregión, mantenimiento y backups
area: administracion
tags: [instancias, multi-region, mantenimiento, maintenance-window, backups, cidr, recreacion, alta-disponibilidad]
aplica_a: [apigee-x]
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/system-administration/instances
revisado: 2026-10-23
---

# Instancias, multirregión, mantenimiento y backups

> **Fecha de corte: 23 de octubre de 2026.** Este documento trata las instancias gestionadas de Apigee X. Las de hybrid aparecen en la UI **solo en lectura** y se gestionan con Helm (ver [11-hybrid](../11-hybrid/01-arquitectura-y-planificacion.md)).

## Instancias

Una **instancia** es el runtime de Apigee en una **región**: **una instancia por región**. Los entornos se adjuntan a una o más instancias. Una instancia **sin entornos adjuntos no sirve tráfico**.

| Requisito de cada instancia | Detalle |
|---|---|
| Rangos de red propios | Un **/22** y un **/28**, **sin solaparse** con nada del peering ni con otras instancias |
| Clave de cifrado de disco propia | Google recomienda además un *key ring* nuevo por instancia |
| Nombre | De 2 a 32 caracteres, `[a-z0-9-]`, empezando por letra |
| Organización | De **pago**: las de evaluación están limitadas a **una** instancia |

**Inmutables:** después de crear la instancia no se pueden cambiar el **rango CIDR** ni la red. Para cambiarlos hay que borrar la instancia y crearla de nuevo, lo que deja sin servicio una organización con una sola instancia.

> [!NOTE]
> Al recrear una instancia **la IP puede cambiar**: normalmente se conserva, pero no está garantizado. Si el *northbound* usa **MIG** (VMs proxy), actualiza la metadata `ENDPOINT` de la plantilla de instancias y haz un *rolling update* del grupo. Con PSC no existe este problema. Ver [redes](03-redes-y-acceso.md).

> [!WARNING]
> **Instancias creadas antes del 25 de enero de 2022:** no tienen espacio IP suficiente para escalar ni para tener **más de 10 entornos**. El 24 de enero de 2022, Google empezó a usar **PUPI** (IPs públicas de uso privado) y redujo el rango necesario. Google recomienda **recrearlas** sin cortes:
> 1. Crea una instancia en otra región.
> 2. Pasa el tráfico a esa instancia.
> 3. Drena la antigua, bórrala y recréala.
>
> Google publica unos scripts en GitHub para hacerlo. Comprueba la fecha en el campo `createdAt` de la instancia.

## Multirregión

Ventajas: **alta disponibilidad** si cae una región, **más capacidad** y **menos latencia** para clientes lejanos.

**Pasos para añadir una región:**

1. Disponer de un /22 y un /28 libres.
2. Crear el *key ring* y la clave.
3. Reservar el rango.
4. Crear la instancia en la región.
5. **Adjuntar los entornos.**
6. Configurar el enrutamiento: un NEG de PSC por región en el balanceador, o un MIG.

**Límites:**

- **Máximo 10 regiones por organización (11 en hybrid).**
- La evaluación no admite una segunda región.
- En Subscription puede requerir *Org units* adicionales; en Pay-as-you-go tiene coste extra.

## Mantenimiento

Google actualiza las instancias de forma rutinaria: funciones nuevas, rendimiento y **parches de seguridad**. Normalmente no se nota, pero **mientras dura** no se puede:

- crear instancias;
- adjuntar entornos a instancias;
- crear *endpoint attachments*;
- hacer ciertas operaciones de escalado.

| Ajuste | Detalle |
|---|---|
| **Ventana de mantenimiento** | Día de la semana y hora de inicio (`startTime` en **UTC**). **Una por instancia.** Entre instancias de la misma organización, deja **al menos 12 horas** de separación. |
| **Orden de actualización** | `WEEK1` o `WEEK2` (`maintenanceChannel`). Son fases de despliegue con **1 o 2 semanas de preaviso**, no semanas del calendario. |
| **Notificaciones** | Opt-in por usuario en *User preferences > Communication*. Requiere haber definido una ventana. |
| **Ver lo programado** | Campos `maintenanceUpdatePolicy` y `scheduledMaintenance` de la instancia |
| **Permiso** | `roles/apigee.admin` o `apigee.instances.update` |

Características del mantenimiento:

- **Dura varias horas.**
- Google respeta la ventana **en la medida de lo posible**, pero puede actualizar fuera de ella por compatibilidad o seguridad.
- **No hay ventanas de congelación ni de exclusión** definidas por el cliente.
- Cambiar la ventana **no afecta a un mantenimiento que ya esté programado**.
- No todas las versiones llegan a las instancias con ventana: Google agrupa versiones estables, así que **puedes saltarte varias**.

> [!TIP]
> **Práctica recomendada por Google:**
> - Pon ventana de mantenimiento en **producción** y **no** la pongas en los entornos no productivos.
> - Las instancias sin ventana se actualizan primero, así que cuando llega la notificación de producción, **la misma versión ya lleva un tiempo funcionando** en tus otros entornos. Eso te da tiempo de detectar regresiones.

## Backups

| Datos | Copia |
|---|---|
| **Plano de control** | Se replica en varias regiones, que **pueden incluir EE. UU.**. Proxies, shared flows, keystores y archivos de recursos están en Cloud Storage **sin backup aparte**. |
| **Analytics** | Regiones UE: backup en la UE. América: en EE. UU. Varias regiones de Asia-Pacífico: en la multirregión de Asia. |
| **Runtime** | En la misma región de cada instancia (solo en organizaciones de Apigee, no en hybrid) |
| **Portal integrado** | Multirregión de EE. UU. |

Las copias se hacen **al menos una vez al día**, cifradas con claves de Google. Google prueba la restauración **trimestralmente** (con evidencia en sus auditorías, como SOC).

> [!IMPORTANT]
> **Google recomienda que hagas tus propias copias del plano de control:**
> - descarga los bundles de proxies y de shared flows;
> - recupera los certificados de los keystores por API;
> - recupera los archivos de recursos por API.
>
> En la práctica, el **control de versiones de los bundles** es tu copia de seguridad (ver [ciclo de vida](../06-devops/01-ciclo-de-vida.md)).
>
> Si tienes **requisitos de residencia de datos**, ten en cuenta que, según esta página, las copias del plano de control pueden replicarse en regiones que incluyan EE. UU. Revisa la documentación de *data residency* de Apigee antes de comprometerte con un regulador.

## Fuentes

Todas consultadas directamente el 2026-10-23:

- Instances: <https://docs.cloud.google.com/apigee/docs/api-platform/system-administration/instances>, requisitos y creación.
- Expanding Apigee to multiple regions: <https://docs.cloud.google.com/apigee/docs/api-platform/system-administration/multi-region>, pasos y límites.
- Recreate an Apigee instance: <https://docs.cloud.google.com/apigee/docs/api-platform/system-administration/instance-recreate>, contenido completo.
- Change instance IPs: <https://docs.cloud.google.com/apigee/docs/api-platform/system-administration/change-instance-ips>, contenido completo.
- Maintenance overview: <https://docs.cloud.google.com/apigee/docs/api-platform/system-administration/maintenance>, contenido completo.
- Manage maintenance windows: <https://docs.cloud.google.com/apigee/docs/api-platform/system-administration/maintenance-windows>, contenido completo.
- Backups: <https://docs.cloud.google.com/apigee/docs/api-platform/system-administration/backups>, contenido completo.
