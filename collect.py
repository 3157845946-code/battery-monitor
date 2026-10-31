#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, re, sys, time, csv, urllib.request, urllib.parse, datetime

TARGET = "http://www.wap.cnyiot.com/nat/pay.aspx?mid=18501681136"
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

def fetch_power():
    urls = [
        "https://api.allorigins.win/raw?url=" + urllib.parse.quote(TARGET, safe=''),
        "https://corsproxy.io/?url=" + urllib.parse.quote(TARGET, safe=''),
        TARGET,
    ]
    for url in urls:
        for attempt in range(2):
            try:
                req = urllib.request.Request(url, headers={
                    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148 MicroMessenger/8.0.32",
                })
                with urllib.request.urlopen(req, timeout=25) as r:
                    html = r.read().decode("utf-8", errors="ignore")
                m = re.search(r"剩余电量:</span>\s*<label[^>]*>([0-9.]+)", html)
                if m:
                    print(f"成功: {url[:60]}")
                    return float(m.group(1))
            except Exception as e:
                print(f"失败: {e}")
            time.sleep(3)
    return None

def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    power = fetch_power()
    if power is None:
        print("全部失败，跳过")
        sys.exit(0)
    now = datetime.datetime.now()
    fpath = os.path.join(DATA_DIR, "readings.csv")
    rows = []
    if os.path.exists(fpath):
        with open(fpath, "r", encoding="utf-8") as f:
            rows = list(csv.reader(f))
    if not rows or rows[0] != ["ts_unix","ts_text","battery"]:
        rows = [["ts_unix","ts_text","battery"]]
    rows.append([str(int(time.time())), now.strftime("%Y-%m-%d %H:%M:%S"), str(power)])
    with open(fpath, "w", encoding="utf-8", newline="") as f:
        csv.writer(f).writerows(rows)
    print(f"记录: {now.strftime('%H:%M:%S')} = {power} kWh, 共{len(rows)-1}条")

if __name__ == "__main__":
    main()
