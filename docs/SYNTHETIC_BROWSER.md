# Synthetic Browser

`Synthetic Browser` no es un proyecto separado. Es un modo futuro de **Generative App Runtime**.

## Entrada prevista

```json
{
  "kind": "synthetic-browser",
  "site": "example",
  "year": 2045,
  "style": "futuristic",
  "features": ["search", "video cards"]
}
```

## Salida

Una interfaz sintética generada en el mismo sandbox que las demás apps. Puede representar una reconstrucción estilizada del pasado o un escenario hipotético del futuro.

## Regla de producto

La UI debe indicar claramente que se trata de contenido **sintético/reconstruido**, no de una página real recuperada de Internet ni de una fuente histórica verificable.

## Reutilización del runtime

Comparte con las apps normales:

- router de modelos;
- streaming;
- AppSpec;
- validación;
- CSP/iframe sandbox;
- versionado;
- biblioteca/cache;
- medición de tokens y costo.
