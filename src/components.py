"""
Reusable page components for Get Solve Spring.
Every page is assembled from these functions, so a change here updates the
whole site on the next build.
"""
import html
import json

import config as C

e = html.escape


# ---------------------------------------------------------------- brand ----
MARK_PATHS = (
    '<path d="M10 39 L19 35 L10 31 L19 27 L10 23 L35 13" fill="none" stroke="{fg}" stroke-width="4" '
    'stroke-linecap="round" stroke-linejoin="round"/>'
    '<path d="M27 11.5 L36.5 12.5 L32.5 21" fill="none" stroke="{fg}" stroke-width="4" '
    'stroke-linecap="round" stroke-linejoin="round"/>'
)


def mark(bg="#10292d", fg="#ffd84d", title=None):
    t = f"<title>{e(title)}</title>" if title else ""
    aria = 'role="img"' if title else 'aria-hidden="true" focusable="false"'
    return (f'<svg viewBox="0 0 48 48" {aria}>{t}<rect width="48" height="48" rx="11" fill="{bg}"/>'
            + MARK_PATHS.format(fg=fg) + "</svg>")


ICONS = {
    "search": '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><circle cx="10.5" cy="10.5" r="6.5" fill="none" stroke="currentColor" stroke-width="2.2"/><path d="M15.5 15.5L21 21" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/></svg>',
    "menu": '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M3 6h18M3 12h18M3 18h18" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/></svg>',
    "money-pay": '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><rect x="2.5" y="6" width="19" height="12" rx="2" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="12" cy="12" r="2.8" fill="none" stroke="currentColor" stroke-width="2"/></svg>',
    "work-career": '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><rect x="3" y="7.5" width="18" height="12" rx="2" fill="none" stroke="currentColor" stroke-width="2"/><path d="M9 7.5V5.5a1.5 1.5 0 0 1 1.5-1.5h3A1.5 1.5 0 0 1 15 5.5v2M3 13h18" fill="none" stroke="currentColor" stroke-width="2"/></svg>',
    "small-business": '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M4 10v10h16V10M3 10l2-6h14l2 6zM10 20v-5h4v5" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/></svg>',
    "everyday-math": '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M7 4v6M4 7h6M14 7h6M5 15l4 4M9 15l-4 4M14 15h6M14 19h6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
    "personal-finance": '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M4 20V11M10 20V7M16 20v-6M3 20h18M14 6l4-3 3 3" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "taxes": '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M6 3h9l4 4v14H6z M15 3v4h4M9 12h7M9 16h7" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/></svg>',
    "mindset": '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><circle cx="12" cy="12" r="8.5" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="12" cy="12" r="4.5" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="12" cy="12" r="1" fill="currentColor"/></svg>',
    "faith-scripture": '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M12 6c-2-1.5-5-2-8-1.5v14c3-.5 6 0 8 1.5 2-1.5 5-2 8-1.5v-14C17 4 14 4.5 12 6zM12 6v14" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/></svg>',
}


# ----------------------------------------------------------------- head ----
def head(title, description, path, jsonld=None, og_type="website", extra=""):
    url = C.SITE_URL + path
    full_title = title if title.endswith(C.SITE_NAME) else f"{title} | {C.SITE_NAME}"
    ld = ""
    for block in (jsonld or []):
        ld += '<script type="application/ld+json">' + json.dumps(block, ensure_ascii=False).replace("</", "<\\/") + "</script>\n"
    adsense = ""
    if C.ADSENSE_CLIENT:
        adsense = (f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={e(C.ADSENSE_CLIENT)}" '
                   'crossorigin="anonymous"></script>\n')
    return f"""<!doctype html>
<html lang="en-US">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(full_title)}</title>
<meta name="description" content="{e(description)}">
<link rel="canonical" href="{e(url)}">
<meta name="theme-color" content="#10292d">
<meta property="og:site_name" content="{C.SITE_NAME}">
<meta property="og:type" content="{og_type}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:url" content="{e(url)}">
<meta property="og:image" content="{C.SITE_URL}/assets/images/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="en_US">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(title)}">
<meta name="twitter:description" content="{e(description)}">
<meta name="twitter:image" content="{C.SITE_URL}/assets/images/og-image.png">
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="icon" href="/assets/icons/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/assets/icons/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="preload" href="/assets/fonts/hanken-grotesk-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/bricolage-grotesque-latin-800-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/css/site.css?v={C.ASSET_VERSION}">
{extra}{adsense}{ld}</head>
"""


# --------------------------------------------------------------- header ----
def nav_items():
    from content import CATEGORIES
    return [("Tools", "/tools/")] + [(c["name"], f"/{c['slug']}/") for c in CATEGORIES] + [("Blog", "/blog/")]


