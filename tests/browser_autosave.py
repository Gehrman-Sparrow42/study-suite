"""Autosave timing, real backing-file writes, recovery and unsupported browsers."""
import json
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / 'tests/artifacts'
ARTIFACTS.mkdir(exist_ok=True)


def run(kind, name, **options):
    browser = kind.launch(headless=True, **options)
    context = browser.new_context(viewport={'width': 1440, 'height': 1000}, accept_downloads=True)
    context.route('https://cdn.jsdelivr.net/**', lambda route: route.abort())
    page = context.new_page()
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.on('dialog', lambda dialog: dialog.accept())
    backing = ARTIFACTS / f'{name}-autosaved.html'
    context.expose_function('persistHTML', lambda value: backing.write_text(value, encoding='utf-8'))
    page.goto((ROOT / 'output/Demo_Study_Suite.html').as_uri())
    page.evaluate("""() => {
      window.writes = 0; window.activeWrites = 0; window.overlapped = false;
      window.delayWrite = false; window.failWrite = false; window.pickCount = 0;
      window.showSaveFilePicker = async () => {
        window.pickCount++;
        return {createWritable: async () => {
          if (window.failWrite) throw new Error('permission revoked');
          let value;
          return {
            write: async html => {
              window.activeWrites++;
              if (window.activeWrites > 1) window.overlapped = true;
              if (window.delayWrite) {
                window.delayWrite = false;
                await new Promise(resolve => window.releaseWrite = resolve);
              }
              value = html;
            },
            close: async () => { await window.persistHTML(value); window.activeWrites--; window.writes++; },
            abort: async () => {}
          };
        }};
      };
    }""")
    page.locator('#autosave').click()
    page.wait_for_function('window.writes === 1')
    expect(page.locator('#autosave')).to_have_attribute('aria-pressed', 'true')
    heading = page.locator('h1')
    heading.fill('Auto-save first edit')
    page.wait_for_function('window.writes === 2')
    assert 'Auto-save first edit' in backing.read_text(encoding='utf-8')
    assert page.evaluate('window.pickCount') == 1

    # Hold a write open, edit again, then allow the old version to finish.
    page.evaluate('window.delayWrite = true')
    heading.fill('Version while writing')
    page.wait_for_function('typeof window.releaseWrite === "function"')
    heading.fill('Newest version survives')
    page.evaluate('window.releaseWrite()')
    page.wait_for_function('window.writes >= 4')
    assert 'Newest version survives' in backing.read_text(encoding='utf-8')
    assert not page.evaluate('window.overlapped')
    page.locator('#save').click()
    page.wait_for_function('window.writes >= 5')
    expect(page.locator('#status')).to_have_text('Saved to your selected file.')

    # A denied write pauses autosave and leaves explicit recovery for reload.
    page.evaluate('window.failWrite = true')
    heading.fill('Recover my latest notes')
    page.wait_for_function("document.querySelector('#save-state').textContent.includes('paused')")
    expect(page.locator('#autosave')).to_have_attribute('aria-pressed', 'false')
    page.reload()
    expect(page.locator('#restore-recovery')).to_be_visible()
    page.locator('#restore-recovery').click()
    expect(page.locator('h1')).to_have_text('Recover my latest notes')
    expect(page.locator('#autosave')).to_have_attribute('aria-pressed', 'false')

    # Recovery includes paragraph boundaries and authored inline math.
    body = page.locator('.explanation-body').first
    body.fill('First recovered paragraph\\(a=b\\)\n\nSecond recovered paragraph')
    lead = page.locator('.lead').first
    lead.fill('Recovered core first')
    lead.press('End')
    lead.press('Enter')
    lead.press_sequentially('Recovered core second')
    lead.press('Shift+Enter')
    lead.press_sequentially('Hard break')
    page.wait_for_function("JSON.parse(localStorage.getItem(Object.keys(localStorage).find(k => k.startsWith('study-suite-recovery:')))).edits && document.querySelector('#save-state').textContent.includes('stored')")
    page.reload()
    page.locator('#restore-recovery').click()
    expect(body.locator('p')).to_have_count(2)
    expect(body.locator('.equation-render')).to_have_attribute('data-raw', 'a=b')
    expect(body.locator('.equation-render')).to_have_attribute('data-display', 'inline')
    expect(lead.locator('p')).to_have_count(2)
    assert lead.locator('br').count() >= 1
    expect(lead).to_contain_text('Hard break')
    body.locator('.edit-formula').click()
    expect(page.locator('#formula-source')).to_have_value('a=b')
    page.locator('#cancel-formula').click()

    page.evaluate("() => {window.showSaveFilePicker = async () => {throw new DOMException('cancel', 'AbortError')}}")
    page.locator('#autosave').click()
    expect(page.locator('#status')).to_contain_text('setup cancelled')
    expect(page.locator('#autosave')).to_have_attribute('aria-pressed', 'false')

    page.evaluate('window.showSaveFilePicker = undefined')
    page.locator('#autosave').click()
    expect(page.locator('#status')).to_contain_text('cannot write directly')
    for width in [390, 320]:
        page.set_viewport_size({'width': width, 'height': 844})
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        expect(page.locator('#autosave')).to_be_in_viewport()
        expect(page.locator('#save')).to_be_in_viewport()
        if width == 390:
            page.screenshot(path=str(ARTIFACTS / f'{name}-autosave-mobile.png'))

    # An undo of an already saved note is itself a recoverable change.
    page.goto(backing.as_uri())
    expect(page.locator('h1')).to_have_text('Newest version survives')
    baseline_title = page.evaluate("JSON.parse(document.querySelector('#suite-state').textContent).baseline.title")
    page.locator('h1').fill(baseline_title)
    page.wait_for_function("document.querySelector('#save-state').textContent.includes('stored')")
    page.reload()
    page.locator('#nav-toggle').click()
    page.locator('#restore-recovery').click()
    expect(page.locator('h1')).to_have_text(baseline_title)
    page.locator('#nav-toggle').click()
    page.evaluate("""() => {window.showSaveFilePicker = async () => ({createWritable: async () => {
      await new Promise(resolve => window.completeManual = resolve);
      let value;
      return {write: async html => {value = html}, close: async () => {await window.persistHTML(value)}};
    }});} """)
    page.locator('#save').click()
    page.wait_for_function('typeof window.completeManual === "function"')
    page.locator('h1').fill('Unsaved while manual write')
    page.evaluate('window.completeManual()')
    expect(page.locator('#status')).to_contain_text('Newer edits still need saving')
    expect(page.locator('#save-state')).to_contain_text('Newer edits unsaved')
    assert 'Unsaved while manual write' not in backing.read_text(encoding='utf-8')
    page.evaluate("""() => {window.showSaveFilePicker = async () => ({createWritable: async () => {
      await new Promise(resolve => window.manualRelease = resolve); throw new Error('disk full');
    }});} """)
    page.locator('#save').click()
    page.wait_for_function('typeof window.manualRelease === "function"')
    page.locator('h1').fill('New edit during failed manual save')
    with page.expect_download() as download:
        page.evaluate('window.manualRelease()')
    fallback = ARTIFACTS / f'{name}-fresh-fallback.html'
    download.value.save_as(fallback)
    assert 'New edit during failed manual save' in fallback.read_text(encoding='utf-8')
    expect(page.locator('#save-state')).to_contain_text('Download requested')
    page.evaluate("() => {Storage.prototype.setItem = () => {throw new Error('quota exceeded')}}")
    page.locator('h1').fill('Still editable when storage fails')
    page.wait_for_function("document.querySelector('#save-state').textContent.includes('unavailable')")
    assert not errors, errors
    context.close()
    browser.close()
    return {'browser': name, 'autosave_and_recovery': 'passed',
            'picker': 'mocked; backing HTML writes real', 'overlapping_writes': False}


if __name__ == '__main__':
    with sync_playwright() as playwright:
        results = [run(playwright.chromium, 'edge', channel='msedge'), run(playwright.firefox, 'firefox')]
    (ARTIFACTS / 'autosave-results.json').write_text(json.dumps(results, indent=2), encoding='utf-8')
    print(json.dumps(results, indent=2))
