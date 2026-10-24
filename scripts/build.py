"""Build one portable Study Suite from authored JSON. Python 3.11+, no dependencies."""
from __future__ import annotations

import argparse
import base64
import html
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import tomllib
from course_state import prepare_course, snapshot_json, validate_metadata

ROOT = Path(__file__).resolve().parents[1]
CATEGORIES = {'definition', 'process', 'formula', 'warning'}
TYPES = {'concept', 'prose', 'process', 'formula', 'comparison', 'worked', 'figure', 'review', 'details'}
ACCENTS = {'auto': '#88b9ae', 'teal': '#88b9ae', 'violet': '#b5a2d4', 'blue': '#96b8db', 'green': '#96c3a4'}
EDIT = ' contenteditable="true" spellcheck="false"'


def esc(value: str) -> str:
    return html.escape(str(value), quote=True)


def text(value, location: str, *, allow_empty=False) -> str:
    if not isinstance(value, str) or (not allow_empty and not value.strip()):
        raise ValueError(f'{location}: expected nonempty text')
    if any(ord(c) < 32 and c not in '\n\r\t' for c in value):
        raise ValueError(f'{location}: invalid control character (check LaTeX escapes)')
    return value


def load_config(path: Path | None = None, overrides: dict | None = None) -> dict:
    config = tomllib.loads((ROOT / 'config/defaults.toml').read_text(encoding='utf-8-sig'))
    allowed = set(config) | {'exam_days_left'}
    if path:
        config.update(tomllib.loads(path.read_text(encoding='utf-8-sig')))
    config.update(overrides or {})
    if set(config) - allowed:
        raise ValueError(f'Unknown configuration keys: {sorted(set(config) - allowed)}')
    choices = {'language': {'en'}, 'depth': {'cram', 'focused_learning', 'balanced_high_yield', 'thorough'},
               'visuals': {'off', 'slide_only', 'smart'}, 'visual_density': {'low', 'adaptive', 'high'},
               'practice': {'off'}, 'source_labels': {'minimal', 'off'}}
    for key, values in choices.items():
        if not isinstance(config[key], str) or config[key] not in values:
            raise ValueError(f'{key}: choose from {sorted(values)}')
    for key in ('include_review_mode', 'allow_web_visuals'):
        if type(config[key]) is not bool:
            raise ValueError(f'{key}: expected true or false')
    accent = config['theme_accent']
    if not isinstance(accent, str) or (accent not in ACCENTS and not re.fullmatch(r'#[0-9a-fA-F]{6}', accent)):
        raise ValueError('theme_accent: expected a named accent or #RRGGBB')
    if 'exam_days_left' in config and (type(config['exam_days_left']) is not int or config['exam_days_left'] < 0):
        raise ValueError('exam_days_left must be a nonnegative integer')
    filename = config['output_filename']
    if not isinstance(filename, str) or '/' in filename or '\\' in filename or not filename.endswith('.html'):
        raise ValueError('output_filename must be a plain .html filename')
    text(config['course_title'], 'course_title', allow_empty=True)
    return config


