#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, os, re, sys, time, urllib.request, urllib.error, datetime

URL = "http://www.wap.cnyiot.com/nat/pay.aspx?mid=18501681136"
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.32(0x18002032) NetType/WIFI Language/zh_CN",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Referer": "https://open.weixin.qq.com/",
    "Connection": "keep-alive",
}

def fetch_power():
    last_err = None
    for attempt in range(3):
        try:
            req = urllib.request.Request(URL, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=20) as r:
                html = r.read().decode("utf-8", errors="ignore")
            m = re.search(r"剩余电量:</span>\s*<label[^>]*>([0-9.]+)", html)
            if m:
                return float(m.group(1))
            print(f"第{attempt+1}次: 页面返回但未匹配到电量")
        except urllib.error.HTTPError as e:
            last_err = e
            print(f"第{attempt+1}次: HTTP {e.code}")
        except Exception as e:
            last_err = e
            print(f"第{attempt+1}次: {e}")
        time.sleep(5)
    print(f"抓取失败: {last_err}")
    return None

def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    now = datetime.datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M")
    fpath = os.path.join(DATA_DIR, f"{date_str}.json")

    power = fetch_power()
    if power is None:
        print("本次跳过")
        sys.exit(0)

    records = []
    if os.path.exists(fpath):
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                records = json.load(f)
        except: records = []

    records = [r for r in records if r["t"] != time_str]
    records.append({"t": time_str, "v": power})
    records.sort(key=lambda x: x["t"])

    with open(fpath, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    index_path = os.path.join(DATA_DIR, "index.json")
    dates = []
    if os.path.exists(index_path):
        try:
            with open(index_path, "r", encoding="utf-8") as f:
                dates = json.load(f)
        except: dates = []
    if date_str not in dates:
        dates.append(date_str)
        dates.sort()
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(dates, f, ensure_ascii=False, indent=2)

    print(f"[{now}] 记录: {power} kWh, 今日共 {len(records)} 条")

if __name__ == "__main__":
    main()
