"""Weekly updates: source identity, stable merges, ordering and preservation failures."""
import copy
import hashlib
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build import build, load_config, render_course  # noqa: E402 -- local scripts after path bootstrap
from course_state import prepare_course, read_snapshot, reconcile_edits  # noqa: E402
from update import apply_update, scan_sources  # noqa: E402


class WeeklyUpdateTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.source = self.root / 'course.json'
        self.delta = self.root / 'week-06.delta.json'
        self.inputs = self.root / 'inputs'
        shutil.copytree(ROOT / 'demo/weekly_sources', self.inputs)
        shutil.copy2(ROOT / 'demo/measurement.svg', self.root / 'measurement.svg')
        shutil.copy2(ROOT / 'demo/weekly_course.json', self.source)
        shutil.copy2(ROOT / 'demo/week_06.delta.json', self.delta)
        self.course = json.loads(self.source.read_text())
        self.initial = build(self.source, self.root / 'initial.html')
        self.state = read_snapshot(self.initial.read_text(encoding='utf-8'))
        self.output_course, self.output_html = self.root / 'next.json', self.root / 'next.html'

    def saved_html(self, state):
        value = self.initial.read_text(encoding='utf-8')
        start = value.index('>', value.index('<script id="suite-state"')) + 1
        end = value.index('</script>', start)
        state_text = json.dumps(state).replace('<', '\\u003c')
        path = self.root / 'edited.html'
        path.write_text(value[:start] + state_text + value[end:], encoding='utf-8')
        return path

    def apply(self, edited_html=None):
        return apply_update(self.source, self.delta, self.inputs, self.output_course, self.output_html, edited_html)

    def test_scan_tracks_new_duplicate_changed_and_missing_sources(self):
        report = scan_sources(self.course, self.inputs)
        self.assertEqual([s['path'] for s in report['new']], ['week-06.txt'])
        shutil.copy2(self.inputs / 'week-01.txt', self.inputs / 'renamed.pdf')
        (self.inputs / 'week-02.txt').write_text('Updated lecture')
        (self.inputs / 'week-03.txt').unlink()
        report = scan_sources(self.course, self.inputs)
        self.assertEqual(report['duplicates'][0]['path'], 'renamed.pdf')
        self.assertEqual(report['changed'][0]['path'], 'week-02.txt')
        self.assertEqual(report['missing'][0]['path'], 'week-03.txt')

    def test_append_preserves_existing_content_and_sources(self):
        before = self.source.read_bytes()
        result = self.apply()
        updated = json.loads(self.output_course.read_text())
        self.assertEqual(result['added_sections'], 1)
        self.assertEqual(updated['sections'][:5], prepare_course(self.course)['sections'])
        self.assertEqual(len(updated['sources']), 6)
        self.assertEqual(self.source.read_bytes(), before)
        self.assertIn('data:image/svg+xml;base64,', self.output_html.read_text(encoding='utf-8'))
        self.assertFalse(scan_sources(updated, self.inputs)['new'])

    def test_browser_edits_merge_into_source(self):
        self.state['edits'] = {
            'sections/0/blocks/0/body': 'My first paragraph.\n\nMy new paragraph with \\(x=2\\).',
            'sections/1/blocks/0/latex': r'\bar{r}=6',
            'sections/2/blocks/0/rows/0/2': 'My table wording',
            'sections/3/blocks/0/caption': 'My figure explanation',
            'sections/4/blocks/0/steps/0': 'My first step',
            'title': 'My course edition',
        }
        result = self.apply(self.saved_html(self.state))
        updated = json.loads(self.output_course.read_text())
        self.assertEqual(result['preserved_edit_fields'], 6)
        self.assertEqual(updated['title'], 'My course edition')
        self.assertEqual(updated['sections'][0]['blocks'][0]['body'], self.state['edits']['sections/0/blocks/0/body'])
        self.assertEqual(updated['sections'][1]['blocks'][0]['latex'], r'\bar{r}=6')

    def test_conflicting_edits_stop_without_writing_outputs(self):
        self.state['edits']['sections/0/blocks/0/body'] = 'Browser explanation'
        self.course['sections'][0]['blocks'][0]['body'] = 'Different authored explanation'
        self.source.write_text(json.dumps(self.course))
        with self.assertRaisesRegex(ValueError, 'Conflicting browser/source edits'):
            self.apply(self.saved_html(self.state))
        self.assertFalse(self.output_course.exists())
        self.assertFalse(self.output_html.exists())

    def test_unrelated_authored_edits_and_reordering_merge_by_id(self):
        self.state['edits']['sections/0/blocks/0/body'] = 'Browser explanation'
        self.course['sections'][1]['blocks'][0]['summary'] = 'Authored clarification'
        self.course['sections'].reverse()
        merged, count = reconcile_edits(self.course, self.state)
        self.assertEqual(count, 1)
        self.assertEqual(merged['sections'][0]['blocks'][0]['body'], 'Browser explanation')
        self.assertEqual(merged['sections'][1]['blocks'][0]['summary'], 'Authored clarification')

    def test_same_edit_on_both_sides_is_not_a_conflict(self):
        self.state['edits']['sections/0/title'] = 'Revised heading'
        self.course['sections'][0]['title'] = 'Revised heading'
        merged, _ = reconcile_edits(self.course, self.state)
        self.assertEqual(merged['sections'][0]['title'], 'Revised heading')

    def test_mismatched_course_and_invalid_edit_pointers_are_rejected(self):
        state = copy.deepcopy(self.state)
        state['baseline']['course_id'] = 'another-course'
        with self.assertRaisesRegex(ValueError, 'identity'):
            reconcile_edits(self.course, state)
        self.state['edits']['sections/999/title'] = 'Wrong target'
        with self.assertRaisesRegex(ValueError, 'Unrecognized edit'):
            reconcile_edits(self.course, self.state)

    def test_existing_output_is_never_overwritten(self):
        self.output_html.write_text('My saved notes')
        with self.assertRaisesRegex(ValueError, 'already exists'):
            self.apply()
        self.assertEqual(self.output_html.read_text(), 'My saved notes')
        self.assertFalse(self.output_course.exists())

    def test_changed_old_or_new_sources_stop_the_update(self):
        (self.inputs / 'week-01.txt').write_text('Changed old lecture')
        with self.assertRaisesRegex(ValueError, 'Previously processed sources changed'):
            self.apply()
        shutil.copy2(ROOT / 'demo/weekly_sources/week-01.txt', self.inputs / 'week-01.txt')
        (self.inputs / 'week-06.txt').write_text('Changed after authoring')
        with self.assertRaisesRegex(ValueError, 'changed since authoring'):
            self.apply()
        self.assertFalse(self.output_course.exists())

    def test_duplicate_content_under_new_name_is_not_processed_twice(self):
        delta = json.loads(self.delta.read_text())
        duplicate = self.course['sources'][0]['sha256']
        delta['sources'][0]['sha256'] = duplicate
        self.delta.write_text(json.dumps(delta))
        with self.assertRaisesRegex(ValueError, 'already processed'):
            self.apply()

    def test_wrong_week_and_unreferenced_sources_are_rejected(self):
        delta = json.loads(self.delta.read_text())
        delta['sections'][0]['week'] = 7
        self.delta.write_text(json.dumps(delta))
        with self.assertRaisesRegex(ValueError, 'week must match'):
            self.apply()
        delta['sections'][0]['week'] = 6
        delta['sections'][0]['source_files'] = ['unknown.pdf']
        self.delta.write_text(json.dumps(delta))
        with self.assertRaisesRegex(ValueError, 'source_files'):
            self.apply()

    def test_week_sort_is_numeric_and_stable(self):
        sections = self.course['sections']
        sections[0]['week'], sections[1]['week'] = 10, 2
        ordered = prepare_course(self.course)
        self.assertEqual([s['week'] for s in ordered['sections']], [2, 3, 4, 5, 10])
        self.assertEqual(ordered['sections'][0]['id'], 'week-02')

    def test_missing_assets_fail_before_publishing(self):
        (self.root / 'measurement.svg').unlink()
        with self.assertRaises(OSError):
            self.apply()
        self.assertFalse(self.output_course.exists())
        self.assertFalse(self.output_html.exists())

    def test_legacy_or_incomplete_html_is_not_guessed(self):
        with self.assertRaisesRegex(ValueError, 'Legacy HTML'):
            read_snapshot('<html>My old notes</html>')
        self.state['capture_error'] = 'A field disappeared'
        with self.assertRaisesRegex(ValueError, 'incomplete edit capture'):
            read_snapshot(self.saved_html(self.state).read_text(encoding='utf-8'))

    def test_snapshot_escapes_script_endings(self):
        self.course['title'] = '</script><script>alert(1)</script>'
        value = render_course(self.course, self.root, load_config())
        state = read_snapshot(value)
        self.assertEqual(state['baseline']['title'], self.course['title'])
        self.assertNotIn('</script><script>alert(1)', value)

    def test_multiple_weekly_updates_do_not_repeat_prior_material(self):
        self.apply()
        data = 'Synthetic week 7 material'
        (self.inputs / 'week-07.txt').write_text(data)
        delta = json.loads(self.delta.read_text())
        delta['sources'] = [{'path': 'week-07.txt', 'sha256': hashlib.sha256(data.encode()).hexdigest(), 'week': 7}]
        delta['sections'][0].update(id='week-07', week=7, source_files=['week-07.txt'])
        next_delta = self.root / 'week-07.delta.json'
        next_delta.write_text(json.dumps(delta))
        final_json, final_html = self.root / 'final.json', self.root / 'final.html'
        apply_update(self.output_course, next_delta, self.inputs, final_json, final_html, self.output_html)
        course = json.loads(final_json.read_text())
        self.assertEqual([s['week'] for s in course['sections']], list(range(1, 8)))
        self.assertEqual(len(course['sources']), 7)


if __name__ == '__main__':
    unittest.main()
