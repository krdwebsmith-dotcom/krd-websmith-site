#!/usr/bin/env python3
"""
KRD Websmith — static page builder.

Generates the 10 committed .html files in the repo root from one shared shell so
the header, footer and <head> can never drift between pages again.

The generated HTML is what deploys (Cloudflare serves the repo root), so this
script is a convenience, not a runtime dependency. Run it after editing:

    python3 tools/build.py

Nothing here touches wrangler.jsonc or the contact worker endpoint.
"""

import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://krdwebsmith.com"
WORKER = "https://krd-websmith-contact.newonb123.workers.dev"

try:
    from PIL import Image
except ImportError:
    Image = None

_dim_cache = {}


def dims(rel):
    """Real intrinsic width/height attributes, to stop layout shift."""
    if rel in _dim_cache:
        return _dim_cache[rel]
    out = ""
    path = os.path.join(ROOT, rel)
    if Image and os.path.exists(path):
        try:
            with Image.open(path) as im:
                out = f' width="{im.width}" height="{im.height}"'
        except Exception:
            out = ""
    _dim_cache[rel] = out
    return out


def shot(rel, alt, cls="browser-shot", lazy=True, extra=""):
    load = ' loading="lazy" decoding="async"' if lazy else ' decoding="async"'
    return f'<img class="{cls}" src="{rel}" alt="{alt}"{dims(rel)}{load}{extra}>'


# ---------------------------------------------------------------------------
# navigation
# ---------------------------------------------------------------------------

NAV = [
    ("work.html", "Work", "01"),
    ("services.html", "Services", "02"),
    ("process.html", "Process", "03"),
    ("about.html", "About", "04"),
    ("audit.html", "Audit", "05"),
    ("contact.html", "Contact", "06"),
]

MARK = (
    '<svg class="krd-mark" viewBox="0 0 24 24" aria-hidden="true" fill="none">'
    '<path d="M4 4v16M4 12h7l6-8M11 12l6 8" stroke="currentColor" stroke-width="2.4" '
    'stroke-linecap="square"/><rect x="17.5" y="2.5" width="4" height="4" fill="currentColor"/></svg>'
)


def head(title, desc, page, extra_css=""):
    canonical = f"{SITE}/" if page == "index.html" else f"{SITE}/{page}"
    css = f"\n  <style>\n{extra_css}\n  </style>" if extra_css else ""
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="{desc}">
  <link rel="canonical" href="{canonical}">
  <meta name="theme-color" content="#F4F1EA">
  <meta name="author" content="KRD Websmith">

  <meta property="og:type" content="website">
  <meta property="og:site_name" content="KRD Websmith">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{desc}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:locale" content="en_CA">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{title}">
  <meta name="twitter:description" content="{desc}">

  <link rel="icon" href="favicon.svg" type="image/svg+xml">
  <link rel="apple-touch-icon" href="favicon.svg">

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="preload" as="style" href="{FONTS}">
  <link rel="stylesheet" href="{FONTS}" media="print" onload="this.media='all'">
  <noscript><link rel="stylesheet" href="{FONTS}"></noscript>
  <link rel="stylesheet" href="styles.css">{css}
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
"""


FONTS = (
    "https://fonts.googleapis.com/css2"
    "?family=Archivo:wght@400;500;600;800"
    "&family=IBM+Plex+Mono:wght@500;600"
    "&family=Playfair+Display:ital,wght@0,600;1,600"
    "&display=swap"
)


def header(active):
    links = "".join(
        f'<a href="{href}"{" class=\"active\" aria-current=\"page\"" if href == active else ""}>{label}</a>'
        for href, label, _ in NAV[:-1]
    )
    mobile = "".join(
        f'<a href="{href}"{" aria-current=\"page\"" if href == active else ""}>'
        f"<span>{label}</span><small>{num}</small></a>"
        for href, label, num in NAV
    )
    return f"""<header id="siteHeader" class="site-header">
  <a class="brand" href="index.html" aria-label="KRD Websmith — home">
    <span class="brand-mark" aria-hidden="true">KRD</span>
    <span class="brand-copy"><strong>KRD Websmith</strong><small>Web design / development</small></span>
  </a>
  <nav class="desktop-nav" aria-label="Primary">{links}</nav>
  <div class="header-action">
    <a class="header-cta" href="contact.html">Start a project <span aria-hidden="true">&#8599;</span></a>
    <button id="menuToggle" class="menu-toggle" type="button" aria-label="Open menu"
            aria-expanded="false" aria-controls="mobileMenu"><i></i><i></i></button>
  </div>
</header>

<div id="mobileMenu" class="mobile-menu">
  <nav aria-label="Mobile">{mobile}</nav>
  <div class="mobile-menu-foot">
    <span>KRD / Web studio</span>
    <span>Kitchener / Ontario</span>
    <span>hello@krdwebsmith.com</span>
  </div>
</div>
"""


def breadcrumbs(label):
    return (
        '<nav class="breadcrumbs shell" aria-label="Breadcrumb">'
        '<a href="index.html">Home</a><span aria-hidden="true">/</span>'
        f'<span aria-current="page">{label}</span></nav>'
    )


def next_step(note, heading, buttons):
    btns = "".join(buttons)
    return f"""<section class="next-step shell">
  <div>
    <p class="meta">{note}</p>
    <h3>{heading}</h3>
  </div>
  <div class="button-row">{btns}</div>
</section>"""


def footer():
    explore = "".join(
        f'<a href="{href}">{label}</a>' for href, label, _ in NAV[:-1]
    )
    return f"""<footer class="site-footer">
  <div class="shell footer-main">
    <div class="footer-brand">
      <p class="label">KRD Websmith</p>
      <h2>KRD<br>Websmith</h2>
      <p>Web design /<br>Kitchener, Ontario</p>
    </div>
    <div class="footer-col">
      <span>Explore</span>{explore}
    </div>
    <div class="footer-col">
      <span>Start</span>
      <a href="contact.html">Start a project</a>
      <a href="mailto:hello@krdwebsmith.com">hello@krdwebsmith.com</a>
    </div>
  </div>
  <div class="shell footer-tech">
    <div><span>Edition</span><strong>KRD / Web edition</strong></div>
    <div><span>Service</span><strong>Design + development</strong></div>
    <div><span>Location</span><strong>Kitchener / Remote</strong></div>
  </div>
  <div class="footer-bottom">
    <span>&copy; <span id="year">2026</span> KRD Websmith</span>
    <span>krdwebsmith.com</span>
  </div>
</footer>

<script src="script.js" defer></script>
</body>
</html>
"""


def page(name, title, desc, body, active=None, extra_css="", extra_js=""):
    html = head(title, desc, name, extra_css)
    html += header(active or name)
    html += body
    html += footer()
    if extra_js:
        html = html.replace(
            '<script src="script.js" defer></script>',
            '<script src="script.js" defer></script>\n<script>\n' + extra_js + "\n</script>",
        )
    with open(os.path.join(ROOT, name), "w", encoding="utf-8") as fh:
        fh.write(html)
    return name


# ===========================================================================
# reusable visual components
# ===========================================================================


def browser(src, alt, url, dim="1440 × 900", cls="", lazy=True, scrolls=False, vh=440):
    """A hairline browser window wrapping a real screenshot."""
    inner = shot(src, alt, lazy=lazy)
    if scrolls:
        body = f'<div class="browser-viewport" style="--vh:{vh}px">{inner}</div>'
        cls = (cls + " scrolls").strip()
    else:
        body = inner
    return f"""<div class="browser {cls}"{f' style="--vh:{vh}px"' if scrolls else ''}>
  <div class="browser-bar">
    <span class="browser-dots" aria-hidden="true"><i></i><i></i><i></i></span>
    <span class="browser-url">{url}</span>
    <span class="browser-dim">{dim}</span>
  </div>
  {body}
</div>"""


def device(src, alt, crop=True, vh=520, lazy=True):
    inner = shot(src, alt, cls="device-shot", lazy=lazy)
    if crop:
        return f"""<div class="device crops">
  <div class="device-bar" aria-hidden="true"><span></span></div>
  <div class="device-viewport" style="--vh:{vh}px">{inner}</div>
</div>"""
    return f"""<div class="device">
  <div class="device-bar" aria-hidden="true"><span></span></div>
  {inner}
