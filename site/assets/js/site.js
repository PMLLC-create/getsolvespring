/* ==========================================================================
   Get Solve Spring — site behavior: mobile menu, smart search, blog filters,
   contact form. No dependencies.
   ========================================================================== */
(function () {
  "use strict";

  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }

  /* ---------- Mobile menu ---------- */
  var toggle = document.querySelector(".menu-toggle");
  var menu = document.getElementById("mobile-menu");
  if (toggle && menu) {
    toggle.addEventListener("click", function () {
      var open = toggle.getAttribute("aria-expanded") === "true";
      toggle.setAttribute("aria-expanded", String(!open));
      menu.setAttribute("data-open", String(!open));
      if (!open) { var f = menu.querySelector("input, a"); if (f) f.focus(); }
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && toggle.getAttribute("aria-expanded") === "true") { toggle.click(); toggle.focus(); }
    });
  }

  /* ---------- Search ---------- */
  var indexPromise = null;
  function loadIndex() {
    if (!indexPromise) indexPromise = fetch("/search-index.json").then(function (r) { return r.json(); }).catch(function () { return []; });
    return indexPromise;
  }

  var STOP = "a an the is are am i my me of to in for on and or how what whats what's do does can with much should calculate calculator find get your you it be by at this that".split(" ");
  var SYN = {
    paycheck: ["take-home", "net", "pay"], wage: ["hourly", "pay"], wages: ["hourly", "pay"], income: ["salary", "pay"],
    yearly: ["annual", "salary"], annually: ["annual", "salary"], year: ["annual", "salary"], hr: ["hourly"], hour: ["hourly"],
    percent: ["percentage"], "%": ["percentage"], sale: ["discount"], off: ["discount"], ot: ["overtime"],
    margin: ["profit", "markup"], loan: ["debt", "interest"], credit: ["debt"], save: ["savings"], saving: ["savings"],
    old: ["age"], birthday: ["age"], days: ["date"], hours: ["time", "hourly"], convert: ["converter", "unit"],
    gratuity: ["tip"], spending: ["budget"], taxes: ["tax"], net: ["take-home"], gross: ["pay"], job: ["salary", "offer"]
  };

  function tokens(q) {
    return q.toLowerCase().replace(/[^a-z0-9%$.\- ]/g, " ").split(/\s+/).filter(function (t) { return t && STOP.indexOf(t) === -1; });
  }

  function score(item, toks) {
    var s = 0, hits = 0;
    var title = item.t.toLowerCase(), kw = (item.k || "").toLowerCase(), desc = (item.d || "").toLowerCase();
    toks.forEach(function (tk) {
      var cands = [tk].concat(SYN[tk] || []);
      var best = 0;
      cands.forEach(function (c, ci) {
        if (/^[$\d.,]+$/.test(c)) return;
        var w = ci === 0 ? 1 : 0.6, v = 0;
        if (new RegExp("\\b" + c.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")).test(title)) v = 6;
        else if (title.indexOf(c) > -1) v = 4;
        else if (kw.indexOf(c) > -1) v = 3;
        else if (desc.indexOf(c) > -1) v = 1;
        best = Math.max(best, v * w);
      });
      if (best > 0) hits++;
      s += best;
    });
    if (!hits) return 0;
    s *= hits / Math.max(1, toks.filter(function (t) { return !/^[$\d.,]+$/.test(t); }).length);
    if (item.type === "tool") s *= 1.8;
    else if (item.type === "page") s *= 0.6;
    return s + (item.w || 0);
  }

  function money(x) { return x.toLocaleString("en-US", { style: "currency", currency: "USD", maximumFractionDigits: x % 1 ? 2 : 0 }); }

  // Instant answers for common question patterns
  function instant(q) {
    var s = q.toLowerCase().replace(/,/g, "");
    var m = /\$?\s*(\d+(?:\.\d+)?)\s*(?:dollars?\s*)?(?:\/|an|a|per|each)?\s*(?:hr|hour)\b/.exec(s);
    if (m && !/salary|year.*hour|to hourly/.test(s.replace(m[0], ""))) {
      var r = +m[1];
      return { q: money(r) + " an hour", a: "≈ " + money(r * 2080) + " a year",
        basis: "Based on 40 hours a week, 52 weeks a year, before taxes. That's about " + money(Math.round(r * 2080 / 12)) + " a month.",
        link: "/tools/hourly-to-salary/?rate=" + r, label: "Adjust hours and weeks" };
    }
    m = /\$?\s*(\d{4,}(?:\.\d+)?)\s*(k)?\s*(?:a|per|\/)?\s*(?:year|yr|annually|salary)/.exec(s) || /\$?\s*(\d+(?:\.\d+)?)(k)\s*(?:a|per|\/)?\s*(?:year|yr|salary)?/.exec(s);
    if (m) {
      var y = +m[1] * (m[2] ? 1000 : 1);
      if (y >= 1000) return { q: money(y) + " a year", a: "≈ " + money(Math.round(y / 2080 * 100) / 100) + " an hour",
        basis: "Based on 40 hours a week, 52 weeks a year, before taxes. That's about " + money(Math.round(y / 12)) + " a month.",
        link: "/tools/salary-to-hourly/?salary=" + y, label: "Adjust your schedule" };
    }
    m = /(\d+(?:\.\d+)?)\s*(?:%|percent)\s*of\s*\$?\s*(\d+(?:\.\d+)?)/.exec(s);
    if (m) {
      var v = +m[1] / 100 * +m[2];
      return { q: m[1] + "% of " + m[2], a: (+v.toFixed(6)).toLocaleString("en-US"), basis: "(" + m[1] + " ÷ 100) × " + m[2] + ".",
        link: "/tools/percentage/?mode=of&a=" + m[1] + "&b=" + m[2], label: "Open the percentage calculator" };
    }
    m = /(\d+(?:\.\d+)?)\s*(?:%|percent)\s*off\s*(?:of\s*)?\$?\s*(\d+(?:\.\d+)?)/.exec(s);
    if (m) {
      var p = +m[2] * (1 - +m[1] / 100);
      return { q: m[1] + "% off " + money(+m[2]), a: money(Math.round(p * 100) / 100), basis: "You save " + money(Math.round((+m[2] - p) * 100) / 100) + ".",
        link: "/tools/discount/?price=" + m[2] + "&disc=" + m[1], label: "Add a second discount or sales tax" };
    }
    return null;
  }

  function renderResults(box, q, items) {
    var html = "", ia = instant(q);
    if (ia) {
      html += '<div class="instant"><p class="instant-q">' + esc(ia.q) + '</p><p class="instant-a">' + esc(ia.a) + '</p><p class="instant-basis">' +
        esc(ia.basis) + '</p><a href="' + esc(ia.link) + '">' + esc(ia.label) + "</a></div>";
    }
    var toks = tokens(q);
    if (ia && /hour|hr/.test(q.toLowerCase())) toks = toks.concat(["hourly", "salary"]);
    var ranked = items.map(function (it) { return { it: it, s: score(it, toks) }; })
      .filter(function (x) { return x.s > 1.5; })
      .sort(function (a, b) { return b.s - a.s; }).slice(0, 8);
    if (ranked.length) {
      html += '<ul class="result-list" aria-label="Search results">' + ranked.map(function (x) {
        var it = x.it, kind = it.type === "tool" ? "Tool" : it.type === "guide" ? "Guide" : "Page";
        return '<li><a href="' + esc(it.u) + '"><span class="result-kind ' + it.type + '">' + kind + '</span><span class="result-title">' +
          esc(it.t) + '</span><span class="result-desc">' + esc(it.d) + "</span></a></li>";
      }).join("") + "</ul>";
    } else if (!ia) {
      html += '<p class="no-results">No match for “' + esc(q) + '”. Try fewer words, like “overtime” or “profit”, or <a href="/tools/">browse all tools</a>.</p>';
    }
    box.innerHTML = html;
    var status = box.parentNode.querySelector("[data-search-status]");
    if (status) status.textContent = ranked.length ? ranked.length + " results" : ia ? "Instant answer shown" : "No results";
  }

  document.querySelectorAll("[data-live-search]").forEach(function (form) {
    var input = form.querySelector("input[name=q]");
    var box = form.querySelector("[data-results]");
    if (!input || !box) return;
    var t;
    function go() {
      var q = input.value.trim();
      if (q.length < 2) { box.innerHTML = ""; return; }
      loadIndex().then(function (items) { renderResults(box, q, items); });
    }
    input.addEventListener("input", function () { clearTimeout(t); t = setTimeout(go, 120); });
    input.addEventListener("focus", loadIndex);
    if (form.hasAttribute("data-search-page")) {
      var q0 = new URLSearchParams(location.search).get("q");
      if (q0) { input.value = q0; go(); }
      form.addEventListener("submit", function (e) {
        e.preventDefault(); go();
        if (history.replaceState) history.replaceState(null, "", "?q=" + encodeURIComponent(input.value.trim()));
      });
    }
  });

  document.querySelectorAll("[data-try]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var input = document.getElementById(btn.getAttribute("data-try"));
      input.value = btn.textContent.trim();
      input.dispatchEvent(new Event("input"));
      input.focus();
    });
  });

  /* ---------- Blog index filters ---------- */
  var blog = document.querySelector("[data-blog-list]");
  if (blog) {
    var cards = Array.prototype.slice.call(blog.querySelectorAll("[data-cat]"));
    var buttons = document.querySelectorAll("[data-filter]");
    var bsearch = document.getElementById("blog-search");
    var count = document.getElementById("blog-count");
    var active = new URLSearchParams(location.search).get("category") || "all";
    function apply() {
      var q = bsearch ? bsearch.value.trim().toLowerCase() : "", shown = 0;
      cards.forEach(function (c) {
        var ok = (active === "all" || c.getAttribute("data-cat") === active) && (!q || c.textContent.toLowerCase().indexOf(q) > -1);
        c.hidden = !ok; if (ok) shown++;
      });
      buttons.forEach(function (b) { b.setAttribute("aria-pressed", String(b.getAttribute("data-filter") === active)); });
      if (count) count.textContent = shown === 1 ? "1 guide" : shown + " guides";
    }
    buttons.forEach(function (b) { b.addEventListener("click", function () { active = b.getAttribute("data-filter"); apply(); }); });
    if (bsearch) bsearch.addEventListener("input", apply);
    apply();
  }

  /* ---------- Contact form ---------- */
  var cf = document.getElementById("contact-form");
  if (cf) {
    var status = document.getElementById("form-status");
    var started = Date.now();
    cf.addEventListener("submit", function (e) {
      e.preventDefault();
      status.className = "form-status";
      var bad = Array.prototype.filter.call(cf.querySelectorAll("[required]"), function (el) { return !el.value.trim(); });
      var email = cf.elements.email.value.trim();
      if (bad.length) { status.textContent = "Fill in every field before sending."; status.classList.add("bad"); bad[0].focus(); return; }
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) { status.textContent = "Enter a valid email address so we can reply."; status.classList.add("bad"); cf.elements.email.focus(); return; }
      if (cf.elements.website.value || Date.now() - started < 2500) { status.textContent = "Message sent. Thank you."; status.classList.add("ok"); cf.reset(); return; }
      var endpoint = cf.getAttribute("data-endpoint");
      if (!endpoint) {
        var to = cf.getAttribute("data-email");
        location.href = "mailto:" + to + "?subject=" + encodeURIComponent(cf.elements.subject.value) +
          "&body=" + encodeURIComponent(cf.elements.message.value + "\n\n— " + cf.elements.name.value + " (" + email + ")");
        status.textContent = "Your email app should open with the message ready to send.";
        status.classList.add("ok");
        return;
      }
      status.textContent = "Sending…";
      fetch(endpoint, { method: "POST", headers: { Accept: "application/json" }, body: new FormData(cf) })
        .then(function (r) { if (!r.ok) throw new Error(); status.textContent = "Message sent. Thank you."; status.classList.add("ok"); cf.reset(); })
        .catch(function () { status.textContent = "The message didn't send. Email us directly at " + cf.getAttribute("data-email") + "."; status.classList.add("bad"); });
    });
  }
})();
