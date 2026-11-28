"""Browser verification for /playground/ and /playground/oracle/.

Serve the repo root, then run:
  python3 -m http.server 8000 --bind 127.0.0.1
  uv run --with playwright python tools/playground/verify_oracle.py [--base http://127.0.0.1:8000] [--shots DIR]
Uses a local Chromium (PLAYWRIGHT_CHROMIUM or `playwright install chromium`).
"""
import argparse, asyncio, os, sys
from urllib.parse import urlparse
from playwright.async_api import async_playwright

ap = argparse.ArgumentParser()
ap.add_argument("--base", default="http://127.0.0.1:8000")
ap.add_argument("--shots", default="tools/playground/shots")
ap.add_argument("--cdp", default=None, help="connect to an existing Chrome over CDP instead of launching")
args = ap.parse_args()
BASE = args.base.rstrip("/")
HOST = urlparse(BASE).netloc
os.makedirs(args.shots, exist_ok=True)

results = []
def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    print(("PASS " if ok else "FAIL ") + name + (f"  [{detail}]" if detail and not ok else ""))

class Watch:
    def __init__(self, page, label):
        self.label, self.errors, self.foreign, self.broken = label, [], [], []
        page.on("console", lambda m: self.errors.append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: self.errors.append(str(e)))
        page.on("request", lambda r: self.foreign.append(r.url) if urlparse(r.url).scheme in ("http", "https") and urlparse(r.url).netloc != HOST else None)
        # ERR_ABORTED is a request cancelled by our own navigation, not a missing asset
        page.on("requestfailed", lambda r: self.broken.append(f"{r.failure} {r.url}") if "ERR_ABORTED" not in (r.failure or "") else None)
        page.on("response", lambda r: self.broken.append(f"{r.status} {r.url}") if r.status >= 400 else None)
    def report(self):
        check(f"{self.label}: no console errors", not self.errors, "; ".join(self.errors))
        check(f"{self.label}: no third-party requests", not self.foreign, "; ".join(self.foreign))
        check(f"{self.label}: no broken assets", not self.broken, "; ".join(self.broken))

async def text(page, bind):
    return (await page.locator(f'[data-bind="{bind}"]').first.inner_text()).strip()

async def credits(page):
    return await text(page, "credits")

async def visible(page, sel):
    return await page.locator(sel).first.is_visible()

async def reveal_state(page):
    return {k: await text(page, k) for k in ("youValue", "exactAfterAB", "aquilaAfterAB")}

async def oracle(ctx, label):
    page = await ctx.new_page()
    w = Watch(page, label)
    await page.goto(BASE + "/playground/oracle/")
    return page, w

