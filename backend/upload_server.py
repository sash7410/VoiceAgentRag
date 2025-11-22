"""
Tiny HTTP server to support optional dynamic PDF upload for the dealer handbook.

This is intentionally separate from the LiveKit worker. Run it in a
dedicated process:

    source .venv/bin/activate
    python -m backend.upload_server

The React frontend's optional "Upload Handbook PDF" button POSTs a PDF file
to this server, which overwrites `backend/resources/dealer_handbook.pdf`
and resets the RAG cache so subsequent questions use the new content.
"""

from __future__ import annotations

from aiohttp import web

from backend.config import PROJECT_ROOT
from backend.rag.handbook_rag import reset_rag_cache


HANDOOK_PATH = PROJECT_ROOT / "backend" / "resources" / "dealer_handbook.pdf"


async def _handle_options(request: web.Request) -> web.Response:
    """
    Minimal CORS preflight handler so the Vite dev server can call us.
    """
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    }
    return web.Response(headers=headers)


async def upload_handbook(request: web.Request) -> web.Response:
    """
    Accept a multipart/form-data upload containing a single `pdf` field.
    """
    if request.method == "OPTIONS":
        return await _handle_options(request)

    headers = {"Access-Control-Allow-Origin": "*"}

    reader = await request.multipart()
    field = await reader.next()
    if field is None or field.name != "pdf":
        return web.json_response(
            {"error": "expected form-data field named 'pdf'"},
            status=400,
            headers=headers,
        )

    filename = field.filename or "dealer_handbook.pdf"
    data = await field.read()

    HANDOOK_PATH.parent.mkdir(parents=True, exist_ok=True)
    HANDOOK_PATH.write_bytes(data)

    # Clear the cached vector store so the new PDF is indexed on next use.
    reset_rag_cache()

    return web.json_response(
        {"status": "ok", "bytes_written": len(data), "filename": filename},
        headers=headers,
    )


def create_app() -> web.Application:
    app = web.Application()
    app.router.add_route("POST", "/upload-handbook", upload_handbook)
    app.router.add_route("OPTIONS", "/upload-handbook", upload_handbook)
    return app


def main() -> None:
    """
    Run a small HTTP server on port 8000 for handbook uploads.
    """
    web.run_app(create_app(), port=8000)


if __name__ == "__main__":
    main()