</div>"""


def caption(left, right):
    return f'<p class="shot-caption"><span>{left}</span><b>{right}</b></p>'


PROJECTS = [
    {
        "slug": "apex",
        "page": "project-apex.html",
        "name": "APEX Auto Detailing",
        "plain": "APEX Auto Detailing",
        "num": "001",
        "category": "Automotive",
        "tagline": "Performance / premium service",
        "url": "apexautodetailing.ca",
        "blurb": "A performance-led concept that makes a local detailing business feel more premium, focused, and easier to book.",
        "challenge": "Detailing websites often use the same aggressive template language, which makes businesses blur together.",
        "direction": "Use strong typography, confident contrast, package clarity, and fewer but stronger calls to action.",
        "purpose": "Help customers understand the offer faster and make the brand feel worth a premium price.",
        "tags": ["Charcoal + hot accent", "Condensed display", "Package table", "Booking path"],
    },
    {
        "slug": "noir",
        "page": "project-noir.html",
        "name": "NOIR HOUSE",
        "plain": "NOIR HOUSE",
        "num": "002",
        "category": "Barbering",
        "tagline": "Editorial / booking",
        "url": "noirhouse.ca",
        "blurb": "A quieter, editorial barbershop direction built around taste, service clarity, and a cleaner booking experience.",
        "challenge": "The category is crowded with the same dark masculine aesthetic and interchangeable layouts.",
        "direction": "Shift toward editorial typography, warm paper tones, restrained colour, and a calmer information hierarchy.",
        "purpose": "Make the shop more memorable while keeping service selection and booking straightforward.",
        "tags": ["Bone + espresso", "High-contrast serif", "Service list", "Time-slot booking"],
    },
    {
        "slug": "evercrest",
        "page": "project-evercrest.html",
        "name": "EVERCREST Outdoor",
        "plain": "EVERCREST Outdoor",
        "num": "003",
        "category": "Landscape",
        "tagline": "High-ticket service / lead qualification",
        "url": "evercrestoutdoor.ca",
        "blurb": "A landscape construction concept designed to build trust before the first call and attract more serious project inquiries.",
        "challenge": "Large outdoor projects require more reassurance, proof, and process clarity than a simple service purchase.",
        "direction": "Use architectural spacing, project-led imagery, process storytelling, and budget-aware inquiry fields.",
        "purpose": "Support more serious inquiries and make the company feel capable of larger, higher-value projects.",
        "tags": ["Forest + stone", "Grounded sans", "Estimate flow", "Service areas"],
    },
]

BY_SLUG = {p["slug"]: p for p in PROJECTS}


SERVICES = [
    {
        "num": "01",
        "name": "Business Website",
        "copy": "For service businesses that need a professional site, clear service pages, responsive design, and a real inquiry path.",
        "includes": ["Custom homepage", "Services content", "Responsive design", "Contact form", "Basic SEO setup", "Two revision rounds"],
        "price": "From $300 CAD",
        "scope": "3–5 pages",
        "peek": "assets/shots/noir-detail.webp",
        "peek_alt": "Service and price list from the NOIR HOUSE concept",
    },
    {
        "num": "02",
        "name": "Growth Website",
        "copy": "For businesses that need more content depth, stronger conversion architecture, project galleries, and custom interactions.",
        "includes": ["Multiple pages", "Custom interactions", "Lead-focused structure", "Project / gallery system", "Forms and integrations", "Two revision rounds"],
        "price": "From $500 CAD",
        "scope": "6–10 pages",
        "peek": "assets/shots/apex-detail.webp",
        "peek_alt": "Package comparison table from the APEX Auto Detailing concept",
    },
    {
        "num": "03",
        "name": "Advanced Build",
        "copy": "For deeper systems, integrations, custom workflows, or requirements that go beyond a standard brochure website.",
        "includes": ["Custom scope", "Advanced interactions", "Third-party integrations", "Custom forms", "Unique content systems"],
        "price": "Quoted by scope",
        "scope": "Defined together",
        "peek": "assets/shots/evercrest-detail.webp",
        "peek_alt": "Multi-step estimate form from the EVERCREST Outdoor concept",
    },
]


PROCESS = [
    ("01", "Understand", ["Business", "Customer", "Goal"],
     "Define the business, audience, current site, required pages, and what the new website actually needs to accomplish.",
     "Output / scope + page list"),
    ("02", "Direction", ["Structure", "Type", "Image", "Interaction"],
     "Establish typography, image language, page hierarchy, interaction style, and the customer journey before polishing screens.",
     "Output / design direction"),
    ("03", "Build", ["Responsive", "Accessible", "Fast"],
     "Code the approved direction for desktop, tablet and mobile with the required forms, content and interactions.",
     "Output / working website"),
    ("04", "Refine", ["Test", "Review", "Adjust"],
     "Test on real screen sizes, review the details, and complete the agreed revision rounds before anything ships.",
     "Output / revision rounds"),
    ("05", "Release", ["Deploy", "Verify", "Hand over"],
     "Deploy the approved site, verify the live domain and forms, and hand over a working system you own.",
     "Output / live site"),
]


# ===========================================================================
# HOME
# ===========================================================================


def build_index():
    apex, noir, ever = BY_SLUG["apex"], BY_SLUG["noir"], BY_SLUG["evercrest"]

    # ---- archive rows, three deliberately different compositions ----------
    def archive_a(p):
        return f"""<article class="archive-item comp-a">
  <div class="archive-meta reveal">
    <p class="label">Project / {p['num']}</p>
    <h3>{p['name']}</h3>
    <dl class="metalist">
      <div><dt>Category</dt><dd>{p['category']}</dd></div>
      <div><dt>Role</dt><dd>Design + development</dd></div>
      <div><dt>Status</dt><dd>Concept project</dd></div>
    </dl>
    <p class="body-copy">{p['blurb']}</p>
    <p><a class="textlink" href="{p['page']}">View project <span aria-hidden="true">&#8599;</span></a></p>
  </div>
  <div class="archive-visual reveal" data-delay="1">
    {browser(f"assets/shots/{p['slug']}-desktop-full.webp", f"{p['plain']} concept homepage, desktop", p['url'], scrolls=True, vh=470)}
    {caption("Full page / hover to scroll", "1440 × 900")}
  </div>
</article>"""

    def archive_b(p):
        return f"""<article class="archive-item comp-b">
  <div class="archive-meta reveal">
    <p class="label">Project / {p['num']}</p>
    <h3>{p['name']}</h3>
    <dl class="metalist">
      <div><dt>Category</dt><dd>{p['category']}</dd></div>
      <div><dt>Focus</dt><dd>Mobile booking</dd></div>
      <div><dt>Status</dt><dd>Concept project</dd></div>
    </dl>
    <p class="body-copy">{p['blurb']}</p>
    <p><a class="textlink" href="{p['page']}">View project <span aria-hidden="true">&#8599;</span></a></p>
  </div>
  <div class="archive-visual reveal" data-delay="1">
    <div class="mobile-led">
      {device(f"assets/shots/{p['slug']}-mobile-full.webp", f"{p['plain']} concept on a phone", vh=470)}
      {browser(f"assets/shots/{p['slug']}-desktop.webp", f"{p['plain']} concept homepage, desktop", p['url'], dim="1440 × 900")}
    </div>
    {caption("Responsive pair / 390 &times; 844 + 1440 &times; 900", "Mobile first")}
  </div>
</article>"""

    def archive_c(p):
        return f"""<article class="archive-item comp-c">
  <div class="archive-meta reveal">
    <div>
      <p class="label">Project / {p['num']}</p>
      <h3>{p['name']}</h3>
    </div>
    <div>
      <p class="body-copy">{p['blurb']}</p>
      <p style="margin-top:18px"><a class="textlink" href="{p['page']}">View project <span aria-hidden="true">&#8599;</span></a></p>
    </div>
  </div>
  <div class="archive-visual reveal" data-delay="1">
    <div class="stacked-shots">
      <div>
        {browser(f"assets/shots/{p['slug']}-desktop.webp", f"{p['plain']} concept homepage", p['url'])}
        {caption("Home / desktop", "1440 × 900")}
      </div>
      <div>
        {browser(f"assets/shots/{p['slug']}-detail.webp", f"Estimate form detail from the {p['plain']} concept", p['url'] + "/estimate", dim="Detail")}
        {caption("Estimate flow / detail", "Qualification")}
      </div>
    </div>
  </div>
</article>"""

    # ---- services rows ----------------------------------------------------
    offer_rows = "".join(
        f"""<a class="offer-row reveal" href="services.html">
  <span class="num">{s['num']}</span>
  <div class="offer-body">
    <h3>{s['name']}</h3>
    <p>{s['copy']}</p>
  </div>
  <div class="offer-peek">
    <div class="frame" style="aspect-ratio:16/10">{shot(s['peek'], s['peek_alt'], cls="")}</div>
  </div>
  <div class="offer-price">
    <b>{s['price']}</b>
    <span>{s['scope']}</span>
    <small>View services &#8594;</small>
  </div>
</a>"""
        for s in SERVICES
    )

    doc_steps = "".join(
        f"""<div class="doc-step reveal">
  <span class="num">{num}</span>
  <div>
    <h3>{title}</h3>
    <div class="doc-terms">{"".join(f"<span>{t}</span>" for t in terms)}</div>
  </div>
  <div class="doc-body">
    <p>{copy}</p>
    <p class="meta">{out}</p>
  </div>
