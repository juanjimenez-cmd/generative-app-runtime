# Contributing

Gracias por ayudar a mejorar Generative App Runtime.

## Flujo recomendado

1. Crea un fork o una rama desde `main`.
2. Mantén cada cambio enfocado en un Issue.
3. Ejecuta las pruebas con `pytest -q`.
4. No subas `.env`, claves API, bases SQLite ni HTML generado localmente.
5. Abre un Pull Request explicando qué cambia, cómo probarlo y riesgos de seguridad.

## Convención de ramas

- `feat/...` nuevas funciones.
- `fix/...` correcciones.
- `docs/...` documentación.
- `security/...` endurecimiento de seguridad.

## Seguridad

Nunca agregues ejecución directa de código generado en el host. Cualquier futura ejecución Python debe ir en un sandbox efímero con límites estrictos y sin red por defecto.

## Commits

Se recomienda Conventional Commits: `feat:`, `fix:`, `docs:`, `test:`, `chore:`.
