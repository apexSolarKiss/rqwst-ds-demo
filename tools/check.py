#!/usr/bin/env python3
"""Check this repository before a release.

  python3 tools/check.py                   the checks that need nothing outside this repository
  python3 tools/check.py --donor DIR       also check every vendored file against its donor commit in a
                                           design-system-ASK clone at DIR, and run that commit's role-conformance
                                           check on index.html with the RQWST presentation assignment
                                           (needs Node 22 or later and Google Chrome)
  python3 tools/check.py --denylist FILE   also scan the tree for the terms listed in FILE, a list kept outside
                                           this repository (or name it in $RQWST_CHECK_DENYLIST)

The options combine. A denylist file holds one term per line, matched without regard to case; a line
starting "allow:" names an exact passage that is content and is set aside before matching; blank lines
and lines starting "#" are ignored. A hit is reported by file, line and the term's number (the five
generic patterns first, then the denylist's terms in order), never by the term itself. Line numbers
are the file's own: in index.html, the parts set aside before matching keep their line breaks.

What it checks:

  vendor     every file VENDOR.md lists is present, has the listed bytes, SHA-256 and git blob, and no
             other file sits in the vendored folders; with --donor, each listed blob is the donor commit's
  seal       sealing source/pages/public-demo.html again reproduces index.html byte for byte, and each
             sealed block is its source file verbatim
  delivery   index.html loads nothing from outside itself: every stylesheet, script, image, icon and font
             is inlined; its only other addresses are ordinary links, the canonical link and its link-preview
             metadata (og: and twitter:), none of which the page loads
  public     no absolute local path (a home or temporary folder) and no file: URL appears anywhere in the
             tree, nor, with --denylist, any listed term; no rqwst.com email address appears other than
             RQWST's public contact, hello@rqwst.com, and no rqwst.com URL other than its three public
             pages (PUBLIC_URLS below); the vendored design-system bytes are verified by identity instead
  artwork    the repository artwork draws RQWST's own identity paths, and the PNGs are the banner's exports
  assignment with --donor: the design system's role-conformance check passes on index.html, opened as a
             file, in light and dark, at 1440px and at 375px on a phone, under the assignment's declaration

Exit 0: every check ran and passed. 1: a check failed. 2: every check that ran passed, but the donor
checks did not run (no --donor). Running without a denylist is reported and does not change the exit
code. Standard library only.
"""
import base64, hashlib, html, importlib.util, json, os, re, shutil, struct, subprocess, sys, tempfile

sys.dont_write_bytecode = True   # importing tools/seal.py must leave no cache file in the tree

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VENDORED_DIRS = ('source/_dsa-tokens', 'source/_dsa-surface', 'licenses/design-system-ASK')
CHECKER = ('tools/check-role-conformance.mjs', 'tools/role-conformance.js')

# Absolute local paths and file: URLs, matched without regard to case. Each entry is split so that this
# file does not match itself. Other terms come from a denylist kept outside the repository (--denylist).
GENERIC = ['/Us' 'ers/', '/ho' 'me/', '/pri' 'vate/', '/t' 'mp/', 'file' '://']

# RQWST's public contact and its three public pages are the only rqwst.com email address and URLs the
# tree may carry, at rqwst.com or any subdomain, plainly written, %-encoded or as HTML entities. Any other
# is reported by file and line only, never by the address or URL.
PUBLIC_CONTACT = 'hello@rqwst.com'
PUBLIC_URLS = {'https://rqwst.com/', 'https://rqwst.com/apply', 'https://rqwst.com/terms'}
RQWST_ADDRESS = re.compile(r"(?<![\w.%+!#$&'*/=?^`{|}~-])[\w.%+-]+(?:@|%40)(?:[A-Za-z0-9-]+\.)*rqwst\.com\b", re.I)
RQWST_URL = re.compile(r"https?://(?:[A-Za-z0-9-]+\.)*rqwst\.com\b[^\s\"'<>()]*", re.I)


