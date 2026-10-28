# -*- coding: utf-8 -*-
"""
云端抓取脚本（GitHub Actions 运行）
- 每30分钟由 .github/workflows/collect.yml 触发
- 抓取剩余电量，追加到 data/readings.csv
- 重建 data.json 供 index.html 读取
"""
import os
import re
import csv
import json
import urllib.request
import datetime

TARGET_URL = "http://www.wap.cnyiot.com/nat/pay.aspx?mid=18501681136"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "data", "readings.csv")
JSON_PATH = os.path.join(BASE_DIR, "data.json")

BATTERY_RE = re.compile(
    r"剩余电量[^0-9\-]*?<label[^>]*>\s*([0-9]+(?:\.[0-9]+)?)\s*</label>",
    re.S,
)

def fetch_battery():
    req = urllib.request.Request(
        TARGET_URL,
        headers={"User-Agent": "Mozilla/5.0 BatteryMonitor/1.0"},
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        html = resp.read().decode("utf-8", errors="ignore")
    m = BATTERY_RE.search(html)
    if not m:
        raise RuntimeError("未匹配到剩余电量字段")
    return float(m.group(1))

def beijing_now():
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))

def append_csv(ts_unix, ts_text, battery):
    is_new = not os.path.exists(CSV_PATH)
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if is_new:
            w.writerow(["ts_unix", "ts_text", "battery"])
        w.writerow([ts_unix, ts_text, f"{battery:.2f}"])

def rebuild_json():
    rows = []
    if not os.path.exists(CSV_PATH):
        with open(JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False)
        return
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            try:
                rows.append({
                    "ts_unix": int(r["ts_unix"]),
                    "ts": r["ts_text"],
                    "battery": float(r["battery"]),
                })
            except Exception:
                continue
    rows.sort(key=lambda x: x["ts_unix"])
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False)

def main():
    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
    v = fetch_battery()
    now = beijing_now()
    ts_unix = int(now.timestamp())
    ts_text = now.strftime("%Y-%m-%d %H:%M:%S")
    append_csv(ts_unix, ts_text, v)
    rebuild_json()
    print(f"[{ts_text}] battery = {v:.2f} kWh, total rows = ", end="")
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        print(sum(1 for _ in f) - 1)

if __name__ == "__main__":
    main()
