"""
Categories, homepage questions, and the text of the trust/legal pages.
"""
import config as C

CATEGORIES = [
    dict(slug="money-pay", name="Money & Pay", blurb="Hourly, salary, paycheck, overtime, and raise math.",
         intro="Turn hourly rates into salaries, estimate your paycheck, and see what overtime or a raise really adds up to."),
    dict(slug="work-career", name="Work & Career", blurb="Hours, overtime, raises, and comparing jobs.",
         intro="Practical math for work: hours on a timesheet, overtime, raises, and how two job offers really compare."),
    dict(slug="small-business", name="Small Business", blurb="Margins, markups, pricing, and break-even.",
         intro="Price with confidence. Work out margins and markups, set prices, and find how many sales cover your costs."),
    dict(slug="everyday-math", name="Everyday Math", blurb="Percentages, dates, time, tips, and unit conversions.",
         intro="Quick answers for everyday numbers: percentages, tips, dates, time worked, ages, and unit conversions."),
    dict(slug="personal-finance", name="Personal Finance", blurb="Budgets, savings goals, debt payoff, and interest.",
         intro="Plan a budget, set a savings target, see how long debt will take to pay off, and how interest adds up."),
    dict(slug="taxes", name="Taxes", blurb="Paycheck tax estimates using current tax-year data.",
         intro="Simple estimates based on published tax-year figures. These tools are for planning, not filing, and aren't official tax advice."),
    dict(slug="mindset", name="Mindset", blurb="Practical tools for goals, habits, and money routines.",
         intro="Practical help for setting goals, building better money habits, and sticking with them. No hype, just tools that make the next step clearer."),
    dict(slug="faith-scripture", name="Faith & Scripture", blurb="Scripture study and reading tools, kept separate from money tools.",
         intro="Tools for reading and studying Scripture, kept separate from our financial and math tools. Where traditions differ, we say so rather than picking a side."),
]
CAT = {c["slug"]: c for c in CATEGORIES}

# Homepage "Popular questions": (question, href, target label)
POPULAR_QUESTIONS = [
    ("How much is $25 an hour per year?", "/blog/how-much-is-25-an-hour/", "Guide"),
    ("How much is $30 an hour per year?", "/blog/how-much-is-30-an-hour/", "Guide"),
    ("How do I calculate overtime?", "/blog/how-to-calculate-overtime-pay/", "Guide and Overtime Calculator"),
    ("How do I calculate profit margin?", "/tools/profit-margin/", "Profit Margin Calculator"),
    ("How much should I save each month?", "/tools/savings-goal/", "Savings Goal Calculator"),
    ("How do I calculate a percentage?", "/tools/percentage/", "Percentage Calculator"),
    ("What is gross pay?", "/blog/what-is-gross-pay/", "Guide"),
    ("What is net pay?", "/blog/what-is-net-pay/", "Guide and Take-Home Pay Estimator"),
    ("How do I compare two job offers?", "/blog/how-to-compare-two-job-offers/", "Guide"),
    ("What is the difference between markup and margin?", "/blog/markup-vs-profit-margin/", "Guide"),
]

HERO_EXAMPLES = ["$25 an hour", "$60,000 a year", "20% of 150", "overtime", "profit margin", "paycheck"]

EFFECTIVE = "October 3, 2026"

PAGES = {}

PAGES["about"] = dict(
    title="About Get Solve Spring",
    description="Get Solve Spring is an American-based online resource with simple tools, calculators, and guides for everyday questions.",
    lede="Simple tools. Clear answers.",
    body=f"""
<p>Get Solve Spring is an American-based online resource providing simple tools, calculators, guides, and practical information to help people solve everyday questions.</p>
<p>The idea is simple: people shouldn't have to search through ten pages just to answer a simple question. If you want to know what $25 an hour is per year, how much overtime you'll make this week, or what price gives you a 40% margin, you should be able to get the answer in seconds and understand how it was worked out.</p>
<h2>What you'll find here</h2>
<ul>
<li><strong>Calculators</strong> for pay, budgets, savings, debt, pricing, and everyday math</li>
<li><strong>Converters</strong> for units, dates, and time</li>
<li><strong>Straightforward explanations</strong> under every tool, so you can see the formula and check the math yourself</li>
<li><strong>Guides</strong> that answer common questions directly, with worked examples</li>
</ul>
<h2>How we work</h2>
<ul>
<li><strong>The tools come first.</strong> Pages are built so the calculator is easy to use on any device. Ads, if we add them, won't sit in the way of a calculator.</li>
<li><strong>We show our work.</strong> Every calculator explains its formula and assumptions.</li>
<li><strong>We use authoritative sources for rules that change,</strong> such as IRS and Social Security figures, and we note the tax year.</li>
<li><strong>We keep it honest.</strong> No fake reviews, no invented statistics, no pressure tactics.</li>
</ul>
<p>Read our <a href="/methodology/">methodology</a> for how calculations and data are handled, and the <a href="/disclaimer/">disclaimer</a> for what these tools can and can't do.</p>
<h2>Get in touch</h2>
<p>Found an error, have a question, or want a tool we don't have yet? <a href="/contact/">Contact us</a>.</p>
""")

