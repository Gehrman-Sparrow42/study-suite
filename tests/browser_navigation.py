"""The contents panel follows reading, without scrolling the reading page."""
import copy
import json
import sys
import tempfile
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build import load_config, render_course


def run():
    course = json.loads((ROOT / 'demo/sample_course.json').read_text(encoding='utf-8'))
    prototype = course['sections'][0]
    course['sections'] = []
    for index in range(24):
        section = copy.deepcopy(prototype)
        section.update(id=f'topic-{index}', title=f'Topic {index + 1}: a long synthetic navigation title')
        course['sections'].append(section)
    course['included_section_ids'] = [section['id'] for section in course['sections']]
    course.pop('study_brief', None)
    with tempfile.TemporaryDirectory() as directory, sync_playwright() as p:
        target = Path(directory) / 'reader.html'
        target.write_text(render_course(course, ROOT / 'demo', load_config()), encoding='utf-8')
        browser = p.chromium.launch(channel='msedge', headless=True)
        context = browser.new_context(accept_downloads=True, reduced_motion='reduce', viewport={'width': 1366, 'height': 768})
        context.route('https://**/*', lambda route: route.abort())
        context.add_init_script('window.showSaveFilePicker=undefined')
        page = context.new_page()
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.goto(target.as_uri())
        page.add_style_tag(content='html{scroll-behavior:auto!important}')

        def go(index):
            page.evaluate('(i)=>window.scrollTo(0,document.querySelector("#section-topic-"+i).getBoundingClientRect().top+scrollY-115)', index)
            expect(page.locator(f'nav a[href="#section-topic-{index}"]')).to_have_attribute('aria-current', 'location')

        def current_is_inside_panel():
            assert page.evaluate('''() => {
              const s=document.querySelector('#sidebar').getBoundingClientRect();
              const a=document.querySelector('nav a[aria-current]').getBoundingClientRect();
              return a.top>=s.top+10 && a.bottom<=s.bottom-10;
            }''')

        go(20)
        current_is_inside_panel()
        assert page.locator('#sidebar').evaluate('(e)=>e.scrollTop') > 0
        reading_y = page.evaluate('scrollY')
        page.locator('#sidebar').evaluate('(e)=>e.scrollTop=0')
        assert page.evaluate('scrollY') == reading_y
        page.locator('#sidebar').evaluate('(e)=>e.scrollTop=e.scrollHeight')
        page.mouse.move(100, 400)
        page.mouse.wheel(0, 600)
        page.wait_for_timeout(500)
        assert page.evaluate('scrollY') == reading_y
        page.locator('#sidebar').evaluate('(e)=>e.scrollTop=0')
        # Scrolling within the same section must not fight manual contents browsing.
        page.evaluate('window.scrollBy(0,10)')
        page.wait_for_timeout(100)
        assert page.locator('#sidebar').evaluate('(e)=>e.scrollTop') == 0
        go(21)
        current_is_inside_panel()
        go(2)
        current_is_inside_panel()
        go(20)
        page.locator('#nav-toggle').click()
        page.locator('#sidebar').evaluate('(e)=>e.scrollTop=0')
        reading_y = page.evaluate('scrollY')
        page.locator('#nav-toggle').click()
        current_is_inside_panel()
        assert page.evaluate('scrollY') == reading_y
        page.set_viewport_size({'width':390,'height':844})
        page.evaluate('window.scrollTo(0,document.querySelector("#section-topic-22").getBoundingClientRect().top+scrollY-145)')
        expect(page.locator('nav a[href="#section-topic-22"]')).to_have_attribute('aria-current','location')
        reading_y = page.evaluate('scrollY')
        page.locator('#nav-toggle').click()
        current_is_inside_panel()
        assert page.evaluate('scrollY') == reading_y
        page.locator('#scrim').click(position={'x':380,'y':20})
        with page.expect_download() as event:
            page.locator('#save').click()
        saved = Path(directory) / 'saved.html'
        event.value.save_as(saved)
        page.goto(saved.as_uri())
        page.set_viewport_size({'width':1366,'height':768})
        page.add_style_tag(content='html{scroll-behavior:auto!important}')
        go(23)
        current_is_inside_panel()
        assert not errors, errors
        browser.close()
    return {'contents_follows_only_reading_desktop_mobile_export': 'passed'}


if __name__ == '__main__':
    print(json.dumps(run(), indent=2))
