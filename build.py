#!/usr/bin/env python3
"""
Build the Get Solve Spring website into ./site

    python3 build.py

Requires Python 3.8+ and the `markdown` package (pip install markdown).
Everything in ./site is plain static HTML/CSS/JS that can be uploaded to any
static host (Cloudflare Pages, GitHub Pages, Netlify, etc.).
"""
import datetime
import json
import math
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

import markdown  # noqa: E402

import config as C  # noqa: E402
from components import (ICONS, ad_slot, affiliate_box, article_card, breadcrumb_ld, breadcrumbs, calculator, category_link,  # noqa: E402
                        disclaimer, e, footer, head, header, link_list, mark, tool_row, tool_tile, webpage_ld)
from content import CAT, CATEGORIES, HERO_EXAMPLES, PAGES, POPULAR_QUESTIONS  # noqa: E402
from tools import PLANNED, TOOLS  # noqa: E402

OUT = ROOT / "site"
# The calculator that runs directly on each category page
FEATURED = {
    "money-pay": "hourly-to-salary", "work-career": "overtime", "small-business": "profit-margin",
    "everyday-math": "percentage", "personal-finance": "savings-goal", "taxes": "tax-bracket",
    "mindset": "goal-breakdown", "faith-scripture": "scripture-lookup",
}
TOOL = {t["slug"]: t for t in TOOLS}
PAGES_OUT = []          # (path, priority) for sitemap
SEARCH = []             # search index entries


def write(path, html, priority="0.6"):
    """path like '/tools/overtime/' -> site/tools/overtime/index.html"""
    target = OUT / path.strip("/") / "index.html" if path.endswith("/") else OUT / path.lstrip("/")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(html, encoding="utf-8")
    if path.endswith("/"):
        PAGES_OUT.append((path, priority))


def human_date(iso):
    d = datetime.date.fromisoformat(iso)
    return d.strftime("%B ") + str(d.day) + d.strftime(", %Y")


# ------------------------------------------------------------- tax data ----
def load_tax():
    years = {}
    for f in sorted((ROOT / "src" / "data" / "tax").glob("*.json")):
        d = json.loads(f.read_text())
        years[str(d["year"])] = d
    return years


TAX = load_tax()
BIBLE = json.loads((ROOT / "src" / "data" / "bible-books.json").read_text())
BIBLE["files"] = json.loads((ROOT / "static" / "data" / "web" / "_files.json").read_text())
for t in TOOLS:
    for f in t["fields"]:
        if f.get("options") == "{TAX_YEARS}":
            f["options"] = [(y, f"{y}") for y in sorted(TAX, reverse=True)]
        if f.get("options") == "{BIBLE_BOOKS}":
            f["options"] = [(b[0], b[0]) for b in BIBLE["books"]]
        if f.get("default") == "{TAX_DEFAULT}":
            f["default"] = str(C.TAX_DEFAULT_YEAR)


# ------------------------------------------------------------- articles ----
def load_articles():
    arts = []
    for f in sorted((ROOT / "src" / "articles").glob("*.md")):
        raw = f.read_text(encoding="utf-8")
        meta_txt, body = raw.split("\n---\n", 1)
        meta = {}
        for line in meta_txt.strip().splitlines():
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
        for k in ("tools", "related"):
            meta[k] = [s.strip() for s in meta.get(k, "").split(",") if s.strip()]
        meta["sources"] = [tuple(s.strip().rsplit("|", 1)) for s in meta.get("sources", "").split(";") if s.strip()]
        meta["featured"] = meta.get("featured") == "true"
        meta.setdefault("updated", meta["published"])
        meta["body_md"] = body
        words = len(re.sub(r"<[^>]+>", " ", body).split())
        meta["minutes"] = max(1, math.ceil(words / 230))
        meta["published_human"] = human_date(meta["published"])
        meta["updated_human"] = human_date(meta["updated"])
        arts.append(meta)
    arts.sort(key=lambda a: (a["published"], a["title"]), reverse=True)
    return arts


ARTICLES = load_articles()
ART = {a["slug"]: a for a in ARTICLES}


def check_links():
    for t in TOOLS:
        for s in t["related"]:
            assert s in TOOL, f"{t['slug']}: unknown related tool {s}"
        for s in t["guides"]:
            assert s in ART, f"{t['slug']}: unknown guide {s}"
    for a in ARTICLES:
        for s in a["tools"]:
            assert s in TOOL, f"{a['slug']}: unknown tool {s}"
        for s in a["related"]:
            assert s in ART, f"{a['slug']}: unknown article {s}"
        assert a["category"] in CAT, f"{a['slug']}: unknown category"