</div>"""
        for num, title, terms, copy, out in PROCESS
    )

    body = f"""<main id="main">

  <!-- ============ HERO ============ -->
  <section class="hero">
    <div class="shell hero-grid">
      <div class="hero-head">
        <p class="label reveal">Web design for service businesses</p>
        <h1 class="display reveal" data-delay="1">
          Your website <br class="brk">should make the <br class="brk">next customer
          <em>trust you faster.</em>
        </h1>
      </div>

      <div class="hero-side reveal" data-delay="2">
        <dl class="metalist">
          <div><dt>KRD</dt><dd>Web studio</dd></div>
          <div><dt>Location</dt><dd>Kitchener, ON</dd></div>
          <div><dt>Service</dt><dd>Design + development</dd></div>
          <div><dt>Output</dt><dd>Responsive web</dd></div>
        </dl>
        <div class="annotation">
          <span>Objective /</span>
          <strong>Turn attention<br>into trust.</strong>
        </div>
      </div>

      <div class="hero-body reveal" data-delay="2">
        <p class="body-copy lead measure">I build custom websites for businesses that have outgrown
          their current site, need a stronger first impression, or want a clearer path from visitor
          to inquiry.</p>
        <div class="button-row">
          <a class="button dark" href="contact.html">Get a project quote <span aria-hidden="true">&#8599;</span></a>
          <a class="button" href="work.html">See the work <span aria-hidden="true">&#8594;</span></a>
        </div>
      </div>

      <div class="hero-note reveal" data-delay="3">
        <strong>Got my email? / Note 001</strong>
        <span>I only reach out when I spot a real opportunity. You can see exactly how I think
          about websites here before deciding whether to reply.</span>
      </div>
    </div>

    <div class="shell hero-visual">
      <div class="reveal mask">
        {browser("assets/shots/apex-desktop.webp", "APEX Auto Detailing concept homepage built by KRD Websmith", apex['url'], lazy=False)}
        {caption("Project / 001 &nbsp;·&nbsp; Concept &nbsp;·&nbsp; Automotive", "1440 × 900")}
      </div>
      <div class="reveal" data-delay="1">
        {device("assets/shots/apex-mobile.webp", "APEX Auto Detailing concept on a phone", crop=False, lazy=False)}
        {caption("Same build", "390 × 844")}
      </div>
    </div>

    <div class="shell"><div class="ticks" aria-hidden="true"></div></div>

    <div class="shell hero-strip">
      <div><span>01</span><strong>Custom coded</strong></div>
      <div><span>02</span><strong>Mobile first</strong></div>
      <div><span>03</span><strong>Clear project scope</strong></div>
      <div><span>04</span><strong>Direct communication</strong></div>
    </div>
  </section>

  <!-- ============ 01 / WHAT EARNS TRUST ============ -->
  <section class="section shell" aria-labelledby="trust-title">
    <div class="section-index">
      <b>01</b><span class="spacer" aria-hidden="true"></span><span>What earns trust / 001</span>
    </div>
    <div class="section-head">
      <div>
        <h2 class="display-sm reveal" id="trust-title">A good <br class="brk">website <br class="brk">removes
          <em>doubt.</em></h2>
      </div>
      <p class="body-copy section-note reveal" data-delay="1">Your customer is making decisions before
        they contact you. The site needs to answer the important questions quickly, look credible on
        every screen, and make the next action obvious.</p>
    </div>

    <div class="trust">
      <!-- 01 first impression — huge screenshot -->
      <article class="trust-item t1">
        <div class="trust-head reveal">
          <p class="label">01 / First impression</p>
          <h3 class="display-xs">Look established before <br class="brk">the first call.</h3>
          <p class="body-copy">Strong typography, image direction, spacing, and page hierarchy can make
            a small business feel organized and trustworthy without pretending to be something it is not.</p>
        </div>
        <div class="archive-visual reveal mask" data-delay="1">
          {browser("assets/shots/noir-desktop.webp", "NOIR HOUSE concept homepage showing typographic hierarchy", noir['url'])}
          {caption("Project / 002 &nbsp;·&nbsp; First impression", "1440 × 900")}
        </div>
      </article>

      <!-- 02 mobile — real responsive comparison -->
      <article class="trust-item t2">
        <div class="archive-visual reveal" data-delay="1">
          <div class="responsive-pair">
            <div>
              {browser("assets/shots/evercrest-desktop.webp", "EVERCREST Outdoor concept on desktop", ever['url'])}
              {caption("Desktop", "1440 × 900")}
            </div>
            <div>
              {device("assets/shots/evercrest-mobile.webp", "EVERCREST Outdoor concept on a phone", crop=False)}
              {caption("Phone", "390 × 844")}
            </div>
          </div>
        </div>
        <div class="trust-head reveal">
          <p class="label">02 / Mobile</p>
          <h3 class="display-xs">Work properly <br class="brk">where customers <br class="brk">actually browse.</h3>
          <p class="body-copy">The mobile layout is treated as a primary experience. Navigation, forms,
            service content, and calls to action are built intentionally for smaller screens — not
            stacked as an afterthought.</p>
        </div>
      </article>

      <!-- 03 clarity — typographic proof -->
      <article class="trust-item t3">
        <div class="trust-head reveal">
          <p class="label">03 / Clarity</p>
          <h3 class="display-xs">Make the offer <br class="brk">easy to understand.</h3>
          <p class="body-copy measure">Visitors should know what you do, who it is for, and why they
            should care without digging through vague marketing copy or confusing menus.</p>
          <div class="clarity-demo">
            <div class="vague">
              <span>Vague /</span>
              <p>We deliver innovative solutions tailored to elevate your brand experience.</p>
            </div>
            <div class="clear">
              <span>Clear /</span>
              <p>We detail cars in Kitchener. Book online. Most jobs done in a day.</p>
            </div>
          </div>
        </div>
      </article>

      <!-- 04 action — CTA hierarchy demonstrated -->
      <article class="trust-item t4">
        <div class="trust-head reveal">
          <p class="label">04 / Action</p>
          <h3 class="display-xs">Give every page <br class="brk">a useful next step.</h3>
          <p class="body-copy">Quote requests, bookings, calls, service comparisons, and project
            inquiries are placed where they make sense instead of being buried in one generic
            contact button.</p>
        </div>
        <div class="cta-demo reveal" data-delay="1" aria-hidden="true">
          <div class="cta-demo-row">
            <small>Primary</small>
            <span class="cta-solid">Get a quote <span>&#8599;</span></span>
          </div>
          <div class="cta-demo-row">
            <small>Secondary</small>
            <span class="cta-ghost">See the work <span>&#8594;</span></span>
          </div>
          <div class="cta-demo-row">
            <small>Tertiary</small>
            <span class="cta-text">Read the process &#8594;</span>
          </div>
        </div>
      </article>
    </div>
  </section>

  <!-- ============ 02 / SELECTED WORK ============ -->
  <section class="section shell" aria-labelledby="work-title">
    <div class="section-index">
      <b>02</b><span class="spacer" aria-hidden="true"></span><span>Selected work / Archive</span>
    </div>
    <div class="section-head">
      <h2 class="display-sm reveal" id="work-title">Selected work<br><em>archive.</em></h2>
      <p class="body-copy section-note reveal" data-delay="1">These are concept projects, not fake
        client claims. Each one is a real, working website — built, screenshotted, and shown here to
        demonstrate how the visual system, customer path, and page hierarchy change per business.</p>
    </div>

    <div class="archive">
      {archive_a(apex)}
      {archive_b(noir)}
      {archive_c(ever)}
    </div>

    <div class="button-row" style="margin-top:36px">
      <a class="button" href="work.html">Open the full archive <span aria-hidden="true">&#8599;</span></a>
    </div>
  </section>

  <!-- ============ 03 / SERVICES ============ -->
  <section class="section shell" aria-labelledby="offer-title">
    <div class="section-index">
      <b>03</b><span class="spacer" aria-hidden="true"></span><span>What I build / Scope</span>
    </div>
    <div class="section-head">
      <h2 class="display-sm reveal" id="offer-title">Websites with a<br><em>business purpose.</em></h2>
      <p class="body-copy section-note reveal" data-delay="1">Choose the closest starting point. The
        final scope is adjusted around the business, not forced into a rigid template.</p>
    </div>
    <div class="offer">{offer_rows}</div>
    <div class="button-row" style="margin-top:32px">
      <a class="button dark" href="services.html#recommender">Find my package <span aria-hidden="true">&#8599;</span></a>
      <a class="button" href="audit.html">Score my current site <span aria-hidden="true">&#8594;</span></a>
    </div>
  </section>

  <!-- ============ 04 / PROCESS ============ -->
  <section class="section shell" aria-labelledby="process-title">
    <div class="section-index">
      <b>04</b><span class="spacer" aria-hidden="true"></span><span>Process / Documentation</span>
    </div>
    <div class="section-head">
      <h2 class="display-sm reveal" id="process-title">How the work<br><em>gets made.</em></h2>
      <p class="body-copy section-note reveal" data-delay="1">A simple project structure keeps decisions
        clear and prevents the build from turning into endless back-and-forth.</p>
    </div>
    <div class="doc">{doc_steps}</div>
  </section>

  <!-- ============ 05 / CLOSE ============ -->
  <section class="section tight shell" aria-labelledby="close-title">
    <div class="section-index">
      <b>05</b><span class="spacer" aria-hidden="true"></span><span>If you came from my email</span>
    </div>
    <div class="section-head">
      <h2 class="display-sm reveal" id="close-title">You do not need <br class="brk">to decide today.
        <em>Just compare.</em></h2>
      <div class="section-note reveal" data-delay="1">
        <p class="body-copy">Look at your current site, look at the work here, and decide whether the
          difference matters to your business. If it does, send me the project and I&rsquo;ll tell you
          what I would change first.</p>
        <div class="button-row" style="margin-top:26px">
          <a class="button dark" href="contact.html">Request a project quote <span aria-hidden="true">&#8599;</span></a>
          <a class="button" href="audit.html">Score my current site <span aria-hidden="true">&#8594;</span></a>
        </div>
      </div>
    </div>
    <div class="ticks-lg reveal draw" aria-hidden="true"></div>
  </section>
