# Get Solve Spring — website

Get unstuck. Get answers. Get moving.

This folder contains everything for **getsolvespring.com**:

| Folder / file | What it is |
|---|---|
| `site/` | **The finished website.** Plain HTML, CSS, and JavaScript. This is what you upload. |
| `src/` | The content you edit: tools, articles, categories, pages, settings, tax data |
| `static/` | Files copied into the site as-is: CSS, JavaScript, fonts, logo, icons |
| `build.py` | Rebuilds `site/` from `src/` and `static/` |
| `scripts/make_images.py` | Regenerates the logo, favicon, and social image (only if the logo changes) |
| `.github/workflows/deploy.yml` | Optional: automatic deploy to GitHub Pages |

No database, no paid hosting, no framework. The `site/` folder works on any free static host.

---

## 1. Put the site online

You can deploy the ready-made `site/` folder without installing anything.

### Option A: Cloudflare Pages (recommended)

1. Create a free account at <https://dash.cloudflare.com>.
2. Go to **Workers & Pages → Create → Pages → Upload assets**.
3. Name the project `getsolvespring` and drag in the **contents** of the `site/` folder.
4. Click **Deploy**. You'll get a preview address like `getsolvespring.pages.dev`.

To update later, upload a new `site/` folder to the same project.

If you'd rather have Cloudflare rebuild automatically from GitHub, connect the repository instead of uploading, and use:

- **Build command:** `pip install markdown && python3 build.py`
- **Build output directory:** `site`

### Option B: GitHub Pages

1. Create a GitHub repository (for example `getsolvespring`) and upload this whole folder.
2. In the repository, go to **Settings → Pages** and set **Source** to **GitHub Actions**.
3. The included workflow builds and publishes the site every time you push to `main`.

---

## 2. Connect getsolvespring.com

### With Cloudflare Pages

1. In your Pages project, go to **Custom domains → Set up a custom domain** and enter `getsolvespring.com`.
2. If the domain's DNS is already on Cloudflare, it's added automatically. If not, Cloudflare shows the records to add at your registrar (usually a CNAME pointing to `getsolvespring.pages.dev`), or you can move the domain's nameservers to Cloudflare.
3. Add `www.getsolvespring.com` as well and set it to redirect to the main domain.

### With GitHub Pages

1. In **Settings → Pages → Custom domain**, enter `getsolvespring.com` and save. (The build already writes a `CNAME` file.)
2. At your domain registrar, add these DNS records:
   - Four **A** records for `@` pointing to `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`
   - A **CNAME** record for `www` pointing to `<your-github-username>.github.io`
3. After DNS updates (minutes to a few hours), check **Enforce HTTPS**.

GitHub's current instructions: <https://docs.github.com/pages/configuring-a-custom-domain-for-your-github-pages-site>

### After the domain works

