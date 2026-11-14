#!/usr/bin/env python3
"""Seal the public demo page into one self-contained HTML file.

The authoring source is source/pages/public-demo.html (artifact id
`rqwst-public-demo`). Sealing applies the design system's output-artifact
sealed-output contract to it and writes the result to the repository root,
where it is served as index.html:

- every stylesheet is inlined verbatim, in load order, as
  <style data-sealed-from="<repository path>">;
- the foundation's eight font URLs become embedded woff2 data;
- the page icon and the two identity images become data: URIs;
- both scripts are inlined verbatim, as <script data-sealed-from="...">;
- the two embedded fonts' complete copyright notices and SIL OFL 1.1 texts are
  carried verbatim in a comment header straight after the charset declaration.

Nothing else changes. The sealed file loads nothing from outside itself: its
only other addresses are ordinary links (<a href>), the canonical link
(<link rel="canonical">) and the link-preview metadata (og: and twitter:
<meta> tags), none of which the page loads. Sealing the same source twice
gives the same bytes.

  python3 tools/seal.py                write index.html at the repository root
  python3 tools/seal.py --out FILE     write the sealed page to FILE instead

Standard library only.
"""
import base64, hashlib, html.parser, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = 'source/pages/public-demo.html'
ARTIFACT = 'rqwst-public-demo'
FONTS = 'source/_dsa-tokens/fonts'
ALLOWED_LINK = ('https://',)


def seal(root=ROOT):
    page_dir = os.path.dirname(PAGE)
    page = open(os.path.join(root, PAGE), encoding='utf-8').read()
    used = []

    def resolve(ref):
        rel = os.path.normpath(os.path.join(page_dir, ref)).replace(os.sep, '/')
        assert not rel.startswith('../'), ref + ' resolves outside the repository'
        return rel

    def read(rel):
        b = open(os.path.join(root, rel), 'rb').read()
        used.append((rel, len(b), hashlib.sha256(b).hexdigest()))
        return b

    def data_uri(rel, mime):
        return f'data:{mime};base64,' + base64.b64encode(read(rel)).decode()

    def css_inline(m):
        rel = resolve(m.group(1)); css = read(rel).decode('utf-8')
        if rel.endswith('/colors_and_type.css'):
            base = os.path.dirname(rel)
            css, n = re.subn(r"url\('(fonts/[^']+\.woff2)'\)",
                             lambda fm: f"url('{data_uri(base + '/' + fm.group(1), 'font/woff2')}')", css)
            assert n == 8, n
        assert 'url(' not in re.sub(r"url\('data:[^']+'\)", '', css), rel + ' keeps a url()'
        assert '@import' not in css, rel + ' imports a stylesheet'
        return f'<style data-sealed-from="{rel}">\n{css}\n</style>'

    out, n = re.subn(r'<link rel="stylesheet" href="([^"]+)">', css_inline, page); assert n == 10, n
    out, n = re.subn(r'<link rel="icon" type="image/svg\+xml" href="([^"]+)">',
                     lambda m: f'<link rel="icon" type="image/svg+xml" href="{data_uri(resolve(m.group(1)), "image/svg+xml")}">', out); assert n == 1, n
    out, n = re.subn(r'<img src="([^"]+\.svg)"',
                     lambda m: f'<img src="{data_uri(resolve(m.group(1)), "image/svg+xml")}"', out); assert n == 2, n
    out, n = re.subn(r'<script src="([^"]+)"></script>',
                     lambda m: f'<script data-sealed-from="{resolve(m.group(1))}">\n{read(resolve(m.group(1))).decode("utf-8")}\n</script>', out); assert n == 2, n

    def ofl(rel):
        t = read(rel).decode('utf-8'); assert '-->' not in t and '<!--' not in t, rel
        return t
    notice = ('\n<!--\nFONT NOTICES // the two fonts embedded below as data are under the SIL Open Font License 1.1.\n'
              'Their complete copyright notices and license texts follow, verbatim from design-system-ASK.\n\n'
              f'== Inter ({FONTS}/Inter-OFL.txt) ==\n\n' + ofl(f'{FONTS}/Inter-OFL.txt') +
              f'\n== JetBrains Mono ({FONTS}/JetBrainsMono-OFL.txt) ==\n\n' + ofl(f'{FONTS}/JetBrainsMono-OFL.txt') + '-->')
    out, n = re.subn(r'(<meta charset="UTF-8">)', lambda m: m.group(1) + notice, out, count=1); assert n == 1
    problems = external_loads(out)
    assert not problems, problems
    return out, used


class _Refs(html.parser.HTMLParser):
    """Every reference in the markup outside <style> and <script> bodies."""
    def __init__(self):
        super().__init__(convert_charrefs=True); self.found = []

    def handle_starttag(self, tag, attrs):
        self.found.append((tag, dict(attrs)))
    handle_startendtag = handle_starttag


def external_loads(doc):
    """What in a sealed page would load from outside the file. Empty means self-contained."""
    problems = []
    markup = re.sub(r'<(style|script)\b[^>]*>.*?</\1>', '', doc, flags=re.S)
    p = _Refs(); p.feed(markup)
    for tag, a in p.found:
        if tag in ('iframe', 'frame', 'embed', 'object', 'video', 'audio', 'source', 'track', 'base', 'portal'):
            problems.append(f'<{tag}> is not allowed')
        if tag == 'script' and 'src' in a:
            problems.append(f'<script src="{a["src"]}">')
        if tag == 'meta' and a.get('http-equiv', '').lower() == 'refresh':
            problems.append('<meta http-equiv="refresh">')
        for attr in ('src', 'srcset', 'poster', 'data', 'background', 'action', 'formaction', 'ping', 'xlink:href'):
            if attr in a and not a[attr].startswith('data:'):
                problems.append(f'<{tag} {attr}="{a[attr][:60]}">')
        if 'href' in a:
            h = a['href']; rel = a.get('rel', '').lower().split()
            if tag == 'a':
                if not (h.startswith('#') or h.startswith('mailto:') or h.startswith(ALLOWED_LINK)):
                    problems.append(f'<a href="{h[:60]}">: a link must be a fragment, mailto: or https:')
            elif tag == 'link' and rel == ['canonical']:
                if not h.startswith(ALLOWED_LINK):
                    problems.append(f'<link rel="canonical" href="{h[:60]}">: must be https:')
            elif not h.startswith('data:'):
                problems.append(f'<{tag} rel="{a.get("rel", "")}" href="{h[:60]}">: loads from outside the file')
        if 'style' in a and re.search(r'url\((?!\s*[\'"]?data:)', a['style']):
            problems.append(f'<{tag} style> loads a url()')
    for kind, body in re.findall(r'<(style|script)\b[^>]*>(.*?)</\1>', doc, flags=re.S):
        if kind == 'style':
            if re.search(r'url\((?!\s*[\'"]?data:)', body):
                problems.append('a <style> block loads a url() that is not data:')
            if '@import' in body:
                problems.append('a <style> block uses @import')
    return problems


if __name__ == '__main__':
    args = sys.argv[1:]
    target = os.path.join(ROOT, 'index.html')
    if args[:1] == ['--out'] and len(args) == 2:
        target = args[1]
    elif args:
        sys.exit(__doc__)
    doc, used = seal()
    with open(target, 'w', encoding='utf-8', newline='') as f:
        f.write(doc)
    b = open(target, 'rb').read()
    print(json.dumps({'page': PAGE, 'artifact': ARTIFACT, 'out': os.path.relpath(target, ROOT) if target.startswith(ROOT) else os.path.basename(target),
                      'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest(), 'inlined': used}, indent=1))
