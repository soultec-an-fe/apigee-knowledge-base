---
id: proxies-shared-flows
titulo: Shared flows y flow hooks
area: proxies
tags: [shared-flow, flowcallout, flow-hook, reutilizacion, preproxy, posttarget]
aplica_a: [apigee-x, apigee-hybrid]
fuente: https://cloud.google.com/apigee/docs/api-platform/fundamentals/shared-flows
revisado: 2026-08-20
---

# Shared flows y flow hooks

Un **shared flow** es una colección reutilizable de políticas, desplegable de forma independiente, invocable desde cualquier proxy. Es el mecanismo de DRY de Apigee.

## Cuándo usarlos

| Señal | Acción |
|---|---|
| La misma secuencia de políticas está copiada en 3+ proxies | Extraer a shared flow |
| Una política de seguridad debe aplicarse a **todos** los proxies sin excepción | Shared flow + **flow hook** |
| Cada equipo reimplementa el formato de error corporativo | Shared flow de manejo de errores |
| El logging debe ser idéntico en toda la plataforma | Shared flow en el hook `PostProxy` |

## Estructura de un shared flow

Casi idéntica a un proxy, pero **sin** endpoints ni RouteRules:

```
sharedflowbundle/
├── comun-seguridad.xml
├── sharedflows/
│   └── default.xml
├── policies/
│   ├── VAK-VerificarApiKey.xml
│   ├── SA-FrenoDePicos.xml
│   └── Q-Cuota.xml
└── resources/
```

`sharedflowbundle/comun-seguridad.xml`:

```xml
<SharedFlowBundle revision="1" name="comun-seguridad">
    <DisplayName>Seguridad común</DisplayName>
    <SharedFlows>
        <SharedFlow>default</SharedFlow>
    </SharedFlows>
</SharedFlowBundle>
```

`sharedflowbundle/sharedflows/default.xml`:

```xml
<SharedFlow name="default">
    <Step>
        <Name>VAK-VerificarApiKey</Name>
        <Condition>!(proxy.pathsuffix MatchesPath "/health")</Condition>
    </Step>
    <Step><Name>SA-FrenoDePicos</Name></Step>
    <Step><Name>Q-Cuota</Name></Step>
</SharedFlow>
```

> [!NOTE]
> Un `<SharedFlow>` es una **lista plana de `<Step>`**. No tiene PreFlow/PostFlow ni `<Flows>` condicionales. Las condiciones van en cada Step.

## Despliegue

Los shared flows se despliegan a un environment igual que un proxy, y **deben estar desplegados antes** de que un proxy los invoque.

```bash
apigeecli sharedflows create bundle \
  --name comun-seguridad --sf-folder ./sharedflowbundle \
  --org "$ORG" --token "$(gcloud auth print-access-token)"

apigeecli sharedflows deploy \
  --name comun-seguridad --rev 1 \
  --org "$ORG" --env prod --ovr --wait \
  --token "$(gcloud auth print-access-token)"
```

Límite: **75 shared flows por entorno** en Apigee X (10 en hybrid 2021). Se retienen 250 revisiones.

## Invocación explícita: FlowCallout

Desde el proxy consumidor:

```xml
<FlowCallout continueOnError="false" enabled="true" name="FC-Seguridad">
    <DisplayName>Aplicar seguridad común</DisplayName>
    <SharedFlowBundle>comun-seguridad</SharedFlowBundle>
</FlowCallout>
```

Y se referencia como cualquier política:

```xml
<PreFlow name="PreFlow">
    <Request>
        <Step><Name>FC-Seguridad</Name></Step>
    </Request>
</PreFlow>
```

### Pasar parámetros

`FlowCallout` admite `<Parameters>`, accesibles dentro del shared flow con el prefijo `flowcallout.<nombre>.`:

```xml
<FlowCallout name="FC-Cuota">
    <SharedFlowBundle>comun-cuota</SharedFlowBundle>
    <Parameters>
        <Parameter name="limite">1000</Parameter>
        <Parameter name="unidad">hour</Parameter>
    </Parameters>
</FlowCallout>
```

Dentro del shared flow:

```xml
<Quota name="Q-Dinamica">
    <Allow countRef="flowcallout.FC-Cuota.limite" count="100"/>
    <Interval>1</Interval>
    <TimeUnit ref="flowcallout.FC-Cuota.unidad">hour</TimeUnit>
</Quota>
```

