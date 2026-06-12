#!/usr/bin/env python3
"""IndexNow 색인 통보 스크립트.

sitemap.xml의 URL(또는 인자로 받은 URL)을 IndexNow API로 제출한다.
api.indexnow.org 한 곳에 제출하면 참여 검색엔진(빙, 네이버, 얀덱스, Seznam)
전체에 공유된다. 구글은 IndexNow 미참여 — scripts/google_indexing.py 참고.

사용법:
  python3 scripts/ping_indexnow.py                 # sitemap.xml 전체 URL 제출
  python3 scripts/ping_indexnow.py URL [URL ...]   # 특정 URL만 제출
"""
import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from content.site import BASE_URL  # noqa: E402

HOST = BASE_URL.split("//", 1)[1].rstrip("/")
KEY = "9e702d8add22dac78825c23534de8d8f"
KEY_LOCATION = f"{BASE_URL.rstrip('/')}/{KEY}.txt"
ENDPOINT = "https://api.indexnow.org/indexnow"


def sitemap_urls():
    xml = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    return re.findall(r"<loc>(.*?)</loc>", xml)


def submit(urls):
    payload = json.dumps({
        "host": HOST,
        "key": KEY,
        "keyLocation": KEY_LOCATION,
        "urlList": urls,
    }).encode("utf-8")
    req = urllib.request.Request(
        ENDPOINT, data=payload,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as res:
        # 200 OK / 202 Accepted 모두 정상 접수
        print(f"IndexNow: HTTP {res.status} — {len(urls)}개 URL 제출 완료")


if __name__ == "__main__":
    urls = sys.argv[1:] or sitemap_urls()
    if not urls:
        sys.exit("제출할 URL이 없습니다. 먼저 python3 build.py 를 실행하세요.")
    submit(urls)