def tool_scripts(tools):
    """Script tags a page needs to run the given calculators."""
    out = ""
    if any(t.get("tax") for t in tools):
        out += f'<script src="/assets/js/tax-data.js?v={C.ASSET_VERSION}" defer></script>\n'
    if any(t.get("bible") for t in tools):
        out += f'<script src="/assets/js/bible-data.js?v={C.ASSET_VERSION}" defer></script>\n'
    out += f'<script src="/assets/js/calc.js?v={C.ASSET_VERSION}" defer></script>\n'
    return out


def tools_in(cat_slug):
    return [t for t in TOOLS if t["cat"] == cat_slug or cat_slug in t.get("also", [])]


def articles_in(cat_slug):
    return [a for a in ARTICLES if a["category"] == cat_slug]


# ---------------------------------------------------------------- pages ----
def build_home():
    title = f"{C.SITE_NAME}: Simple Tools and Calculators for Everyday Questions"
    desc = "Free calculators and plain-English guides for pay, budgets, savings, small business pricing, percentages, dates, and more. Get unstuck. Get answers. Get moving."
    ld = [{
        "@context": "https://schema.org", "@type": "WebSite", "name": C.SITE_NAME, "url": C.SITE_URL + "/",
        "description": desc,
        "potentialAction": {"@type": "SearchAction", "target": {"@type": "EntryPoint", "urlTemplate": C.SITE_URL + "/search/?q={search_term_string}"},
                            "query-input": "required name=search_term_string"},
    }, {
        "@context": "https://schema.org", "@type": "Organization", "name": C.SITE_NAME, "url": C.SITE_URL + "/",
        "logo": C.SITE_URL + "/assets/icons/icon-512.png",
    }]
    popular = [t for t in TOOLS if t.get("popular")]
    tries = "".join(f'<button type="button" data-try="hero-q">{e(x)}</button>' for x in HERO_EXAMPLES)
    featured_calc = TOOL["hourly-to-salary"]
    latest = ARTICLES[:6]
    qs = "".join(f'<li><a href="{h}">{e(q)}<span class="q-target">{e(lbl)}</span></a></li>' for q, h, lbl in POPULAR_QUESTIONS)
    html = head(title, desc, "/", ld) + header("/") + f"""
<section class="hero">
<div class="wrap">
<p class="hero-brand">{mark(bg="#ffd84d", fg="#10292d")}{C.SITE_NAME}</p>
<h1>Get unstuck. Get answers. Get moving.</h1>
<p class="lede">Simple tools, calculators, and guides for figuring out everyday questions.</p>
<form class="ask" action="/search/" method="get" role="search" aria-label="Ask a question" data-live-search>
<label for="hero-q">What are you trying to figure out?</label>
<div class="ask-row"><input id="hero-q" name="q" type="search" autocomplete="off" placeholder="How much is $25 an hour per year?" aria-describedby="hero-try"><button class="btn" type="submit">Find My Answer</button></div>
<p class="visually-hidden" aria-live="polite" data-search-status></p>
<div class="results" data-results></div>
<p class="ask-tryline" id="hero-try">Try: {tries}</p>
</form>
</div>
</section>
{ad_slot("home-below-hero")}
<section>
<div class="wrap">
<div class="section-head"><h2>Popular tools</h2><a href="/tools/">All tools</a></div>
<div class="tile-grid">{"".join(tool_tile(t) for t in popular)}</div>
</div>
</section>
<section>
<div class="wrap">
<div class="section-head"><h2>Browse by category</h2></div>
<div class="cat-grid">{"".join(category_link(c) for c in CATEGORIES)}</div>
</div>
</section>
<section class="feature-band">
<div class="wrap">
<div class="section-head"><h2>Try it now: {e(featured_calc["name"])}</h2><a href="/tools/{featured_calc['slug']}/">Open the full calculator</a></div>
{calculator(featured_calc)}
</div>
</section>
<section>
<div class="wrap">
<div class="section-head"><h2>Latest guides</h2><a href="/blog/">All guides</a></div>
<ul class="article-list">{"".join(article_card(a, CAT[a['category']]['name']) for a in latest)}</ul>
</div>
</section>
{ad_slot("home-mid")}
<section>
<div class="wrap">
<h2>Why {C.SITE_NAME}?</h2>
<div class="why-grid">
<div><h3>Simple</h3><p>Tools designed to answer practical questions quickly. Type your numbers, get the answer.</p></div>
<div><h3>Useful</h3><p>Calculators and guides built around real-life problems: paychecks, prices, budgets, and deadlines.</p></div>
<div><h3>Clear</h3><p>Straightforward explanations without unnecessary complexity. Every tool shows the formula it uses.</p></div>
</div>
</div>
</section>
<section>
<div class="wrap">
<h2>Popular questions</h2>
<ul class="question-list">{qs}</ul>
</div>
</section>
<section>
<div class="wrap">
<div class="newsletter">
<h2>Email updates are on the way</h2>
<p>We're working on a short, occasional email with new tools and guides. No spam, and it isn't live yet. In the meantime, bookmark this site or <a href="/contact/">tell us which tool you'd like next</a>.</p>
</div>
</div>
</section>
""" + footer('<script src="/assets/js/calc.js?v=' + C.ASSET_VERSION + '" defer></script>\n')
    write("/", html, "1.0")


