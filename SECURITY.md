# Security model

## Regla principal

**El modelo no ejecuta comandos en el host.** El MVP solo acepta como artefacto generado un documento HTML/CSS/JavaScript autocontenido y lo muestra en un iframe con `sandbox="allow-scripts"`.

## Controles actuales

1. La API key vive únicamente en el backend mediante variable de entorno.
2. No hay endpoint para ejecutar shell, Python, Node, AppleScript o PowerShell generado.
3. El HTML se limita por tamaño.
4. Se eliminan `iframe`, `object`, `embed`, `base`, `link` y metas `http-equiv` generadas.
5. Se inyecta Content Security Policy: sin red (`connect-src 'none'`), sin objetos, sin frames, sin formularios y sin navegación base.
6. El iframe **no** usa `allow-same-origin`, por lo que el documento tiene un origen opaco y no puede leer el DOM del runtime.
7. La respuesta HTML añade CSP, `nosniff`, `no-referrer` y una `Permissions-Policy` restrictiva.

## Riesgos residuales

- JavaScript generado puede consumir CPU/memoria y congelar la pestaña.
- Un modelo puede producir lógica incorrecta o cálculos erróneos.
- Los datos que el usuario pega en el prompt se envían al proveedor de inferencia. No incluyas secretos o documentos sensibles sin una política adecuada.
- La aplicación no tiene autenticación. Está diseñada para `127.0.0.1` o una red controlada, no para exposición pública.

## Antes de publicar en Internet

Agrega autenticación, CSRF/rate limiting, HTTPS, separación por usuario, cuotas, auditoría, secretos administrados, reverse proxy, backups y pruebas de seguridad. Considera ejecutar cada app en un origen separado y efímero.

## Futuro sandbox Python

Si se añade Python, debe ejecutarse en un contenedor/VM temporal sin privilegios, sin socket Docker, sin red por defecto, con filesystem efímero, límites de CPU/RAM/PIDs/tiempo y un protocolo explícito de entrada/salida. Nunca uses `exec()` o `subprocess` directamente sobre código del modelo en el host.
