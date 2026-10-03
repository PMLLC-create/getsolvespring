"""
Site settings. Change these, then run `python3 build.py`.
"""
import datetime

SITE_NAME = "Get Solve Spring"
SITE_URL = "https://getsolvespring.com"   # no trailing slash
TAGLINE = "Get unstuck. Get answers. Get moving."
TAGLINE_2 = "Simple tools. Clear answers."

# Contact page. Replace with your business inbox whenever you like.
CONTACT_EMAIL = "hello@getsolvespring.com"

# Optional: a form service endpoint so the contact form sends without opening
# an email app. Free options: Formspree (https://formspree.io) gives you a URL
# like "https://formspree.io/f/abcdwxyz". Leave "" to fall back to email.
FORM_ENDPOINT = ""

# Advertising. Leave ADSENSE_CLIENT empty until AdSense approves the site.
# When approved, paste your publisher ID, e.g. "ca-pub-1234567890123456".
ADSENSE_CLIENT = ""
# True shows dashed boxes where ads will go (useful for layout review only).
SHOW_AD_SLOTS = False

# The tax year selected by default in tax tools. Each year's data lives in
# src/data/tax/<year>.json. Add a new file and change this to switch years.
TAX_DEFAULT_YEAR = 2026

YEAR = datetime.date.today().year
# Bump to bust browser caches after CSS/JS changes.
ASSET_VERSION = datetime.date.today().strftime("%Y%m%d")

# ---------------------------------------------------------------------------
# Affiliate partners
# Each placement points to one of your MyFreeScoreNow referral links.
# To change which offer appears where, edit the code at the end of the URL.
# Set AFFILIATE_ENABLED = False to hide every affiliate box site-wide.
# ---------------------------------------------------------------------------
AFFILIATE_ENABLED = True
AFFILIATE_PARTNER = "MyFreeScoreNow"
AFFILIATE_LINKS = {
    "credit-page": "https://app.myfreescorenow.com/enroll/B01A1433",     # B01
    "debt-payoff": "https://app.myfreescorenow.com/enroll/B02A1433",     # B02, lowest price
    "debt-to-income": "https://app.myfreescorenow.com/enroll/B02A1433",  # B02, lowest price
}
# Your MyFreeScoreNow plan links (price / trial / commission, as of Oct 3, 2026):
#   B01  $39.90, no trial       $20.80/mo commission
#   B02  $29.90, no trial       $13.80/mo commission
#   B03  $47.00, no trial       $25.80/mo commission
#   B04  $39.90, 7-day trial    $19.30/mo commission
#   C01  $39.95, 15-day trial   $17.90/mo commission
# Swap the code at the end of any URL above to change which plan a page uses.
AFFILIATE_PAID_NOTE = "Credit monitoring is a paid subscription service. Review the current price, features, billing, and cancellation terms before enrolling."
AFFILIATE_DISCLOSURE = "Disclosure: Get Solve Spring may earn a commission if you sign up through this link."