</main>
"""

    return page(
        "index.html",
        "KRD Websmith — Web design for service businesses in Kitchener, Ontario",
        "KRD Websmith builds custom websites for service businesses that need a stronger first "
        "impression, a clearer customer path, and a real inquiry route. Kitchener, Ontario.",
        body,
    )


# ===========================================================================
# WORK
# ===========================================================================


def build_work():
    items = []
    for i, p in enumerate(PROJECTS):
        comp = ["comp-a", "comp-b", "comp-c"][i]
        if comp == "comp-b":
            visual = f"""<div class="mobile-led">
      {device(f"assets/shots/{p['slug']}-mobile-full.webp", f"{p['plain']} concept on a phone", vh=520)}
      {browser(f"assets/shots/{p['slug']}-desktop.webp", f"{p['plain']} concept homepage", p['url'])}
    </div>
    {caption("Responsive pair", "390 × 844 + 1440 × 900")}"""
        elif comp == "comp-c":
            visual = f"""<div class="stacked-shots">
      <div>{browser(f"assets/shots/{p['slug']}-desktop.webp", f"{p['plain']} concept homepage", p['url'])}{caption("Home", "1440 × 900")}</div>
      <div>{browser(f"assets/shots/{p['slug']}-detail.webp", f"Interface detail from the {p['plain']} concept", p['url'], dim="Detail")}{caption("Interface detail", "Crop")}</div>
    </div>"""
        else:
            visual = f"""{browser(f"assets/shots/{p['slug']}-desktop-full.webp", f"{p['plain']} concept homepage, full page", p['url'], scrolls=True, vh=500)}
    {caption("Full page / hover to scroll", "1440 × 900")}"""

        meta_inner = f"""<p class="label">Project / {p['num']}</p>
    <h3>{p['name']}</h3>
    <dl class="metalist">
      <div><dt>Category</dt><dd>{p['category']}</dd></div>
      <div><dt>Type</dt><dd>Service business</dd></div>
      <div><dt>Role</dt><dd>Design + development</dd></div>
      <div><dt>Viewport</dt><dd>Responsive</dd></div>
      <div><dt>Status</dt><dd>Concept project</dd></div>
    </dl>
    <p class="body-copy">{p['blurb']}</p>
    <div class="archive-tags">{"".join(f"<span>{t}</span>" for t in p['tags'])}</div>
    <p style="margin-top:6px"><a class="textlink" href="{p['page']}">Open case study <span aria-hidden="true">&#8599;</span></a></p>"""

        if comp == "comp-c":
            meta = f"""<div class="archive-meta reveal">
    <div><p class="label">Project / {p['num']}</p><h3>{p['name']}</h3></div>
    <div>
      <p class="body-copy">{p['blurb']}</p>
      <div class="archive-tags" style="margin-top:16px">{"".join(f"<span>{t}</span>" for t in p['tags'])}</div>
      <p style="margin-top:18px"><a class="textlink" href="{p['page']}">Open case study <span aria-hidden="true">&#8599;</span></a></p>
    </div>
  </div>"""
        else:
            meta = f'<div class="archive-meta reveal">{meta_inner}</div>'

        items.append(f"""<article class="archive-item {comp}">
  {meta}
  <div class="archive-visual reveal" data-delay="1">
    {visual}
  </div>
</article>""")

    body = f"""<main id="main">
  {breadcrumbs("Work")}
  <section class="page-hero shell">
    <div class="page-hero-grid">
      <div>
        <p class="label">Selected work / Archive</p>
        <h1 class="display">Built to fit<br><em>the business.</em></h1>
      </div>
      <div class="page-hero-aside">
        <p class="body-copy">Each project changes because the customer, offer, tone, and conversion
          goal change. These are concept studies, built as real working websites to demonstrate range.</p>
        <div class="page-actions button-row">
          <a class="button dark" href="contact.html">Start a project <span aria-hidden="true">&#8599;</span></a>
          <a class="button" href="services.html">View services <span aria-hidden="true">&#8594;</span></a>
        </div>
      </div>
    </div>
  </section>

  <section class="section shell">
    <div class="section-index">
      <b>Archive</b><span class="spacer" aria-hidden="true"></span><span>003 projects / All concept</span>
    </div>
    <h2 class="sr-only">Project archive</h2>
    <div class="archive">{"".join(items)}</div>
  </section>

  {next_step("Next step", "Seen enough? Find the right package or start the conversation.", [
      '<a class="button" href="services.html#recommender">Recommend my package</a>',
      '<a class="button dark" href="contact.html">Start a project <span aria-hidden="true">&#8599;</span></a>',
  ])}
</main>
"""
    return page(
        "work.html",
        "Work — KRD Websmith",
        "Concept website projects by KRD Websmith: APEX Auto Detailing, NOIR HOUSE and EVERCREST "
        "Outdoor. Real working builds shown at desktop and mobile.",
        body,
    )


# ===========================================================================
# CASE STUDIES
# ===========================================================================


def build_case(p):
    others = [q for q in PROJECTS if q["slug"] != p["slug"]]
    prev_p, next_p = others[0], others[-1]

    body = f"""<main id="main">
  {breadcrumbs(p['plain'])}
  <section class="page-hero shell">
    <div class="page-hero-grid">
      <div>
        <p class="label">Project / {p['num']} &nbsp;·&nbsp; Concept project</p>
        <h1 class="display">{p['name']}</h1>
      </div>
      <div class="page-hero-aside">
        <p class="body-copy">{p['blurb']}</p>
        <div class="page-actions button-row">
          <a class="button dark" href="contact.html?project={p['plain'].replace(' ', '%20')}">Build something like this <span aria-hidden="true">&#8599;</span></a>
          <a class="button" href="work.html">Back to work <span aria-hidden="true">&#8592;</span></a>
        </div>
      </div>
    </div>
  </section>

  <section class="section tight shell">
    <div class="reveal mask">
      {browser(f"assets/shots/{p['slug']}-desktop.webp", f"{p['plain']} concept homepage", p['url'], lazy=False)}
      {caption(f"{p['category']} / concept homepage", "1440 × 900")}
    </div>
  </section>

  <section class="shell">
    <dl class="metalist" style="grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:0 40px">
      <div><dt>Client</dt><dd>Concept project</dd></div>
      <div><dt>Industry</dt><dd>{p['category']}</dd></div>
      <div><dt>Role</dt><dd>Design + development</dd></div>
      <div><dt>Year</dt><dd>2026</dd></div>
      <div><dt>Status</dt><dd>Concept &mdash; not a commissioned build</dd></div>
      <div><dt>Output</dt><dd>Responsive website</dd></div>
    </dl>
  </section>

  <section class="section shell">
    <div class="section-head">
      <h2 class="display-sm reveal">{p['tagline'].split(' / ')[0]}<br><em>documented.</em></h2>
      <p class="body-copy section-note reveal" data-delay="1">The goal is not to make every project
        look like KRD Websmith. The goal is to make each interface feel native to the business it
        represents.</p>
    </div>

    <div class="doc" style="border-top:0">
      <article class="case-chapter">
        <div class="case-text reveal">
          <p class="label">01 / Context</p>
          <h2>What existed before</h2>
          <p>{p['category']} businesses in this category typically run a template site or a social
            profile. There was no prior KRD build to redesign, so this starts from the category
            itself: what a customer actually needs to see before they commit.</p>
        </div>
        <div class="case-visual reveal" data-delay="1">
          {browser(f"assets/shots/{p['slug']}-desktop.webp", f"{p['plain']} concept homepage above the fold", p['url'])}
          {caption("Above the fold", "1440 × 900")}
        </div>
      </article>

      <article class="case-chapter">
        <div class="case-text reveal">
          <p class="label">02 / Problem</p>
          <h2>What was not working</h2>
          <p>{p['challenge']}</p>
        </div>
        <div class="case-visual reveal" data-delay="1">
          {browser(f"assets/shots/{p['slug']}-detail.webp", f"Interface detail from the {p['plain']} concept", p['url'], dim="Detail")}
          {caption("Interface detail", "Crop")}
        </div>
      </article>

      <article class="case-chapter">
        <div class="case-text reveal">
          <p class="label">03 / Direction</p>
          <h2>The design approach</h2>
          <p>{p['direction']}</p>
          <div class="archive-tags">{"".join(f"<span>{t}</span>" for t in p['tags'])}</div>
        </div>
        <div class="case-visual reveal" data-delay="1">
          {browser(f"assets/shots/{p['slug']}-desktop-full.webp", f"{p['plain']} concept, full page", p['url'], scrolls=True, vh=480)}
          {caption("Full page / hover to scroll", "1440 × 900")}
        </div>
      </article>

      <article class="case-chapter">
        <div class="case-text reveal">
          <p class="label">04 / Build</p>
          <h2>How it was implemented</h2>
          <p>Hand-written semantic HTML and CSS with a small amount of JavaScript. A single type and
            spacing system, real photography, and no framework overhead — so the page stays fast and
            the layout holds at every width.</p>
          <dl class="metalist">
            <div><dt>Markup</dt><dd>Semantic HTML</dd></div>
            <div><dt>Styling</dt><dd>Hand-written CSS</dd></div>
            <div><dt>Motion</dt><dd>Restrained, reduced-motion safe</dd></div>
          </dl>
        </div>
        <div class="case-visual reveal" data-delay="1">
          {browser(f"assets/shots/{p['slug']}-detail.webp", f"Component detail from the {p['plain']} concept", p['url'], dim="Component")}
          {caption("Component / detail", "Crop")}
        </div>
      </article>

      <article class="case-chapter">
        <div class="case-text reveal">
          <p class="label">05 / Mobile</p>
          <h2>How it adapts</h2>
          <p>The phone layout is designed, not stacked. Type scales down deliberately, touch targets
            stay large, metadata compresses, and the primary action stays reachable without hunting.</p>
        </div>
        <div class="case-visual reveal" data-delay="1">
          <div class="responsive-pair">
            <div>
              {browser(f"assets/shots/{p['slug']}-desktop.webp", f"{p['plain']} concept on desktop", p['url'])}
              {caption("Desktop", "1440 × 900")}
            </div>
            <div>
              {device(f"assets/shots/{p['slug']}-mobile.webp", f"{p['plain']} concept on a phone", crop=False)}
              {caption("Phone", "390 × 844")}
            </div>
          </div>
        </div>
      </article>

      <article class="case-chapter full">
        <div class="case-text reveal" style="position:static">
          <p class="label">06 / Result</p>
          <h2>The finished website</h2>
          <p class="measure">{p['purpose']}</p>
        </div>
        <div class="case-visual reveal" data-delay="1">
          {browser(f"assets/shots/{p['slug']}-mobile-full.webp", f"{p['plain']} concept full mobile page", p['url'], dim="390 × 844", scrolls=True, vh=560)}
          {caption("Full mobile page / hover to scroll", "390 × 844")}
        </div>
      </article>
    </div>
  </section>

  {next_step("Archive", f"Next project: {next_p['plain']}.", [
      f'<a class="button" href="{prev_p["page"]}"><span aria-hidden="true">&#8592;</span> {prev_p["plain"]}</a>',
      f'<a class="button" href="{next_p["page"]}">{next_p["plain"]} <span aria-hidden="true">&#8594;</span></a>',
      f'<a class="button dark" href="contact.html?project={p["plain"].replace(" ", "%20")}">Start a similar project <span aria-hidden="true">&#8599;</span></a>',
  ])}
</main>
"""
    return page(
        p["page"],
        f"{p['plain']} — concept project by KRD Websmith",
        f"{p['blurb']} A concept website project by KRD Websmith, Kitchener, Ontario.",
        body,
    )


