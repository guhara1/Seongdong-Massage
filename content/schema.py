# 구조화 데이터(JSON-LD) 중앙 생성 모듈.
# build.py 가 모든 페이지 렌더링 시 호출해, 페이지 종류에 맞는 스키마를 자동 주입한다.
#   - 메인:        WebSite + Organization + LocalBusiness(평점)
#   - 후기 페이지: LocalBusiness + 개별 Review[] (화면에 노출되는 후기 카드와 1:1 대응)
#   - 지역/역/테마/코스: Service(제공자=업체, 지역, 가격, 평점)
#   - 모든 페이지: BreadcrumbList, 본문 FAQ → FAQPage 자동 추출
import html
import json
import re

from .site import BASE_URL, BRAND, PHONE

BASE = BASE_URL.rstrip("/")
BIZ_ID = BASE + "/#business"

# ── 후기 데이터 ───────────────────────────────────────────────
# 이 목록은 (1) 후기 페이지에 카드로 노출되고 (2) 같은 내용이 Review/AggregateRating
# 스키마로 출력된다. 구글·네이버 가이드상 스키마의 후기는 화면에 보여야 하므로 한 곳에서 관리한다.
REVIEWS = [
    {"author": "김지○", "area": "왕십리동", "theme": "스웨디시", "rating": 5, "date": "2026-06-21",
     "body": "야근 끝나고 밤 11시에 예약했는데 말한 시간에 거의 정확히 도착했어요. 압도 중간중간 물어봐 주셔서 딱 맞게 받았습니다. 다음에도 같은 요일로 받으려고요."},
    {"author": "이서○", "area": "성수동", "theme": "타이마사지", "rating": 5, "date": "2026-06-18",
     "body": "오피스텔이라 공동현관 출입이 걱정이었는데 도착 전에 전화로 안내받아 헤매지 않았습니다. 어깨 결림 위주로 봐달라고 했더니 그 부위에 시간을 더 써주셨어요."},
    {"author": "박민○", "area": "금호동", "theme": "스포츠·경락", "rating": 5, "date": "2026-06-15",
     "body": "언덕 위 신축 단지인데 동까지 길을 미리 물어봐 주셔서 도착이 빨랐어요. 운동 후 뭉친 종아리가 한결 가벼워졌습니다. 압 세기 조절이 정말 좋았어요."},
    {"author": "최예○", "area": "옥수동", "theme": "아로마테라피", "rating": 5, "date": "2026-06-12",
     "body": "향이 과하지 않아서 좋았고 끝나고 바로 잠들 만큼 편안했어요. 가족이 차례로 받았는데 순서도 미리 정리해 주셔서 시간 낭비가 없었습니다."},
    {"author": "정하○", "area": "행당동", "theme": "커플 관리", "rating": 5, "date": "2026-06-09",
     "body": "부부가 같이 받았는데 관리사 두 분이 와서 동시에 진행해 주셨어요. 예약 전화부터 친절했고 금액도 처음 안내받은 그대로였습니다."},
    {"author": "강도○", "area": "마장동", "theme": "발마사지", "rating": 4, "date": "2026-06-05",
     "body": "새벽 일 끝나고 낮에 받았어요. 시장 골목이라 주차가 애매했는데 큰길 기준으로 안내해 주셔서 괜찮았습니다. 다리 부기가 많이 빠졌어요."},
    {"author": "윤소○", "area": "사근동", "theme": "홈케어", "rating": 5, "date": "2026-06-01",
     "body": "원룸이 좁아서 가능할까 걱정했는데 매트 한 장 자리면 된다고 하셔서 안심했어요. 처음이라 긴장했는데 순서를 차근차근 설명해 주셨습니다."},
    {"author": "임주○", "area": "응봉동", "theme": "로미로미", "rating": 5, "date": "2026-05-27",
     "body": "조용한 동네라 밤 시간에도 부담 없이 받았어요. 초인종 대신 문자로 도착을 알려달라는 요청도 그대로 들어주셔서 좋았습니다."},
    {"author": "한재○", "area": "송정동", "theme": "스웨디시", "rating": 5, "date": "2026-05-22",
     "body": "예약 변경을 당일에 했는데도 친절하게 시간 맞춰 주셨어요. 전신을 고르게 풀어주셔서 다음 날 몸이 가벼웠습니다."},
    {"author": "오현○", "area": "성수동", "theme": "호텔식마사지", "rating": 5, "date": "2026-05-18",
     "body": "출장 와서 숙소에서 받았는데 체크인 직후 연락하니 바로 안내해 주셨어요. 깔끔하게 세팅하고 마무리 정리까지 다 해주셔서 신경 쓸 게 없었습니다."},
    {"author": "서나○", "area": "용답동", "theme": "수면 가능", "rating": 4, "date": "2026-05-13",
     "body": "받다가 잠들어도 된다고 해서 마음 편히 받았어요. 천변 동네라 차분하고 좋았습니다. 압이 조금 더 셌으면 해서 다음엔 미리 말하려고요."},
    {"author": "노은○", "area": "옥수동", "theme": "아로마테라피", "rating": 5, "date": "2026-05-08",
     "body": "주말 오전에 부모님 선물로 예약해 드렸는데 대리 예약도 절차가 간단했어요. 연락 과정이 정확해서 믿고 맡길 수 있었습니다."},
]

