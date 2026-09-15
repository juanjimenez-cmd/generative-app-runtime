from __future__ import annotations

import shutil
import uuid
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .cerebras import generate_app
from .config import BASE_DIR, CEREBRAS_API_KEY, GENERATED_DIR, MODEL_PRICING, SUPPORTED_MODELS
from .db import db, init_db, utcnow
from .examples import seed_examples
from .security import extract_html, response_security_headers

app = FastAPI(title="Generative App Runtime", version="0.1.0")
STATIC_DIR = BASE_DIR / "static"


class GenerateRequest(BaseModel):
    prompt: str = Field(min_length=5, max_length=20000)
    title: str | None = Field(default=None, max_length=120)
    model: str = "auto"
    app_id: str | None = None


class RenameRequest(BaseModel):
    title: str = Field(min_length=1, max_length=120)


def rowdict(row):
    return dict(row) if row else None


def version_summary(conn, version_id: str | None):
    if not version_id:
        return None
    row = conn.execute("SELECT * FROM versions WHERE id=?", (version_id,)).fetchone()
    if not row:
        return None
    data = rowdict(row)
    data.pop("html_path", None)
    return data


def app_payload(conn, row):
    data = rowdict(row)
    data["is_example"] = bool(data["is_example"])
    data["current_version"] = version_summary(conn, data["current_version_id"])
    return data


@app.on_event("startup")
def startup() -> None:
    init_db()
    seed_examples()


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/api/config")
def config():
    return {
        "api_key_configured": bool(CEREBRAS_API_KEY),
        "models": ["auto", *SUPPORTED_MODELS],
        "pricing": MODEL_PRICING,
        "sandbox": "iframe sandbox=allow-scripts + restrictive CSP",
    }


@app.get("/api/apps")
def list_apps():
    with db() as conn:
        rows = conn.execute("SELECT * FROM apps ORDER BY updated_at DESC").fetchall()
        return [app_payload(conn, row) for row in rows]


@app.get("/api/apps/{app_id}")
def get_app(app_id: str):
    with db() as conn:
        row = conn.execute("SELECT * FROM apps WHERE id=?", (app_id,)).fetchone()
        if not row:
            raise HTTPException(404, "App no encontrada")
        data = app_payload(conn, row)
        versions = conn.execute(
            "SELECT * FROM versions WHERE app_id=? ORDER BY version_number DESC", (app_id,)
        ).fetchall()
        data["versions"] = []
        for item in versions:
            v = rowdict(item)
            v.pop("html_path", None)
            data["versions"].append(v)
        return data


@app.post("/api/apps/generate")
async def create_or_regenerate(req: GenerateRequest):
    try:
        result = await generate_app(req.prompt, req.model)
        safe_html = extract_html(result.content)
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(400 if isinstance(exc, ValueError) else 502, str(exc)) from exc
    except Exception as exc:
        raise HTTPException(502, f"No se pudo generar la app: {exc}") from exc

    now = utcnow()
    with db() as conn:
        if req.app_id:
            existing = conn.execute("SELECT * FROM apps WHERE id=?", (req.app_id,)).fetchone()
            if not existing:
                raise HTTPException(404, "App base no encontrada")
            app_id = req.app_id
            next_version = conn.execute(
                "SELECT COALESCE(MAX(version_number),0)+1 AS n FROM versions WHERE app_id=?", (app_id,)
            ).fetchone()["n"]
            title = req.title or existing["title"]
        else:
            app_id = str(uuid.uuid4())
            next_version = 1
            title = (req.title or req.prompt.strip().splitlines()[0])[:120]

        version_id = str(uuid.uuid4())
        folder = GENERATED_DIR / app_id
        folder.mkdir(parents=True, exist_ok=True)
        html_path = folder / f"v{next_version}.html"
        html_path.write_text(safe_html, encoding="utf-8")

        if req.app_id:
            conn.execute(
                "UPDATE apps SET title=?,updated_at=?,current_version_id=? WHERE id=?",
                (title, now, version_id, app_id),
            )
        else:
            conn.execute(
                "INSERT INTO apps(id,title,created_at,updated_at,current_version_id,is_example) VALUES(?,?,?,?,?,0)",
                (app_id, title, now, now, version_id),
            )

        conn.execute(
            """INSERT INTO versions(id,app_id,version_number,prompt,model,input_tokens,output_tokens,estimated_cost_usd,html_path,created_at)
               VALUES(?,?,?,?,?,?,?,?,?,?)""",
            (
                version_id,
                app_id,
                next_version,
                req.prompt,
                result.model,
                result.input_tokens,
                result.output_tokens,
                result.estimated_cost_usd,
                str(html_path),
                now,
            ),
        )
        row = conn.execute("SELECT * FROM apps WHERE id=?", (app_id,)).fetchone()
        return app_payload(conn, row)