def header(active=""):
    def cur(href):
        return ' aria-current="page"' if href == active else ""
    cats = "".join(f'<li><a href="{h}"{cur(h)}>{e(n)}</a></li>' for n, h in nav_items())
    mobile = "".join(f'<li><a href="{h}"{cur(h)}>{e(n)}</a></li>' for n, h in [("Home", "/")] + nav_items())
    search = f"""<form class="header-search" action="/search/" method="get" role="search" aria-label="{{label}}">
<label class="visually-hidden" for="{{id}}">Search tools and guides</label>
{ICONS['search']}<input id="{{id}}" name="q" type="search" placeholder="Search tools and guides" autocomplete="off">
</form>"""
    return f"""<body class="{'show-ad-slots' if C.SHOW_AD_SLOTS else ''}">
<a class="skip-link" href="#main">Skip to main content</a>
<header class="site-header">
<div class="wrap header-main">
<a class="brand" href="/" aria-label="{C.SITE_NAME} home">{mark()}<span class="brand-name">{C.SITE_NAME}</span></a>
{search.replace('{id}', 'q-head').replace('{label}', 'Site search')}
<nav class="header-links" aria-label="Primary"><a href="/tools/"{cur('/tools/')}>Tools</a><a href="/blog/"{cur('/blog/')}>Blog</a></nav>
<button class="menu-toggle" type="button" aria-expanded="false" aria-controls="mobile-menu">{ICONS['menu']}Menu</button>
</div>
<nav class="cat-nav" aria-label="Categories"><div class="wrap"><ul>{cats}</ul></div></nav>
<div class="mobile-menu wrap" id="mobile-menu" data-open="false">
{search.replace('{id}', 'q-mobile').replace('{label}', 'Site search, menu')}
<nav aria-label="Mobile"><ul>{mobile}</ul></nav>
</div>
</header>
<main id="main">
"""


# --------------------------------------------------------------- footer ----
def footer(scripts=""):
    links = [("Tools", "/tools/"), ("Blog", "/blog/"), ("About", "/about/"), ("Contact", "/contact/"),
             ("Privacy Policy", "/privacy/"), ("Terms of Use", "/terms/"), ("Disclaimer", "/disclaimer/"),
             ("Accessibility", "/accessibility/"), ("Methodology", "/methodology/"),
             ("Affiliate Disclosure", "/affiliate-disclosure/")]
    lis = "".join(f'<li><a href="{h}">{n}</a></li>' for n, h in links)
    return f"""</main>
<footer class="site-footer">
<div class="wrap">
<div class="footer-grid">
<div>
<div class="footer-brand">{mark(bg="#ffd84d", fg="#10292d")}{C.SITE_NAME}</div>
<p class="footer-tag">Get unstuck. Get answers. Get moving.</p>
<p class="small">An American-based online resource with simple tools, calculators, and guides for everyday questions.</p>
</div>
<nav aria-label="Footer"><ul class="footer-links">{lis}</ul></nav>
</div>
<div class="footer-base">
<p>Calculators provide estimates for educational purposes. They are not financial, tax, or legal advice. <a href="/disclaimer/" style="color:#fff">Read the disclaimer</a>.</p>
<p>© {C.YEAR} {C.SITE_NAME}. American-based online resource.</p>
</div>
</div>
</footer>
<script src="/assets/js/site.js?v={C.ASSET_VERSION}" defer></script>
{scripts}</body>
</html>
"""


# ----------------------------------------------------------- breadcrumbs ----
def breadcrumbs(trail):
    """trail: [(name, path)], last item is current page."""
    items = []
    for i, (name, path) in enumerate(trail):
        if i == len(trail) - 1:
            items.append(f'<li><span aria-current="page">{e(name)}</span></li>')
        else:
            items.append(f'<li><a href="{path}">{e(name)}</a></li>')
    return f'<nav class="breadcrumbs wrap" aria-label="Breadcrumb"><ol>{"".join(items)}</ol></nav>'


def breadcrumb_ld(trail):
    return {
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": C.SITE_URL + p}
            for i, (n, p) in enumerate(trail)
        ],
    }


def webpage_ld(name, description, path):
    return {"@context": "https://schema.org", "@type": "WebPage", "name": name, "description": description,
            "url": C.SITE_URL + path, "isPartOf": {"@type": "WebSite", "name": C.SITE_NAME, "url": C.SITE_URL + "/"}}


