"""Validate generated or browser-exported Study Suite HTML without dependencies."""
import argparse
import base64
from html.parser import HTMLParser
from pathlib import Path

VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}
# These tags implicitly end a paragraph in an HTML browser. Merely balancing
# opening/closing tags misses the changed editing boundaries after reopening.
P_BREAKERS = {'address', 'article', 'aside', 'blockquote', 'details', 'div', 'dl', 'fieldset', 'figcaption', 'figure', 'footer', 'form', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'header', 'hgroup', 'hr', 'main', 'menu', 'nav', 'ol', 'p', 'pre', 'section', 'table', 'ul'}


class Inspector(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids, self.anchors, self.errors, self.stack = set(), [], [], []
        self.sections = 0

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag in P_BREAKERS and 'p' in self.stack:
            self.errors.append(f'Invalid paragraph nesting: {tag} inside p; browser reopening changes the DOM')
        if tag not in VOID:
            self.stack.append(tag)
        ident = values.get('id')
        if ident:
            if ident in self.ids:
                self.errors.append(f'Duplicate id: {ident}')
            self.ids.add(ident)
        if tag == 'section' and 'section' in values.get('class', '').split():
            self.sections += 1
        if tag == 'a' and values.get('href', '').startswith('#'):
            self.anchors.append(values['href'][1:])
        if tag == 'img':
            src = values.get('src', '')
            if not src.startswith('data:image/') or ';base64,' not in src:
                self.errors.append('Image is not embedded')
            else:
                try:
                    if not base64.b64decode(src.split(',', 1)[1], validate=True):
                        self.errors.append('Empty embedded image')
                except ValueError:
                    self.errors.append('Invalid base64 image')
            if not values.get('alt'):
                self.errors.append('Image is missing alt text')
        if tag in {'script', 'link'} and (values.get('src') or values.get('href')):
            self.errors.append('Unexpected external script/stylesheet in exported HTML')
        if 'style' in values and not values['style'].strip():
            self.errors.append('Empty style attribute')
        if values.get('contenteditable') == 'true' and values.get('spellcheck') != 'false':
            self.errors.append('Editable element must disable spellcheck')

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack or self.stack[-1] != tag:
            self.errors.append(f'Mismatched closing tag: {tag}')
        else:
            self.stack.pop()


def validate_html(value, expected_sections=None):
    parser = Inspector()
    parser.feed(value)
    errors = parser.errors
    if parser.stack:
        errors.append('Unclosed tags: ' + ', '.join(parser.stack))
    errors.extend(f'Missing anchor target: {a}' for a in parser.anchors if a not in parser.ids)
    for ident in ('suite-styles', 'suite-app', 'sidebar', 'content', 'save', 'search', 'learn', 'review', 'formula-dialog', 'image-dialog'):
        if ident not in parser.ids:
            errors.append(f'Missing required element: {ident}')
    if not parser.sections:
        errors.append('No reading sections')
    if expected_sections is not None and parser.sections != expected_sections:
        errors.append('Rendered section count does not match selection')
    if not value.lower().startswith('<!doctype html>'):
        errors.append('Missing HTML doctype')
    return errors


if __name__ == '__main__':
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('html', type=Path)
    args = cli.parse_args()
    issues = validate_html(args.html.read_text(encoding='utf-8-sig'))
    print('\n'.join(issues) if issues else 'PASS: structure, IDs, anchors, inline assets, and editable markup')
    raise SystemExit(bool(issues))
