# Generative App Runtime

Un **runtime local de micro-aplicaciones generadas por IA**. Describes una herramienta, Cerebras genera una app HTML/CSS/JavaScript autocontenida, el servidor la valida y la ejecuta dentro de un `iframe` aislado. Las apps útiles se guardan localmente con versiones, consumo de tokens y costo estimado.

> Estado: MVP experimental. Pensado para uso local y para compartir entre amigos/desarrolladores. No lo expongas directamente a Internet sin autenticación y endurecimiento adicional.

## Qué incluye

- Escritorio web para crear y abrir apps.
- Backend Python + FastAPI.
- Cerebras API con `qwen-3.8-27b` y `gpt-oss-120b`.
- Selector manual o modo `auto` (Qwen por defecto en este MVP).
- Apps generadas como un único archivo HTML, sin dependencias externas.
- Sandbox del navegador: `iframe sandbox="allow-scripts"` + CSP restrictiva.
- SQLite para catálogo, prompts, versiones, tokens y costos.
- Guardar, renombrar, duplicar y eliminar apps.
- Regenerar una app como nueva versión.
- Tres ejemplos locales: calculadora, caudales y visor CSV.
- Docker Compose opcional.
- Sin ejecución de Python, shell ni comandos generados por el modelo.

## Inicio rápido — macOS / Linux

1. Instala Python 3.11+.
2. Copia el archivo de entorno:

```bash
cp .env.example .env
```

3. Edita `.env` y coloca tu clave:

```env
CEREBRAS_API_KEY=tu_clave_aqui
```

4. Ejecuta:

```bash
chmod +x scripts/run.sh
./scripts/run.sh
```

5. Abre `http://127.0.0.1:8000`.

## Inicio rápido — Windows 10/11

En PowerShell:

```powershell
Copy-Item .env.example .env
# Edita .env y agrega CEREBRAS_API_KEY
.\scripts\run.ps1
```

Abre `http://127.0.0.1:8000`.

## Con Docker

```bash
cp .env.example .env
# agrega CEREBRAS_API_KEY en .env
docker compose up --build
```

Luego abre `http://localhost:8000`.

## Compartir con amigos

Comparte el ZIP o el repositorio **sin tu archivo `.env`**. Cada persona debe crear su propio `.env` y usar su propia API key de Cerebras. `.env` está ignorado por Git.

## Arquitectura resumida

```text
Navegador
  ├─ Escritorio / biblioteca
  └─ iframe sandbox (app generada)
           ▲
           │ HTML validado + CSP
FastAPI ───┼── SQLite (metadatos/versiones)
           ├── data/generated/*.html
           └── Cerebras Inference API
                 ├─ qwen-3.8-27b
                 └─ gpt-oss-120b
```

La app generada **no recibe** la API key. Solo el backend conoce `CEREBRAS_API_KEY`.

## Costos

El runtime registra `prompt_tokens` y `completion_tokens` reportados por Cerebras y calcula un costo estimado usando tarifas configurables en `.env.example`. Si Cerebras cambia precios, actualiza esas variables sin modificar el código.

## Seguridad importante

Este MVP reduce riesgo, no lo elimina. El HTML generado puede ejecutar JavaScript dentro del iframe y podría crear un bucle que congele esa pestaña. No ejecutamos código generado en Python/shell ni damos acceso directo al filesystem. Revisa [SECURITY.md](SECURITY.md) antes de ampliarlo.

## Pruebas

```bash
python -m pip install -r requirements-dev.txt
pytest -q
```

## Próximos pasos

Consulta [docs/ROADMAP.md](docs/ROADMAP.md). La siguiente etapa propuesta agrega autenticación, límites por usuario, router inteligente de modelos, previsualización con watchdog y un sandbox Docker separado para tareas Python explícitamente aprobadas.

## Licencia

MIT. Ver [LICENSE](LICENSE).
