#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, os, re, sys, time, urllib.request, urllib.error, datetime, csv

URL = "http://www.wap.cnyiot.com/nat/pay.aspx?mid=18501681136"
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

def fetch_once():
    headers_list = [
        {
            "User-Agent": "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36 MicroMessenger/8.0.32",
            "Referer": "https://open.weixin.qq.com/",
            "X-Forwarded-For": "112.10.20.30",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9",
        },
        {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1 MicroMessenger/8.0.40",
            "Referer": "https://servicewechat.com/",
            "X-Forwarded-For": "223.104.50.60",
        },
    ]
    for h in headers_list:
        for attempt in range(2):
            try:
                req = urllib.request.Request(URL, headers=h)
                with urllib.request.urlopen(req, timeout=20) as r:
                    html = r.read().decode("utf-8", errors="ignore")
                m = re.search(r"剩余电量:</span>\s*<label[^>]*>([0-9.]+)", html)
                if m:
                    return float(m.group(1))
            except Exception as e:
                print(f"尝试失败: {e}")
            time.sleep(3)
    return None

def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    power = fetch_once()
    if power is None:
        print("抓取失败，跳过（不报错）")
        sys.exit(0)

    now = datetime.datetime.now()
    ts = int(time.time())
    ts_text = now.strftime("%Y-%m-%d %H:%M:%S")
    fpath = os.path.join(DATA_DIR, "readings.csv")

    rows = []
    if os.path.exists(fpath):
        with open(fpath, "r", encoding="utf-8") as f:
            rows = list(csv.reader(f))

    header = ["ts_unix", "ts_text", "battery"]
    if not rows:
        rows.append(header)
    rows.append([str(ts), ts_text, str(power)])

    with open(fpath, "w", encoding="utf-8", newline="") as f:
        csv.writer(f).writerows(rows)

    print(f"记录成功: {ts_text} = {power} kWh, 共 {len(rows)-1} 条")

if __name__ == "__main__":
    main()