# ===========================================================================
# SERVICES
# ===========================================================================

SERVICES_CSS = """
    .tier{border-top:1px solid var(--rule);padding-block:clamp(40px,5vw,80px);
      display:grid;grid-template-columns:74px 1fr .95fr;gap:clamp(20px,3vw,48px);align-items:start}
    .tier:last-of-type{border-bottom:1px solid var(--rule)}
    .tier h2{font:800 clamp(32px,4.4vw,68px)/.92 var(--sans);letter-spacing:-.05em;text-transform:uppercase}
    .tier-lede{margin:16px 0 0;color:var(--muted);font-size:15px;line-height:1.78;max-width:46ch}
    .tier-price{margin-top:22px;display:flex;flex-wrap:wrap;align-items:baseline;gap:14px}
    .tier-price b{font:800 clamp(22px,2.2vw,30px) var(--sans);letter-spacing:-.03em}
    .tier-price span{font:600 10px var(--mono);text-transform:uppercase;letter-spacing:.13em;color:var(--blue)}
    .tier-list{display:grid;gap:0;border-top:1px solid var(--line)}
    .tier-list span{display:flex;align-items:center;gap:12px;padding:11px 0;
      border-bottom:1px solid var(--line);font:500 11px var(--mono);
      text-transform:uppercase;letter-spacing:.09em}
    .tier-list span::before{content:"";width:6px;height:6px;background:var(--blue);flex:none}
    .tier-visual{margin-top:22px}

    .rec{border:1px solid var(--rule);background:var(--paper-2);
      padding:clamp(24px,3.4vw,52px);display:grid;
      grid-template-columns:.85fr 1.15fr;gap:clamp(28px,4vw,60px);align-items:start}
    .rec-steps{display:grid;gap:26px}
    .rec-step h3{font:600 20px var(--serif);letter-spacing:-.02em;text-transform:none;
      font-weight:600;margin-bottom:12px}
    .rec-options{display:flex;flex-wrap:wrap;gap:8px}
    .rec-options button,.choices button{
      min-height:44px;padding:0 15px;background:transparent;
      border:1px solid var(--line-2);cursor:pointer;
      font:600 10px var(--mono);text-transform:uppercase;letter-spacing:.1em;
      transition:background .25s ease,color .25s ease,border-color .25s ease}
    .rec-options button:hover,.choices button:hover{border-color:var(--ink)}
    .rec-options button.active,.choices button.active{
      background:var(--blue);border-color:var(--blue);color:#fff}
    .rec-result{margin-top:8px;padding-top:26px;border-top:1px solid var(--line);
      opacity:.35;transition:opacity .4s ease}
    .rec-result.show{opacity:1}
    .rec-result h3{margin:12px 0 10px;font:800 clamp(26px,3vw,40px) var(--sans);
      letter-spacing:-.04em;text-transform:uppercase}
    .rec-result p{color:var(--muted);font-size:14px;line-height:1.75;margin-bottom:22px}
    .rec-result[aria-hidden="true"] .button{pointer-events:none}
    .rec-result.show .button{pointer-events:auto}
    @media(max-width:1100px){
      .tier{grid-template-columns:56px 1fr}
      .tier-side{grid-column:2}
      .rec{grid-template-columns:1fr}
    }
    @media(max-width:760px){
      .tier{grid-template-columns:1fr;gap:14px}
      .tier-side{grid-column:auto}
      .tier-lede{max-width:none}
    }
"""

SERVICES_JS = """
const answers={};
document.querySelectorAll(".rec-step").forEach(step=>step.querySelectorAll("button").forEach(btn=>btn.addEventListener("click",()=>{
  step.querySelectorAll("button").forEach(x=>{x.classList.remove("active");x.setAttribute("aria-pressed","false")});
  btn.classList.add("active");btn.setAttribute("aria-pressed","true");
  answers[step.dataset.key]=Number(btn.dataset.v);
  if(Object.keys(answers).length===3){
    const score=Object.values(answers).reduce((a,b)=>a+b,0);
    let title,text;
    if(score<=5){title="Business Website";text="Focused scope. Keep the build clear and useful without paying for complexity you do not need."}
    else if(score<=10){title="Growth Website";text="Your project benefits from more pages, stronger lead paths, and a fuller content system."}
    else{title="Advanced Build";text="The scope points toward custom functionality or deeper systems that should be quoted individually."}
    document.getElementById("recTitle").textContent=title;
    document.getElementById("recText").textContent=text;
    document.getElementById("recContact").href="contact.html?package="+encodeURIComponent(title);
    const box=document.getElementById("recResult");
    box.classList.add("show");
    box.setAttribute("aria-hidden","false");
  }
})));
"""


def build_services():
    tiers = []
    for s in SERVICES:
        tiers.append(f"""<section class="tier">
  <span class="num">{s['num']}</span>
  <div>
    <h2>{s['name']}</h2>
    <p class="tier-lede">{s['copy']}</p>
    <div class="tier-price">
      <b>{s['price']}</b><span>{s['scope']}</span>
    </div>
    <div class="button-row" style="margin-top:24px">
      <a class="button dark" href="contact.html?package={s['name'].replace(' ', '%20')}">Start with this <span aria-hidden="true">&#8599;</span></a>
    </div>
  </div>
  <div class="tier-side">
    <div class="tier-list">{"".join(f"<span>{i}</span>" for i in s['includes'])}</div>
    <div class="tier-visual">
      <div class="frame" style="aspect-ratio:16/10">{shot(s['peek'], s['peek_alt'], cls="")}</div>
      {caption("Example / concept work", "Detail")}
    </div>
  </div>
</section>""")

    body = f"""<main id="main">
  {breadcrumbs("Services")}
  <section class="page-hero shell">
    <div class="page-hero-grid">
      <div>
        <p class="label">Services / Scope</p>
        <h1 class="display">Buy the<br><em>right thing.</em></h1>
      </div>
      <div class="page-hero-aside">
        <p class="body-copy">Clear starting points without locking the project into a rigid template.
          The scope should fit the business.</p>
        <div class="page-actions button-row">
          <a class="button" href="#recommender">Find my package <span aria-hidden="true">&#8595;</span></a>
          <a class="button dark" href="contact.html">Start a project <span aria-hidden="true">&#8599;</span></a>
        </div>
      </div>
    </div>
  </section>

  <div class="shell section tight">
    {"".join(tiers)}
  </div>

  <section class="section shell" id="recommender">
    <div class="section-index">
      <b>Tool</b><span class="spacer" aria-hidden="true"></span><span>Package recommender / 003 questions</span>
    </div>
    <div class="section-head">
      <h2 class="display-sm">Tell me the shape.<br><em>I&rsquo;ll narrow the scope.</em></h2>
      <p class="body-copy section-note">This gives you a starting point. It is not a binding quote.</p>
    </div>

    <div class="rec">
      <div class="rec-steps">
        <div class="rec-step" data-key="pages">
          <h3>How much content?</h3>
          <div class="rec-options">
            <button type="button" data-v="1" aria-pressed="false">1&ndash;3 pages</button>
            <button type="button" data-v="2" aria-pressed="false">4&ndash;7 pages</button>
            <button type="button" data-v="4" aria-pressed="false">8+ pages</button>
          </div>
        </div>
        <div class="rec-step" data-key="features">
          <h3>How custom?</h3>
          <div class="rec-options">
            <button type="button" data-v="1" aria-pressed="false">Standard business site</button>
            <button type="button" data-v="3" aria-pressed="false">Custom interactions</button>
            <button type="button" data-v="6" aria-pressed="false">Advanced features</button>
          </div>
        </div>
        <div class="rec-step" data-key="goal">
          <h3>Main goal?</h3>
          <div class="rec-options">
            <button type="button" data-v="1" aria-pressed="false">Look professional</button>
            <button type="button" data-v="3" aria-pressed="false">Generate leads</button>
            <button type="button" data-v="5" aria-pressed="false">Build something unique</button>
          </div>
        </div>
      </div>

      <div class="rec-result" id="recResult" aria-live="polite" aria-hidden="true">
        <p class="label">Recommended fit</p>
        <h3 id="recTitle">Answer the three questions</h3>
        <p id="recText">A recommendation appears here once all three are selected.</p>
        <a class="button dark" id="recContact" href="contact.html">Start with this package <span aria-hidden="true">&#8599;</span></a>
      </div>
    </div>
  </section>

  {next_step("Next step", "Know what you need now?", [
      '<a class="button" href="work.html">See examples</a>',
      '<a class="button" href="process.html">See process</a>',
      '<a class="button dark" href="contact.html">Start a project <span aria-hidden="true">&#8599;</span></a>',
  ])}
</main>
"""
    return page(
        "services.html",
        "Services — KRD Websmith",
        "Three clear website packages from KRD Websmith: Business Website from $300 CAD, Growth "
        "Website from $500 CAD, and Advanced Build quoted by scope.",
        body,
        extra_css=SERVICES_CSS,
        extra_js=SERVICES_JS,
    )


