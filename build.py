#!/usr/bin/env python3
"""간다GO — 성동 출장마사지 정적 사이트 빌드 스크립트.

content/ 패키지의 페이지 정의를 읽어 정적 HTML을 생성한다.

규칙(자동 적용):
  - 본문 텍스트 2,000자 미만 페이지는 robots noindex 처리
  - sitemap.xml 에는 index 허용 페이지만 포함
  - 지역+역+테마 조합 경로는 생성 자체가 불가능한 구조
"""
import html
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from content import PAGES
from content.schema import build_schema, REVIEWS, AGG
from content.site import (BASE_URL, BRAND, NAV, PHONE, PHONE_DISPLAY)

ROOT = os.path.dirname(os.path.abspath(__file__))
MIN_INDEX_CHARS = 2000


def text_length(body_html: str) -> int:
    """태그를 제거한 본문 글자수(공백 포함, 연속 공백은 1자).
    공통 요금 블록은 페이지 고유 본문이 아니므로 측정에서 제외한다."""
    text = re.sub(r'<section class="pricing">.*?</section>', " ", body_html, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return len(text)


def render_nav(current_path: str) -> str:
    items = []
    for label, href, children in NAV:
        active = " is-active" if href == "/" + current_path else ""
        if children:
            sub = "".join(
                f'<li><a href="{c_href}">{c_label}</a></li>'
                for c_label, c_href in children
            )
            items.append(
                f'<li class="nav-item has-sub{active}">'
                f'<a href="{href}">{label}</a>'
                f'<ul class="sub-menu">{sub}</ul></li>'
            )
        else:
            items.append(
                f'<li class="nav-item{active}"><a href="{href}">{label}</a></li>'
            )
    return "".join(items)


def render_breadcrumb(crumbs) -> str:
    if not crumbs:
        return ""
    parts = ['<nav class="breadcrumb" aria-label="현재 위치"><ol>']
    parts.append('<li><a href="/">홈</a></li>')
    for label, href in crumbs:
        if href:
            parts.append(f'<li><a href="{href}">{label}</a></li>')
        else:
            parts.append(f"<li><span>{label}</span></li>")
    parts.append("</ol></nav>")
    return "".join(parts)


def inject_toc(body: str):
    """본문 섹션(h2)에 id를 보장하고 좌측 목차 데이터를 만든다."""
    items = []
    counter = [0]

    def repl(m):
        attrs, title = m.group(1), m.group(2)
        idm = re.search(r'id="([^"]+)"', attrs)
        if idm:
            sid = idm.group(1)
            opening = f"<section{attrs}>"
        else:
            counter[0] += 1
            sid = f"sec-{counter[0]}"
            opening = f'<section id="{sid}"{attrs}>'
        label = re.sub(r"<[^>]+>", "", title).strip()
        items.append((sid, label))
        return f"{opening}<h2>{title}</h2>"

    body = re.sub(r"<section([^>]*)>\s*<h2>(.*?)</h2>", repl, body, flags=re.S)
    return body, items


def render_toc(items) -> str:
    if len(items) < 3:
        return ""
    links = "".join(
        f'<li><a href="#{sid}">{label}</a></li>' for sid, label in items
    )
    return (
        '<aside class="page-toc"><nav aria-label="페이지 목차">'
        '<p class="toc-title">목차</p>'
        f"<ul>{links}</ul></nav></aside>"
    )


def _link_list(links) -> str:
    return "".join(f'<li><a href="{href}">{label}</a></li>' for label, href in links)


def related_links(page: dict) -> str:
    """지역(동) 페이지 하단에 롱테일 주제 내부링크 모듈을 붙인다.
    동 이름을 앵커에 넣어 페이지마다 고유한 연관 링크가 되도록 한다."""
    path = page["path"]
    is_dong = (
        path.startswith("seongdong/")
        and path.count("/") == 2
        and not path.startswith("seongdong/stations/")
    )
    if not is_dong:
        return ""
    crumbs = page.get("breadcrumb") or []
    dong = crumbs[-1][0] if crumbs else "이 지역"
    links = [
        (f"{dong} 홈타이 예약 방법", "/reservation/"),
        (f"{dong} 심야·24시간 출장마사지", "/themes/24hours/"),
        (f"{dong} 스웨디시 마사지 안내", "/themes/swedish/"),
        (f"{dong} 인근 지하철역별 안내", "/seongdong/stations/"),
        (f"{dong}에서 받는 커플·가족 관리", "/themes/couple/"),
        ("성동구 전지역 지역별 안내", "/seongdong/"),
        ("처음 이용자 가이드", "/magazine/first-time-guide/"),
        ("코스·요금 한눈에 보기", "/courses/"),
    ]
    return (
        '<section class="related-links" aria-label="함께 보면 좋은 안내">'
        f"<h2>{dong} 방문 관리, 이런 주제도 함께 보세요</h2>"
        f'<ul class="related-grid">{_link_list(links)}</ul></section>'
    )


def topics_block() -> str:
    """메인 페이지 롱테일 주제 내부링크 모듈."""
    links = [
        ("성동구 심야 24시간 출장마사지", "/themes/24hours/"),
        ("받다가 잠드는 수면 가능 홈타이", "/themes/overnight/"),
        ("왕십리동 야간 방문 마사지", "/seongdong/wangsimni-dong/"),
        ("성수동 오피스텔·숙소 출장마사지", "/seongdong/seongsu-dong/"),
        ("옥수동 한강변 단지 방문 관리", "/seongdong/oksu-dong/"),
        ("부부·커플 동시 홈타이 예약", "/themes/couple/"),
        ("처음 받는 스웨디시 전신 관리", "/themes/swedish/"),
        ("샤워 없이 받는 홈타이(타이마사지)", "/themes/thai/"),
        ("운동 후 회복 스포츠·경락", "/themes/sports/"),
        ("기업·단체 출장 마사지 견적", "/courses/#group"),
        ("성동구 지역별 이용 후기", "/reviews/"),
        ("처음 이용 준비 가이드", "/magazine/first-time-guide/"),
    ]
    return (
        '<section id="topics" class="related-links" aria-label="주제별 안내">'
        "<h2>주제별로 빠르게 찾기</h2>"
        "<p>찾으시는 상황이 분명하다면 아래 롱테일 주제에서 바로 들어가 보세요. "
        "지역·시간대·관리 유형별로 자주 찾는 안내를 모았습니다.</p>"
        f'<ul class="related-grid">{_link_list(links)}</ul></section>'
    )


def _stars(n: int) -> str:
    return "★" * n + "☆" * (5 - n)


def review_cards() -> str:
    """후기 페이지에 노출되는 후기 카드 — schema.py 의 REVIEWS 와 동일 데이터."""
    cards = "".join(
        '<li class="review-card">'
        f'<div class="review-head"><span class="review-stars" aria-label="별점 {r["rating"]}점">{_stars(r["rating"])}</span>'
        f'<span class="review-meta">{r["area"]} · {r["theme"]} · '
        f'<time datetime="{r["date"]}">{r["date"].replace("-", ". ")}</time></span></div>'
        f'<p class="review-body">{r["body"]}</p>'
        f'<p class="review-author">— {r["author"]}님</p>'
        "</li>"
        for r in REVIEWS
    )
    return (
        '<section id="list">'
        f'<h2>등록된 이용 후기 <span class="rev-agg">평균 {AGG["ratingValue"]}점 · {AGG["reviewCount"]}건</span></h2>'
        "<p>실제 이용이 확인된 예약 건의 후기입니다. 이용 지역과 받은 테마, 별점을 함께 표기합니다.</p>"
        f'<ul class="review-list">{cards}</ul></section>'
    )


def inject_modules(page: dict, body: str) -> str:
    """빌드 시점에만 들어가는 구조화 UI 모듈(후기 카드·롱테일 링크).
    본문 글자수 감사에는 잡히지 않도록 page['body'] 가 아닌 렌더 단계에서 주입한다."""
    body = body.replace("<!--REVIEW_CARDS-->", review_cards())
    body = body.replace("<!--TOPICS-->", topics_block())
    body += related_links(page)
    return body


def render_page(page: dict) -> str:
    path = page["path"]
    title = page["title"]
    desc = page["desc"]
    h1 = page["h1"]
    body = page["body"]
    crumbs = page.get("breadcrumb") or []
    extra_head = page.get("extra_head", "")
    hero = page.get("hero", "")

    chars = text_length(body)
    noindex = page.get("noindex", False) or chars < MIN_INDEX_CHARS
    robots = (
        '<meta name="robots" content="noindex,follow">'
        if noindex
        else '<meta name="robots" content="index,follow">'
    )
    canonical = BASE_URL.rstrip("/") + "/" + path

    # 히어로가 있는 페이지(메인)는 H1을 히어로 안에서 출력한다.
    if hero:
        page_head = hero
    else:
        page_head = ""

    h1_html = "" if hero else f"<h1>{h1}</h1>"

    body, toc_items = inject_toc(body)
    body = inject_modules(page, body)
    toc_html = render_toc(toc_items)
    layout_cls = "page-layout has-toc" if toc_html else "page-layout"

    schema_html = build_schema(page, canonical, noindex)

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
{robots}
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canonical}">
<meta property="og:site_name" content="{BRAND}">
<meta property="og:image" content="{BASE_URL.rstrip('/')}/assets/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{BASE_URL.rstrip('/')}/assets/og-image.png">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" type="image/svg+xml" href="/assets/favicon.svg">
<link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon-32.png">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<meta name="theme-color" content="#0a1120">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&family=Noto+Serif+KR:wght@600;700;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/style.css">
{schema_html}{extra_head}</head>
<body>
<header class="site-header">
  <div class="header-accent" aria-hidden="true"></div>
  <div class="header-top">
    <div class="header-inner">
      <a class="brand" href="/"><span class="brand-mark">G</span> <span class="brand-text">{BRAND}</span></a>
      <p class="header-tagline"><span class="tag-gem">◆</span> 성동구 전지역 방문 관리 <span class="tag-gem">◆</span> 24시간 상담</p>
      <a class="header-call" href="tel:{PHONE}"><span class="call-label">예약전화</span> {PHONE_DISPLAY}</a>
      <button class="nav-toggle" aria-label="메뉴 열기" aria-expanded="false"><span></span><span></span><span></span></button>
    </div>
  </div>
  <nav class="main-nav" aria-label="주 메뉴">
    <div class="nav-inner"><ul class="nav-list">{render_nav(path)}</ul></div>
  </nav>
