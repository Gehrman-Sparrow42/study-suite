"""Browser regression suite. Uses installed Edge and Playwright Firefox; artifacts stay local."""
import json
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from validate import validate_html
ARTIFACTS = ROOT / 'tests/artifacts'
ARTIFACTS.mkdir(exist_ok=True)
DEMO = ROOT / 'output/Demo_Study_Suite.html'


def download(page, name):
    with page.expect_download() as event:
        page.locator('#save').click()
    path = ARTIFACTS / name
    event.value.save_as(path)
    assert event.value.failure() is None
    return path


def editing_regressions(context, name, errors):
    page = context.new_page()
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.route('https://cdn.jsdelivr.net/**', lambda route: route.abort())
    page.goto(DEMO.as_uri())
    # Matching explanations open; unrelated source notes do not. A subsequent
    # query restores the original detail state rather than accumulating opens.
    provenance = page.locator('details.provenance').first
    page.locator('#search').fill('quantity')
    assert not provenance.evaluate('(e) => e.open')
    page.locator('nav a:visible').first.click()
    expect(page.locator('#search')).to_have_value('quantity')
    page.locator('#search').fill('Synthetic illustration')
    assert provenance.evaluate('(e) => e.open')
    page.locator('#search').fill('quantity')
    assert not provenance.evaluate('(e) => e.open')
    page.locator('#search').fill('')
    # A section without an optional introduction still searches normally.
    page.locator('.section-intro').first.evaluate('(e) => e.remove()')
    page.locator('#search').fill('Quantity')
    expect(page.locator('#section-foundations')).to_be_visible()
    page.locator('#search').fill('')

    body = page.locator('[data-type="process"] .explanation-body')
    expect(body.locator('p')).to_have_count(2)
    body.locator('p').nth(1).evaluate('''e => {
      e.parentElement.focus(); const range = document.createRange();
      range.setStart(e.firstChild, 0); range.collapse(true);
      const selection = getSelection(); selection.removeAllRanges(); selection.addRange(range);
    }''')
    page.keyboard.press('Backspace')
    expect(body.locator('p')).to_have_count(1)
    # Enter inside existing prose must remain editable after an actual download.
    body.locator('p').first.evaluate('''e => {
      e.parentElement.focus(); const range = document.createRange();
      range.setStart(e.firstChild, 12); range.collapse(true);
      const selection = getSelection(); selection.removeAllRanges(); selection.addRange(range);
    }''')
    page.keyboard.press('Enter')
    page.keyboard.type('Added reading paragraph. ')
    lead = page.locator('[data-type="concept"] .lead').first
    lead.focus()
    page.keyboard.press('End')
    page.keyboard.press('Enter')
    page.keyboard.type('Added core explanation. ')
    # Real formula deletion/undo, followed by a DOM reconstruction, exercises
    # the delegated controls without assuming browser Undo loses listeners.
    page.locator('.inline-math').evaluate('''e => {
      e.parentElement.focus(); const range = document.createRange(); range.selectNode(e);
      const selection = getSelection(); selection.removeAllRanges(); selection.addRange(range);
    }''')
    page.keyboard.press('Backspace')
    expect(page.locator('.inline-math')).to_have_count(0)
    page.keyboard.press('Control+z')
    expect(page.locator('.inline-math')).to_have_count(1)
    page.locator('.inline-math').evaluate('(e) => e.replaceWith(e.cloneNode(true))')
    page.locator('.inline-math .edit-formula').click()
    expect(page.locator('#formula-dialog')).to_be_visible()
    page.locator('#cancel-formula').click()
    page.locator('.figure-open').evaluate('(e) => e.replaceWith(e.cloneNode(true))')
    page.locator('.figure-open').click()
    expect(page.locator('#image-dialog')).to_be_visible()
    page.locator('#close-image').click()
    exported = download(page, f'{name}-multiline.html')
    assert not validate_html(exported.read_text(encoding='utf-8'))
    reopened = context.new_page()
    reopened.on('pageerror', lambda error: errors.append(str(error)))
    reopened.route('https://cdn.jsdelivr.net/**', lambda route: route.abort())
    reopened.goto(exported.as_uri())
    for selector, marker in [('[data-type="process"] .explanation-body', 'Added reading paragraph.'), ('[data-type="concept"] .lead', 'Added core explanation.')]:
        host = reopened.locator(selector).first
        expect(host).to_contain_text(marker)
        # Inspect the actual marker text node; seeing the text is insufficient.
        assert host.evaluate('''(e, marker) => {
          const walker = document.createTreeWalker(e, NodeFilter.SHOW_TEXT);
          let node; while ((node = walker.nextNode())) {
            if (node.textContent.includes(marker)) return node.parentElement.isContentEditable;
          }
          return false;
        }''', marker)
        host.evaluate('''(e, marker) => {
          const walker = document.createTreeWalker(e, NodeFilter.SHOW_TEXT);
          let node; while ((node = walker.nextNode())) {
            if (node.textContent.includes(marker)) {
              e.focus(); const range = document.createRange(); range.setStart(node, node.length); range.collapse(true);
              const selection = getSelection(); selection.removeAllRanges(); selection.addRange(range); break;
            }
          }
        }''', marker)
        reopened.keyboard.type('Continued after reopening. ')
        expect(host).to_contain_text('Continued after reopening.')
    again = download(reopened, f'{name}-multiline-continued.html')
    assert not validate_html(again.read_text(encoding='utf-8'))
    assert 'Continued after reopening.' in again.read_text(encoding='utf-8')
    page.close(run_before_unload=False)
    reopened.close(run_before_unload=False)


