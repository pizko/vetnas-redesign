#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from html import unescape
from pathlib import Path

BASE_URL = "https://vetnasvyaz.ru"
SITE_NAME = "Ветеринар на связи"
SITE_DESCRIPTION = (
    "Ветеринарная клиника в Раменском: прием, диагностика, вакцинация, "
    "хирургия и помощь питомцам в клинике Ветеринар на связи."
)
PHONE = "+7 (495) 144-48-03"
PHONE_E164 = "+74951444803"
ADDRESS_LOCALITY = "Раменское"
STREET_ADDRESS = "ул. Красноармейская, д. 13"
LATITUDE = 55.572556
LONGITUDE = 38.233634

ROOT = Path(__file__).resolve().parent.parent
SKIP_FILES = {
    "landing-template.html",
    "index-skolkovo.html",
    "index.html.1.html",
    "_article-template.html",
}
STATIC_REMAP = {
    "diagnostika.html": "uslugi-i-tseny.html",
    "vakcinaciya.html": "vakcinaciya-priem-chipirovanie.html",
    "vaktsinatsiya.html": "vakcinaciya-priem-chipirovanie.html",
    "onkologiya.html": "onkologiya-zhivotnykh-ramenskoe.html",
    "ornitologiya.html": "ornitolog-ptitsy-popugai-zapis.html",
    "narkoz-anesteziya.html": "infuzionnaya-terapiya-kapelnitsy-ves.html",
    "lechenie-glaz-koshek-ramenskoe": "lechenie-koshek.html",
    "lechenie-glaz-koshek-ramenskoe.html": "lechenie-koshek.html",
}