# ===========================================================================
# PROCESS
# ===========================================================================


def build_process():
    steps = "".join(
        f"""<div class="doc-step reveal">
  <span class="num">{num}</span>
  <div>
    <h3>{title}</h3>
    <div class="doc-terms">{"".join(f"<span>{t}</span>" for t in terms)}</div>
  </div>
  <div class="doc-body">
    <p>{copy}</p>
    <p class="meta">{out}</p>
  </div>
</div>"""
        for num, title, terms, copy, out in PROCESS
    )

    body = f"""<main id="main">
  {breadcrumbs("Process")}
  <section class="page-hero shell">
    <div class="page-hero-grid">
      <div>
        <p class="label">Process / Scope to launch</p>
        <h1 class="display">How the work<br><em>gets made.</em></h1>
      </div>
      <div class="page-hero-aside">
        <p class="body-copy">You should know what is happening, what I need from you, and what comes
          next. No mystery, no invented ceremony.</p>
        <div class="page-actions button-row">
          <a class="button dark" href="contact.html">Start a project <span aria-hidden="true">&#8599;</span></a>
          <a class="button" href="services.html">See services <span aria-hidden="true">&#8594;</span></a>
        </div>
      </div>
    </div>
  </section>

  <section class="section shell">
    <div class="section-index">
      <b>Documentation</b><span class="spacer" aria-hidden="true"></span><span>005 stages / Scope to launch</span>
    </div>
    <h2 class="sr-only">The five stages</h2>
    <div class="doc">{steps}</div>
  </section>

  <section class="section tight shell">
    <div class="section-head">
      <h2 class="display-sm reveal">What you get<br><em>at every stage.</em></h2>
      <p class="body-copy section-note reveal" data-delay="1">Each stage ends with something you can
        look at and respond to, so the project never disappears into silence.</p>
    </div>
    <div class="reveal mask">
      <div class="frame" style="aspect-ratio:21/9">
        <img src="assets/img/desk-1400.webp"
             srcset="assets/img/desk-800.webp 800w, assets/img/desk-1400.webp 1400w, assets/img/desk-2000.webp 2000w"
             sizes="(max-width:760px) 100vw, 1400px"
             alt="A working desk with a website design in progress"
             width="1400" height="933" loading="lazy" decoding="async">
        <span class="frame-tag">Scope &#8594; Direction &#8594; Build &#8594; Refine &#8594; Release</span>
      </div>
    </div>
  </section>

  {next_step("Next step", "Want to see the process applied?", [
      '<a class="button" href="work.html">View work</a>',
      '<a class="button" href="services.html#recommender">Find my package</a>',
      '<a class="button dark" href="contact.html">Start a project <span aria-hidden="true">&#8599;</span></a>',
  ])}
</main>
"""
    return page(
        "process.html",
        "Process — KRD Websmith",
        "How a KRD Websmith project runs: understand, direction, build, refine, release. Clear "
        "stages, clear deliverables, no mystery.",
        body,
    )


# ===========================================================================
# ABOUT
# ===========================================================================

ABOUT_PRINCIPLES = [
    ("01", "Clear communication", "You know what is happening, what is needed, and what the next step is."),
    ("02", "Customer-first decisions", "Navigation, content, and calls to action are built around how real visitors use the site."),
    ("03", "No fake proof", "No invented testimonials, fake client logos, or made-up performance numbers."),
    ("04", "Built to grow", "The structure can expand as the business adds services, pages, and stronger systems."),
]


def build_about():
    principles = "".join(
        f"""<div class="doc-step reveal">
  <span class="num">{num}</span>
  <div><h3>{title}</h3></div>
  <div class="doc-body"><p>{copy}</p></div>
</div>"""
        for num, title, copy in ABOUT_PRINCIPLES
    )

    body = f"""<main id="main">
  {breadcrumbs("About")}
  <section class="page-hero shell">
    <div class="page-hero-grid">
      <div>
        <p class="label">About / KRD</p>
        <h1 class="display">Small studio.<br><em>Direct process.</em></h1>
      </div>
      <div class="page-hero-aside">
        <p class="body-copy">You work directly with the person designing and building the website.
          Fewer layers means clearer communication and fewer lost details.</p>
        <div class="page-actions button-row">
          <a class="button dark" href="contact.html">Start a project <span aria-hidden="true">&#8599;</span></a>
          <a class="button" href="work.html">See the work <span aria-hidden="true">&#8594;</span></a>
        </div>
      </div>
    </div>
  </section>

  <section class="section shell">
    <div class="section-index">
      <b>Studio</b><span class="spacer" aria-hidden="true"></span><span>KRD / Independent practice</span>
    </div>
    <div class="section-head">
      <h2 class="display-sm reveal">Direct contact.<br><em>Real attention.</em></h2>
      <div class="section-note reveal" data-delay="1">
        <dl class="metalist">
          <div><dt>Studio</dt><dd>KRD Websmith</dd></div>
          <div><dt>Based</dt><dd>Kitchener, Ontario</dd></div>
          <div><dt>Works</dt><dd>Local + remote</dd></div>
          <div><dt>Size</dt><dd>Independent practice</dd></div>
        </dl>
      </div>
    </div>

    <div class="trust-item t1" style="border-bottom:0;padding-top:0">
      <div class="trust-head reveal">
        <p class="body-copy lead">KRD Websmith is a web design and development studio based in
          Kitchener, Ontario. I build custom websites for local businesses that want something
          clearer, more credible, and more considered than a premade template.</p>
        <p class="body-copy">The priority is the customer experience. The site should be easy to
          understand, easy to use, and easy to act on. The code and the motion only matter when they
          support that.</p>
        <p><a class="textlink" href="process.html">See the process <span aria-hidden="true">&#8594;</span></a></p>
      </div>
      <div class="archive-visual reveal mask" data-delay="1">
        <div class="frame" style="aspect-ratio:4/3">
          <img src="assets/img/studio-1400.webp"
               srcset="assets/img/studio-800.webp 800w, assets/img/studio-1400.webp 1400w, assets/img/studio-2000.webp 2000w"
               sizes="(max-width:1100px) 100vw, 720px"
               alt="A quiet studio workspace" width="1400" height="934" loading="lazy" decoding="async">
          <span class="frame-tag">Kitchener, Ontario / Remote</span>
        </div>
      </div>
    </div>
  </section>

  <section class="section tight shell">
    <div class="section-index">
      <b>How I work</b><span class="spacer" aria-hidden="true"></span><span>004 principles</span>
    </div>
    <div class="doc">{principles}</div>
  </section>

  {next_step("Next step", "Want to see how I work or what a project costs?", [
      '<a class="button" href="process.html">Process</a>',
      '<a class="button" href="services.html">Services</a>',
      '<a class="button dark" href="contact.html">Contact <span aria-hidden="true">&#8599;</span></a>',
  ])}
</main>
"""
    return page(
        "about.html",
        "About — KRD Websmith",
        "KRD Websmith is a small independent web design and development studio in Kitchener, "
        "Ontario. You work directly with the person building your website.",
        body,
    )


# ===========================================================================
# AUDIT
# ===========================================================================