async def player_flows(ctx, shots):
    page, w = await oracle(ctx, "oracle desktop")
    check("initial: 4 credits", await credits(page) == "4")
    check("initial: displays unread", await text(page, "displayA") == "Unread" and await text(page, "displayB") == "Unread")
    check("initial: wired to sensor A", "feeds both displays" in await text(page, "wiringText") and not await visible(page, "#or-sensor-b"))
    check("initial: 50% prior shown", "50%" in await page.locator("#player").inner_text())
    check("initial: Read A visible without scrolling", await page.locator('[data-move="readA"]').is_visible() and (await page.locator('[data-move="readA"]').bounding_box())["y"] < 900)

    # double activation must not double-charge
    await page.locator('[data-move="readA"]').dblclick()
    check("read A: 2 credits after double click", await credits(page) == "2")
    check("read A: display A positive", "Positive" in await text(page, "displayA"))
    check("read A: exact 80% and Aquila 80%", await text(page, "exactAfterA") == "80%" and await text(page, "aquilaEpisode") == "80%")

    # stop path
    await page.click('[data-move="stop"]')
    check("stop: still 2 credits", await credits(page) == "2")
    check("stop: Aquila stop described", "stopped with two credits" in (await page.locator('[data-step="aquila"]').inner_text()))
    check("stop: copy offer shown, forecast hidden", await visible(page, '[data-move="showCopy"]') and not await visible(page, '[data-step="forecast"]'))
    await page.click('[data-move="showCopy"]')
    check("show copy: no charge", await credits(page) == "2")
    check("show copy: B positive (supplied)", "Positive" in await text(page, "displayB") and "supplied" in (await text(page, "ledgerB")).lower())
    check("show copy: forecast form shown", await visible(page, "#or-guess"))

    # validation
    for bad in ["", "  ", "101", "-5", "abc", "100.5"]:
        await page.fill("#or-guess", bad)
        await page.press("#or-guess", "Enter")
        check(f"forecast {bad!r} rejected", await visible(page, "#or-guess-error") and not await visible(page, '[data-step="revealed"]'))
    check("invalid input marked aria-invalid", await page.get_attribute("#or-guess", "aria-invalid") == "true")
    await page.fill("#or-guess", "82.5")
    await page.click('[data-step="forecast"] button[type="submit"]')
    r = await reveal_state(page)
    check("copy reveal: 82.5% / 80% / 90.5%", r == {"youValue": "82.5%", "exactAfterAB": "80%", "aquilaAfterAB": "90.5%"}, str(r))
    check("copy reveal: comparison sections available", await visible(page, "#compare"))
    await page.wait_for_timeout(1200)
    await page.locator('[data-step="revealed"]').scroll_into_view_if_needed()
    await page.evaluate("window.scrollTo(0, 0)")
    await page.screenshot(path=f"{shots}/desktop-copy-reveal.png", full_page=True)

    # rewire
    await page.check('input[name="wiring"][value="independent"]')
    await page.wait_for_timeout(600)
    r = await reveal_state(page)
    check("independent: exact 94.1%, Aquila 90.5%", r["exactAfterAB"] == "94.1%" and r["aquilaAfterAB"] == "90.5%", str(r))
    check("independent: readings and credits kept", await credits(page) == "2" and "Positive" in await text(page, "displayA") and "Positive" in await text(page, "displayB"))
    check("independent: guess attributed to same-sensor", "same-sensor" in (await text(page, "youNote")).lower())
    check("independent: sensor B drawn and described", await visible(page, "#or-sensor-b") and "independent" in (await text(page, "wiringText")).lower())
    await page.check('input[name="wiring"][value="copy"]')
    r = await reveal_state(page)
    check("toggle back: 82.5% / 80% / 90.5%", r == {"youValue": "82.5%", "exactAfterAB": "80%", "aquilaAfterAB": "90.5%"}, str(r))

    # comparison table
    await page.click("#compare summary")
    rows = await page.locator("#or-family tr").evaluate_all("rs => rs.map(r => [...r.cells].map(c => c.innerText.trim()))")
    got = [(r[0], r[3], r[4]) for r in rows]
    want = [("Inkling 2 Mini (base)", "80%", "80%"), ("Oracle Lyra", "66.7%", "88.9%"), ("Oracle Vega", "71.4%", "88.9%"), ("Oracle Aquila", "80%", "90.5%"), ("Oracle Altair", "66.7%", "80%"), ("Oracle Cygnus", "72.7%", "94.1%"), ("Oracle Deneb", "80%", "94.1%")]
    check("table: seven rows with supplied values", got == want, str(got))
    await page.click("#odds summary")
    check("odds explanation mentions 16/17", "16/17" in (await page.locator("#odds").inner_text()).replace(" ", ""))

    # reset
    await page.click('[data-move="reset"]')
    check("reset: 4 credits, unread, copy wiring, empty input", await credits(page) == "4" and await text(page, "displayA") == "Unread" and await text(page, "displayB") == "Unread"
          and await page.input_value("#or-guess") == "" and await page.is_checked('input[value="copy"]') and not await visible(page, '[data-step="revealed"]') and not await visible(page, "#more"))

    # buy path, boundary values
    for val, shown in [("0", "0%"), ("100", "100%")]:
        await page.click('[data-move="readA"]')
        await page.click('[data-move="buyB"]')
        check(f"buy ({val}): 0 credits, both positive", await credits(page) == "0" and "Positive" in await text(page, "displayB"))
        check(f"buy ({val}): Aquila's actual stop described", "stopped" in (await page.locator('[data-step="aquila"]').inner_text()).lower())
        check(f"buy ({val}): no copy offer", not await visible(page, '[data-move="showCopy"]'))
        await page.fill("#or-guess", val)
        await page.press("#or-guess", "Enter")
        await page.press("#or-guess", "Enter") if await visible(page, "#or-guess") else None
        r = await reveal_state(page)
        check(f"buy reveal {val}: {shown} / 80% / 90.5%", r == {"youValue": shown, "exactAfterAB": "80%", "aquilaAfterAB": "90.5%"}, str(r))
        await page.click('[data-move="reset"]')
    await page.click('[data-move="readA"]'); await page.click('[data-move="buyB"]'); await page.click('[data-move="skip"]')
    r = await reveal_state(page)
    check("just show me: no visitor value, 80% / 90.5%", r["youValue"] in ("—", "\u2014") and r["exactAfterAB"] == "80%" and r["aquilaAfterAB"] == "90.5%", str(r))
    await page.reload()
    check("refresh: back to initial", await credits(page) == "4")
    w.report()

