# -*- coding: utf-8 -*-
"""Turn a live page into (state, action space).

Jev takes text only, so a screenshot is useless here. And raw HTML is worse
than useless: accuracy falls as the state grows with content unrelated to the
decision. So this walks the DOM once, tags every usable control with a ref,
and returns the controls separately from the prose.

`scope` is the filter. Scoped to the game container you get the room; left
open you get the nav, the cookie banner, the ads and the footer as well -
which is exactly the comparison stress.py runs.
"""

_JS = r"""
(scope) => {
  const root = scope ? document.querySelector(scope) : document.body;
  if (!root) return {screen: "", actions: {}, counts: {}};

  const visible = (el) => {
    const r = el.getBoundingClientRect();
    if (r.width <= 0 || r.height <= 0) return false;
    const s = getComputedStyle(el);
    return s.visibility !== "hidden" && s.display !== "none" && s.opacity !== "0";
  };
  const clean = (t) => (t || "").replace(/\s+/g, " ").trim().slice(0, 120);
  const label = (el) => clean(
      el.getAttribute("aria-label") || el.innerText || el.value ||
      el.getAttribute("placeholder") || el.getAttribute("title") || "");

  const SEL = "button,a[href],input:not([type=hidden]),select,textarea," +
              "[role=button],[role=link],[role=tab],[role=menuitem]";

  let n = 0;
  const actions = {};
  root.querySelectorAll(SEL).forEach((el) => {
    if (!visible(el)) return;
    if (el.disabled || el.getAttribute("aria-disabled") === "true") return;
    const name = label(el);
    if (!name) return;
    const ref = "e" + (++n);
    el.setAttribute("data-jev-ref", ref);
    const role = el.getAttribute("role") || el.tagName.toLowerCase();
    actions[ref] = role + ' "' + name + '"';
  });

  const lines = [];
  root.querySelectorAll("h1,h2,h3,h4,p,li,td,th,label,span,div").forEach((el) => {
    if (el.closest(SEL)) return;
    if (!visible(el)) return;
    const own = Array.from(el.childNodes)
      .filter((c) => c.nodeType === 3).map((c) => c.textContent).join(" ");
    const t = clean(own);
    if (t) lines.push(t);
  });

  const screen = lines.join("\n");
  return {screen, actions,
          counts: {actions: Object.keys(actions).length,
                   screen_chars: screen.length,
                   html_chars: root.innerHTML.length}};
}
"""


def snapshot(page, scope=None):
    """-> {'screen': str, 'actions': {ref: 'role \"name\"'}, 'counts': {...}}"""
    return page.evaluate(_JS, scope)


def click_ref(page, ref, timeout=5000):
    page.click(f'[data-jev-ref="{ref}"]', timeout=timeout)


def outcome(page):
    """The sample page records its own verdict, so no scraping guesswork."""
    return page.evaluate("() => ({outcome: document.body.dataset.outcome || null,"
                         " picked: document.body.dataset.picked || null})")
