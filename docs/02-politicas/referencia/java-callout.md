---
id: politica-java-callout
titulo: JavaCallout — referencia completa
area: politicas
tags: [javacallout, java, jar, execution, messagecontext, permisos, extensible]
aplica_a: [apigee-x, apigee-hybrid, apigee-edge]
elemento_xml: JavaCallout
tipo_politica: extensible
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/java-callout-policy
fuente_edge: https://docs.apigee.com/api-platform/reference/policies/java-callout-policy
revisado: 2026-10-22
---

# JavaCallout — referencia completa

> [!NOTE]
> **Tipo:** Extensible. **Elemento raíz:** `<JavaCallout>`.
> **Aplica a:** Apigee X, hybrid y Edge. En X/hybrid, la versión soportada es **JDK 11** (Oracle u OpenJDK). En Edge depende de la versión instalada (*Supported software*).

JavaCallout ejecuta una clase Java empaquetada en un JAR dentro del flujo del proxy. El código puede leer y modificar mensajes, leer y escribir variables, llamar servicios externos y lanzar fallos. Es la opción de **mayor rendimiento** para lógica en línea, pero también la más cara de mantener: compilación, dependencias y un *sandbox* de permisos estricto.

## Cuándo usarla

Según la guía de buenas prácticas de Google:

| Necesidad | Usa |
|---|---|
| Lógica simple sobre el mensaje (cabeceras, parámetros, contenido) | [JavaScript](javascript.md) o [PythonScript](python-script.md) |
| Llamar a un servicio remoto | [ServiceCallout](service-callout.md) |
| Lógica en línea donde el **rendimiento es crítico**, o que ya existe en librerías Java | **JavaCallout** |
| Lógica de negocio que tarda más de un segundo, o frameworks (Spring, JEE) | Fuera del gateway: ExternalCallout o ServiceCallout hacia Cloud Run o Cloud Functions |

## Sintaxis completa

```xml
<JavaCallout name="JC-Nombre" continueOnError="false" enabled="true">
  <DisplayName>Nombre legible</DisplayName>
  <ClassName>com.empresa.apigee.MiCallout</ClassName>
  <ResourceURL>java://mi-callout.jar</ResourceURL>
  <Properties>
    <Property name="algoritmo">SHA256withRSA</Property>
  </Properties>
</JavaCallout>
```

## Atributos del elemento raíz

Los comunes: `name` (obligatorio), `continueOnError`, `enabled` y `async` (obsoleto). No tiene atributos propios.

## Elementos hijos

| Elemento | Obligatorio | Resumen |
|---|---|---|
| `<ClassName>` | **Sí** | Clase completa (con paquete) que implementa `Execution`. Debe estar dentro del JAR de `<ResourceURL>`. |
| `<ResourceURL>` | **Sí** | `java://archivo.jar`. Puede ir en el bundle (`apiproxy/resources/java/`) o como recurso del entorno o de la organización. |
| `<Properties>/<Property name>` | No | Pares nombre/valor que la clase recibe en su constructor como `Map<String, String>`. **Solo literales**: no admite variables de flujo ni plantillas. |

> [!IMPORTANT]
> Si usas `<Properties>`, la clase necesita un constructor que reciba el mapa (`public MiCallout(Map<String, String> props)`). Si el constructor no existe, el despliegue falla con `NoAppropriateConstructor`.

## La clase Java

Toda clase de JavaCallout implementa `com.apigee.flow.execution.spi.Execution` y su método `execute(MessageContext, ExecutionContext)`.

