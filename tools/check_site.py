#!/usr/bin/env python3
"""Check local site links, both languages and read-only Swagger without a network."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit,unquote
import json

ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'site'
class Page(HTMLParser):
    def __init__(self):super().__init__();self.links=[];self.ids=set();self.lang=None
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if 'id' in attrs:self.ids.add(attrs['id'])
        if tag=='html':self.lang=attrs.get('lang')
        for key in ('href','src'):
            if attrs.get(key):self.links.append(attrs[key])


def main():
    pages={}
    for path in SITE.rglob('*.html'):
        parser=Page();parser.feed(path.read_text());pages[path.resolve()]=parser
    errors=[];checked=set()
    for path,page in pages.items():
        for link in page.links:
            parts=urlsplit(link)
            if parts.scheme or parts.netloc:continue
            target=unquote(parts.path)
            if target.startswith('/instagram-edits-sdk/'):
                destination=SITE/target.removeprefix('/instagram-edits-sdk/')
            elif target.startswith('/'):
                errors.append(f'Unexpected root link {path.relative_to(SITE)}: {link}');continue
            else:destination=path.parent/target if target else path
            if destination.is_dir():destination=destination/'index.html'
            destination=destination.resolve();checked.add(destination)
            if not destination.is_relative_to(SITE.resolve()) or not destination.exists():
                errors.append(f'Broken link {path.relative_to(SITE)}: {link}')
            elif parts.fragment and destination in pages and unquote(parts.fragment) not in pages[destination].ids:
                errors.append(f'Broken anchor {path.relative_to(SITE)}: {link}')
    for prefix,lang in [('', 'en'),('ru/','ru')]:
        home=(SITE/prefix/'index.html').resolve()
        if pages[home].lang!=lang:errors.append('Wrong language: '+prefix)
        count=len(list((SITE/prefix/'methods').glob('*/index.html')))
        if count!=15:errors.append(f'Expected 15 method pages for {lang}, found {count}')
        spec=json.loads((SITE/prefix/'openapi.json').read_text())
        examples=spec['paths']['/graphql_www']['post']['requestBody']['content']['application/x-www-form-urlencoded']['examples']
        if len(examples)!=9:errors.append('Expected 9 Swagger examples')
        viewer=(SITE/prefix/'swagger-ui/viewer.js').read_text()
        if 'supportedSubmitMethods: []' not in viewer:errors.append('Swagger execution must stay disabled')
        if not (SITE/prefix/'search/search_index.json').exists():errors.append('Search index missing')
    if errors:raise SystemExit('\n'.join(errors[:40]))
    print(f'Checked {len(pages)} HTML pages and {len(checked)} local targets; EN/RU, method pages, search and Swagger present.')

if __name__=='__main__':main()
