"""Verify that bullet explanations collapse in Review and survive saved exports."""
import argparse
import json
import sys
import tempfile
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build import (  # noqa: E402 -- local scripts after path bootstrap
    load_config,
    render_course,
)
from validate import validate_html  # noqa: E402 -- local scripts after path bootstrap


def run(browser_type, name, **launch_options):
    course = json.loads((ROOT / 'demo/sample_course.json').read_text(encoding='utf-8'))
    course['sections'][0]['blocks'].append({
        'type': 'review', 'id': 'expanded-bullets', 'learn_only': True,
        'title': 'Expanded bullet explanation', 'summary': 'Extra context for learning.',
        'steps': ['Distinctive explanation about the measuring instrument.', 'Another supporting detail.'],
    })
    with tempfile.TemporaryDirectory() as directory:
        source = Path(directory) / 'reading.html'
        source.write_text(render_course(course, ROOT / 'demo', load_config()), encoding='utf-8')
        browser = browser_type.launch(headless=True, **launch_options)
        context = browser.new_context(accept_downloads=True, viewport={'width': 1440, 'height': 1000})
        context.add_init_script('window.showSaveFilePicker = undefined')
        context.route('https://cdn.jsdelivr.net/**', lambda route: route.abort())
        page = context.new_page()
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.goto(source.as_uri())
        expect(page.locator('#study-brief')).to_be_hidden()
        brief_text = page.locator('#study-brief').text_content()
        extra = page.locator('[data-block-id="expanded-bullets"]')
        expect(extra).to_be_visible()
        expect(extra.locator('.label')).to_have_text('Further explanation')
        extra.locator('li').first.fill('Distinctive explanation with a saved personal note.')
        page.locator('#review').click()
        expect(extra).to_be_hidden()
        expect(page.locator('[data-type="formula"]').first).to_be_visible()
        expect(page.locator('[data-type="comparison"]').first).to_be_visible()
        # Genuine takeaways remain visible; formatting alone must not hide them.
        expect(page.locator('[data-type="review"]:not(.explanation)').first).to_be_visible()
        page.locator('#search').fill('Distinctive explanation')
        expect(extra).to_be_visible()
        page.locator('#search').fill('')
        expect(extra).to_be_hidden()
        with page.expect_download() as download:
            page.locator('#save').click()
        saved = Path(directory) / 'saved.html'
        download.value.save_as(saved)
        assert not validate_html(saved.read_text(encoding='utf-8'))
        reopened = context.new_page()
        reopened.on('pageerror', lambda error: errors.append(str(error)))
        reopened.goto(saved.as_uri())
        expect(reopened.locator('#study-brief')).to_be_hidden()
        assert reopened.locator('#study-brief').text_content() == brief_text
        state = reopened.locator('#suite-state').evaluate('(e) => JSON.parse(e.textContent)')
        assert state['baseline']['study_brief'] == course['study_brief']
        expect(reopened.locator('body')).to_have_attribute('data-mode', 'review')
        saved_extra = reopened.locator('[data-block-id="expanded-bullets"]')
        expect(saved_extra).to_be_hidden()
        reopened.locator('#learn').click()
        expect(saved_extra).to_be_visible()
        expect(saved_extra.locator('li').first).to_contain_text('saved personal note')
        assert saved_extra.locator('li').first.evaluate('(e) => e.isContentEditable')
        for width in (390, 320):
            reopened.set_viewport_size({'width': width, 'height': 844})
            reopened.locator('#review').click()
            expect(saved_extra).to_be_hidden()
            reopened.locator('#learn').click()
            expect(saved_extra).to_be_visible()
            assert reopened.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
        assert not errors, errors
        context.close()
        browser.close()
    return {'browser': name, 'learn_review_search_export_reopen_mobile': 'passed'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--browser', choices=('edge', 'firefox', 'all'), default='all')
    args = parser.parse_args()
    with sync_playwright() as p:
        results = []
        if args.browser in ('edge', 'all'):
            results.append(run(p.chromium, 'Edge', channel='msedge'))
        if args.browser in ('firefox', 'all'):
            results.append(run(p.firefox, 'Firefox'))
    print(json.dumps(results, indent=2))
