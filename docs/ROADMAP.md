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

- [ ] Streaming de generación y progreso visual.
- [ ] Router de modelos por tarea, contexto y costo.
- [ ] Reparación automática si el HTML falla validaciones.
- [ ] Plantillas de prompts y favoritos.
- [ ] Búsqueda y etiquetas en Mis Apps.
- [ ] Exportar/importar una app como paquete.
- [ ] Watchdog para cerrar iframes que consuman recursos en exceso.

## Fase 2 — Multiusuario privado

- [ ] Login y workspaces.
- [ ] Cuotas por usuario/proyecto.
- [ ] Registro de auditoría.
- [ ] PostgreSQL + object storage.
- [ ] Reverse proxy, HTTPS y despliegue privado.
- [ ] Compartir apps por enlace interno.

## Fase 3 — Data apps

- [ ] API segura para datasets subidos por el usuario.
- [ ] CSV/XLSX más robusto sin enviar archivos al LLM por defecto.
- [ ] Componentes de gráficos preaprobados.
- [ ] Exportación de resultados.

## Fase 4 — Sandbox de cómputo

- [ ] Contenedor/VM efímero para Python explícitamente aprobado.
- [ ] Sin red por defecto.
- [ ] CPU/RAM/PID/time limits.
- [ ] Filesystem temporal y allowlist de archivos.
- [ ] Destrucción del sandbox al terminar.

## Fase 5 — “Generative Desktop”

- [ ] Catálogo de capacidades en lugar de apps permanentes.
- [ ] Apps temporales que expiran automáticamente.
- [ ] Memoria de interfaces exitosas y reutilización para evitar costos.
- [ ] Apps compuestas por varios micro-servicios aislados.
