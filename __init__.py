import json
import os
import urllib.parse
import urllib.request


def _json(data):
    return json.dumps(data, ensure_ascii=False)


SEARCH_SOP_SCHEMA = {
    "name": "search_sop",
    "description": (
        "查詢健諮中心 SOP 知識庫。"
        "當使用者詢問 SOP、行政流程、交接、歸檔、心理健康假、"
        "活動辦理、公告發布、評鑑資料、表單路徑或中心內部流程時使用。"
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "使用者想查詢的 SOP 問題或關鍵字，例如：結案紀錄、心理健康假、心衛活動。"
            }
        },
        "required": ["query"]
    }
}


def handle_search_sop(params, **kwargs):
    del kwargs

    query = (params.get("query") or "").strip()
    if not query:
        return _json({
            "ok": False,
            "error": "missing query"
        })

    api_url = os.getenv("SOP_API_URL", "").strip()
    api_key = os.getenv("SOP_API_KEY", "").strip()

    if not api_url:
        return _json({
            "ok": False,
            "error": "SOP_API_URL is not configured"
        })

    if not api_key:
        return _json({
            "ok": False,
            "error": "SOP_API_KEY is not configured"
        })

    try:
        encoded_query = urllib.parse.quote(query)
        encoded_key = urllib.parse.quote(api_key)
        separator = "&" if "?" in api_url else "?"
        url = f"{api_url}{separator}key={encoded_key}&q={encoded_query}"

        with urllib.request.urlopen(url, timeout=20) as response:
            body = response.read().decode("utf-8")

        try:
            data = json.loads(body)
        except Exception:
            return _json({
                "ok": False,
                "error": "SOP API returned non-JSON response",
                "raw": body[:1000]
            })

        return _json({
            "ok": True,
            "query": query,
            "source": "google_apps_script_sop_api",
            "data": data
        })

    except Exception as e:
        return _json({
            "ok": False,
            "error": str(e)
        })


def register(ctx):
    ctx.register_tool(
        name="search_sop",
        toolset="sop",
        schema=SEARCH_SOP_SCHEMA,
        handler=handle_search_sop,
        description="Search SOP knowledge base from Google Apps Script API."
    )