def build_tool(t):
    path = f"/tools/{t['slug']}/"
    cat = CAT[t["cat"]]
    trail = [("Home", "/"), ("Tools", "/tools/"), (cat["name"], f"/{cat['slug']}/"), (t["name"], path)]
    app_cat = "FinanceApplication" if t["cat"] in ("money-pay", "personal-finance", "taxes", "small-business", "work-career") else "UtilitiesApplication"
    ld = [{
        "@context": "https://schema.org", "@type": "WebApplication", "name": t["name"], "url": C.SITE_URL + path,
        "description": t["desc"], "applicationCategory": app_cat, "operatingSystem": "Any",
        "browserRequirements": "Requires JavaScript", "isAccessibleForFree": True,
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
        "publisher": {"@type": "Organization", "name": C.SITE_NAME, "url": C.SITE_URL + "/"},
    }, breadcrumb_ld(trail)]
    rel_tools = link_list([(TOOL[s]["name"], f"/tools/{s}/", TOOL[s]["short"]) for s in t["related"]])
    rel_guides = link_list([(ART[s]["title"], f"/blog/{s}/", f"{ART[s]['minutes']} min read") for s in t["guides"]]) if t["guides"] else \
        f'<p class="muted">Guides for this tool are coming. Browse <a href="/blog/">all guides</a>.</p>'
    cats_html = ", ".join(f'<a href="/{c}/">{e(CAT[c]["name"])}</a>' for c in [t["cat"]] + t.get("also", []))
    scripts = tool_scripts([t])
    tax_sources = ""
    if t.get("tax"):
        d = TAX[str(C.TAX_DEFAULT_YEAR)]
        tax_sources = '<div class="content-block prose"><h2>Sources</h2><ul class="sources">' + "".join(
            f'<li><a href="{e(s["url"])}" rel="noopener">{e(s["title"])}</a></li>' for s in d["sources"]) + \
            f'</ul><p class="small muted">Tax data last reviewed {human_date(d["lastReviewed"])}.</p></div>'
    tool_sources = ""
    if t.get("sources"):
        tool_sources = '<div class="content-block prose"><h2>Sources</h2><ul class="sources">' + "".join(
            f'<li><a href="{e(u)}" rel="noopener">{e(ti)}</a></li>' for ti, u in t["sources"]) + "</ul></div>"
    partner = affiliate_box(**t["partner"]) if t.get("partner") else ""
    html = head(t["name"], t["desc"], path, ld) + header(f"/{t['cat']}/") + breadcrumbs(trail) + f"""
<div class="wrap">
<header class="page-head"><h1>{e(t["name"])}</h1><p class="lede">{e(t["short"])}</p></header>
{calculator(t)}
<div class="content-block prose"><h2>How this calculator works</h2>{t["how"]}</div>
<div class="content-block prose"><h2>Example</h2>{t["example"]}</div>
{tax_sources}
{tool_sources}
{partner}
</div>
{ad_slot("tool-below-content")}
<div class="wrap">
<div class="related">
<div><h2>Related tools</h2>{rel_tools}</div>
<div><h2>Related guides</h2>{rel_guides}</div>
</div>
<p class="small muted" style="margin-top:24px">Category: {cats_html}</p>
{disclaimer(t["disclaimer"])}
</div>
""" + footer(scripts)
    write(path, html, "0.9")
    SEARCH.append(dict(t=t["name"], u=path, d=t["short"], k=t["keywords"], type="tool", w=0.5 if t.get("popular") else 0))


