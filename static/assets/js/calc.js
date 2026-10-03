/* ==========================================================================
   Get Solve Spring — calculator engine
   --------------------------------------------------------------------------
   Every tool page has <form data-calc="slug">. The engine:
     1. reads and validates inputs (data-kind, data-min, data-max, required)
     2. calls GSS_CALCS[slug](values)
     3. renders the returned answer object into [data-answer]

   A compute function returns either:
     { error: "message" }
   or
     { primary: { label, value },
       rows:  [[label, value], ...],
       note:  "plain text shown under the answer",
       table: { caption, head: [...], rows: [[...]], numCols: [indexes] } }

   To add a calculator: define its inputs in src/tools.py, then add a
   function to GSS_CALCS below with the same slug. See README.md.
   ========================================================================== */
(function () {
  "use strict";

  /* ---------- Formatting ---------- */
  var usd2 = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", minimumFractionDigits: 2, maximumFractionDigits: 2 });
  var usd0 = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", minimumFractionDigits: 0, maximumFractionDigits: 0 });
  var fmt = {
    money: function (x) {
      if (!isFinite(x)) return "—";
      var r = Math.round(x * 100) / 100;
      return Math.abs(r - Math.round(r)) < 0.005 ? usd0.format(Math.round(r)) : usd2.format(r);
    },
    money2: function (x) { return isFinite(x) ? usd2.format(x) : "—"; },
    money0: function (x) { return isFinite(x) ? usd0.format(Math.round(x)) : "—"; },
    pct: function (x, d) {
      if (!isFinite(x)) return "—";
      d = d === undefined ? 2 : d;
      var s = (Math.round(x * Math.pow(10, d)) / Math.pow(10, d)).toLocaleString("en-US", { maximumFractionDigits: d });
      return s + "%";
    },
    num: function (x, d) {
      if (!isFinite(x)) return "—";
      return x.toLocaleString("en-US", { maximumFractionDigits: d === undefined ? 4 : d });
    },
    plural: function (n, word) { return n + " " + word + (n === 1 ? "" : "s"); },
    duration: function (months) {
      var y = Math.floor(months / 12), m = months % 12, parts = [];
      if (y) parts.push(fmt.plural(y, "year"));
      if (m || !y) parts.push(fmt.plural(m, "month"));
      return parts.join(", ");
    },
    date: function (d) {
      return d.toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric", timeZone: "UTC" });
    }
  };

  /* ---------- Date helpers (UTC to avoid daylight-saving surprises) ---------- */
  function parseDate(s) {
    var m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(s || "");
    if (!m) return null;
    var d = new Date(Date.UTC(+m[1], +m[2] - 1, +m[3]));
    return d.getUTCMonth() === +m[2] - 1 ? d : null;
  }
  function todayISO() {
    var t = new Date();
    return t.getFullYear() + "-" + String(t.getMonth() + 1).padStart(2, "0") + "-" + String(t.getDate()).padStart(2, "0");
  }
  function daysInMonth(y, m) { return new Date(Date.UTC(y, m + 1, 0)).getUTCDate(); }
  var DAY = 86400000;
  function ymdDiff(a, b) {
    var y = b.getUTCFullYear() - a.getUTCFullYear();
    var mo = b.getUTCMonth() - a.getUTCMonth();
    var d = b.getUTCDate() - a.getUTCDate();
    if (d < 0) {
      mo -= 1;
      var pm = b.getUTCMonth() - 1, py = b.getUTCFullYear();
      if (pm < 0) { pm = 11; py -= 1; }
      d += daysInMonth(py, pm);
    }
    if (mo < 0) { y -= 1; mo += 12; }
    return { y: y, m: mo, d: d };
  }

  /* ---------- Tax helpers (data comes from /assets/js/tax-data.js) ---------- */
  function bracketTax(taxable, brackets) {
    var tax = 0, rows = [];
    for (var i = 0; i < brackets.length; i++) {
      var lo = brackets[i][0], rate = brackets[i][1];
      var hi = i + 1 < brackets.length ? brackets[i + 1][0] : Infinity;
      if (taxable <= lo) break;
      var amt = Math.min(taxable, hi) - lo;
      tax += amt * rate;
      rows.push({ rate: rate, amount: amt, tax: amt * rate });
    }
    return { tax: tax, rows: rows, marginal: rows.length ? rows[rows.length - 1].rate : brackets[0][1] };
  }

  /* ---------- Unit data for the converter ---------- */
  var UNITS = {
    length: { mm: ["Millimeters", 0.001], cm: ["Centimeters", 0.01], m: ["Meters", 1], km: ["Kilometers", 1000],
      in: ["Inches", 0.0254], ft: ["Feet", 0.3048], yd: ["Yards", 0.9144], mi: ["Miles", 1609.344] },
    weight: { mg: ["Milligrams", 0.000001], g: ["Grams", 0.001], kg: ["Kilograms", 1], oz: ["Ounces", 0.028349523125],
      lb: ["Pounds", 0.45359237], st: ["Stone", 6.35029318], ton: ["US tons", 907.18474], tonne: ["Metric tons", 1000] },
    volume: { ml: ["Milliliters", 0.001], l: ["Liters", 1], tsp: ["Teaspoons (US)", 0.00492892159375], tbsp: ["Tablespoons (US)", 0.01478676478125],
      floz: ["Fluid ounces (US)", 0.0295735295625], cup: ["Cups (US)", 0.2365882365], pt: ["Pints (US)", 0.473176473],
      qt: ["Quarts (US)", 0.946352946], gal: ["Gallons (US)", 3.785411784] },
    area: { sqin: ["Square inches", 0.00064516], sqft: ["Square feet", 0.09290304], sqyd: ["Square yards", 0.83612736],
      sqm: ["Square meters", 1], acre: ["Acres", 4046.8564224], ha: ["Hectares", 10000], sqmi: ["Square miles", 2589988.110336] },
    speed: { mph: ["Miles per hour", 0.44704], kph: ["Kilometers per hour", 1 / 3.6], mps: ["Meters per second", 1],
      fps: ["Feet per second", 0.3048], kn: ["Knots", 1852 / 3600] },
    temperature: { f: ["Fahrenheit", null], c: ["Celsius", null], k: ["Kelvin", null] }
  };
  var UNIT_DEFAULTS = { length: ["ft", "m"], weight: ["lb", "kg"], volume: ["cup", "ml"], area: ["sqft", "sqm"], speed: ["mph", "kph"], temperature: ["f", "c"] };
  function convert(cat, val, from, to) {
    if (cat === "temperature") {
      var c = from === "c" ? val : from === "f" ? (val - 32) * 5 / 9 : val - 273.15;
      return to === "c" ? c : to === "f" ? c * 9 / 5 + 32 : c + 273.15;
    }
    return val * UNITS[cat][from][1] / UNITS[cat][to][1];
  }

  /* ======================================================================
     Calculators
     ====================================================================== */
  var C = {};

  C["hourly-to-salary"] = function (v) {
    var otPay = v.otHours * v.rate * v.otMult;
    var week = v.rate * v.hours + otPay;
    var annual = week * v.weeks;
    var rows = [
      ["Weekly (a full work week)", fmt.money(week)],
      ["Biweekly (every two weeks)", fmt.money(annual / 26)],
      ["Semimonthly (twice a month)", fmt.money(annual / 24)],
      ["Monthly (average)", fmt.money(annual / 12)],
      ["Daily (" + v.days + "-day week)", fmt.money(week / v.days)]
    ];
    if (v.otHours > 0) rows.push(["Overtime included per week", fmt.money(otPay)]);
    return {
      primary: { label: "Annual pay before taxes", value: fmt.money(annual) },
      rows: rows,
      note: "Monthly pay is an average: annual pay divided by 12. Biweekly and semimonthly amounts are annual pay divided by 26 and 24. All figures are gross pay, before taxes and deductions."
    };
  };

  C["salary-to-hourly"] = function (v) {
    var hourly = v.salary / (v.hours * v.weeks);
    var rows = [
      ["Weekly", fmt.money(v.salary / v.weeks)],
      ["Biweekly (26 paychecks)", fmt.money(v.salary / 26)],
      ["Semimonthly (24 paychecks)", fmt.money(v.salary / 24)],
      ["Monthly (average)", fmt.money(v.salary / 12)],
      ["Daily (5-day week)", fmt.money(v.salary / v.weeks / 5)]
    ];
    var note = "Hourly rate = annual salary ÷ (hours per week × weeks per year). All figures are before taxes.";
    if (v.actualHours > 0 && v.actualHours !== v.hours) {
      var eff = v.salary / (v.actualHours * v.weeks);
      rows.unshift(["Effective rate at " + fmt.num(v.actualHours) + " hrs/week", fmt.money2(eff)]);
      note += " If you regularly work more hours than your schedule says, your effective hourly rate drops.";
    }
    return { primary: { label: "Hourly rate", value: fmt.money2(hourly) }, rows: rows, note: note };
  };

  C["take-home-pay"] = function (v) {
    var data = (window.GSS_TAX || {})[v.taxYear];
    if (!data) return { error: "Tax data for " + v.taxYear + " isn't available yet." };
    var G = v.gross, R = Math.min(v.retirement, G), H = Math.min(v.health, G - R);
    var taxable = Math.max(0, G - R - H - data.standardDeduction[v.status]);
    var fed = bracketTax(taxable, data.brackets[v.status]);
    var ficaWages = Math.max(0, G - H);
    var f = data.fica;
    var ss = Math.min(ficaWages, f.socialSecurityWageBase) * f.socialSecurityRate;
    var med = ficaWages * f.medicareRate;
    var addl = Math.max(0, ficaWages - f.additionalMedicareWithholdingThreshold) * f.additionalMedicareRate;
    var state = Math.max(0, G - R - H) * v.stateRate / 100;
    var net = G - R - H - fed.tax - ss - med - addl - state;
    var p = v.frequency;
    var lines = [
      ["Gross pay", G],
      ["Pre-tax retirement", -R],
      ["Pre-tax health and other", -H],
      ["Federal income tax", -fed.tax],
      ["Social Security", -ss],
      ["Medicare", -med]
    ];
    if (addl > 0) lines.push(["Additional Medicare", -addl]);
    if (v.stateRate > 0) lines.push(["State and local (your rate)", -state]);
    lines.push(["Take-home pay", net]);
    var freqName = { 52: "weekly", 26: "biweekly", 24: "semimonthly", 12: "monthly" }[p] || "per paycheck";
    return {
      primary: { label: "Estimated take-home pay, " + freqName, value: fmt.money2(net / p) },
      rows: [
        ["Annual take-home", fmt.money(Math.round(net))],
        ["Federal taxable income", fmt.money(Math.round(taxable))],
        ["Federal tax bracket (marginal)", fmt.pct(fed.marginal * 100, 0)],
        ["Federal income tax as % of gross", fmt.pct(G ? fed.tax / G * 100 : 0, 1)],
        ["All taxes as % of gross", fmt.pct(G ? (fed.tax + ss + med + addl + state) / G * 100 : 0, 1)]
      ],
      table: {
        caption: "Breakdown, tax year " + v.taxYear,
        head: ["Item", "Per year", "Per paycheck"],
        numCols: [1, 2],
        rows: lines.filter(function (l) { return l[1] !== 0 || l[0] === "Gross pay" || l[0] === "Take-home pay"; })
          .map(function (l) { return [l[0], fmt.money2(l[1]), fmt.money2(l[1] / p)]; })
      },
      note: "Estimate only — not official tax advice. Uses the " + v.taxYear + " standard deduction and federal brackets with no credits or other deductions. Actual withholding depends on your W-4 and your employer's payroll method."
    };
  };

  C["overtime"] = function (v) {
    var regular = v.rate * v.regHours;
    var otRate = v.rate * v.otMult;
    var ot = otRate * v.otHours;
    var dt = v.rate * 2 * v.dtHours;
    var total = regular + ot + dt;
    var rows = [
      ["Regular pay (" + fmt.num(v.regHours) + " hrs)", fmt.money2(regular)],
      ["Overtime rate", fmt.money2(otRate) + "/hr"],
      ["Overtime pay (" + fmt.num(v.otHours) + " hrs)", fmt.money2(ot)]
    ];
    if (v.dtHours > 0) rows.push(["Double-time pay (" + fmt.num(v.dtHours) + " hrs)", fmt.money2(dt)]);
    if (regular > 0 && (ot + dt) > 0) rows.push(["Overtime adds", fmt.pct((ot + dt) / regular * 100, 1) + " to regular pay"]);
    return {
      primary: { label: "Total pay for the week, before taxes", value: fmt.money2(total) },
      rows: rows,
      note: "Under the federal Fair Labor Standards Act, covered nonexempt employees generally earn at least 1.5 times their regular rate for hours over 40 in a workweek. Some states have stricter rules, such as daily overtime."
    };
  };

  C["percentage"] = function (v) {
    var a = v.a, b = v.b;
    if (v.mode === "of") {
      return { primary: { label: fmt.num(a) + "% of " + fmt.num(b) + " is", value: fmt.num(a / 100 * b) },
        note: "Formula: (percent ÷ 100) × number." };
    }
    if (v.mode === "is") {
      if (b === 0) return { error: "The whole can't be zero. Enter the total you're comparing against." };
      return { primary: { label: fmt.num(a) + " is this percent of " + fmt.num(b), value: fmt.pct(a / b * 100, 4) },
        note: "Formula: (part ÷ whole) × 100." };
    }
    if (v.mode === "change") {
      if (a === 0) return { error: "Percent change from zero is undefined. Enter a starting value other than 0." };
      var ch = (b - a) / Math.abs(a) * 100;
      return { primary: { label: "Percent change from " + fmt.num(a) + " to " + fmt.num(b), value: (ch > 0 ? "+" : "") + fmt.pct(ch, 4) },
        rows: [["Difference", fmt.num(b - a)], ["Direction", ch > 0 ? "Increase" : ch < 0 ? "Decrease" : "No change"]],
        note: "Formula: (new − old) ÷ |old| × 100." };
    }
    return { primary: { label: fmt.num(b) + " increased by " + fmt.num(a) + "%", value: fmt.num(b * (1 + a / 100)) },
      rows: [[fmt.num(b) + " decreased by " + fmt.num(a) + "%", fmt.num(b * (1 - a / 100))], [fmt.num(a) + "% of " + fmt.num(b), fmt.num(b * a / 100)]],
      note: "Formula: number × (1 ± percent ÷ 100)." };
  };

  C["discount"] = function (v) {
    var after = v.price * (1 - v.disc / 100) * (1 - v.extra / 100);
    var tax = after * v.tax / 100;
    var eff = (1 - (1 - v.disc / 100) * (1 - v.extra / 100)) * 100;
    var rows = [["You save", fmt.money2(v.price - after)], ["Total discount", fmt.pct(eff, 2)]];
    if (v.tax > 0) rows.push(["Sales tax", fmt.money2(tax)], ["Total with tax", fmt.money2(after + tax)]);
    return {
      primary: { label: "Sale price" + (v.tax > 0 ? " before tax" : ""), value: fmt.money2(after) },
      rows: rows,
      note: v.extra > 0 ? "Stacked discounts multiply rather than add: " + fmt.num(v.disc) + "% off then " + fmt.num(v.extra) + "% off is " + fmt.pct(eff, 2) + " off, not " + fmt.num(v.disc + v.extra) + "%." : "Sale price = original price × (1 − discount ÷ 100)."
    };
  };

  C["pay-raise"] = function (v) {
    var cur = v.current, nw, pct;
    if (v.mode === "percent") { pct = v.raisePct; nw = cur * (1 + pct / 100); }
    else { nw = v.newPay; pct = (nw - cur) / cur * 100; }
    var diff = nw - cur;
    var hourly = v.payType === "hourly";
    var unit = hourly ? "/hr" : "/yr";
    var annualDiff = hourly ? diff * v.hoursYear : diff;
    return {
      primary: { label: "New pay", value: (hourly ? fmt.money2(nw) : fmt.money(nw)) + unit },
      rows: [
        ["Raise amount", (hourly ? fmt.money2(diff) : fmt.money(diff)) + unit],
        ["Raise percentage", fmt.pct(pct, 2)],
        ["Difference per year", fmt.money(annualDiff)],
        ["Difference per month (average)", fmt.money2(annualDiff / 12)],
        ["Difference per biweekly paycheck", fmt.money2(annualDiff / 26)]
      ],
      note: (hourly ? "Yearly figures assume " + fmt.num(v.hoursYear) + " paid hours a year. " : "") + "Amounts are before taxes. A raise only raises the tax rate on the extra dollars, not on your whole paycheck."
    };
  };

  C["profit-margin"] = function (v) {
    var profit = v.price - v.cost;
    var margin = profit / v.price * 100;
    var rows = [[profit >= 0 ? "Gross profit" : "Loss", fmt.money2(profit)]];
    rows.push(["Markup on cost", v.cost > 0 ? fmt.pct(profit / v.cost * 100, 2) : "—"]);
    if (v.qty > 1) rows.push(["Profit on " + fmt.num(v.qty) + " units", fmt.money2(profit * v.qty)], ["Revenue on " + fmt.num(v.qty) + " units", fmt.money2(v.price * v.qty)]);
    return {
      primary: { label: "Profit margin", value: fmt.pct(margin, 2) },
      rows: rows,
      note: "Margin = (price − cost) ÷ price. Markup = (price − cost) ÷ cost. Same dollars, different base." + (profit < 0 ? " A negative margin means you're selling below cost." : "")
    };
  };

  C["markup"] = function (v) {
    var price;
    if (v.mode === "markup") price = v.cost * (1 + v.pct / 100);
    else {
      if (v.pct >= 100) return { error: "A margin must be below 100%. At 100% the cost would have to be zero." };
      price = v.cost / (1 - v.pct / 100);
    }
    var profit = price - v.cost;
    return {
      primary: { label: "Selling price", value: fmt.money2(price) },
      rows: [
        ["Profit per item", fmt.money2(profit)],
        ["Markup on cost", v.cost > 0 ? fmt.pct(profit / v.cost * 100, 2) : "—"],
        ["Profit margin on price", price > 0 ? fmt.pct(profit / price * 100, 2) : "—"]
      ],
      note: v.mode === "markup" ? "Price = cost × (1 + markup ÷ 100)." : "Price = cost ÷ (1 − margin ÷ 100). A 50% margin needs a 100% markup."
    };
  };

  C["break-even"] = function (v) {
    var cm = v.price - v.varCost;
    if (cm <= 0) return { error: "Your price must be higher than the variable cost per unit, or every sale loses money and there is no break-even point." };
    var units = (v.fixed + v.target) / cm;
    var whole = Math.ceil(units - 1e-9);
    return {
      primary: { label: v.target > 0 ? "Units to sell to reach your profit target" : "Break-even point", value: fmt.num(whole, 0) + " units" },
      rows: [
        ["Sales revenue needed", fmt.money2(whole * v.price)],
        ["Contribution margin per unit", fmt.money2(cm)],
        ["Contribution margin ratio", fmt.pct(cm / v.price * 100, 2)],
        ["Exact (unrounded) units", fmt.num(units, 2)]
      ],
      note: "Break-even units = (fixed costs" + (v.target > 0 ? " + target profit" : "") + ") ÷ (price − variable cost per unit), rounded up to a whole unit. Use the same time period for fixed costs and sales."
    };
  };

  C["budget"] = function (v) {
    var cats = [
      ["Housing", v.housing, "need"], ["Utilities and phone", v.utilities, "need"], ["Groceries", v.groceries, "need"],
      ["Transportation", v.transport, "need"], ["Insurance and health", v.insurance, "need"], ["Debt payments", v.debt, "need"],
      ["Savings", v.savings, "save"], ["Everything else", v.other, "want"]
    ];
    var total = 0, needs = 0, wants = 0, save = 0;
    cats.forEach(function (c) { total += c[1]; if (c[2] === "need") needs += c[1]; else if (c[2] === "want") wants += c[1]; else save += c[1]; });
    var left = v.income - total;
    var pct = function (x) { return v.income > 0 ? fmt.pct(x / v.income * 100, 1) : "—"; };
    return {
      primary: { label: left >= 0 ? "Left over each month" : "Over budget each month", value: fmt.money2(Math.abs(left)) },
      rows: [["Total planned spending", fmt.money2(total)], ["Monthly take-home income", fmt.money2(v.income)]],
      table: {
        caption: "Where your money goes",
        head: ["Category", "Amount", "% of income"], numCols: [1, 2],
        rows: cats.map(function (c) { return [c[0], fmt.money2(c[1]), pct(c[1])]; })
      },
      note: "50/30/20 check — needs: " + pct(needs) + " (guideline 50%), wants: " + pct(wants) + " (guideline 30%), savings: " + pct(save) + " (guideline 20%). The 50/30/20 split is a rule of thumb, not a requirement."
    };
  };

  C["savings-goal"] = function (v) {
    var n = Math.round(v.months), i = v.rate / 100 / 12;
    var grown = v.current * Math.pow(1 + i, n);
    var remaining = v.goal - grown;
    if (remaining <= 0) {
      return { primary: { label: "Monthly savings needed", value: "$0" },
        rows: [["Projected balance", fmt.money2(grown)]],
        note: "Your current savings are projected to reach the goal on their own at the return you entered." };
    }
    var monthly = i > 0 ? remaining * i / (Math.pow(1 + i, n) - 1) : remaining / n;
    var contributed = monthly * n;
    return {
      primary: { label: "Save each month", value: fmt.money2(monthly) },
      rows: [
        ["Per week (average)", fmt.money2(monthly * 12 / 52)],
        ["Per biweekly paycheck", fmt.money2(monthly * 12 / 26)],
        ["Total you'll put in", fmt.money2(contributed + v.current)],
        ["Growth from returns", fmt.money2(v.goal - contributed - v.current)]
      ],
      note: "Assumes deposits at the end of each month" + (v.rate > 0 ? " and a steady " + fmt.num(v.rate) + "% annual return compounded monthly. Real returns vary." : " and no interest.")
    };
  };

  function payoff(balance, apr, payment) {
    var i = apr / 100 / 12, bal = balance, months = 0, interest = 0;
    if (payment <= bal * i) return null;
    while (bal > 0.005 && months < 1200) {
      var int = bal * i;
      interest += int;
      bal = bal + int - payment;
      months++;
    }
    var lastOver = bal < 0 ? -bal : 0;
    return { months: months, interest: interest, total: balance + interest, lastOver: lastOver };
  }
  C["debt-payoff"] = function (v) {
    var pay = v.payment + v.extra;
    var monthlyInterest = v.balance * v.apr / 100 / 12;
    var r = payoff(v.balance, v.apr, pay);
    if (!r) return { error: "That payment doesn't cover the monthly interest (" + fmt.money2(monthlyInterest) + "), so the balance would never go down. Enter a larger payment." };
    var end = new Date(); end.setMonth(end.getMonth() + r.months);
    var rows = [
      ["Debt-free by", end.toLocaleDateString("en-US", { month: "long", year: "numeric" })],
      ["Total interest", fmt.money2(r.interest)],
      ["Total paid", fmt.money2(r.total)]
    ];
    var note = "Assumes a fixed APR, the same payment every month, and no new charges.";
    if (v.extra > 0) {
      var base = payoff(v.balance, v.apr, v.payment);
      if (base) {
        rows.push(["Without the extra payment", fmt.duration(base.months)], ["Interest saved by paying extra", fmt.money2(base.interest - r.interest)]);
      } else {
        rows.push(["Without the extra payment", "Never paid off"]);
      }
    }
    return { primary: { label: "Time to pay off", value: fmt.duration(r.months) }, rows: rows, note: note };
  };

  C["debt-to-income"] = function (v) {
    var debts = v.housing + v.car + v.student + v.cards + v.personal + v.otherDebt;
    var dti = debts / v.income * 100;
    return {
      primary: { label: "Debt-to-income ratio", value: fmt.pct(dti, 1) },
      rows: [
        ["Total monthly debt payments", fmt.money2(debts)],
        ["Gross monthly income", fmt.money2(v.income)],
        ["Housing ratio (rent or mortgage only)", fmt.pct(v.housing / v.income * 100, 1)],
        ["Debt payments excluding housing", fmt.money2(debts - v.housing)],
        ["Income left after debt payments (before taxes)", fmt.money2(v.income - debts)]
      ],
      note: "DTI = monthly debt payments ÷ gross monthly income. Different loan products and lenders set different DTI limits, so ask the lender what they use."
    };
  };

  C["simple-interest"] = function (v) {
    var years = v.unit === "years" ? v.time : v.unit === "months" ? v.time / 12 : v.time / 365;
    var interest = v.principal * v.rate / 100 * years;
    return {
      primary: { label: "Interest earned or owed", value: fmt.money2(interest) },
      rows: [["Total (principal + interest)", fmt.money2(v.principal + interest)], ["Time in years", fmt.num(years, 4)]],
      note: "Simple interest = principal × annual rate × time in years. Interest is not added to the balance, so it doesn't compound." + (v.unit === "days" ? " Days are converted using a 365-day year." : "")
    };
  };

  C["compound-interest"] = function (v) {
    var r = v.rate / 100, n = +v.compound;
    var m = Math.pow(1 + r / n, n / 12) - 1;
    var bal = v.principal, contrib = v.principal, rows = [];
    var months = Math.round(v.years * 12);
    for (var k = 1; k <= months; k++) {
      bal = bal * (1 + m) + v.monthly;
      contrib += v.monthly;
      if (k % 12 === 0 || k === months) rows.push([k % 12 === 0 ? String(k / 12) : fmt.num(k / 12, 2), fmt.money0(contrib), fmt.money0(bal - contrib), fmt.money0(bal)]);
    }
    return {
      primary: { label: "Balance after " + fmt.num(v.years) + " years", value: fmt.money2(bal) },
      rows: [["Total contributions", fmt.money2(contrib)], ["Interest earned", fmt.money2(bal - contrib)]],
      table: rows.length > 1 ? { caption: "Year by year", head: ["Year", "Put in", "Interest", "Balance"], numCols: [1, 2, 3], rows: rows } : null,
      note: "Assumes a steady " + fmt.num(v.rate) + "% annual rate, compounded " + ({ 1: "yearly", 4: "quarterly", 12: "monthly", 365: "daily" }[n]) + ", with monthly deposits at the end of each month. Real investment returns go up and down."
    };
  };

  C["age"] = function (v) {
    var b = parseDate(v.birth), a = parseDate(v.asof);
    if (!b) return { error: "Enter a valid date of birth." };
    if (!a) return { error: "Enter a valid 'age on' date." };
    if (a < b) return { error: "The 'age on' date is before the date of birth." };
    var d = ymdDiff(b, a);
    var days = Math.round((a - b) / DAY);
    var ny = a.getUTCFullYear(), bm = b.getUTCMonth(), bd = b.getUTCDate();
    function bday(y) { return new Date(Date.UTC(y, bm, Math.min(bd, daysInMonth(y, bm)))); }
    var next = bday(ny);
    if (next <= a) next = bday(ny + 1);
    var until = Math.round((next - a) / DAY);
    return {
      primary: { label: "Age", value: fmt.plural(d.y, "year") },
      rows: [
        ["Exact age", fmt.plural(d.y, "year") + ", " + fmt.plural(d.m, "month") + ", " + fmt.plural(d.d, "day")],
        ["Total months", fmt.num(d.y * 12 + d.m, 0)],
        ["Total weeks", fmt.num(Math.floor(days / 7), 0)],
        ["Total days", fmt.num(days, 0)],
        ["Next birthday", fmt.date(next) + " (" + fmt.plural(until, "day") + ")"]
      ],
      note: "February 29 birthdays are counted on February 28 in non-leap years."
    };
  };

  C["date-difference"] = function (v) {
    var a = parseDate(v.start), b = parseDate(v.end);
    if (!a || !b) return { error: "Enter both dates." };
    var swapped = false;
    if (b < a) { var t = a; a = b; b = t; swapped = true; }
    var days = Math.round((b - a) / DAY) + (v.inclusive ? 1 : 0);
    var d = ymdDiff(a, b);
    var biz = 0, cur = new Date(a.getTime()), stop = b.getTime() + (v.inclusive ? DAY : 0);
    while (cur.getTime() < stop) { var wd = cur.getUTCDay(); if (wd !== 0 && wd !== 6) biz++; cur = new Date(cur.getTime() + DAY); }
    return {
      primary: { label: "Days between the dates", value: fmt.plural(days, "day") },
      rows: [
        ["Weeks and days", fmt.plural(Math.floor(days / 7), "week") + ", " + fmt.plural(days % 7, "day")],
        ["Years, months, days", fmt.plural(d.y, "year") + ", " + fmt.plural(d.m, "month") + ", " + fmt.plural(d.d, "day")],
        ["Weekdays (Mon–Fri)", fmt.num(biz, 0)]
      ],
      note: (v.inclusive ? "Counts both the start and end date. " : "Counts from the start date up to, but not including, the end date. ") +
        "Weekday count doesn't skip holidays." + (swapped ? " The end date was earlier, so the dates were swapped." : "")
    };
  };

  C["time-duration"] = function (v) {
    var re = /^(\d{1,2}):(\d{2})/;
    var s = re.exec(v.start), e = re.exec(v.end);
    if (!s || !e) return { error: "Enter a start and end time." };
    var sm = +s[1] * 60 + +s[2], em = +e[1] * 60 + +e[2];
    var overnight = em <= sm;
    var mins = (overnight ? em + 1440 : em) - sm - v.breakMin;
    if (mins < 0) return { error: "The break is longer than the time worked." };
    var h = Math.floor(mins / 60), m = mins % 60;
    var rows = [["Decimal hours", fmt.num(mins / 60, 2)], ["Total minutes", fmt.num(mins, 0)]];
    if (v.rate > 0) rows.push(["Pay at " + fmt.money2(v.rate) + "/hr", fmt.money2(mins / 60 * v.rate)]);
    return {
      primary: { label: "Time worked", value: h + " hr " + m + " min" },
      rows: rows,
      note: (overnight ? "The end time is earlier than the start time, so it's treated as the next day. " : "") +
        (v.breakMin > 0 ? fmt.num(v.breakMin) + " minutes of break time subtracted. " : "") +
        "Decimal hours are what most timesheets and payroll systems use."
    };
  };

  C["unit-converter"] = function (v) {
    var cat = UNITS[v.category];
    if (!cat[v.from] || !cat[v.to]) return { error: "Choose units to convert between." };
    if (v.category === "temperature" && v.from === "k" && v.value < 0) return { error: "Kelvin can't be negative." };
    var out = convert(v.category, v.value, v.from, v.to);
    var rows = Object.keys(cat).filter(function (k) { return k !== v.from && k !== v.to; })
      .map(function (k) { return [cat[k][0], fmt.num(convert(v.category, v.value, v.from, k), 6)]; });
    return {
      primary: { label: fmt.num(v.value) + " " + cat[v.from][0].toLowerCase() + " =", value: fmt.num(out, 6) + " " + cat[v.to][0].toLowerCase() },
      table: { caption: "Same amount in other units", head: ["Unit", "Value"], numCols: [1], rows: rows },
      note: "US customary units are used for cups, pints, quarts, gallons, and fluid ounces."
    };
  };

  C["tip"] = function (v) {
    var tip = v.bill * v.pct / 100;
    var total = v.bill + tip;
    var per = total / v.people;
    var rows = [["Tip", fmt.money2(tip)], ["Total with tip", fmt.money2(total)]];
    if (v.people > 1) {
      if (v.roundUp) { var up = Math.ceil(per); rows.push(["Each person pays (rounded up)", fmt.money2(up)], ["Extra tip from rounding", fmt.money2(up * v.people - total)]); }
      rows.push(["Tip per person", fmt.money2(tip / v.people)]);
    }
    return {
      primary: { label: v.people > 1 ? "Each person pays" : "Total with tip", value: fmt.money2(v.people > 1 ? per : total) },
      rows: rows,
      note: "Tip = bill × tip percent. Many people tip on the pre-tax amount; enter whichever total you prefer."
    };
  };


  /* ---------- Taxes ---------- */
  C["tax-bracket"] = function (v) {
    var data = (window.GSS_TAX || {})[v.taxYear];
    if (!data) return { error: "Tax data for " + v.taxYear + " isn't available yet." };
    var taxable = v.incomeType === "gross" ? Math.max(0, v.income - data.standardDeduction[v.status]) : v.income;
    var r = bracketTax(taxable, data.brackets[v.status]);
    var base = v.income;
    var rows = [
      ["Taxable income", fmt.money2(taxable)],
      ["Federal income tax", fmt.money2(r.tax)],
      ["Effective rate on " + (v.incomeType === "gross" ? "total" : "taxable") + " income", base > 0 ? fmt.pct(r.tax / base * 100, 2) : "0%"],
      ["Income after federal income tax", fmt.money2(base - r.tax)]
    ];
    if (v.incomeType === "gross") rows.unshift(["Standard deduction", fmt.money2(data.standardDeduction[v.status])]);
    var brackets = data.brackets[v.status];
    var table = r.rows.map(function (b, i) {
      var lo = brackets[i][0], hi = i + 1 < brackets.length ? brackets[i + 1][0] : null;
      return [fmt.pct(b.rate * 100, 0) + " on " + fmt.money0(lo) + (hi ? "–" + fmt.money0(hi) : "+"), fmt.money2(b.amount), fmt.money2(b.tax)];
    });
    return {
      primary: { label: "Your federal tax bracket (marginal rate)", value: fmt.pct(r.marginal * 100, 0) },
      rows: rows,
      table: table.length ? { caption: "Tax in each bracket, " + v.taxYear, head: ["Bracket", "Income taxed", "Tax"], numCols: [1, 2], rows: table } : null,
      note: "Estimate only — not official tax advice. Uses " + v.taxYear + " federal brackets with no credits, itemized deductions, or special rates."
    };
  };

  C["self-employment-tax"] = function (v) {
    var data = (window.GSS_TAX || {})[v.taxYear];
    if (!data) return { error: "Tax data for " + v.taxYear + " isn't available yet." };
    var se = data.selfEmployment, base = data.fica.socialSecurityWageBase;
    var net = v.profit * se.netEarningsFactor;
    if (net < 400) {
      return { primary: { label: "Estimated self-employment tax", value: "$0" },
        rows: [["Net earnings from self-employment", fmt.money2(net)]],
        note: "No self-employment tax is due when net earnings are under $400. Income tax may still apply." };
    }
    var ssRoom = Math.max(0, base - v.wages);
    var ss = Math.min(net, ssRoom) * se.socialSecurityRate;
    var med = net * se.medicareRate;
    var total = ss + med;
    return {
      primary: { label: "Estimated self-employment tax", value: fmt.money2(total) },
      rows: [
        ["Net earnings (profit × 92.35%)", fmt.money2(net)],
        ["Social Security portion (12.4%)", fmt.money2(ss)],
        ["Medicare portion (2.9%)", fmt.money2(med)],
        ["Deductible half of SE tax", fmt.money2(total / 2)],
        ["Set aside per quarter for SE tax", fmt.money2(total / 4)]
      ],
      note: "Estimate only — not official tax advice. Covers self-employment tax only, not income tax on the same profit or the Additional Medicare Tax." +
        (v.wages > 0 ? " Your W-2 wages use up part of the " + fmt.money0(base) + " Social Security wage base first." : "")
    };
  };

  /* ---------- Mindset ---------- */
  function todayUTC() { return parseDate(todayISO()); }
  C["goal-breakdown"] = function (v) {
    var end = parseDate(v.deadline);
    if (!end) return { error: "Enter a deadline date." };
    var now = todayUTC();
    var days = Math.round((end - now) / DAY);
    if (days <= 0) return { error: "Pick a deadline after today." };
    var left = v.goal - v.done;
    var unit = (v.unit || "").trim();
    var u = function (x, d) { return fmt.num(x, d === undefined ? 2 : d) + (unit ? " " + unit : ""); };
    if (left <= 0) return { primary: { label: "Goal reached", value: "100%" }, note: "You've already met this goal. Time to set the next one." };
    var workDays = days * v.days / 7;
    var perDay = left / workDays;
    return {
      primary: { label: "Do this much each week", value: u(perDay * v.days) },
      rows: [
        ["Per " + (v.days < 7 ? "working " : "") + "day", u(perDay)],
        ["Per month (average)", u(left / days * 30.44)],
        ["Still to go", u(left)],
        ["Progress so far", fmt.pct(v.done / v.goal * 100, 1)],
        ["Days until the deadline", fmt.num(days, 0) + " (" + fmt.num(days / 7, 1) + " weeks)"]
      ],
      note: "Assumes steady progress " + (v.days < 7 ? v.days + " days a week" : "every day") + " from today until " + fmt.date(end) + "."
    };
  };

  C["habit-consistency"] = function (v) {
    var start = parseDate(v.start);
    if (!start) return { error: "Enter the day you started." };
    var now = todayUTC();
    var elapsed = Math.round((now - start) / DAY) + 1;
    if (elapsed < 1) return { error: "The start date is in the future." };
    if (v.completed > elapsed) return { error: "That's more days than have passed since you started (" + elapsed + "). Check the start date." };
    var pct = v.completed / elapsed * 100;
    var remaining = Math.max(0, v.target - v.completed);
    var rows = [
      ["Days since you started (including today)", fmt.num(elapsed, 0)],
      ["Days missed", fmt.num(elapsed - v.completed, 0)],
      ["Days left to reach " + fmt.num(v.target, 0), fmt.num(remaining, 0)]
    ];
    if (remaining > 0) rows.push(["Earliest date to reach your target", fmt.date(new Date(now.getTime() + remaining * DAY))]);
    return {
      primary: { label: "Consistency", value: fmt.pct(pct, 1) },
      rows: rows,
      note: remaining === 0 ? "You've reached your target. Consider setting a new one." : "The earliest date assumes you do the habit every day starting tomorrow."
    };
  };

  C["time-allocation"] = function (v) {
    var items = [
      ["Sleep", v.sleep * 7], ["Work", v.work], ["Commuting", v.commuteMin * v.workdays / 60],
      ["Chores and errands", v.chores], ["Family and caregiving", v.family], ["Meals and personal care", v.selfcare * 7], ["Other commitments", v.other]
    ];
    var used = items.reduce(function (a, b) { return a + b[1]; }, 0);
    var free = 168 - used;
    if (free < 0) return { error: "These add up to " + fmt.num(used, 1) + " hours, more than the 168 hours in a week. Check your entries." };
    items.push(["Free time", free]);
    return {
      primary: { label: "Free time each week", value: fmt.num(free, 1) + " hours" },
      rows: [["Free time per day (average)", fmt.num(free / 7, 1) + " hours"], ["Committed time per week", fmt.num(used, 1) + " hours"]],
      table: { caption: "Your 168-hour week", head: ["Activity", "Hours per week", "Share of week"], numCols: [1, 2],
        rows: items.map(function (i) { return [i[0], fmt.num(i[1], 1), fmt.pct(i[1] / 168 * 100, 1)]; }) },
      note: "A week has 168 hours. Daily amounts are multiplied by 7, and commuting by your workdays."
    };
  };

  /* ---------- Faith & Scripture ---------- */
  function bibleBooks() { return (window.GSS_BIBLE || { books: [] }).books; }
  var SCOPES = {
    bible: function (b) { return true; }, ot: function (b) { return b[2] === "OT"; }, nt: function (b) { return b[2] === "NT"; },
    gospels: function (b) { return b[3] === "Gospels"; }, psalms: function (b) { return b[0] === "Psalms"; }, proverbs: function (b) { return b[0] === "Proverbs"; }
  };
  function chapterList(scope) {
    var out = [];
    bibleBooks().filter(SCOPES[scope]).forEach(function (b) { for (var c = 1; c <= b[1]; c++) out.push([b[0], c]); });
    return out;
  }
  function rangeLabel(list, a, b) {
    var s = list[a], e = list[b];
    if (s[0] === e[0]) return s[0] + " " + s[1] + (e[1] !== s[1] ? "–" + e[1] : "");
    return s[0] + " " + s[1] + " – " + e[0] + " " + e[1];
  }
  C["bible-reading-plan"] = function (v) {
    var list = chapterList(v.scope), n = list.length;
    if (!n) return { error: "Bible data didn't load. Refresh the page and try again." };
    var start = parseDate(v.start);
    if (!start) return { error: "Enter a start date." };
    var days = v.mode === "days" ? Math.round(v.days) : Math.ceil(n / v.perDay - 1e-9);
    days = Math.max(1, Math.min(days, n));
    var end = new Date(start.getTime() + (days - 1) * DAY);
    var weekly = days > 120;
    var rows = [], i, a, b;
    if (!weekly) {
      for (i = 0; i < days; i++) {
        a = Math.round(i * n / days); b = Math.round((i + 1) * n / days) - 1;
        var d = new Date(start.getTime() + i * DAY);
        rows.push(["Day " + (i + 1), d.toLocaleDateString("en-US", { weekday: "short", month: "short", day: "numeric", timeZone: "UTC" }), rangeLabel(list, a, b)]);
      }
    } else {
      var weeks = Math.ceil(days / 7);
      for (i = 0; i < weeks; i++) {
        var d0 = i * 7, d1 = Math.min(days, d0 + 7) - 1;
        a = Math.round(d0 * n / days); b = Math.round((d1 + 1) * n / days) - 1;
        var ws = new Date(start.getTime() + d0 * DAY);
        rows.push(["Week " + (i + 1), ws.toLocaleDateString("en-US", { month: "short", day: "numeric", timeZone: "UTC" }), rangeLabel(list, a, b)]);
      }
    }
    return {
      primary: { label: "Read about this much each day", value: fmt.num(n / days, 1) + (Math.round(n / days * 10) === 10 ? " chapter" : " chapters") },
      rows: [["Total chapters", fmt.num(n, 0)], ["Days", fmt.num(days, 0)], ["Finish date", fmt.date(end)]],
      table: { caption: "Reading schedule", head: [weekly ? "Week" : "Day", weekly ? "Starts" : "Date", "Read"], numCols: [], rows: rows },
      note: (weekly ? "Shown week by week; split each week's reading across its days. " : "") + "Chapters follow the 66-book Protestant canon in traditional order."
    };
  };

  C["bible-book-overview"] = function (v) {
    var books = bibleBooks(), idx = -1;
    books.forEach(function (b, i) { if (b[0] === v.book) idx = i; });
    if (idx < 0) return { error: "Choose a book." };
    var b = books[idx];
    var sameSection = books.filter(function (x) { return x[3] === b[3] && x[2] === b[2]; });
    var pos = sameSection.map(function (x) { return x[0]; }).indexOf(b[0]) + 1;
    var tChapters = books.filter(function (x) { return x[2] === b[2]; }).reduce(function (a, x) { return a + x[1]; }, 0);
    var days = Math.ceil(b[1] / v.perDay - 1e-9);
    return {
      primary: { label: b[0], value: fmt.plural(b[1], "chapter") },
      rows: [
        ["Testament", b[2] === "OT" ? "Old Testament" : "New Testament"],
        ["Section", b[3] + " (book " + pos + " of " + sameSection.length + ")"],
        ["Order in the Bible", "Book " + (idx + 1) + " of 66"],
        ["Share of its testament", fmt.pct(b[1] / tChapters * 100, 1) + " of chapters"],
        ["Reading time at " + fmt.num(v.perDay) + " chapters a day", fmt.plural(days, "day")],
        ["Comes before and after", (idx > 0 ? books[idx - 1][0] : "—") + " / " + (idx < 65 ? books[idx + 1][0] : "—")]
      ],
      note: "Sections follow a common Protestant arrangement. Other traditions group or include some books differently."
    };
  };

  C["scripture-memory"] = function (v) {
    var start = parseDate(v.start);
    if (!start) return { error: "Enter a start date." };
    var weeks = Math.ceil(v.verses / v.perWeek);
    var end = new Date(start.getTime() + (weeks * 7 - 1) * DAY);
    var rows = [];
    for (var w = 0; w < weeks; w++) {
      var a = w * v.perWeek + 1, b = Math.min(v.verses, (w + 1) * v.perWeek);
      var d = new Date(start.getTime() + w * 7 * DAY);
      rows.push(["Week " + (w + 1), d.toLocaleDateString("en-US", { month: "short", day: "numeric", timeZone: "UTC" }),
        "Learn " + (a === b ? "verse " + a : "verses " + a + "–" + b), a > 1 ? "Review 1–" + (a - 1) : "—"]);
    }
    var label = (v.passage || "").trim();
    return {
      primary: { label: (label ? label + ": " : "") + "time to memorize", value: fmt.plural(weeks, "week") },
      rows: [["Verses", fmt.num(v.verses, 0)], ["New verses per week", fmt.num(v.perWeek, 0)], ["About per day", fmt.num(v.perWeek / 7, 2) + " verses"], ["Finish date", fmt.date(end)]],
      table: { caption: "Week-by-week plan", head: ["Week", "Starts", "New", "Review"], numCols: [], rows: rows.slice(0, 104) },
      note: weeks > 104 ? "Showing the first two years of the plan." : "Learn the new verses early in the week and review the rest each day."
    };
  };


  /* ---------- World English Bible (public domain) ---------- */
  var WEB_NOTE = "Scripture quotations are from the World English Bible (WEB), which is in the public domain.";
  var bookCache = {};
  function loadBook(i) {
    if (!bookCache[i]) {
      var files = (window.GSS_BIBLE || {}).files || [];
      bookCache[i] = fetch((window.GSS_BASE || "/") + "data/web/" + files[i] + ".json")
        .then(function (r) { if (!r.ok) throw new Error("load"); return r.json(); });
    }
    return bookCache[i];
  }
  var NUM_WORDS = { first: "1", second: "2", third: "3", i: "1", ii: "2", iii: "3", "1st": "1", "2nd": "2", "3rd": "3" };
  var ALIASES = { psalm: "psalms", ps: "psalms", psa: "psalms", song: "song of songs", songofsolomon: "song of songs", canticles: "song of songs",
    jn: "john", jhn: "john", mt: "matthew", mk: "mark", lk: "luke", rev: "revelation", revelations: "revelation", phil: "philippians",
    php: "philippians", philem: "philemon", phm: "philemon", jas: "james", jude: "jude", judg: "judges", jdg: "judges" };
  function findBook(raw) {
    var books = bibleBooks();
    var t = raw.toLowerCase().replace(/\./g, " ").trim().split(/\s+/);
    if (t.length > 1 && NUM_WORDS[t[0]]) t[0] = NUM_WORDS[t[0]];
    var key = t.join(" ").replace(/^(\d)\s*/, "$1 ");
    var flat = key.replace(/\s/g, "");
    if (ALIASES[flat]) key = ALIASES[flat];
    else if (ALIASES[key]) key = ALIASES[key];
    var norm = function (n) { return n.toLowerCase().replace(/\s/g, ""); };
    var k = norm(key);
    for (var i = 0; i < books.length; i++) if (norm(books[i][0]) === k) return i;
    if (k.length >= 2) for (i = 0; i < books.length; i++) if (norm(books[i][0]).indexOf(k) === 0) return i;
    return -1;
  }
  // Parses "John 3:16", "John 3:16-18", "Psalm 23", "Gen 1:1-2:3", "1 Cor 13:4-7"
  function parseRef(str) {
    var m = /^\s*((?:[1-3]|i{1,3}|first|second|third|1st|2nd|3rd)?\s*[a-z][a-z .]*?)\s*(\d+)(?::(\d+))?(?:\s*[-–]\s*(\d+)(?::(\d+))?)?\s*$/i.exec(str);
    if (!m) return { error: "“" + str.trim() + "” isn't a reference I recognize. Try a format like John 3:16 or Psalm 23." };
    var bi = findBook(m[1]);
    if (bi < 0) return { error: "No book named “" + m[1].trim() + "”. Check the spelling." };
    var b = bibleBooks()[bi];
    var c1 = +m[2], v1 = m[3] ? +m[3] : 1, c2 = c1, v2 = m[3] ? +m[3] : 999;
    if (m[4] && m[5]) { c2 = +m[4]; v2 = +m[5]; }
    else if (m[4]) { if (m[3]) v2 = +m[4]; else { c2 = +m[4]; v2 = 999; } }
    if (c1 < 1 || c1 > b[1]) return { error: b[0] + " has " + fmt.plural(b[1], "chapter") + "." };
    if (c2 < c1 || c2 > b[1]) return { error: "Check the chapter range for " + b[0] + "." };
    return { book: bi, c1: c1, v1: v1, c2: c2, v2: v2 };
  }
  function versesFor(ref, data) {
    var out = [];
    for (var c = ref.c1; c <= ref.c2; c++) {
      var ch = data[c - 1] || [];
      var from = c === ref.c1 ? ref.v1 : 1, to = c === ref.c2 ? Math.min(ref.v2, ch.length) : ch.length;
      for (var v = from; v <= to; v++) out.push([c, v, ch[v - 1]]);
    }
    return out;
  }
  function oneName(n) { return n === "Psalms" ? "Psalm" : n; }
  function refLabel(ref, verses) {
    var name = oneName(bibleBooks()[ref.book][0]);
    if (!verses.length) return name;
    var a = verses[0], z = verses[verses.length - 1];
    if (a[0] === z[0]) return name + " " + a[0] + ":" + a[1] + (z[1] !== a[1] ? "–" + z[1] : "");
    return name + " " + a[0] + ":" + a[1] + "–" + z[0] + ":" + z[1];
  }
  function passageHTML(label, verses) {
    return '<div class="passage"><h3>' + esc(label) + '</h3><p>' + verses.map(function (x) {
      return '<sup class="vnum">' + (x[1] === 1 && verses.length > 1 ? x[0] + ":" : "") + x[1] + "</sup>" + esc(x[2]);
    }).join(" ") + "</p></div>";
  }
  function getPassages(refStr, maxRefs) {
    var parts = refStr.split(/[;\n]+/).map(function (x) { return x.trim(); }).filter(Boolean).slice(0, maxRefs || 10);
    var parsed = parts.map(parseRef);
    var bad = parsed.filter(function (p) { return p.error; })[0];
    if (bad) return Promise.resolve({ error: bad.error });
    return Promise.all(parsed.map(function (p) { return loadBook(p.book); })).then(function (datas) {
      return parsed.map(function (p, i) { var vs = versesFor(p, datas[i]); return { label: refLabel(p, vs), verses: vs, ref: p }; });
    });
  }

  C["scripture-lookup"] = function (v) {
    if (!v.ref.trim()) return { error: "Enter a reference, like John 3:16." };
    return getPassages(v.ref, 10).then(function (res) {
      if (res.error) return res;
      var empty = res.filter(function (r) { return !r.verses.length; })[0];
      if (empty) return { error: "That verse number is past the end of the chapter. Check the reference." };
      var count = res.reduce(function (a, r) { return a + r.verses.length; }, 0);
      return {
        primary: { label: "Showing", value: res.map(function (r) { return r.label; }).join("; ") },
        html: res.map(function (r) { return passageHTML(r.label, r.verses); }).join(""),
        note: fmt.plural(count, "verse") + ". " + WEB_NOTE
      };
    });
  };

  var TOPICS = {
    faith: ["Hebrews 11:1", "Hebrews 11:6", "Romans 10:17", "2 Corinthians 5:7", "Ephesians 2:8-9", "Mark 11:22-24"],
    hope: ["Romans 15:13", "Isaiah 40:31", "Lamentations 3:22-23", "Hebrews 6:19", "1 Peter 1:3", "Psalm 42:11"],
    perseverance: ["James 1:2-4", "Romans 5:3-5", "Galatians 6:9", "Hebrews 12:1-2", "2 Corinthians 4:16-18", "Philippians 3:13-14"],
    wisdom: ["James 1:5", "Proverbs 3:5-6", "Proverbs 9:10", "Proverbs 4:7", "Psalm 90:12", "Colossians 3:16"],
    stewardship: ["1 Peter 4:10", "Luke 16:10-11", "Matthew 25:21", "1 Corinthians 4:2", "Psalm 24:1", "Genesis 2:15"],
    work: ["Colossians 3:23-24", "Proverbs 14:23", "Proverbs 16:3", "Ecclesiastes 9:10", "Proverbs 22:29", "2 Thessalonians 3:10"],
    money: ["Hebrews 13:5", "1 Timothy 6:10", "Matthew 6:19-21", "Proverbs 22:7", "Proverbs 13:11", "Luke 14:28"],
    family: ["Joshua 24:15", "Exodus 20:12", "Deuteronomy 6:6-7", "Psalm 127:3", "Ephesians 6:1-4", "1 Timothy 5:8"],
    forgiveness: ["Ephesians 4:32", "Colossians 3:13", "Matthew 6:14-15", "Matthew 18:21-22", "1 John 1:9", "Psalm 103:12"],
    purpose: ["Jeremiah 29:11", "Romans 8:28", "Ephesians 2:10", "Proverbs 19:21", "Philippians 1:6", "Ecclesiastes 3:1"],
    peace: ["Philippians 4:6-7", "John 14:27", "Isaiah 26:3", "Matthew 6:34", "1 Peter 5:7", "Psalm 4:8"],
    strength: ["Isaiah 41:10", "Philippians 4:13", "2 Corinthians 12:9", "Psalm 46:1", "Joshua 1:9", "Nehemiah 8:10"],
    love: ["1 Corinthians 13:4-7", "John 13:34-35", "1 John 4:7-8", "Romans 8:38-39", "John 15:13"],
    gratitude: ["1 Thessalonians 5:16-18", "Psalm 107:1", "Colossians 3:17", "Psalm 100:4", "Philippians 4:11-12"]
  };
  window.GSS_TOPICS = TOPICS;
  C["scripture-topics"] = function (v) {
    var refs = TOPICS[v.topic];
    if (!refs) return { error: "Choose a topic." };
    return getPassages(refs.join(";"), 20).then(function (res) {
      if (res.error) return res;
      return {
        primary: { label: "Verses on", value: v.topic.charAt(0).toUpperCase() + v.topic.slice(1) },
        html: res.map(function (r) { return passageHTML(r.label, r.verses); }).join(""),
        note: "A starting list of passages often read on this topic, not a complete or official list. Read each in context. " + WEB_NOTE
      };
    });
  };

  function normText(t) { return t.toLowerCase().replace(/[’‘]/g, "'").replace(/[“”]/g, '"'); }
  C["bible-verse-finder"] = function (v) {
    var q = normText(v.q.trim());
    if (q.length < 2) return { error: "Enter a word or phrase to search for." };
    var books = bibleBooks(), idxs = [];
    books.forEach(function (b, i) { if (SCOPES[v.scope](b)) idxs.push(i); });
    var words = q.replace(/["']/g, function (c) { return c; }).split(/\s+/).filter(Boolean);
    var re = v.match === "phrase"
      ? [new RegExp("\\b" + q.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "i")]
      : words.map(function (w) { return new RegExp("\\b" + w.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "i"); });
    return Promise.all(idxs.map(loadBook)).then(function (datas) {
      var hits = [];
      datas.forEach(function (data, k) {
        var name = oneName(books[idxs[k]][0]);
        data.forEach(function (ch, ci) {
          ch.forEach(function (txt, vi) {
            var n = normText(txt);
            if (re.every(function (r) { return r.test(n); })) hits.push([name, ci + 1, vi + 1, txt]);
          });
        });
      });
      if (!hits.length) return { primary: { label: "Verses found", value: "0" }, note: "No verses match. Try fewer words, a different form of the word, or a wider search. " + WEB_NOTE };
      var hl = new RegExp("(" + (v.match === "phrase" ? [q] : words).map(function (w) {
        return "\\b" + w.replace(/[.*+?^${}()|[\]\\]/g, "\\$&").replace(/'/g, "['’]");
      }).join("|") + ")", "gi");
      var shown = hits.slice(0, 150);
      var html = '<ol class="verse-hits">' + shown.map(function (h) {
        return '<li><strong>' + esc(h[0] + " " + h[1] + ":" + h[2]) + "</strong> " + esc(h[3]).replace(hl, "<mark>$1</mark>") + "</li>";
      }).join("") + "</ol>";
      return {
        primary: { label: "Verses found", value: fmt.num(hits.length, 0) },
        html: html,
        note: (hits.length > shown.length ? "Showing the first " + shown.length + ". Add words or narrow the search to see fewer. " : "") + WEB_NOTE
      };
    }, function () { return { error: "The Bible text didn't load. Check your connection and try again." }; });
  };

  window.GSS_CALCS = C;
  window.GSS_UNITS = UNITS;

  /* ======================================================================
     Engine
     ====================================================================== */
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }

  function parseNum(raw) {
    var s = String(raw).replace(/[$,%\s]/g, "");
    if (s === "" || s === "-" || s === ".") return NaN;
    return /^-?\d*\.?\d+$/.test(s) || /^-?\d+\.?$/.test(s) ? parseFloat(s) : NaN;
  }

  function initForm(form) {
    var slug = form.getAttribute("data-calc");
    var fn = C[slug];
    var answer = document.querySelector("[data-answer]");
    if (!fn || !answer) return;
    var touched = {};
    var modeSel = form.querySelector('[name="mode"]');

    // Defaults: "today" for dates
    form.querySelectorAll("[data-default]").forEach(function (el) {
      var m = /^today(?:([+-])(\d+))?$/.exec(el.getAttribute("data-default"));
      if (m) {
        var d = new Date(); d.setDate(d.getDate() + (m[1] === "-" ? -1 : 1) * (+m[2] || 0));
        var iso = d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0");
        el.setAttribute("data-default", iso);
        if (!el.value) el.value = iso;
      }
    });

    // Prefill from URL (?rate=25&hours=40)
    var params = new URLSearchParams(location.search);
    params.forEach(function (val, key) {
      var el = form.elements[key];
      if (el && el.tagName) { if (el.type === "checkbox") el.checked = val === "1" || val === "true"; else el.value = val; }
    });

    // Unit converter: populate unit lists by category
    if (slug === "unit-converter") {
      var catSel = form.elements.category, fromSel = form.elements.from, toSel = form.elements.to;
      var fill = function (keep) {
        var cat = UNITS[catSel.value], keys = Object.keys(cat), d = UNIT_DEFAULTS[catSel.value];
        var prevFrom = keep ? fromSel.value : null, prevTo = keep ? toSel.value : null;
        [fromSel, toSel].forEach(function (sel) {
          sel.innerHTML = keys.map(function (k) { return '<option value="' + k + '">' + esc(cat[k][0]) + "</option>"; }).join("");
        });
        fromSel.value = cat[prevFrom] ? prevFrom : d[0];
        toSel.value = cat[prevTo] ? prevTo : d[1];
      };
      fill(!!params.get("from"));
      catSel.addEventListener("change", function () { fill(false); });
    }

    function applyMode() {
      if (!modeSel) return;
      var mode = modeSel.value;
      form.querySelectorAll("[data-show-modes]").forEach(function (f) {
        f.hidden = f.getAttribute("data-show-modes").split(",").indexOf(mode) === -1;
      });
      form.querySelectorAll("[data-labels]").forEach(function (lab) {
        var map = JSON.parse(lab.getAttribute("data-labels"));
        if (map[mode]) lab.textContent = map[mode];
      });
    }

    function read() {
      var vals = {}, errors = [];
      Array.prototype.forEach.call(form.elements, function (el) {
        if (!el.name || el.name === "website") return;
        var field = el.closest(".field");
        if (field && field.hidden) { vals[el.name] = parseNum(el.getAttribute("data-default") || "0") || 0; return; }
        var kind = el.getAttribute("data-kind") || "text";
        var label = field ? field.querySelector("label").textContent.trim() : el.name;
        var msg = "";
        if (el.type === "checkbox") { vals[el.name] = el.checked; return; }
        if (["money", "number", "percent", "integer"].indexOf(kind) > -1) {
          var raw = el.value.trim(), n;
          if (raw === "") {
            if (el.hasAttribute("data-optional")) n = 0; else msg = "Enter " + label.toLowerCase() + ".";
          } else {
            n = parseNum(raw);
            if (isNaN(n)) msg = "Use numbers only, like " + (kind === "money" ? "25.50" : "40") + ".";
            else {
              var min = el.getAttribute("data-min"), max = el.getAttribute("data-max");
              if (min !== null && n < +min) msg = +min === 0 ? "Enter 0 or more." : "Enter at least " + fmt.num(+min) + ".";
              else if (min !== null && el.hasAttribute("data-positive") && n <= +min) msg = "Enter a number greater than " + fmt.num(+min) + ".";
              else if (max !== null && n > +max) msg = "Enter " + fmt.num(+max) + " or less.";
              else if (kind === "integer" && Math.floor(n) !== n) msg = "Enter a whole number.";
            }
          }
          vals[el.name] = n;
        } else {
          vals[el.name] = el.value;
          if (el.required && !el.value) msg = "Enter " + label.toLowerCase() + ".";
        }
        if (msg) errors.push({ el: el, msg: msg });
        setError(el, touched[el.name] ? msg : "");
      });
      return { vals: vals, errors: errors };
    }

    function setError(el, msg) {
      var err = document.getElementById(el.id + "-err");
      if (!err) return;
      err.textContent = msg;
      if (msg) el.setAttribute("aria-invalid", "true"); else el.removeAttribute("aria-invalid");
    }

    function render(res) {
      if (res.error) { answer.innerHTML = '<p class="answer-error" role="alert">' + esc(res.error) + "</p>"; return; }
      var h = "";
      if (res.primary) h += '<p class="answer-primary"><span class="label">' + esc(res.primary.label) + '</span><span class="value">' + esc(res.primary.value) + "</span></p>";
      if (res.rows && res.rows.length) {
        h += '<dl class="answer-rows">' + res.rows.map(function (r) { return "<dt>" + esc(r[0]) + "</dt><dd>" + esc(r[1]) + "</dd>"; }).join("") + "</dl>";
      }
      if (res.table) {
        var t = res.table, nc = t.numCols || [];
        h += '<div class="answer-table-wrap"><table><caption class="visually-hidden">' + esc(t.caption || "") + "</caption><thead><tr>" +
          t.head.map(function (c, i) { return '<th scope="col"' + (nc.indexOf(i) > -1 ? ' class="num"' : "") + ">" + esc(c) + "</th>"; }).join("") +
          "</tr></thead><tbody>" + t.rows.map(function (r) {
            return "<tr>" + r.map(function (c, i) { return i === 0 ? '<th scope="row">' + esc(c) + "</th>" : "<td" + (nc.indexOf(i) > -1 ? ' class="num"' : "") + ">" + esc(c) + "</td>"; }).join("") + "</tr>";
          }).join("") + "</tbody></table></div>";
      }
      if (res.html) h += '<div class="answer-html">' + res.html + "</div>";
      if (res.note) h += '<p class="answer-note">' + esc(res.note) + "</p>";
      answer.innerHTML = h;
    }

    function run(showAll) {
      if (showAll) Array.prototype.forEach.call(form.elements, function (el) { if (el.name) touched[el.name] = true; });
      var r = read();
      if (r.errors.length) {
        answer.innerHTML = '<p class="answer-error">' + (Object.keys(touched).length ? "Check the highlighted field to see your answer." : "Fill in the fields to see your answer.") + "</p>";
        if (showAll) r.errors[0].el.focus();
        return;
      }
      var ticket = ++runId;
      try {
        var out = fn(r.vals);
        if (out && typeof out.then === "function") {
          answer.setAttribute("aria-busy", "true");
          if (!answer.querySelector(".answer-primary")) answer.innerHTML = '<p class="muted">Loading…</p>';
          out.then(function (res) { if (ticket === runId) { answer.removeAttribute("aria-busy"); render(res); } },
            function () { if (ticket === runId) { answer.removeAttribute("aria-busy"); render({ error: "Something didn't load. Check your connection and try again." }); } });
        } else render(out);
      } catch (e) { answer.innerHTML = '<p class="answer-error">Something went wrong with these entries. Check them and try again.</p>'; }
    }

    var timer, runId = 0;
    form.addEventListener("input", function (e) {
      if (e.target.name) touched[e.target.name] = true;
      clearTimeout(timer);
      timer = setTimeout(function () { run(false); }, 200);
    });
    form.addEventListener("change", function (e) {
      if (e.target.name === "mode") applyMode();
      if (e.target.name) touched[e.target.name] = true;
      run(false);
    });
    form.addEventListener("submit", function (e) { e.preventDefault(); run(true); answer.closest(".answer").scrollIntoView({ block: "nearest", behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" }); });
    var reset = form.querySelector("[data-reset]");
    if (reset) reset.addEventListener("click", function () {
      Array.prototype.forEach.call(form.elements, function (el) {
        if (!el.name) return;
        var d = el.getAttribute("data-default");
        if (el.type === "checkbox") el.checked = d === "1";
        else if (d !== null) el.value = d;
        setError(el, "");
      });
      touched = {};
      if (slug === "unit-converter") form.elements.category.dispatchEvent(new Event("change"));
      if (history.replaceState) history.replaceState(null, "", location.pathname);
      applyMode();
      run(false);
      var first = form.querySelector("input, select");
      if (first) first.focus();
    });

    applyMode();
    run(false);
  }

  document.querySelectorAll("form[data-calc]").forEach(initForm);
})();
