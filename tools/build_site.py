#!/usr/bin/env python3
"""Stage bilingual documentation and build a local static site. Never publishes."""
import argparse
import html
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import yaml

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'website'
STAGE=ROOT/'.docs-build'
SITE=ROOT/'site'
REPO='https://github.com/lupikovoleg/instagram-edits-sdk'
PUBLIC='https://lupikovoleg.github.io/instagram-edits-sdk/'
VERSION=re.search(r'__version__ = "([^"]+)"', (ROOT/'src/edits_api/__init__.py').read_text()).group(1)


def write(path,content):
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(content)


def credit(lang):
    author='Олег Лупиков' if lang=='ru' else 'Oleg Lupikov'
    note='Независимый проект · Не связан с Meta' if lang=='ru' else 'Independent project · Not affiliated with Meta'
    return (f'<span class="author-credit">© 2026 <a href="{REPO}">{author}</a></span>'
            f'<span class="footer-meta"><a href="{REPO}/blob/main/LICENSE">MIT License</a> · {note} · SDK {VERSION}</span>')


def rewrite_links(text,source):
    def replace(match):
        target=match.group(1)
        if '://' in target or target.startswith('#') or target.startswith('mailto:'):return match.group(0)
        plain,sep,anchor=target.partition('#')
        if plain.startswith('swagger/'):
            return ']('+target.replace('swagger/','swagger-ui/',1)+')'
        real=(source.parent/plain).resolve()
        try:rel=real.relative_to(ROOT)
        except ValueError:return match.group(0)
        if rel.parts[0] in {'examples','src','.github','tools'}:
            suffix='#'+anchor if sep else ''
            return ']('+REPO+'/blob/main/'+rel.as_posix()+suffix+')'
        return match.group(0)
    return re.sub(r'\]\(([^)\s]+)\)',replace,text)


def generate_methods(root,ops,translations):
    lines=['# Operation catalog','','15 detailed contracts, 9 read operations exercised live. A larger catalog contains 88 Basel/Eddy name matches and 1663 shared APK entries.','',
           '[Evidence levels](verification.md) · [Download the full registry](downloads/operations.json)','','## Detailed contracts','','| Operation | Evidence | Purpose |','|---|---|---|']
    for op in ops:
        if 'variables' not in op:continue
        name=op['operation_name'];t=translations[name]
        assert set(t['variables'])==set(op['variables']),name
        state=op.get('live_semantic_status','static')
        label={'data':'Live · data returned','empty':'Live · empty result','unavailable':'Live · unavailable','static':'Static contract'}[state]
        lines.append(f"| [{name}](methods/{name}.md) | {label} | {t['description']} |")
        card=[f'# {name}','',f'<span class="evidence-pill evidence-{state}">{label}</span>','',t['description'],'',
              f"**Persisted query ID:** `{op['client_doc_id']}`  ",f"**Schema:** `{op['schema']}` · **Kind:** `{op['kind']}`",'']
        if state=='static':card+=['Not tested on the server. The contract was recovered from the APK; no live availability is promised.','']
        else:card += ['Exercised on one consenting account on 18 October 2026. **Observed result:** '+op['live_observation']+'.','[Verification scope](../verification.md).','']
        card+=['## Variables','','| Field | Contract |','|---|---|']
        for key,value in t['variables'].items():card.append('| `'+key+'` | '+value.replace('|','\\|')+' |')
        card+=['','## Response','',t['returns'],'','Raw wire names can have canonical prefixes and arguments. Use `QueryResult.get_data()` for logical paths.','']
        if op['kind']=='mutation':card+=['## Mutating operation','','This operation changes account state. It was not used in live tests. `execute()` rejects it unless `allow_mutation=True` is explicitly passed. Incomplete input fields must not be guessed.','']
        else:
            card+=['## Calling the operation','','```python',f'response = client.execute("{name}", variables)','payload = response.payload','```','','[Data fields and SDK wrappers](../data-reference.md) · [Authentication](../authentication.md)','']
        card+=['## Static sources','','These paths refer to the original research workspace. Decompiled Meta sources are not shipped with this project.','']+[f'- `{r}`' for r in op.get('source_references',[])]
        write(root/'methods'/f'{name}.md','\n'.join(card)+'\n')
    lines+=['','## Remaining Basel / Eddy entries','','A registry entry is not a confirmed working endpoint. Parameters and reachability can be unknown.','','| Operation | Kind | Persisted query ID | Evidence |','|---|---|---|---|']
    for op in ops:
        if op['edits_related']:lines.append(f"| `{op['operation_name']}` | {op['kind']} | `{op['client_doc_id']}` | {op['evidence_level']} |")
    write(root/'methods.md','\n'.join(lines)+'\n')


