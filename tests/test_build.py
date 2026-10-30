"""Focused deterministic builder checks; run with unittest discovery."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build import (  # noqa: E402 -- local scripts after path bootstrap
    build,
    embedded_asset,
    explanation_html,
    load_config,
    render_block,
    render_course,
    rich_text,
    validate_course,
)
from validate import validate_html  # noqa: E402 -- local scripts after path bootstrap


class BuilderTests(unittest.TestCase):
    def setUp(self):
        self.course = json.loads((ROOT / 'demo/sample_course.json').read_text(encoding='utf-8-sig'))

    def test_study_brief_is_escaped_hidden_and_preserved_in_snapshot(self):
        from course_state import read_snapshot

        self.course['study_brief']['course_context'] += ' <script>alert(1)</script>'
        value = render_course(self.course, ROOT / 'demo', load_config())
        self.assertIn('<aside id="study-brief" hidden>', value)
        self.assertIn('&lt;script&gt;alert(1)&lt;/script&gt;', value)
        self.assertNotIn('<script>alert(1)</script>', value)
        self.assertEqual(read_snapshot(value)['baseline']['study_brief'], self.course['study_brief'])
        self.assertFalse(validate_html(value))
        del self.course['study_brief']
        self.assertNotIn('id="study-brief"', render_course(self.course, ROOT / 'demo', load_config()))

    def test_study_brief_rejects_unlabelled_claims_and_stale_section_references(self):
        valid = copy.deepcopy(self.course)
        for field, bad_value in [('basis', 'certain_exam_prediction'), ('section_ids', ['missing-section']),
                                 ('evidence', ''), ('statement', '')]:
            with self.subTest(field=field):
                self.course = copy.deepcopy(valid)
                self.course['study_brief']['scope'][0][field] = bad_value
                with self.assertRaisesRegex(ValueError, 'study_brief'):
                    validate_course(self.course)

    def test_study_brief_contains_context_without_tutor_behavior_directives(self):
        value = render_course(self.course, ROOT / 'demo', load_config())
        self.assertNotIn('Author-recommended tutoring approach', value)
        self.assertNotIn('Follow the learner', value)
        self.course['study_brief']['tutoring_guidance'] = ['Use a fixed tutoring method.']
        with self.assertRaisesRegex(ValueError, 'context only'):
            validate_course(self.course)

    def test_portable_deterministic_build(self):
        with tempfile.TemporaryDirectory() as directory:
            a, b = Path(directory) / 'a.html', Path(directory) / 'b.html'
            build(ROOT / 'demo/sample_course.json', a)
            build(ROOT / 'demo/sample_course.json', b)
            self.assertEqual(a.read_bytes(), b.read_bytes())
            self.assertFalse(validate_html(a.read_text(encoding='utf-8'), 3))
            self.assertIn('data:image/svg+xml;base64,', a.read_text(encoding='utf-8'))

    def test_no_practice(self):
        with self.assertRaises(ValueError):
            load_config(overrides={'practice': 'quiz'})
        self.course['sections'][0]['blocks'][0]['type'] = 'flashcard'
        with self.assertRaises(ValueError):
            validate_course(self.course)

    def test_safe_bold_and_bullet_explanations(self):
        value = explanation_html('Short introduction.\n\n- **Photosynthesis:** light and carbon.\n- **Lipids:** a conditional feedstock.\n\nConditions still apply.')
        self.assertIn('<ul><li><strong>Photosynthesis:</strong>', value)
        self.assertIn('</ul><p>Conditions still apply.</p>', value)
        self.assertIn('&lt;script&gt;', rich_text('**<script>**'))
        self.assertNotIn('<script>', rich_text('**<script>**'))
        self.assertIn('data-raw="x=2"', rich_text(r'**Rate** and \(x=2\)'))

    def test_process_flow_preserves_ordered_editable_steps(self):
        block = {'type': 'process', 'title': 'Conversion', 'summary': 'A sequence.',
                 'presentation': 'flow', 'steps': ['**Input** enters.', 'Output leaves.'],
                 'body': 'An optional explanation.'}
        rendered = render_block(block, ROOT / 'demo', load_config(), 'sections/0/blocks/0')
        self.assertIn('<ol class="process-flow"', rendered)
        self.assertIn('data-field="sections/0/blocks/0/steps/0"', rendered)
        self.assertIn('<strong>Input</strong> enters.', rendered)
        self.assertIn('<details class="explanation" open>', rendered)
        self.course['sections'][0]['blocks'][0]['presentation'] = 'flow'
        with self.assertRaisesRegex(ValueError, 'presentation'):
            validate_course(self.course)

    def test_focused_learning_build_preserves_authored_content(self):
        # Depth is validated authoring metadata, not an automatic text cutter.
        with tempfile.TemporaryDirectory() as directory:
            output = build(ROOT / 'demo/sample_course.json', Path(directory) / 'focused.html',
                           ROOT / 'config/focused.example.toml')
            value = output.read_text(encoding='utf-8')
            self.assertFalse(validate_html(value, 3))
            self.assertIn('focused learning', value)
            self.assertIn(self.course['sections'][0]['blocks'][0]['summary'], value)

    def test_learn_only_bullets_use_explanation_visibility(self):
        block = {'type': 'review', 'id': 'extra-context', 'title': 'More context',
                 'summary': 'Expanded teaching points.', 'steps': ['First explanation.', 'Second explanation.'],
                 'learn_only': True}
        rendered = render_block(block, ROOT / 'demo', load_config(), 'sections/0/blocks/0')
        self.assertIn('takeaway explanation', rendered)
        self.assertIn('Further explanation', rendered)
        self.assertIn('<ul>', rendered)
        self.assertIn('data-field="sections/0/blocks/0/steps/0"', rendered)
        block['learn_only'] = False
        persistent = render_block(block, ROOT / 'demo', load_config())
        self.assertNotIn('takeaway explanation', persistent)
        self.assertIn('Section takeaway', persistent)

    def test_learn_only_requires_boolean(self):
        self.course['sections'][0]['blocks'][0]['learn_only'] = 'true'
        with self.assertRaisesRegex(ValueError, 'learn_only must be true or false'):
            validate_course(self.course)

    def test_selection_and_duplicate_ids(self):
        self.course['included_section_ids'].pop()
        with self.assertRaises(ValueError):
            validate_course(self.course)
        self.setUp()
        self.course['sections'][1]['id'] = 'foundations'
        with self.assertRaises(ValueError):
            validate_course(self.course)

    def test_invalid_table(self):
        self.course['sections'][0]['blocks'][2]['rows'][0].pop()
        with self.assertRaises(ValueError):
            validate_course(self.course)

    def test_plain_text_escaped(self):
        self.course['title'] = '<script>alert(1)</script> {{CSS}}'
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'course.json'
            # No local figure needed for this escaping check.
            source.write_text(json.dumps(self.course), encoding='utf-8')
            output = build(source, Path(directory) / 'out.html', overrides={'visuals': 'off'})
            value = output.read_text(encoding='utf-8')
            self.assertIn('&lt;script&gt;alert(1)&lt;/script&gt; {{CSS}}', value)
            self.assertNotIn('<script>alert(1)</script>', value)

    def test_assets_and_visual_policy(self):
        block = self.course['sections'][1]['blocks'][3]
        block['asset'] = '../template/app.js'
        with self.assertRaises(ValueError):
            embedded_asset(block, ROOT / 'demo')
        with tempfile.TemporaryDirectory() as directory:
            output = build(ROOT / 'demo/sample_course.json', Path(directory) / 'out.html', overrides={'visuals': 'slide_only'})
            self.assertNotIn('data:image/', output.read_text(encoding='utf-8'))

    def test_svg_active_content_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'bad.svg'
            path.write_text('<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>')
            with self.assertRaises(ValueError):
                embedded_asset({'asset': 'bad.svg'}, Path(directory))

    def test_config_overrides(self):
        config = load_config(ROOT / 'config/course.example.toml', {'depth': 'cram'})
        self.assertEqual(config['depth'], 'cram')
        self.assertEqual(config['theme_accent'], 'violet')
        with self.assertRaises(ValueError):
            load_config(overrides={'language': 'tr'})

    def test_production_demo_guard(self):
        self.course['synthetic'] = False
        self.course['subtitle'] = 'Synthetic demo'
        with self.assertRaises(ValueError):
            validate_course(self.course)

    def test_validator_detects_broken_output(self):
        value = (ROOT / 'output/Demo_Study_Suite.html').read_text(encoding='utf-8')
        errors = validate_html(value.replace('id="section-foundations"', 'id="save"'))
        self.assertTrue(any('Duplicate' in e for e in errors))
        self.assertTrue(any('Missing anchor' in e for e in errors))

    def test_validator_detects_paragraph_repair(self):
        value = (ROOT / 'output/Demo_Study_Suite.html').read_text(encoding='utf-8')
        errors = validate_html(value.replace('</main>', '<p><div>Inserted notes</div></p></main>'))
        self.assertTrue(any('Invalid paragraph nesting' in e for e in errors))

    def test_optional_intro_omitted(self):
        for section in self.course['sections']:
            section.pop('intro', None)
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'course.json'
            source.write_text(json.dumps(self.course), encoding='utf-8')
            output = build(source, Path(directory) / 'out.html', overrides={'visuals': 'off'})
            value = output.read_text(encoding='utf-8')
            self.assertNotIn('class="editable-text section-intro"', value)
            self.assertFalse(validate_html(value))


if __name__ == '__main__':
    unittest.main()