# ----------------------------------------------------------------- cards ----
def tool_tile(t):
    return (f'<a class="tile" href="/tools/{t["slug"]}/"><span class="tile-name">{e(t["name"])}</span>'
            f'<span class="tile-eg">{e(t["teaser"])}</span><span class="tile-desc">{e(t["short"])}</span></a>')


def tool_row(t):
    return f'<li><a href="/tools/{t["slug"]}/"><strong>{e(t["name"])}</strong><span>{e(t["short"])}</span></a></li>'


def article_card(a, cat_name):
    return f"""<li class="article-card" data-cat="{a['category']}"><a href="/blog/{a['slug']}/">
<p class="card-cat">{e(cat_name)}</p><h3>{e(a['title'])}</h3><p>{e(a['description'])}</p>
<span class="card-meta"><span>{a['minutes']} min read</span> <span>{a['published_human']}</span></span></a></li>"""


def category_link(c):
    return (f'<a class="cat-link" href="/{c["slug"]}/"><span class="cat-icon">{ICONS[c["slug"]]}</span>'
            f'<span class="cat-title">{e(c["name"])}</span><span class="cat-desc">{e(c["blurb"])}</span></a>')


def link_list(items):
    """items: [(title, href, sub)]"""
    return '<ul class="link-list">' + "".join(
        f'<li><a href="{h}">{e(t)}<span>{e(s)}</span></a></li>' for t, h, s in items) + "</ul>"


def ad_slot(name):
    """Placeholder for a future ad unit. Hidden unless SHOW_AD_SLOTS is True in config.
    Never place one inside or directly beside a calculator form."""
    return f'<div class="ad-slot wrap" data-ad-slot="{name}" aria-hidden="true">Advertisement placeholder ({name})</div>'


# ------------------------------------------------------------ disclaimer ----
DISCLAIMERS = {
    "info": "<strong>Educational information — not financial or legal advice.</strong> This page explains general rules and options. Your situation may differ. For decisions about credit, loans, or disputes, check official sources or talk with a qualified professional.",
    "general": "<strong>Estimate only.</strong> Results are for general information and depend on the numbers you enter. Your actual pay or results may differ. Check important figures with your employer, a professional, or the official source.",
    "financial": "<strong>Estimate only — not financial advice.</strong> This calculator uses the assumptions shown and can't account for your full situation. Real interest rates, returns, and fees vary. Consider talking with a qualified financial professional before making major decisions.",
    "tax": "<strong>Estimate only — not official tax advice.</strong> Get Solve Spring is not affiliated with the IRS or any government agency. Figures are simplified and based on published tax-year data. Your actual tax depends on your full return. For withholding decisions, use official IRS resources or a qualified tax professional.",
}


def disclaimer(kind):
    if kind not in DISCLAIMERS:
        return ""
    return f'<aside class="disclaimer-box" aria-label="Disclaimer"><p>{DISCLAIMERS[kind]} <a href="/disclaimer/">Full disclaimer</a>.</p></aside>'


# ------------------------------------------------------------ calculator ----
def field(f, mode_default=None):
    fid = f"f-{f['name']}"
    kind = f["kind"]
    attrs = [f'id="{fid}"', f'name="{f["name"]}"']
    described = []
    if f.get("help"):
        described.append(f"{fid}-help")
    described.append(f"{fid}-err")
    cls = "field" + (" wide" if f.get("wide") else "")
    extra = ""
    if f.get("modes"):
        extra += f' data-show-modes="{f["modes"]}"'
        if mode_default and mode_default not in f["modes"].split(","):
            extra += " hidden"
    label_attr = f" data-labels='{json.dumps(f['labels'])}'" if f.get("labels") else ""
    label_text = f["label"]
    if f.get("labels") and mode_default in f["labels"]:
        label_text = f["labels"][mode_default]

    if kind == "check":
        checked = " checked" if f["default"] == "1" else ""
        return (f'<div class="{cls} check-field wide"{extra}><input type="checkbox" {" ".join(attrs)} data-default="{f["default"]}"{checked}>'
                f'<label for="{fid}">{e(label_text)}</label></div>')

    if kind == "select":
        opts = "".join(f'<option value="{e(v)}"{" selected" if v == f["default"] else ""}>{e(l)}</option>' for v, l in f["options"])
        control = f'<select {" ".join(attrs)} data-default="{e(f["default"])}" aria-describedby="{" ".join(described)}">{opts}</select>'
    else:
        prefix = suffix = ""
        if kind == "money":
            prefix = "$"
        if kind == "percent":
            suffix = "%"
        if f.get("suffix"):
            suffix = f["suffix"]
        if kind in ("date", "time"):
            attrs.append(f'type="{kind}"')
            if f.get("required"):
                attrs.append("required")
            val = "" if f["default"] in ("", "today") or f["default"].startswith("today") else f["default"]
        else:
            attrs.append('type="text"')
            if kind != "text":
                attrs.append('inputmode="decimal"' if kind != "integer" else 'inputmode="numeric"')
            attrs.append(f'data-kind="{kind}"')
            attrs.append('autocomplete="off"')
            val = f["default"]
            for k in ("min", "max"):
                if k in f:
                    attrs.append(f'data-{k}="{f[k]}"')
            if f.get("positive"):
                attrs.append("data-positive")
            if f.get("optional"):
                attrs.append("data-optional")
        attrs.append(f'value="{e(val)}"')
        attrs.append(f'data-default="{e(f["default"])}"')
        attrs.append(f'aria-describedby="{" ".join(described)}"')
        wrap_cls = "input-wrap" + (" has-prefix" if prefix else "") + (" has-suffix" if suffix else "")
        control = (f'<div class="{wrap_cls}">' + (f'<span class="affix prefix" aria-hidden="true">{prefix}</span>' if prefix else "")
                   + f'<input {" ".join(attrs)}>'
                   + (f'<span class="affix suffix" aria-hidden="true">{e(suffix)}</span>' if suffix else "") + "</div>")
    help_html = f'<span class="help" id="{fid}-help">{e(f["help"])}</span>' if f.get("help") else ""
    return (f'<div class="{cls}"{extra}><label for="{fid}"{label_attr}>{e(label_text)}</label>{control}{help_html}'
            f'<span class="field-error" id="{fid}-err" aria-live="polite"></span></div>')