def config(lang,root,ops):
    ru=lang=='ru'
    labels=({'home':'Обзор','start':'Начало работы','quick':'Быстрый старт','auth':'Авторизация','sdk':'Использование SDK','retention':'Удержание','data':'Справочник данных','integration':'Интеграция','examples':'Примеры','api':'API и методы','catalog':'Каталог операций','http':'HTTP-контракт','swagger':'Swagger / OpenAPI','research':'Исследование','verification':'Проверки и источники','releasing':'Сопровождение'} if ru else
            {'home':'Overview','start':'Get started','quick':'Quickstart','auth':'Authentication','sdk':'Use the SDK','retention':'Retention','data':'Data reference','integration':'Integration','examples':'Examples','api':'API reference','catalog':'Operation catalog','http':'HTTP transport','swagger':'Swagger / OpenAPI','research':'Research','verification':'Evidence & verification','releasing':'Maintenance'})
    nav=[{labels['home']:'index.md'},{labels['start']:[{labels['quick']:'quickstart.md'},{labels['auth']:'authentication.md'}]},
         {labels['sdk']:[{labels['retention']:'retention.md'},{labels['data']:'data-reference.md'},{labels['integration']:'integration.md'},{labels['examples']:'examples.md'}]},
         {labels['api']:[{labels['catalog']:'methods.md'},{labels['http']:'http-api.md'},{labels['swagger']:'swagger.md'}]+[{o['operation_name']:'methods/'+o['operation_name']+'.md'} for o in ops if 'variables' in o]},
         {labels['research']:[{labels['verification']:'verification.md'},{labels['releasing']:'releasing.md'}]}]
    return {'site_name':'Instagram Edits SDK','site_description':'Unofficial Python SDK for Reel statistics, retention and audience insights.',
      'site_url':PUBLIC+('ru/' if ru else ''),'docs_dir':str(root),'site_dir':str(SITE/('ru' if ru else '')),
      'repo_url':REPO,'repo_name':'instagram-edits-sdk','edit_uri':'','use_directory_urls':True,
      'theme':{'name':'material','custom_dir':str(SOURCE/'overrides'),'language':lang,'font':False,'logo':'assets/logo.svg','favicon':'assets/logo.svg',
               'features':['navigation.tabs','navigation.sections','navigation.top','search.suggest','search.highlight','content.code.copy']},
      'plugins':[{'search':{'lang':[lang]}}],
      'markdown_extensions':['admonition','attr_list','md_in_html','tables','pymdownx.highlight','pymdownx.superfences',{'toc':{'permalink':True}}],
      'extra_css':['assets/site.css'],'nav':nav,'hooks':[str(SOURCE/'hooks.py')],
      'extra':{'language_root':PUBLIC,'alternate':[{'name':'English','link':PUBLIC,'lang':'en'},{'name':'Русский','link':PUBLIC+'ru/','lang':'ru'}]},
      'copyright':credit(lang),
      'validation':{'links':{'not_found':'warn','unrecognized_links':'warn','anchors':'warn'}},
      'not_in_nav':'swagger-ui/index.html\n'}