```java
package com.empresa.apigee;

import com.apigee.flow.execution.ExecutionContext;
import com.apigee.flow.execution.ExecutionResult;
import com.apigee.flow.execution.spi.Execution;
import com.apigee.flow.message.MessageContext;
import java.util.Map;

public class FirmaCallout implements Execution {

    private final String algoritmo;

    public FirmaCallout(Map<String, String> props) {
        this.algoritmo = props.getOrDefault("algoritmo", "SHA256withRSA");
    }

    @Override
    public ExecutionResult execute(MessageContext ctx, ExecutionContext execCtx) {
        try {
            String contenido = ctx.getMessage().getContent();
            ctx.setVariable("firma.valor", firmar(contenido));
            return ExecutionResult.SUCCESS;
        } catch (Exception e) {
            ctx.setVariable("firma.error", e.getMessage());
            return ExecutionResult.ABORT;
        }
    }

    private String firmar(String contenido) { /* ... */ return ""; }
}
```

| API | Uso |
|---|---|
| `ctx.getMessage()` | El mensaje del flujo actual: la petición si la política va en el flujo de petición, la respuesta si va en el de respuesta. Google lo prefiere a `getRequestMessage()` o `getResponseMessage()` porque funciona en ambos flujos. |
| `getHeader`, `setContent`, `removeHeader`… | Operaciones sobre el mensaje. |
| `ctx.getVariable(nombre)` / `ctx.setVariable(nombre, valor)` | Variables de flujo. Para leer un KVM, usa antes una política [KeyValueMapOperations](key-value-map-operations.md) que deje el valor en una variable. |
| `ExecutionResult.SUCCESS` / `ExecutionResult.ABORT` | Continuar, o marcar la política como fallida (el flujo entra en error). |

### Compilación y dependencias

- Las interfaces vienen en dos JAR de Apigee: `message-flow-1.0.0.jar` (`com.apigee.gateway.libraries:message-flow`) y `expressions-1.0.0.jar` (`com.apigee.infra.libraries:expressions`). Se descargan del repositorio Maven de Artifact Registry `https://us-maven.pkg.dev/apigee-release/apigee-java-callout-dependencies`.
- La documentación de Google trae un proyecto de ejemplo (`api-platform-samples/doc-samples/java-hello`) con su POM.
- Las librerías de terceros se ponen como JAR aparte en `resources/java/`. No hace falta referenciarlas en la política.

## Restricciones del sandbox

Apigee aplica una política de permisos de Java a tu código **y al de todas las librerías que importes**. Si cualquier parte la viola, la ejecución falla.

| Ámbito | Permitido | Bloqueado |
|---|---|---|
| Sistema de archivos | Lectura con restricciones | Escritura, ejecución y borrado |
| Red | Conexiones salientes a hosts públicos | Direcciones *loopback*, *link-local*, *site-local*, *anylocal* y **rangos privados RFC 1918** (`10/8`, `172.16/12`, `192.168/16`). No se permite `listen` ni `accept`. |
| Entorno y proceso | Leer propiedades del sistema | `getenv`, `exitVM`, *shutdown hooks*, información de procesos, CPU y memoria |
| Reflexión y cargadores de clases | `getClassLoader`, `setContextClassLoader` | `createClassLoader`, `accessDeclaredMembers`, `suppressAccessChecks` |
| Seguridad | — | Cambiar el `SecurityManager`, *providers* o propiedades de seguridad; `setDefaultSSLContext`, `setHostnameVerifier` |
| Paquetes | — | No uses `com.apigee` ni `io.apigee` como paquete propio: están reservados. |

> [!WARNING]
> **Consecuencias prácticas del sandbox:**
> - Un JavaCallout **no puede conectarse a IPs privadas**. Para llegar a un backend interno, usa un ServiceCallout o el TargetEndpoint con la red configurada.
> - Las librerías que dependen de reflexión sobre miembros privados (algunos serializadores JSON y frameworks de inyección) pueden fallar por la falta de `accessDeclaredMembers`. Prueba la librería en un entorno real antes de diseñar sobre ella.
> - **No dependas de las librerías Java que ya trae Apigee.** Google declara ese uso no soportado: pueden cambiar o desaparecer entre versiones.