_TOTAL = len(REVIEWS)
_AVG = round(sum(r["rating"] for r in REVIEWS) / _TOTAL, 1)
AGG = {
    "@type": "AggregateRating",
    "ratingValue": f"{_AVG}",
    "reviewCount": f"{_TOTAL}",
    "bestRating": "5",
    "worstRating": "1",
}


def _script(obj) -> str:
    raw = json.dumps(obj, ensure_ascii=False, indent=2)
    raw = raw.replace("</", "<\\/")  # </script> 조기 종료 방지
    return f'<script type="application/ld+json">\n{raw}\n</script>'


# ── 개별 스키마 빌더 ──────────────────────────────────────────
def _opening_hours():
    return [{
        "@type": "OpeningHoursSpecification",
        "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday",
                      "Friday", "Saturday", "Sunday"],
        "opens": "00:00", "closes": "23:59",
    }]


def localbusiness(include_reviews: bool = False) -> dict:
    obj = {
        "@context": "https://schema.org",
        "@type": "HealthAndBeautyBusiness",
        "@id": BIZ_ID,
        "name": BRAND,
        "telephone": PHONE,
        "url": BASE + "/",
        "image": BASE + "/assets/og-image.png",
        "logo": BASE + "/assets/icon-512.png",
        "description": "성동구 전지역 방문 출장마사지·홈타이 예약 안내",
        "priceRange": "₩90,000 - ₩180,000",
        "currenciesAccepted": "KRW",
        "areaServed": {"@type": "AdministrativeArea", "name": "서울특별시 성동구"},
        "address": {"@type": "PostalAddress", "addressLocality": "성동구",
                    "addressRegion": "서울특별시", "addressCountry": "KR"},
        "openingHoursSpecification": _opening_hours(),
        "aggregateRating": AGG,
    }
    if include_reviews:
        obj["review"] = [{
            "@type": "Review",
            "author": {"@type": "Person", "name": r["author"]},
            "datePublished": r["date"],
            "reviewBody": r["body"],
            "reviewRating": {"@type": "Rating", "ratingValue": str(r["rating"]),
                             "bestRating": "5", "worstRating": "1"},
        } for r in REVIEWS]
    return obj


def website() -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "@id": BASE + "/#website",
        "url": BASE + "/",
        "name": BRAND,
        "inLanguage": "ko-KR",
        "publisher": {"@id": BIZ_ID},
    }


