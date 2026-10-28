"""Gemini API の小さなクライアント(問題の下書きと、答えを見ない検算に使う)。

キーは環境変数 GEMINI_API_KEY、なければ gemini-pdf-digest スキルの api_key.txt から読む。
キーはリポジトリに入れない。
"""
import glob
import json
import os
import ssl
import time
import urllib.error
import urllib.request

MODELS = ["gemini-3.8-flash", "gemini-3.5-flash", "gemini-3-flash-preview", "gemini-flash-latest", "gemini-flash-lite-latest"]


def api_key():
    k = os.environ.get("GEMINI_API_KEY")
    if k:
        return k.strip()
    for p in glob.glob("/root/.claude/skills/**/gemini-pdf-digest/api_key.txt", recursive=True) + \
            glob.glob("/mnt/skills/**/gemini-pdf-digest/api_key.txt", recursive=True):
        t = open(p).read().strip()
        return t.split("=", 1)[1].strip() if t.startswith("GEMINI_API_KEY=") else t
    raise SystemExit("Gemini の API キーが見つからない(GEMINI_API_KEY か api_key.txt)")


def _ctx():
    ca = os.environ.get("SSL_CERT_FILE") or ("/root/.ccr/ca-bundle.crt" if os.path.exists("/root/.ccr/ca-bundle.crt") else None)
    return ssl.create_default_context(cafile=ca) if ca else ssl.create_default_context()


def generate_json(prompt, models=None, temperature=0.7, max_tokens=60000):
    """prompt を送り、JSON として解釈できる返答を返す。404/429/503 は次のモデルへ。"""
    body = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseMimeType": "application/json", "temperature": temperature, "maxOutputTokens": max_tokens},
    }).encode()
    last = None
    for m in models or MODELS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent"
        req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json", "x-goog-api-key": api_key()})
        for attempt in range(2):
            try:
                with urllib.request.urlopen(req, context=_ctx(), timeout=600) as r:
                    data = json.loads(r.read())
                text = "".join(p.get("text", "") for p in data["candidates"][0]["content"]["parts"] if not p.get("thought"))
                return json.loads(text), m
            except urllib.error.HTTPError as e:
                last = f"{m}: HTTP {e.code} {e.read()[:300]!r}"
                if e.code == 503 and attempt == 0:
                    time.sleep(20)  # 混雑はすぐ戻ることが多いので1回だけ待つ
                    continue
                if e.code in (404, 429, 503):
                    break
                if e.code >= 500 and attempt == 0:
                    time.sleep(5)
                    continue
                raise SystemExit(last)
            except (json.JSONDecodeError, KeyError) as e:
                last = f"{m}: 返答を JSON として読めない ({e})"
                break
    raise SystemExit(f"Gemini が使えない: {last}")
