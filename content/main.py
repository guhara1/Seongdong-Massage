# 메인 페이지 — 허브 역할. 모든 키워드를 밀어 넣지 않고 상세 페이지로 연결한다.
from .site import BASE_URL, BRAND, PHONE, PHONE_DISPLAY
from .pricing import PRICING

_JSONLD = f"""<meta name="naver-site-verification" content="aaa585a5584bb0979adb7c977c4d2d15a310523a" />
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "HealthAndBeautyBusiness",
  "name": "{BRAND}",
  "telephone": "{PHONE}",
  "url": "{BASE_URL}/",
  "image": "{BASE_URL}/assets/og-image.png",
  "description": "성동구 전지역 방문 출장마사지·홈타이 예약 안내",
  "areaServed": {{
    "@type": "AdministrativeArea",
    "name": "서울특별시 성동구"
  }},
  "openingHours": "Mo-Su 00:00-24:00",
  "priceRange": "₩90,000 - ₩180,000"
}}
</script>
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {{
      "@type": "Question",
      "name": "성동구 전지역 방문이 가능한가요?",
      "acceptedAnswer": {{
        "@type": "Answer",
        "text": "예약 시간, 정확한 위치, 배정 상황에 따라 가능 여부가 달라집니다. 지역별 안내 페이지에서 왕십리동, 성수동, 금호동, 옥수동, 행당동 등 열 개 대표 동 기준으로 확인할 수 있습니다."
      }}
    }},
    {{
      "@type": "Question",
      "name": "왕십리역이나 성수역 근처도 가능한가요?",
      "acceptedAnswer": {{
        "@type": "Answer",
        "text": "성동구 주요 역세권은 역 상세 페이지에서 주변 생활권과 함께 안내합니다. 정확한 가능 여부는 예약 시 위치를 기준으로 확인합니다."
      }}
    }},
    {{
      "@type": "Question",
      "name": "금호1가동이나 성수1가제1동 페이지는 왜 없나요?",
      "acceptedAnswer": {{
        "@type": "Answer",
        "text": "가 단위·숫자 행정동은 금호동, 성수동, 행당동, 왕십리동 대표 페이지에서 통합 안내하여 중복 페이지 위험을 줄입니다."
      }}
    }},
    {{
      "@type": "Question",
      "name": "당일 예약도 가능한가요?",
      "acceptedAnswer": {{
        "@type": "Answer",
        "text": "가능할 수 있지만 저녁 시간대와 주말은 문의가 많을 수 있어 사전 예약을 권장합니다."
      }}
    }},
    {{
      "@type": "Question",
      "name": "테마별 관리는 어디에서 확인하나요?",
      "acceptedAnswer": {{
        "@type": "Answer",
        "text": "스웨디시, 타이마사지, 홈케어 등 테마별 안내 페이지에서 특징과 추천 대상을 확인할 수 있습니다."
      }}
    }}
  ]
}}
</script>
"""

_HERO = f"""<section class="hero">
  <div class="hero-inner">
    <p class="hero-badge">Premium Visiting Spa · 성동구 전지역</p>
    <h1>성동 출장마사지·홈타이<br>예약 안내</h1>
    <p class="hero-lead">샵을 찾아다닐 필요 없이, 계신 곳으로 찾아가는 프리미엄 방문 관리.<br>자택·오피스텔·숙소 어디든 전화 한 통이면 예약이 끝납니다.</p>
    <div class="hero-actions">
      <a class="hero-btn primary" href="tel:{PHONE}">📞 {PHONE_DISPLAY}</a>
      <a class="hero-btn" href="/courses/">코스 안내 보기</a>
    </div>
    <ul class="hero-stats">
      <li><strong>10개</strong><span>대표 지역</span></li>
      <li><strong>14개</strong><span>역세권 안내</span></li>
      <li><strong>14개</strong><span>관리 테마</span></li>
      <li><strong>24시간</strong><span>예약 상담</span></li>
    </ul>
  </div>
</section>
"""