def build_tools_index():
    path = "/tools/"
    desc = "Every Get Solve Spring calculator in one place: pay, overtime, budgets, savings, debt, pricing, percentages, dates, time, and unit conversions."
    trail = [("Home", "/"), ("Tools", path)]
    groups = ""
    for c in CATEGORIES:
        ts = tools_in(c["slug"])
        if not ts:
            continue
        groups += (f'<div class="dir-group"><h2 id="{c["slug"]}"><span class="cat-icon">{ICONS[c["slug"]]}</span>'
                   f'<a href="/{c["slug"]}/" style="color:inherit;text-decoration:none">{e(c["name"])}</a></h2>'
                   f'<ul class="dir-list">{"".join(tool_row(t) for t in ts)}</ul></div>')
    html = head("All Tools and Calculators", desc, path, [webpage_ld("All tools", desc, path), breadcrumb_ld(trail)]) + header(path) + breadcrumbs(trail) + f"""
<div class="wrap">
<header class="page-head"><h1>All tools</h1><p class="lede">{len(TOOLS)} free calculators and converters, grouped by what you're trying to figure out. Some tools appear in more than one group.</p></header>
{groups}
<p class="muted">More tools are on the way. <a href="/contact/">Tell us what you'd like to see next</a>.</p>
</div>
""" + footer()
    write(path, html, "0.9")


def build_category(c):
    path = f"/{c['slug']}/"
    trail = [("Home", "/"), (c["name"], path)]
    ts = tools_in(c["slug"])
    arts = articles_in(c["slug"])
    desc = f"{c['name']} tools and guides from {C.SITE_NAME}. {c['intro']}"[:300]
    tools_html = f'<ul class="dir-list">{"".join(tool_row(t) for t in ts)}</ul>' if ts else \
        '<p class="planned-note">The first tools in this section are being built now. Here\'s what\'s planned.</p>'
    feat = TOOL.get(FEATURED.get(c["slug"], ""))
    featured_html = ""
    if feat:
        featured_html = (f'<section class="feature-band category-try" aria-labelledby="try-h"><div class="section-head">'
                         f'<h2 id="try-h">Try it here: {e(feat["name"])}</h2><a href="/tools/{feat["slug"]}/">Open the full page</a></div>'
                         f'{calculator(feat)}</section>')
    resources_html = ""
    if c["slug"] == "personal-finance":
        resources_html = ('<h3 style="margin-top:28px">Resources</h3>'
                          + link_list([("Credit & Credit Scores", "/credit/", "Check your credit reports, understand scores, and fix errors.")]))
    planned = PLANNED.get(c["slug"], [])
    planned_html = ""
    if planned:
        planned_html = (f'<h3 style="margin-top:28px">Coming next</h3><ul class="planned-list">'
                        + "".join(f"<li>{e(p)}</li>" for p in planned) + "</ul>")
    if arts:
        guides_html = f'<ul class="article-list">{"".join(article_card(a, c["name"]) for a in arts)}</ul>'
    else:
        others = [a for a in ARTICLES if any(s in [t["slug"] for t in ts] for s in a["tools"])][:3]
        guides_html = '<p class="muted">Guides for this section are in progress.</p>'
        if others:
            guides_html += f'<p>Related reading:</p><ul class="article-list">{"".join(article_card(a, CAT[a["category"]]["name"]) for a in others)}</ul>'
    html = head(f"{c['name']} Tools and Guides", desc, path, [webpage_ld(c["name"], desc, path), breadcrumb_ld(trail)]) + header(path) + breadcrumbs(trail) + f"""
<div class="wrap">
<header class="page-head"><h1>{e(c["name"])}</h1><p class="lede">{e(c["intro"])}</p></header>
{featured_html}
<section style="padding-top:0"><h2>All {e(c["name"])} tools</h2>{tools_html}{resources_html}{planned_html}</section>
<section><h2>Guides</h2>{guides_html}</section>
</div>
""" + footer(tool_scripts([feat]) if feat else "")
    write(path, html, "0.8")
    SEARCH.append(dict(t=c["name"], u=path, d=c["blurb"], k="category " + c["name"].lower(), type="page", w=0))


