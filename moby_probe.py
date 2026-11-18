"""Moby MCP connectivity probe, read-only by design.

Uses MCP Streamable HTTP JSON-RPC. Never calls trading/order tools.
Set MOBY_MCP_URL as a private environment secret; never commit it.
"""
import json
import os
import urllib.request
import urllib.error
import argparse

ALLOWED = {"tools/list", "initialize"}

def rpc(url, method, params, request_id=1):
    if method not in ALLOWED:
        raise ValueError("Only read-only MCP discovery calls are permitted")
    payload = json.dumps({"jsonrpc": "2.0", "id": request_id, "method": method, "params": params}).encode()
    req = urllib.request.Request(url, data=payload, headers={
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "MCP-Protocol-Version": "2025-03-26",
    }, method="POST")
    with urllib.request.urlopen(req, timeout=15) as res:
        raw = res.read(2_000_000).decode()
        if "text/event-stream" in res.headers.get("Content-Type", ""):
            for line in raw.splitlines():
                if line.startswith("data: "):
                    try:
                        obj = json.loads(line[6:])
                        if obj.get("id") == request_id:
                            return obj
                    except json.JSONDecodeError:
                        continue
            raise RuntimeError("No matching response in event stream")
        return json.loads(raw)

def main():
    p = argparse.ArgumentParser(description="Moby read-only connection check")
    p.add_argument("--check", action="store_true", required=True)
    args = p.parse_args()
    url = os.environ.get("MOBY_MCP_URL", "")
    if not url.startswith("https://"):
        raise SystemExit("Set private MOBY_MCP_URL (https://...) first")
    try:
        init = rpc(url, "initialize", {
            "protocolVersion": "2025-03-26",
            "capabilities": {},
            "clientInfo": {"name": "DESK-paper", "version": "0.1.0"}
        })
        if "error" in init:
            raise RuntimeError("Server rejected MCP initialization")
        # Some MCP servers require session IDs; probe stops safely if unsupported.
        tools = rpc(url, "tools/list", {}, 2)
        if "error" in tools:
            raise RuntimeError("Server rejected tool listing")
        names = [t.get("name") for t in tools.get("result", {}).get("tools", [])]
        print(json.dumps({"connected": True, "read_only": True, "available_tools": names}, indent=2))
    except (urllib.error.URLError, TimeoutError, RuntimeError, ValueError) as exc:
        print("Connection check failed:", type(exc).__name__, "- check MCP endpoint/session/auth; no trading attempted")
        raise SystemExit(1)

if __name__ == "__main__":
    main()
