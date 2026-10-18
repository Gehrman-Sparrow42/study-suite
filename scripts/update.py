"""Scan new course sources, reconcile saved browser edits, and append weekly content.

Codex authors the new content. This tool does not summarize PDFs or call an API.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path

from build import load_config, render_course, validate_course
from course_state import prepare_course, read_snapshot, reconcile_edits

MATERIAL_TYPES = {'.pdf', '.pptx', '.docx', '.txt', '.md'}


def read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding='utf-8-sig'))
    if not isinstance(value, dict):
        raise ValueError(f'{path.name}: expected a JSON object')
    return value


def digest(path: Path) -> str:
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def source_path(root: Path, relative: str) -> Path:
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError(f'Source escapes the selected input directory: {relative}')
    return path


def scan_sources(course: dict, root: Path) -> dict:
    validate_course(course)
    if not root.is_dir():
        raise ValueError('Input directory does not exist')
    recorded = {item['path']: item for item in course.get('sources', [])}
    known_hashes = {}
    for item in recorded.values():
        known_hashes.setdefault(item['sha256'], []).append(item['path'])
    report = {key: [] for key in ('new', 'changed', 'unchanged', 'missing', 'duplicates')}
    seen = set()
    for path in sorted(root.rglob('*')):
        if not path.is_file() or path.suffix.lower() not in MATERIAL_TYPES:
            continue
        relative = path.relative_to(root).as_posix()
        resolved = source_path(root, relative)
        sha = digest(resolved)
        item = {'path': relative, 'sha256': sha}
        seen.add(relative)
        if relative in recorded:
            key = 'unchanged' if sha == recorded[relative]['sha256'] else 'changed'
            report[key].append(item)
        elif sha in known_hashes:
            report['duplicates'].append({**item, 'matches': known_hashes[sha]})
        else:
            report['new'].append(item)
    report['missing'] = [item for path, item in recorded.items() if path not in seen]
    return report


def publish_new(path: Path, content: str) -> None:
    """Publish a complete new file without ever overwriting an existing edition."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent, suffix='.tmp', delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(content)
        # Both paths are on the same filesystem. link fails if destination exists.
        os.link(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def apply_update(source: Path, delta_path: Path, input_root: Path, output_course: Path,
                 output_html: Path, edited_html: Path | None = None,
                 config_path: Path | None = None) -> dict:
    for path in (output_course, output_html):
        if path.exists():
            raise ValueError(f'Output already exists; choose a new revision filename: {path}')
    if output_course.resolve() == output_html.resolve():
        raise ValueError('Course and HTML output paths must differ')
    if source.parent.resolve() != delta_path.parent.resolve() or source.parent.resolve() != output_course.parent.resolve():
        raise ValueError('Keep course JSON, weekly delta and new course JSON in the same authoring directory so asset paths remain valid')
    current = read_json(source)
    validate_course(current)
    current = prepare_course(current)
    changed = scan_sources(current, input_root)['changed']
    if changed:
        raise ValueError('Previously processed sources changed; reconcile their existing sections first: ' + ', '.join(item['path'] for item in changed))
    state = read_snapshot(edited_html.read_text(encoding='utf-8-sig')) if edited_html else None
    config = load_config(config_path, None if config_path or not state else state.get('config', {}))
    current['title'] = config['course_title'] or current['title']
    preserved = 0
    if state:
        current, preserved = reconcile_edits(current, state)
    delta = read_json(delta_path)
    if delta.get('schema_version') != 3 or delta.get('course_id') != current['course_id']:
        raise ValueError('Weekly delta must have schema_version=3 and the same course_id')
    additions, sources = delta.get('sections'), delta.get('sources')
    if not isinstance(additions, list) or not additions or not isinstance(sources, list) or not sources:
        raise ValueError('Weekly delta requires nonempty sections and sources lists')
    merged = copy.deepcopy(current)
    merged['sections'].extend(additions)
    merged['sources'] = merged.get('sources', []) + sources
    merged['included_section_ids'] = [section.get('id') for section in merged['sections'] if isinstance(section, dict)]
    validate_course(merged)
    # Validate all new file identities before recording them as processed.
    known_paths = {item['path'] for item in current.get('sources', [])}
    known_hashes = {item['sha256'] for item in current.get('sources', [])}
    new_paths = {item['path'] for item in sources}
    if len({item['sha256'] for item in sources}) != len(sources):
        raise ValueError('The new source list contains duplicate file contents')
    for item in sources:
        if item['path'] in known_paths or item['sha256'] in known_hashes:
            raise ValueError(f'Source already processed (including renamed copies): {item["path"]}')
        if digest(source_path(input_root, item['path'])) != item['sha256']:
            raise ValueError(f'Source changed since authoring; review it before updating: {item["path"]}')
    used_sources = set()
    for section in additions:
        if type(section.get('week')) is not int or section['week'] < 1:
            raise ValueError('Every added section needs a positive week number')
        references = section.get('source_files')
        if not isinstance(references, list) or not references or not all(isinstance(item, str) and item in new_paths for item in references):
            raise ValueError('Every added section needs source_files referencing the new source records')
        if any(next(item['week'] for item in sources if item['path'] == path) != section['week'] for path in references):
            raise ValueError('Section week must match its source records')
        used_sources.update(references)
    if used_sources != new_paths:
        raise ValueError('Each newly processed source must be referenced by an added section')
    merged = prepare_course(merged)
    # Browser title edits take precedence over the old configured title.
    config['course_title'] = ''
    value = render_course(merged, source.parent, config)
    publish_new(output_course, json.dumps(merged, ensure_ascii=False, indent=2) + '\n')
    publish_new(output_html, value)
    return {'course': str(output_course.resolve()), 'html': str(output_html.resolve()),
            'added_sections': len(additions), 'preserved_edit_fields': preserved,
            'processed_sources': len(sources)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    scan = commands.add_parser('scan', help='Report new, changed, duplicate and missing sources')
    scan.add_argument('course', type=Path)
    scan.add_argument('--input', required=True, type=Path)
    apply = commands.add_parser('apply', help='Add authored weekly content to a new edition')
    apply.add_argument('course', type=Path)
    apply.add_argument('delta', type=Path)
    apply.add_argument('--input', required=True, type=Path)
    apply.add_argument('--edited-html', type=Path)
    apply.add_argument('--config', type=Path)
    apply.add_argument('--output-course', required=True, type=Path)
    apply.add_argument('--output-html', required=True, type=Path)
    args = parser.parse_args()
    try:
        if args.command == 'scan':
            report = scan_sources(read_json(args.course), args.input)
        else:
            report = apply_update(args.course, args.delta, args.input, args.output_course,
                                  args.output_html, args.edited_html, args.config)
        print(json.dumps(report, ensure_ascii=True, indent=2))
        return 0
    except (ValueError, OSError) as error:
        print(f'Update stopped: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
