import asyncio
import json
import mimetypes
import threading
import types
from collections.abc import Callable
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from homeykit import api
from homeykit.domain.errors import SettingsValidationError

from tests.support.running_app import RunningApp, running_app

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SETTINGS_DIRECTORY = PROJECT_ROOT / "settings"
LOCALES_DIRECTORY = PROJECT_ROOT / "locales"
MANIFEST_PATH = PROJECT_ROOT / ".homeycompose" / "app.json"
API_PREFIX = "/__api"
HOMEY_STUB_PATH = "/homey.js"

HOMEY_STUB_TEMPLATE = """
(function () {
  const locales = __LOCALES__;
  const language = new URLSearchParams(location.search).get("lang") || "en";
  function lookup(key) {
    return key.split(".").reduce(function (node, part) {
      return node === undefined ? undefined : node[part];
    }, locales[language]);
  }
  function translate(key, tokens) {
    let text = lookup(key);
    if (text === undefined) return key;
    Object.keys(tokens || {}).forEach(function (name) {
      text = text.split("__" + name + "__").join(tokens[name]);
    });
    return text;
  }
  async function callApi(method, path, body, callback) {
    try {
      const response = await fetch("__PREFIX__" + path, {
        method: method,
        headers: { "Content-Type": "application/json" },
        body: method === "GET" ? undefined : JSON.stringify(body || {}),
      });
      const payload = await response.json();
      if (response.ok) callback(null, payload);
      else callback(new Error(payload.error));
    } catch (error) {
      callback(error);
    }
  }
  const homey = {
    __: translate,
    api: callApi,
    ready: function () { window.homeyReady = true; },
  };
  window.addEventListener("load", function () { window.onHomeyReady(homey); });
})();
"""


def build_homey_stub() -> bytes:
    locales = {
        language: json.loads((LOCALES_DIRECTORY / f"{language}.json").read_text())
        for language in ("en", "nl")
    }
    script = HOMEY_STUB_TEMPLATE.replace("__LOCALES__", json.dumps(locales))
    return script.replace("__PREFIX__", API_PREFIX).encode()


def load_route_table() -> dict[tuple[str, str], str]:
    manifest = json.loads(MANIFEST_PATH.read_text())
    return {
        (route["method"], route["path"]): name
        for name, route in manifest["api"].items()
    }


class Backend:
    def __init__(self, state_directory: Path) -> None:
        self._state_directory = state_directory
        self._ready = threading.Event()
        self._stop_event: asyncio.Event | None = None
        self._loop: asyncio.AbstractEventLoop | None = None
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._server: ThreadingHTTPServer | None = None
        self.app: RunningApp | None = None
        self.base_url = ""

    def start(self) -> None:
        self._thread.start()
        if not self._ready.wait(timeout=20):
            raise RuntimeError("The backend did not start")

    def stop(self) -> None:
        if self._loop is not None and self._stop_event is not None:
            self._loop.call_soon_threadsafe(self._stop_event.set)
        self._thread.join(timeout=20)

    def run_in_backend_loop(self, coroutine: Any) -> Any:
        assert self._loop is not None
        return asyncio.run_coroutine_threadsafe(coroutine, self._loop).result(
            timeout=30
        )

    def _run(self) -> None:
        asyncio.run(self._main())

    async def _main(self) -> None:
        self._loop = asyncio.get_running_loop()
        self._stop_event = asyncio.Event()
        async with running_app(self._state_directory) as app:
            self.app = app
            self._server = self._start_server(app)
            self._ready.set()
            await self._stop_event.wait()
            self._server.shutdown()
            self._server.server_close()

    def _start_server(self, app: RunningApp) -> ThreadingHTTPServer:
        handler = build_handler(app, self.run_in_backend_loop)
        server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        self.base_url = f"http://127.0.0.1:{server.server_address[1]}"
        threading.Thread(target=server.serve_forever, daemon=True).start()
        return server


def build_handler(
    app: RunningApp, run_in_backend_loop: Callable[[Any], Any]
) -> type[BaseHTTPRequestHandler]:
    routes = load_route_table()
    homey = types.SimpleNamespace(app=types.SimpleNamespace(services=app.container))
    homey_stub = build_homey_stub()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args: Any) -> None:
            return

        def do_GET(self) -> None:
            self._dispatch("GET")

        def do_PUT(self) -> None:
            self._dispatch("PUT")

        def _dispatch(self, method: str) -> None:
            path = urlsplit(self.path).path
            if path.startswith(API_PREFIX):
                self._call_api(method, path.removeprefix(API_PREFIX))
            elif path == HOMEY_STUB_PATH:
                self._send(200, homey_stub, "application/javascript")
            else:
                self._serve_static_file(path)

        def _call_api(self, method: str, path: str) -> None:
            name = routes.get((method, path))
            if name is None:
                self._send_json(404, {"error": "unknown_route"})
                return
            length = int(self.headers.get("Content-Length") or 0)
            body = json.loads(self.rfile.read(length) or b"{}")
            endpoint = getattr(api, name)
            try:
                result = run_in_backend_loop(
                    endpoint(homey=homey, query={}, params={}, body=body)
                )
            except SettingsValidationError as error:
                self._send_json(400, {"error": error.error_code})
            except Exception as error:
                self._send_json(500, {"error": str(error)})
            else:
                self._send_json(200, result)

        def _serve_static_file(self, path: str) -> None:
            relative = path.lstrip("/") or "index.html"
            file_path = (SETTINGS_DIRECTORY / relative).resolve()
            if not file_path.is_file() or SETTINGS_DIRECTORY not in file_path.parents:
                self._send(404, b"not found", "text/plain")
                return
            content_type = mimetypes.guess_type(file_path.name)[0] or "text/plain"
            self._send(200, file_path.read_bytes(), content_type)

        def _send_json(self, status: int, payload: Any) -> None:
            self._send(status, json.dumps(payload).encode(), "application/json")

        def _send(self, status: int, content: bytes, content_type: str) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)

    return Handler
