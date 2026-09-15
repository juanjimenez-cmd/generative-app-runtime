# Architecture

## Objetivo

Convertir una descripción natural en una micro-aplicación utilizable en segundos, manteniendo una frontera clara entre **generación de código** y **ejecución segura**.

## Componentes

### 1. Web desktop
Frontend sin framework para reducir dependencias. Gestiona creación, biblioteca, versiones y el iframe de previsualización.

### 2. FastAPI
Guarda metadatos, llama a Cerebras, extrae/valida HTML y sirve versiones con cabeceras restrictivas.

### 3. Cerebras adapter
Usa `POST /v1/chat/completions`. El proveedor nunca se llama desde el navegador, por lo que la API key no queda expuesta.

### 4. SQLite
Tablas `apps` y `versions`. Una app apunta a su versión actual; cada versión conserva prompt, modelo, tokens, costo y ruta del HTML.

### 5. Artifact store
`data/generated/<app_id>/vN.html`. En el MVP es almacenamiento local. Más adelante puede migrarse a object storage.

### 6. Browser sandbox
El documento se ejecuta con `sandbox="allow-scripts"`, sin `allow-same-origin`, y una CSP que bloquea red y embeds.

## Flujo de generación

```text
Prompt del usuario
   ↓
POST /api/apps/generate
   ↓
Prompt de sistema seguro
   ↓
Cerebras /chat/completions
   ↓
Texto del modelo
   ↓
extract_html()
   ├─ extrae fences
   ├─ normaliza documento
   ├─ retira tags de embed
   ├─ inyecta CSP
   └─ controla tamaño
   ↓
HTML versionado en disco + SQLite
   ↓
iframe sandbox
```

## Decisiones del MVP

- HTML único en vez de proyectos npm: maximiza velocidad y reduce superficie de ejecución.
- Sin ejecución server-side de código generado.
- Sin plugins externos en las apps generadas.
- `auto` selecciona Qwen 3.8 27B por ahora. El router inteligente es una fase posterior.
- El costo es estimado desde los tokens reportados y tarifas configurables.

## Límites intencionales

No cubre autenticación multiusuario, colaboración en tiempo real, almacenamiento cloud, sandbox Python ni publicación pública de apps. Esas funciones pertenecen a fases posteriores.