</header>
{page_head}<main class="site-main">
  <div class="container {layout_cls}">
    {toc_html}
    <article class="page-content">
      {render_breadcrumb(crumbs)}
      {h1_html}
      {body}
    </article>
  </div>
</main>
<footer class="site-footer">
  <div class="container footer-grid">
    <div class="footer-col footer-about">
      <p class="footer-brand">{BRAND}</p>
      <p class="footer-desc">성동구 전지역 방문 출장마사지·홈타이 안내 사이트입니다. 모든 서비스는 안내된 관리 범위와 위생·안전 기준 안에서만 제공됩니다.</p>
      <address class="footer-contact">
        <span class="footer-contact-row"><span class="footer-label">예약전화</span> <a href="tel:{PHONE}">{PHONE_DISPLAY}</a></span>
        <span class="footer-contact-row"><span class="footer-label">상담시간</span> 연중무휴 24시간</span>
        <span class="footer-contact-row"><span class="footer-label">서비스 지역</span> 서울특별시 성동구 전지역</span>
      </address>
    </div>
    <nav class="footer-col" aria-label="서비스 안내">
      <p class="footer-title">서비스</p>
      <ul>
        <li><a href="/massage/">성동 출장마사지</a></li>
        <li><a href="/seongdong/">지역별 안내</a></li>
        <li><a href="/seongdong/stations/">지하철역별 안내</a></li>
        <li><a href="/themes/">테마별 안내</a></li>
        <li><a href="/courses/">코스안내</a></li>
      </ul>
    </nav>
    <nav class="footer-col" aria-label="이용 안내">
      <p class="footer-title">이용 안내</p>
      <ul>
        <li><a href="/reservation/">예약안내</a></li>
        <li><a href="/guide/">이용가이드</a></li>
        <li><a href="/reviews/">이용 후기</a></li>
        <li><a href="/support/">고객센터</a></li>
        <li><a href="/support/#faq">자주 묻는 질문</a></li>
      </ul>
    </nav>
    <nav class="footer-col" aria-label="정책 및 기준">
      <p class="footer-title">정책</p>
      <ul>
        <li><a href="/about/">운영자 소개</a></li>
        <li><a href="/support/privacy/">개인정보처리방침</a></li>
        <li><a href="/support/terms/">이용약관</a></li>
        <li><a href="/guide/#hygiene">위생·안전 기준</a></li>
        <li><a href="/guide/#prohibited">금지행위 안내</a></li>
        <li><a href="/support/#biz">제휴·기업 문의</a></li>
      </ul>
    </nav>
  </div>
  <div class="footer-bottom">
    <div class="container footer-bottom-inner">
      <p class="footer-copy">&copy; {BRAND}. All rights reserved.</p>
      <p class="footer-note">건전한 방문 관리 서비스를 운영하며, 불법적인 요청은 어떤 경우에도 응하지 않습니다.</p>
      <a class="footer-made" href="https://t.me/googleseolab" target="_blank" rel="noopener nofollow">웹사이트 제작문의 ↗</a>
    </div>
  </div>