AUDIT_CSS = """
    .question{padding-block:clamp(26px,3vw,40px);border-bottom:1px solid var(--line);
      display:grid;grid-template-columns:74px 1fr .8fr;gap:clamp(18px,3vw,40px);align-items:center}
    .question h3{font:800 clamp(20px,2.2vw,30px)/1.1 var(--sans);letter-spacing:-.035em;text-transform:uppercase}
    .choices{display:flex;flex-wrap:wrap;gap:8px;justify-content:flex-end}
    .audit-result{border:1px solid var(--rule);background:var(--paper-2);
      padding:clamp(24px,3.4vw,48px);opacity:.4;transition:opacity .4s ease}
    .audit-result.show{opacity:1}
    .score{font:800 clamp(56px,9vw,132px)/.85 var(--sans);letter-spacing:-.06em}
    .audit-result h3{margin:14px 0 10px;font:600 clamp(22px,2.4vw,32px) var(--serif);
      letter-spacing:-.02em;text-transform:none;font-weight:600}
    .audit-result > p{color:var(--muted);font-size:15px;line-height:1.75}
    .bars{margin-top:30px;display:grid;gap:0;border-top:1px solid var(--line)}
    .barrow{display:grid;grid-template-columns:.9fr 1.6fr auto;gap:16px;align-items:center;
      padding:12px 0;border-bottom:1px solid var(--line)}
    .barrow span{font:600 10px var(--mono);text-transform:uppercase;letter-spacing:.12em}
    .barrow .bar{height:6px;background:var(--paper-3)}
    .barrow .bar i{display:block;height:100%;background:var(--blue);transition:width .6s var(--ease)}
    .barrow b{font:600 11px var(--mono);letter-spacing:.06em;min-width:34px;text-align:right}
    @media(max-width:900px){
      .question{grid-template-columns:56px 1fr;gap:14px}
      .choices{grid-column:2;justify-content:flex-start}
    }
    @media(max-width:760px){
      .question{grid-template-columns:1fr}
      .choices{grid-column:auto}
      .barrow{grid-template-columns:1fr auto;gap:8px 12px}
      .barrow .bar{grid-column:1/-1}
    }
"""

AUDIT_JS = """
const ans={},labels={appearance:"Visual credibility",mobile:"Mobile usability",clarity:"Offer clarity",action:"Conversion path",confidence:"Overall confidence"};
document.querySelectorAll(".question").forEach(q=>q.querySelectorAll("button").forEach(b=>b.addEventListener("click",()=>{
  q.querySelectorAll("button").forEach(x=>{x.classList.remove("active");x.setAttribute("aria-pressed","false")});
  b.classList.add("active");b.setAttribute("aria-pressed","true");
  ans[q.dataset.key]={v:Number(b.dataset.v),w:Number(q.dataset.weight)};
  if(Object.keys(ans).length===5){
    const total=Math.round(Object.values(ans).reduce((s,x)=>s+x.v*x.w,0));
    const weak=Object.entries(ans).sort((a,b)=>(a[1].v*a[1].w)-(b[1].v*b[1].w))[0][0];
    document.getElementById("score").textContent=total+"/100";
    document.getElementById("resultTitle").textContent=total>=80?"Strong foundation.":total>=55?"Good base, but there is friction.":"The site may be underselling the business.";
    document.getElementById("resultText").textContent="The first area I would inspect is "+labels[weak]+".";
    document.getElementById("bars").innerHTML=Object.entries(ans).map(([k,x])=>`<div class="barrow"><span>${labels[k]}</span><div class="bar"><i style="width:${Math.round(x.v*100)}%"></i></div><b>${Math.round(x.v*100)}</b></div>`).join("");
    document.getElementById("auditContact").href="contact.html?audit="+total+"&focus="+encodeURIComponent(labels[weak]);
    const box=document.getElementById("result");
    box.classList.add("show");
    box.setAttribute("aria-hidden","false");
  }
})));
"""

AUDIT_QUESTIONS = [
    ("appearance", "15", "Does the site look current and credible?", ["Yes", "Somewhat", "No"]),
    ("mobile", "25", "Is it genuinely easy to use on a phone?", ["Yes", "Mostly", "No"]),
    ("clarity", "25", "Can a visitor tell what you sell quickly?", ["Yes", "Maybe", "No"]),
    ("action", "20", "Is the next step obvious?", ["Yes", "Sometimes", "No"]),
    ("confidence", "15", "Would you confidently send a new customer there?", ["Yes", "Depends", "No"]),
]


def build_audit():
    vals = ["1", ".5", "0"]
    questions = "".join(
        f"""<div class="question" data-key="{key}" data-weight="{weight}">
  <span class="num">{str(i + 1).zfill(2)}</span>
  <h3>{q}</h3>
  <div class="choices" role="group" aria-label="{q}">
    {"".join(f'<button type="button" data-v="{vals[j]}" aria-pressed="false">{opt}</button>' for j, opt in enumerate(opts))}
  </div>
</div>"""
        for i, (key, weight, q, opts) in enumerate(AUDIT_QUESTIONS)
    )

    body = f"""<main id="main">
  {breadcrumbs("Audit")}
  <section class="page-hero shell">
    <div class="page-hero-grid">
      <div>
        <p class="label">Quick website audit / 005 questions</p>
        <h1 class="display">Five questions.<br><em>One clearer step.</em></h1>
      </div>
      <div class="page-hero-aside">
        <p class="body-copy">Answer honestly about your current website. The score is weighted by
          what actually affects whether a visitor becomes an inquiry.</p>
        <div class="page-actions button-row">
          <a class="button" href="services.html#recommender">Find my package <span aria-hidden="true">&#8594;</span></a>
        </div>
      </div>
    </div>
  </section>

  <section class="section shell">
    <div class="section-index">
      <b>Weighted by impact</b><span class="spacer" aria-hidden="true"></span><span>Utility before decoration</span>
    </div>
    <h2 class="sr-only">The five questions</h2>
    <div class="doc">{questions}</div>
  </section>

  <section class="section tight shell">
    <div class="audit-result" id="result" aria-live="polite" aria-hidden="true">
      <p class="label">Result</p>
      <div class="score" id="score">0/100</div>
      <h3 id="resultTitle">Answer the five questions above.</h3>
      <p id="resultText">Your weakest area and a suggested first fix appear here.</p>
      <div class="bars" id="bars"></div>
      <div class="button-row" style="margin-top:28px">
        <a class="button dark" id="auditContact" href="contact.html">Ask about a redesign <span aria-hidden="true">&#8599;</span></a>
        <a class="button" href="services.html#recommender">Find my package <span aria-hidden="true">&#8594;</span></a>
      </div>
    </div>
  </section>

  {next_step("Next step", "Use your result to decide what to improve first.", [
      '<a class="button" href="work.html">See the work</a>',
      '<a class="button dark" href="contact.html">Start a project <span aria-hidden="true">&#8599;</span></a>',
  ])}
</main>
"""
    return page(
        "audit.html",
        "Website audit — KRD Websmith",
        "A free five-question website audit. Score your current site on credibility, mobile "
        "usability, offer clarity and conversion path.",
        body,
        extra_css=AUDIT_CSS,
        extra_js=AUDIT_JS,
    )


# ===========================================================================
# CONTACT  — the form contract below is preserved exactly
# ===========================================================================

CONTACT_CSS = """
    .contact-layout{display:grid;grid-template-columns:.74fr 1.26fr;
      gap:clamp(32px,5vw,80px);align-items:start}
    .contact-info{position:sticky;top:108px}
    .contact-form{border-top:1px solid var(--rule)}
    .progress{height:5px;background:var(--paper-3);margin-bottom:8px}
    .progress i{display:block;height:100%;width:0;background:var(--blue);transition:width .3s var(--ease)}
    .progress-meta{display:flex;justify-content:space-between;
      font:600 10px var(--mono);text-transform:uppercase;letter-spacing:.12em;
      color:var(--muted);margin-bottom:20px}
    .form-grid{display:grid;grid-template-columns:1fr 1fr;gap:0 clamp(20px,3vw,36px)}
    .contact-form label{display:block;padding:18px 0 16px;border-bottom:1px solid var(--line)}
    .contact-form label > span{display:block;margin-bottom:10px;color:var(--blue);
      font:600 10px var(--mono);text-transform:uppercase;letter-spacing:.13em}
    .contact-form input,.contact-form textarea,.contact-form select{
      width:100%;border:0;background:transparent;padding:10px 0;outline:0;
      font-size:16px;line-height:1.5;color:var(--ink);min-height:30px}
    .contact-form input:focus-visible,.contact-form textarea:focus-visible,
    .contact-form select:focus-visible{outline:2px solid var(--blue);outline-offset:4px}
    .contact-form textarea{resize:vertical;min-height:130px}
    .contact-form select{cursor:pointer}
    .field-error{min-height:15px;margin-top:6px;color:#9C2B20;
      font:500 11px var(--mono);letter-spacing:.04em}
    .submit{margin-top:26px;width:100%;max-width:340px}
    .form-status{margin-top:16px;min-height:20px;
      font:600 11px var(--mono);text-transform:uppercase;letter-spacing:.1em}
    .form-status.ok{color:var(--blue)}
    .form-status.bad{color:#9C2B20}
    @media(max-width:1000px){
      .contact-layout{grid-template-columns:1fr}
      .contact-info{position:static}
    }
    @media(max-width:760px){
      .form-grid{grid-template-columns:1fr}
      .submit{max-width:none}
    }
"""

