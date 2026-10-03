#!/usr/bin/env python3
"""
Regenerate logo, favicon, app icons, and the social preview image into
static/assets/. Only needed if you change the logo. Requires Playwright:
    pip install playwright && playwright install chromium
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from components import mark  # noqa: E402
from PIL import Image  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

ICONS = ROOT / "static" / "assets" / "icons"
IMAGES = ROOT / "static" / "assets" / "images"
FONTS = (ROOT / "static" / "assets" / "fonts").as_uri()
ICONS.mkdir(parents=True, exist_ok=True)
IMAGES.mkdir(parents=True, exist_ok=True)


def svg(bg, fg):
    return mark(bg, fg).replace("<svg ", '<svg xmlns="http://www.w3.org/2000/svg" ', 1)


# SVG files
(ICONS / "favicon.svg").write_text(svg("#10292d", "#ffd84d"))
(IMAGES / "mark.svg").write_text(svg("#10292d", "#ffd84d"))
(IMAGES / "mark-mono-black.svg").write_text(svg("#000000", "#ffffff"))
(IMAGES / "mark-mono-white.svg").write_text(svg("#ffffff", "#000000"))

FONT_CSS = f"""@font-face{{font-family:B;font-weight:800;src:url({FONTS}/bricolage-grotesque-latin-800-normal.woff2)}}
@font-face{{font-family:A;font-weight:400;src:url({FONTS}/hanken-grotesk-latin-400-normal.woff2)}}"""


def wordmark_svg(color, mark_bg, mark_fg):
    # Horizontal logo: mark + name. Text is live SVG text in Bricolage Grotesque
    # with system fallbacks, so it stays editable.
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 420 64" width="420" height="64">
<g transform="translate(4 8)">{mark(mark_bg, mark_fg).replace('<svg viewBox="0 0 48 48" aria-hidden="true" focusable="false">', '<svg width="48" height="48" viewBox="0 0 48 48">')}</g>
<text x="66" y="44" font-family="'Bricolage Grotesque','Avenir Next','Segoe UI',Arial,sans-serif" font-weight="800" font-size="34" letter-spacing="-0.6" fill="{color}">Get Solve Spring</text>
</svg>"""


(IMAGES / "logo.svg").write_text(wordmark_svg("#10292d", "#10292d", "#ffd84d"))
(IMAGES / "logo-reverse.svg").write_text(wordmark_svg("#ffffff", "#ffd84d", "#10292d"))
(IMAGES / "logo-mono.svg").write_text(wordmark_svg("#000000", "#000000", "#ffffff"))

OG = f"""<html><head><style>{FONT_CSS}
body{{margin:0;width:1200px;height:630px;background:#10292d;color:#fff;font-family:A,sans-serif;display:flex;flex-direction:column;justify-content:center;padding:0 90px;box-sizing:border-box}}
.b{{display:flex;align-items:center;gap:22px;font:800 46px B,sans-serif;color:#ffd84d;margin-bottom:46px}}
.b svg{{width:84px;height:84px}}
h1{{font:800 92px/1 B,sans-serif;letter-spacing:-2.5px;margin:0 0 30px;max-width:900px}}
p{{font-size:34px;color:#c9dbd7;margin:0}}</style></head><body>
<div class="b">{mark("#ffd84d", "#10292d")}Get Solve Spring</div>
<h1>Get unstuck. Get answers. Get moving.</h1>
<p>Simple tools. Clear answers.</p></body></html>"""

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1200, "height": 630})
    pg.set_content(OG)
    pg.wait_for_timeout(300)
    pg.screenshot(path=str(IMAGES / "og-image.png"))
    for size, name in [(512, "icon-512.png"), (192, "icon-192.png"), (180, "apple-touch-icon.png"), (64, "icon-64.png")]:
        pg = b.new_page(viewport={"width": size, "height": size})
        # apple-touch-icon gets a full-bleed square (iOS rounds corners itself)
        inner = mark("#10292d", "#ffd84d")
        if name == "apple-touch-icon.png":
            inner = inner.replace('rx="11"', 'rx="0"')
        pg.set_content(f"<html><body style='margin:0;background:transparent'><div style='width:{size}px;height:{size}px'>{inner}</div></body></html>")
        pg.screenshot(path=str(ICONS / name), omit_background=True)
    b.close()

img = Image.open(ICONS / "icon-64.png")
img.save(ROOT / "static" / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
print("images written")