PAGES["privacy"] = dict(
    title="Privacy Policy",
    description="How Get Solve Spring handles information when you use our calculators, guides, and contact form.",
    lede=f"Effective {EFFECTIVE}",
    body=f"""
<p>This policy explains what information Get Solve Spring ("we," "us") handles when you use getsolvespring.com.</p>
<h2>Calculators run in your browser</h2>
<p>The numbers you type into our calculators are processed in your own web browser. We don't send them to our servers or store them. If you share a calculator link that includes numbers in the web address, anyone with that link can see those numbers.</p>
<h2>Information you send us</h2>
<p>If you use the contact form or email us, we receive the name, email address, and message you provide. We use it only to respond and to improve the site. The contact form may be processed by a third-party form service on our behalf, which handles the message under its own privacy policy.</p>
<h2>Information collected automatically</h2>
<p>Like most websites, our hosting provider may automatically log technical information such as IP address, browser type, pages requested, and the date and time of a visit, for security and to keep the site running. We do not currently use analytics or advertising cookies on our own pages.</p>
<h2>Partner links</h2>
<p>Some pages include links to partner services, such as a credit-monitoring provider. These links are labeled, and the disclosure appears next to each one. If you click a partner link, you leave Get Solve Spring, and the partner may use cookies or similar technology to record that you came from our site so we can be credited for a referral. Anything you enter on the partner's site is handled under the partner's own privacy policy. We don't receive the personal or financial details you give them. See our <a href="/affiliate-disclosure/">affiliate disclosure</a>.</p>
<h2>Advertising</h2>
<p>We may show ads in the future, for example through Google AdSense. If we do, third-party vendors, including Google, may use cookies to serve ads based on your prior visits to this and other websites. We will update this policy before that happens, explain how to opt out of personalized advertising, and request consent where the law requires it.</p>
<h2>Children</h2>
<p>This site is for a general audience and is not directed at children under 13. We don't knowingly collect personal information from children.</p>
<h2>Your choices</h2>
<p>You can ask us to delete any message you've sent by contacting us. You can also block or delete cookies in your browser settings.</p>
<h2>Changes</h2>
<p>We'll post any changes on this page and update the effective date above.</p>
<h2>Contact</h2>
<p>Questions about privacy? Email <a href="mailto:{C.CONTACT_EMAIL}">{C.CONTACT_EMAIL}</a>.</p>
""")

PAGES["terms"] = dict(
    title="Terms of Use",
    description="The terms that apply when you use Get Solve Spring's calculators, tools, and guides.",
    lede=f"Effective {EFFECTIVE}",
    body=f"""
<p>By using getsolvespring.com, you agree to these terms. If you don't agree, please don't use the site.</p>
<h2>Educational use</h2>
<p>Our calculators, guides, and other content are provided for general information and education. They are not financial, tax, legal, or other professional advice. See our <a href="/disclaimer/">disclaimer</a>.</p>
<h2>No guarantee</h2>
<p>We work to keep our tools accurate and up to date, but we provide the site "as is" and "as available," without warranties of any kind, express or implied, including accuracy, completeness, or fitness for a particular purpose. Results depend on the information you enter and the assumptions described on each page.</p>
<h2>Limitation of liability</h2>
<p>To the fullest extent allowed by law, Get Solve Spring is not liable for any loss or damage arising from your use of, or reliance on, the site or its content. You are responsible for verifying important information with an authoritative source or a qualified professional before acting on it.</p>
<h2>Acceptable use</h2>
<p>Please don't attempt to disrupt the site, scrape it in a way that burdens it, or use it for anything unlawful.</p>
<h2>Content</h2>
<p>The text, design, and code of this site belong to Get Solve Spring unless otherwise noted. You're welcome to link to any page. Please don't republish substantial portions without permission.</p>
<h2>Links to other sites</h2>
<p>We link to official and third-party sources for reference. We don't control those sites and aren't responsible for their content.</p>
<h2>Changes</h2>
<p>We may update these terms. Changes take effect when posted here.</p>
<h2>Contact</h2>
<p>Email <a href="mailto:{C.CONTACT_EMAIL}">{C.CONTACT_EMAIL}</a>.</p>
""")

