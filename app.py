from __future__ import annotations

import argparse
import json
import re
import subprocess
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE_DIR = Path(__file__).resolve().parent
OLLAMA_URL = "http://127.0.0.1:11434"
MODEL_NAME_RE = re.compile(r"^[A-Za-z0-9._:/-]{1,120}$")


class OllamaRequestError(RuntimeError):
    """Raised when local Ollama API call fails."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


def ollama_chat_payload(messages: list[dict]) -> str:
    prompt_parts = []
    for message in messages:
        role = str(message.get("role", "user")).strip() or "user"
        text = str(message.get("content", "")).strip()
        if not text:
            continue
        prompt_parts.append(f"{role}: {text}")
    return "\n".join(prompt_parts)


def ollama_request(endpoint: str, payload: dict | None = None, method: str = "POST") -> dict:
    if payload is None and method == "POST":
        payload = {}
    req = Request(
        f"{OLLAMA_URL}{endpoint}",
        method=method,
        headers={"Content-Type": "application/json"},
    )
    if payload is not None:
        req.data = json.dumps(payload).encode("utf-8")

    try:
        with urlopen(req, timeout=120) as response:
            body = response.read().decode("utf-8")
    except HTTPError as exc:
        raise OllamaRequestError(f"Ollama API returned {exc.code}: {exc.reason}", status_code=exc.code) from exc
    except URLError as exc:
        raise OllamaRequestError("Cannot reach Ollama at 127.0.0.1:11434") from exc

    if not body:
        raise OllamaRequestError("Empty response from Ollama")

    # Ollama chat responses can be newline-delimited JSON when streaming,
        # so keep the last parsed object.
    if endpoint == "/api/chat":
        for line in body.splitlines():
            if line.strip():
                data = json.loads(line)
        return data if "data" in locals() else {}

    return json.loads(body)


def ollama_get_tags():
    try:
        data = ollama_request("/api/tags", method="GET")
    except OllamaRequestError as exc:
        # Some older/newer builds are strict about method shape. Fallback to a
        # POST with an empty payload.
        if exc.status_code == 405:
            data = ollama_request("/api/tags", {})
        else:
            raise

    if not data:
        return []
    return data.get("models", [])


def ollama_pull_model(model_name: str) -> dict:
    model_name = str(model_name).strip()
    if not MODEL_NAME_RE.fullmatch(model_name):
        raise OllamaRequestError("Invalid model name")

    try:
        result = subprocess.run(
            ["ollama", "pull", model_name],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as exc:
        raise OllamaRequestError("Failed to execute ollama pull") from exc

    output = "\n".join(part for part in (result.stdout.strip(), result.stderr.strip()) if part).strip()
    if result.returncode != 0:
        raise OllamaRequestError(output or f"ollama pull failed with exit code {result.returncode}")

    return {
        "model": model_name,
        "output": output or f"Installed {model_name}",
    }


class Handler(BaseHTTPRequestHandler):
    server_version = "OllamaChatHTTP/1.0"

    def _set_cors(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _send_json(self, code: int, body: dict):
        payload = json.dumps(body).encode("utf-8")
        self.send_response(code)
        self._set_cors()
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _send_file(self, content: bytes, content_type: str):
        self.send_response(200)
        self._set_cors()
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_OPTIONS(self):
        self.send_response(200)
        self._set_cors()
        self.end_headers()

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            content = (BASE_DIR / "index.html").read_text(encoding="utf-8")
            self._send_file(content.encode("utf-8"), "text/html; charset=utf-8")
            return

        if self.path == "/api/models":
            try:
                models = [{"name": model["name"]} for model in ollama_get_tags()]
                self._send_json(200, {"models": models})
            except OllamaRequestError as exc:
                self._send_json(503, {"error": str(exc)})
            return

        self.send_error(404, "Not Found")

    def do_POST(self):
        if self.path not in ("/api/chat", "/api/install"):
            self._send_json(404, {"error": "Not Found"})
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(content_length).decode("utf-8") if content_length else "{}"
        try:
            req = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            self._send_json(400, {"error": "Invalid JSON"})
            return

        if self.path == "/api/install":
            model = req.get("model")
            if not model:
                self._send_json(400, {"error": "Payload must include model"})
                return

            try:
                payload = ollama_pull_model(model)
                self._send_json(200, payload)
            except OllamaRequestError as exc:
                self._send_json(503, {"error": str(exc)})
            return

        model = req.get("model")
        messages = req.get("messages")
        if not model or not isinstance(messages, list):
            self._send_json(400, {"error": "Payload must include model and messages[]"})
            return

        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
        }

        try:
            try:
                data = ollama_request("/api/chat", payload)
                message = data.get("message") or {}
                content = message.get("content", "")
            except OllamaRequestError as exc:
                # Older/alternate Ollama builds may expose only the legacy generate API.
                if exc.status_code not in (404, 405):
                    raise
                data = ollama_request(
                    "/api/generate",
                    {
                        "model": model,
                        "prompt": ollama_chat_payload(messages),
                        "stream": False,
                    },
                )
                content = data.get("response", "")

            if not content:
                content = "(empty response)"
            self._send_json(200, {"content": content})
        except OllamaRequestError as exc:
            self._send_json(503, {"error": str(exc)})


def main() -> None:
    parser = argparse.ArgumentParser(description="Simple local web UI for Ollama chat")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=7860)
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"Serving http://{args.host}:{args.port}")
    print("Ollama backend: http://127.0.0.1:11434")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Shutting down")


if __name__ == "__main__":
    main()