TOOL_CALLOUT = re.compile(r"^\[\[tool:([a-z0-9-]+)\|(.+?)\]\]$", re.M)


def build_article(a):
    path = f"/blog/{a['slug']}/"
    cat = CAT[a["category"]]
    trail = [("Home", "/"), ("Blog", "/blog/"), (cat["name"], f"/{cat['slug']}/"), (a["title"], path)]

    def callout(m):
        t = TOOL[m.group(1)]
        return (f'<div class="tool-callout"><p>{e(m.group(2))}</p>'
                f'<a class="btn" href="/tools/{t["slug"]}/">Open the {e(t["name"])}</a></div>')
    body_md = TOOL_CALLOUT.sub(callout, a["body_md"])
    body = markdown.markdown(body_md, extensions=["tables", "sane_lists"])
    # Wrap tables for horizontal scrolling on phones; right-align numeric columns
    body = re.sub(r"<table>", '<div class="table-scroll"><table>', body).replace("</table>", "</table></div>")
    body = body.replace('<th style="text-align: right;">', '<th class="num">').replace('<td style="text-align: right;">', '<td class="num">')
    # Insert an in-article ad slot after the second H2 (hidden unless enabled)
    parts = body.split("<h2", 3)
    if len(parts) == 4:
        body = parts[0] + "<h2" + parts[1] + "<h2" + parts[2] + ad_slot("article-inline").replace(" wrap", "") + "<h2" + parts[3]
    answer = markdown.markdown(a["answer"])
    sources = ""
    if a["sources"]:
        sources = '<h2>Sources</h2><ul class="sources">' + "".join(
            f'<li><a href="{e(u)}" rel="noopener">{e(t)}</a></li>' for t, u in a["sources"]) + "</ul>"
    rel_tools = link_list([(TOOL[s]["name"], f"/tools/{s}/", TOOL[s]["short"]) for s in a["tools"]])
    rel_arts = link_list([(ART[s]["title"], f"/blog/{s}/", f"{ART[s]['minutes']} min read") for s in a["related"]])
    updated = f'<span>Updated {a["updated_human"]}</span>' if a["updated"] != a["published"] else ""
    ld = [{
        "@context": "https://schema.org", "@type": "Article", "headline": a["title"], "description": a["description"],
        "datePublished": a["published"], "dateModified": a["updated"], "mainEntityOfPage": C.SITE_URL + path,
        "image": C.SITE_URL + "/assets/images/og-image.png",
        "author": {"@type": "Organization", "name": C.SITE_NAME, "url": C.SITE_URL + "/"},
        "publisher": {"@type": "Organization", "name": C.SITE_NAME, "logo": {"@type": "ImageObject", "url": C.SITE_URL + "/assets/icons/icon-512.png"}},
    }, breadcrumb_ld(trail)]
    html = head(a["title"], a["description"], path, ld, og_type="article") + header("/blog/") + breadcrumbs(trail) + f"""
<article class="wrap">
<header class="article-head">
<h1>{e(a["title"])}</h1>
<p class="article-meta"><a href="/{cat['slug']}/">{e(cat["name"])}</a><span>{a["minutes"]} min read</span><span>Published {a["published_human"]}</span>{updated}</p>
</header>
<div class="direct-answer"><p class="da-label">The short answer</p>{answer}</div>
<div class="article-body">
{body}
{sources}
</div>
<div class="related">
<div><h2>Tools for this</h2>{rel_tools}</div>
<div><h2>Related guides</h2>{rel_arts}</div>
</div>
<p class="small muted" style="margin-top:24px">Filed under <a href="/{cat['slug']}/">{e(cat["name"])}</a>. <a href="/blog/">See all guides</a>.</p>
{disclaimer(a.get("disclaimer", ""))}
</article>
{ad_slot("article-bottom")}
""" + footer()
    write(path, html, "0.8")
    SEARCH.append(dict(t=a["title"], u=path, d=a["description"], k=" ".join(a["tools"]).replace("-", " ") + " " + cat["name"].lower(), type="guide", w=0))