Tabla completa: [Java permission reference](https://docs.cloud.google.com/apigee/docs/api-platform/reference/java-permission-reference).

## Variables de flujo

La política no fija variables propias, salvo la de fallo. Las que necesites las escribe tu código.

## Errores

### En runtime

| Código | HTTP | Causa |
|---|---|---|
| `steps.javacallout.ExecutionError` | 500 | El código lanzó una excepción o devolvió `null`. |

> [!NOTE]
> La respuesta de error de ejemplo de la documentación muestra `errorcode: "javacallout.ExecutionError"`, sin el prefijo `steps.` que aparece en la tabla de códigos. En las FaultRules, condiciona por `fault.name Matches "ExecutionError"`, que funciona con cualquiera de las dos formas.

### Al desplegar

| Error | Causa |
|---|---|
| `ResourceDoesNotExist` | El JAR de `<ResourceURL>` no existe. |
| `JavaCalloutInstantiationFailed` | La clase de `<ClassName>` no está en el JAR. |
| `IncompatibleJavaVersion` | Clase compilada para una versión de Java no soportada. |
| `JavaClassNotFoundInJavaResource` | No se encuentra la clase en el JAR indicado. |
| `JavaClassDefinitionNotFound` | Falla la carga de la definición de la clase, a menudo por una dependencia ausente. |
| `NoAppropriateConstructor` | Falta el constructor adecuado (por ejemplo, el que recibe el `Map` cuando hay `<Properties>`). |
| `NoResourceForURL` | No se localiza el recurso de la URL. |

> [!NOTE]
> **Contradicción en la documentación oficial:** la página de X dice que la versión soportada es JDK 11, pero la fila de `IncompatibleJavaVersion` de la misma página menciona «Oracle JDK 7/8 y OpenJDK 7/8». Es un resto de la documentación de Edge. Compila con `--release 11`.

### Variables de fallo

`fault.name` y `javacallout.{policy_name}.failed`.

## Buenas prácticas

- **JAR comunes como recurso del entorno**, no copiados en cada bundle. Ahorra espacio y tiempo de despliegue.
- **Nunca la misma librería en dos sitios** (bundle y entorno) ni en dos versiones. Los conflictos de *ClassLoader* producen comportamiento no determinista en runtime.
- **No gestiones recursos** (pools de hilos, conexiones propias) desde el callout.
- **Versiona el código fuente**, no solo el JAR compilado.
- **Devuelve `ABORT` o lanza una excepción** ante un fallo, y deja una variable con el detalle para que la FaultRule construya la respuesta.

## Diferencias en Apigee Edge

- **Versión de Java:** depende de la versión de Edge (ver *Supported software and supported versions*). La página de Edge no fija ninguna en la propia política.
- La API (`Execution`, `MessageContext`), las restricciones y los errores son los mismos, y Edge también tiene su propia tabla de permisos.
- La restricción de red de la página de Edge menciona *sitelocal*, *anylocal*, *loopback* y *linklocal*. La mención explícita a los rangos RFC 1918 solo aparece en la tabla de permisos de X.

## Antipatrones

- Usar JavaCallout para lo que hace una política estándar o un JavaScript de diez líneas.
- Llamar a servicios HTTP desde Java cuando basta un ServiceCallout.
- Meter lógica de negocio o frameworks completos en el gateway.
- Empaquetar JAR enormes en cada proxy: ralentizan el arranque de los gateways.

## Fuentes

- JavaCallout policy — Apigee X/hybrid: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/java-callout-policy> (consultada directamente, contenido completo, 2026-10-22).
- How to create a Java callout: <https://docs.cloud.google.com/apigee/docs/api-platform/develop/how-create-java-callout> (consultada directamente, contenido completo, 2026-10-22).
- Java permission reference: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/java-permission-reference> (consultada directamente, contenido completo, 2026-10-22).
- Best practices for API proxy design and development: <https://docs.cloud.google.com/apigee/docs/api-platform/fundamentals/best-practices-api-proxy-design-and-development> (consultada directamente, contenido completo, 2026-10-22).
- JavaCallout policy — Apigee Edge: <https://docs.apigee.com/api-platform/reference/policies/java-callout-policy> (consultada directamente, contenido completo, 2026-10-22).
