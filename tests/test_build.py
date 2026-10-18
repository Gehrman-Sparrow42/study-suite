"""Focused deterministic builder checks; run with unittest discovery."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build import build, load_config, validate_course, embedded_asset
from validate import validate_html


class BuilderTests(unittest.TestCase):
    def setUp(self):
        self.course = json.loads((ROOT / 'demo/sample_course.json').read_text(encoding='utf-8-sig'))

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


if __name__ == '__main__':
    unittest.main()
