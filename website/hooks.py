"""Keep language links on the same page, including in the local preview."""

def on_page_context(context, page, config, nav):
    depth = len([part for part in page.url.split('/') if part])
    root = '../' * depth
    if config.theme['language'] == 'ru':
        root += '../'
    public = config.extra['language_root']
    config.extra['alternate'] = [
        {'name': 'English', 'lang': 'en', 'link': public + page.url,
         'local_link': root + page.url or './'},
        {'name': 'Русский', 'lang': 'ru', 'link': public + 'ru/' + page.url,
         'local_link': root + 'ru/' + page.url},
    ]
    return context
