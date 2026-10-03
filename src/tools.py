"""
Tool registry for Get Solve Spring.

Each tool here becomes a page at /tools/<slug>/. The calculation itself lives
in static/assets/js/calc.js under the same slug.

To add a calculator:
  1. Add a TOOL(...) entry below (inputs, explanation, example, related links).
  2. Add GSS_CALCS["<slug>"] = function (v) {...} in calc.js.
  3. Run `python3 build.py`.
"""


def F(name, label, kind="number", default="", **o):
    """One input field.
    kind: money | number | percent | integer | select | date | time | check
    options: min, max, help, options=[(value, label)], modes="a,b",
             labels={mode: label}, adv=True (inside "More options"),
             optional=True (blank counts as 0), positive=True (> min), suffix
    """
    return dict(name=name, label=label, kind=kind, default=default, **o)


TOOLS = [
    dict(
        slug="hourly-to-salary",
        name="Hourly to Salary Calculator",
        short="Turn an hourly wage into yearly, monthly, biweekly, and weekly pay.",
        desc="Convert an hourly wage to annual salary, monthly, biweekly, and weekly pay. Includes overtime and unpaid weeks.",
        cat="money-pay", also=["work-career"], popular=True,
        teaser="$25/hr → $52,000/yr",
        keywords="hourly wage salary annual yearly convert per hour an hour pay rate 25 30 20 15 per year income",
        fields=[
            F("rate", "Hourly rate", "money", "25", min=0, positive=True),
            F("hours", "Hours per week", "number", "40", min=0, max=168, positive=True),
            F("weeks", "Paid weeks per year", "number", "52", min=1, max=53, help="Use 50 if you take 2 unpaid weeks off."),
            F("otHours", "Overtime hours per week", "number", "0", min=0, max=128, adv=True, optional=True),
            F("otMult", "Overtime multiplier", "select", "1.5", adv=True, options=[("1.5", "1.5× (time and a half)"), ("2", "2× (double time)")]),
            F("days", "Workdays per week", "number", "5", min=1, max=7, adv=True),
        ],
        how="""<p>Your yearly pay is your hourly rate times the hours you work in a week, times the number of weeks you're paid.</p>
<p class="formula">Annual pay = hourly rate × hours per week × paid weeks per year</p>
<p>Overtime hours, if you add them, are paid at the multiplier you choose and added to each week. Monthly pay is annual pay divided by 12, so it's an average: some months have more paydays than others. Biweekly pay is annual pay divided by 26 paychecks, and semimonthly is divided by 24.</p>""",
        example="""<p>At <strong>$25 an hour</strong>, 40 hours a week, 52 weeks a year:</p>
<div class="table-scroll"><table><thead><tr><th>Pay period</th><th class="num">Gross pay</th></tr></thead><tbody>
<tr><td>Weekly</td><td class="num">$1,000</td></tr><tr><td>Biweekly</td><td class="num">$2,000</td></tr>
<tr><td>Monthly (average)</td><td class="num">about $4,333</td></tr><tr><td>Annual</td><td class="num">$52,000</td></tr></tbody></table></div>
<p>A quick shortcut: at 40 hours a week, double your hourly rate and add three zeros. $25 × 2 = 50, so roughly $50,000 (the exact figure is $52,000).</p>""",
        related=["salary-to-hourly", "take-home-pay", "overtime", "pay-raise", "time-duration"],
        guides=["how-much-is-25-an-hour", "how-much-is-30-an-hour", "what-is-gross-pay"],
        disclaimer="general",
    ),
    dict(
        slug="salary-to-hourly",
        name="Salary to Hourly Calculator",
        short="Find the hourly rate behind a yearly salary.",
        desc="Convert an annual salary to an hourly rate, plus weekly, biweekly, and monthly pay. See your effective rate if you work extra hours.",
        cat="money-pay", also=["work-career"], popular=True,
        teaser="$60,000/yr → $28.85/hr",
        keywords="salary to hourly annual per hour rate yearly convert wage 50000 60000 70000 effective hourly job offer",
        fields=[
            F("salary", "Annual salary", "money", "60000", min=0, positive=True),
            F("hours", "Hours per week", "number", "40", min=0, max=168, positive=True),
            F("weeks", "Weeks per year", "number", "52", min=1, max=53),
            F("actualHours", "Hours you actually work per week", "number", "", min=0, max=168, adv=True, optional=True,
              help="Optional. Salaried jobs often run longer than 40 hours."),
        ],
        how="""<p>Divide the salary by the number of hours it pays for in a year.</p>
<p class="formula">Hourly rate = annual salary ÷ (hours per week × weeks per year)</p>
<p>A standard full-time year is 40 × 52 = 2,080 hours. If you regularly work more than your scheduled hours, add your real weekly hours under More options to see your effective hourly rate.</p>""",
        example="""<p>A <strong>$60,000</strong> salary at 40 hours a week for 52 weeks is $60,000 ÷ 2,080 = <strong>$28.85 an hour</strong>. If that job really takes 50 hours a week, the effective rate falls to $60,000 ÷ 2,600 = $23.08 an hour.</p>""",
        related=["hourly-to-salary", "take-home-pay", "pay-raise", "overtime"],
        guides=["how-to-compare-two-job-offers", "how-much-is-30-an-hour", "what-is-gross-pay"],
        disclaimer="general",
    ),
    dict(
        slug="take-home-pay",
        name="Take-Home Pay Estimator",
        short="Estimate your paycheck after federal income tax, Social Security, and Medicare.",
        desc="Estimate take-home pay per paycheck after federal income tax, Social Security, Medicare, pre-tax deductions, and your state tax rate.",
        cat="money-pay", also=["taxes", "personal-finance"], popular=True, tax=True,
        teaser="$52,000/yr → net per paycheck",
        keywords="take home pay paycheck net pay after tax salary calculator withholding federal income tax fica social security medicare biweekly how much will my paycheck be",
        fields=[
            F("taxYear", "Tax year", "select", "{TAX_DEFAULT}", options="{TAX_YEARS}"),
            F("status", "Filing status", "select", "single", options=[("single", "Single"), ("married_joint", "Married filing jointly"), ("head_household", "Head of household")]),
            F("gross", "Annual gross pay", "money", "52000", min=0),
            F("frequency", "Pay frequency", "select", "26", options=[("52", "Weekly"), ("26", "Every two weeks"), ("24", "Twice a month"), ("12", "Monthly")]),
            F("retirement", "Pre-tax retirement per year", "money", "0", min=0, adv=True, optional=True, help="401(k), 403(b), or similar. Lowers income tax but not Social Security or Medicare."),
            F("health", "Pre-tax health and other per year", "money", "0", min=0, adv=True, optional=True, help="Health premiums, HSA, FSA through payroll. Lowers income tax and FICA."),
            F("stateRate", "State and local income tax rate", "percent", "0", min=0, max=20, adv=True, optional=True, help="Your own estimate. Leave at 0 for states with no income tax."),
        ],
        how="""<p>This estimator starts with your gross pay and subtracts the main paycheck taxes:</p>
<ul>
<li><strong>Federal income tax</strong> — gross pay, minus pre-tax deductions and the standard deduction for your filing status, run through that year's federal brackets.</li>
<li><strong>Social Security</strong> — 6.2% of wages up to the yearly wage base.</li>
<li><strong>Medicare</strong> — 1.45% of all wages, plus an extra 0.9% that employers withhold on wages above $200,000.</li>
<li><strong>State and local tax</strong> — a flat rate you enter, applied after pre-tax deductions. State rules vary a lot, so this is a rough placeholder.</li>
</ul>
<p class="formula">Take-home = gross − pre-tax deductions − federal income tax − Social Security − Medicare − state tax</p>
<p>It does not include tax credits (such as the Child Tax Credit), itemized deductions, special deductions such as those for qualified tips or overtime, or after-tax payroll deductions. Your actual paycheck also depends on the W-4 you gave your employer. For withholding decisions, use the <a href="https://www.irs.gov/individuals/tax-withholding-estimator" rel="noopener">IRS Tax Withholding Estimator</a>.</p>""",
        example="""<p>A single filer earning <strong>$52,000</strong> in 2026, paid every two weeks, with no pre-tax deductions:</p>
<div class="table-scroll"><table><thead><tr><th>Item</th><th class="num">Per year</th></tr></thead><tbody>
<tr><td>Taxable income ($52,000 − $16,100 standard deduction)</td><td class="num">$35,900</td></tr>
<tr><td>Federal income tax (10% on the first $12,400, 12% on the rest)</td><td class="num">$4,060</td></tr>
<tr><td>Social Security (6.2%)</td><td class="num">$3,224</td></tr>
<tr><td>Medicare (1.45%)</td><td class="num">$754</td></tr>
<tr><td><strong>Take-home before state tax</strong></td><td class="num"><strong>$43,962</strong></td></tr></tbody></table></div>
<p>That's about $1,690.85 per biweekly paycheck before any state income tax.</p>""",
        related=["hourly-to-salary", "salary-to-hourly", "budget", "pay-raise"],
        guides=["what-is-net-pay", "what-is-gross-pay", "how-much-should-i-save-from-each-paycheck"],
        disclaimer="tax",
    ),
    dict(
        slug="overtime",
        name="Overtime Calculator",
        short="Work out overtime pay and your total for the week.",
        desc="Calculate overtime pay at time and a half or double time, and see your total weekly pay before taxes.",
        cat="money-pay", also=["work-career"], popular=True,
        teaser="5 OT hrs at $20 → $150 extra",
        keywords="overtime ot pay time and a half double time 1.5 extra hours over 40 weekly pay flsa",
        fields=[
            F("rate", "Regular hourly rate", "money", "20", min=0, positive=True),
            F("regHours", "Regular hours this week", "number", "40", min=0, max=168),
            F("otHours", "Overtime hours", "number", "5", min=0, max=128),
            F("otMult", "Overtime rate", "select", "1.5", options=[("1.5", "1.5× (time and a half)"), ("2", "2× (double time)")]),
            F("dtHours", "Double-time hours (in addition)", "number", "0", min=0, max=128, adv=True, optional=True, help="For jobs or states that pay double time on top of time and a half."),
        ],
        how="""<p>Overtime pay is your regular hourly rate times the overtime multiplier, times the overtime hours.</p>
<p class="formula">Overtime pay = hourly rate × 1.5 × overtime hours<br>Total pay = regular pay + overtime pay</p>
<p>Under the federal Fair Labor Standards Act (FLSA), covered nonexempt employees generally must receive at least time and a half for hours worked over 40 in a workweek. Some states go further. California, for example, also requires daily overtime in many cases. Exempt employees, often salaried, may not be owed overtime at all. See the <a href="https://www.dol.gov/agencies/whd/overtime" rel="noopener">U.S. Department of Labor overtime page</a> for the federal rules.</p>""",
        example="""<p>You earn <strong>$20 an hour</strong> and work 45 hours in a week. The overtime rate is $20 × 1.5 = $30. Regular pay is 40 × $20 = $800, overtime pay is 5 × $30 = $150, and the week's total is <strong>$950</strong> before taxes.</p>""",
        related=["hourly-to-salary", "time-duration", "take-home-pay", "pay-raise"],
        guides=["how-to-calculate-overtime-pay", "what-is-gross-pay", "how-much-is-25-an-hour"],
        disclaimer="general",
    ),
    dict(
        slug="percentage",
        name="Percentage Calculator",
        short="Find a percent of a number, what percent one number is of another, or the percent change.",
        desc="Free percentage calculator: find X% of a number, what percent one number is of another, percent increase or decrease, and percent change.",
        cat="everyday-math", also=["money-pay", "small-business"], popular=True,
        teaser="20% of 150 = 30",
        keywords="percent percentage of what percent change increase decrease difference calculate math ratio",
        fields=[
            F("mode", "What do you want to find?", "select", "of", wide=True, options=[
                ("of", "What is X% of a number?"), ("is", "X is what percent of Y?"),
                ("change", "Percent change from X to Y"), ("add", "Increase or decrease a number by X%")]),
            F("a", "Percent", "number", "20", labels={"of": "Percent", "is": "Part (X)", "change": "Starting value (X)", "add": "Percent"}),
            F("b", "Of this number", "number", "150", labels={"of": "Of this number", "is": "Whole (Y)", "change": "New value (Y)", "add": "Starting number"}),
        ],
        how="""<p>Every percentage problem is one of a few forms. Pick the one that matches your question:</p>
<div class="table-scroll"><table><thead><tr><th>Question</th><th>Formula</th></tr></thead><tbody>
<tr><td>What is X% of Y?</td><td>(X ÷ 100) × Y</td></tr>
<tr><td>X is what percent of Y?</td><td>(X ÷ Y) × 100</td></tr>
<tr><td>Percent change from X to Y</td><td>(Y − X) ÷ |X| × 100</td></tr>
<tr><td>Y increased by X%</td><td>Y × (1 + X ÷ 100)</td></tr></tbody></table></div>""",
        example="""<p>20% of 150 is 0.20 × 150 = <strong>30</strong>. If rent goes from $1,200 to $1,320, the change is ($1,320 − $1,200) ÷ $1,200 × 100 = <strong>10%</strong>. And 45 out of 60 questions right is 45 ÷ 60 × 100 = <strong>75%</strong>.</p>""",
        related=["discount", "pay-raise", "tip", "profit-margin", "markup"],
        guides=["how-to-calculate-a-percentage", "markup-vs-profit-margin"],
        disclaimer="none",
    ),
    dict(
        slug="discount",
        name="Discount Calculator",
        short="See the sale price and how much you save, including stacked discounts and sales tax.",
        desc="Calculate the sale price after a percent-off discount, stacked discounts, and sales tax. See exactly how much you save.",
        cat="money-pay", also=["small-business", "everyday-math"],
        teaser="30% off $80 → $56",
        keywords="discount sale price percent off coupon savings stacked extra off clearance sales tax",
        fields=[
            F("price", "Original price", "money", "80", min=0),
            F("disc", "Discount", "percent", "30", min=0, max=100),
            F("extra", "Extra discount (applied after)", "percent", "0", min=0, max=100, adv=True, optional=True, help="For “an extra 20% off sale prices.”"),
            F("tax", "Sales tax rate", "percent", "0", min=0, max=30, adv=True, optional=True),
        ],
        how="""<p class="formula">Sale price = original price × (1 − discount ÷ 100)</p>
<p>Stacked discounts apply one after the other, so they multiply. 30% off and then an extra 20% off leaves you paying 0.70 × 0.80 = 56% of the original price, a total discount of 44%, not 50%. Sales tax is added to the discounted price.</p>""",
        example="""<p>A jacket is <strong>$80</strong> and 30% off: $80 × 0.70 = <strong>$56</strong>, saving $24. With an extra 20% off at checkout: $56 × 0.80 = $44.80.</p>""",
        related=["percentage", "tip", "markup", "budget"],
        guides=["how-to-calculate-a-percentage"],
        disclaimer="none",
    ),
    dict(
        slug="pay-raise",
        name="Pay Raise Calculator",
        short="See your new pay from a raise percentage, or find the percentage from your new pay.",
        desc="Calculate a pay raise: new hourly or annual pay, raise percentage, and how much more you'll earn per paycheck and per year.",
        cat="money-pay", also=["work-career"], popular=True,
        teaser="3% on $50,000 → +$1,500/yr",
        keywords="pay raise salary increase percent raise cost of living cola new salary promotion merit increase hourly",
        fields=[
            F("payType", "Pay type", "select", "annual", options=[("annual", "Annual salary"), ("hourly", "Hourly wage")]),
            F("current", "Current pay", "money", "50000", min=0, positive=True),
            F("mode", "I know…", "select", "percent", options=[("percent", "The raise percentage"), ("newpay", "My new pay")]),
            F("raisePct", "Raise percentage", "percent", "3", min=-100, max=1000, modes="percent"),
            F("newPay", "New pay", "money", "51500", min=0, modes="newpay"),
            F("hoursYear", "Paid hours per year (hourly)", "number", "2080", min=1, max=8760, adv=True, help="40 hours × 52 weeks = 2,080."),
        ],
        how="""<p class="formula">New pay = current pay × (1 + raise ÷ 100)<br>Raise % = (new pay − current pay) ÷ current pay × 100</p>
<p>For hourly pay, the yearly difference is the hourly raise times your paid hours per year. Because U.S. income tax is progressive, a raise can push some income into a higher bracket, but only the dollars above the bracket line are taxed at the higher rate.</p>""",
        example="""<p>A <strong>3% raise on $50,000</strong> is $1,500 a year, bringing pay to <strong>$51,500</strong>. That's $125 more a month on average, or about $57.69 more per biweekly paycheck before taxes.</p>""",
        related=["hourly-to-salary", "salary-to-hourly", "take-home-pay", "percentage"],
        guides=["how-to-compare-two-job-offers", "what-is-net-pay", "how-to-calculate-a-percentage"],
        disclaimer="general",
    ),
    dict(
        slug="profit-margin",
        name="Profit Margin Calculator",
        short="Find your profit and margin from cost and selling price.",
        desc="Calculate gross profit, profit margin percentage, and markup from your cost and selling price. Works for products and services.",
        cat="small-business", also=["money-pay"], popular=True,
        teaser="Cost $40, price $60 → 33.33%",
        keywords="profit margin gross profit percentage margin markup cost price revenue small business pricing net profit",
        fields=[
            F("cost", "Cost", "money", "40", min=0, help="What it costs you to make or buy one unit."),
            F("price", "Selling price", "money", "60", min=0, positive=True),
            F("qty", "Units sold", "integer", "1", min=1, adv=True, help="Optional. Shows totals for a batch."),
        ],
        how="""<p>Profit margin tells you how much of each sale you keep after the cost of the item.</p>
<p class="formula">Gross profit = price − cost<br>Profit margin = gross profit ÷ price × 100</p>
<p>This is <strong>gross</strong> margin on a product. It doesn't subtract overhead like rent, software, or your own time. To see net margin for a whole business, use total revenue and total expenses for the same period.</p>""",
        example="""<p>You buy a product for <strong>$40</strong> and sell it for <strong>$60</strong>. Profit is $20, and the margin is $20 ÷ $60 = <strong>33.33%</strong>. The markup on cost is $20 ÷ $40 = 50%.</p>""",
        related=["markup", "break-even", "percentage", "discount"],
        guides=["how-to-calculate-profit-margin", "markup-vs-profit-margin"],
        disclaimer="general",
    ),
    dict(
        slug="markup",
        name="Markup Calculator",
        short="Set a selling price from cost using a markup or a target margin.",
        desc="Calculate selling price from cost and markup percentage, or price for a target profit margin. Shows profit, markup, and margin.",
        cat="small-business",
        teaser="Cost $40 + 50% → $60",
        keywords="markup pricing selling price cost plus target margin wholesale retail keystone small business",
        fields=[
            F("mode", "Price using…", "select", "markup", options=[("markup", "A markup on cost"), ("margin", "A target profit margin")]),
            F("cost", "Cost per item", "money", "40", min=0),
            F("pct", "Markup", "percent", "50", min=0, max=10000, labels={"markup": "Markup", "margin": "Target margin"}),
        ],
        how="""<p class="formula">Price from markup = cost × (1 + markup ÷ 100)<br>Price from margin = cost ÷ (1 − margin ÷ 100)</p>
<p>Markup is measured against cost. Margin is measured against price. That's why a 50% markup only gives you a 33% margin, and a 50% margin needs a 100% markup.</p>""",
        example="""<p>An item costs <strong>$40</strong>. A 50% markup gives a price of $40 × 1.5 = <strong>$60</strong>. To hit a 50% margin instead, price it at $40 ÷ 0.5 = <strong>$80</strong>.</p>""",
        related=["profit-margin", "break-even", "discount", "percentage"],
        guides=["markup-vs-profit-margin", "how-to-calculate-profit-margin"],
        disclaimer="general",
    ),
    dict(
        slug="break-even",
        name="Break-Even Calculator",
        short="Find how many units you need to sell to cover your costs.",
        desc="Calculate your break-even point in units and sales dollars from fixed costs, price, and variable cost per unit. Add a profit target.",
        cat="small-business", popular=True,
        teaser="$3,000 fixed → 200 units",
        keywords="break even breakeven point units sales fixed costs variable costs contribution margin small business profit target",
        fields=[
            F("fixed", "Fixed costs (per month)", "money", "3000", min=0, help="Rent, insurance, software, salaries — costs that don't change with sales."),
            F("price", "Price per unit", "money", "25", min=0, positive=True),
            F("varCost", "Variable cost per unit", "money", "10", min=0, help="Materials, packaging, transaction fees per sale."),
            F("target", "Profit target (same period)", "money", "0", min=0, adv=True, optional=True),
        ],
        how="""<p>Each sale contributes the difference between its price and its variable cost toward your fixed costs. That's the contribution margin.</p>
<p class="formula">Break-even units = fixed costs ÷ (price − variable cost per unit)</p>
<p>Add a profit target and the calculator shows how many units cover fixed costs <em>and</em> that profit. Keep the time period consistent: monthly fixed costs give you monthly units.</p>""",
        example="""<p>Fixed costs are <strong>$3,000 a month</strong>. You sell at $25 with $10 of variable cost, so each sale contributes $15. Break-even is $3,000 ÷ $15 = <strong>200 units</strong>, or $5,000 in sales per month.</p>""",
        related=["profit-margin", "markup", "budget", "percentage"],
        guides=["how-to-calculate-profit-margin", "markup-vs-profit-margin"],
        disclaimer="general",
    ),
    dict(
        slug="budget",
        name="Budget Calculator",
        short="Plan a monthly budget and see what's left over.",
        desc="Free monthly budget calculator. Enter your take-home pay and expenses to see what's left, where your money goes, and a 50/30/20 check.",
        cat="personal-finance", also=["mindset"], popular=True,
        teaser="See what's left each month",
        keywords="budget monthly budget planner expenses spending left over 50/30/20 needs wants savings money plan",
        fields=[
            F("income", "Monthly take-home income", "money", "4000", min=0, wide=True),
            F("housing", "Housing (rent or mortgage)", "money", "1300", min=0, optional=True),
            F("utilities", "Utilities and phone", "money", "250", min=0, optional=True),
            F("groceries", "Groceries", "money", "500", min=0, optional=True),
            F("transport", "Transportation", "money", "400", min=0, optional=True, help="Car payment, gas, insurance, transit."),
            F("insurance", "Insurance and health", "money", "200", min=0, optional=True),
            F("debt", "Debt payments", "money", "250", min=0, optional=True),
            F("savings", "Savings", "money", "400", min=0, optional=True),
            F("other", "Everything else", "money", "500", min=0, optional=True, help="Dining out, subscriptions, fun, gifts."),
        ],
        how="""<p>A budget is income minus spending. Use take-home pay, the amount that actually lands in your account, not your gross salary.</p>
<p class="formula">Left over = monthly take-home income − total planned spending</p>
<p>The calculator also compares your plan to the 50/30/20 rule of thumb: about 50% of take-home pay for needs, 30% for wants, and 20% for savings and extra debt payoff. It's a starting point, not a rule. In high-cost areas, needs often take more than half.</p>""",
        example="""<p>With <strong>$4,000</strong> of monthly take-home pay and the default expenses entered here, planned spending is $3,800, leaving <strong>$200</strong> unassigned. You could move that to savings or keep it as a buffer.</p>""",
        related=["take-home-pay", "savings-goal", "debt-payoff", "compound-interest"],
        guides=["how-much-should-i-save-from-each-paycheck", "what-is-net-pay"],
        disclaimer="financial",
    ),
    dict(
        slug="savings-goal",
        name="Savings Goal Calculator",
        short="Find out how much to save each month to reach a goal by a deadline.",
        desc="Calculate how much to save per month, per week, or per paycheck to reach a savings goal, with optional interest.",
        cat="personal-finance", also=["mindset"], popular=True,
        teaser="$5,000 in 12 months → $417/mo",
        keywords="savings goal how much to save monthly save each month per paycheck emergency fund down payment vacation target",
        fields=[
            F("goal", "Savings goal", "money", "5000", min=0, positive=True),
            F("current", "Already saved", "money", "0", min=0, optional=True),
            F("months", "Months to reach it", "integer", "12", min=1, max=600),
            F("rate", "Annual interest or return", "percent", "0", min=0, max=30, adv=True, optional=True, help="A high-yield savings account rate, for example. Leave at 0 to keep it simple."),
        ],
        how="""<p>Without interest, divide what you still need by the number of months.</p>
<p class="formula">Monthly savings = (goal − already saved) ÷ months</p>
<p>If you add an interest rate, the calculator lets your current savings grow at that rate and uses the future-value-of-annuity formula to find the monthly deposit that closes the gap, assuming deposits at the end of each month.</p>""",
        example="""<p>To save <strong>$5,000 in 12 months</strong> from zero, set aside $5,000 ÷ 12 = <strong>$416.67 a month</strong>, which is about $192.31 per biweekly paycheck.</p>""",
        related=["budget", "compound-interest", "simple-interest", "take-home-pay"],
        guides=["how-much-should-i-save-from-each-paycheck", "what-is-net-pay"],
        disclaimer="financial",
    ),
    dict(
        slug="debt-payoff",
        name="Debt Payoff Calculator",
        short="See how long it takes to pay off a debt and how much interest you'll pay.",
        desc="Calculate how long it will take to pay off a credit card or loan, total interest, and how much an extra payment saves.",
        cat="personal-finance", popular=True,
        teaser="$5,000 at 22% → months to $0",
        keywords="debt payoff credit card loan pay off interest apr monthly payment extra payment how long debt free",
        fields=[
            F("balance", "Balance owed", "money", "5000", min=0, positive=True),
            F("apr", "Interest rate (APR)", "percent", "22", min=0, max=100),
            F("payment", "Monthly payment", "money", "200", min=0, positive=True),
            F("extra", "Extra payment per month", "money", "0", min=0, adv=True, optional=True),
        ],
        how="""<p>Each month, interest is added at one-twelfth of the APR, then your payment is subtracted. The calculator repeats that until the balance reaches zero.</p>
<p class="formula">Monthly interest = balance × (APR ÷ 12)<br>New balance = balance + monthly interest − payment</p>
<p>If your payment is less than the first month's interest, the balance grows and never gets paid off. Credit card issuers may calculate interest daily, so your statement can differ slightly.</p>""",
        example="""<p>A <strong>$5,000</strong> balance at 22% APR with a $200 monthly payment takes about 3 years to pay off. Adding $50 a month shortens that and cuts the interest. Try it above to see the exact numbers.</p>""",
        related=["debt-to-income", "budget", "simple-interest", "compound-interest", "savings-goal"],
        guides=["how-much-should-i-save-from-each-paycheck"],
        disclaimer="financial",
        partner=dict(placement="debt-payoff", heading="Keep an eye on your credit",
                     text="Want to keep an eye on your credit while working through your debt? Credit monitoring can help you track changes to your credit information.",
                     cta="Check Credit Monitoring Options"),
    ),
    dict(
        slug="debt-to-income",
        name="Debt-to-Income Calculator",
        short="Find your debt-to-income ratio, the number lenders use to judge new loans.",
        desc="Calculate your debt-to-income (DTI) ratio from gross monthly income and monthly debt payments. Shows your housing ratio and total DTI.",
        cat="personal-finance", popular=False,
        teaser="$2,000 debts ÷ $6,000 = 33%",
        keywords="debt to income dti ratio mortgage loan qualify lender back-end front-end housing ratio credit debt payments",
        fields=[
            F("income", "Gross monthly income", "money", "6000", min=0, positive=True, wide=True, help="Before taxes and deductions. Include steady income you can document."),
            F("housing", "Rent or mortgage payment", "money", "1500", min=0, optional=True, help="For a mortgage, include property tax, homeowners insurance, and HOA dues if you pay them monthly."),
            F("car", "Car loan payments", "money", "350", min=0, optional=True),
            F("student", "Student loan payments", "money", "0", min=0, optional=True),
            F("cards", "Credit card minimum payments", "money", "150", min=0, optional=True, help="The minimum due, not the full balance."),
            F("personal", "Personal and other loan payments", "money", "0", min=0, optional=True),
            F("otherDebt", "Other required payments", "money", "0", min=0, optional=True, help="For example, child support or alimony you pay."),
        ],
        how="""<p>Your debt-to-income ratio, or DTI, is all your monthly debt payments divided by your gross monthly income.</p>
<p class="formula">DTI = total monthly debt payments ÷ gross monthly income × 100</p>
<p>Lenders often look at two versions:</p>
<ul>
<li><strong>Housing ratio</strong> (sometimes called front-end): just your rent or mortgage payment divided by gross income.</li>
<li><strong>Total DTI</strong> (back-end): every monthly debt payment, including housing, divided by gross income.</li>
</ul>
<p>Count required monthly payments on debts. Everyday bills like groceries, utilities, phone, and insurance premiums (other than homeowners insurance built into a mortgage payment) usually aren't included. Different loan products and lenders set different DTI limits, so check with the lender you're considering.</p>""",
        example="""<p>You earn <strong>$6,000 a month</strong> before taxes. Your rent is $1,500, your car payment is $350, and your credit card minimums are $150, for $2,000 in monthly debt payments.</p>
<p>$2,000 ÷ $6,000 × 100 = <strong>33.3% DTI</strong>. Your housing ratio is $1,500 ÷ $6,000 = 25%.</p>""",
        related=["debt-payoff", "budget", "take-home-pay", "savings-goal"],
        guides=["what-is-gross-pay", "what-is-net-pay"],
        disclaimer="financial",
        partner=dict(placement="debt-to-income", heading="Related credit resource",
                     text="Lenders usually look at your credit along with your DTI. Want to review your credit information and credit-monitoring options?",
                     cta="Check Your Credit & Monitoring Options"),
        sources=[("Consumer Financial Protection Bureau: What is a debt-to-income ratio?", "https://www.consumerfinance.gov/ask-cfpb/what-is-a-debt-to-income-ratio-en-1791/")],
    ),
    dict(
        slug="simple-interest",
        name="Simple Interest Calculator",
        short="Calculate simple interest on a loan or deposit.",
        desc="Calculate simple interest from principal, annual rate, and time in years, months, or days. See interest and the total amount.",
        cat="personal-finance", also=["everyday-math"],
        teaser="$1,000 at 5% for 3 yrs → $150",
        keywords="simple interest principal rate time loan deposit i=prt interest earned owed",
        fields=[
            F("principal", "Principal", "money", "1000", min=0),
            F("rate", "Annual interest rate", "percent", "5", min=0, max=100),
            F("time", "Time", "number", "3", min=0),
            F("unit", "Time unit", "select", "years", options=[("years", "Years"), ("months", "Months"), ("days", "Days")]),
        ],
        how="""<p class="formula">Interest = principal × annual rate × time in years</p>
<p>With simple interest, you only earn or pay interest on the original principal. Interest doesn't build on itself. Most savings accounts and credit cards use compound interest instead.</p>""",
        example="""<p><strong>$1,000</strong> at 5% for 3 years earns $1,000 × 0.05 × 3 = <strong>$150</strong>, for a total of $1,150.</p>""",
        related=["compound-interest", "debt-payoff", "savings-goal", "percentage"],
        guides=["how-to-calculate-a-percentage"],
        disclaimer="financial",
    ),
    dict(
        slug="compound-interest",
        name="Compound Interest Calculator",
        short="See how savings grow with compound interest and monthly deposits.",
        desc="Calculate compound interest with monthly contributions. See your future balance, total deposits, interest earned, and a year-by-year table.",
        cat="personal-finance", popular=True,
        teaser="$100/mo for 10 yrs at 5%",
        keywords="compound interest investment growth savings growth future value monthly contributions apy compounding retirement",
        fields=[
            F("principal", "Starting amount", "money", "1000", min=0),
            F("monthly", "Monthly deposit", "money", "100", min=0, optional=True),
            F("rate", "Annual interest rate", "percent", "5", min=0, max=50),
            F("years", "Years", "number", "10", min=0.0833, max=100),
            F("compound", "Compounding", "select", "12", options=[("12", "Monthly"), ("365", "Daily"), ("4", "Quarterly"), ("1", "Yearly")]),
        ],
        how="""<p>Compound interest earns interest on your interest. The calculator converts the annual rate and compounding frequency into an equivalent monthly rate, then grows the balance month by month and adds your deposit at the end of each month.</p>
<p class="formula">Monthly rate = (1 + annual rate ÷ n)<sup>n ÷ 12</sup> − 1, where n is compounding periods per year<br>Each month: balance = balance × (1 + monthly rate) + deposit</p>""",
        example="""<p>Start with <strong>$1,000</strong>, add <strong>$100 a month</strong>, and earn 5% compounded monthly. After 10 years you've put in $13,000 and the balance is about <strong>$17,175</strong>, so roughly $4,175 came from interest.</p>""",
        related=["simple-interest", "savings-goal", "budget", "debt-payoff"],
        guides=["how-much-should-i-save-from-each-paycheck"],
        disclaimer="financial",
    ),
    dict(
        slug="age",
        name="Age Calculator",
        short="Find exact age in years, months, and days, and the days until the next birthday.",
        desc="Calculate exact age in years, months, and days from a date of birth. Also shows total days, weeks, and the next birthday.",
        cat="everyday-math",
        teaser="Exact age + next birthday",
        keywords="age calculator how old am i date of birth birthday years months days born",
        fields=[
            F("birth", "Date of birth", "date", "", required=True),
            F("asof", "Age on this date", "date", "today", required=True),
        ],
        how="""<p>The calculator counts full years, then full months, then remaining days between the two dates. If the day of the month hasn't been reached yet, it borrows the length of the previous month.</p>
<p>People born on February 29 are counted as having their birthday on February 28 in non-leap years. Some laws and organizations use March 1 instead.</p>""",
        example="""<p>Someone born on <strong>May 15, 1990</strong> is <strong>36 years, 4 months, and 18 days</strong> old on October 3, 2026.</p>""",
        related=["date-difference", "time-duration", "unit-converter"],
        guides=[],
        disclaimer="none",
    ),
    dict(
        slug="date-difference",
        name="Date Difference Calculator",
        short="Count the days, weeks, and weekdays between two dates.",
        desc="Count days between two dates, including weeks, months, and weekdays (Monday–Friday). Choose whether to include the end date.",
        cat="everyday-math", also=["work-career"],
        teaser="Days until any date",
        keywords="days between dates date difference how many days until countdown weeks business days weekdays duration",
        fields=[
            F("start", "Start date", "date", "today", required=True),
            F("end", "End date", "date", "today+30", required=True),
            F("inclusive", "Include the end date in the count", "check", "0"),
        ],
        how="""<p>The calculator subtracts the start date from the end date. By default it counts the start date but not the end date, the way you'd count nights of a hotel stay. Check the box to include both dates, the way you'd count days of an event.</p>
<p>The weekday count includes Monday through Friday and does not skip public holidays.</p>""",
        example="""<p>From <strong>October 3, 2026</strong> to <strong>December 25, 2026</strong> is <strong>83 days</strong>, which is 11 weeks and 6 days.</p>""",
        related=["age", "time-duration", "savings-goal"],
        guides=[],
        disclaimer="none",
    ),
    dict(
        slug="time-duration",
        name="Time Duration Calculator",
        short="Find the hours and minutes between two times, minus breaks.",
        desc="Calculate hours worked between a start and end time, subtract breaks, handle overnight shifts, and convert to decimal hours for timesheets.",
        cat="everyday-math", also=["work-career"],
        teaser="9:00–5:30 minus 30 min = 8.00 hrs",
        keywords="time duration hours worked timesheet time card shift clock in clock out decimal hours break overnight",
        fields=[
            F("start", "Start time", "time", "09:00", required=True),
            F("end", "End time", "time", "17:30", required=True),
            F("breakMin", "Unpaid break (minutes)", "integer", "30", min=0, max=1440, optional=True),
            F("rate", "Hourly rate", "money", "", min=0, adv=True, optional=True, help="Optional. Shows pay for this shift."),
        ],
        how="""<p class="formula">Time worked = end time − start time − break</p>
<p>If the end time is earlier than the start time, the shift is treated as running past midnight. Decimal hours divide the minutes by 60, so 8 hours 15 minutes is 8.25 hours.</p>""",
        example="""<p>A shift from <strong>9:00 a.m. to 5:30 p.m.</strong> with a 30-minute unpaid lunch is 8 hours 30 minutes minus 30 minutes = <strong>8 hours</strong>, or 8.00 decimal hours.</p>""",
        related=["overtime", "hourly-to-salary", "date-difference"],
        guides=["how-to-calculate-overtime-pay"],
        disclaimer="none",
    ),
    dict(
        slug="unit-converter",
        name="Unit Converter",
        short="Convert length, weight, volume, area, speed, and temperature.",
        desc="Convert units of length, weight, volume, area, speed, and temperature between U.S. customary and metric. Cups, feet, pounds, Fahrenheit, and more.",
        cat="everyday-math",
        teaser="1 cup = 236.59 mL",
        keywords="unit converter conversion metric imperial feet meters inches cm pounds kg ounces grams cups ml fahrenheit celsius miles km mph acres gallons liters",
        fields=[
            F("category", "Type of measurement", "select", "length", options=[("length", "Length"), ("weight", "Weight"), ("volume", "Volume and cooking"), ("temperature", "Temperature"), ("area", "Area"), ("speed", "Speed")]),
            F("value", "Amount", "number", "1"),
            F("from", "From", "select", "ft", options=[("ft", "Feet")]),
            F("to", "To", "select", "m", options=[("m", "Meters")]),
        ],
        how="""<p>The converter changes the amount into a base unit (meters, kilograms, liters, square meters, or meters per second) and then into the unit you want, using exact conversion factors. For example, one inch is exactly 2.54 centimeters, and one pound is exactly 0.45359237 kilograms.</p>
<p class="formula">°F = °C × 9 ÷ 5 + 32<br>°C = (°F − 32) × 5 ÷ 9</p>""",
        example="""<p><strong>6 feet</strong> is 1.8288 meters. <strong>1 cup</strong> (U.S.) is about 236.59 milliliters. <strong>350°F</strong> is about 176.67°C.</p>""",
        related=["percentage", "time-duration", "age"],
        guides=[],
        disclaimer="none",
    ),
    dict(
        slug="tip",
        name="Tip Calculator",
        short="Work out the tip and split the bill.",
        desc="Calculate the tip, total bill, and each person's share. Round up per person for an easy split.",
        cat="everyday-math", also=["money-pay"],
        teaser="20% on $64 split 3 ways",
        keywords="tip gratuity restaurant bill split per person 15 18 20 percent dinner",
        fields=[
            F("bill", "Bill amount", "money", "64", min=0),
            F("pct", "Tip", "percent", "20", min=0, max=100),
            F("people", "Number of people", "integer", "1", min=1, max=100),
            F("roundUp", "Round each person's share up to the next dollar", "check", "0"),
        ],
        how="""<p class="formula">Tip = bill × tip percent ÷ 100<br>Each person pays = (bill + tip) ÷ number of people</p>
<p>Quick mental math: 10% is the bill with the decimal moved one place left. Double it for 20%. For 15%, add half of the 10% amount.</p>""",
        example="""<p>A <strong>$64</strong> bill with a 20% tip is $12.80, for a total of $76.80. Split three ways, each person pays $25.60.</p>""",
        related=["percentage", "discount", "budget"],
        guides=["how-to-calculate-a-percentage"],
        disclaimer="none",
    ),
    dict(
        slug="tax-bracket",
        name="Tax Bracket Calculator",
        short="See your federal tax bracket, how much tax falls in each bracket, and your effective rate.",
        desc="Find your federal income tax bracket, marginal and effective tax rates, and tax owed in each bracket for the selected tax year.",
        cat="taxes", also=["money-pay"], tax=True, popular=True,
        teaser="$60,000 single → 12% bracket",
        keywords="tax bracket federal income tax marginal rate effective tax rate how much tax do i owe irs brackets 2026 single married head of household",
        fields=[
            F("taxYear", "Tax year", "select", "{TAX_DEFAULT}", options="{TAX_YEARS}"),
            F("status", "Filing status", "select", "single", options=[("single", "Single"), ("married_joint", "Married filing jointly"), ("head_household", "Head of household")]),
            F("incomeType", "The income I'm entering is…", "select", "gross", wide=True, options=[("gross", "Total income (subtract the standard deduction for me)"), ("taxable", "Taxable income (deductions already subtracted)")]),
            F("income", "Income", "money", "60000", min=0, wide=True),
        ],
        how="""<p>The U.S. uses progressive brackets: each rate applies only to the slice of taxable income inside that bracket. Your <strong>marginal rate</strong> is the rate on your last dollar. Your <strong>effective rate</strong> is your total tax divided by your income.</p>
<p class="formula">Tax = sum of (income in each bracket × that bracket's rate)<br>Effective rate = total tax ÷ income × 100</p>
<p>If you choose total income, the calculator subtracts the standard deduction for your filing status first. It doesn't include credits, itemized deductions, capital gains rates, or other special rules.</p>""",
        example="""<p>A single filer with <strong>$60,000</strong> of income in 2026 subtracts the $16,100 standard deduction, leaving $43,900 of taxable income. The first $12,400 is taxed at 10% ($1,240) and the remaining $31,500 at 12% ($3,780), for <strong>$5,020</strong> of federal income tax.</p>
<p>The marginal rate is 12%, but the effective rate on the full $60,000 is about 8.4%.</p>""",
        related=["take-home-pay", "self-employment-tax", "pay-raise", "salary-to-hourly"],
        guides=["what-is-net-pay", "what-is-gross-pay"],
        disclaimer="tax",
    ),
    dict(
        slug="self-employment-tax",
        name="Self-Employment Tax Estimator",
        short="Estimate Social Security and Medicare tax on freelance, gig, or small-business profit.",
        desc="Estimate self-employment tax (Social Security and Medicare) on net profit, the deductible half, and a quarterly set-aside amount.",
        cat="taxes", also=["small-business", "work-career"], tax=True,
        teaser="$40,000 profit → about $5,652",
        keywords="self employment tax se tax 1099 freelance gig independent contractor schedule se social security medicare 15.3 quarterly estimated side hustle",
        fields=[
            F("taxYear", "Tax year", "select", "{TAX_DEFAULT}", options="{TAX_YEARS}"),
            F("profit", "Net self-employment profit for the year", "money", "40000", min=0, wide=True, help="Income minus business expenses (for example, Schedule C net profit)."),
            F("wages", "W-2 wages from a job, if any", "money", "0", min=0, adv=True, optional=True, help="W-2 wages count toward the Social Security wage limit first."),
        ],
        how="""<p>Self-employed people pay both the employee and employer shares of Social Security and Medicare, through self-employment (SE) tax.</p>
<p class="formula">Net earnings = net profit × 92.35%<br>SE tax = net earnings × 12.4% (Social Security, up to the yearly wage base) + net earnings × 2.9% (Medicare)</p>
<p>The 92.35% step reflects the employer-equivalent share. If you also have W-2 wages, they use up part of the Social Security wage base first. No SE tax is due if net earnings are under $400. You can generally deduct half of your SE tax when figuring income tax.</p>
<p>This estimate covers SE tax only. Income tax on the same profit, and the Additional Medicare Tax at higher incomes, are separate.</p>""",
        example="""<p><strong>$40,000</strong> of net profit gives net earnings of $40,000 × 0.9235 = $36,940. SE tax is $36,940 × 15.3% = <strong>$5,651.82</strong>. Half of that, $2,825.91, is deductible. Setting aside about $1,413 a quarter covers the SE tax portion.</p>""",
        related=["tax-bracket", "take-home-pay", "profit-margin", "savings-goal"],
        guides=["what-is-net-pay"],
        disclaimer="tax",
    ),
    dict(
        slug="goal-breakdown",
        legend="Your goal",
        name="Goal Breakdown Calculator",
        short="Turn a big goal into a daily, weekly, and monthly target.",
        desc="Break any goal into daily, weekly, and monthly targets based on your deadline and progress so far. Works for money, pages, miles, or anything you can count.",
        cat="mindset", also=["personal-finance"], popular=True,
        teaser="$3,000 in 90 days → $233/wk",
        keywords="goal breakdown goal setting planner target per day per week deadline progress pace motivation small steps",
        fields=[
            F("goal", "Goal amount", "number", "3000", min=0, positive=True),
            F("unit", "Unit", "text", "dollars", help="Dollars, pages, miles, sales calls — whatever you're counting."),
            F("done", "Already done", "number", "0", min=0, optional=True),
            F("deadline", "Deadline", "date", "today+90", required=True),
            F("days", "Days per week you'll work on it", "integer", "7", min=1, max=7, adv=True),
        ],
        how="""<p>The calculator counts the days from today to your deadline and spreads what's left evenly across them.</p>
<p class="formula">Per day = (goal − already done) ÷ working days left<br>Per week = per day × days per week you'll work on it</p>
<p>Smaller targets are easier to start and easier to track. If the daily number looks too high, move the deadline or adjust the goal. A realistic plan you keep beats an ambitious one you drop.</p>""",
        example="""<p>You want to save <strong>$3,000 in 90 days</strong> and have nothing saved yet. That's $33.33 a day, $233.33 a week, or about $1,000 a month.</p>""",
        related=["savings-goal", "habit-consistency", "time-allocation", "budget"],
        guides=["how-much-should-i-save-from-each-paycheck"],
        disclaimer="none",
    ),
    dict(
        slug="habit-consistency",
        legend="Your habit",
        name="Habit Consistency Calculator",
        short="See how consistent you've been with a habit and when you'll reach your target.",
        desc="Track a habit: enter your start date and days completed to see your consistency rate, missed days, and when you'll hit your target streak or day count.",
        cat="mindset",
        teaser="21 of 30 days → 70%",
        keywords="habit tracker habit consistency streak routine days completed discipline challenge 30 day",
        fields=[
            F("start", "Day you started", "date", "today-29", required=True),
            F("completed", "Days you did the habit", "integer", "21", min=0),
            F("target", "Target number of days", "integer", "30", min=1, max=3650, help="For example, a 30-day challenge."),
        ],
        how="""<p class="formula">Consistency = days completed ÷ days since you started × 100</p>
<p>Days since you started includes today. The calculator also shows how many more days you need to reach your target and the earliest date you could get there if you do it every day from tomorrow.</p>
<p>Missing a day doesn't erase your progress. Consistency over weeks matters more than an unbroken streak.</p>""",
        example="""<p>You started a habit <strong>30 days ago</strong> (counting today) and did it on <strong>21</strong> of those days. Your consistency is 21 ÷ 30 = <strong>70%</strong>. To reach 30 total days, you need 9 more.</p>""",
        related=["goal-breakdown", "time-allocation", "date-difference"],
        guides=[],
        disclaimer="none",
    ),
    dict(
        slug="time-allocation",
        legend="Your week",
        name="Time Allocation Calculator",
        short="See where your 168 hours a week go and how much free time is left.",
        desc="Add up sleep, work, commuting, chores, and family time to see how much free time you really have each week and each day.",
        cat="mindset", also=["work-career"],
        teaser="168 hrs → your free time",
        keywords="time allocation time management free time hours in a week schedule balance productivity planner 168 hours",
        fields=[
            F("sleep", "Sleep per night (hours)", "number", "8", min=0, max=24),
            F("work", "Work per week (hours)", "number", "40", min=0, max=168),
            F("commuteMin", "Commute per workday (minutes, round trip)", "number", "40", min=0, max=1440),
            F("workdays", "Workdays per week", "integer", "5", min=0, max=7),
            F("chores", "Chores and errands per week (hours)", "number", "10", min=0, max=168, optional=True),
            F("family", "Family and caregiving per week (hours)", "number", "10", min=0, max=168, optional=True),
            F("selfcare", "Meals and personal care per day (hours)", "number", "2", min=0, max=24, optional=True),
            F("other", "Other commitments per week (hours)", "number", "4", min=0, max=168, optional=True, help="Church, classes, volunteering, appointments."),
        ],
        how="""<p>Every week has 168 hours (24 × 7). The calculator converts daily amounts to weekly ones, adds up your commitments, and shows what's left.</p>
<p class="formula">Free time = 168 − (sleep × 7) − work − commute − chores − family − (personal care × 7) − other</p>
<p>Seeing the real number helps you plan goals you can keep. If free time is tight, the table shows where the hours are going.</p>""",
        example="""<p>With 8 hours of sleep a night, a 40-hour work week, a 40-minute daily commute 5 days a week, and the other defaults on this page, you have about <strong>30.7 free hours a week</strong>, or roughly 4.4 hours a day.</p>""",
        related=["goal-breakdown", "habit-consistency", "time-duration", "budget"],
        guides=[],
        disclaimer="none",
    ),
    dict(
        slug="bible-reading-plan",
        legend="Your plan", button="Build my plan", answer_title="Your plan",
        name="Bible Reading Plan Generator",
        short="Build a day-by-day Bible reading plan that fits your pace.",
        desc="Create a Bible reading plan for the whole Bible, the Old or New Testament, the Gospels, Psalms, or Proverbs. Choose a finish date or chapters per day.",
        cat="faith-scripture", popular=True, bible=True,
        teaser="Whole Bible in a year → 3–4 chapters/day",
        keywords="bible reading plan read the bible in a year schedule chapters per day new testament old testament gospels psalms proverbs devotional",
        fields=[
            F("scope", "What do you want to read?", "select", "bible", wide=True, options=[
                ("bible", "The whole Bible (66 books, 1,189 chapters)"), ("ot", "Old Testament (929 chapters)"),
                ("nt", "New Testament (260 chapters)"), ("gospels", "The four Gospels (89 chapters)"),
                ("psalms", "Psalms (150 chapters)"), ("proverbs", "Proverbs (31 chapters)")]),
            F("start", "Start date", "date", "today", required=True),
            F("mode", "Plan by…", "select", "days", options=[("days", "Number of days"), ("perday", "Chapters per day")]),
            F("days", "Days to finish", "integer", "365", min=1, max=3650, modes="days"),
            F("perDay", "Chapters per day", "number", "3", min=0.1, max=200, modes="perday"),
        ],
        how="""<p>The generator lists the chapters in order and divides them as evenly as possible across your days, so each day's reading is about the same length.</p>
<p class="formula">Chapters per day = total chapters ÷ days<br>Days needed = total chapters ÷ chapters per day</p>
<p>Chapter counts follow the 66-book Protestant canon. Catholic and Orthodox Bibles include additional books, and some readers prefer chronological or mixed Old and New Testament plans. Chapter length varies a lot, so some days will take longer than others.</p>""",
        example="""<p>Reading the whole Bible (1,189 chapters) in <strong>365 days</strong> works out to about <strong>3.3 chapters a day</strong>. The New Testament (260 chapters) in 90 days is about 2.9 chapters a day.</p>""",
        related=["scripture-lookup", "scripture-memory", "bible-book-overview", "habit-consistency"],
        guides=[],
        disclaimer="none",
    ),
    dict(
        slug="bible-book-overview",
        legend="Choose a book", button="Show overview", answer_title="Overview",
        name="Bible Book Overview",
        short="Look up any book of the Bible: its testament, section, chapters, and reading time.",
        desc="Quick facts for each of the 66 books of the Protestant Bible: testament, traditional section, number of chapters, order, and how long it takes to read at your pace.",
        cat="faith-scripture", bible=True,
        teaser="Romans → 16 chapters, Pauline letters",
        keywords="bible book overview books of the bible how many chapters old testament new testament gospels epistles prophets order",
        fields=[
            F("book", "Book", "select", "Romans", wide=True, options="{BIBLE_BOOKS}"),
            F("perDay", "Your reading pace (chapters per day)", "number", "3", min=0.1, max=200),
        ],
        how="""<p>Pick a book to see where it sits in the Bible, the section it's traditionally grouped with, and how many chapters it has. The reading-time line divides the chapters by your daily pace.</p>
<p>Sections follow a common Protestant arrangement: Law, History, Poetry and Wisdom, Major Prophets, and Minor Prophets in the Old Testament; Gospels, History, Paul's Letters, General Letters, and Prophecy in the New Testament. Other traditions group some books differently. Hebrews, for example, is sometimes listed with Paul's letters.</p>""",
        example="""<p><strong>Romans</strong> is the 45th book, the first of Paul's letters in the New Testament, with 16 chapters. At 3 chapters a day, you'd finish it in 6 days.</p>""",
        related=["scripture-lookup", "bible-reading-plan", "scripture-memory"],
        guides=[],
        disclaimer="none",
    ),
    dict(
        slug="scripture-memory",
        legend="Your plan", button="Build my plan", answer_title="Your plan",
        name="Scripture Memorization Planner",
        short="Plan how many verses to learn each week and when you'll finish.",
        desc="Plan Scripture memorization: enter how many verses you want to learn and your weekly pace to get a finish date and a week-by-week schedule with review.",
        cat="faith-scripture", also=["mindset"],
        teaser="24 verses at 2/week → 12 weeks",
        keywords="scripture memorization memorize bible verses plan memory verse schedule weekly review",
        fields=[
            F("passage", "Passage or set of verses", "text", "Psalm 23 and Romans 8", help="Optional label for your plan."),
            F("verses", "Number of verses", "integer", "24", min=1, max=5000),
            F("perWeek", "New verses per week", "integer", "2", min=1, max=100),
            F("start", "Start date", "date", "today", required=True),
        ],
        how="""<p class="formula">Weeks needed = number of verses ÷ new verses per week (rounded up)</p>
<p>Each week, learn the new verses and review everything you've already learned. Many people find a small weekly amount with steady review sticks better than cramming. The schedule numbers verses in the order you plan to learn them.</p>""",
        example="""<p>Learning <strong>24 verses</strong> at <strong>2 new verses a week</strong> takes <strong>12 weeks</strong>. By week 6, you'd be reviewing 10 verses and adding 2 new ones.</p>""",
        related=["scripture-lookup", "scripture-topics", "bible-reading-plan", "habit-consistency"],
        guides=[],
        disclaimer="none",
    ),
    dict(
        slug="scripture-lookup",
        legend="Your reference", button="Look up", answer_title="Passage",
        name="Scripture Reference Lookup",
        short="Type a Bible reference and read the passage in the World English Bible.",
        desc="Look up any Bible verse or passage by reference, like John 3:16, Psalm 23, or Romans 8:28-39, and read it in the public-domain World English Bible.",
        cat="faith-scripture", bible=True, popular=True,
        teaser="John 3:16 → read it instantly",
        keywords="bible verse lookup scripture reference john 3:16 psalm 23 read bible online passage world english bible web verse",
        fields=[
            F("ref", "Reference", "text", "Psalm 23; John 3:16-17", wide=True,
              help="Examples: John 3:16, Romans 8:28-39, Psalm 23, Genesis 1:1-2:3. Separate several with a semicolon."),
        ],
        how="""<p>Type a book, chapter, and verse. The lookup understands full names and common short forms (Gen, Ps, 1 Cor, Phil), whole chapters (Psalm 23), verse ranges (Romans 8:28-39), and ranges that cross chapters (Genesis 1:1-2:3). Separate up to 10 references with semicolons.</p>
<p>The text is the <strong>World English Bible (WEB)</strong>, a modern English translation in the public domain. In the Old Testament, the WEB writes God's name as “Yahweh” where many translations use “the LORD.”</p>""",
        example="""<p>Enter <strong>Philippians 4:6-7</strong> to read two verses, <strong>Psalm 23</strong> for the whole psalm, or <strong>Matthew 5:3-12; Luke 6:20-23</strong> to compare two passages.</p>""",
        related=["bible-verse-finder", "scripture-topics", "scripture-memory", "bible-reading-plan"],
        guides=[],
        disclaimer="none",
    ),
    dict(
        slug="bible-verse-finder",
        legend="Your search", button="Search", answer_title="Results",
        name="Bible Verse Finder",
        short="Search the whole Bible for a word or phrase.",
        desc="Search the World English Bible by keyword or exact phrase. Narrow to the Old Testament, New Testament, Gospels, Psalms, or Proverbs.",
        cat="faith-scripture", bible=True,
        teaser="Search “shepherd” in Psalms",
        keywords="bible verse finder search the bible keyword find verse about word phrase concordance where in the bible",
        fields=[
            F("q", "Word or phrase", "text", "shepherd", wide=True),
            F("scope", "Search in", "select", "psalms", options=[
                ("bible", "The whole Bible"), ("ot", "Old Testament"), ("nt", "New Testament"),
                ("gospels", "The four Gospels"), ("psalms", "Psalms"), ("proverbs", "Proverbs")]),
            F("match", "Match", "select", "all", options=[("all", "All of these words"), ("phrase", "This exact phrase")]),
        ],
        how="""<p>The finder looks through every verse in the books you choose and lists the ones that contain your words. “All of these words” finds verses that contain each word anywhere in the verse. “This exact phrase” finds the words together, in order.</p>
<p>Searches match the start of words, so <em>forgive</em> also finds <em>forgiven</em> and <em>forgiveness</em>. The first whole-Bible search loads the full text (a few megabytes), so it can take a moment on a slow connection. Searches after that are instant.</p>
<p>Results use the <strong>World English Bible (WEB)</strong>. Different translations use different words, so a verse you remember may be worded differently here.</p>""",
        example="""<p>Searching <strong>shepherd</strong> in Psalms finds verses including Psalm 23:1 and Psalm 80:1. Searching the exact phrase <strong>be strong and courageous</strong> across the whole Bible finds passages in Deuteronomy and Joshua.</p>""",
        related=["scripture-lookup", "scripture-topics", "bible-book-overview"],
        guides=[],
        disclaimer="none",
    ),
    dict(
        slug="scripture-topics",
        legend="Choose a topic", button="Show verses", answer_title="Passages",
        name="Scripture Topic Finder",
        short="Read passages often studied on faith, hope, work, money, family, and more.",
        desc="Choose a topic like faith, hope, wisdom, stewardship, work, money, family, forgiveness, or purpose and read related Bible passages in the World English Bible.",
        cat="faith-scripture", also=["mindset"], bible=True,
        teaser="Topic: hope → 6 passages",
        keywords="bible verses about topic scripture on faith hope perseverance wisdom stewardship work money family forgiveness purpose peace strength love gratitude",
        fields=[
            F("topic", "Topic", "select", "hope", wide=True, options=[
                ("faith", "Faith"), ("hope", "Hope"), ("perseverance", "Perseverance"), ("wisdom", "Wisdom"),
                ("stewardship", "Stewardship"), ("work", "Work"), ("money", "Money"), ("family", "Family"),
                ("forgiveness", "Forgiveness"), ("purpose", "Purpose"), ("peace", "Peace and worry"),
                ("strength", "Strength and courage"), ("love", "Love"), ("gratitude", "Gratitude")]),
        ],
        how="""<p>Each topic shows a short set of passages that are commonly read on that subject, with the full text from the <strong>World English Bible (WEB)</strong>.</p>
<p>These lists are a starting point for study, not a complete or official list, and they don't represent one tradition's interpretation. Reading the surrounding chapter helps you see each passage in context. Use the <a href="/tools/scripture-lookup/">Scripture Reference Lookup</a> to read more.</p>""",
        example="""<p>Choosing <strong>Money</strong> shows passages including Hebrews 13:5, Matthew 6:19-21, and Luke 14:28, the verse about counting the cost before you build.</p>""",
        related=["scripture-lookup", "bible-verse-finder", "scripture-memory", "bible-reading-plan"],
        guides=[],
        disclaimer="none",
    ),
]


