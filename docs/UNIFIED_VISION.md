# Unified Vision — Generative App Runtime

Este documento unifica las dos líneas de ideas que en conversaciones distintas parecían proyectos separados.

## Idea central

Generative App Runtime no es solo un generador de HTML. La visión completa es un **runtime de software generado bajo demanda**: el usuario describe una necesidad y el sistema construye, valida, ejecuta y opcionalmente conserva una aplicación temporal o reutilizable.

```text
Lenguaje natural
   ↓
AppSpec estructurado
   ↓
Validador / policy engine
   ↓
Generador de implementación
   ↓
Sandbox / runtime JIT
   ↓
App, dashboard, simulador, juego, documento o navegador sintético
```

## AppSpec

Antes de generar código, una fase futura convertirá la petición del usuario en una especificación JSON estable. Ejemplo conceptual:

```json
{
  "kind": "app",
  "title": "Calculadora de amortización",
  "inputs": ["capital", "tasa", "plazo"],
  "features": ["tabla", "exportar CSV"],
  "runtime": "browser",
  "network": "none",
  "persistence": "optional"
}
```

El AppSpec separa intención de implementación, facilita validación, cache, regeneración y evolución incremental.

## Modos del mismo runtime

### 1. On-demand apps
Micro-apps generadas para resolver una tarea concreta y opcionalmente guardadas.

### 2. Generative dashboards
Paneles creados a partir de una necesidad o dataset, sin mantener una interfaz fija para cada caso.

### 3. Temporary JIT tools
Herramientas que se crean, usan y descartan. El runtime base permanece instalado; la aplicación específica puede ser efímera.

### 4. Synthetic Browser
Modo experimental `/synthetic-browser` donde el usuario define:

- `site`
- `year`
- `style`
- `features`

El modelo genera una reconstrucción o interpretación sintética de una interfaz web. No debe presentarse como una copia histórica verificable ni como contenido real recuperado de Internet.

### 5. Counterfactual simulations
Interfaces y simuladores que representan escenarios hipotéticos explícitamente etiquetados como sintéticos.

## Estrategia de ejecución

En equipos modestos como un Mac Apple Silicon con poca RAM, el runtime, la UI, SQLite y las apps pueden correr localmente mientras la inferencia pesada se delega a Cerebras. La arquitectura mantiene abierta una ruta local mediante modelos pequeños, pero no depende de ejecutar el modelo grande en el dispositivo.

## Reutilización y costo

No todo debe regenerarse desde cero:

```text
Prompt → AppSpec → búsqueda de coincidencias
                     ├─ reutilizar app existente
                     ├─ aplicar diff incremental
                     └─ generar desde cero
```

Se priorizarán:

- cache semántico;
- biblioteca de apps exitosas;
- generación incremental por diffs;
- reutilización de componentes aprobados;
- versionado;
- medición de tokens y costo.

## Seguridad

La frontera sigue siendo la misma: **el modelo propone software; el runtime decide qué puede ejecutarse**.

La primera capa seguirá siendo HTML/CSS/JavaScript autocontenido dentro de un iframe aislado. Python u otros runtimes solo podrán añadirse más adelante mediante contenedores/VM efímeros con límites estrictos.

## Nombre único

Todas estas líneas se desarrollan dentro de:

**Generative App Runtime**

Repositorio canónico: `juanjimenez-cmd/generative-app-runtime`.