def load_denylist(path):
    terms, allowed = [], []
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n')
            if not line.strip() or line.lstrip().startswith('#'):
                continue
            (allowed if line.startswith('allow:') else terms).append(line[6:] if line.startswith('allow:') else line.strip())
    return terms, allowed


def rd(rel, mode='r'):
    with open(os.path.join(ROOT, rel), mode, **({} if 'b' in mode else {'encoding': 'utf-8'})) as f:
        return f.read()


def blob_id(b):
    return hashlib.sha1(b'blob %d\0' % len(b) + b).hexdigest()


def vendor_table():
    text = rd('VENDOR.md')
    donor = re.search(r'\*\*Donor:\*\* `apexSolarKiss/design-system-ASK` at commit `([0-9a-f]{40})`', text)
    rows = re.findall(r'^\| `([^`]+)` \| `([^`]+)` \| ([\d,]+) \| `([0-9a-f]{40})` \| `([0-9a-f]{64})` \|$', text, flags=re.M)
    return (donor.group(1) if donor else None), [(h, u, int(n.replace(',', '')), b, s) for h, u, n, b, s in rows]


def check_vendor(donor_dir, out):
    commit, rows = vendor_table()
    if not commit or not rows:
        return out('vendor', False, 'VENDOR.md names no donor commit or lists no file')
    bad = []
    for here, up, n, blob, sha in rows:
        p = os.path.join(ROOT, here)
        if not os.path.isfile(p):
            bad.append(f'{here}: missing'); continue
        b = open(p, 'rb').read()
        if len(b) != n: bad.append(f'{here}: {len(b)} bytes, VENDOR.md lists {n}')
        if hashlib.sha256(b).hexdigest() != sha: bad.append(f'{here}: SHA-256 differs from VENDOR.md')
        if blob_id(b) != blob: bad.append(f'{here}: git blob {blob_id(b)}, VENDOR.md lists {blob}')
    listed = {h for h, *_ in rows}
    for d in VENDORED_DIRS:
        for dp, _, fs in os.walk(os.path.join(ROOT, d)):
            for f in fs:
                rel = os.path.relpath(os.path.join(dp, f), ROOT).replace(os.sep, '/')
                if rel not in listed and f != '.DS_Store':
                    bad.append(f'{rel}: in a vendored folder but not listed in VENDOR.md')
    out('vendor', not bad, f'{len(rows)} files at {commit[:7]}' if not bad else '; '.join(bad))
    if donor_dir is None:
        return None
    bad = []
    for here, up, n, blob, sha in rows:
        spec = f'{commit}:{up}'
        if subprocess.run(['git', '-C', donor_dir, 'cat-file', '-e', spec], capture_output=True).returncode:
            bad.append(f'{up}: not in the donor commit'); continue
        got = subprocess.run(['git', '-C', donor_dir, 'rev-parse', spec], capture_output=True, text=True, check=True).stdout.strip()
        if got != blob: bad.append(f'{up}: donor blob {got}, VENDOR.md lists {blob}')
    out('vendor, donor', not bad, f'{len(rows)} files equal their blobs at {commit}' if not bad else '; '.join(bad))


def load_seal():
    spec = importlib.util.spec_from_file_location('rqwst_seal', os.path.join(ROOT, 'tools', 'seal.py'))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


SEALED = re.compile(r'<(style|script) data-sealed-from="([^"]+)">\n(.*?)\n</\1>', re.S)
FONT_URI = re.compile(r"url\('data:font/woff2;base64,([A-Za-z0-9+/=]+)'\)")


