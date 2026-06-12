#!/usr/bin/env python3
"""배포 전 SEO 감사 스크립트.

검사 항목:
  1. 타이틀/디스크립션 중복 및 길이
  2. 색인 페이지 본문 글자수 범위(2,000~2,500자)
  3. 페이지 간 유사도(8-gram Jaccard) — 복붙 페이지 탐지
  4. 도어웨이 URL 패턴(지역+테마 조합, 숫자 행정동, 출구별 페이지)
  5. JSON-LD 파싱 오류
  6. "출장마사지" 키워드 본문 빈도(페이지당 5회 이하)

통과 기준: 중복 0 / 범위 밖 0 / 유사도 < 0.30 / 위반 0.
"""
import html
import json
import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from content import PAGES

FAIL = 0


def err(msg):
    global FAIL
    FAIL += 1
    print(f"  ✗ {msg}")


def body_text(body):
    t = re.sub(r'<section class="pricing">.*?</section>', " ", body, flags=re.S)
    t = re.sub(r"<[^>]+>", " ", t)
    t = html.unescape(t)
    return re.sub(r"\s+", " ", t).strip()


def ngrams(text, n=8):
    toks = text.split()
    return set(tuple(toks[i:i + n]) for i in range(max(0, len(toks) - n + 1)))


print("1) 타이틀/디스크립션 중복·길이")
titles, descs = {}, {}
for p in PAGES:
    titles.setdefault(p["title"], []).append(p["path"] or "/")
    descs.setdefault(p["desc"], []).append(p["path"] or "/")
    if not (10 <= len(p["desc"]) <= 160):
        err(f"desc 길이 {len(p['desc'])}자: {p['path'] or '/'}")
for t, paths in titles.items():
    if len(paths) > 1:
        err(f"타이틀 중복: {t} — {paths}")
for d, paths in descs.items():
    if len(paths) > 1:
        err(f"디스크립션 중복: {paths}")

print("2) 색인 페이지 글자수 범위")
for p in PAGES:
    n = len(body_text(p["body"]))
    if p.get("noindex"):
        continue
    if not (2000 <= n <= 2500):
        err(f"{n}자: {p['path'] or '/'}")

print("3) 페이지 간 유사도 (8-gram Jaccard)")
texts = [(p["path"] or "/", ngrams(body_text(p["body"]))) for p in PAGES if not p.get("noindex")]
worst = 0.0
for i in range(len(texts)):
    for j in range(i + 1, len(texts)):
        a, b = texts[i][1], texts[j][1]
        if not a or not b:
            continue
        jac = len(a & b) / len(a | b)
        worst = max(worst, jac)
        if jac >= 0.30:
            err(f"유사도 {jac:.2f}: {texts[i][0]} ↔ {texts[j][0]}")
print(f"  최대 유사도: {worst:.3f}")

print("4) 도어웨이 URL 패턴")
BAD = [
    r"station/[^/]+/",                      # 역 하위 경로(역+테마 조합)
    r"-dong/[^/]+/",                        # 동 하위 경로(동+테마 조합)
    r"\d+ga", r"ga-dong", r"-\d+-dong",     # 가/숫자 행정동
    r"exit", r"chulgu",                     # 출구별
]
for p in PAGES:
    for pat in BAD:
        if re.search(pat, p["path"]):
            err(f"도어웨이 패턴({pat}): {p['path']}")

print("5) JSON-LD 파싱")
for p in PAGES:
    eh = p.get("extra_head", "")
    for m in re.finditer(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', eh, re.S):
        try:
            json.loads(m.group(1))
        except json.JSONDecodeError as e:
            err(f"JSON-LD 오류({e}): {p['path'] or '/'}")

print("6) 키워드 빈도 (출장마사지 ≤ 5회/페이지)")
for p in PAGES:
    cnt = body_text(p["body"]).count("출장마사지")
    if cnt > 5:
        err(f"{cnt}회: {p['path'] or '/'}")

print()
if FAIL:
    print(f"FAILED — {FAIL}건 위반")
    sys.exit(1)
print(f"PASS — {len(PAGES)} pages, 위반 0건")
