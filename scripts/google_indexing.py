#!/usr/bin/env python3
"""구글 Indexing API URL 제출 스크립트.

구글은 IndexNow에 참여하지 않으므로 별도로 Indexing API를 사용한다.

주의사항:
  - 공식적으로 Indexing API는 구인(JobPosting)·라이브방송(BroadcastEvent)
    페이지용이다. 일반 페이지는 Search Console의 사이트맵 제출과
    "URL 검사 → 색인 생성 요청"이 정석이며, 이 스크립트는 보조 수단이다.
  - 기존 sitemap ping 엔드포인트(google.com/ping)는 2023년 폐기되어
    더 이상 동작하지 않는다. sitemap은 Search Console에 등록해 두면
    빌드 시 갱신되는 lastmod 를 구글이 주기적으로 확인한다.
  - 기본 할당량: 하루 200건.

사전 준비:
  1. Google Cloud 프로젝트에서 "Web Search Indexing API" 활성화
  2. 서비스 계정 생성 → JSON 키 다운로드
  3. Search Console 속성(seongdong-massage.netlify.app)에 서비스 계정
     이메일을 "소유자"로 추가
  4. pip install google-auth requests

사용법:
  GOOGLE_APPLICATION_CREDENTIALS=service-account.json \
      python3 scripts/google_indexing.py                 # sitemap 전체
  ... python3 scripts/google_indexing.py URL [URL ...]   # 특정 URL만
"""
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

try:
    import requests
    from google.auth.transport.requests import Request
    from google.oauth2 import service_account
except ImportError:
    sys.exit("필요 패키지가 없습니다: pip install google-auth requests")

SCOPES = ["https://www.googleapis.com/auth/indexing"]
ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"


def sitemap_urls():
    xml = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    return re.findall(r"<loc>(.*?)</loc>", xml)


def main():
    cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not cred_path or not os.path.exists(cred_path):
        sys.exit("GOOGLE_APPLICATION_CREDENTIALS 환경변수에 서비스 계정 JSON 경로를 지정하세요.")

    creds = service_account.Credentials.from_service_account_file(
        cred_path, scopes=SCOPES)
    creds.refresh(Request())
    headers = {"Authorization": f"Bearer {creds.token}",
               "Content-Type": "application/json"}

    urls = sys.argv[1:] or sitemap_urls()
    ok = fail = 0
    for url in urls:
        res = requests.post(ENDPOINT, headers=headers, timeout=30,
                            json={"url": url, "type": "URL_UPDATED"})
        if res.status_code == 200:
            ok += 1
        else:
            fail += 1
            print(f"  실패 {res.status_code}: {url} — {res.text[:120]}")
    print(f"Google Indexing API: 성공 {ok} / 실패 {fail}")


if __name__ == "__main__":
    main()