PAGES["disclaimer"] = dict(
    title="Disclaimer",
    description="Get Solve Spring calculators provide estimates for educational purposes and are not financial, tax, or legal advice.",
    lede="What our calculators and guides can and can't do.",
    body="""
<h2>Calculators provide estimates</h2>
<p>Every calculator on Get Solve Spring produces an estimate based on the numbers you enter and the assumptions explained on that page. Real-world results can differ because of rounding, timing, rules that apply to your situation, or details a simple calculator can't capture.</p>
<h2>Information is educational</h2>
<p>Our tools and guides are for general information and education. They don't consider your complete circumstances.</p>
<h2>Not financial advice</h2>
<p>Financial calculators, including budgeting, savings, interest, and debt tools, are not individualized financial advice. Interest rates, returns, and fees change. Consider consulting a qualified financial professional before making significant decisions.</p>
<h2>Not official tax advice</h2>
<p>Tax tools are estimates based on published tax-year figures. They are not official IRS calculations or advice, and Get Solve Spring is not affiliated with the IRS, the U.S. Department of Labor, the Social Security Administration, or any other government agency. For official guidance, use <a href="https://www.irs.gov/" rel="noopener">IRS.gov</a> or a qualified tax professional.</p>
<h2>Not legal advice</h2>
<p>Information about pay rules, such as overtime, describes general federal rules and examples. Employment law varies by state and situation. For questions about your rights, contact the appropriate government agency or an attorney.</p>
<h2>Verify important information</h2>
<p>Before relying on a result for an important decision, verify it with an authoritative source, your employer, your lender, or a qualified professional. Results may vary based on individual circumstances.</p>
<h2>Faith content</h2>
<p>Scripture text on this site is from the World English Bible (WEB), which is in the public domain. Faith & Scripture resources are offered for personal study. Where Christian traditions interpret a passage differently, we try to note that rather than present one view as settled.</p>
""")

PAGES["accessibility"] = dict(
    title="Accessibility",
    description="Get Solve Spring's commitment to an accessible website, what we've done, and how to report a barrier.",
    lede="Everyone should be able to use these tools.",
    body=f"""
<p>We aim for Get Solve Spring to be usable by as many people as possible, including people who use screen readers, keyboard navigation, magnification, or voice control. We design with the Web Content Accessibility Guidelines (WCAG) 2.2 Level AA in mind.</p>
<h2>What we've done</h2>
<ul>
<li>Every calculator input has a visible label, and errors are announced and explained in text</li>
<li>All features work with a keyboard, with a clearly visible focus outline</li>
<li>Results are announced to screen readers when they update</li>
<li>Text and controls meet contrast guidelines, and color is never the only signal</li>
<li>Pages use headings, landmarks, and a "skip to main content" link</li>
<li>Layouts adapt from small phones to large screens, and text can be enlarged</li>
<li>Animations are minimal and respect the "reduce motion" setting</li>
</ul>
<h2>Known limits</h2>
<p>We're a small site and test as we build. Some pages may still have issues we haven't found.</p>
<h2>Report a barrier</h2>
<p>If something doesn't work for you, please tell us which page and what happened. Email <a href="mailto:{C.CONTACT_EMAIL}">{C.CONTACT_EMAIL}</a> or use the <a href="/contact/">contact form</a>. We'll do our best to fix it and, in the meantime, help you get the answer you need.</p>
""")

