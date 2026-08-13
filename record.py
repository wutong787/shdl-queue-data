#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""云端版：抓取 Queue-Times 上海迪士尼(park_id=30)实时排队，追加到 data/queue_times.jsonl。
供 GitHub Actions 等 CI 定时任务调用。逻辑与 scraper/fetch_queue_times.py 一致，输出改为 JSONL 行。
每行 = 某次快照里某个项目的排队记录，便于日后塞进 wait_model / detail_10min_overrides。
"""
import json
import os
import urllib.request
from datetime import datetime, timezone, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
MAP_PATH = os.path.join(HERE, "queue_times_map.json")
DATA_DIR = os.path.join(HERE, "data")
DATA_PATH = os.path.join(DATA_DIR, "queue_times.jsonl")
API_URL = "https://queue-times.com/parks/30/queue_times.json"
SHANGHAI = timezone(timedelta(hours=8))


def load_map():
    with open(MAP_PATH, encoding="utf-8") as f:
        return json.load(f)


def fetch():
    req = urllib.request.Request(API_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def is_park_open(now_local):
    # 上海迪士尼大致 08:00–22:30；非营业时段跳过，避免写一堆空快照
    h = now_local.hour + now_local.minute / 60.0
    return 7.5 <= h <= 22.5


def main():
    m = load_map()
    now_utc = datetime.now(timezone.utc)
    now_local = now_utc.astimezone(SHANGHAI)
    if not is_park_open(now_local):
        print(f"[{now_local}] park closed, skip")
        return
    data = fetch()
    rides_map = m["rides"]
    single = set(m.get("single_rider_ride_ids", []))
    ignore = set(m.get("ignore_ride_ids", []))
    os.makedirs(DATA_DIR, exist_ok=True)
    snap = now_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = []
    for land in data.get("lands", []):
        for ride in land.get("rides", []):
            rid = ride["id"]
            if rid in ignore or rid in single:
                continue
            if str(rid) not in rides_map:
                continue  # 只记录映射到 21 项目的
            open_flag = 1 if ride.get("is_open") else 0
            wait = ride.get("wait_time") if open_flag else None
            rec = {
                "snapshot_utc": snap,
                "project": rides_map[str(rid)]["project"],
                "ride_id": rid,
 "land": rides_map[str(rid)]["land"],
                "wait_time": wait,
                "is_open": open_flag,
                "last_updated_utc": ride.get("last_updated"),
            }
            lines.append(json.dumps(rec, ensure_ascii=False))
    with open(DATA_PATH, "a", encoding="utf-8") as f:
        for ln in lines:
            f.write(ln + "\n")
    print(f"[{now_local}] appended {len(lines)} rides -> {DATA_PATH}")


if __name__ == "__main__":
    main()
