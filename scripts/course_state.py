"""Portable course snapshots, stable identities and conflict-aware edit merging."""
from __future__ import annotations

import copy
import hashlib
import json
import re
from html.parser import HTMLParser

SLUG = re.compile(r'[a-z][a-z0-9-]*')


def prepare_course(course: dict) -> dict:
    """Materialize IDs once and sort numbered weeks, retaining within-week order."""
    result = copy.deepcopy(course)
    result.setdefault('course_id', 'course-' + hashlib.sha256(result['title'].encode()).hexdigest()[:20])
    for section in result['sections']:
        for index, block in enumerate(section['blocks'], 1):
            block.setdefault('id', f'block-{index:03}')
    result['sections'].sort(key=lambda section: section.get('week', 0))
    result['included_section_ids'] = [section['id'] for section in result['sections']]
    return result


def validate_metadata(course: dict) -> None:
    if 'course_id' in course and (not isinstance(course['course_id'], str) or not SLUG.fullmatch(course['course_id'])):
        raise ValueError('course_id must be a stable lowercase slug')
    for section in course['sections']:
        if 'week' in section and (type(section['week']) is not int or section['week'] < 1):
            raise ValueError('Section week must be a positive integer')
        identifiers = set()
        for block in section['blocks']:
            if 'id' in block:
                ident = block['id']
                if not isinstance(ident, str) or not SLUG.fullmatch(ident) or ident in identifiers:
                    raise ValueError(f'Invalid or duplicate block ID in {section["id"]}: {ident!r}')
                identifiers.add(ident)
    sources = course.get('sources', [])
    if not isinstance(sources, list):
        raise ValueError('sources must be a list')
    paths = set()
    for source in sources:
        if not isinstance(source, dict):
            raise ValueError('Each source must be an object')
        path, digest = source.get('path'), source.get('sha256')
        if not isinstance(path, str) or not path or path in paths or '\\' in path or ':' in path or path.startswith('/') or any(part in {'', '.', '..'} for part in path.split('/')):
            raise ValueError(f'Invalid or duplicate relative source path: {path!r}')
        if not isinstance(digest, str) or not re.fullmatch(r'[0-9a-f]{64}', digest):
            raise ValueError(f'{path}: sha256 must contain 64 lowercase hex digits')
        if type(source.get('week')) is not int or source['week'] < 1:
            raise ValueError(f'{path}: source week must be a positive integer')
        paths.add(path)


def editable_fields(course: dict):
    """Yield DOM pointers and stable identities with references into the JSON."""
    for field in ('title', 'subtitle'):
        yield field, field, course, field
    for si, section in enumerate(course['sections']):
        for field in ('title', 'intro'):
            if field in section:
                yield f'sections/{si}/{field}', f'{section["id"]}/{field}', section, field
        for bi, block in enumerate(section['blocks']):
            pointer = f'sections/{si}/blocks/{bi}'
            stable = f'{section["id"]}/{block["id"]}'
            for field in ('title', 'summary', 'body', 'latex', 'caption'):
                if field in block:
                    yield f'{pointer}/{field}', f'{stable}/{field}', block, field
            for field in ('steps', 'headers'):
                for index in range(len(block.get(field, []))):
                    yield f'{pointer}/{field}/{index}', f'{stable}/{field}/{index}', block[field], index
            for ri, row in enumerate(block.get('rows', [])):
                for ci in range(len(row)):
                    yield f'{pointer}/rows/{ri}/{ci}', f'{stable}/rows/{ri}/{ci}', row, ci


def snapshot_json(course: dict, rendered_fields: list[str], config: dict) -> str:
    state = {'version': 1, 'baseline': course, 'edits': {}, 'rendered_fields': rendered_fields, 'config': config}
    # JSON is raw text inside a script element, not HTML-escaped markup.
    return json.dumps(state, ensure_ascii=False).replace('<', '\\u003c')


class SnapshotParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.active = False
        self.parts = []
        self.count = 0

    def handle_starttag(self, tag, attrs):
        if tag == 'script' and dict(attrs).get('id') == 'suite-state':
            self.count += 1
            self.active = True

    def handle_endtag(self, tag):
        if tag == 'script':
            self.active = False

    def handle_data(self, data):
        if self.active:
            self.parts.append(data)


def read_snapshot(value: str) -> dict:
    parser = SnapshotParser()
    parser.feed(value)
    if parser.count != 1:
        raise ValueError('Expected one update snapshot. Legacy HTML needs one-time manual reconciliation; existing files were not changed.')
    state = json.loads(''.join(parser.parts))
    if not isinstance(state, dict) or state.get('version') != 1 or not isinstance(state.get('baseline'), dict) or not isinstance(state.get('edits'), dict):
        raise ValueError('Unsupported or malformed update snapshot')
    if state.get('capture_error'):
        raise ValueError('The saved HTML reports incomplete edit capture. Reconcile its visible edits manually before updating.')
    return state


def reconcile_edits(current: dict, state: dict) -> tuple[dict, int]:
    """Three-way field merge: stop if authored and browser edits disagree."""
    from build import validate_course

    baseline = state['baseline']
    validate_course(baseline)
    validate_course(current)
    baseline = prepare_course(baseline)
    merged = prepare_course(current)
    if baseline['course_id'] != merged['course_id']:
        raise ValueError('Course identity differs from the saved HTML')
    original = {p: (stable, obj[key]) for p, stable, obj, key in editable_fields(baseline)}
    destinations = {stable: (obj, key) for _, stable, obj, key in editable_fields(merged)}
    conflicts, count = [], 0
    for pointer, edited in state['edits'].items():
        if pointer not in original or not isinstance(edited, str):
            raise ValueError(f'Unrecognized edit field: {pointer}')
        stable, previous = original[pointer]
        if edited == previous:
            continue
        target = destinations.get(stable)
        if target is None:
            conflicts.append(stable)
            continue
        obj, key = target
        if obj[key] not in (previous, edited):
            conflicts.append(stable)
        else:
            obj[key] = edited
            count += 1
    if conflicts:
        raise ValueError('Conflicting browser/source edits; resolve these fields before updating: ' + ', '.join(conflicts))
    validate_course(merged)
    return merged, count