async def keyboard(ctx):
    page, w = await oracle(ctx, "oracle keyboard")
    async def tab_to(sel, limit=60):
        for _ in range(limit):
            await page.keyboard.press("Tab")
            if await page.evaluate("(s) => document.activeElement && document.activeElement.matches(s)", sel):
                return True
        return False
    ok = await tab_to('[data-move="readA"]')
    outline = await page.evaluate("getComputedStyle(document.activeElement).outlineStyle")
    check("keyboard: reach Read A by Tab with visible focus", ok and outline != "none", outline)
    await page.keyboard.press("Enter"); await page.keyboard.press("Enter")
    check("keyboard: Enter repeat charges once", await credits(page) == "2")
    check("keyboard: focus moves to next step", await page.evaluate("document.activeElement.tagName") == "H2")
    ok = await tab_to('[data-move="buyB"]'); await page.keyboard.press("Enter")
    ok = ok and await tab_to("#or-guess")
    await page.keyboard.type("82.5"); await page.keyboard.press("Enter")
    r = await reveal_state(page)
    check("keyboard: buy + forecast + reveal", ok and r["youValue"] == "82.5%", str(r))
    ok = await tab_to('input[name="wiring"]')
    await page.keyboard.press("ArrowRight")
    check("keyboard: arrow key rewires", ok and await text(page, "exactAfterAB") == "94.1%")
    ok = await tab_to("#compare summary"); await page.keyboard.press("Enter")
    check("keyboard: open comparison", ok and await page.get_attribute("#compare", "open") is not None)
    w.report()

async def no_overflow(page):
    return await page.evaluate("document.documentElement.scrollWidth <= document.documentElement.clientWidth + 1")

async def phone(browser, shots, width):
    ctx = await browser.new_context(viewport={"width": width, "height": 780}, device_scale_factor=2, is_mobile=True, has_touch=True)
    page, w = await oracle(ctx, f"phone {width}")
    async def in_view(sel):
        return await page.evaluate("(s) => { const r = document.querySelector(s).getBoundingClientRect(); return r.top >= 0 && r.bottom <= innerHeight; }", sel)
    async def clear_of_instrument(sel):
        return await page.evaluate("(s) => document.querySelector(s).getBoundingClientRect().top >= document.querySelector('.or-instrument').getBoundingClientRect().bottom", sel)
    check(f"phone {width}: no horizontal overflow (start)", await no_overflow(page))
    check(f"phone {width}: Read A visible on load without scrolling", await in_view('[data-move="readA"]'))
    await page.tap('[data-move="readA"]'); await page.tap('[data-move="buyB"]')
    await page.fill("#or-guess", "82.5"); await page.tap('[data-step="forecast"] button[type="submit"]')
    await page.locator('input[value="independent"]').tap()
    await page.wait_for_timeout(600)
    check(f"phone {width}: rewired to 94.1%", await text(page, "exactAfterAB") == "94.1%")
    seen = {sel: await in_view(sel) for sel in (".or-seg", ".or-board", ".or-display-b", '[data-step="revealed"] [data-bind="exactAfterAB"]', '[data-step="revealed"] [data-bind="aquilaAfterAB"]')}
    check(f"phone {width}: switch, wiring and both forecasts on screen together", all(seen.values()), str(seen))
    check(f"phone {width}: values not hidden under the sticky instrument", await clear_of_instrument('[data-step="revealed"] .or-three') and await clear_of_instrument(".or-seg"))
    check(f"phone {width}: no horizontal overflow (revealed)", await no_overflow(page))
    if width == 390:
        await page.locator(".or-instrument").scroll_into_view_if_needed()
        await page.evaluate("document.querySelector('.or-instrument').scrollIntoView({block:'start'})")
        await page.screenshot(path=f"{shots}/phone-rewired.png")
        await page.screenshot(path=f"{shots}/phone-rewired-full.png", full_page=True)
    # mobile menu shows Playground active
    await page.evaluate("window.scrollTo(0,0)")
    await page.tap("button.menu")
    check(f"phone {width}: menu shows Playground active", await page.locator('#primary-nav a[href="/playground/"][aria-current="page"]').is_visible())
    w.report()
    await ctx.close()