</footer>
<a class="call-fab" href="tel:{PHONE}" aria-label="전화 예약 {PHONE_DISPLAY}">
  <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"/></svg>
  <span class="call-fab-label">예약 전화</span>
</a>
<script src="/assets/nav.js"></script>
</body>
</html>
"""


def _rfc822(dt) -> str:
    """RSS pubDate 형식 (RFC 822, KST)."""
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    return (f"{days[dt.weekday()]}, {dt.day:02d} {months[dt.month - 1]} "
            f"{dt.year} {dt.hour:02d}:{dt.minute:02d}:00 +0900")


def build() -> None:
    import datetime

    report = []
    sitemap_urls = []
    rss_items = []
    base = BASE_URL.rstrip("/")
    today = datetime.datetime.now()
    lastmod = today.strftime("%Y-%m-%d")

    for page in PAGES:
        path = page["path"]  # "" 또는 "seongdong/wangsimni-dong/" 형태
        out_dir = os.path.join(ROOT, path)
        os.makedirs(out_dir, exist_ok=True)
        html_out = render_page(page)
        with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(html_out)

        chars = text_length(page["body"])
        noindex = page.get("noindex", False) or chars < MIN_INDEX_CHARS
        if not noindex:
            loc = base + "/" + path
            sitemap_urls.append(loc)
            # RSS 아이템 — 아티클은 JSON-LD datePublished, 그 외는 빌드일 사용
            pub = today
            m = re.search(r'"datePublished"\s*:\s*"(\d{4})-(\d{2})-(\d{2})"',
                          page.get("extra_head", ""))
            if m:
                pub = datetime.datetime(int(m.group(1)), int(m.group(2)),
                                        int(m.group(3)), 9, 0)
            rss_items.append((pub, loc, page["title"], page["desc"]))
        report.append((path or "/", chars, "noindex" if noindex else "index"))

    # sitemap.xml — lastmod·changefreq·priority 포함
    # (검색엔진이 갱신 여부와 중요도를 빠르게 판단하도록 신호를 강화)
    def _sm_meta(u: str):
        rel = u[len(base):].strip("/")
        if rel == "":
            return "daily", "1.0"          # 메인
        depth = rel.count("/")
        if depth == 0 or rel in ("seongdong", "themes", "seongdong/stations", "magazine"):
            return "weekly", "0.9"          # 허브
        return "weekly", "0.7"              # 상세
    rows = []
    for u in sitemap_urls:
        cf, pr = _sm_meta(u)
        rows.append(
            f"  <url><loc>{html.escape(u)}</loc>"
            f"<lastmod>{lastmod}</lastmod>"
            f"<changefreq>{cf}</changefreq>"
            f"<priority>{pr}</priority></url>"
        )
    urls = "\n".join(rows)
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            f"{urls}\n</urlset>\n"
        )

    # rss.xml — 네이버 서치어드바이저 RSS 제출용 (RSS 2.0)
    rss_items.sort(key=lambda it: it[0], reverse=True)
    items_xml = "\n".join(
        "  <item>\n"
        f"    <title>{html.escape(t)}</title>\n"
        f"    <link>{html.escape(u)}</link>\n"
        f"    <guid isPermaLink=\"true\">{html.escape(u)}</guid>\n"
        f"    <description>{html.escape(d)}</description>\n"
        f"    <pubDate>{_rfc822(pub)}</pubDate>\n"
        "  </item>"
        for pub, u, t, d in rss_items
    )
    with open(os.path.join(ROOT, "rss.xml"), "w", encoding="utf-8") as f:
        f.write(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\n'
            "<channel>\n"
            f"  <title>{html.escape(BRAND)} — 성동 출장마사지·홈타이 안내</title>\n"
            f"  <link>{base}/</link>\n"
            "  <description>성동구 전지역 방문 관리(출장마사지·홈타이) 지역·역세권·테마 안내</description>\n"
            "  <language>ko</language>\n"
            f"  <lastBuildDate>{_rfc822(today)}</lastBuildDate>\n"
            f'  <atom:link href="{base}/rss.xml" rel="self" type="application/rss+xml" />\n'
            f"{items_xml}\n"
            "</channel>\n</rss>\n"
        )

    # robots.txt — 네이버(Yeti)·구글(Googlebot) 명시 허용 + 사이트맵 안내
    with open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(
            "# 네이버 검색로봇\n"
            "User-agent: Yeti\n"
            "Allow: /\n\n"
            "# 구글 검색로봇\n"
            "User-agent: Googlebot\n"
            "Allow: /\n\n"
            "User-agent: Googlebot-Image\n"
            "Allow: /\n\n"
            "# 그 외 모든 로봇\n"
            "User-agent: *\n"
            "Allow: /\n\n"
            f"Sitemap: {base}/sitemap.xml\n"
        )

    # .nojekyll (GitHub Pages)
    open(os.path.join(ROOT, ".nojekyll"), "w").close()

    width = max(len(p) for p, _, _ in report)
    print(f"{'PATH'.ljust(width)}  CHARS  ROBOTS")
    for p, c, r in sorted(report):
        flag = "" if (r == "noindex" or MIN_INDEX_CHARS <= c <= 2500) else "  ⚠"
        print(f"{p.ljust(width)}  {str(c).rjust(5)}  {r}{flag}")
    print(f"\n{len(report)} pages built, {len(sitemap_urls)} in sitemap.")


if __name__ == "__main__":
    build()
