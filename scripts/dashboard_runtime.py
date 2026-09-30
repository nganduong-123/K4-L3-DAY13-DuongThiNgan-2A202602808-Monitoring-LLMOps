"""Small dependency-free runtime dashboard backed by data/logs.jsonl."""
from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from statistics import mean

LOG_PATH = Path("data/logs.jsonl")


def percentile(values: list[float], p: int) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, round((p / 100) * len(ordered) + 0.5) - 1))
    return ordered[index]


def read_records() -> list[dict]:
    if not LOG_PATH.exists():
        return []
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=60)
    records: list[dict] = []
    for line in LOG_PATH.read_text(encoding="utf-8").splitlines():
        try:
            record = json.loads(line)
            timestamp = datetime.fromisoformat(str(record["ts"]).replace("Z", "+00:00"))
            if timestamp >= cutoff:
                records.append(record)
        except (json.JSONDecodeError, KeyError, TypeError, ValueError):
            continue
    return records


def render() -> str:
    records = read_records()
    requests = [item for item in records if item.get("event") == "request_received"]
    responses = [item for item in records if item.get("event") == "response_sent"]
    failures = [item for item in records if item.get("event") == "request_failed"]
    latencies = [float(item.get("latency_ms", 0)) for item in responses]
    ttfts = [float(item.get("ttft_ms", 0)) for item in responses]
    costs = [float(item.get("cost_usd", 0)) for item in responses]
    quality = [float(item.get("quality_score", 0)) for item in responses]
    tokens_in = sum(int(item.get("tokens_in", 0)) for item in responses)
    tokens_out = sum(int(item.get("tokens_out", 0)) for item in responses)
    tool_results = [item for item in records if item.get("tool_success") is not None]
    tool_success = (
        100 * sum(item.get("tool_success") is True for item in tool_results) / len(tool_results)
        if tool_results else 100.0
    )
    error_rate = 100 * len(failures) / len(requests) if requests else 0.0
    breakdown = Counter(str(item.get("error_type", "unknown")) for item in failures)
    error_text = ", ".join(f"{key}: {value}" for key, value in breakdown.items()) or "none"

    panels = [
        ("Latency percentiles and TTFT", f"P50 {percentile(latencies, 50):.0f} · P95 {percentile(latencies, 95):.0f} · P99 {percentile(latencies, 99):.0f}<br>TTFT P95 {percentile(ttfts, 95):.0f}", "ms", "P95 ≤ 3000 ms"),
        ("Request traffic", f"{len(requests)} requests<br>{len(requests) / 60:.2f} requests/min", "requests/minute", "rate ≥ 1 request/min"),
        ("Error rate and retrieval success", f"Error {error_rate:.1f}% · Retrieval {tool_success:.1f}%<br>Breakdown: {error_text}", "percent", "error ≤ 2%; retrieval ≥ 90%"),
        ("Cost over time", f"${sum(costs):.6f}<br>Average ${mean(costs):.6f}" if costs else "$0.000000<br>Average $0.000000", "USD", "total ≤ $2.50"),
        ("Input and output tokens", f"Input {tokens_in:,}<br>Output {tokens_out:,}", "tokens", "total ≤ 50,000"),
        ("Quality proxy", f"{mean(quality):.2f}" if quality else "0.00", "score 0–1", "mean ≥ 0.75"),
    ]
    cards = "".join(
        f'<section class="card"><h2>{title}</h2><div class="value">{value}</div><p>Unit: {unit}</p><div class="threshold">SLO/threshold: {threshold}</div></section>'
        for title, value, unit, threshold in panels
    )
    generated = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
    return f"""<!doctype html><html><head><meta charset="utf-8"><meta http-equiv="refresh" content="30">
<title>K4-L3B Day 13 Monitoring & LLMOps</title><style>
body{{font:15px system-ui;background:#07111f;color:#eaf2ff;margin:0;padding:28px}}header{{display:flex;justify-content:space-between;align-items:end;margin-bottom:22px}}h1{{margin:0;font-size:27px}}.meta{{color:#9cb0ca;text-align:right}}main{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}}.card{{min-height:180px;background:linear-gradient(145deg,#10233b,#0b192c);border:1px solid #254567;border-radius:15px;padding:20px;box-shadow:0 8px 24px #0004}}h2{{font-size:16px;color:#8fc7ff;margin:0 0 22px}}.value{{font-size:25px;font-weight:700;line-height:1.5}}p{{color:#9cb0ca}}.threshold{{border-top:1px solid #254567;padding-top:12px;color:#72e0a4}}footer{{margin-top:18px;color:#7890ad}}@media(max-width:900px){{main{{grid-template-columns:1fr 1fr}}}}
</style></head><body><header><div><h1>K4-L3B Day 13 — Monitoring & LLMOps</h1><div>Runtime dashboard · source: data/logs.jsonl</div></div><div class="meta">Time range: last 60 minutes<br>Auto refresh: 30 seconds<br>{generated}</div></header><main>{cards}</main><footer>{len(records)} log records in current window · student 2A202602808</footer></body></html>"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        payload = render().encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, *_: object) -> None:
        return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve the six-panel Day 13 dashboard")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8050)
    args = parser.parse_args()
    print(f"Dashboard: http://{args.host}:{args.port}")
    ThreadingHTTPServer((args.host, args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