def validate_course(course: dict) -> None:
    if not isinstance(course, dict) or course.get('schema_version') != 3:
        raise ValueError('Expected a course object with schema_version: 3')
    if course.get('language') != 'en':
        raise ValueError('Course language must be en; author and review all text in English')
    if type(course.get('synthetic')) is not bool:
        raise ValueError('Explicit synthetic: true/false is required')
    text(course.get('title'), 'title')
    text(course.get('subtitle'), 'subtitle')
    sections = course.get('sections')
    if not isinstance(sections, list) or not sections:
        raise ValueError('sections: expected a nonempty list')
    identifiers = set()
    for section in sections:
        if not isinstance(section, dict):
            raise ValueError('Each section must be an object')  # noqa: TRY004 - keep the public validation error contract
        ident = section.get('id', '')
        if not isinstance(ident, str) or not re.fullmatch(r'[a-z][a-z0-9-]*', ident) or ident in identifiers:
            raise ValueError(f'Invalid or duplicate section id: {ident!r}')
        identifiers.add(ident)
        text(section.get('title'), f'{ident}.title')
        text(section.get('intro', ''), f'{ident}.intro', allow_empty=True)
        if not isinstance(section.get('blocks'), list) or not section['blocks']:
            raise ValueError(f'{ident}: blocks must be a nonempty list')
        for block in section['blocks']:
            if not isinstance(block, dict):
                raise ValueError('Each block must be an object')  # noqa: TRY004 - keep the public validation error contract
            kind = block.get('type')
            if not isinstance(kind, str) or kind not in TYPES:
                raise ValueError(f'{ident}: unsupported block type {kind!r}; no question or quiz blocks')
            text(block.get('title'), f'{ident}.block.title')
            if 'compact' in block and type(block['compact']) is not bool:
                raise ValueError('compact must be true or false')
            if 'learn_only' in block and type(block['learn_only']) is not bool:
                raise ValueError('learn_only must be true or false')
            category = block.get('category', {'process': 'process', 'worked': 'formula', 'formula': 'formula'}.get(kind, 'definition'))
            if not isinstance(category, str) or category not in CATEGORIES:
                raise ValueError(f'Unknown semantic category {category!r}')
            for field in ('summary', 'body', 'source'):
                if field in block:
                    text(block[field], f'{ident}.{field}')
            if kind != 'figure' and not block.get('summary'):
                raise ValueError(f'{ident}/{block["title"]}: summary is required for Review mode')
            if kind == 'formula':
                text(block.get('latex'), f'{ident}.latex')
            if kind in {'process', 'worked', 'review'}:
                if not isinstance(block.get('steps'), list) or not block['steps']:
                    raise ValueError(f'{kind}: nonempty steps list required')
                for step in block['steps']:
                    text(step, f'{ident}.step')
            if kind == 'comparison':
                headers, rows = block.get('headers'), block.get('rows')
                if not isinstance(headers, list) or not headers or not isinstance(rows, list) or not rows:
                    raise ValueError('comparison: headers and rows must be nonempty lists')
                for header in headers:
                    text(header, 'table header')
                for row in rows:
                    if not isinstance(row, list) or len(row) != len(headers):
                        raise ValueError('comparison: every row must match the header width')
                    for cell in row:
                        text(cell, 'table cell')
            if kind == 'figure':
                for field in ('asset', 'alt', 'caption', 'credit'):
                    text(block.get(field), f'{ident}.{field}')
                if block.get('origin') not in {'slide', 'custom', 'web'}:
                    raise ValueError('figure origin must be slide, custom, or web')
                if block['origin'] == 'web':
                    for field in ('source_url', 'license'):
                        text(block.get(field), f'web figure {field}')
                    if not block['source_url'].startswith('https://'):
                        raise ValueError('Web figure requires an https source_url')
    expected = course.get('included_section_ids', [])
    if not isinstance(expected, list) or not all(isinstance(x, str) for x in expected) or len(set(expected)) != len(expected) or set(expected) != identifiers:
        raise ValueError('included_section_ids must list every selected section exactly once')
    if not course['synthetic'] and re.search(r'\b(synthetic demo|lorem ipsum|TODO|placeholder)\b', json.dumps(course), re.IGNORECASE):
        raise ValueError('Production content contains demo/placeholder markers')
    validate_metadata(course)


def embedded_asset(block: dict, content_dir: Path) -> str:
    path = (content_dir / block['asset']).resolve()
    if not path.is_relative_to(content_dir.resolve()):
        raise ValueError('Assets must be inside the content JSON directory')
    mime = {'.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp', '.svg': 'image/svg+xml'}.get(path.suffix.lower())
    if not mime:
        raise ValueError(f'Unsupported image type: {path.suffix}')
    data = path.read_bytes()
    if len(data) > 8 * 1024 * 1024:
        raise ValueError(f'{path.name}: image exceeds 8 MiB; crop/optimize first')
    if mime == 'image/svg+xml':
        svg = ET.fromstring(data)
        if svg.tag.split('}')[-1] != 'svg':
            raise ValueError('SVG root is not svg')
        for node in svg.iter():
            if node.tag.split('}')[-1] in {'script', 'foreignObject', 'style', 'image', 'use'}:
                raise ValueError('SVG must be a self-contained static diagram without scripts or external assets')
            for key, value in node.attrib.items():
                key = key.split('}')[-1].lower()
                if key.startswith('on') or key in {'href', 'src'} or 'url(' in value.lower():
                    raise ValueError('SVG contains an active or external reference')
    return f'data:{mime};base64,{base64.b64encode(data).decode("ascii")}'