# The submit handler, the endpoint and the payload shape are unchanged from the
# live site. Only accessibility wiring (aria-live class, aria-invalid) was added.
CONTACT_JS = """
const form=document.getElementById("contactForm"),req=[...form.querySelectorAll("[required]")],all=[...form.querySelectorAll("input,select,textarea")];
/* Prefill comes from the query string, e.g. contact.html?package=Growth+Website */
const params=new URLSearchParams(location.search);
if(params.get("package")){form.elements.type.value=params.get("package")==="Advanced Build"?"Custom build":params.get("package")==="Growth Website"?"Website redesign":"New business website";form.elements.message.value="Recommended package: "+params.get("package")}
if(params.get("audit"))form.elements.message.value="Website audit score: "+params.get("audit")+"/100. Main focus: "+(params.get("focus")||"website improvement")+".";
if(params.get("project"))form.elements.message.value="I am interested in a project with a similar level of design to "+params.get("project")+".";
function progress(){const done=req.filter(x=>x.value.trim()).length;document.getElementById("progressFill").style.width=Math.round(done/req.length*100)+"%";document.getElementById("progressCount").textContent=done+" / "+req.length+" required"}
all.forEach(x=>{x.addEventListener("input",progress);x.addEventListener("change",progress)});progress();
function valid(f){const e=f.parentElement.querySelector(".field-error");let m="";if(f.required&&!f.value.trim())m="Required.";if(f.type==="email"&&f.value&&!/^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test(f.value))m="Use a valid email.";if(f.type==="url"&&f.value&&!/^https?:\\/\\//i.test(f.value))m="Include https://";if(e)e.textContent=m;f.setAttribute("aria-invalid",m?"true":"false");return !m}
all.forEach(f=>f.addEventListener("blur",()=>valid(f)));
form.addEventListener("submit",async ev=>{
  ev.preventDefault();
  const s=document.getElementById("status");
  if(!all.map(valid).every(Boolean)){s.className="form-status bad";s.textContent="Check the highlighted fields.";const bad=all.find(f=>f.getAttribute("aria-invalid")==="true");if(bad)bad.focus();return}
  const b=form.querySelector(".submit"),old=b.innerHTML;
  b.disabled=true;b.textContent="Sending...";
  s.className="form-status";s.textContent="";
  try{
    const r=await fetch("https://krd-websmith-contact.newonb123.workers.dev",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(Object.fromEntries(new FormData(form).entries()))});
    const data=await r.json();
    if(!r.ok||!data.success)throw new Error(data.error||"Failed");
    s.className="form-status ok";s.textContent="Sent successfully. I\\u2019ll reply by email.";
    form.reset();all.forEach(f=>f.setAttribute("aria-invalid","false"));progress();
  }catch(e){
    s.className="form-status bad";s.textContent="Could not send. Please email hello@krdwebsmith.com.";
  }finally{b.disabled=false;b.innerHTML=old}
});
"""


def build_contact():
    body = f"""<main id="main">
  {breadcrumbs("Contact")}
  <section class="page-hero shell">
    <div class="page-hero-grid">
      <div>
        <p class="label">Start a project / Inquiry</p>
        <h1 class="display">Have a business. <br class="brk">Need the site.
          <em>Let&rsquo;s build it properly.</em></h1>
      </div>
      <div class="page-hero-aside">
        <p class="body-copy">What does the business do, what exists now, and what should the new
          website do better?</p>
        <div class="page-actions button-row">
          <a class="button" href="services.html#recommender">Not sure what you need? <span aria-hidden="true">&#8594;</span></a>
        </div>
      </div>
    </div>
  </section>

  <section class="section shell contact-layout">
    <div class="contact-info">
      <p class="label">Project details</p>
      <h2 class="display-xs" style="margin:14px 0 20px">Good work deserves
        <em>a good front door.</em></h2>
      <p class="body-copy measure">Starter projects begin around $300 CAD. Final quotes depend on
        scope, pages, content, integrations, and revisions.</p>
      <dl class="metalist" style="margin-top:32px">
        <div><dt>Location</dt><dd>Kitchener, Ontario</dd></div>
        <div><dt>Projects</dt><dd>Local + remote</dd></div>
        <div><dt>Email</dt><dd>hello@krdwebsmith.com</dd></div>
        <div><dt>Reply</dt><dd>By email</dd></div>
      </dl>
    </div>

    <form id="contactForm" class="contact-form" novalidate>
      <div class="progress" aria-hidden="true"><i id="progressFill"></i></div>
      <p class="progress-meta"><span>Inquiry / 001</span><span id="progressCount">0 / 5 required</span></p>

      <div class="form-grid">
        <label><span>Name</span>
          <input name="name" required autocomplete="name" autocapitalize="words">
          <div class="field-error"></div></label>
        <label><span>Business</span>
          <input name="business" required autocomplete="organization">
          <div class="field-error"></div></label>
        <label><span>Email</span>
          <input name="email" type="email" required autocomplete="email"
                 inputmode="email" autocapitalize="off" spellcheck="false">
          <div class="field-error"></div></label>
        <label><span>Current website</span>
          <input name="website" type="url" placeholder="https://" inputmode="url"
                 autocapitalize="off" spellcheck="false">
          <div class="field-error"></div></label>
        <label><span>Project type</span>
          <select name="type" required>
            <option value="">Select one</option>
            <option>New business website</option>
            <option>Website redesign</option>
            <option>Landing page</option>
            <option>Custom build</option>
          </select>
          <div class="field-error"></div></label>
        <label><span>Budget</span>
          <select name="budget" required>
            <option value="">Select range</option>
            <option>$300&ndash;$500</option>
            <option>$500&ndash;$800</option>
            <option>$800&ndash;$1,200</option>
            <option>$1,200+</option>
          </select>
          <div class="field-error"></div></label>
      </div>

      <label><span>What do you need?</span>
        <textarea name="message" rows="6"
          placeholder="Tell me about the business, current site, goals, pages, or features."></textarea>
        <div class="field-error"></div></label>

      <button class="button dark submit" type="submit">Send project request
        <span aria-hidden="true">&#8599;</span></button>
      <p class="form-status" id="status" role="status" aria-live="polite"></p>
    </form>
  </section>

  {next_step("Need more context first?", "You can still explore before submitting anything.", [
      '<a class="button" href="work.html">Work</a>',
      '<a class="button" href="services.html">Services</a>',
      '<a class="button" href="process.html">Process</a>',
  ])}
</main>
"""
    return page(
        "contact.html",
        "Contact — KRD Websmith",
        "Start a website project with KRD Websmith. Tell me about the business, the current site, "
        "and what the new website should do better.",
        body,
        extra_css=CONTACT_CSS,
        extra_js=CONTACT_JS,
    )


# ===========================================================================
# extras
# ===========================================================================


def build_extras(pages):
    with open(os.path.join(ROOT, "favicon.svg"), "w", encoding="utf-8") as fh:
        fh.write(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">'
            '<rect width="32" height="32" fill="#111111"/>'
            '<path d="M8 8v16M8 16h5.5l6-8M13.5 16l6 8" stroke="#F4F1EA" stroke-width="2.6" '
            'fill="none" stroke-linecap="square"/>'
            '<rect x="22" y="7" width="4" height="4" fill="#173EAF"/></svg>\n'
        )

    with open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8") as fh:
        fh.write(f"User-agent: *\nAllow: /\nDisallow: /docs/\n\nSitemap: {SITE}/sitemap.xml\n")

    prio = {"index.html": "1.0", "work.html": "0.9", "services.html": "0.9", "contact.html": "0.8"}
    urls = []
    for name in pages:
        loc = f"{SITE}/" if name == "index.html" else f"{SITE}/{name}"
        urls.append(
            f"  <url><loc>{loc}</loc><changefreq>monthly</changefreq>"
            f"<priority>{prio.get(name, '0.7')}</priority></url>"
        )
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as fh:
        fh.write(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + "\n".join(urls)
            + "\n</urlset>\n"
        )

    # Cloudflare static-asset headers. Does not affect the contact worker.
    with open(os.path.join(ROOT, "_headers"), "w", encoding="utf-8") as fh:
        fh.write(
            "/*\n"
            "  X-Content-Type-Options: nosniff\n"
            "  X-Frame-Options: SAMEORIGIN\n"
            "  Referrer-Policy: strict-origin-when-cross-origin\n"
            "  Permissions-Policy: geolocation=(), microphone=(), camera=()\n"
            "\n"
            "/assets/*\n"
            "  Cache-Control: public, max-age=31536000, immutable\n"
            "\n"
            "/styles.css\n"
            "  Cache-Control: public, max-age=604800\n"
            "\n"
            "/script.js\n"
            "  Cache-Control: public, max-age=604800\n"
        )


def main():
    built = [
        build_index(),
        build_work(),
        build_services(),
        build_process(),
        build_about(),
        build_audit(),
        build_contact(),
    ]
    for p in PROJECTS:
        built.append(build_case(p))

    build_extras(built)

    print(f"built {len(built)} pages")
    for name in built:
        size = os.path.getsize(os.path.join(ROOT, name))
        print(f"  {name:26} {size / 1024:6.1f} KB")

    # guardrail: the worker endpoint must survive every rebuild
    contact = open(os.path.join(ROOT, "contact.html"), encoding="utf-8").read()
    assert WORKER in contact, "FATAL: contact worker endpoint missing from contact.html"
    for field in ["name", "business", "email", "website", "type", "budget", "message"]:
        assert f'name="{field}"' in contact, f"FATAL: form field {field} missing"
    assert "Content-Type" in contact and "JSON.stringify" in contact, "FATAL: submit handler changed"
    print("\nform contract verified: endpoint + all 7 fields + JSON submit intact")


if __name__ == "__main__":
    main()
