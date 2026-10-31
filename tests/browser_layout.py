"""Check unequal-height packing, companion figures and portable measurements."""
import copy
import json
import re
import sys
import tempfile
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build import load_config, render_course


def run():
    course = json.loads((ROOT / 'demo/sample_course.json').read_text(encoding='utf-8-sig'))
    figure = copy.deepcopy(next(b for s in course['sections'] for b in s['blocks'] if b['type'] == 'figure'))
    figure.update(id='companion', placement='alongside')
    section = course['sections'][0]
    section['blocks'] = [
        {'id': 'tall', 'type': 'concept', 'title': 'Tall', 'summary': 'First concept.',
         'body': '\n\n'.join(['A longer synthetic teaching explanation.'] * 18)},
        {'id': 'short', 'type': 'concept', 'title': 'Short', 'summary': 'Second concept.'},
        {'id': 'following', 'type': 'concept', 'title': 'Following', 'summary': 'Third concept.'},
        {'id': 'boundary', 'type': 'comparison', 'title': 'Comparison boundary',
         'summary': 'A wide teaching structure.', 'headers': ['A', 'B'], 'rows': [['One', 'Two']]},
        {'id': 'companion-text', 'type': 'concept', 'title': 'Figure explanation',
         'summary': 'The illustration belongs with this explanation.'},
        figure,
    ]
    course['sections'] = [section]
    course['included_section_ids'] = [section['id']]
    course.pop('study_brief', None)  # Fixture replaces the sections named by the demo brief.
    with tempfile.TemporaryDirectory() as directory, sync_playwright() as p:
        target = Path(directory) / 'reader.html'
        target.write_text(render_course(course, ROOT / 'demo', load_config()), encoding='utf-8')
        browser = p.chromium.launch(channel='msedge', headless=True)
        context = browser.new_context(accept_downloads=True, reduced_motion='reduce', viewport={'width': 2560, 'height': 1440})
        context.add_init_script('window.showSaveFilePicker=undefined')
        context.route('https://cdn.jsdelivr.net/**', lambda route: route.abort())
        page = context.new_page()
        page.goto(target.as_uri())
        page.wait_for_function("document.querySelector('.card-group').classList.contains('packed')")

        def rect(ident):
            return page.locator(f'[data-block-id="{ident}"]').bounding_box()

        def settled():
            page.evaluate('()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))')

        def no_overlap():
            boxes = page.locator('.block').evaluate_all('(items)=>items.filter(e=>e.getClientRects().length).map(e=>e.getBoundingClientRect().toJSON())')
            for index, a in enumerate(boxes):
                for b in boxes[index + 1:]:
                    assert min(a['right'], b['right']) - max(a['left'], b['left']) <= 1 or min(a['bottom'], b['bottom']) - max(a['top'], b['top']) <= 1
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')

        settled()
        tall, short, following = [rect(x) for x in ('tall', 'short', 'following')]
        assert abs(following['x'] - short['x']) < 2
        assert 23 <= following['y'] - short['y'] - short['height'] <= 26
        assert following['y'] < tall['y'] + tall['height']
        text, image = rect('companion-text'), rect('companion')
        assert abs(text['y'] - image['y']) < 2 and image['x'] > text['x']
        no_overlap()
        before = page.locator('.card-group').bounding_box()['height']
        page.locator('[data-block-id="tall"] details.explanation summary').click()
        settled()
        assert page.locator('.card-group').bounding_box()['height'] < before
        no_overlap()
        for width in (1920, 1366, 1000, 390, 320):
            page.set_viewport_size({'width': width, 'height': 900})
            settled()
            no_overlap()
            if width > 720:
                page.locator('#nav-toggle').click()
                settled()
                no_overlap()
                page.locator('#nav-toggle').click()
        # Export must not retain spans measured for the current viewport.
        with page.expect_download() as event:
            page.locator('#save').click()
        saved = Path(directory) / 'saved.html'
        event.value.save_as(saved)
        assert not re.search(r'<article[^>]*grid-row-end', saved.read_text(encoding='utf-8'))
        page.set_viewport_size({'width': 2560, 'height': 1440})
        page.goto(saved.as_uri())
        settled()
        expect(page.locator('.card-group.packed')).to_have_count(1)
        no_overlap()
        browser.close()
    return {'packed_cards_companion_figures_resize_disclosure_export': 'passed'}


if __name__ == '__main__':
    print(json.dumps(run(), indent=2))
