# Roadmap

## Fase 0 — MVP compartible (incluida)

- [x] FastAPI + UI local.
- [x] Cerebras Qwen 3.8 27B / GPT-OSS-120B.
- [x] Apps HTML autocontenidas.
- [x] iframe sandbox + CSP.
- [x] SQLite y biblioteca local.
- [x] Versiones, renombrar, duplicar y eliminar.
- [x] Tokens y costo estimado.
- [x] Docker y scripts Mac/Windows.

## Fase 1 — Calidad y control

- [x] Streaming de generación y progreso visual en `v0.2-dev`.
- [x] Router inicial de modelos por tarea, contexto y costo en `v0.2-dev`.
- [x] Edición por lenguaje natural con nuevas versiones en `v0.2-dev`.
- [ ] Reparación automática si el HTML falla validaciones.
- [ ] Plantillas de prompts y favoritos.
- [ ] Búsqueda y etiquetas en Mis Apps.
- [ ] Exportar/importar una app como paquete.
- [ ] Watchdog para cerrar iframes que consuman recursos en exceso.

## Fase 2 — AppSpec y generación estructurada

- [ ] Convertir lenguaje natural en un `AppSpec` JSON antes de escribir código.
- [ ] Validador/policy engine sobre permisos, red, persistencia y runtime.
- [ ] Separar intención, implementación y ejecución.
- [ ] Generación HTML/CSS/JS desde AppSpec.
- [ ] Explorar React/Web Components solo cuando el sandbox y el empaquetado lo justifiquen.
- [ ] Tests de contrato AppSpec → implementación.

## Fase 3 — Reutilización, cache y generación incremental

- [ ] Cache semántico de apps y AppSpecs.
- [ ] Detectar si una app ya existente resuelve la petición.
- [ ] Diffs incrementales en vez de regeneración completa.
- [ ] Biblioteca de componentes aprobados.
- [ ] Medición comparativa de latencia/costo: reutilizar vs editar vs generar.

## Fase 4 — Multiusuario privado

- [ ] Login y workspaces.
- [ ] Cuotas por usuario/proyecto.
- [ ] Registro de auditoría.
- [ ] PostgreSQL + object storage.
- [ ] Reverse proxy, HTTPS y despliegue privado.
- [ ] Compartir apps por enlace interno.

## Fase 5 — Data apps

- [ ] API segura para datasets subidos por el usuario.
- [ ] CSV/XLSX más robusto sin enviar archivos al LLM por defecto.
- [ ] Generative dashboards a partir de datasets/AppSpec.
- [ ] Componentes de gráficos preaprobados.
- [ ] Exportación de resultados.

## Fase 6 — Sandbox de cómputo

- [ ] Contenedor/VM efímero para Python explícitamente aprobado.
- [ ] Sin red por defecto.
- [ ] CPU/RAM/PID/time limits.
- [ ] Filesystem temporal y allowlist de archivos.
- [ ] Destrucción del sandbox al terminar.

## Fase 7 — Synthetic Browser

- [ ] Ruta/modo `/synthetic-browser`.
- [ ] Entradas `site`, `year`, `style`, `features`.
- [ ] Generar interfaces sintéticas claramente etiquetadas como reconstrucciones/hipótesis.
- [ ] Separar contenido sintético de navegación web real.
- [ ] Presets históricos/futuristas sin afirmar autenticidad factual.

## Fase 8 — Generative Desktop

- [ ] Catálogo de capacidades en lugar de apps permanentes.
- [ ] Apps temporales que expiran automáticamente.
- [ ] Memoria de interfaces exitosas y reutilización para evitar costos.
- [ ] Apps compuestas por varios micro-servicios aislados.
- [ ] Counterfactual simulations como otro tipo de AppSpec.

Consulta también [UNIFIED_VISION.md](UNIFIED_VISION.md).
