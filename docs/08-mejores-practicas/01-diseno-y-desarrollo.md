---
id: practicas-diseno
titulo: Mejores prácticas de diseño y desarrollo
area: practicas
tags: [best-practices, diseno, desarrollo, google, recomendaciones]
aplica_a: [apigee-x, apigee-hybrid]
fuente: https://docs.apigee.com/api-platform/fundamentals/best-practices-api-proxy-design-and-development
revisado: 2026-08-20
---

# Mejores prácticas de diseño y desarrollo

Recopilación de las recomendaciones oficiales de Google, agrupadas por área.

---

## Estándares de desarrollo

### Comentarios y documentación

- **Pon comentarios en línea** en las configuraciones de ProxyEndpoint y TargetEndpoint. Mejoran la legibilidad de un flujo, sobre todo cuando el nombre del archivo de política no es suficientemente descriptivo.
- **Haz comentarios útiles.** Evita los obvios (`<!-- verifica la api key -->` sobre un `VerifyAPIKey` no aporta nada).
- Mantén **indentación, espaciado y alineación vertical consistentes**.

### Framework-style coding

- Guarda los recursos del proxy en tu propio **sistema de control de versiones**, para poder reutilizarlos entre entornos de desarrollo locales.
- Implementa funciones **reutilizables y especializadas** siguiendo el principio DRY. Ejemplo: una política dedicada `ExtractVariables.ExtractRequestParameters`.
- **Elimina políticas y recursos sin usar**: ralentizan el despliegue.

---

## Diseño del proxy

- ⚠️ **No llames a la API de gestión desde dentro de un proxy.** Usa políticas.
- **Usa políticas y funcionalidad nativa siempre que sea posible**, en lugar de programar toda la lógica en JavaScript, Java o Python.
- **Organiza los flujos** con múltiples `<Flow>` de una sola condición, en lugar de múltiples `<Step>` con condición colgando del mismo PreFlow o PostFlow.
- **Crea un proxy por defecto** con `<BasePath>/</BasePath>` como red de seguridad para peticiones que no encajan en ningún basepath.
- **Usa recursos `TargetServer`** para desacoplar la configuración de las URLs concretas del backend.
- **Define la RouteRule por defecto la última.** Las RouteRules se evalúan **de arriba abajo**.
- **Límite del bundle: 15 MB.**
- **Un solo ProxyEndpoint por proxy.** Ver [antipatrones](../09-antipatrones/01-catalogo-antipatrones.md).
- **No superes ~3.000 basepaths por entorno o environment group.** Por encima, aumenta la latencia de **todos** los despliegues, nuevos y existentes.

---

## CORS

- **Habilita CORS antes de publicar** APIs que vayan a consumirse desde el navegador.
- ⚠️ **Si usas una política de caché, asegúrate de que la respuesta de CORS no se cachea.**