def build_credit():
    path = "/credit/"
    title = "Credit & Credit Scores"
    desc = "Understand your credit report and credit scores, how to check your reports for free, how to fix errors, and how credit fits with your debt and budget."
    cat = CAT["personal-finance"]
    trail = [("Home", "/"), (cat["name"], "/personal-finance/"), (title, path)]
    partner = affiliate_box("credit-page", "Check your credit",
        "Understanding your credit can help you make more informed financial decisions. If you want to review your credit information and monitoring options, explore our recommended credit resource.",
        "Check Your Credit & Monitoring Options")
    related = link_list([(TOOL[s]["name"], f"/tools/{s}/", TOOL[s]["short"]) for s in ["debt-to-income", "debt-payoff", "budget", "savings-goal"]])
    html = head(title, desc, path, [webpage_ld(title, desc, path), breadcrumb_ld(trail)]) + header("/personal-finance/") + breadcrumbs(trail) + f"""
<div class="wrap">
<header class="page-head"><h1>{title}</h1><p class="lede">What's in your credit report, how to check it, and what affects your scores.</p></header>
<div class="prose">
<h2>Credit report vs. credit score</h2>
<p>Your <strong>credit report</strong> is a record of your credit accounts and how you've paid them: credit cards, loans, balances, payment history, and certain public records. Three nationwide credit bureaus keep reports: Equifax, Experian, and TransUnion.</p>
<p>A <strong>credit score</strong> is a number calculated from the information in a credit report. There isn't just one. Different scoring models and different bureaus' data can produce different scores, so the number a lender sees may not match the one you see elsewhere.</p>
<p>The reports from each bureau can also differ, because each one may get information from different sources.</p>

<h2>How to check your credit reports</h2>
<p>You can check your credit report from each of the three bureaus <strong>for free, once a week</strong>, at <a href="https://www.annualcreditreport.com/" rel="noopener">AnnualCreditReport.com</a>. According to the Federal Trade Commission, it's the only website authorized to fill orders for the free credit reports you're entitled to by law. Watch for look-alike sites with misspelled addresses.</p>
<p>Some people also use a credit-monitoring service, which can show scores and send alerts when something changes on your report. These are usually paid subscriptions. Compare what's included, the price, and how to cancel before you sign up.</p>
</div>
{partner}
<div class="prose content-block">
<h2>What generally affects your credit scores</h2>
<p>Scoring models differ, but most look at factors like these:</p>
<ul>
<li><strong>Payment history:</strong> whether you pay on time</li>
<li><strong>Amounts owed:</strong> how much of your available credit you're using</li>
<li><strong>Length of credit history:</strong> how long your accounts have been open</li>
<li><strong>New credit:</strong> recent applications and newly opened accounts</li>
<li><strong>Credit mix:</strong> the types of credit you have</li>
</ul>
<p>Paying every bill on time and keeping card balances low relative to your limits are the habits most people can act on right away.</p>

<h2>If you find an error</h2>
<p>Under the Fair Credit Reporting Act, credit bureaus must let you dispute mistakes. Contact both the credit bureau and the business that supplied the wrong information, explain what's wrong, and include copies of documents that support your dispute. Keep records of everything you send.</p>

<h2>How credit connects to your other numbers</h2>
<p>When you apply for a loan, lenders usually look at your credit together with your <a href="/tools/debt-to-income/">debt-to-income ratio</a>. Paying down balances can help both. The <a href="/tools/debt-payoff/">Debt Payoff Calculator</a> shows how long that takes and how much interest an extra payment saves.</p>

<h2>Sources</h2>
<ul class="sources">
<li><a href="https://consumer.ftc.gov/articles/free-credit-reports" rel="noopener">Federal Trade Commission: Free Credit Reports</a></li>
<li><a href="https://www.consumerfinance.gov/ask-cfpb/what-is-a-debt-to-income-ratio-en-1791/" rel="noopener">Consumer Financial Protection Bureau: What is a debt-to-income ratio?</a></li>
</ul>
</div>
<div class="related"><div><h2>Related tools</h2>{related}</div></div>
{disclaimer("info")}
</div>
""" + footer()
    write(path, html, "0.8")
    SEARCH.append(dict(t=title, u=path, d="Check your credit reports, understand credit scores, and fix errors.",
                       k="credit score report check credit monitoring bureau equifax experian transunion dispute fico", type="tool", w=0.3))