- Submit `https://getsolvespring.com/sitemap.xml` in **Google Search Console** (<https://search.google.com/search-console>) and **Bing Webmaster Tools**.

---

## 3. Make changes

Install once: Python 3.8 or newer, then `pip install markdown`.

After any edit, run:

```
python3 build.py
```

To preview locally:

```
cd site
python3 -m http.server 8000
```

Then open <http://localhost:8000>.

### Site settings — `src/config.py`

- `CONTACT_EMAIL` — the address on the Contact page and legal pages (currently hello@getsolvespring.com)
- `FORM_ENDPOINT` — see "Contact form" below
- `ADSENSE_CLIENT`, `SHOW_AD_SLOTS` — see "Google AdSense" below
- `TAX_DEFAULT_YEAR` — the tax year tax tools use by default

### Contact form

Static sites can't send email on their own. Right now the form opens the visitor's email app with the message filled in. To have it send directly:

1. Create a free form at <https://formspree.io> (or a similar service) using your email.
2. Copy the form URL it gives you (like `https://formspree.io/f/abcdwxyz`).
3. Paste it into `FORM_ENDPOINT` in `src/config.py` and rebuild.

Spam protection is built in: a hidden "honeypot" field and a minimum time on page. Most form services add their own filtering too.

---

## 4. Add a new calculator

1. **Describe it** in `src/tools.py`. Copy an existing `dict(...)` block and change:
   - `slug` (becomes the URL: `/tools/<slug>/`), `name`, `short`, `desc`, `teaser`
   - `cat` (main category) and `also` (other categories it should appear in)
   - `keywords` (words people might search for)
   - `fields` — one `F(...)` per input. Kinds: `money`, `number`, `percent`, `integer`, `select`, `date`, `time`, `check`
   - `how` and `example` — the explanation and worked example (HTML)
   - `related` (other tool slugs) and `guides` (article slugs)
   - `disclaimer`: `"general"`, `"financial"`, `"tax"`, or `"none"`
2. **Write the math** in `static/assets/js/calc.js`. Add a function with the same slug:

   ```js
   C["my-new-tool"] = function (v) {
     // v.fieldName holds each input value (numbers already parsed)
     var result = v.a * v.b;
     return {
       primary: { label: "Your result", value: fmt.money2(result) },
       rows: [["Another figure", fmt.pct(12.5)]],
       note: "Formula: a × b."
     };
   };
   ```

   Return `{ error: "message" }` for impossible inputs.
3. If it's in `PLANNED` in `src/tools.py`, remove it from that list.
4. Run `python3 build.py`. The tool page, category listings, search, and sitemap update automatically.

---

## 5. Add a blog post

1. Create `src/articles/<slug>.md`. Copy an existing article as a starting point.
2. Fill in the header above the `---` line:

   ```
   title: How to Calculate Your Hourly Rate
   slug: how-to-calculate-hourly-rate
   description: One or two sentences for Google and social previews.
   category: work-career
   published: 2026-11-01
   updated: 2026-11-15          (optional)
   featured: true               (optional; shows at the top of the blog)
   tools: salary-to-hourly, hourly-to-salary
   related: what-is-gross-pay, how-to-compare-two-job-offers
   answer: The direct answer in one or two sentences. **Bold** works here.
   disclaimer: general          (general, financial, tax, or leave out)
   sources: Title of source|https://example.gov/page; Second source|https://...
   ---
   ```

3. Write the article in Markdown below the `---`. Tables, headings, and lists all work.
4. To insert a "try the tool" box, put this on its own line:

   ```
   [[tool:hourly-to-salary|Run your own numbers.]]
   ```

5. Run `python3 build.py`.

Remaining articles from the original plan: How to Calculate Your Hourly Rate; Salary vs Hourly Pay; How to Calculate Break-Even Point; How to Build an Emergency Fund; How to Calculate a Pay Raise; W-2 vs 1099; Revenue vs Profit; How to Price a Product for Profit; How to Create a Simple Monthly Budget; How to Calculate Your Debt-to-Income Ratio.

---

## 6. Update tax-year data

Tax figures live in one file per year: `src/data/tax/2026.json`.

When the IRS publishes the next year's numbers (usually in October or November):

1. Copy `2026.json` to `2027.json`.
2. Update `year`, `standardDeduction`, every `brackets` threshold, and `socialSecurityWageBase`, using:
   - IRS: search IRS.gov for "inflation adjustments for tax year 2027"
   - SSA: <https://www.ssa.gov/oact/cola/cbb.html> for the wage base
3. Update `sources` and `lastReviewed`.
4. In `src/config.py`, set `TAX_DEFAULT_YEAR = 2027` when you want it to become the default.
5. Rebuild. The year appears in the Tax year dropdown automatically, and both years stay available.

Each bracket is `[starting taxable income, rate]`. Only change numbers you've confirmed from an official source.

---

## 7. Affiliate links (MyFreeScoreNow)

Partner links are set in `src/config.py` under **Affiliate partners**:

- `AFFILIATE_LINKS` assigns one referral link to each placement: `credit-page` (/credit/), `debt-payoff`, and `debt-to-income`. The Credit page uses B01 ($39.90, no trial). The two debt tools use B02 ($29.90, no trial), the most affordable plan for people already working on debt. All five plans are listed underneath with price, trial, and commission; swap the code at the end of a URL to switch.
- `AFFILIATE_DISCLOSURE` is the sentence shown directly under every partner button.
- `AFFILIATE_ENABLED = False` hides every partner box at once.

To add a partner box to another tool, give that tool a `partner=dict(placement=..., heading=..., text=..., cta=...)` entry in `src/tools.py` and add the placement to `AFFILIATE_LINKS`. Keep them on pages where credit is already the topic.

## 8. Google AdSense

The layout already has reserved ad positions (below the homepage hero, mid-homepage, inside and after articles, below tool explanations). None sit inside or beside a calculator.

- To see where they are, set `SHOW_AD_SLOTS = True` and rebuild. Turn it back off before publishing.
- When AdSense approves the site, put your publisher ID in `ADSENSE_CLIENT`. Then either use AdSense Auto ads, or replace the placeholders in `src/components.py` → `ad_slot()` with your ad unit code.
- Before turning on ads, update the Advertising section of the Privacy Policy (`src/content.py`) and set up a cookie consent message as Google requires for some regions.

---

## Bible text

The Faith & Scripture tools use the **World English Bible (WEB)**, which is in the public domain. The text lives in `static/data/web/`, one file per book (66 files, 31,103 verses, checked against the published verse counts). Book order and chapter counts are in `src/data/bible-books.json`. Topic lists for the Scripture Topic Finder are in `static/assets/js/calc.js` under `TOPICS`; add a topic there and to the `topic` options in `src/tools.py`.

The WEB's publisher asks that the name "World English Bible" only be used for the unaltered text, so don't edit the verse files.

## Design notes

- **Colors:** ink `#10292d`, spring green `#0a7a62`, spark yellow `#ffd84d` (answer highlights), mist `#eef4f2`
- **Type:** Bricolage Grotesque (headings), Hanken Grotesk (text). Both are self-hosted under the SIL Open Font License; license files are in `static/assets/fonts/`.
- **Logo:** a compressed spring releasing into an upward arrow. Files in `static/assets/images/`: `logo.svg`, `logo-reverse.svg` (for dark backgrounds), `logo-mono.svg`, `mark.svg`, `mark-mono-black.svg`, `mark-mono-white.svg`. The wordmark SVGs use live text, so for print or a sign, open them in a design tool with Bricolage Grotesque installed and convert text to outlines.

## What was tested

- All 29 calculators against hand-worked examples, invalid input, reset, and links that prefill values
- Every internal link, unique titles and descriptions, valid structured data, one H1 per page
- Automated accessibility scan (axe-core, WCAG 2.1 AA rules) on representative pages
- Layout at 320, 375, 390, 430, 768, 1024, and 1440 pixels wide with no sideways scrolling
- Keyboard use of the mobile menu, search, and forms