> [!TIP]
> Alternativa más simple y habitual: el proxy asigna variables con `AssignMessage` **antes** del FlowCallout, y el shared flow las lee. El contexto de variables es compartido.

## Invocación implícita: flow hooks

Un **flow hook** ata un shared flow a un **punto del pipeline a nivel de environment**. Se ejecuta para **todos** los proxies de ese entorno, sin que los proxies lo sepan ni puedan evitarlo.

| Hook | Cuándo se ejecuta |
|---|---|
| **PreProxy** | Antes del PreFlow del ProxyEndpoint |
| **PostProxy** | Después del PostFlow del ProxyEndpoint (respuesta) |
| **PreTarget** | Antes del PreFlow del TargetEndpoint |
| **PostTarget** | Después del PostFlow del TargetEndpoint (respuesta) |

Pipeline con hooks:

```
──► [FH PreProxy] ► ProxyEndpoint Request ► [FH PreTarget] ► TargetEndpoint Request
                                                                        │
                                                                     BACKEND
                                                                        │
◄── [FH PostProxy] ◄ ProxyEndpoint Response ◄ [FH PostTarget] ◄ TargetEndpoint Response
```

Configuración (por entorno, no en el bundle):

```bash
apigeecli flowhooks attach \
  --name PreProxy \
  --sharedflow comun-seguridad \
  --org "$ORG" --env prod \
  --token "$(gcloud auth print-access-token)"
```

### Cuándo usar hook y cuándo FlowCallout

| Situación | Mecanismo |
|---|---|
| Política **obligatoria** en toda la plataforma (auditoría, seguridad de base) | Flow hook |
| Comportamiento **opcional** que cada proxy decide adoptar | FlowCallout |
| Lógica específica de un dominio o equipo | FlowCallout |
| Logging corporativo unificado | Flow hook `PostProxy` |

> [!CAUTION]
> Los flow hooks son **invisibles desde el bundle del proxy**. Un desarrollador puede pasar horas depurando un 401 sin entender de dónde sale, porque el `VerifyAPIKey` está en un hook. Documenta agresivamente qué hooks hay activos en cada entorno, y prevé exclusiones (`/health`, `/metrics`) dentro del propio shared flow.

## Composición

Un shared flow **puede** llamar a otro con `FlowCallout`. Mantén la profundidad baja:

```
comun-todo
  ├─ FlowCallout → comun-seguridad
  ├─ FlowCallout → comun-cabeceras
  └─ FlowCallout → comun-logging
```

> [!WARNING]
> Evita la recursión. Un shared flow que se llama a sí mismo directa o indirectamente agota el pipeline.

## Manejo de errores dentro de un shared flow

Un shared flow **no tiene `<FaultRules>` propias**. Si una política falla dentro de él, el error se propaga al proxy invocador y lo maneja **la FaultRule del proxy**.

Consecuencia práctica: los `fault.name` que produce el shared flow deben estar contemplados en las FaultRules de todos los proxies. Por eso lo habitual es tener también un **shared flow de manejo de errores** invocado desde la `DefaultFaultRule` de cada proxy:

```xml
<DefaultFaultRule name="fallback">
    <Step><Name>FC-ManejoErrores</Name></Step>
    <AlwaysEnforce>true</AlwaysEnforce>
</DefaultFaultRule>
```

## Buenas prácticas

1. **Responsabilidad única.** Un shared flow para seguridad, otro para logging, otro para cabeceras. No un `comun-todo` monolítico.
2. **Nombres con prefijo de dominio**: `sf-seguridad-oauth`, `sf-logging-cloudlogging`.
3. **Versiona en el nombre cuando rompas compatibilidad**: `sf-seguridad-v2`. Un cambio incompatible en un shared flow desplegado afecta a **todos** los proxies a la vez.
4. **Despliega el shared flow antes que los proxies** que lo consumen, y despublica después.
5. **Prueba el shared flow de forma aislada** con un proxy de prueba dedicado.
6. **Documenta las variables de entrada y salida** en el `<Description>` del bundle.
7. **Contempla exclusiones** (`/health`, `/metrics`, rutas públicas) dentro del shared flow, no en cada proxy.

## Fuentes

- <https://cloud.google.com/apigee/docs/api-platform/fundamentals/shared-flows>
- <https://cloud.google.com/apigee/docs/api-platform/fundamentals/flow-hooks>
- <https://cloud.google.com/apigee/docs/api-platform/reference/limits>