def run(browser_type, name, **launch_options):
    browser = browser_type.launch(headless=True, **launch_options)
    context = browser.new_context(viewport={'width': 1440, 'height': 1000}, accept_downloads=True)
    # Exercise actual anchor downloads, including Chromium where the picker is normally available.
    context.add_init_script('window.showSaveFilePicker = undefined')
    page = context.new_page()
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.goto(DEMO.as_uri())
    expect(page.locator('h1')).to_contain_text('From observation')
    page.wait_for_function("document.querySelector('mjx-container') !== null", timeout=45000)
    assert page.locator('mjx-merror').count() == 0
    assert page.evaluate("getComputedStyle(document.body).backgroundColor") == 'rgb(0, 0, 0)'
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
    page.screenshot(path=str(ARTIFACTS / f'{name}-desktop.png'), full_page=False)
    page.locator('nav a[href="#section-reasoning"]').click()
    expect(page.locator('nav a[href="#section-reasoning"]')).to_have_attribute('aria-current', 'location')
    page.screenshot(path=str(ARTIFACTS / f'{name}-dense.png'))
    page.locator('#review').click()
    expect(page.locator('.explanation').first).to_be_hidden()
    page.locator('#search').fill('instantaneous')
    expect(page.locator('[data-type="details"]')).to_be_visible()
    expect(page.locator('[data-type="details"] .explanation')).to_be_visible()
    page.locator('#search').fill('unfindablewordzz')
    expect(page.locator('#search-status')).to_have_text('No matching concepts. Try another term.')
    page.locator('#search').fill('')
    page.locator('#learn').click()
    expect(page.locator('.explanation').first).to_be_visible()
    page.locator('#search').fill('quantity, its unit, and its context')
    expect(page.locator('#section-foundations')).to_be_visible()
    page.locator('#search').fill('')
    page.locator('h1').fill('My edited study edition')
    expect(page).to_have_title('My edited study edition')
    page.locator('[aria-label="Edit inline formula"]').click()
    page.locator('#formula-source').fill(r'\bar{r}=4')
    page.locator('#apply-formula').click()
    expect(page.locator('.inline-math .equation-render')).to_have_attribute('data-raw', r'\bar{r}=4')
    editable = page.locator('[data-type="concept"] .lead').first
    editable.fill('Edited explanation: units preserve meaning.')
    page.locator('td').first.fill('Edited amount')
    page.locator('#section-foundations h2').fill('Edited foundations')
    expect(page.locator('nav a').first).to_contain_text('Edited foundations')
    page.locator('[data-type="formula"] .edit-formula').click()
    page.locator('#formula-source').fill(r'\bar{r}=\frac{18}{3}=6\;\mathrm{units}\,\mathrm{s}^{-1}')
    page.locator('#apply-formula').click()
    expect(page.locator('[data-type="formula"] .equation-render')).to_have_attribute('data-raw', r'\bar{r}=\frac{18}{3}=6\;\mathrm{units}\,\mathrm{s}^{-1}')
    page.wait_for_function("document.querySelector('.equation-render mjx-container') !== null")
    page.locator('.figure-open').click()
    expect(page.locator('#image-dialog')).to_be_visible()
    page.locator('#zoom').click()
    expect(page.locator('.image-stage')).to_have_class('image-stage zoomed')
    page.keyboard.press('Escape')
    expect(page.locator('#image-dialog')).to_be_hidden()
    # Closing details and exporting during a search must restore their pre-search state.
    page.locator('[data-type="details"] summary').click()
    page.locator('#review').click()
    page.locator('#search').fill('instantaneous')
    exported = download(page, f'{name}-edited.html')
    expect(page.locator('#status')).to_contain_text('Download requested')
    value = exported.read_text(encoding='utf-8')
    assert not validate_html(value), validate_html(value)
    assert 'Edited explanation: units preserve meaning.' in value
    assert 'Edited amount' in value
    assert 'data:image/svg+xml;base64,' in value
    assert '<mjx-container' not in value
    # Reopen a real downloaded local file and export it again.
    page2 = context.new_page()
    page2.on('pageerror', lambda error: errors.append(str(error)))
    page2.goto(exported.as_uri())
    expect(page2.locator('[data-type="concept"] .lead').first).to_have_text('Edited explanation: units preserve meaning.')
    expect(page2.locator('td').first).to_have_text('Edited amount')
    expect(page2).to_have_title('My edited study edition')
    expect(page2.locator('.inline-math .equation-render')).to_have_attribute('data-raw', r'\bar{r}=4')
    expect(page2.locator('body')).to_have_attribute('data-mode', 'review')
    expect(page2.locator('#search')).to_have_value('')
    expect(page2.locator('.section:visible')).to_have_count(3)
    expect(page2.locator('nav a:visible')).to_have_count(3)
    expect(page2.locator('[data-type="details"] details')).not_to_have_attribute('open', '')
    page2.wait_for_function("document.querySelector('mjx-container') !== null", timeout=45000)
    assert page2.locator('img').first.evaluate('(e) => e.complete && e.naturalWidth > 0')
    again = download(page2, f'{name}-edited-again.html')
    assert abs(again.stat().st_size - exported.stat().st_size) < 200, (again.stat().st_size, exported.stat().st_size)
    assert not validate_html(again.read_text(encoding='utf-8'))
    # Mobile: drawer, navigation, scrollable table, diagram, formula and no page overflow.
    page2.set_viewport_size({'width': 390, 'height': 844})
    page2.locator('#learn').click()
    expect(page2.locator('#sidebar')).to_be_hidden()
    page2.locator('#nav-toggle').click()
    expect(page2.locator('#sidebar')).to_be_visible()
    page2.locator('nav a[href="#section-reasoning"]').click()
    expect(page2.locator('#sidebar')).to_be_hidden()
    assert page2.evaluate('document.documentElement.scrollWidth <= innerWidth')
    page2.wait_for_function("Math.abs(document.querySelector('#section-reasoning').getBoundingClientRect().top - 130) < 5")
    page2.mouse.move(0,0)
    page2.screenshot(path=str(ARTIFACTS / f'{name}-mobile-dense.png'))
    page2.locator('[data-type="formula"]').scroll_into_view_if_needed()
    page2.screenshot(path=str(ARTIFACTS / f'{name}-mobile-formula.png'))
    page2.locator('.figure-open').click()
    expect(page2.locator('#image-dialog')).to_be_visible()
    page2.locator('#close-image').click()
    page2.locator('#nav-toggle').click()
    page2.locator('nav a').first.click()
    page2.evaluate("window.scrollTo({top:0,behavior:'instant'})")
    page2.screenshot(path=str(ARTIFACTS / f'{name}-mobile.png'))
    table_scroll = page2.locator('.table-scroll')
    assert table_scroll.evaluate('(e) => e.scrollWidth > e.clientWidth')
    table_scroll.evaluate('(e) => e.scrollLeft = 100')
    assert table_scroll.evaluate('(e) => e.scrollLeft > 0')
    page2.set_viewport_size({'width': 320, 'height': 700})
    assert page2.evaluate('document.documentElement.scrollWidth <= innerWidth')
    page2.locator('#nav-toggle').click()
    page2.keyboard.press('Escape')
    expect(page2.locator('#sidebar')).to_be_hidden()
    page2.locator('#review').click()
    page2.evaluate("window.scrollTo({top:document.documentElement.scrollHeight,behavior:'instant'})")
    expect(page2.locator('nav a').last).to_have_attribute('aria-current', 'location')
    editing_regressions(context, name, errors)
    assert not errors, errors
    context.close()
    browser.close()
    return {'browser': name, 'result': 'passed', 'export_bytes': exported.stat().st_size, 'repeat_export_bytes': again.stat().st_size}


