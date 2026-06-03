"""
🦅 Golden Eagle Bot — Ultimate Edition
Health-check web server. Reads the live status written by the bot at startup
and renders a futuristic, auto-refreshing status dashboard.
"""
import json
import os
from flask import Flask, jsonify

app = Flask(__name__)

STATUS_PATHS = ["bot_status.json", "/app/bot_status.json"]


def _load_status():
    for p in STATUS_PATHS:
        try:
            with open(p) as f:
                return json.load(f)
        except Exception:
            continue
    return None


@app.route("/health")
def health():
    """Machine-readable health endpoint for uptime monitors."""
    data = _load_status()
    if data and data.get("connected"):
        return jsonify(status="ok", **data), 200
    return jsonify(status="starting", data=data or {}), 503


@app.route("/")
def index():
    data = _load_status()

    if data is None:
        badge = "⏳"
        title = "Bot is waking up…"
        sub = "No status reported yet — refresh in a few seconds."
        color = "#f6c343"
        rows = ""
    elif data.get("connected"):
        badge = "✅"
        title = "LIVE &amp; Connected"
        sub = f"Open <b>@{data.get('username')}</b> in Telegram and send /start"
        color = "#22d36b"
        rows = f"""
            <div class="row"><span>🤖 Username</span><b>@{data.get('username')}</b></div>
            <div class="row"><span>🆔 Bot ID</span><b>{data.get('id')}</b></div>
            <div class="row"><span>📛 Name</span><b>{data.get('name')}</b></div>
            <div class="row"><span>🕒 Since</span><b>{data.get('time')}</b></div>
        """
    else:
        badge = "❌"
        title = "Not Connected"
        sub = "The bot failed to authenticate with Telegram."
        color = "#ff4d4f"
        rows = f"""
            <div class="row"><span>⚠️ Error</span><b>{data.get('error')}</b></div>
            <div class="row"><span>🕒 Time</span><b>{data.get('time')}</b></div>
        """

    return f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>🦅 Golden Eagle — Status</title>
<meta http-equiv="refresh" content="15">
<style>
  :root{{--accent:{color}}}
  *{{margin:0;padding:0;box-sizing:border-box;font-family:'Segoe UI',system-ui,sans-serif}}
  body{{min-height:100vh;display:grid;place-items:center;
    background:radial-gradient(circle at 20% 20%,#1a1f3a,#05060f 70%);color:#e8ecff;overflow:hidden}}
  .glow{{position:fixed;width:480px;height:480px;border-radius:50%;
    background:var(--accent);filter:blur(160px);opacity:.18;animation:float 8s ease-in-out infinite}}
  @keyframes float{{0%,100%{{transform:translate(-40px,-30px)}}50%{{transform:translate(40px,30px)}}}}
  .card{{position:relative;z-index:2;width:min(92vw,440px);padding:38px 34px;border-radius:24px;
    background:rgba(255,255,255,.04);backdrop-filter:blur(18px);
    border:1px solid rgba(255,255,255,.08);box-shadow:0 20px 60px rgba(0,0,0,.5);text-align:center}}
  .badge{{font-size:58px;animation:pulse 2s ease-in-out infinite}}
  @keyframes pulse{{0%,100%{{transform:scale(1)}}50%{{transform:scale(1.12)}}}}
  h1{{font-size:15px;letter-spacing:3px;text-transform:uppercase;color:#8b93c4;margin:14px 0 4px}}
  h2{{font-size:24px;color:var(--accent);margin-bottom:8px}}
  .sub{{font-size:14px;color:#aab2e0;line-height:1.6;margin-bottom:22px}}
  .row{{display:flex;justify-content:space-between;align-items:center;padding:11px 16px;margin:7px 0;
    background:rgba(255,255,255,.03);border-radius:12px;font-size:13.5px}}
  .row span{{color:#8b93c4}} .row b{{color:#fff;font-weight:600;text-align:right;max-width:60%;word-break:break-word}}
  .foot{{margin-top:24px;font-size:11px;color:#5a6196;letter-spacing:1px}}
  .live{{display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--accent);
    margin-right:6px;box-shadow:0 0 10px var(--accent);animation:pulse 1.4s infinite}}
</style></head><body>
  <div class="glow"></div>
  <div class="card">
    <div class="badge">{badge}</div>
    <h1>Golden Eagle Bot</h1>
    <h2>{title}</h2>
    <p class="sub">{sub}</p>
    {rows}
    <div class="foot"><span class="live"></span>AUTO-REFRESH 15s · ULTIMATE EDITION</div>
  </div>
</body></html>"""


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