def verbatim_blocks(doc):
    """Each sealed block and whether it is its source file verbatim (the foundation with its font URLs restored)."""
    blocks = []
    for kind, src, body in SEALED.findall(doc):
        try:
            want = rd(src)
        except OSError:
            blocks.append((kind, src, False)); continue
        if src.endswith('/colors_and_type.css'):
            fonts_ok = all(base64.b64decode(u) == rd(os.path.dirname(src) + '/' + f, 'rb')
                           for u, f in zip(FONT_URI.findall(body), re.findall(r"url\('(fonts/[^']+\.woff2)'\)", want)))
            same = fonts_ok and FONT_URI.sub('U', body) == re.sub(r"url\('fonts/[^']+\.woff2'\)", 'U', want)
        else:
            same = body == want
        blocks.append((kind, src, same))
    return blocks


def check_seal(out):
    seal = load_seal()
    try:
        doc, _ = seal.seal(ROOT)
    except AssertionError as e:
        return out('seal', False, f'sealing fails: {e}')
    have = rd('index.html', 'rb')
    fresh = doc.encode('utf-8')
    out('seal', fresh == have, f'index.html {len(have)} B, sha256 {hashlib.sha256(have).hexdigest()}; a fresh seal is '
        + ('byte-identical' if fresh == have else f'{len(fresh)} B, sha256 {hashlib.sha256(fresh).hexdigest()}: run python3 tools/seal.py'))
    blocks = verbatim_blocks(have.decode('utf-8'))
    bad = [src for _, src, same in blocks if not same]
    out('seal, blocks', len(blocks) == 12 and not bad, f'{len(blocks)} sealed blocks, each its source verbatim' if not bad else 'not verbatim: ' + ', '.join(bad))


def check_delivery(out):
    seal = load_seal(); doc = rd('index.html')
    problems = seal.external_loads(doc)
    markup = re.sub(r'<(style|script)\b[^>]*>.*?</\1>', '', doc, flags=re.S)
    for m in re.finditer(r'\b(src|href|srcset|poster|data)\s*=\s*["\']([^"\']*)', markup):
        v = m.group(2)
        if v.startswith(('data:', '#', 'mailto:')):
            continue
        tag = markup[markup.rfind('<', 0, m.start()):m.start()]
        if v.startswith('https://') and m.group(1) == 'href' and (tag.startswith('<a ') or tag.startswith('<link rel="canonical"')):
            continue
        problems.append(f'{m.group(1)}="{v[:60]}"')
    problems += [f'names a source path: {p}' for p in sorted(set(re.findall(r'(?:href|src)="(?:\./)?source/[^"]*"', markup)))]
    out('delivery', not problems, 'no stylesheet, script, image, icon or font loads from outside the file' if not problems else '; '.join(sorted(set(problems))))


def blank(s):
    """The same text with every character but its line breaks turned to a space: what is set aside before
    matching keeps its length and its line breaks, so a hit's line is the file's own."""
    return re.sub(r'[^\n]', ' ', s)


def scan(text, where, found, terms, allowed):
    # A hit names the term by its number, never by its words or their context: a denylist holds words that
    # must not be copied anywhere, and that includes this report.
    low = text.lower()
    for a in allowed:
        low = low.replace(a.lower(), blank(a))
    for k, t in enumerate(terms, 1):
        n = low.count(t.lower())
        if n:
            line = low.count('\n', 0, low.index(t.lower())) + 1
            found.append(f'{where}, line {line}: term {k} x{n}')
    hits = set()
    for form in {text, html.unescape(text)}:
        for m in RQWST_ADDRESS.finditer(form):
            if m.group(0).replace('%40', '@').lower() != PUBLIC_CONTACT:
                hits.add((form.count('\n', 0, m.start()) + 1, f'an rqwst.com email address other than {PUBLIC_CONTACT}'))
        for m in RQWST_URL.finditer(form):
            if m.group(0).rstrip('.,;:') not in PUBLIC_URLS:
                hits.add((form.count('\n', 0, m.start()) + 1, 'an rqwst.com URL other than its public pages'))
    found.extend(f'{where}, line {line}: {what}' for line, what in sorted(hits))


