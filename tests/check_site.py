from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
import sys

ROOT = Path(__file__).resolve().parents[1]
ERRORS = []

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs = []
        self.ids = set()
        self.sponsored_missing = []
        self.rows_without_official = []
        self.in_thead = False
        self.current_row = None
        self.row_number = 0
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'thead':
            self.in_thead = True
        if tag == 'tr' and not self.in_thead:
            self.current_row = False
            self.row_number += 1
        if attrs.get('id'):
            self.ids.add(attrs['id'])
        href = attrs.get('href')
        if href:
            self.hrefs.append(href)
            if 'link.amazon/' in href and 'sponsored' not in attrs.get('rel', '').split():
                self.sponsored_missing.append(href)
            if self.current_row is not None and href.startswith(('https://affiliate-program.amazon.com/', 'https://www.ftc.gov/', 'https://support.google.com/')):
                self.current_row = True
    def handle_endtag(self, tag):
        if tag == 'tr' and self.current_row is not None:
            if not self.current_row:
                self.rows_without_official.append(self.row_number)
            self.current_row = None
        if tag == 'thead':
            self.in_thead = False

html_files = sorted([ROOT / 'index.html', * (ROOT / 'pages').glob('*.html')])
for file in html_files:
    rel = file.relative_to(ROOT)
    parser = Links()
    text = file.read_text(encoding='utf-8')
    parser.feed(text)
    if 'As an Amazon Associate I earn from qualifying purchases.' not in text:
        ERRORS.append(f'{rel}: missing visible Associates disclosure')
    if 'class="footer"' not in text or 'class="disclosure"' not in text:
        ERRORS.append(f'{rel}: missing disclosure strip or footer')
    for href in parser.hrefs:
        parts = urlsplit(href)
        if parts.scheme or parts.netloc or href.startswith(('mailto:', 'tel:', 'data:')):
            continue
        target = (file.parent / parts.path).resolve() if parts.path else file.resolve()
        if not target.exists():
            ERRORS.append(f'{rel}: broken local link {href}')
            continue
        if parts.fragment and target.suffix.lower() in ('.html', '.htm'):
            target_parser = Links()
            target_parser.feed(target.read_text(encoding='utf-8'))
            if parts.fragment not in target_parser.ids:
                ERRORS.append(f'{rel}: missing anchor {href}')
    for href in parser.sponsored_missing:
        ERRORS.append(f'{rel}: Amazon outbound URL missing rel sponsored: {href}')
    if parser.rows_without_official:
        ERRORS.append(f'{rel}: table rows lack an official-source link: {parser.rows_without_official}')

for path in ['sitemap.xml', 'feed.xml', 'robots.txt']:
    if not (ROOT / path).is_file():
        ERRORS.append(f'missing {path}')

if ERRORS:
    print('\n'.join('ERROR: ' + e for e in ERRORS))
    sys.exit(1)
print(f'OK: checked {len(html_files)} HTML pages, local links, anchors, disclosure placement, and sponsored outbound URLs.')
