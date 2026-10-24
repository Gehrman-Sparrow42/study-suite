"""Verify bold/list editing, saved snapshots, rebuilding and browser recovery."""
import json
import sys
import tempfile
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build import load_config, render_course
from course_state import read_snapshot, reconcile_edits
from validate import validate_html


def run():
    course = json.loads((ROOT / 'demo/sample_course.json').read_text(encoding='utf-8'))
    host = course['sections'][0]['blocks'][0]
    host['summary'] = '**Problem:** Interpret a synthetic rate.\n\n**Given:** Two illustrative quantities.\n\n**Find:** The rate and its units.'
    host['body'] = 'Useful **products**.\n\n- **Light:** a condition.\n- **Rate:** \\(x=2\\) is illustrative.\n\nConditions remain important.'
    course['sections'][0]['blocks'].append({
        'id': 'flow-example', 'type': 'process', 'title': 'Synthetic process',
        'summary': 'Input becomes output.', 'presentation': 'flow',
        'steps': ['**Input** enters.', 'Output leaves.'],
    })
    course['sections'][0]['blocks'].append({
        'id': 'compact-table', 'type': 'comparison', 'compact': True,
        'title': 'Small comparison', 'summary': 'Two related meanings.',
        'headers': ['Term', 'Meaning'], 'rows': [['Input', 'Feed'], ['Output', 'Product']],
    })
    with tempfile.TemporaryDirectory() as directory:
        target = Path(directory) / 'reader.html'
        target.write_text(render_course(course, ROOT / 'demo', load_config()), encoding='utf-8')
        with sync_playwright() as p:
            browser = p.chromium.launch(channel='msedge', headless=True)
            context = browser.new_context(accept_downloads=True)
            context.add_init_script('window.showSaveFilePicker=undefined')
            context.route('https://cdn.jsdelivr.net/**', lambda route: route.abort())
            page = context.new_page()
            page.goto(target.as_uri())
            body = page.locator('.explanation-body').first
            expect(page.locator('.lead').first.locator('p')).to_have_count(3)
            expect(page.locator('.card-group>.compact[data-type="comparison"]')).to_have_count(1)
            expect(body.locator('li')).to_have_count(2)
            expect(body.locator('strong')).to_have_count(3)
            disclosure = body.locator('..')
            disclosure.locator('summary').click()
            expect(body).to_be_hidden()
            page.locator('#search').fill('Useful products')
            expect(body).to_be_visible()
            page.locator('#search').fill('')
            expect(body).to_be_hidden()
            disclosure.locator('summary').click()
            expect(body).to_be_visible()
            section = body.locator('xpath=ancestor::section')
            section.locator('.section-toggle').click()
            expect(body).to_be_hidden()
            page.locator('#search').fill('Useful products')
            expect(body).to_be_visible()
            # A clean export must not invent edits merely from rendering formatting.
            with page.expect_download() as event:
                page.locator('#save').click()
            clean = Path(directory) / 'clean.html'
            event.value.save_as(clean)
            assert not read_snapshot(clean.read_text(encoding='utf-8'))['edits']
            reopened = context.new_page()
            reopened.goto(clean.as_uri())
            expect(reopened.locator('.explanation-body').first).to_be_hidden()
            reopened.locator('nav a').first.click()
            expect(reopened.locator('.explanation-body').first).to_be_visible()
            reopened.close()
            page.locator('#search').fill('')
            expect(body).to_be_hidden()
            page.locator('nav a').first.click()
            expect(body).to_be_visible()
            page.locator('.process-flow li').first.fill('Edited input enters.')
            body.locator('strong').first.fill('edited products')
            body.locator('li').last.click()
            page.keyboard.press('End')
            page.keyboard.press('Enter')
            page.keyboard.type('A new editable bullet.')
            expect(body.locator('li')).to_have_count(3)
            page.locator('#review').click()
            expect(body).to_be_hidden()
            page.locator('#search').fill('edited products')
            expect(body).to_be_visible()
            page.locator('#search').fill('')
            expect(body).to_be_hidden()
            page.locator('#learn').click()
            # Actual recovery reconstructs semantic lists and emphasis from markers.
            page.wait_for_timeout(450)
            page.reload()
            expect(page.locator('#restore-recovery')).to_be_visible()
            page.locator('#restore-recovery').click()
            body = page.locator('.explanation-body').first
            expect(body.locator('li')).to_have_count(3)
            expect(body.locator('strong').first).to_have_text('edited products')
            with page.expect_download() as event:
                page.locator('#save').click()
            saved = Path(directory) / 'saved.html'
            event.value.save_as(saved)
            assert not validate_html(saved.read_text(encoding='utf-8'))
            state = read_snapshot(saved.read_text(encoding='utf-8'))
            edited, count = reconcile_edits(state['baseline'], state)
            assert count == 2
            rebuilt = Path(directory) / 'rebuilt.html'
            rebuilt.write_text(render_course(edited, ROOT / 'demo', load_config()), encoding='utf-8')
            for output in (saved, rebuilt):
                page.goto(output.as_uri())
                body = page.locator('.explanation-body').first
                expect(body.locator('li')).to_have_count(3)
                expect(body.locator('strong').first).to_have_text('edited products')
                assert body.locator('li').last.evaluate('(e)=>e.isContentEditable')
                expect(body.locator('.equation-render')).to_have_attribute('data-raw', 'x=2')
                expect(page.locator('.process-flow li').first).to_have_text('Edited input enters.')
            browser.close()
    return {'bold_lists_clean_snapshot_edit_recovery_export_rebuild': 'passed'}


if __name__ == '__main__':
    print(json.dumps(run(), indent=2))