async def reduced_motion(browser):
    ctx = await browser.new_context(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
    page, w = await oracle(ctx, "reduced motion")
    await page.click('[data-move="readA"]'); await page.click('[data-move="buyB"]'); await page.click('[data-move="skip"]')
    before = await page.get_attribute("#or-wire-b", "d")
    await page.check('input[value="independent"]')
    after1 = await page.get_attribute("#or-wire-b", "d")
    await page.wait_for_timeout(500)
    after2 = await page.get_attribute("#or-wire-b", "d")
    check("reduced motion: wire jumps without animation", before != after1 and after1 == after2, f"{before} | {after1} | {after2}")
    w.report()
    await ctx.close()

async def zoom(browser):
    # 1440x900 window at 200% zoom == 720x450 CSS px at 2x
    ctx = await browser.new_context(viewport={"width": 720, "height": 450}, device_scale_factor=2)
    page, w = await oracle(ctx, "200% zoom")
    await page.click('[data-move="readA"]'); await page.click('[data-move="stop"]'); await page.click('[data-move="showCopy"]')
    await page.fill("#or-guess", "50"); await page.press("#or-guess", "Enter")
    await page.check('input[value="independent"]')
    check("200% zoom: flow works", await text(page, "exactAfterAB") == "94.1%")
    check("200% zoom: no horizontal overflow", await no_overflow(page))
    w.report()
    await ctx.close()

async def no_js(browser, shots):
    ctx = await browser.new_context(viewport={"width": 1440, "height": 900}, java_script_enabled=False)
    page = await ctx.new_page()
    w = Watch(page, "no JavaScript")
    await page.goto(BASE + "/playground/oracle/")
    body = await page.locator(".or-static").inner_text()
    check("no JS: static explanation visible", await page.locator(".or-static").is_visible())
    check("no JS: copy 80% / independent 94.1% / Aquila 90.5%", all(s in body for s in ("80%", "94.1%", "90.5%")))
    check("no JS: interactive player hidden", not await page.locator("#player").is_visible())
    await page.wait_for_timeout(1200)  # let the site-wide entrance animation finish
    await page.screenshot(path=f"{shots}/nojs.png", full_page=True)
    await page.goto(BASE + "/playground/")
    check("no JS: Playground index readable", "Oracle and the Second Sensor" in await page.inner_text("main"))
    w.report()
    await ctx.close()

async def navigation(ctx, shots):
    page = await ctx.new_page()
    w = Watch(page, "navigation")
    for path in ["/playground/", "/playground/oracle/"]:
        resp = await page.goto(BASE + path)
        check(f"direct {path}: 200", resp.status == 200)
        await page.reload()
        check(f"refresh {path}: playground nav active", await page.locator('#primary-nav a[href="/playground/"][aria-current="page"]').count() == 1)
        canon = await page.get_attribute('link[rel="canonical"]', "href")
        check(f"{path}: canonical", canon == "https://laplaceresearch.org" + path, canon)
        og = await page.get_attribute('meta[property="og:image"]', "content")
        r = await page.request.get(BASE + urlparse(og).path)
        check(f"{path}: OG image exists", r.ok, og)
    for path in ["/playground", "/playground/oracle"]:
        resp = await page.goto(BASE + path)
        check(f"{path} redirects to trailing slash", page.url.endswith(path + "/") and resp.ok, page.url)
    await page.goto(BASE + "/")
    await page.click('#primary-nav a[href="/playground/"]')
    check("home -> Playground via rail", page.url.endswith("/playground/"))
    index = await page.inner_text("main")
    check("index: title, entry, question", all(s in index for s in ("Playground", "Oracle and the Second Sensor", "Would you pay twice for the same evidence?")))
    await page.wait_for_timeout(600)
    await page.screenshot(path=f"{shots}/desktop-playground-index.png", full_page=True)
    await page.click("text=Try the experiment")
    check("index -> experiment", page.url.endswith("/playground/oracle/"))
    await page.click('a[href="/playground/"] >> text=Playground >> nth=0')
    check("experiment -> back to Playground", page.url.endswith("/playground/"))
    # every same-origin link on both pages resolves
    bad = []
    for path in ["/playground/", "/playground/oracle/"]:
        await page.goto(BASE + path)
        hrefs = await page.locator("a[href^='/']").evaluate_all("as => [...new Set(as.map(a => a.getAttribute('href')))]")
        for h in hrefs:
            r = await page.request.get(BASE + h.split("#")[0])
            if not r.ok: bad.append(f"{r.status} {h}")
    check("internal links resolve", not bad, "; ".join(bad))
    w.report()

async def main():
    async with async_playwright() as p:
        if args.cdp:
            browser = await p.chromium.connect_over_cdp(args.cdp)
        else:
            exe = os.environ.get("PLAYWRIGHT_CHROMIUM")
            browser = await p.chromium.launch(executable_path=exe) if exe else await p.chromium.launch()
        desk = await browser.new_context(viewport={"width": 1440, "height": 900})
        await navigation(desk, args.shots)
        await player_flows(desk, args.shots)
        await keyboard(desk)
        await desk.close()
        for wd in (360, 390):
            await phone(browser, args.shots, wd)
        await reduced_motion(browser)
        await zoom(browser)
        await no_js(browser, args.shots)
        await browser.close()
    failed = [r for r in results if not r[1]]
    print(f"\n{len(results) - len(failed)}/{len(results)} checks passed")
    sys.exit(1 if failed else 0)

asyncio.run(main())
