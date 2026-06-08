"""
Static marketing / legal content pages (About, Terms, Privacy, FAQ, Contact).

Kept separate from the app so they render fast, are crawlable for SEO, and carry
the legal disclaimers the project needs before it's used by general users. Each
page shares one HTML shell with full SEO head + header + footer.
"""
from __future__ import annotations

BRAND = "Ghosted"
TAGLINE = "Hide your Instagram story from everyone, in one click."

_ICON = "/static/icon.svg"

# Footer + header are shared so every page links to the rest (good for SEO and UX).
_NAV = [("/", "Home"), ("/about", "About"), ("/faq", "FAQ"),
        ("/privacy", "Privacy"), ("/terms", "Terms"), ("/contact", "Contact")]


def _shell(slug: str, title: str, description: str, body: str) -> str:
    nav = "".join(
        f'<a href="{href}" class="hover:text-indigo-600 {"text-indigo-600 font-medium" if href == slug else "text-slate-600"}">{label}</a>'
        for href, label in _NAV
    )
    foot = " · ".join(f'<a href="{href}" class="hover:text-indigo-600">{label}</a>' for href, label in _NAV)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{title} — {BRAND}</title>
<meta name="description" content="{description}" />
<meta name="robots" content="index, follow" />
<meta name="theme-color" content="#6366f1" />
<link rel="canonical" href="{slug}" />
<meta property="og:type" content="website" />
<meta property="og:site_name" content="{BRAND}" />
<meta property="og:title" content="{title} — {BRAND}" />
<meta property="og:description" content="{description}" />
<meta property="og:image" content="/static/og.svg" />
<meta name="twitter:card" content="summary_large_image" />
<link rel="icon" href="{_ICON}" />
<link rel="manifest" href="/static/manifest.webmanifest" />
<script src="https://cdn.tailwindcss.com"></script>
<style>body{{font-family:ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}}
.prose h2{{font-size:1.25rem;font-weight:700;margin:1.5rem 0 .5rem}}
.prose h3{{font-weight:600;margin:1rem 0 .25rem}}
.prose p,.prose li{{color:#475569;line-height:1.7;font-size:15px}}
.prose ul{{list-style:disc;padding-left:1.25rem;margin:.5rem 0}}
.prose a{{color:#4f46e5;text-decoration:underline}}</style>
</head>
<body class="bg-gradient-to-b from-slate-100 to-slate-50 text-slate-900 min-h-screen flex flex-col">
<header class="border-b bg-white/70 backdrop-blur sticky top-0 z-10">
  <div class="max-w-4xl mx-auto px-5 py-3 flex items-center justify-between">
    <a href="/" class="flex items-center gap-2 font-bold tracking-tight">
      <img src="{_ICON}" class="w-7 h-7 rounded-lg" alt="{BRAND}" /> {BRAND}
    </a>
    <nav class="hidden sm:flex items-center gap-4 text-sm">{nav}</nav>
    <a href="/" class="sm:hidden text-sm text-indigo-600 font-medium">Open app</a>
  </div>
</header>
<main class="max-w-3xl mx-auto px-5 py-10 flex-1 w-full">
  <div class="bg-white rounded-2xl shadow-sm ring-1 ring-slate-900/5 p-6 sm:p-8 prose max-w-none">
    {body}
  </div>
</main>
<footer class="border-t bg-white">
  <div class="max-w-4xl mx-auto px-5 py-6 text-xs text-slate-500 flex flex-col sm:flex-row gap-2 sm:items-center sm:justify-between">
    <div>© {BRAND}. Not affiliated with Instagram or Meta.</div>
    <div class="flex flex-wrap gap-x-3 gap-y-1">{foot}</div>
  </div>
</footer>
</body>
</html>"""


_DISCLAIMER = (
    "<strong>Ghosted is an independent tool and is not affiliated with, endorsed by, "
    "or sponsored by Instagram or Meta Platforms, Inc.</strong> \"Instagram\" is a "
    "trademark of Meta Platforms, Inc."
)

_ABOUT = f"""
<h1 class="text-2xl font-extrabold">About {BRAND}</h1>
<p>{BRAND} is a privacy-first dashboard for managing your own Instagram presence. It lets you
<strong>hide or unhide your story from every follower in one click</strong>, see who doesn't follow
you back, find non-mutuals and likely-bot accounts, and bulk unfollow — all with safe pacing so you
stay in control.</p>
<h2>How it works</h2>
<p>{BRAND} runs locally on your own machine and talks to Instagram using your own session. Your
password is used once to sign in and is <strong>never sent to us or any third party</strong> — there
is no Ghosted server holding your credentials.</p>
<h2>What you can do</h2>
<ul>
<li>Hide / unhide your story from all followers at once</li>
<li>Find accounts that don't follow you back</li>
<li>Filter by hidden, mutual, private, verified, no-photo and more</li>
<li>Bulk unfollow, follow back, block / unblock</li>
<li>Whitelist people you never want to act on</li>
</ul>
<h2>Safety first</h2>
<p>Instagram limits how fast automated actions can run. {BRAND} paces actions and offers speed
tiers so you can choose your own balance of speed versus risk. Read our <a href="/faq">FAQ</a> and
<a href="/terms">Terms</a> before bulk-actioning an account you care about.</p>
<p class="text-xs text-slate-400 mt-6">{_DISCLAIMER}</p>
"""

_FAQ = f"""
<h1 class="text-2xl font-extrabold">Frequently asked questions</h1>

<h2>How do I hide my Instagram story from everyone at once?</h2>
<p>Instagram's own settings only let you toggle people one at a time. {BRAND} adds a single
<strong>“Hide story from all followers”</strong> button that applies it to your entire follower list,
skipping anyone already hidden, with safe pacing built in.</p>

<h2>Can I unhide my story from everyone at once?</h2>
<p>Yes. The <strong>“Unhide for all followers”</strong> button reverses it for everyone you've hidden.
There is no native Instagram button for this — it's exactly what {BRAND} was built for.</p>

<h2>Will using {BRAND} get my account banned?</h2>
<p>It can. {BRAND} uses Instagram's private API, which automation tools rely on but which violates
Instagram's Terms of Use. Risks include temporary action-blocks, reach throttling, or — in the worst
case — account suspension. Use the <strong>Safe</strong> speed, avoid brand-new accounts, and don't run
it on an account you can't afford to lose.</p>

<h2>How fast can it go?</h2>
<p>From Safe (45–90s between actions) up to Max (parallel, no delay). Faster tiers finish sooner but
raise the chance Instagram rate-limits or blocks you. Hiding/unhiding stories is a "soft" action
Instagram tolerates better than mass unfollowing.</p>

<h2>Does {BRAND} store my Instagram password?</h2>
<p>No. Your password is used only to create a session on your own device. It is never transmitted to
us. See our <a href="/privacy">Privacy Policy</a>.</p>

<h2>How do I find who doesn't follow me back?</h2>
<p>Open the <strong>“Doesn't follow back”</strong> tab. You can filter and bulk-unfollow from there.</p>

<h2>Is {BRAND} affiliated with Instagram?</h2>
<p>No. {_DISCLAIMER}</p>
"""

_PRIVACY = f"""
<h1 class="text-2xl font-extrabold">Privacy Policy</h1>
<p class="text-xs text-slate-400">Last updated: 2026</p>
<p>{BRAND} is designed to be private by default. This policy explains what is and isn't collected.</p>
<h2>Your Instagram credentials</h2>
<p>Your username and password are used only to sign in to Instagram from your own device. They are
<strong>not transmitted to {BRAND}</strong> and are not stored on any server we control. The
resulting Instagram session is saved locally on your machine so you don't have to log in repeatedly.</p>
<h2>Data we process</h2>
<ul>
<li><strong>Follower / following data</strong> — fetched from Instagram and cached locally to power the
dashboard. It stays on your device.</li>
<li><strong>Feedback you submit</strong> — if you send feedback, the message and any email you provide
are stored so we can read and respond. Don't include sensitive information.</li>
</ul>
<h2>What we don't do</h2>
<ul>
<li>We don't sell or share your data.</li>
<li>We don't post, message, or act on your account without your explicit action.</li>
<li>We don't run ads or third-party trackers in the app.</li>
</ul>
<h2>Contact</h2>
<p>Questions about privacy? Use the <a href="/contact">contact page</a>.</p>
<p class="text-xs text-slate-400 mt-6">{_DISCLAIMER}</p>
"""

_TERMS = f"""
<h1 class="text-2xl font-extrabold">Terms &amp; Conditions</h1>
<p class="text-xs text-slate-400">Last updated: 2026</p>
<p>By using {BRAND} (“the Service”) you agree to these Terms. If you do not agree, do not use the
Service.</p>

<h2>1. Independence from Instagram</h2>
<p>{_DISCLAIMER} The Service interacts with Instagram through an unofficial interface.</p>

<h2>2. Compliance and your responsibility</h2>
<p>Automating actions on Instagram may violate Instagram's Terms of Use. <strong>You are solely
responsible</strong> for how you use the Service and for any consequences to your account, including
action-blocks, reach throttling, suspension, or permanent disablement. You represent that you are
acting on your own account and have the right to do so.</p>

<h2>3. No warranty</h2>
<p>The Service is provided “as is” and “as available,” without warranties of any kind, express or
implied, including fitness for a particular purpose, reliability, or that actions will succeed or
remain undetected.</p>

<h2>4. Limitation of liability</h2>
<p>To the maximum extent permitted by law, {BRAND} and its creators shall not be liable for any
indirect, incidental, special, or consequential damages, or for any loss of account access, data,
reach, or revenue, arising from your use of the Service. Your sole remedy is to stop using it.</p>

<h2>5. Acceptable use</h2>
<ul>
<li>Use the Service only on accounts you own or are authorized to manage.</li>
<li>Do not use it to harass, spam, or target others.</li>
<li>Do not resell or redistribute the Service without permission.</li>
</ul>

<h2>6. Changes</h2>
<p>These Terms may be updated. Continued use after changes constitutes acceptance.</p>

<h2>7. Contact</h2>
<p>Questions about these Terms? See the <a href="/contact">contact page</a>.</p>
"""

_CONTACT = f"""
<h1 class="text-2xl font-extrabold">Contact &amp; Feedback</h1>
<p>Found a bug, want a feature, or have a question? Send us a note — we read everything.</p>
<form id="fbForm" class="mt-4 space-y-3 not-prose">
  <div class="flex gap-2">
    <input id="fbEmail" type="email" placeholder="Your email (optional)"
      class="flex-1 border rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400" />
    <select id="fbRating" class="border rounded-lg px-3 py-2.5 text-sm">
      <option value="">Rating</option>
      <option value="5">★★★★★</option><option value="4">★★★★</option>
      <option value="3">★★★</option><option value="2">★★</option><option value="1">★</option>
    </select>
  </div>
  <textarea id="fbMsg" rows="5" placeholder="Your message…"
    class="w-full border rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"></textarea>
  <button type="submit" class="bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg px-5 py-2.5 text-sm font-medium hover:opacity-95">Send feedback</button>
  <div id="fbOut" class="text-sm"></div>
</form>
<script>
document.getElementById('fbForm').addEventListener('submit', async (e) => {{
  e.preventDefault();
  const out = document.getElementById('fbOut');
  const message = document.getElementById('fbMsg').value.trim();
  if (!message) {{ out.textContent = 'Please write a message.'; out.className = 'text-sm text-red-600'; return; }}
  try {{
    const r = await fetch('/api/feedback', {{ method: 'POST', headers: {{'Content-Type':'application/json'}},
      body: JSON.stringify({{ message, email: document.getElementById('fbEmail').value.trim() || null,
        rating: document.getElementById('fbRating').value || null, page: 'contact' }}) }});
    if (!r.ok) throw 0;
    document.getElementById('fbForm').reset();
    out.textContent = 'Thanks! Your feedback was sent.'; out.className = 'text-sm text-emerald-600';
  }} catch {{ out.textContent = 'Could not send — try again.'; out.className = 'text-sm text-red-600'; }}
}});
</script>
"""

PAGES = {
    "/about": ("About", "Learn what Ghosted does: bulk hide/unhide your Instagram story, find non-followers, and manage following — privately and locally.", _ABOUT),
    "/faq": ("FAQ", "How to hide your Instagram story from everyone, unhide all at once, whether it's safe, and whether it stores your password.", _FAQ),
    "/privacy": ("Privacy Policy", "How Ghosted handles your data. Your Instagram password never leaves your device; nothing is sold or shared.", _PRIVACY),
    "/terms": ("Terms & Conditions", "Terms of use for Ghosted, including disclaimers, your responsibilities, and limitation of liability.", _TERMS),
    "/contact": ("Contact", "Send feedback, report a bug, or ask a question about Ghosted.", _CONTACT),
}


def render(slug: str) -> str | None:
    page = PAGES.get(slug)
    if not page:
        return None
    title, description, body = page
    return _shell(slug, title, description, body)


def all_slugs() -> list[str]:
    return ["/"] + list(PAGES.keys())