def rich_text(value: str) -> str:
    """Escaped prose with restricted bold and inline math; never arbitrary HTML."""
    pieces = re.split(r'(\\\(.*?\\\)|\*\*[^*\n]+\*\*)', value, flags=re.DOTALL)
    output = []
    for piece in pieces:
        if piece.startswith('\\(') and piece.endswith('\\)'):
            raw = esc(piece[2:-2])
            output.append(f'<span class="math-unit inline-math" contenteditable="false"><span class="equation-render" data-display="inline" data-raw="{raw}">{raw}</span><button class="edit-formula" aria-label="Edit inline formula">Edit</button></span>')
        elif piece.startswith('**') and piece.endswith('**'):
            output.append(f'<strong>{esc(piece[2:-2])}</strong>')
        else:
            output.append(esc(piece))
    return ''.join(output)


def explanation_html(value: str) -> str:
    """Keep authored paragraphs and simple bullet groups in one editable host."""
    output = []
    for group in value.split('\n\n'):
        lines = group.split('\n')
        if lines and all(line.startswith('- ') for line in lines):
            output.append('<ul>' + ''.join(f'<li>{rich_text(line[2:])}</li>' for line in lines) + '</ul>')
        else:
            output.append(f'<p>{rich_text(group)}</p>')
    return ''.join(output)


def field_attr(pointer: str | None) -> str:
    return f' data-field="{esc(pointer)}"' if pointer else ''


def paragraph(value: str, css='', field=None) -> str:
    # Browsers may insert block children on Enter. A div keeps them valid and
    # editable after serialization and reparsing, unlike an editable p host.
    classes = 'editable-text' + (f' {css}' if css else '')
    return f'<div class="{classes}"{EDIT}{field_attr(field)}>{rich_text(value)}</div>'


def render_block(block: dict, content_dir: Path, config: dict, pointer='') -> str:
    kind = block['type']
    if kind == 'figure' and (config['visuals'] == 'off' or (config['visuals'] == 'slide_only' and block['origin'] != 'slide') or (block['origin'] == 'web' and not config['allow_web_visuals'])):
        return ''
    category = block.get('category', {'process': 'process', 'worked': 'formula', 'formula': 'formula'}.get(kind, 'definition'))
    label = {'concept': category, 'worked': 'Worked example', 'comparison': 'Compare & distinguish', 'review': 'Section takeaway', 'details': 'Further explanation'}.get(kind, kind)
    if block.get('learn_only'):
        label = 'Further explanation'
    classes = f'block {category}' + (' compact' if block.get('compact') and kind in {'concept', 'prose'} else '') + (' takeaway' if kind == 'review' else '')
    if block.get('learn_only'):
        # Reuse the reader's explanation visibility, search and export behavior.
        # Bullet lists need the same author-controlled distinction as prose bodies.
        classes += ' explanation'
    out = [f'<article class="{classes}" data-type="{kind}" data-block-id="{esc(block.get("id", ""))}"><div class="label">{esc(label)}</div><h3{EDIT}{field_attr(pointer + "/title")}>{esc(block["title"])}</h3>']
    if block.get('summary'):
        out.append(paragraph(block['summary'], 'lead', pointer + '/summary'))
    if kind == 'formula':
        out.append(f'<div class="math-unit"><div class="equation-render" data-raw="{esc(block["latex"])}"{field_attr(pointer + "/latex")}>{esc(block["latex"])}</div><button class="edit-formula">Edit formula</button></div>')
    if kind == 'comparison':
        out.append('<div class="table-scroll" tabindex="0" role="region" aria-label="Comparison table"><table><thead><tr>')
        out.extend(f'<th scope="col"{EDIT}{field_attr(pointer + "/headers/" + str(ci))}>{rich_text(cell)}</th>' for ci, cell in enumerate(block['headers']))
        out.append('</tr></thead><tbody>')
        for ri, row in enumerate(block['rows']):
            out.append('<tr>' + ''.join(f'<td{EDIT}{field_attr(pointer + f"/rows/{ri}/{ci}")}>{rich_text(cell)}</td>' for ci, cell in enumerate(row)) + '</tr>')
        out.append('</tbody></table></div>')
    if kind in {'process', 'worked', 'review'}:
        tag = 'ul' if kind == 'review' else 'ol'
        out.append(f'<{tag}>' + ''.join(f'<li{EDIT}{field_attr(pointer + "/steps/" + str(index))}>{rich_text(step)}</li>' for index, step in enumerate(block['steps'])) + f'</{tag}>')
    if kind == 'figure':
        uri = embedded_asset(block, content_dir)
        credit = block['credit'] + (f' · {block["source_url"]} · {block["license"]}' if block['origin'] == 'web' else '')
        out.append(f'<figure><button class="figure-open" aria-label="Enlarge figure: {esc(block["alt"])}"><img src="{uri}" alt="{esc(block["alt"])}"></button><figcaption{EDIT}{field_attr(pointer + "/caption")}>{esc(block["caption"])}</figcaption><span class="credit">{esc(credit)}</span></figure>')
    if block.get('body'):
        paragraphs = explanation_html(block['body'])
        body = f'<div class="explanation-body"{EDIT}{field_attr(pointer + "/body")}>{paragraphs}</div>'
        out.append(f'<details class="explanation" open><summary>Read the explanation</summary>{body}</details>' if kind == 'details' else f'<div class="explanation">{body}</div>')
    if block.get('source') and config['source_labels'] == 'minimal':
        out.append(f'<details class="provenance"><summary>Source note</summary>{esc(block["source"])}</details>')
    out.append('</article>')
    return ''.join(out)