Ver [políticas de mediación](../02-politicas/03-mediacion.md#cors).

---

## Tamaño del payload

- Restricción de **10 MB** para evitar problemas de memoria. Superarlo produce `protocol.http.TooBigBody`.
- Límites vigentes en Apigee X: **30 MB bufferizado**, **10 MB en streaming**.

Estrategias recomendadas:

- **Hacer streaming** de peticiones y respuestas. Con la advertencia crítica: **las políticas pierden acceso al contenido del mensaje**.
- Para paginar o trocear, hacerlo a nivel de API, no aumentando los buffers.

> ⚠️ **Solo Edge:** en Private Cloud se podía ajustar `HTTPRequest.body.buffer.limit` y `HTTPResponse.body.buffer.limit` en `http.properties`, `router.properties` o `message-processor.properties` (valor por defecto: `10m`). No aplica a Apigee X.

---

## Manejo de fallos

- **Usa FaultRules para todo el manejo de errores.**
- **Construye las respuestas de error con `AssignMessage`** dentro del flujo de la FaultRule.
- **Ejecuta los `AssignMessage` condicionalmente** según el tipo de fallo.
- **Incluye siempre un manejador catch-all** por defecto.
- **Ajusta las respuestas de error al formato estándar** de tu empresa o proyecto.
- **Usa mensajes de error legibles y con significado** que sugieran una solución al problema.

Ver [manejo de errores](../05-operacion/01-manejo-de-errores.md).

---

## Persistencia

### Key/Value Maps

- Úsalos **solo para conjuntos de datos limitados**. No están diseñados para almacenamiento a largo plazo.
- Ten en cuenta el impacto en rendimiento: los datos viven en **Cassandra**.

### Caché de respuesta

- **No caches respuestas no exitosas ni peticiones que no sean GET:**
  ```xml
  <SkipCachePopulation>response.status.code != 200 or request.verb != "GET"</SkipCachePopulation>
  ```
- **Cachea con un content-type consistente** (siempre XML o siempre JSON; convierte antes si hace falta).
- **Asegúrate de que la cache key es suficiente.** `request.querystring` suele servir como identificador único.
- **No incluyas la API key (`client_id`) en la cache key** salvo que sea imprescindible.
- **Configura intervalos de expiración adecuados** para evitar lecturas obsoletas.
- **Ejecuta la política de población en el PostFlow del response del ProxyEndpoint** (después de la mediación).
- **Ejecuta la política de lookup en el PreFlow del request del ProxyEndpoint.**
- Mantén el lookup cerca de la petición del cliente y la población cerca de la respuesta.
- Con **varias políticas de caché**: condiciones mutuamente excluyentes y **recursos de caché distintos**.

Ver [caching y persistencia](../05-operacion/04-caching-y-persistencia.md).

---

## Política vs código personalizado

Orden de preferencia:

1. **Políticas nativas primero**: están endurecidas, optimizadas y soportadas.
2. **`AssignMessage` y `ExtractVariables`** en lugar de JavaScript siempre que sea posible.
3. **JavaScript** antes que Python.
4. **Java** si el rendimiento es prioritario.

### JavaScript

- Úsalo para manipulación intuitiva del payload o parseo complejo.
- Soporta codificación/decodificación **Base64** e iteración de JSON.
- **Tiene límite de tiempo** (bloquea bucles infinitos).
- **Usa siempre Steps de JavaScript**; coloca los archivos en la carpeta de recursos `jsc`.
- **La política de tipo `Javascript` precompila en el despliegue**: detecta errores de sintaxis antes de producción.
- Soporta XML vía **E4X**.

### Java

- ⚠️ **Depender de las librerías Java incluidas en Apigee no está soportado.**
- Úsalo si el rendimiento es lo más prioritario o si la lógica no puede escribirse en JavaScript.
- **Versiona los archivos fuente Java** en control de versiones.

### Python

- **Evítalo salvo que sea absolutamente necesario**: introduce un cuello de botella de rendimiento porque se interpreta en runtime.
- No existe en Apigee X.

---

## Script callouts (Java, JavaScript, Python)

- **Usa try/catch global** o su equivalente.
- **Lanza excepciones con significado** y captúralas adecuadamente para las respuestas de fallo.
- **Lanza y captura excepciones pronto.** Evita el catch-all global al final.
- **Comprueba null/undefined** en variables de flujo opcionales.
- ⚠️ **No hagas peticiones HTTP/S dentro de un script callout.** Usa la política `ServiceCallout`.

**Específico de Java:**
- Usa `context.getMessage()` en lugar de métodos separados para request y response.
- **Importa las librerías a la organización o al entorno**; exclúyelas del JAR.
- **Importa los JAR vía la API de recursos de Apigee**, no en la carpeta de recursos del proxy.
- **No uses Java para gestionar recursos** (thread pools, etc.).

Ver [políticas de extensión](../02-politicas/04-extension.md).

---

## ServiceCallouts

- Válido para **encadenar proxies**; evita callouts recursivos infinitos.
- Para proxies de la **misma organización y entorno**, usa una **conexión local** para evitar la sobrecarga de red.
- **Construye el mensaje de petición con `AssignMessage`.**
- ⚠️ **El protocolo de la URL debe especificarse literalmente**: no se pueden usar variables para la parte del protocolo.
- **Usa variables separadas** para el dominio y la ruta.
- **Almacena la respuesta en una variable de mensaje separada** para preservar el payload original.

---

## Acceso a entidades

- Con la política `AccessEntity`, **busca las apps por `uuid` en lugar de por nombre**: es más rápido.

---

## Logging

- **Usa una política syslog consistente** en todos los bundles para tener un formato estandarizado.

Ver [analytics y monitoreo](../05-operacion/03-analytics-monitoreo.md).

---

## Monitorización

- En Apigee gestionado, **Google Cloud Operations monitoriza los componentes de la plataforma**.
- **Usa Analytics** para monitorización no crítica (porcentajes de error, tendencias).
- **Usa la herramienta Trace** para depurar problemas de runtime, tanto en desarrollo como en producción.

Ver [debug y trace](../05-operacion/02-debug-trace.md).

---

## Seguridad

- **Usa la política `AccessControl`** para restringir por dirección IP el acceso a los entornos de test.
- **Aplica siempre políticas de protección de contenido** (JSON/XML) a los proxies de producción:
  - `JSONThreatProtection`
  - `XMLThreatProtection`
  - `RegularExpressionProtection`
  - `SOAPMessageValidation`

Ver [threat protection](../03-seguridad/05-threat-protection.md).

## Fuentes

- <https://docs.apigee.com/api-platform/fundamentals/best-practices-api-proxy-design-and-development>
- <https://cloud.google.com/apigee/docs/api-platform/fundamentals/best-practices-api-proxy-design-and-development>