_BODY = f"""
<section id="service">
<h2>성동 출장마사지·홈타이 서비스 안내</h2>
<p>성동구에서 방문 마사지와 홈타이 예약을 찾는 분들을 위해 가능 지역, 예약 절차, 코스 선택 기준, 이용 전 확인사항을 한곳에 정리했습니다. 이 페이지는 성동구 전체 구조를 보여주는 허브이며, 상세한 내용은 지역별·지하철역별·테마별 안내에서 이어집니다. {BRAND}는 예약 확인부터 방문 관리까지 정해진 절차로 진행하고, 처음 이용하시는 분도 헤매지 않도록 단계마다 필요한 내용을 미리 안내해 드립니다.</p>
</section>

<section id="coverage">
<h2>성동구 전지역 방문 가능 안내</h2>
<p>성동구 지역 안내는 왕십리동, 마장동, 사근동, 행당동, 응봉동, 금호동, 옥수동, 성수동, 송정동, 용답동 열 개 대표 동 기준입니다. 왕십리도선동·왕십리제2동, 행당제1·2동, 금호1가~4가동, 성수1가·2가처럼 숫자나 가 단위로 나뉜 행정동은 별도 페이지 없이 대표 동 페이지에서 통합 안내합니다. 같은 생활권을 잘게 쪼개 비슷한 설명을 반복하기보다, 동 단위로 묶어 한 번에 정확히 설명하는 편이 이용자에게 낫기 때문입니다.</p>
</section>

<section id="areas">
<h2>지역별 안내</h2>
<p>각 동 페이지에서는 해당 생활권의 특징, 가까운 역세권, 방문 전 확인사항, 예약 가능 시간, 어울리는 테마를 동마다 고유한 내용으로 다룹니다. 거주하시거나 머무시는 동을 선택해 주세요.</p>
<ul class="card-grid">
<li><a href="/seongdong/wangsimni-dong/">왕십리동</a></li>
<li><a href="/seongdong/majang-dong/">마장동</a></li>
<li><a href="/seongdong/sageun-dong/">사근동</a></li>
<li><a href="/seongdong/haengdang-dong/">행당동</a></li>
<li><a href="/seongdong/eungbong-dong/">응봉동</a></li>
<li><a href="/seongdong/geumho-dong/">금호동</a></li>
<li><a href="/seongdong/oksu-dong/">옥수동</a></li>
<li><a href="/seongdong/seongsu-dong/">성수동</a></li>
<li><a href="/seongdong/songjeong-dong/">송정동</a></li>
<li><a href="/seongdong/yongdap-dong/">용답동</a></li>
</ul>
<p>성동구 전체 구조가 궁금하시면 <a href="/seongdong/">성동구 전체 안내</a>에서 한눈에 확인하실 수 있습니다.</p>
</section>

<section id="stations">
<h2>지하철역 인근 안내</h2>
<p>지하철역별 안내는 성동구를 지나는 2·3·5호선과 경의중앙선, 수인분당선 주요 역세권 기준입니다. 각 역 페이지에서는 인근 생활권과 대표 동, 방문 전 준비사항을 다루며, 출구별 페이지는 만들지 않습니다. 왕십리역과 옥수역 같은 환승역도 노선이 여러 개일 뿐 페이지는 하나로 운영합니다.</p>
<ul class="card-grid">
<li><a href="/seongdong/stations/sangwangsimni-station/">상왕십리역</a></li>
<li><a href="/seongdong/stations/wangsimni-station/">왕십리역</a></li>
<li><a href="/seongdong/stations/hanyang-univ-station/">한양대역</a></li>
<li><a href="/seongdong/stations/ttukseom-station/">뚝섬역</a></li>
<li><a href="/seongdong/stations/seongsu-station/">성수역</a></li>
<li><a href="/seongdong/stations/yongdap-station/">용답역</a></li>
<li><a href="/seongdong/stations/sindap-station/">신답역</a></li>
<li><a href="/seongdong/stations/geumho-station/">금호역</a></li>
<li><a href="/seongdong/stations/oksu-station/">옥수역</a></li>
<li><a href="/seongdong/stations/singeumho-station/">신금호역</a></li>
<li><a href="/seongdong/stations/haengdang-station/">행당역</a></li>
<li><a href="/seongdong/stations/majang-station/">마장역</a></li>
<li><a href="/seongdong/stations/eungbong-station/">응봉역</a></li>
<li><a href="/seongdong/stations/seoul-forest-station/">서울숲역</a></li>
</ul>
</section>

<section id="themes">
<h2>테마별 관리 안내</h2>
<p>테마별 안내에서는 관리 유형별 특징, 추천 대상, 예약 전 확인사항을 설명합니다. 테마는 각각 독립 페이지로 운영하며, 특정 역이나 동과 테마를 조합한 페이지는 만들지 않습니다. 원하시는 관리 유형을 먼저 고르신 뒤 예약 시 위치를 알려주시면 됩니다.</p>
<ul class="card-grid">
<li><a href="/themes/swedish/">스웨디시</a></li>
<li><a href="/themes/lomilomi/">로미로미</a></li>
<li><a href="/themes/thai/">타이마사지</a></li>
<li><a href="/themes/chinese/">중국마사지</a></li>
<li><a href="/themes/aroma/">아로마테라피</a></li>
<li><a href="/themes/homecare/">홈케어</a></li>
<li><a href="/themes/hotel-style/">호텔식마사지</a></li>
<li><a href="/themes/foot/">발마사지</a></li>
<li><a href="/themes/sports/">스포츠·경락</a></li>
<li><a href="/themes/skincare/">스킨케어</a></li>
<li><a href="/themes/waxing/">왁싱</a></li>
<li><a href="/themes/couple/">커플 관리</a></li>
<li><a href="/themes/24hours/">24시간</a></li>
<li><a href="/themes/overnight/">수면 가능</a></li>
</ul>
</section>

<section id="course">
<h2>코스 선택 안내</h2>
<p>코스는 이용 목적과 그날의 컨디션에 맞춰 고르시는 것이 좋습니다. 누적된 피로를 풀고 싶은 분, 향과 함께 편안한 휴식이 필요한 분, 운동 후 근육 이완이 필요한 분, 숙소로 방문을 원하시는 분, 둘이 함께 받고 싶은 분 등 상황별 선택 기준을 <a href="/courses/">코스안내</a>에서 자세히 다룹니다. 고민되시면 예약 전화에서 그날의 몸 상태를 말씀해 주세요. 함께 정해 드립니다.</p>
</section>

<section id="how">
<h2>예약 진행 방식</h2>
<p>예약은 다섯 단계로 진행됩니다. 희망 지역 또는 역 인근 위치를 확인하고, 희망 시간을 확인한 뒤, 코스와 인원을 정하고, 방문 가능 여부를 안내받은 다음 예약을 확정합니다. 저녁 시간대와 주말에는 문의가 몰릴 수 있어 한두 시간 이상 여유를 두고 연락 주시기를 권장합니다. 자세한 절차는 <a href="/reservation/">예약안내</a>에서 확인하실 수 있습니다.</p>
</section>

<section id="check">
<h2>이용 전 확인사항</h2>
<p>원활한 방문을 위해 정확한 주소, 공동현관 출입 방법, 주차 가능 여부, 조용한 공간 확보 여부를 미리 확인해 주시면 좋습니다. 성동구는 언덕 지형의 대단지부터 오피스텔, 지식산업센터 인근 숙소까지 건물 유형이 다양해, 건물 출입 안내를 함께 알려주시면 도착이 한층 빨라집니다. 준비사항 전체는 <a href="/guide/">이용가이드</a>에 정리되어 있습니다.</p>
</section>

<section id="safety">
<h2>위생 및 안전 안내</h2>
<p>건전하고 안전한 방문 관리를 위해 위생 기준, 예약 정보 확인, 개인정보 보호, 금지행위 안내를 명확히 제공합니다. 이용 전 서비스 범위와 유의사항을 확인해 주시고, 불법적이거나 무리한 요청은 어떤 경우에도 진행하지 않는다는 기준을 분명히 안내드립니다. 예약 정보는 관리 목적 외에는 사용하지 않습니다.</p>
</section>

<section id="faq">
<h2>자주 묻는 질문</h2>
<div class="faq-item">
<h3>성동구 전지역 방문이 가능한가요?</h3>
<p>예약 시간, 정확한 위치, 배정 상황에 따라 가능 여부가 달라집니다. 지역별 안내 페이지에서 왕십리동, 성수동, 금호동, 옥수동, 행당동 등 열 개 대표 동 기준으로 확인할 수 있습니다.</p>
</div>
<div class="faq-item">
<h3>왕십리역이나 성수역 근처도 가능한가요?</h3>
<p>성동구 주요 역세권은 역 상세 페이지에서 주변 생활권과 함께 안내합니다. 정확한 가능 여부는 예약 시 위치를 기준으로 확인합니다.</p>
</div>
<div class="faq-item">
<h3>금호1가동이나 성수1가제1동 페이지는 왜 없나요?</h3>
<p>가 단위·숫자 행정동은 금호동, 성수동, 행당동, 왕십리동 대표 페이지에서 통합 안내하여 중복 페이지 위험을 줄입니다.</p>
</div>
<div class="faq-item">
<h3>당일 예약도 가능한가요?</h3>
<p>가능할 수 있지만 저녁 시간대와 주말은 문의가 많을 수 있어 사전 예약을 권장합니다.</p>
</div>
<div class="faq-item">
<h3>테마별 관리는 어디에서 확인하나요?</h3>
<p>스웨디시, 타이마사지, 홈케어 등 테마별 안내 페이지에서 특징과 추천 대상을 확인할 수 있습니다.</p>
</div>
</section>

{PRICING}
<section id="contact" class="cta">
<h2>예약문의</h2>
<p>성동구 방문 관리 예약과 상담은 전화로 가장 빠르게 진행됩니다. 위치와 희망 시간을 알려주시면 가능 여부를 바로 확인해 드립니다.</p>
<a class="cta-phone" href="tel:{PHONE}">{PHONE_DISPLAY}</a>
</section>
"""

PAGE = {
    "path": "",
    "title": "성동 출장마사지·홈타이 | 성동구 전지역 방문 마사지 예약 안내",
    "desc": "성동 출장마사지·홈타이 안내 페이지입니다. 왕십리동, 성수동, 금호동, 옥수동, 행당동과 성동구 주요 지하철역 인근, 테마별 관리, 예약 전 확인사항을 확인해보세요.",
    "h1": "성동 출장마사지·홈타이 예약 안내",
    "body": _BODY,
    "extra_head": _JSONLD,
    "breadcrumb": [],
    "hero": _HERO,
}