# Planned tools, shown on category pages as "coming next" (not linked).
PLANNED = {
    "money-pay": ["Pay Cut Calculator", "Commission Calculator", "Bonus Calculator", "Weekly, Biweekly, and Daily Pay Calculators",
                  "Tax Percentage Calculator", "Hourly Rate Goal Calculator", "Freelance Rate Calculator", "Emergency Fund Calculator"],
    "work-career": ["Job Offer Comparison Tool", "Salary Comparison Calculator", "Timecard Calculator", "PTO and Vacation Hours Calculator",
                    "Commute Cost Calculator", "Remote Work Savings Calculator", "Contractor Rate Calculator", "Career Change Salary Calculator"],
    "small-business": ["Gross and Net Profit Calculators", "Revenue Calculator", "Business Expense Calculator", "Wholesale and Retail Pricing Calculators",
                       "Sales Tax Calculator", "Cash Flow Calculator", "ROI Calculator", "Startup Cost Calculator"],
    "everyday-math": ["Fraction Calculator", "Ratio Calculator", "Average Calculator", "Date Calculator (add or subtract days)",
                      "Area Calculator", "Speed and Distance Calculator", "Fuel Cost Calculator", "Recipe Measurement Converter"],
    "personal-finance": ["Emergency Fund Calculator", "Credit Card Payoff Calculator", "Loan Payment Calculator",
                         "Net Worth Calculator", "Mortgage Payment Calculator", "Rent vs. Buy Calculator", "Car Affordability Calculator"],
    "taxes": ["Federal Income Tax Estimator", "Estimated Quarterly Tax Calculator", "W-2 vs. 1099 Calculator", "Tax Withholding Estimator", "Tax Refund Estimate Tool"],
    "mindset": ["Monthly Goal Planner", "Goal Setting Worksheet", "Productivity Planner", "Savings Motivation Calculator"],
    "faith-scripture": ["Prayer Journal Generator", "Verse of the Day", "Side-by-Side Passage Compare"],
}
