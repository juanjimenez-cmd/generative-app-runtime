# AppSpec — borrador de contrato

`AppSpec` será la representación estructurada entre la petición en lenguaje natural y el código ejecutable.

## Objetivos

- validar permisos antes de generar código;
- permitir cache y reutilización;
- hacer el router de modelos más explicable;
- soportar distintos tipos de artefacto sin duplicar pipelines;
- facilitar generación incremental.

## Borrador

```json
{
  "schema_version": "0.1",
  "kind": "app",
  "title": "Calculadora de amortización",
  "description": "Calcula cuotas y tabla mensual",
  "runtime": "browser",
  "inputs": [],
  "outputs": [],
  "features": [],
  "permissions": {
    "network": "none",
    "files": "user-selected-only",
    "clipboard": false,
    "camera": false,
    "microphone": false,
    "geolocation": false
  },
  "persistence": "optional",
  "lifecycle": "reusable"
}
```

## Tipos previstos

- `app`
- `dashboard`
- `tool`
- `synthetic-browser`
- `simulation`
- `document`
- `game`

El esquema final deberá ser versionado y validado antes de pasar al generador de implementación.
