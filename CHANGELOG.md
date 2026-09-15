# Changelog

Todas las versiones relevantes de este proyecto se documentan aquí.

## [Unreleased]

### Planeado para v0.2
- Streaming de generación.
- Edición de apps por lenguaje natural.
- Router automático Qwen / GPT-OSS.

## [0.1.0] - 2026-09-15

### Added
- FastAPI + interfaz web local.
- Integración con Cerebras (`qwen-3.8-27b` y `gpt-oss-120b`).
- Generación de apps HTML/CSS/JavaScript autocontenidas.
- Sandbox con iframe + CSP restrictiva.
- SQLite y biblioteca local de apps/versiones.
- Cálculo de tokens y costo estimado.
- Apps de ejemplo locales.
- Docker, scripts macOS/Linux/Windows.
- Documentación de arquitectura, seguridad y roadmap.

### Security
- API keys solo en backend mediante `.env`.
- Sin ejecución de shell/Python/Node generado en el host.