def png_text(b):
    """The PNG's non-pixel chunks, as text: everything a reader could find in the file besides the image."""
    i, parts = 8, []
    while i < len(b):
        n = struct.unpack('>I', b[i:i + 4])[0]; kind = b[i + 4:i + 8]
        if kind not in (b'IDAT', b'IHDR', b'PLTE', b'IEND'):
            parts.append(kind.decode('latin-1') + ' ' + b[i + 8:i + 8 + n].decode('latin-1'))
        i += 12 + n
    return '\n'.join(parts)


def check_public(out, denylist):
    _, rows = vendor_table(); vendored = {h: s for h, _, _, _, s in rows}
    extra, allowed = load_denylist(denylist) if denylist else ([], [])
    terms = GENERIC + extra
    found, scanned = [], 0
    scan_ = lambda text, where: scan(text, where, found, terms, allowed)
    for dp, ds, fs in os.walk(ROOT):
        ds[:] = [d for d in ds if d != '.git']
        for f in fs:
            rel = os.path.relpath(os.path.join(dp, f), ROOT).replace(os.sep, '/')
            b = open(os.path.join(dp, f), 'rb').read()
            if rel in vendored and hashlib.sha256(b).hexdigest() == vendored[rel]:
                continue      # design-system bytes, verified by identity (vendor)
            scanned += 1
            if b[:8] == b'\x89PNG\r\n\x1a\n':
                scan_(png_text(b), rel); continue
            text = b.decode('utf-8', errors='replace')
            if rel == 'index.html':
                for kind, src, same in verbatim_blocks(text):
                    if same and src in vendored:
                        text = re.sub(r'<' + kind + r' data-sealed-from="' + re.escape(src) + r'">\n.*?\n</' + kind + '>',
                                      lambda m: blank(m.group(0)), text, count=1, flags=re.S)
                for ofl in ('source/_dsa-tokens/fonts/Inter-OFL.txt', 'source/_dsa-tokens/fonts/JetBrainsMono-OFL.txt'):
                    text = text.replace(rd(ofl), blank(rd(ofl)), 1)
                for mime, data in re.findall(r'data:([\w/+.-]+);base64,([A-Za-z0-9+/=]+)', text):
                    if mime != 'font/woff2':
                        scan_(base64.b64decode(data).decode('utf-8', errors='replace'), f'index.html ({mime} data)')
                text = re.sub(r'data:[\w/+.-]+;base64,[A-Za-z0-9+/=]+', 'data:', text)
            scan_(text, rel)
    what = f'{len(GENERIC)} generic patterns' + (f' and {len(extra)} denylist terms ({len(allowed)} allowed passages)' if denylist else '')
    out('public', not found, f'{scanned} files scanned for {what}; {len(vendored)} vendored files verified by identity' if not found else '; '.join(found[:12]) + (f' (+{len(found) - 12})' if len(found) > 12 else ''))


def check_artwork(out):
    bad = []
    paths = lambda rel: re.findall(r'<path [^>]*/>', rd(rel))
    for rel, part in (('rqwst-ds-demo-banner.svg', 'source/assets/rqwst-lockup.svg'), ('favicon.svg', 'source/assets/rqwst-plume.svg')):
        if paths(rel) != paths(part):
            bad.append(f'{rel} does not draw {part}\'s paths verbatim')
    stamp = hashlib.sha256(rd('rqwst-ds-demo-banner.svg', 'rb')).hexdigest()
    for rel, size in (('rqwst-ds-demo-banner.png', (2752, 1536)), ('og-image.png', (1200, 630))):
        b = rd(rel, 'rb')
        if b[:8] != b'\x89PNG\r\n\x1a\n':
            bad.append(f'{rel}: not a PNG'); continue
        if struct.unpack('>II', b[16:24]) != size:
            bad.append(f'{rel}: {struct.unpack(">II", b[16:24])}, expected {size}')
        if 'sRGB' not in png_text(b):
            bad.append(f'{rel}: declares no sRGB color space')
        if f'artwork-master-sha256\x00{stamp}' not in png_text(b):
            bad.append(f'{rel}: not stamped as an export of the current rqwst-ds-demo-banner.svg')
    out('artwork', not bad, 'banner and favicon draw the identity files\' own paths; both PNGs are stamped exports of the banner' if not bad else '; '.join(bad))


