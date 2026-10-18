"""Real saved edits -> Week 6 -> further saved edits -> Week 7, in Edge/Firefox."""
import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build import build  # noqa: E402 -- local scripts after path bootstrap
from course_state import read_snapshot  # noqa: E402
from update import apply_update, scan_sources  # noqa: E402
from validate import validate_html  # noqa: E402

ARTIFACTS = ROOT / 'tests/artifacts'
ARTIFACTS.mkdir(exist_ok=True)


def save(page, name):
    with page.expect_download() as event:
        page.locator('#save').click()
    path = ARTIFACTS / name
    event.value.save_as(path)
    assert event.value.failure() is None
    return path


def run(kind, name, **options):
    with tempfile.TemporaryDirectory() as directory:
        authoring = Path(directory)
        source = authoring / 'course.json'
        delta = authoring / 'week-06.delta.json'
        inputs = authoring / 'inputs'
        shutil.copy2(ROOT / 'demo/weekly_course.json', source)
        shutil.copy2(ROOT / 'demo/week_06.delta.json', delta)
        shutil.copy2(ROOT / 'demo/measurement.svg', authoring / 'measurement.svg')
        shutil.copytree(ROOT / 'demo/weekly_sources', inputs)
        initial = build(source, authoring / 'initial.html')
        browser = kind.launch(headless=True, **options)
        context = browser.new_context(viewport={'width': 1440, 'height': 1000}, accept_downloads=True)
        context.add_init_script('window.showSaveFilePicker = undefined')
        context.route('https://cdn.jsdelivr.net/**', lambda route: route.abort())
        page = context.new_page()
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.goto(initial.as_uri())
        untouched = save(page, f'{name}-weekly-untouched.html')
        assert read_snapshot(untouched.read_text(encoding='utf-8'))['edits'] == {}
        body = page.locator('#section-week-01 .explanation-body')
        body.locator('p').first.evaluate('''e => {
          e.parentElement.focus(); const range = document.createRange();
          range.setStart(e.firstChild, e.firstChild.length); range.collapse(true);
          const selection = getSelection(); selection.removeAllRanges(); selection.addRange(range);
        }''')
        page.keyboard.press('Enter')
        page.keyboard.type('My note: always carry the units.')
        page.locator('#section-week-01 h2').fill('Quantities in my own words')
        page.locator('#section-week-02 .edit-formula').click()
        page.locator('#formula-source').fill(r'\bar{r}=\frac{18}{3}=6')
        page.locator('#apply-formula').click()
        page.locator('#section-week-03 td').first.fill('My amount label')
        page.locator('#section-week-04 figcaption').fill('My diagram note: follow the units.')
        page.locator('#section-week-05 li').first.fill('First, define the amount carefully.')
        exported = save(page, f'{name}-weekly-edited.html')
        state = read_snapshot(exported.read_text(encoding='utf-8'))
        assert 'My note: always carry the units.' in state['edits']['sections/0/blocks/0/body']
        assert state['edits']['sections/1/blocks/0/latex'] == r'\bar{r}=\frac{18}{3}=6'
        assert len(state['edits']) == 6, state['edits']
        updated_course = authoring / 'weeks-1-6.json'
        updated_html = ARTIFACTS / f'{name}-weeks-1-6.html'
        # Outputs from an earlier test run are test artifacts only, explicitly
        # unlinked here so the production command can retain no-overwrite policy.
        updated_html.unlink(missing_ok=True)
        result = apply_update(source, delta, inputs, updated_course, updated_html, exported)
        assert result['preserved_edit_fields'] == 6
        assert not validate_html(updated_html.read_text(encoding='utf-8'))
        page2 = context.new_page()
        page2.on('pageerror', lambda error: errors.append(str(error)))
        page2.goto(updated_html.as_uri())
        expect(page2.locator('.section')).to_have_count(6)
        assert page2.locator('.section>.week-label').all_text_contents() == [f'Week {n}' for n in range(1, 7)]
        expect(page2.locator('#section-week-01 .explanation-body')).to_contain_text('My note: always carry the units.')
        expect(page2.locator('#section-week-01 h2')).to_have_text('Quantities in my own words')
        expect(page2.locator('#section-week-02 .equation-render')).to_have_attribute('data-raw', r'\bar{r}=\frac{18}{3}=6')
        expect(page2.locator('#section-week-03 td').first).to_have_text('My amount label')
        expect(page2.locator('#section-week-04 figcaption')).to_have_text('My diagram note: follow the units.')
        expect(page2.locator('#section-week-05 li').first).to_have_text('First, define the amount carefully.')
        assert page2.locator('img').evaluate('(e) => e.complete && e.naturalWidth > 0')
        expect(page2.locator('#section-week-06')).to_contain_text('240 units per minute')
        page2.locator('#search').fill('240 units per minute')
        expect(page2.locator('nav a:visible')).to_have_count(1)
        page2.locator('nav a:visible').click()
        expect(page2.locator('#search')).to_have_value('240 units per minute')
        page2.locator('#search').fill('')
        page2.set_viewport_size({'width': 390, 'height': 844})
        page2.locator('#nav-toggle').click()
        page2.locator('nav a[href="#section-week-06"]').click()
        expect(page2.locator('#section-week-06 h2')).to_be_in_viewport()
        assert page2.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page2.screenshot(path=str(ARTIFACTS / f'{name}-weekly-mobile.png'))
        page2.locator('#section-week-06 .explanation-body').fill('My Week 6 explanation, retained in the next update.')
        saved_again = save(page2, f'{name}-weekly-after-week-6.html')
        assert not read_snapshot(saved_again.read_text(encoding='utf-8')).get('capture_error')
        text = 'Synthetic Week 7: use the same calculation in another context.'
        (inputs / 'week-07.txt').write_text(text, encoding='utf-8')
        week7 = {'schema_version': 3, 'course_id': 'weekly-measurement-demo',
                 'sources': [{'path': 'week-07.txt', 'sha256': hashlib.sha256(text.encode()).hexdigest(), 'week': 7}],
                 'sections': [{'id': 'week-07', 'week': 7, 'title': 'Continue the reading trail', 'source_files': ['week-07.txt'],
                               'blocks': [{'id': 'connect', 'type': 'concept', 'title': 'Connect the ideas', 'summary': 'Prior explanations can be reused.'}]}]}
        next_delta = authoring / 'week-07.delta.json'
        next_delta.write_text(json.dumps(week7), encoding='utf-8')
        final_json, final_html = authoring / 'weeks-1-7.json', authoring / 'weeks-1-7.html'
        apply_update(updated_course, next_delta, inputs, final_json, final_html, saved_again)
        final = json.loads(final_json.read_text(encoding='utf-8'))
        assert len(final['sections']) == 7
        assert 'My note: always carry the units.' in final['sections'][0]['blocks'][0]['body']
        assert final['sections'][5]['blocks'][0]['body'] == 'My Week 6 explanation, retained in the next update.'
        assert not scan_sources(final, inputs)['new']
        # Structural edits that cannot be mapped must keep the visible HTML but
        # explicitly block automatic reconciliation, rather than drop notes.
        page2.locator('#section-week-06 .lead').evaluate('(e) => e.after(e.cloneNode(true))')
        unsupported = save(page2, f'{name}-weekly-structural-edit.html')
        assert read_snapshot_unavailable(unsupported)
        assert not errors, errors
        context.close()
        browser.close()
        return {'browser': name, 'result': 'passed', 'week6_preserved_edit_fields': result['preserved_edit_fields'], 'second_update_week_count': 7}


def read_snapshot_unavailable(path):
    try:
        read_snapshot(path.read_text(encoding='utf-8'))
    except ValueError as error:
        return 'incomplete edit capture' in str(error)
    return False


if __name__ == '__main__':
    with sync_playwright() as playwright:
        results = [run(playwright.chromium, 'edge', channel='msedge'), run(playwright.firefox, 'firefox')]
    (ARTIFACTS / 'weekly-results.json').write_text(json.dumps(results, indent=2), encoding='utf-8')
    print(json.dumps(results, indent=2))