def calculator(t):
    mode_f = next((f for f in t["fields"] if f["name"] == "mode"), None)
    mode_default = mode_f["default"] if mode_f else None
    main = "".join(field(f, mode_default) for f in t["fields"] if not f.get("adv"))
    adv = [f for f in t["fields"] if f.get("adv")]
    adv_html = ""
    if adv:
        adv_html = ('<details class="more-options"><summary>More options</summary><div class="field-grid">'
                    + "".join(field(f, mode_default) for f in adv) + "</div></details>")
    badge = ""
    if t.get("tax"):
        badge = f'<p class="tax-year-badge" data-tax-badge>Tax year: {C.TAX_DEFAULT_YEAR}</p><p class="small muted" style="margin-top:0">Estimate only — not official tax advice.</p>'
    return f"""<div class="calc-layout">
<form class="calc-form" data-calc="{t['slug']}" novalidate>
{badge}
<fieldset><legend>{e(t.get("legend", "Your numbers"))}</legend>
<div class="field-grid">{main}</div>
{adv_html}
</fieldset>
<div class="calc-actions"><button class="btn" type="submit">{e(t.get("button", "Calculate"))}</button><button class="btn btn-quiet" type="button" data-reset>Reset</button></div>
</form>
<section class="answer" aria-labelledby="answer-h" aria-live="polite">
<h2 id="answer-h">{e(t.get("answer_title", "Your answer"))}</h2>
<div data-answer><p class="muted">Turn on JavaScript to use this calculator. The formula is explained below so you can work it out by hand.</p></div>
</section>
</div>"""


# -------------------------------------------------------------- affiliate ----
def affiliate_box(placement, heading, text, cta):
    """A clearly labeled partner recommendation with the disclosure directly
    under the link (FTC guidance: clear, conspicuous, and close to the link).
    Placement keys and URLs live in config.AFFILIATE_LINKS."""
    url = getattr(C, "AFFILIATE_LINKS", {}).get(placement)
    if not getattr(C, "AFFILIATE_ENABLED", False) or not url:
        return ""
    return f"""<aside class="partner-box" aria-labelledby="partner-{placement}">
<p class="partner-label">Partner resource</p>
<h2 id="partner-{placement}">{e(heading)}</h2>
<p>{e(text)}</p>
<p class="partner-note"><strong>Paid subscription:</strong> {e(getattr(C, "AFFILIATE_PAID_NOTE", ""))}</p>
<p class="partner-cta"><a class="btn btn-partner" href="{e(url)}" rel="sponsored nofollow noopener" target="_blank" data-partner="{e(C.AFFILIATE_PARTNER)}" data-placement="{placement}">{e(cta)}<span class="visually-hidden"> (opens {e(C.AFFILIATE_PARTNER)} in a new tab)</span></a><span class="partner-name">Offered by {e(C.AFFILIATE_PARTNER)}</span></p>
<p class="partner-disclosure">{e(C.AFFILIATE_DISCLOSURE)} <a href="/affiliate-disclosure/">How we handle partners</a>.</p>
</aside>"""