def build_blog_index():
    path = "/blog/"
    desc = "Guides & Answers: plain-English explanations with worked examples for pay, budgets, small business pricing, percentages, and more."
    trail = [("Home", "/"), ("Blog", path)]
    feat = next((a for a in ARTICLES if a["featured"]), ARTICLES[0])
    rest = [a for a in ARTICLES if a is not feat]
    used_cats = [c for c in CATEGORIES if articles_in(c["slug"])]
    buttons = '<button type="button" data-filter="all" aria-pressed="true">All</button>' + "".join(
        f'<button type="button" data-filter="{c["slug"]}" aria-pressed="false">{e(c["name"])}</button>' for c in used_cats)
    html = head("Guides & Answers", desc, path, [webpage_ld("Guides & Answers", desc, path), breadcrumb_ld(trail)]) + header(path) + breadcrumbs(trail) + f"""
<div class="wrap">
<header class="page-head"><h1>Guides &amp; Answers</h1><p class="lede">Direct answers to common questions, with the math shown and a tool to run your own numbers.</p></header>
<a class="featured-article" href="/blog/{feat['slug']}/">
<span class="card-cat">Featured guide, {e(CAT[feat['category']]['name'])}</span>
<h2>{e(feat["title"])}</h2>
<p>{e(feat["description"])}</p>
<span class="card-meta"><span>{feat['minutes']} min read</span> <span>{feat['published_human']}</span></span>
</a>
<h2>Latest guides</h2>
<div class="blog-tools">
<div><label for="blog-search">Search guides</label><input id="blog-search" type="search" placeholder="Try “overtime” or “margin”" autocomplete="off"></div>
<p class="muted" id="blog-count" aria-live="polite" style="margin:0 0 10px"></p>
</div>
<div class="filter-bar" role="group" aria-label="Filter by category">{buttons}</div>
<ul class="article-list" data-blog-list>{"".join(article_card(a, CAT[a['category']]['name']) for a in rest)}</ul>
</div>
""" + footer()
    write(path, html, "0.8")


def build_search():
    path = "/search/"
    desc = "Search Get Solve Spring tools and guides."
    html = head("Search", desc, path, [webpage_ld("Search", desc, path)], extra='<meta name="robots" content="noindex, follow">\n') + header() + f"""
<div class="wrap search-page">
<header class="page-head"><h1>Search</h1></header>
<form class="ask" action="/search/" method="get" role="search" aria-label="Search page" data-live-search data-search-page>
<label for="search-q">What are you trying to figure out?</label>
<div class="ask-row"><input id="search-q" name="q" type="search" autocomplete="off" placeholder="Try “$25 an hour” or “profit”"><button class="btn" type="submit">Find My Answer</button></div>
<p class="visually-hidden" aria-live="polite" data-search-status></p>
<div class="results" data-results></div>
</form>
<p class="muted" style="margin-top:24px">Or browse <a href="/tools/">all tools</a> and <a href="/blog/">all guides</a>.</p>
</div>
""" + footer()
    write(path, html)
    PAGES_OUT.pop()  # don't list search results in the sitemap


def build_static_pages():
    for slug, p in PAGES.items():
        path = f"/{slug}/"
        trail = [("Home", "/"), (p["title"], path)]
        html = head(p["title"], p["description"], path, [webpage_ld(p["title"], p["description"], path), breadcrumb_ld(trail)]) + header() + breadcrumbs(trail) + f"""
<div class="wrap">
<header class="page-head"><h1>{e(p["title"])}</h1><p class="lede">{e(p["lede"])}</p></header>
<div class="prose">{p["body"]}</div>
</div>
""" + footer()
        write(path, html, "0.4")
        SEARCH.append(dict(t=p["title"], u=path, d=p["description"], k=slug, type="page", w=0))


def build_contact():
    path = "/contact/"
    desc = "Contact Get Solve Spring with questions, corrections, or ideas for new tools."
    trail = [("Home", "/"), ("Contact", path)]
    html = head("Contact", desc, path, [webpage_ld("Contact", desc, path), breadcrumb_ld(trail)]) + header() + breadcrumbs(trail) + f"""
<div class="wrap">
<header class="page-head"><h1>Contact us</h1><p class="lede">Questions, corrections, and tool ideas are all welcome.</p></header>
<div class="prose">
<p>Email <a href="mailto:{C.CONTACT_EMAIL}">{C.CONTACT_EMAIL}</a> or use the form below. We read every message but can't give individual financial, tax, or legal advice.</p>
<form id="contact-form" class="form-stack" novalidate data-email="{e(C.CONTACT_EMAIL)}" data-endpoint="{e(C.FORM_ENDPOINT)}" action="{e(C.FORM_ENDPOINT) or 'mailto:' + e(C.CONTACT_EMAIL)}" method="post">
<div class="field"><label for="c-name">Name</label><input id="c-name" name="name" type="text" autocomplete="name" required></div>
<div class="field"><label for="c-email">Email</label><input id="c-email" name="email" type="email" autocomplete="email" required></div>
<div class="field"><label for="c-subject">Subject</label><input id="c-subject" name="subject" type="text" required></div>
<div class="field"><label for="c-message">Message</label><textarea id="c-message" name="message" required></textarea></div>
<div class="hp-field" aria-hidden="true"><label for="c-website">Leave this field empty</label><input id="c-website" name="website" type="text" tabindex="-1" autocomplete="off"></div>
<div><button class="btn" type="submit">Send message</button></div>
<p id="form-status" class="form-status" role="status" aria-live="polite"></p>
</form>
</div>
</div>
""" + footer()
    write(path, html, "0.4")


