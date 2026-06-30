# 간다GO — 성동 출장마사지·홈타이 안내 사이트

성동구 전지역 방문 관리(출장마사지·홈타이) 안내용 정적 사이트입니다.
예약전화: **0508-202-4719**

## 구조

- 정적 HTML 사이트 — 어느 호스팅(GitHub Pages, Netlify, 일반 웹서버)에서든 그대로 서빙 가능
- `build.py` + `content/` 패키지에서 페이지를 생성하는 빌드 방식
- 생성물(각 디렉터리의 `index.html`, `sitemap.xml`, `robots.txt`)도 저장소에 포함

```
build.py            # 빌드 스크립트 (레이아웃·글자수 검사·sitemap 생성)
content/
  site.py           # 상호·전화·BASE_URL·메뉴 구조
  main.py           # 메인 페이지 (+ LocalBusiness/FAQPage JSON-LD)
  areas.py          # 지역별: 성동구 허브 + 대표 동 10개
  stations.py       # 지하철역별: 허브 + 14개 역
  themes.py         # 테마별: 허브 + 14개 테마
  info.py           # 출장마사지 안내·코스·예약·가이드·후기·고객센터·약관
  magazine.py       # 매거진 허브 + 정보성 아티클
  about.py          # 운영자 소개 (E-E-A-T)
assets/             # CSS, 모바일 내비 JS, 파비콘·OG 이미지
```

## 빌드

```bash
python3 build.py
```

빌드 시 페이지별 본문 글자수 리포트가 출력됩니다.

## SEO 운영 원칙 (빌드에 강제됨)

- 본문 **2,000자 미만 페이지는 자동 `noindex`** 처리되고 sitemap에서 제외
- 지역은 대표 동 10개만 (왕십리동·마장동·사근동·행당동·응봉동·금호동·옥수동·성수동·송정동·용답동)
  — 숫자·가 단위 행정동 페이지 없음 (금호1가동, 성수1가제1동, 행당제1동 등은 대표 동으로 통합)
- 역은 역 1개당 페이지 1개 — 환승역(왕십리역·옥수역·성수역)도 URL 하나, 출구별 페이지 없음
- **지역+역+테마 조합 페이지 없음** (도어웨이 방지) — 테마는 독립 페이지로만 운영
- 상단/하위 메뉴와 푸터에 키워드·지역명·역명 대량 나열 없음
- 모든 페이지 본문은 페이지별 고유 작성 (지역명만 바꾼 복붙 없음)

## 색인(인덱싱) 운영

배포 도메인: **https://seongdong-massage.netlify.app** (`content/site.py`의 `BASE_URL`)

빌드 시 자동 생성되는 파일:

- `sitemap.xml` — 색인 페이지 56개, `lastmod` 포함 (noindex 약관 2종 제외)
- `rss.xml` — RSS 2.0, 네이버 서치어드바이저 RSS 제출용
- `robots.txt` — 네이버(Yeti)·구글(Googlebot) 명시 허용 + Sitemap 안내

### 최초 1회 등록

1. **구글 Search Console**: 속성 등록 → `sitemap.xml` 제출
2. **네이버 서치어드바이저**: 소유확인(메인페이지 메타태그 적용됨) →
   요청 > 사이트맵 제출(`sitemap.xml`) + RSS 제출(`rss.xml`)

### 빠른 색인 통보 자동화

- **IndexNow** (빙·네이버 등 참여 엔진 즉시 통보):
  키 파일 `9e702d8add22dac78825c23534de8d8f.txt`가 사이트 루트에 배포되며,
  `python3 scripts/ping_indexnow.py` 실행 시 sitemap 전체(또는 인자 URL)를 제출.
  `.github/workflows/indexnow.yml`이 main 푸시 시 자동 실행.
- **구글 Indexing API** (구글은 IndexNow 미참여):
  `scripts/google_indexing.py` — 서비스 계정 JSON 필요, 사용법은 스크립트 주석 참고.
  GitHub Actions 수동 실행: `.github/workflows/google-indexing.yml`
  (Secrets에 `GOOGLE_INDEXING_CREDENTIALS` 등록).
  공식적으로는 구인·라이브방송 페이지용 API이므로 일반 페이지는
  Search Console 사이트맵 + URL 검사 색인 요청이 정석.
- **sitemap ping**: 구글의 `google.com/ping` 엔드포인트는 2023년 폐기되어
  더 이상 동작하지 않음 — Search Console 등록으로 대체됨.

### 콘텐츠 수정 시

1. `content/` 수정 → `python3 build.py` → `python3 audit.py` 통과 확인
2. 커밋·푸시 (Cloudflare Pages 자동 배포)
3. IndexNow 워크플로가 자동 통보 (수동: `python3 scripts/ping_indexnow.py`)
