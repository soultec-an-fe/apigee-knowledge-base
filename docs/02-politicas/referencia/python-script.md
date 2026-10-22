---
id: politica-python-script
titulo: PythonScript — referencia completa
area: politicas
tags: [pythonscript, python, jython, script, extension, extensible]
aplica_a: [apigee-x, apigee-hybrid, apigee-edge]
elemento_xml: Script
tipo_politica: extensible
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/python-script-policy
fuente_edge: https://docs.apigee.com/api-platform/reference/policies/python-script-policy
revisado: 2026-10-22
---

# PythonScript — referencia completa

> [!NOTE]
> **Tipo:** Extensible. **Elemento raíz:** `<Script>`.
> **Aplica a:** Apigee X, hybrid y Edge. **Puede no estar disponible en todos los planes de Apigee**: compruébalo en la página de precios.

PythonScript ejecuta un script **Python** en un punto del flujo. La política no contiene código: referencia un archivo `.py` guardado como recurso.

| Aspecto | Detalle |
|---|---|
| Intérprete | **Jython 2.5.2**: sintaxis de **Python 2.5**, sobre la JVM |
| Librerías | Solo **Python puro**; nada con extensiones nativas (C) |
| Acceso al contexto | Objeto `flow` (`flow.getVariable`, `flow.setVariable`), equivalente al modelo de objetos de JavaScript |
| Recursos | `/apiproxy/resources/py`, o a nivel de entorno u organización para reutilizar |

> [!WARNING]
> Jython 2.5.2 implementa una versión de Python **muy antigua** (sin soporte desde hace más de una década; Python 2 dejó de recibir soporte en 2020). No tiene f-strings, `print()` como función ni la mayoría de librerías modernas. Para lógica nueva, prefiere [JavaScript](../04-extension.md) o JavaCallout. Esta valoración no es de la documentación de Apigee.

> [!CAUTION]
> La documentación advierte que hay que **limitar o deshabilitar el acceso SSH** a los recursos de seguridad para que esta política no se use para leer archivos internos, el usuario actual, la lista de procesos o el uso de CPU/memoria. El código Python corre con más capacidades de sistema de lo que parece: revísalo como código de servidor.

## Sintaxis completa

```xml
<Script name="PY-Nombre" continueOnError="false" enabled="true">
  <DisplayName>Nombre legible</DisplayName>
  <ResourceURL>py://principal.py</ResourceURL>
  <IncludeURL>py://utilidades.py</IncludeURL>
</Script>
```

## Atributos del elemento raíz

| Atributo | Obligatorio | Default | Qué hace |
|---|---|---|---|
| `name` | Sí | — | Nombre interno; da nombre a `pythonscript.{name}.failed`. |
| `continueOnError` | No | `false` | Con `true`, un error del script no corta el flujo. |
| `enabled` | No | `true` | Con `false` no se ejecuta. |
| `async` | No | `false` | **Obsoleto.** |

## Elementos hijos

| Elemento | Obligatorio | Resumen |
|---|---|---|
| `<ResourceURL>` | **Sí** | Script principal: `py://archivo.py`. |
| `<IncludeURL>` | No | Dependencias que se cargan **antes**, en el orden en que aparecen. Puede haber varias. |

Si subes los `.py` a nivel de entorno u organización con la API, hazlo como `multipart/form-data` (opción `-F` de curl).

## Variables de flujo

No publica variables propias; el script lee y escribe las que necesite con `flow.getVariable` / `flow.setVariable`.

## Errores

### En runtime

| Código | HTTP | Causa |
|---|---|---|
| `steps.script.ScriptEvaluationFailed` | 500 | Error en el script (p. ej. `NameError`, `ZeroDivisionError`). |

La tabla habla de `ScriptEvaluationFailed`, mientras que la descripción, el ejemplo de respuesta y la FaultRule usan `ScriptExecutionFailed`. Comprueba en Debug cuál recibes.

### Al desplegar

| Error | Causa |
|---|---|
| `InvalidResourceUrlFormat` | `<ResourceURL>` o `<IncludeURL>` con formato inválido. |
| `InvalidResourceUrlReference` | El archivo referenciado no existe en el proxy, el entorno ni la organización. |

### Variables de fallo

`fault.name` y `pythonscript.{name}.failed`.

## Ejemplo

```python
# principal.py (Jython 2.5)
import base64

usuario = flow.getVariable("private.backend.usuario")
clave = flow.getVariable("private.backend.password")
credencial = base64.encodestring("%s:%s" % (usuario, clave)).strip()
flow.setVariable("flujo.authorization", "Basic " + credencial)
```

Para este caso concreto, [BasicAuthentication](basic-authentication.md) hace lo mismo sin código.

## Diferencias en Apigee Edge

Sin diferencias funcionales documentadas.

## Antipatrones

- Escribir lógica nueva en Jython 2.5 cuando hay alternativas modernas.
- Depender de librerías con código nativo.
- Usar Python para lo que resuelve una política estándar.

## Fuentes

- PythonScript policy — Apigee X/hybrid: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/python-script-policy> (consultada directamente, contenido completo, 2026-10-22).
- Python Script policy — Apigee Edge: <https://docs.apigee.com/api-platform/reference/policies/python-script-policy> (consultada directamente, 2026-10-22).
