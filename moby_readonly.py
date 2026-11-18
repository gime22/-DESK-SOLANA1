"""Read-only Moby account check. Never sends trades or logs wallet credentials."""
import json
import os
import urllib.request

URL = os.environ.get("MOBY_MCP_URL", "")
VERSION = "2025-03-26"

def call(method, params, ident, session=None):
    headers = {"Content-Type":"application/json","Accept":"application/json, text/event-stream","MCP-Protocol-Version":VERSION}
    if session:
        headers["Mcp-Session-Id"] = session
    body=json.dumps({"jsonrpc":"2.0","id":ident,"method":method,"params":params}).encode()
    with urllib.request.urlopen(urllib.request.Request(URL,body,headers,method="POST"),timeout=20) as res:
        session = res.headers.get("Mcp-Session-Id") or session
        raw=res.read(500000).decode()
        if "text/event-stream" in res.headers.get("Content-Type",""):
            for line in raw.splitlines():
                if line.startswith("data:"):
                    try:
                        obj=json.loads(line[5:].strip())
                        if obj.get("id")==ident:
                            return obj,session
                    except ValueError:
                        pass
            raise RuntimeError("Missing MCP response")
        return json.loads(raw),session

def main():
    if not URL.startswith("https://"):
        raise SystemExit("MOBY_MCP_URL GitHub Secret is missing")
    init,session=call("initialize",{"protocolVersion":VERSION,"capabilities":{},"clientInfo":{"name":"DESK-readonly","version":"0.2"}},1)
    if init.get("error"):
        raise RuntimeError("MCP initialize rejected")
    tools,session=call("tools/list",{},2,session)
    if tools.get("error"):
        raise RuntimeError("MCP tools/list rejected")
    names={t.get("name") for t in tools.get("result",{}).get("tools",[])}
    for i,name in enumerate(("get_my_guardrails","get_my_balances"),3):
        if name not in names:
            print(name+": unavailable; no trade")
            continue
        try:
            result,session=call("tools/call",{"name":name,"arguments":{}},i,session)
            if result.get("error") or result.get("result",{}).get("isError"):
                print(name+": server returned an error")
            else:
                # Do not print sensitive account information into public repository logs.
                print(name+": succeeded (response suppressed for privacy)")
        except Exception as exc:
            print(name+": failed ("+type(exc).__name__+")")
    print("Read-only check complete. No orders, swaps, signatures, or funds moved.")

if __name__=="__main__":
    main()
