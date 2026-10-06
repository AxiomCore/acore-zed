#!/usr/bin/env python3
"""Check a reviewed real stdio server against the public offline examples.

This checks the native LSP, not Zed's UI or registry installation. It makes
temporary copies, changes only unsaved overlays, and never invokes the CLI.
"""
import argparse
import hashlib
import json
from pathlib import Path
import queue
import shutil
import subprocess
import tempfile
import threading
import time


def read_message(stream):
    headers = {}
    size = 0
    while True:
        line = stream.readline(8193)
        if not line:
            raise EOFError("Server closed its LSP output")
        size += len(line)
        if size > 8192:
            raise ValueError("Oversized LSP headers")
        if line == b"\r\n":
            break
        key, separator, value = line.decode("ascii").partition(":")
        if not separator or key.lower() in headers:
            raise ValueError("Invalid LSP header")
        headers[key.lower()] = value.strip()
    length = int(headers["content-length"])
    if not 0 <= length <= 16 * 1024 * 1024:
        raise ValueError("Oversized LSP body")
    body = bytearray()
    while len(body) < length:
        chunk = stream.read(length - len(body))
        if not chunk:
            raise EOFError("Truncated LSP body")
        body.extend(chunk)
    return json.loads(body)


class Client:
    def __init__(self, server, root):
        self.process = subprocess.Popen([str(server)], cwd=root, stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        self.messages = queue.Queue()
        self.notifications = []
        self.sequence = 0
        self.reader = threading.Thread(target=self.read, daemon=True)
        self.reader.start()

    def read(self):
        try:
            while True:
                self.messages.put(read_message(self.process.stdout))
        except Exception as error:
            self.messages.put(error)

    def send(self, method, params, request_id=None):
        message = {"jsonrpc": "2.0", "method": method, "params": params}
        if request_id is not None:
            message["id"] = request_id
        body = json.dumps(message, ensure_ascii=False).encode()
        self.process.stdin.write(f"Content-Length: {len(body)}\r\n\r\n".encode() + body)
        self.process.stdin.flush()

    def next(self, deadline):
        message = self.messages.get(timeout=max(0, deadline - time.monotonic()))
        if isinstance(message, Exception):
            raise message
        if "method" in message and "id" in message:
            result = [None for _ in message.get("params", {}).get("items", [])] if message["method"] == "workspace/configuration" else None
            body = json.dumps({"jsonrpc": "2.0", "id": message["id"], "result": result}).encode()
            self.process.stdin.write(f"Content-Length: {len(body)}\r\n\r\n".encode() + body)
            self.process.stdin.flush()
        elif "method" in message:
            self.notifications.append(message)
        return message

    def request(self, method, params):
        self.sequence += 1
        request_id = self.sequence
        self.send(method, params, request_id)
        deadline = time.monotonic() + 20
        while True:
            message = self.next(deadline)
            if message.get("id") == request_id and "method" not in message:
                if "error" in message:
                    raise RuntimeError(f"{method}: {message['error']}")
                return message.get("result")

    def diagnostics(self, uri, version):
        deadline = time.monotonic() + 20
        while True:
            for index, message in enumerate(self.notifications):
                params = message.get("params", {})
                if message["method"] == "textDocument/publishDiagnostics" and params.get("uri") == uri and params.get("version") == version:
                    return self.notifications.pop(index)["params"]["diagnostics"]
            self.next(deadline)

    def close(self):
        if self.process.poll() is None:
            try:
                self.request("shutdown", None)
                self.send("exit", None)
                self.process.wait(timeout=3)
            except Exception:
                self.process.terminate()
                try:
                    self.process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    self.process.kill()
                    self.process.wait(timeout=3)
        for stream in (self.process.stdin, self.process.stdout):
            stream.close()
        self.reader.join(timeout=1)


def position(source, needle, offset=0):
    prefix = source[:source.index(needle) + offset]
    return {"line": prefix.count("\n"), "character": len(prefix.rsplit("\n", 1)[-1].encode("utf-16-le")) // 2}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server", type=Path, required=True)
    parser.add_argument("--expected-sha256", required=True, help="Digest from the maintainer's trusted receipt")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    server = args.server.expanduser().resolve()
    digest = hashlib.sha256(server.read_bytes()).hexdigest()
    if digest != args.expected_sha256:
        parser.error("Server does not match the supplied trusted SHA-256; nothing executed")
    metadata = json.loads(subprocess.check_output([str(server), "--version-json"], timeout=5))
    assert metadata["protocolVersion"] == "axiom-editor/v1", metadata
    assert metadata["serverVersion"].startswith("acore/"), metadata
    assert metadata.get("editorFeatures", {}).get("virtualDocumentNavigationOptOut") is True, metadata
    cases = [
        ("config", "main.acore", "Settings", "flag: Boolean = false", 'flag: Boolean = "wrong"', "Settings"),
        ("backend", "models.acore", "Task", "title: String", "title: MissingType", "String"),
        ("frontend", "main.acore", "count", "state count: Int = 0", 'state count: Int = "wrong"', "increment"),
        ("database", "schema.acore", "title", "DatabaseEngine.postgres", "DatabaseEngine.notAnEngine", "postgres"),
    ]
    results = []
    with tempfile.TemporaryDirectory(prefix="acore-zed-smoke-") as temporary:
        for profile, entry, needle, valid, invalid, expected_completion in cases:
            root = Path(temporary) / profile
            shutil.copytree(Path(__file__).resolve().parents[1] / "examples" / profile, root)
            target = root / entry
            source = target.read_text()
            before = {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob("*") if p.is_file()}
            client = Client(server, root)
            try:
                capabilities = client.request("initialize", {
                    "rootUri": root.as_uri(), "capabilities": {"general": {"positionEncodings": ["utf-16"]}},
                    "initializationOptions": {"workspaceTrusted": False, "virtualDocumentNavigation": False,
                                              "frontend": {"entry": "main.acore", "targets": ["web"]},
                                              "database": {"entry": "schema.acore"}},
                })["capabilities"]
                assert capabilities.get("hoverProvider") and capabilities.get("completionProvider"), capabilities
                client.send("initialized", {})
                client.send("textDocument/didOpen", {"textDocument": {"uri": target.as_uri(), "languageId": "acore", "version": 1, "text": source}})
                assert not [d for d in client.diagnostics(target.as_uri(), 1) if d.get("severity") == 1], profile
                params = {"textDocument": {"uri": target.as_uri()}, "position": position(source, needle, 1)}
                assert client.request("textDocument/hover", params), profile + ": missing typed hover"
                completion_params = dict(params)
                if profile == "backend":
                    completion_params["position"] = position(source, "title: String", len("title: S"))
                elif profile == "frontend":
                    completion_params["position"] = position(source, "on_press: increment", len("on_press: i"))
                elif profile == "database":
                    completion_params["position"] = position(source, "DatabaseEngine.postgres", len("DatabaseEngine.p"))
                completion = client.request("textDocument/completion", completion_params)
                items = completion if isinstance(completion, list) else (completion or {}).get("items", [])
                assert expected_completion in {item["label"] for item in items}, (profile, [item["label"] for item in items])
                tokens = client.request("textDocument/semanticTokens/full", {"textDocument": {"uri": target.as_uri()}})
                assert tokens and tokens["data"], profile
                client.send("textDocument/didChange", {"textDocument": {"uri": target.as_uri(), "version": 2}, "contentChanges": [{"text": source.replace(valid, invalid)}]})
                assert any(d.get("severity") == 1 for d in client.diagnostics(target.as_uri(), 2)), profile + ": missing invalid overlay error"
                client.send("textDocument/didChange", {"textDocument": {"uri": target.as_uri(), "version": 3}, "contentChanges": [{"text": source}]})
                assert not [d for d in client.diagnostics(target.as_uri(), 3) if d.get("severity") == 1], profile + ": recovery failed"
                results.append({"profile": profile, "result": "pass", "checks": ["clean diagnostics", "typed hover", "completion", "semantic tokens", "unsaved invalidation", "recovery"]})
            finally:
                client.close()
            after = {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob("*") if p.is_file()}
            assert before == after, profile + ": passive check changed saved inputs"
    report = {"format": "acore-zed-smoke/v1", "serverSha256": digest, "metadata": metadata,
              "settings": {"workspaceTrusted": False, "virtualDocumentNavigation": False}, "profiles": results,
              "scope": "Real native stdio; no Zed UI, platform certification or registry install claim"}
    if args.output:
        args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