def failure_paths(chromium):
    browser = chromium.launch(channel='msedge', headless=True)
    context = browser.new_context()
    context.route('https://cdn.jsdelivr.net/**', lambda route: route.abort())
    page = context.new_page()
    page.goto(DEMO.as_uri())
    expect(page.locator('#status')).to_contain_text('Math renderer unavailable')
    expect(page.locator('[data-type="formula"] .equation-render')).to_contain_text('frac')
    page.locator('[data-type="formula"] .edit-formula').click()
    page.locator('#formula-source').fill('x=7')
    page.locator('#apply-formula').click()
    expect(page.locator('[data-type="formula"] .equation-render')).to_contain_text('x=7')
    page.evaluate("() => { window.showSaveFilePicker = async () => { throw new DOMException('cancel', 'AbortError'); }; }")
    page.locator('#save').click()
    expect(page.locator('#status')).to_contain_text('Save cancelled')
    # Mock only the OS picker API to check write/close ordering and errors.
    page.evaluate("window.savedHTML = ''; window.closedWrite = false; window.showSaveFilePicker = async () => ({createWritable: async () => ({write: async html => {window.savedHTML = html}, close: async () => {window.closedWrite = true}})})")
    page.locator('#save').click()
    expect(page.locator('#status')).to_have_text('Saved to your selected file.')
    assert page.evaluate("window.closedWrite && window.savedHTML.includes('data-raw=\"x=7\"')")
    page.evaluate("() => { window.showSaveFilePicker = async () => ({createWritable: async () => {throw new Error('denied')}}); }")
    downloaded = download(page, 'picker-failure-fallback.html')
    assert downloaded.exists()
    context.close()
    browser.close()
    return {'offline_math_and_picker_branches': 'passed (OS picker mocked; downloads real)'}


if __name__ == '__main__':
    with sync_playwright() as playwright:
        results = [run(playwright.chromium, 'edge', channel='msedge')]
        results.append(run(playwright.firefox, 'firefox'))
        results.append(failure_paths(playwright.chromium))
    (ARTIFACTS / 'results.json').write_text(json.dumps(results, indent=2), encoding='utf-8')
    print(json.dumps(results, indent=2))