def build_404():
    desc = "That page doesn't exist."
    html = head("Page not found", desc, "/404.html", extra='<meta name="robots" content="noindex">\n') + header() + f"""
<div class="wrap search-page">
<header class="page-head"><h1>That page isn't here</h1><p class="lede">The link may be old or mistyped. Search for what you need, or start from the tools list.</p></header>
<form class="ask" action="/search/" method="get" role="search" aria-label="Search after page not found" data-live-search>
<label for="nf-q">What are you trying to figure out?</label>
<div class="ask-row"><input id="nf-q" name="q" type="search" autocomplete="off"><button class="btn" type="submit">Find My Answer</button></div>
<div class="results" data-results></div>
</form>
<p style="margin-top:24px"><a href="/tools/">Browse all tools</a> or <a href="/">go to the homepage</a>.</p>
</div>
""" + footer()
    (OUT / "404.html").write_text(html, encoding="utf-8")


def build_meta_files():
    today = datetime.date.today().isoformat()
    urls = "".join(f"<url><loc>{C.SITE_URL}{p}</loc><lastmod>{today}</lastmod><priority>{pr}</priority></url>\n" for p, pr in PAGES_OUT)
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + "</urlset>\n")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nDisallow: /search/\n\nSitemap: {C.SITE_URL}/sitemap.xml\n")
    (OUT / "search-index.json").write_text(json.dumps(SEARCH, ensure_ascii=False, separators=(",", ":")))
    (OUT / "site.webmanifest").write_text(json.dumps({
        "name": C.SITE_NAME, "short_name": C.SITE_NAME, "start_url": "/", "display": "browser",
        "background_color": "#ffffff", "theme_color": "#10292d",
        "icons": [{"src": "/assets/icons/icon-192.png", "sizes": "192x192", "type": "image/png"},
                  {"src": "/assets/icons/icon-512.png", "sizes": "512x512", "type": "image/png"}]}, indent=1))
    # Tax data: one JS file for the browser, plus the raw JSON under /data/
    js = "/* Generated by build.py from src/data/tax/*.json. Do not edit here. */\nwindow.GSS_TAX = " + json.dumps(TAX, separators=(",", ":")) + ";\n"
    (OUT / "assets" / "js" / "tax-data.js").write_text(js)
    (OUT / "assets" / "js" / "bible-data.js").write_text(
        "/* Generated by build.py from src/data/bible-books.json. Do not edit here. */\nwindow.GSS_BIBLE = " + json.dumps(BIBLE, separators=(",", ":")) + ";\n")
    (OUT / "data" / "tax").mkdir(parents=True, exist_ok=True)
    for y, d in TAX.items():
        (OUT / "data" / "tax" / f"{y}.json").write_text(json.dumps(d, indent=2))
    # Custom domain file for GitHub Pages
    (OUT / "CNAME").write_text(C.SITE_URL.split("://", 1)[1] + "\n")


def main():
    check_links()
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(ROOT / "static", OUT)
    build_home()
    build_tools_index()
    for t in TOOLS:
        build_tool(t)
    for c in CATEGORIES:
        build_category(c)
    build_credit()
    build_blog_index()
    for a in ARTICLES:
        build_article(a)
    build_static_pages()
    build_contact()
    build_search()
    build_404()
    build_meta_files()
    print(f"Built {len(PAGES_OUT)} pages, {len(TOOLS)} tools, {len(ARTICLES)} articles into {OUT}")


if __name__ == "__main__":
    main()