def stage():
    if STAGE.exists():shutil.rmtree(STAGE)
    STAGE.mkdir()
    ops=json.loads((ROOT/'src/edits_api/operations.json').read_text())
    translations=json.loads((SOURCE/'contracts.en.json').read_text())
    assert len(translations)==sum('variables' in o for o in ops)
    for lang in ('en','ru'):
        dest=STAGE/lang;dest.mkdir()
        paths=list((SOURCE/'en').rglob('*.md')) if lang=='en' else list((ROOT/'docs').glob('*.md'))+list((ROOT/'docs/methods').glob('*.md'))
        for source in paths:
            base=SOURCE/'en' if lang=='en' else ROOT/'docs'
            relative=source.relative_to(base)
            if lang=='en' and relative.parts[0]=='methods':continue
            content=rewrite_links(source.read_text(),source)
            if lang=='ru' and relative.parts[0]=='methods':
                op=next(o for o in ops if o['operation_name']==source.stem);state=op.get('live_semantic_status','static')
                label={'data':'На сервере · данные получены','empty':'На сервере · пустой результат','unavailable':'На сервере · недоступно','static':'Статический контракт'}[state]
                content=content.replace('\n\n',f'\n\n<span class="evidence-pill evidence-{state}">{label}</span>\n\n',1)
            write(dest/relative,content)
        if lang=='en':generate_methods(dest,ops,translations)
        else:
            for source in (SOURCE/'ru').glob('*.md'):write(dest/source.name,source.read_text())
        shutil.copytree(SOURCE/'assets',dest/'assets')
        shutil.copytree(ROOT/'docs/evidence',dest/'evidence')
        (dest/'downloads').mkdir();shutil.copyfile(ROOT/'src/edits_api/operations.json',dest/'downloads/operations.json')
        spec=json.loads((ROOT/'docs/openapi.json').read_text())
        if lang=='en':
            for name,t in translations.items():
                schema=spec['components']['schemas'].get(name+'Variables')
                if schema:
                    for key,value in t['variables'].items():schema['properties'][key]['description']=value
        write(dest/'openapi.json',json.dumps(spec,ensure_ascii=False,indent=2)+'\n')
        shutil.copytree(ROOT/'docs/swagger',dest/'swagger-ui')
        index=dest/'swagger-ui/index.html';markup=index.read_text()
        switch='../../swagger-ui/' if lang=='ru' else '../ru/swagger-ui/'
        nav=f'<nav style="max-width:1420px;margin:20px auto;padding:0 20px;font:15px Onest,sans-serif;display:flex;justify-content:space-between"><a href="../">← {"Документация" if lang=="ru" else "Documentation"}</a><a href="{switch}">{"English" if lang=="ru" else "Русский"}</a></nav>'
        markup=markup.replace('<body>','<body>'+nav).replace('</body>',f'<footer class="swagger-footer">{credit(lang)}</footer></body>')
        markup=markup.replace('</head>','''<link rel="stylesheet" href="../assets/site.css">
  <style>
    body{background:#fff;border-top:3px solid transparent;border-image:var(--ig-gradient) 1;font-family:Onest,sans-serif}
    a{color:#a81763}.notice{font-family:Onest,sans-serif;background:#fff5fa;border-color:#dd2a7b;border-radius:0 12px 12px 0}
    .query-example,.query-example select,.swagger-ui,.swagger-ui .info .title,.swagger-ui .info p,.swagger-ui .opblock .opblock-summary-description{font-family:Onest,sans-serif}
    .query-example select{border:1px solid #dedce1;border-radius:10px;background:#fff}
    .query-example pre{background:#17141c;border-radius:14px;font-family:PlexMono,monospace}
  </style></head>''')
        if lang=='ru':
            markup=markup.replace('lang="en"','lang="ru"').replace('Read-only research reference','Справочник · только просмотр').replace('Query example','Пример запроса')
            markup=markup.replace(
                'Choose an example under POST /graphql_www to inspect one of nine tested read queries.\n    Requests and authorization entry are disabled. All viewer assets are local; no CDN or telemetry.\n    Use the Python SDK in your backend. Null comments and empty Kits are recorded availability limits.',
                'Выберите один из девяти проверенных запросов чтения. Отправка запросов и ввод авторизации отключены. '
                'Ресурсы Swagger загружаются локально, без CDN и телеметрии. Для реальных запросов используйте Python SDK на своём сервере. '
                'В проверке анализ комментариев вернул null, а список Kits оказался пустым.')
            viewer=dest/'swagger-ui/viewer.js'
            script=viewer.read_text().replace('Decoded variables (serialize as a JSON string in the form):',
                'Переменные (передайте JSON-строкой в поле формы):').replace(
                'URL-encoded request body (authentication headers omitted):',
                'Тело запроса URL-encoded (заголовки авторизации не показаны):')
            viewer.write_text(script)
        index.write_text(markup)
        write(STAGE/(lang+'.yml'),yaml.safe_dump(config(lang,dest,ops),allow_unicode=True,sort_keys=False))


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--stage-only',action='store_true');args=parser.parse_args()
    stage()
    if args.stage_only:return
    for lang in ('en','ru'):
        subprocess.run([sys.executable,'-m','mkdocs','build','--strict','--config-file',str(STAGE/(lang+'.yml'))],cwd=ROOT,check=True)
    (SITE/'.nojekyll').touch()
    print('Bilingual site built in site/. Nothing was published.')


if __name__=='__main__':main()