def check_assignment(donor_dir, out):
    commit, _ = vendor_table()
    page = rd('index.html'); decl = json.loads(rd('source/assets/rqwst-assignment.json'))
    root = re.search(r'<html\b[^>]*>', page).group(0)
    if f'data-surface-assignment="{decl["name"]}"' not in root or f'data-surface-field="{decl["field"]}"' not in root:
        return out('assignment', False, 'the page root does not declare the assignment the declaration file names')
    if not shutil.which('node'):
        return out('assignment', False, 'node is not on PATH')
    with tempfile.TemporaryDirectory() as tmp:
        os.mkdir(os.path.join(tmp, 'tools'))
        for rel in CHECKER:
            spec = f'{commit}:{rel}'
            data = subprocess.run(['git', '-C', donor_dir, 'cat-file', 'blob', spec], capture_output=True, check=True).stdout
            want = subprocess.run(['git', '-C', donor_dir, 'rev-parse', spec], capture_output=True, text=True, check=True).stdout.strip()
            if blob_id(data) != want:
                return out('assignment', False, f'{rel} at {commit[:7]}: read bytes are not the donor blob')
            open(os.path.join(tmp, rel), 'wb').write(data)
        url = 'file:' '//' + os.path.join(ROOT, 'index.html')
        for label, extra in (('1440', ['--width', '1440']), ('375 phone', ['--width', '375', '--height', '844', '--mobile'])):
            r = subprocess.run(['node', os.path.join(tmp, CHECKER[0]), '--url', url, '--scheme', 'both',
                                '--assignment', os.path.join(ROOT, 'source/assets/rqwst-assignment.json')] + extra, capture_output=True, text=True)
            try:
                rep = json.loads(r.stdout)
            except ValueError:
                return out(f'assignment, {label}', False, f'no report (exit {r.returncode}): {r.stderr.strip()[:200]}')
            runs = [(x['scheme'], x['status'], x.get('governed'), sorted({f['reason'] for f in x.get('findings', [])})) for x in rep.get('runs', [])]
            out(f'assignment, {label}', r.returncode == 0 and rep.get('pass') is True,
                f'role-conformance at {commit[:7]}: ' + '; '.join(f'{s} {st}, {g} governed' + (f', {f}' if f else '') for s, st, g, f in runs))


def main(argv):
    donor, denylist = None, os.environ.get('RQWST_CHECK_DENYLIST') or None
    args = list(argv)
    while args:
        if args[0] in ('--donor', '--denylist') and len(args) >= 2:
            if args[0] == '--donor': donor = os.path.abspath(args[1])
            else: denylist = os.path.abspath(args[1])
            args = args[2:]
        else:
            sys.exit(__doc__)
    if denylist and os.path.realpath(denylist).startswith(os.path.realpath(ROOT) + os.sep):
        sys.exit('the denylist must be kept outside this repository')
    if denylist and not os.path.isfile(denylist):
        sys.exit(f'no denylist at {denylist}')
    results = []

    def out(name, ok, detail):
        results.append(ok); print(f'{"PASS" if ok else "FAIL"}  {name}: {detail}')
    check_vendor(donor, out)
    check_seal(out)
    check_delivery(out)
    check_public(out, denylist)
    if not denylist:
        print('SKIP  public, denylist: no --denylist or RQWST_CHECK_DENYLIST')
    check_artwork(out)
    if donor:
        check_assignment(donor, out)
    else:
        print('SKIP  vendor, donor and assignment: no --donor')
    if not all(results):
        print('check: FAIL'); return 1
    print('check: PASS' if donor else 'check: PASS for the checks that ran; the donor checks did not run')
    return 0 if donor else 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
