---
id: fundamentos-glosario
titulo: Glosario de Apigee
area: fundamentos
tags: [glosario, terminologia, definiciones]
aplica_a: [apigee-x, apigee-hybrid]
fuente: https://cloud.google.com/apigee/docs/api-platform/get-started/what-apigee
revisado: 2026-08-20
---

# Glosario de Apigee

Términos ordenados alfabéticamente. Se conserva el nombre en inglés porque es el que aparece en la configuración XML y en las APIs.

| Término (EN) | Español | Definición |
|---|---|---|
| **AppGroup** | Grupo de apps | Agrupación de developer apps bajo una entidad común (p. ej. una empresa cliente). Hasta 30.000 apps por AppGroup. |
| **API product** | Producto de API | Paquete de acceso: agrupa proxies/operaciones y define cuota, scopes y nivel de acceso. Es lo que consume una app. |
| **API proxy** | Proxy de API | Unidad desplegable. Bundle XML con ProxyEndpoint, TargetEndpoint, políticas y recursos. |
| **Basepath** | Ruta base | Prefijo de URL declarado en el `<HTTPProxyConnection>` que identifica al proxy. Clave de enrutamiento. |
| **Bundle** | Paquete | Estructura de directorios `apiproxy/` empaquetada en ZIP. Máx. 15 MB. |
| **Conditional Flow** | Flujo condicional | Flujo que solo se ejecuta si su `<Condition>` es verdadera. Solo se ejecuta el **primero** que empareje. |
| **continueOnError** | — | Atributo de política. Con `true`, un fallo no entra en error flow; deja `policy.failed = true` en el flujo normal. |
| **DefaultFaultRule** | Regla de fallo por defecto | Manejador de errores que se ejecuta si ninguna FaultRule empareja. Con `<AlwaysEnforce>true</AlwaysEnforce>` se ejecuta siempre. |
| **Developer** | Desarrollador | Entidad registrada en la org que posee apps. Hasta 1 millón por org. |
| **Developer app** | App de desarrollador | Cliente registrado. Posee credenciales (consumer key/secret) y está suscrito a API products. |
| **Environment** | Entorno | Espacio de despliegue dentro de una org. |
| **Environment group** | Grupo de entorno | Agrupación de environments que declara los **hostnames**. Reemplaza a los virtual hosts de Edge. |
| **FaultRule** | Regla de fallo | Bloque condicional que maneja un error. Ver [manejo de errores](../05-operacion/01-manejo-de-errores.md). |
| **Flow hook** | Gancho de flujo | Punto de enganche a nivel de environment donde se ejecuta un shared flow automáticamente: PreProxy, PostProxy, PreTarget, PostTarget. |
| **Flow variable** | Variable de flujo | Par nombre/valor del contexto de ejecución (`request.verb`, `response.status.code`, …). |
| **KVM** (KeyValueMap) | Mapa clave-valor | Almacén clave-valor con scope de org o environment. Clave ≤ 2 KB, valor ≤ 10 KB. Puede ser cifrado. |
| **Message Processor (MP)** | Procesador de mensajes | Componente del runtime que ejecuta el pipeline del proxy. |
| **Organization (org)** | Organización | Contenedor raíz. 1:1 con un proyecto de Google Cloud en X y hybrid. |
| **Policy** | Política | Módulo XML declarativo que ejecuta una acción (validar, transformar, limitar…). |
| **PostClientFlow** | — | Flujo que se ejecuta **después** de enviar la respuesta al cliente. Solo admite MessageLogging y DataCapture. |
| **PreFlow / PostFlow** | Flujo previo / posterior | Flujos incondicionales que envuelven a los Conditional Flows. |
| **ProxyEndpoint** | Endpoint de proxy | Cara del proxy hacia el cliente: basepath, flujos y RouteRules. Máx. 10 por proxy; se recomienda **1**. |
| **PropertySet** | Conjunto de propiedades | Archivo `.properties` empaquetado en el bundle con valores de configuración de solo lectura. Se lee con `ReadPropertySet` o `propertyset.*`. |
| **Revision** | Revisión | Versión numerada e inmutable de un proxy o shared flow. Se retienen 250. |
| **RouteRule** | Regla de enrutamiento | Selecciona el TargetEndpoint. Se evalúan **de arriba abajo**; la última debe ser la de por defecto (sin condición). |
| **Shared flow** | Flujo compartido | Colección reutilizable de políticas, desplegable e invocable con `FlowCallout`. |
| **SpikeArrest** | Freno de picos | Política de suavizado de tráfico instantáneo. **No** es un contador de negocio; para eso está Quota. |
| **Step** | Paso | Referencia a una política dentro de un flujo, con `<Condition>` opcional. |
| **TargetEndpoint** | Endpoint de destino | Cara del proxy hacia el backend: URL o TargetServer, flujos, timeouts, TLS. Máx. 1.000 por proxy. |
| **TargetServer** | Servidor de destino | Recurso con scope de environment que abstrae host/puerto/TLS del backend. Permite cambiar el backend sin redeploy del proxy. |
| **Trace / Debug session** | Sesión de depuración | Captura del recorrido de una petición con el valor de cada variable en cada paso. |
| **Virtual host** | Host virtual | ⚠️ **Solo Edge.** En Apigee X su función la cumplen los environment groups. |

## Prefijos de variables más usados

| Prefijo | Ámbito |
|---|---|
| `request.*` | Petición entrante del cliente |
| `response.*` | Respuesta del backend |
| `message.*` | Contenedor contextual; el único disponible en el error flow |
| `proxy.*` | Configuración del ProxyEndpoint (`basepath`, `pathsuffix`) |
| `target.*` | Conexión con el backend |
| `client.*` | Conexión TCP/TLS con el cliente |
| `system.*` | Hora, región, pod |
| `error.*` / `fault.*` | Solo en error flow |
| `ratelimit.*` | Contadores de Quota y SpikeArrest |
| `apiproduct.*` | Contexto resuelto por VerifyAPIKey / OAuthV2 |

Referencia completa en [variables de flujo](../01-proxies/04-variables-de-flujo.md).

## Fuentes

- <https://cloud.google.com/apigee/docs/api-platform/get-started/what-apigee>
- <https://docs.apigee.com/api-platform/reference/variables-reference>