def strip_tags(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", value)).strip()


def canonical_path(page: Path) -> str:
    if page.name == "index.html":
        return "/"
    if page.parent.name == "news":
        return f"/news/{page.stem}"
    return f"/{page.stem}"


def canonical_url(page: Path) -> str:
    path = canonical_path(page)
    return BASE_URL if path == "/" else f"{BASE_URL}{path}"


def page_title(text: str) -> str:
    match = re.search(r"<title>(.*?)</title>", text, re.S | re.I)
    return strip_tags(unescape(match.group(1))) if match else SITE_NAME


def meta_description(text: str, fallback: str) -> str:
    match = re.search(r'<meta name="description" content="([^"]*)"', text, re.I)
    if not match:
        return fallback
    desc = strip_tags(unescape(match.group(1)))
    return desc or fallback


def h1_text(text: str, fallback: str) -> str:
    match = re.search(r"<h1[^>]*>(.*?)</h1>", text, re.S | re.I)
    return strip_tags(unescape(match.group(1))) if match else fallback


def first_image(text: str) -> str:
    for src in re.findall(r'<img[^>]+src="([^"]+)"', text, re.I):
        if src.startswith(("http://", "https://")):
            return src
        clean = src.split("?", 1)[0]
        if any(
            token in clean
            for token in ("favicon", "logo-1.gif", "vet1.png", "vet2.png", "vet3.png", "vet4.png", "vet5.png", "vet6.png")
        ):
            continue
        if clean.startswith("../"):
            clean = clean[3:]
        return f"{BASE_URL}/{clean.lstrip('/')}"
    return f"{BASE_URL}/54889242_2.jpg"


def page_kind(page: Path, text: str) -> str:
    if page.name == "index.html":
        return "home"
    if page.name == "contacts.html":
        return "contacts"
    if page.name in {"novosti.html", "1.html", "2.html", "3.html"} or "g-article-list" in text:
        return "listing"
    if page.name in {"o-kompanii.html"}:
        return "about"
    if page.name in {"vakansii.html"}:
        return "jobs"
    if page.name in {"uslugi-i-tseny.html", "diagnostika.html"}:
        return "catalog"
    if page.parent.name == "news" or 'class="g-page-article__text"' in text:
        return "article"
    return "service"


def breadcrumb_items(page: Path, kind: str, label: str) -> list[tuple[str | None, str]]:
    if page.name == "index.html":
        return []
    if kind == "article":
        return [
            (f"{BASE_URL}/", "Главная"),
            (f"{BASE_URL}/novosti", "Новости"),
            (None, label),
        ]
    if kind == "listing":
        if page.name == "novosti.html":
            return [
                (f"{BASE_URL}/", "Главная"),
                (None, "Новости"),
            ]
        return [
            (f"{BASE_URL}/", "Главная"),
            (f"{BASE_URL}/novosti", "Новости"),
            (None, label),
        ]
    if kind == "contacts":
        return [
            (f"{BASE_URL}/", "Главная"),
            (None, "Контакты"),
        ]
    if kind == "catalog":
        if page.name == "uslugi-i-tseny.html":
            return [
                (f"{BASE_URL}/", "Главная"),
                (None, "Услуги и цены"),
            ]
        return [
            (f"{BASE_URL}/", "Главная"),
            (f"{BASE_URL}/uslugi-i-tseny", "Услуги и цены"),
            (None, label),
        ]
    if kind == "about":
        return [
            (f"{BASE_URL}/", "Главная"),
            (None, "О компании"),
        ]
    if kind == "jobs":
        return [
            (f"{BASE_URL}/", "Главная"),
            (None, "Вакансии"),
        ]
    return [
        (f"{BASE_URL}/", "Главная"),
        (f"{BASE_URL}/uslugi-i-tseny", "Услуги и цены"),
        (None, label),
    ]


def breadcrumb_markup(page: Path, kind: str, label: str) -> str:
    items = breadcrumb_items(page, kind, label)
    if not items:
        return ""
    prefix = "../" if page.parent.name == "news" else ""

    def href_from_url(url: str) -> str:
        path = url.replace(BASE_URL, "").strip("/")
        if not path:
            return f"{prefix}index.html" if prefix else "index.html"
        return f"{prefix}{path}.html"

    chunks = ['<nav class="concept-breadcrumbs" aria-label="Хлебные крошки">']
    for idx, (url, name) in enumerate(items):
        if idx:
            chunks.append('<span class="concept-breadcrumbs__sep">/</span>')
        if url is None:
            chunks.append(f'<span class="concept-breadcrumbs__current" aria-current="page">{name}</span>')
        else:
            chunks.append(f'<a href="{href_from_url(url)}">{name}</a>')
    chunks.append("</nav>")
    return "\n".join(chunks)


def breadcrumb_schema(page: Path, kind: str, label: str) -> dict | None:
    items = breadcrumb_items(page, kind, label)
    if not items:
        return None
    list_items = []
    for pos, (url, name) in enumerate(items, start=1):
        item = {"@type": "ListItem", "position": pos, "name": name}
        if url:
            item["item"] = url
        list_items.append(item)
    return {
        "@type": "BreadcrumbList",
        "@id": canonical_url(page) + "#breadcrumbs",
        "itemListElement": list_items,
    }


def clinic_schema() -> dict:
    return {
        "@type": ["VeterinaryCare", "LocalBusiness", "MedicalBusiness", "Organization"],
        "@id": f"{BASE_URL}/#clinic",
        "name": SITE_NAME,
        "url": f"{BASE_URL}/",
        "description": SITE_DESCRIPTION,
        "telephone": PHONE,
        "image": f"{BASE_URL}/54889242_2.jpg",
        "logo": f"{BASE_URL}/logo-1.gif",
        "priceRange": "₽₽",
        "address": {
            "@type": "PostalAddress",
            "streetAddress": STREET_ADDRESS,
            "addressLocality": ADDRESS_LOCALITY,
            "addressCountry": "RU",
        },
        "geo": {
            "@type": "GeoCoordinates",
            "latitude": LATITUDE,
            "longitude": LONGITUDE,
        },
        "openingHoursSpecification": [
            {
                "@type": "OpeningHoursSpecification",
                "dayOfWeek": [
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday",
                    "Saturday",
                    "Sunday",
                ],
                "opens": "00:00",
                "closes": "23:59",
            }
        ],
        "areaServed": [
            {"@type": "City", "name": "Раменское"},
            {"@type": "AdministrativeArea", "name": "Раменский район"},
        ],
    }


def page_schema(page: Path, kind: str, title: str, description: str, image: str) -> list[dict]:
    url = canonical_url(page)
    graph: list[dict] = []
    graph.append(
        {
            "@type": "WebPage" if kind != "contacts" else "ContactPage",
            "@id": url + "#webpage",
            "url": url,
            "name": title,
            "description": description,
            "isPartOf": {"@id": f"{BASE_URL}/#website"},
            "about": {"@id": f"{BASE_URL}/#clinic"},
            "primaryImageOfPage": {"@type": "ImageObject", "url": image},
        }
    )
    if kind == "home":
        graph.insert(
            0,
            {
                "@type": "WebSite",
                "@id": f"{BASE_URL}/#website",
                "url": f"{BASE_URL}/",
                "name": SITE_NAME,
                "description": SITE_DESCRIPTION,
            },
        )
        graph.append(clinic_schema())
    else:
        graph.append(clinic_schema())
    return graph


def service_schema(page: Path, title: str, description: str) -> dict:
    return {
        "@type": "Service",
        "@id": canonical_url(page) + "#service",
        "name": title,
        "description": description,
        "serviceType": title,
        "provider": {"@id": f"{BASE_URL}/#clinic"},
        "areaServed": {"@type": "City", "name": ADDRESS_LOCALITY},
        "url": canonical_url(page),
    }


def article_schema(page: Path, title: str, description: str, image: str) -> dict:
    return {
        "@type": "BlogPosting",
        "@id": canonical_url(page) + "#article",
        "headline": title,
        "description": description,
        "mainEntityOfPage": {"@id": canonical_url(page) + "#webpage"},
        "publisher": {"@id": f"{BASE_URL}/#clinic"},
        "author": {"@type": "Organization", "name": SITE_NAME},
        "image": {"@type": "ImageObject", "url": image},
        "url": canonical_url(page),
    }


def catalog_schema(text: str, page: Path, title: str) -> dict:
    items = []
    for href, name in re.findall(r'<a class="concept-service-card" href="([^"]+)".*?<h2>(.*?)</h2>', text, re.S):
        href = href.strip()
        href = STATIC_REMAP.get(href, href)
        if href and not href.startswith(("http://", "https://")):
            clean = href.split("?", 1)[0].split("#", 1)[0]
            if not clean.endswith(".html") and (ROOT / f"{clean}.html").exists():
                clean = f"{clean}.html"
            if clean.endswith(".html"):
                items.append(
                    {
                        "@type": "Offer",
                        "name": strip_tags(name),
                        "url": f"{BASE_URL}/{clean[:-5]}",
                    }
                )
    return {
        "@type": "OfferCatalog",
        "@id": canonical_url(page) + "#catalog",
        "name": title,
        "itemListElement": items,
    }


def build_ldjson(page: Path, text: str, kind: str, title: str, description: str, image: str) -> str:
    graph = page_schema(page, kind, title, description, image)
    breadcrumb = breadcrumb_schema(page, kind, title)
    if breadcrumb:
        graph.append(breadcrumb)
    if kind == "service":
        graph.append(service_schema(page, title, description))
    elif kind == "catalog":
        graph.append(catalog_schema(text, page, title))
    elif kind == "article":
        graph.append(article_schema(page, title, description, image))
    elif kind == "listing":
        graph.append(
            {
                "@type": "CollectionPage",
                "@id": canonical_url(page) + "#collection",
                "name": title,
                "url": canonical_url(page),
                "isPartOf": {"@id": f"{BASE_URL}/#website"},
            }
        )
    data = {"@context": "https://schema.org", "@graph": graph}
    return json.dumps(data, ensure_ascii=False, indent=2)


def normalize_local_link(page: Path, value: str, attr: str) -> str:
    original = value
    value = value.replace("index.html.1.html", "index.html")
    if value.startswith(("http://", "https://", "tel:", "mailto:", "#", "javascript:")):
        return value
    if ".html " in value:
        value = value.split(".html", 1)[0] + ".html"
    value = STATIC_REMAP.get(value, value)
    clean = value.split("?", 1)[0].split("#", 1)[0]
    if page.parent.name == "news" and not clean.startswith(("../", "/")):
        root_candidate = ROOT / clean
        root_html_candidate = ROOT / f"{clean}.html"
        if root_candidate.exists():
            value = "../" + value
            clean = "../" + clean
        elif root_html_candidate.exists():
            suffix = value[len(clean):]
            value = "../" + clean + ".html" + suffix
            clean = "../" + clean + ".html"
    if not clean.startswith(("../", "/")) and "." not in Path(clean).name:
        html_candidate = page.parent / f"{clean}.html"
        root_html_candidate = ROOT / f"{clean}.html"
        if html_candidate.exists():
            suffix = value[len(clean):]
            value = clean + ".html" + suffix
        elif root_html_candidate.exists():
            suffix = value[len(clean):]
            prefix = "../" if page.parent.name == "news" else ""
            value = prefix + clean + ".html" + suffix
    if attr == "href" and value in {"#contacts", "../#contacts"}:
        return "../contacts.html" if page.parent.name == "news" else "contacts.html"
    if original != value:
        return value
    return value


def fix_links(text: str, page: Path) -> str:
    def repl(match: re.Match[str]) -> str:
        attr, value = match.group(1), match.group(2)
        fixed = normalize_local_link(page, value, attr)
        return f'{attr}="{fixed}"'

    return re.sub(r'(href|src)="([^"]+)"', repl, text)


def improve_alts(text: str) -> str:
    text = text.replace('alt="Ветеринар на связи"', 'alt="Логотип ветеринарной клиники Ветеринар на связи"')
    text = text.replace('alt="Фото клиники"', 'alt="Интерьер ветеринарной клиники Ветеринар на связи в Раменском"')
    text = text.replace('alt="Прием в ветеринарной клинике"', 'alt="Прием питомца в ветеринарной клинике Ветеринар на связи в Раменском"')
    text = text.replace('alt="Ветеринарная клиника Ветеринар на связи"', 'alt="Фасад ветеринарной клиники Ветеринар на связи в Раменском"')

    def service_alt(match: re.Match[str]) -> str:
        href, img, title = match.group(1), match.group(2), strip_tags(match.group(3))
        alt = f'{title} — ветеринарная клиника Ветеринар на связи, Раменское'
        return f'<a class="concept-service" href="{href}">\n              <img src="{img}" alt="{alt}">\n              <h3>{match.group(3)}</h3>'

    return re.sub(
        r'<a class="concept-service" href="([^"]+)">\s*<img src="([^"]+)" alt="">\s*<h3>(.*?)</h3>',
        service_alt,
        text,
        flags=re.S,
    )


def inject_head(text: str, page: Path, kind: str, title: str, description: str, image: str) -> str:
    text = re.sub(r"\n?\s*<!-- SEO META START -->.*?<!-- SEO META END -->\s*", "\n", text, flags=re.S)
    text = re.sub(r"\n?\s*<link rel=\"canonical\"[^>]*>\s*", "\n", text)
    text = re.sub(r"\n?\s*<meta property=\"og:[^\"]+\"[^>]*>\s*", "\n", text)
    text = re.sub(r"\n?\s*<meta name=\"twitter:card\"[^>]*>\s*", "\n", text)
    text = re.sub(r"\n?\s*<script type=\"application/ld\\+json\">.*?</script>\s*", "\n", text, flags=re.S)
    og_type = "article" if kind == "article" else "website"
    head = f"""
  <!-- SEO META START -->
  <link rel="canonical" href="{canonical_url(page)}">
  <meta property="og:type" content="{og_type}">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{description}">
  <meta property="og:image" content="{image}">
  <meta property="og:url" content="{canonical_url(page)}">
  <meta name="twitter:card" content="summary_large_image">
  <script type="application/ld+json">
{build_ldjson(page, text, kind, title, description, image)}
  </script>
  <!-- SEO META END -->
"""
    return text.replace("</head>", head + "\n</head>")


def inject_breadcrumbs(text: str, page: Path, kind: str, title: str) -> str:
    text = re.sub(r"\n?\s*<!-- SEO BREADCRUMBS START -->.*?<!-- SEO BREADCRUMBS END -->\s*", "\n", text, flags=re.S)
    crumbs = breadcrumb_markup(page, kind, title)
    if not crumbs:
        return text
    pattern = r'(<p class="concept-kicker">.*?</p>)'
    replacement = r'\1' + "\n          <!-- SEO BREADCRUMBS START -->\n          " + crumbs.replace("\n", "\n          ") + "\n          <!-- SEO BREADCRUMBS END -->"
    return re.sub(pattern, replacement, text, count=1, flags=re.S)


def render_contacts_page() -> str:
    return """<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="all">
  <meta name="description" content="Контакты ветеринарной клиники Ветеринар на связи в Раменском: адрес, телефон, график работы и карта проезда.">
  <title>Контакты ветеринарной клиники Ветеринар на связи в Раменском</title>
  <link rel="preload" href="open_sans-r.woff2" as="font" crossorigin>
  <link rel="preload" href="open_sans-b.woff2" as="font" crossorigin>
  <link rel="preload" href="montserrat-b.woff2" as="font" crossorigin>
  <link rel="icon" href="favicon.png" type="image/png">
  <link rel="stylesheet" href="design-in3p88t1t-1600832236_styles.css">
  <link rel="stylesheet" href="index-skolkovo.css?v=20260430-blue-phone-yellow-icon">
</head>
<body class="vetnas-concept">
  <div class="concept-page">
    <header class="concept-topbar">
      <div class="concept-shell concept-nav">
        <a class="concept-brand" href="index.html">
          <img src="logo-1.gif" alt="Логотип ветеринарной клиники Ветеринар на связи">
          <b>Ветеринар на связи <span>ветеринарная клиника</span></b>
        </a>
        <nav class="concept-menu" aria-label="Навигация">
          <a href="index.html">Главная</a>
          <a href="o-kompanii.html">О компании</a>
          <a href="uslugi-i-tseny.html">Услуги и цены</a>
          <a href="vakansii.html">Вакансии</a>
          <a href="novosti.html">Новости</a>
          <a href="contacts.html">Контакты</a>
        </nav>
        <a class="concept-phone" href="tel:+74951444803">+7 (495) 144-48-03</a>
      </div>
    </header>

    <details class="concept-side-menu" aria-label="Меню сайта">
      <summary class="concept-side-menu__trigger"><span>Меню</span></summary>
      <div class="concept-side-menu__panel">
        <a class="concept-side-menu__main" href="index.html">Главная</a>
        <a class="concept-side-menu__main" href="o-kompanii.html">О компании</a>
        <a class="concept-side-menu__main" href="uslugi-i-tseny.html">Услуги и цены</a>
        <a class="concept-side-menu__main" href="vakansii.html">Вакансии</a>
        <a class="concept-side-menu__main" href="novosti.html">Новости</a>
        <a class="concept-side-menu__main" href="contacts.html">Контакты</a>
      </div>
    </details>

    <a class="concept-phone-float" href="tel:+74951444803" aria-label="Позвонить в клинику"><span>☎</span></a>

    <main>
      <section class="concept-page-hero">
        <div class="concept-shell">
          <p class="concept-kicker">Раменское, Красноармейская, 13</p>
          <h1>Контакты ветеринарной клиники в Раменском</h1>
          <p>Адрес, телефон, круглосуточный режим работы и карта проезда в ветеринарную клинику «Ветеринар на связи».</p>
        </div>
      </section>

      <section class="concept-section">
        <div class="concept-shell">
          <div class="concept-content-card">
            <div class="concept-content">
              <h2>Как связаться с клиникой</h2>
              <p>Если питомцу нужна помощь, вы можете позвонить в клинику и уточнить ближайшее удобное время приема, подготовку к визиту и порядок действий в срочной ситуации.</p>
              <div class="concept-contact-grid">
                <article class="concept-contact-card">
                  <h3>Адрес</h3>
                  <p>г. Раменское, ул. Красноармейская, д. 13</p>
                </article>
                <article class="concept-contact-card">
                  <h3>Телефон</h3>
                  <p><a href="tel:+74951444803">+7 (495) 144-48-03</a></p>
                </article>
                <article class="concept-contact-card">
                  <h3>График работы</h3>
                  <p>Ежедневно, 24/7</p>
                </article>
              </div>
              <h2>Что удобно уточнить перед визитом</h2>
              <ul>
                <li>свободное время приема и срочность обращения;</li>
                <li>нужна ли подготовка к анализам, УЗИ, рентгену или процедурам;</li>
                <li>какие документы и результаты прошлых обследований взять с собой;</li>
                <li>как безопасно привезти питомца в клинику.</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      <section class="concept-section concept-map-section" id="contacts" aria-label="Карта проезда">
        <div class="concept-shell">
          <div class="concept-section-head">
            <h2>Как нас найти</h2>
            <p>г. Раменское, ул. Красноармейская, д. 13</p>
          </div>
          <div class="concept-map-card">
            <iframe src="https://yandex.ru/map-widget/v1/?ll=38.233634%2C55.572556&z=18&pt=38.233634%2C55.572556%2Cpm2rdm" title="Ветеринар на связи на карте" loading="lazy"></iframe>
          </div>
        </div>
      </section>

      <section class="concept-section concept-section--royal">
        <div class="concept-shell concept-final">
          <div>
            <h2>Нужна помощь питомцу?</h2>
            <p>Позвоните в клинику, чтобы быстро сориентироваться по записи и дальнейшим действиям.</p>
          </div>
          <a class="concept-button concept-button--primary" href="tel:+74951444803">Позвонить</a>
        </div>
      </section>
    </main>

    <footer class="concept-footer">
      <div class="concept-shell">
        <span>© 2026 Ветеринар на связи</span>
        <a href="index.html">Главная</a>
      </div>
    </footer>
  </div>
  <script src="concept-menu.js?v=20260430-blue-phone-yellow-icon" defer></script>
</body>
</html>
"""


def render_diagnostics_page() -> str:
    return """<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="all">
  <meta name="description" content="Диагностика животных в Раменском: прием, анализы, УЗИ, рентген и обследования в ветеринарной клинике Ветеринар на связи.">
  <title>Диагностика животных в Раменском | Ветеринар на связи</title>
  <link rel="preload" href="open_sans-r.woff2" as="font" crossorigin>
  <link rel="preload" href="open_sans-b.woff2" as="font" crossorigin>
  <link rel="preload" href="montserrat-b.woff2" as="font" crossorigin>
  <link rel="icon" href="favicon.png" type="image/png">
  <link rel="stylesheet" href="design-in3p88t1t-1600832236_styles.css">
  <link rel="stylesheet" href="index-skolkovo.css?v=20260430-blue-phone-yellow-icon">
</head>
<body class="vetnas-concept">
  <div class="concept-page">
    <header class="concept-topbar">
      <div class="concept-shell concept-nav">
        <a class="concept-brand" href="index.html">
          <img src="logo-1.gif" alt="Логотип ветеринарной клиники Ветеринар на связи">
          <b>Ветеринар на связи <span>ветеринарная клиника</span></b>
        </a>
        <nav class="concept-menu" aria-label="Навигация">
          <a href="index.html">Главная</a>
          <a href="o-kompanii.html">О компании</a>
          <a href="uslugi-i-tseny.html">Услуги и цены</a>
          <a href="vakansii.html">Вакансии</a>
          <a href="novosti.html">Новости</a>
          <a href="contacts.html">Контакты</a>
        </nav>
        <a class="concept-phone" href="tel:+74951444803">+7 (495) 144-48-03</a>
      </div>
    </header>

    <details class="concept-side-menu" aria-label="Меню сайта">
      <summary class="concept-side-menu__trigger"><span>Меню</span></summary>
      <div class="concept-side-menu__panel">
        <a class="concept-side-menu__main" href="index.html">Главная</a>
        <a class="concept-side-menu__main" href="o-kompanii.html">О компании</a>
        <a class="concept-side-menu__main" href="uslugi-i-tseny.html">Услуги и цены</a>
        <a class="concept-side-menu__main" href="vakansii.html">Вакансии</a>
        <a class="concept-side-menu__main" href="novosti.html">Новости</a>
        <a class="concept-side-menu__main" href="contacts.html">Контакты</a>
      </div>
    </details>

    <a class="concept-phone-float" href="tel:+74951444803" aria-label="Позвонить в клинику"><span>☎</span></a>

    <main>
      <section class="concept-page-hero">
        <div class="concept-shell">
          <p class="concept-kicker">Раменское, Красноармейская, 13</p>
          <h1>Диагностика животных в Раменском</h1>
          <p>Прием, анализы, УЗИ, рентген и другие обследования по показаниям в ветеринарной клинике «Ветеринар на связи».</p>
        </div>
      </section>

      <section class="concept-section">
        <div class="concept-shell">
          <div class="concept-content-card">
            <div class="concept-content">
              <h2>Какие обследования можно обсудить на приеме</h2>
              <div class="concept-service-grid">
                <a class="concept-service-card" href="analiz-krovi-zhivotnykh-ramenskoe.html">
                  <span>Лаборатория</span>
                  <h2>Анализы крови</h2>
                  <p>Общий и биохимический анализы по показаниям после очного осмотра.</p>
                  <b>Подробнее</b>
                </a>
                <a class="concept-service-card" href="analiz-mochi-zhivotnym-ramenskoe.html">
                  <span>Лаборатория</span>
                  <h2>Анализ мочи</h2>
                  <p>Оценка состояния мочевыделительной системы и контроль по жалобам.</p>
                  <b>Подробнее</b>
                </a>
                <a class="concept-service-card" href="rentgen.html">
                  <span>Диагностика</span>
                  <h2>Рентген</h2>
                  <p>Снимки при травмах, боли, кашле, хромоте и других показаниях.</p>
                  <b>Подробнее</b>
                </a>
                <a class="concept-service-card" href="uzi.html">
                  <span>Диагностика</span>
                  <h2>УЗИ</h2>
                  <p>Ультразвуковая диагностика органов и систем по назначению врача.</p>
                  <b>Подробнее</b>
                </a>
                <a class="concept-service-card" href="ekg-zhivotnym-ramenskoe.html">
                  <span>Кардиология</span>
                  <h2>ЭКГ</h2>
                  <p>Обследование сердца и оценка ритма у животных по показаниям.</p>
                  <b>Подробнее</b>
                </a>
                <a class="concept-service-card" href="biohimiya-krovi-zhivotnykh.html">
                  <span>Лаборатория</span>
                  <h2>Биохимия крови</h2>
                  <p>Помогает уточнить состояние органов и подобрать дальнейший план.</p>
                  <b>Подробнее</b>
                </a>
              </div>
              <h2>Как строится диагностика</h2>
              <p>Ветеринар сначала проводит очный осмотр, уточняет жалобы, анамнез, питание, перенесенные болезни и текущее состояние питомца. После этого врач объясняет, какие исследования действительно нужны и в какой последовательности их лучше выполнить.</p>
              <ul>
                <li>объем обследования зависит от симптомов, возраста и общего состояния животного;</li>
                <li>часть исследований можно сделать в день обращения, часть назначается по результатам приема;</li>
                <li>итоги диагностики обсуждаются вместе с планом лечения или наблюдения.</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      <section class="concept-section concept-section--royal">
        <div class="concept-shell concept-final">
          <div>
            <h2>Нужна диагностика питомцу?</h2>
            <p>Позвоните в клинику, чтобы уточнить запись, подготовку и порядок обследования.</p>
          </div>
          <a class="concept-button concept-button--primary" href="tel:+74951444803">Позвонить</a>
        </div>
      </section>
    </main>

    <footer class="concept-footer">
      <div class="concept-shell">
        <span>© 2026 Ветеринар на связи</span>
        <a href="index.html">Главная</a>
      </div>
    </footer>
  </div>
  <script src="concept-menu.js?v=20260430-blue-phone-yellow-icon" defer></script>
</body>
</html>
"""


def process_page(page: Path) -> None:
    text = page.read_text(encoding="utf-8")
    text = fix_links(text, page)
    text = improve_alts(text)
    kind = page_kind(page, text)
    title = page_title(text)
    h1 = h1_text(text, title)
    description = meta_description(text, strip_tags(h1) or SITE_DESCRIPTION)
    image = first_image(text)
    text = inject_head(text, page, kind, title, description, image)
    text = inject_breadcrumbs(text, page, kind, h1)
    page.write_text(text, encoding="utf-8")


def main() -> None:
    (ROOT / "contacts.html").write_text(render_contacts_page(), encoding="utf-8")
    (ROOT / "diagnostika.html").write_text(render_diagnostics_page(), encoding="utf-8")

    pages = []
    pages.extend(sorted(ROOT.glob("*.html")))
    pages.extend(sorted((ROOT / "news").glob("*.html")))

    for page in pages:
        if page.name in SKIP_FILES:
            continue
        text = page.read_text(encoding="utf-8")
        if 'class="vetnas-concept"' not in text:
            continue
        process_page(page)


if __name__ == "__main__":
    main()