@app.patch("/api/apps/{app_id}")
def rename_app(app_id: str, req: RenameRequest):
    with db() as conn:
        if not conn.execute("SELECT 1 FROM apps WHERE id=?", (app_id,)).fetchone():
            raise HTTPException(404, "App no encontrada")
        conn.execute("UPDATE apps SET title=?,updated_at=? WHERE id=?", (req.title.strip(), utcnow(), app_id))
        row = conn.execute("SELECT * FROM apps WHERE id=?", (app_id,)).fetchone()
        return app_payload(conn, row)


@app.post("/api/apps/{app_id}/duplicate")
def duplicate_app(app_id: str):
    with db() as conn:
        source = conn.execute("SELECT * FROM apps WHERE id=?", (app_id,)).fetchone()
        if not source:
            raise HTTPException(404, "App no encontrada")
        current = conn.execute("SELECT * FROM versions WHERE id=?", (source["current_version_id"],)).fetchone()
        if not current:
            raise HTTPException(409, "La app no tiene una versión utilizable")

        new_app_id = str(uuid.uuid4())
        new_version_id = str(uuid.uuid4())
        now = utcnow()
        folder = GENERATED_DIR / new_app_id
        folder.mkdir(parents=True, exist_ok=True)
        target = folder / "v1.html"
        shutil.copy2(current["html_path"], target)
        conn.execute(
            "INSERT INTO apps(id,title,created_at,updated_at,current_version_id,is_example) VALUES(?,?,?,?,?,0)",
            (new_app_id, f"{source['title']} (copia)", now, now, new_version_id),
        )
        conn.execute(
            """INSERT INTO versions(id,app_id,version_number,prompt,model,input_tokens,output_tokens,estimated_cost_usd,html_path,created_at)
               VALUES(?,?,?,?,?,?,?,?,?,?)""",
            (
                new_version_id,
                new_app_id,
                1,
                f"Copia de {source['title']}",
                current["model"],
                0,
                0,
                0.0,
                str(target),
                now,
            ),
        )
        row = conn.execute("SELECT * FROM apps WHERE id=?", (new_app_id,)).fetchone()
        return app_payload(conn, row)


@app.delete("/api/apps/{app_id}", status_code=204)
def delete_app(app_id: str):
    with db() as conn:
        row = conn.execute("SELECT * FROM apps WHERE id=?", (app_id,)).fetchone()
        if not row:
            raise HTTPException(404, "App no encontrada")
        conn.execute("DELETE FROM apps WHERE id=?", (app_id,))
    folder = GENERATED_DIR / app_id
    if folder.exists():
        shutil.rmtree(folder, ignore_errors=True)
    return Response(status_code=204)


@app.get("/api/versions/{version_id}/html")
def version_html(version_id: str):
    with db() as conn:
        row = conn.execute("SELECT html_path FROM versions WHERE id=?", (version_id,)).fetchone()
    if not row:
        raise HTTPException(404, "Versión no encontrada")
    path = Path(row["html_path"])
    if not path.exists():
        raise HTTPException(404, "Archivo de versión no encontrado")
    return HTMLResponse(path.read_text(encoding="utf-8"), headers=response_security_headers())


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", response_class=HTMLResponse)
def index():
    return FileResponse(STATIC_DIR / "index.html")