PAGES["methodology"] = dict(
    title="Methodology",
    description="How Get Solve Spring builds calculators, chooses assumptions, updates tax-year data, and reviews information.",
    lede="How our numbers are worked out, and how we keep them current.",
    body="""
<h2>How calculator formulas work</h2>
<p>Each calculator uses standard, published formulas, and every tool page shows the formula under "How this calculator works" with a worked example. Calculations run in your browser using the numbers you enter. Results are rounded for display, usually to the cent for money and to two decimal places for percentages. Intermediate steps use full precision.</p>
<h2>How assumptions are chosen</h2>
<p>When a calculation needs an assumption, we use the most common case and show it on the page so you can change it. Examples:</p>
<ul>
<li>A full-time year is 40 hours a week for 52 weeks (2,080 hours)</li>
<li>Monthly pay is annual pay divided by 12, so it's an average</li>
<li>Biweekly pay assumes 26 paychecks a year; semimonthly assumes 24</li>
<li>Savings and debt tools assume steady rates and monthly payments</li>
<li>Overtime defaults to time and a half for hours over 40 in a workweek, following the federal Fair Labor Standards Act</li>
</ul>
<h2>Tax-year data</h2>
<p>Tax rules change every year. Our tax tools read from a single data file per tax year containing the standard deduction, federal income tax brackets, and Social Security and Medicare rates. Each tool shows which tax year it uses.</p>
<ul>
<li><strong>Current data:</strong> tax year 2026</li>
<li><strong>Sources:</strong> the IRS announcement of 2026 inflation adjustments, and the Social Security Administration's contribution and benefit base</li>
<li><strong>Updates:</strong> when the IRS publishes the next year's figures, typically in the fall, we add a new data file and review the tools that use it</li>
</ul>
<p>Our tax estimates are simplified. They don't include credits, itemized deductions, or every special rule. They are not official IRS calculations.</p>
<h2>How information is reviewed</h2>
<p>Before publishing, each calculator is tested against hand-worked examples, including edge cases like zero values and invalid entries. Guides are checked against their sources, and dates are shown on every article. When a source changes, we update the page and its "updated" date.</p>
<h2>Sources we prefer</h2>
<p>For rules and figures that change, we rely on primary sources such as the IRS, the U.S. Department of Labor, the Social Security Administration, the Bureau of Labor Statistics, the Census Bureau, and official state websites. We link to them where they're used. We don't invent statistics or citations.</p>
<h2>Estimates may differ from actual results</h2>
<p>Your real paycheck, loan balance, or investment return can differ from our estimate because of rounding, timing, fees, or rules specific to your situation. See the <a href="/disclaimer/">disclaimer</a>.</p>
<h2>Found an error?</h2>
<p>Please <a href="/contact/">let us know</a>. Corrections are welcome and taken seriously.</p>
""")

PAGES["affiliate-disclosure"] = dict(
    title="Affiliate Disclosure",
    description="How Get Solve Spring works with partner services, how we label partner links, and how we may earn a commission.",
    lede="How partner links work on this site.",
    body="""
<p>Get Solve Spring is free to use. To help keep it that way, some pages include links to partner services. If you sign up for a partner's product through one of these links, Get Solve Spring may earn a commission.</p>
<h2>How we label partner links</h2>
<ul>
<li>Partner links appear in a box marked <strong>Partner resource</strong>, with the partner's name shown.</li>
<li>A disclosure sits directly under every partner link, not only on this page.</li>
<li>Paid services are labeled as paid, next to the link.</li>
<li>Partner links are marked for search engines as sponsored.</li>
</ul>
<h2>Where partner links appear</h2>
<p>We only place a partner link where it relates to what you're already working on. For example, a credit-monitoring partner appears on our credit page and next to debt-related calculators. Partner links never appear inside a calculator or change how any calculation works.</p>
<h2>Current partners</h2>
<ul>
<li><strong>MyFreeScoreNow</strong>: credit reports, credit scores, and credit-monitoring services. Their plans may involve a paid subscription. Review the offer, price, and cancellation terms on their site before you enroll.</li>
</ul>
<h2>What we don't do</h2>
<ul>
<li>We don't claim a partner is the best option for everyone.</li>
<li>We don't call a paid service "free."</li>
<li>We don't let partnerships change our calculators, formulas, or explanations.</li>
</ul>
<p>Free alternatives exist, and we tell you about them. For example, you can get your credit reports from each nationwide credit bureau for free at <a href="https://www.annualcreditreport.com/" rel="noopener">AnnualCreditReport.com</a>.</p>
<p>Questions? <a href="/contact/">Contact us</a>.</p>
""")
