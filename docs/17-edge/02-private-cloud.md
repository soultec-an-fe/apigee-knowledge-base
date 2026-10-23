---
id: edge-private-cloud
titulo: Edge for Private Cloud — arquitectura, instalación y operación (4.54)
area: edge
tags: [edge, private-cloud, opdk, cassandra, zookeeper, postgres, qpid, ldap, router, message-processor, apigee-setup, java-21, tls]
aplica_a: [apigee-edge]
fuente: https://docs.apigee.com/private-cloud/v4.54.00/overview
revisado: 2026-10-23
---

# Edge for Private Cloud — arquitectura, instalación y operación (4.54)

> **Fecha de corte: 23 de octubre de 2026.** ⚠️ **Solo Edge for Private Cloud.** Versión documentada: **4.54.00** (LTS, octubre de 2026). El ciclo de vida está en el [panorama](01-panorama-y-ciclo-de-vida.md#ciclo-de-vida-de-private-cloud).

## Módulos y componentes

| Módulo | Componentes |
|---|---|
| **Edge Gateway** (API Services) | Management Server, **ZooKeeper**, **Cassandra**, **Router** (Nginx), **Message Processor**, **LDAP** (SymasLDAP, componente `apigee-openldap`) y **New Edge UI** (`edge-management-ui` y `edge-management-ui-static`) |
| **Edge Analytics** | **Qpid** (Apache Qpid y el servicio Qpid Server de Apigee) y **Postgres** (PostgreSQL y el servicio Postgres Server de Apigee) |
| **Monetization Services** | Extensión opcional sobre Gateway y Analytics |

El Router recibe el tráfico y lo pasa a los Message Processors, que ejecutan los proxies. Cassandra guarda los datos de runtime (KMS, KVM, cuotas, caché) y ZooKeeper la configuración del cluster. Los datos de Analytics viajan por Qpid hasta Postgres.

## Topologías

| Topología | Uso | Reparto |
|---|---|---|
| **All-in-one** (1 nodo) | No productiva | Todo en un nodo |
| **2 nodos** | No productiva | Nodo 1: Gateway completo. Nodo 2: Postgres y Qpid. |
| **5 nodos** | No productiva | Nodo 1: Management Server, UI, LDAP, Cassandra y ZooKeeper. Nodos 2–3: Router, MP, Cassandra y ZooKeeper. Nodos 4–5: Postgres y Qpid. |
| **9 nodos** | Producción, un centro de datos | Nodos 1–3: Cassandra y ZooKeeper (el 1 además Management Server, UI y LDAP). Nodos 4–5: Router y MP. Nodos 6–7: Qpid. Nodos 8–9: Postgres. |
| **13 nodos** | Producción, un centro de datos | Nodos 1–3: Cassandra y ZooKeeper. Nodos 4–5: LDAP. Nodos 6–7: Management Server y UI. Nodos 8–9: Postgres. Nodos 10–11: Router y MP. Nodos 12–13: Qpid. |
| **12 nodos** | Producción, **dos centros de datos** | 6 nodos por centro de datos |

Ninguna topología incluye el portal de desarrolladores, que se instala aparte (Drupal).

## Requisitos de hardware (mínimos oficiales)

| Componente | RAM | CPU | Disco (además del SO) |
|---|---|---|---|
| Cassandra, sola o con ZooKeeper | 16 GB | 8 cores | 250 GB **locales en SSD, 2000 IOPS** |
| Postgres y Qpid (juntos o Postgres solo) | 16 GB | 8 cores | 500 GB–1 TB en red, preferiblemente con SSD, **≥ 1000 IOPS** |

**Escalado de Postgres según TPS:**

| TPS | RAM / CPU | IOPS del almacenamiento en red |
|---|---|---|
| Menos de 250 | 8 GB / 4 cores | 1000 |
| Más de 250 | 16 GB / 8 cores | 1000 |
| Más de 1000 | 16 GB / 8 cores | 2000 |
| Más de 2000 | 32 GB / 16 cores | 2000 |
| Más de 4000 | 64 GB / 32 cores | 4000 |

**Sistema operativo:** RHEL y derivados (Rocky) con el repositorio **EPEL** habilitado y **SELinux desactivado o en modo permisivo**. Las versiones exactas están en *Supported software and supported versions*.

## Instalación

1. **En cada nodo:**
   - deshabilita SELinux o ponlo en modo permisivo;
   - decide si activas autenticación en Cassandra y replicación *master-standby* de Postgres.
2. **Como root**, descarga y ejecuta `bootstrap_4.54.00.sh`. Instala `apigee-service`, sus dependencias y crea el usuario **`apigee`**.
3. Instala `apigee-setup`.
4. Con `apigee-setup`, instala en cada nodo los componentes de su topología. Lo controla un **archivo de configuración** con las IPs, la licencia, las contraseñas, etc.
5. En el Management Server, instala **`apigee-provision`** para crear y gestionar organizaciones. Después, **da de alta una organización** (*onboard*).
6. Reinicia y configura la **New Edge UI**: autenticación y ajustes.
7. Valida la instalación con `apigee-validate`, que usa el puerto 59001 del Router.

**Permisos:**

- `install`, `uninstall`, `update` y `setup.sh` exigen **root o sudo completo**.
- `start`, `stop`, `restart` y `configure` exigen **sudo hacia el usuario `apigee`**.
- Los archivos de configuración deben ser legibles por `apigee:apigee`.
- **Sobrescrituras de propiedades:** en `/opt/apigee/customer/application/{componente}.properties`.

## Orden de arranque y parada

Desde `/opt/apigee/apigee-service/bin/`:

| Para **detener**, en este orden | Para **arrancar**, en este orden |
|---|---|
| Management Server, MP, Postgres Server, Qpid Server, Router y New Edge UI; después Cassandra, LDAP, PostgreSQL, Qpidd y ZooKeeper | Cassandra, LDAP, PostgreSQL, Qpidd y ZooKeeper; después Management Server, MP, Postgres Server, Qpid Server, Router y New Edge UI |

Primero los servicios de Edge y luego los almacenes de datos al parar; al revés al arrancar. `apigee-all stop` y `apigee-all start` lo hacen en un nodo.

## Puertos principales

| Componente | Puertos |
|---|---|
| Router | Puertos de los *virtual hosts* (80 y 443 habitualmente), 8081 (gestión), 4527, 15999 y 59001 (validación) |
| Message Processor | 8998 (desde el Router), **8443** si hay TLS entre Router y MP, 4528 y 1101 (JMX) |
| Management Server | **8080** (API de gestión), 1099 (JMX), 4526 y 5636 (monetización) |
| New Edge UI | **3001** (antes 9000; configurable con `conf_uebe_port`) |
| Cassandra | 7000 y 9042; 7199 (JMX) |
| ZooKeeper | 2181; 2888 y 3888 (interno) |
| LDAP | 10389 |
| Postgres | 5432; 8084 (gestión); 22 si hay replicación *master-standby* |
| Qpid | 5672; 8083 (gestión); 8090 (broker) |

## Cambios de la 4.54.00 que hay que preparar

> [!CAUTION]
> **Cambios incompatibles con versiones anteriores.** Antes de actualizar, ejecuta la **herramienta de detección de cambios** (*change detection tool*) y prueba en entornos bajos.

| Cambio | Impacto |
|---|---|
| **Java 8 sale; entran Java 17 (Cassandra y ZooKeeper) y Java 21** (Management Server, MP, Router y Qpid) | Los **JavaCallout** y los JAR propios pueden romperse. Desaparecen JAXB (`javax.xml.bind`), Activation (`javax.activation`), JAX-WS y CORBA (JEP 320) y `sun.misc.BASE64Encoder`; la encapsulación fuerte (JEP 403) bloquea la reflexión sobre `sun.*` y `com.sun.*`. Un proxy puede **desplegarse bien y fallar en runtime**. Ver [JavaCallout](../02-politicas/referencia/java-callout.md). |
| **TLS 1.3 por defecto** hacia backends; se deshabilitan los suites **`TLS_RSA_*`** (RSA estático sin *forward secrecy*) | Los backends antiguos que solo aceptan RSA estático dejan de conectar. Lo recomendado es modernizar el backend a ECDHE. Como transición, se puede reactivar con `conf_jvmsecurity_jdk.tls.disabledAlgorithms`. Revisa también las listas de suites propias, incluida la de Router → MP. |
| **Classic UI eliminada**; solo queda la **New Edge UI** | Hay que migrar antes de actualizar. Las propiedades de la Classic UI no se trasladan. Puerto 9000 → **3001**. |
| **`apigee-sso` sustituido** por un broker OIDC integrado en el LDAP | **Backup completo y validado del LDAP antes de actualizar.** La configuración de `apigee-sso` no migra sola. |
| Componentes actualizados: Cassandra, Postgres, OpenLDAP, ZooKeeper, Qpid Broker-J, Nginx 1.30 y Consul | Revisa los cambios de Nginx si vienes de 1.20.x |

**La 4.54.00 no admite** (si usas alguna, quédate en la 4.53.01 y contacta con soporte):

- instalación en **Google Distributed Cloud air-gapped**;
- **RHEL 8 o Rocky 8 con FIPS habilitado**;
- TLS hacia backends con un **HSM Entrust nShield**.

**Estrategias para los JavaCallout:**

1. Incluir en el bundle las librerías sustitutas, por ejemplo `jakarta.xml.bind`, y activar `conf_system_java.21.enable.external.allowed.packages=true`.
2. Modernizar el código.
3. Redesplegar tras actualizar el nodo:
   - **3A:** en una ventana de mantenimiento;
   - **3B:** en un entorno nuevo, sin corte de servicio;
   - **3C:** poniendo las librerías a nivel de nodo.
4. Para librerías cerradas, usar los flags `--add-opens` y `--add-exports`.

## Conector con API hub

Desde Private Cloud se pueden publicar metadatos y Analytics en **API hub** de Google Cloud con el **conector de API hub para Private Cloud** (un RPM en una VM dedicada):

1. Los MP escriben los datos de Analytics por partida doble: en Analytics y en un **NFS compartido**.
2. El conector lee la API del Management Server y el NFS.
3. El conector publica en **Pub/Sub** las instancias de plugin creadas en API hub.

Ver [API hub](../12-api-hub/02-integraciones-y-funciones.md). Es una vía para gobernar el inventario de Edge desde Google Cloud durante una migración.

## Fuentes

Todas consultadas directamente el 2026-10-23:

- Edge for Private Cloud overview (4.54.00): <https://docs.apigee.com/private-cloud/v4.54.00/overview>, arquitectura.
- Installation overview (4.54.00): <https://docs.apigee.com/private-cloud/v4.54.00/installation-overview>, contenido completo.
- Installation topologies (4.54.00): <https://docs.apigee.com/private-cloud/v4.54.00/installation-topologies>, tabla.
- Installation requirements (4.54.00): <https://docs.apigee.com/private-cloud/v4.54.00/installation-requirements>, tablas de hardware.
- Port requirements (4.54.00): <https://docs.apigee.com/private-cloud/v4.54.00/port-requirements>, tablas.
- Starting, stopping, and restarting Apigee Edge (4.54.00): <https://docs.apigee.com/private-cloud/v4.54.00/starting-stopping-and-restarting-apigee-edge>, orden.
- Changes in Edge for Private Cloud 4.54.00: <https://docs.apigee.com/private-cloud/v4.54.00/changes-privatecloud-45400>, funciones no admitidas, JavaCallout y TLS.
- Apigee API hub connector for Private Cloud overview: <https://docs.apigee.com/private-cloud/v4.54.00/privatecloud-uapim-overview>, contenido completo.
- Edge for Private Cloud release notes, 15 de octubre de 2026: <https://docs.cloud.google.com/apigee/docs/edge-private-cloud/release-notes>.