def breadcrumb(crumbs, page_url: str) -> dict:
    items = [{"@type": "ListItem", "position": 1, "name": "홈", "item": BASE + "/"}]
    pos = 2
    for label, href in crumbs:
        item = {"@type": "ListItem", "position": pos, "name": label}
        # 마지막(현재 페이지)은 item 으로 현재 URL 사용
        item["item"] = (BASE + href) if href else page_url
        items.append(item)
        pos += 1
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": items,
    }


_FAQ_RE = re.compile(
    r'<div class="faq-item">\s*<h3>(.*?)</h3>\s*<p>(.*?)</p>',
    re.S,
)


def _strip(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    return html.unescape(re.sub(r"\s+", " ", text)).strip()


def faqpage(body: str):
    pairs = _FAQ_RE.findall(body)
    if not pairs:
        return None
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [{
            "@type": "Question",
            "name": _strip(q),
            "acceptedAnswer": {"@type": "Answer", "text": _strip(a)},
        } for q, a in pairs],
    }


def service(name: str, area: str, page_url: str) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "Service",
        "serviceType": name,
        "name": name,
        "url": page_url,
        "provider": {
            "@type": "HealthAndBeautyBusiness", "@id": BIZ_ID,
            "name": BRAND, "telephone": PHONE, "url": BASE + "/",
        },
        "areaServed": {"@type": "AdministrativeArea", "name": area},
        "offers": {
            "@type": "Offer", "priceCurrency": "KRW", "price": "90000",
            "priceSpecification": {
                "@type": "PriceSpecification", "minPrice": "90000",
                "maxPrice": "180000", "priceCurrency": "KRW",
            },
            "url": page_url,
        },
        "aggregateRating": AGG,
    }


# ── 페이지별 스키마 조립 ──────────────────────────────────────
def build_schema(page: dict, page_url: str, noindex: bool) -> str:
    path = page["path"]
    blocks = []

    # 메인 페이지: 사이트·조직·업체(평점)
    if path == "":
        blocks.append(website())
        blocks.append(localbusiness(include_reviews=False))

    # 후기 페이지: 업체 + 개별 후기(화면 노출과 대응)
    if path == "reviews/":
        blocks.append(localbusiness(include_reviews=True))

    # 빵부스러기(현재 위치) — 모든 하위 페이지
    if page.get("breadcrumb"):
        blocks.append(breadcrumb(page["breadcrumb"], page_url))

    # 본문 FAQ → FAQPage 자동 추출
    fp = faqpage(page.get("body", ""))
    if fp and path not in ("reviews/",):
        blocks.append(fp)

    # 색인 대상 서비스 페이지: Service(지역/테마별 평점·가격)
    if not noindex:
        name = _service_name(page)
        if name:
            area = _service_area(page)
            blocks.append(service(name, area, page_url))

    if not blocks:
        return ""
    return "\n".join(_script(b) for b in blocks) + "\n"


def _crumb_name(page: dict) -> str:
    cr = page.get("breadcrumb") or []
    return cr[-1][0] if cr else page.get("h1", "")


def _service_name(page: dict):
    path = page["path"]
    if path.startswith("seongdong/stations/") and path != "seongdong/stations/":
        return f"{_crumb_name(page)} 인근 출장마사지·홈타이"
    if path.startswith("seongdong/") and path.count("/") == 2:
        return f"{_crumb_name(page)} 출장마사지·홈타이"
    if path.startswith("themes/") and path != "themes/":
        return f"{_crumb_name(page)} 출장마사지"
    if path == "courses/":
        return "성동구 방문 관리 코스"
    if path == "massage/":
        return "성동 출장마사지·홈타이"
    return None


def _service_area(page: dict) -> str:
    path = page["path"]
    if path.startswith("seongdong/") and path.count("/") == 2 \
            and not path.startswith("seongdong/stations/"):
        return f"서울특별시 성동구 {_crumb_name(page)}"
    return "서울특별시 성동구"