def render_course(course: dict, content_dir: Path, config: dict) -> str:
    validate_course(course)
    course = prepare_course(course)
    course['title'] = config['course_title'] or course['title']
    validate_course(course)
    title = course['title']
    nav, sections = [], []
    for number, section in enumerate(course['sections'], 1):
        pointer = f'sections/{number - 1}'
        ident = 'section-' + section['id']
        week = f'<small class="week-label">Week {section["week"]}</small>' if 'week' in section else ''
        nav.append(f'<a href="#{ident}"><span>{number:02}</span><span>{week}<span class="nav-title">{esc(section["title"])}</span></span></a>')
        blocks = ''.join(render_block(b, content_dir, config, pointer + f'/blocks/{bi}') for bi, b in enumerate(section['blocks']))
        if not blocks:
            raise ValueError(f'{ident}: no reading blocks remain under the chosen visual policy')
        intro = paragraph(section['intro'], 'section-intro', pointer + '/intro') if section.get('intro') else ''
        sections.append(f'<section class="section" id="{ident}">{week}<div class="section-heading"><span class="section-number">{number:02}</span><h2{EDIT}{field_attr(pointer + "/title")}>{esc(section["title"])}</h2></div>{intro}<div class="blocks">{blocks}</div></section>')
    accent = ACCENTS.get(config['theme_accent'], config['theme_accent'])
    values = {'TITLE': esc(title), 'SUBTITLE': esc(course['subtitle']), 'KICKER': 'SYNTHETIC DEMO / NOT COURSE MATERIAL' if course['synthetic'] else 'YOUR COURSE / YOUR READING SPACE',
              'META': f'<span>{len(sections)} sections</span><span>{esc(config["depth"].replace("_", " "))}</span><span>Editable edition</span>',
              'NAV': ''.join(nav), 'CONTENT': ''.join(sections), 'REVIEW_HIDDEN': '' if config['include_review_mode'] else 'hidden',
              'CSS': (ROOT / 'template/styles.css').read_text(encoding='utf-8-sig') + f'\n:root{{--accent:{accent}}}',
              'JS': (ROOT / 'template/app.js').read_text(encoding='utf-8-sig')}
    fields = ['title', 'subtitle'] + re.findall(r'data-field="([^"]+)"', values['CONTENT'])
    values['STATE'] = snapshot_json(course, fields, config)
    template = (ROOT / 'template/base.html').read_text(encoding='utf-8-sig')
    # A single substitution pass prevents authored {{...}} text becoming a template instruction.
    result = re.sub(r'\{\{([A-Z_]+)\}\}', lambda m: values[m[1]], template)
    from validate import validate_html
    errors = validate_html(result, expected_sections=len(sections))
    if errors:
        raise ValueError('Output validation failed: ' + '; '.join(errors))
    return result


def build(source: Path, output: Path | None = None, config_path: Path | None = None, overrides: dict | None = None) -> Path:
    config = load_config(config_path, overrides)
    course = json.loads(source.read_text(encoding='utf-8-sig'))
    result = render_course(course, source.parent, config)
    destination = output or ROOT / 'output' / config['output_filename']
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(result, encoding='utf-8')
    return destination


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--config', type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--set', action='append', default=[], metavar='KEY=TOML_VALUE', help='Task override, e.g. depth="cram"')
    args = parser.parse_args()
    try:
        overrides = {}
        for setting in args.set:
            overrides.update(tomllib.loads(setting))
        destination = build(args.source, args.output, args.config, overrides)
        print(f'Built {destination.resolve()} ({destination.stat().st_size:,} bytes)')
        return 0
    except (ValueError, OSError, ET.ParseError) as error:
        print(f'Build failed: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
