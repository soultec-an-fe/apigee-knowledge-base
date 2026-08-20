---
id: proxies-condiciones
titulo: Condiciones y pattern matching
area: proxies
tags: [condition, operadores, matchespath, javaregex, glob, expresiones]
aplica_a: [apigee-x, apigee-hybrid]
fuente: https://docs.apigee.com/api-platform/reference/conditions-reference
revisado: 2026-08-20
---

# Condiciones y pattern matching

Las `<Condition>` controlan qué flujos, pasos, RouteRules y FaultRules se ejecutan. Su sintaxis es propia de Apigee.

## Tabla completa de operadores

| Símbolo | Forma en palabras | Significado |
|---|---|---|
| `!` | `Not`, `not` | Negación unaria |
| `=` | `Equals`, `Is` | Igual (**sensible a mayúsculas**) |
| `!=` | `NotEquals`, `IsNot` | Distinto (sensible a mayúsculas) |
| `:=` | `EqualsCaseInsensitive` | Igual, **ignorando** mayúsculas |
| `>` / `&gt;` | `GreaterThan` | Mayor que (numérico) |
| `>=` / `&gt;=` | `GreaterThanOrEquals` | Mayor o igual |
| `&lt;` | `LesserThan` | Menor que |
| `&lt;=` | `LesserThanOrEquals` | Menor o igual |
| `&&` | `And`, `and` | Conjunción lógica |
| `\|\|` | `Or`, `or` | Disyunción lógica |
| `~~` | `JavaRegex` | Empareja una regex `javax.util.regex` (sensible a mayúsculas) |
| `~` | `Matches`, `Like` | Empareja un patrón glob con comodín `*` |
| `~/` | `MatchesPath`, `LikePath` | Empareja una expresión de **ruta** |
| `=\|` | `StartsWith` | Empareja los primeros caracteres de una cadena |

> [!WARNING]
> En XML hay que **escapar** `<`, `>` y `&`. Usa `&lt;`, `&gt;` y `&amp;&amp;`, o mejor las formas en palabras (`LesserThan`, `and`) que son más legibles y no requieren escape.

## Reglas de sintaxis

1. **Se aplica la precedencia de Java** a todos los operadores.
2. **Se requiere espacio antes y después** de cada operador.
3. **Los operadores no pueden ser nombres de variable.**
4. Para usar un operador como contenido literal, encierra en comillas simples: `'request.header.help!me'`.
5. **Los operadores aritméticos (`+`, `-`, `*`, `/`, `%`) NO están soportados.** Si necesitas aritmética, hazla en una política `JavaScript`.

## Comodines de pattern matching

### Glob con `~` (Matches / Like)

- `*` — un único elemento de ruta
- `**` — varios niveles de URI
- `%` — carácter de escape (`%{user%}` empareja el literal `{user}`)

```
Patrón          Empareja                      No empareja
/*/a/           /x/a/  ·  /y/a/               /x/y/a/
/*/a/**         /x/a/b/c/d                    /a/b
/statuses/**    /statuses/1  ·  /statuses/a/b  /status
```

### MatchesPath con `~/`

Diseñado para rutas de recurso. Es el operador que debes usar contra `proxy.pathsuffix`.

```xml
<Condition>(proxy.pathsuffix MatchesPath "/pedidos/*")</Condition>
```

### JavaRegex con `~~`

Regex completa. Potente pero cara.

```xml
<Condition>(request.header.x-trace-id ~~ "^[0-9a-f]{32}$")</Condition>
```

> [!CAUTION]
> **No uses cuantificadores greedy** (`.*`, `.+`) en `RegularExpressionProtection` ni en condiciones sobre payloads grandes: es un [antipatrón documentado](../09-antipatrones/01-catalogo-antipatrones.md) que provoca backtracking catastrófico y consumo de CPU.

## Ejemplos por caso de uso

### Enrutar por verbo y ruta

```xml
<Condition>(proxy.pathsuffix MatchesPath "/pedidos") and (request.verb = "GET")</Condition>
```

### Un recurso con ID

```xml
<Condition>(proxy.pathsuffix MatchesPath "/pedidos/*") and (request.verb = "GET")</Condition>
```

### Varios verbos

```xml
<Condition>(request.verb = "POST") or (request.verb = "PUT") or (request.verb = "PATCH")</Condition>
```

### Cabecera ausente

```xml
<Condition>request.header.authorization is null</Condition>
```

### Cabecera presente y con valor

```xml
<Condition>(request.header.x-api-key != null) and (request.header.x-api-key != "")</Condition>
```

### Content-type (insensible a mayúsculas)

```xml
<Condition>request.header.content-type := "application/json"</Condition>
```

### Rango de códigos de estado

```xml
<Condition>(response.status.code GreaterThanOrEquals 500)</Condition>
```

### Códigos concretos

```xml
<Condition>(response.status.code = 503) or (response.status.code = 400)</Condition>
```

### Contenido del payload

```xml
<Condition>(message.content Like "*unavailable*")</Condition>
```

### Detectar fallo de una política con continueOnError

```xml
<Condition>(oauthV2.VAK-VerificarApiKey.failed = "true")</Condition>
```

### Nombre de fallo en una FaultRule

```xml
<Condition>(fault.name = "QuotaViolation")</Condition>
```

### Combinar producto y entorno

```xml
<Condition>(apiproduct.name = "premium") and (environment.name = "prod")</Condition>
```

### Excluir rutas del rate limiting

```xml
<Step>
    <Name>Q-Cuota</Name>
    <Condition>!(proxy.pathsuffix MatchesPath "/health") and !(proxy.pathsuffix MatchesPath "/metrics")</Condition>
</Step>
```

## Condiciones vacías y catch-all

Un `<Flow>` **sin** `<Condition>` empareja siempre. Una `<RouteRule>` sin `<Condition>` es la ruta por defecto. En ambos casos **deben ir los últimos** en su lista, porque la evaluación es de arriba abajo y la primera coincidencia gana.

```xml
<Flows>
    <Flow name="Especifico"><Condition>...</Condition></Flow>
    <Flow name="CatchAll"/>   <!-- sin condición, va al final -->
</Flows>
```

## Depuración de condiciones

Si una condición no dispara:

1. Abre una **sesión de Trace** y busca el valor real de la variable en ese punto del flujo.
2. Comprueba el **ámbito**: `response.*` no existe en el request PreFlow; `request.*` no existe en el error flow.
3. Verifica **mayúsculas**: `=` es sensible; usa `:=` si no debe serlo.
4. Confirma que hay **espacios alrededor del operador**.
5. Para rutas, comprueba si estás usando `proxy.pathsuffix` (sin basepath) o `request.path` (con basepath). Es la confusión más común.

| Variable | Con basepath `/pedidos/v1`, URL `/pedidos/v1/items?x=1` |
|---|---|
| `proxy.basepath` | `/pedidos/v1` |
| `proxy.pathsuffix` | `/items` |
| `request.path` | `/pedidos/v1/items` |
| `request.uri` | `/pedidos/v1/items?x=1` |
| `request.querystring` | `x=1` |

## Fuentes

- <https://docs.apigee.com/api-platform/reference/conditions-reference>
- <https://cloud.google.com/apigee/docs/api-platform/fundamentals/flow-variables-and-conditions>
