import sys
def to_preview(t, depth):
    up = '../' * depth
    t = t.replace('    <meta name="viewport" content="width=device-width, initial-scale=1">\n', '    <meta name="robots" content="noindex">\n    <meta name="viewport" content="width=device-width, initial-scale=1">\n', 1)
    t = t.replace(f'<link rel="stylesheet" href="{up}css/styles.css">', f'<link rel="stylesheet" href="../{up}css/styles.css">', 1)
    t = t.replace(f'<link rel="stylesheet" href="{up}assets/css/site.css">', f'<link rel="stylesheet" href="{up}preview.css">', 1)
    t = t.replace('    <a class="skip-link" href="#main">Skip to content</a>\n', '    <a class="skip-link" href="#main">Skip to content</a>\n    <p class="preview-banner" role="status">PREVIEW, not the live site</p>\n', 1)
    t = t.replace('<a href="/guide/WyoVote-Users-Guide-v1.1.pdf">', '<a href="/preview/guide/WyoVote-Users-Guide-v1.1.pdf">')
    return t
if __name__ == '__main__':
    import os, glob
    B = '/workspace/officials-archive/base'; bad = 0
    for f in glob.glob(f'{B}/officials/2025/*.html'):
        rel = os.path.relpath(f, B)
        if to_preview(open(f).read(), 2) != open(f'{B}/preview/{rel}').read(): bad += 1; print('diff', rel)
    f = 'archive/officials.html'
    if to_preview(open(f'{B}/{f}').read(), 1) != open(f'{B}/preview/{f}').read(): bad += 1; print('diff', f)
    print('preview transform mismatches:', bad)
