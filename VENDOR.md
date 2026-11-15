# Vendored files

The files under `source/_dsa-tokens/` and `source/_dsa-surface/` are copied unmodified from [design-system-ASK](https://github.com/apexSolarKiss/design-system-ASK). They are the design system's tokens, fonts, page shell, compact actions, panel material, text links, document register with its table overflow helper, and treatments. The authoring page, `source/pages/public-demo.html`, loads them as they are, and `tools/seal.py` carries them unchanged into the published `index.html`: the stylesheets and scripts inlined verbatim, the fonts as embedded data, and the two font licenses in a comment at its head.

**Do not edit them.** A local difference belongs in `source/styles/rqwst.css` or `source/styles/rqwst-assignment.css`, which the page loads after them. Keeping the vendored bytes unchanged is what lets each file be checked against the design system.

- **Donor:** `apexSolarKiss/design-system-ASK` at commit `1f5461fa1e6283be2daa2fdaee7849cf2977a7de`, where design-system-ASK#214 merged. All 18 files below are at that commit.
- **Files:** 16 design-system files and the design system's own license and notice, each byte-identical to its donor's file. The git blob is the id `git rev-parse <commit>:<path>` gives for the donor's file, and the id `git hash-object` gives for the copy here.

| Here | In design-system-ASK | Bytes | Git blob | SHA-256 |
|---|---|---:|---|---|
| `source/_dsa-surface/surface-action.css` | `surface-action.css` | 21,898 | `9d827ae1f4814c45353e4a1a61cc8814e26f0ed5` | `f00ccde1b4db17687fd6ecd62644700932107352b37476184718f2036209fb2e` |
| `source/_dsa-surface/surface-document-overflow.js` | `surface-document-overflow.js` | 3,623 | `94dc846a8aeb9410b38e84e72a56c506ea31daab` | `d66d31b36f697e20739ba009dcfa7ba05328be33fd6f401fa41443d3e268bca1` |
| `source/_dsa-surface/surface-document.css` | `surface-document.css` | 88,017 | `537f12d0a906deff7d08f47bbf9c1d875a3bd843` | `57140e0d5383f95d4d88001e535c682d0c47152e2165e92516ece2ba4cf999ed` |
| `source/_dsa-surface/surface-panel.css` | `surface-panel.css` | 11,230 | `12582f538ad7b3c7e2ba229101e481a39dd5657a` | `883e24ac5407a4fe24f9149b0d8964a06995cc88b6b6150b1a1bdfd9aee2976e` |
| `source/_dsa-surface/surface-shell.css` | `patterns/surface-shell/surface-shell.css` | 72,505 | `333f387bf61087f787e1982ea754d478d456b10d` | `2c9bbe388396f88198a08140758832ec09452a68addacce49f275728343559d3` |
| `source/_dsa-surface/surface-shell.js` | `patterns/surface-shell/surface-shell.js` | 53,439 | `38b01d4b2f299aef261050ff465a76c781b5b700` | `a69b9de1d5b316ab8ee37f2670f61284dac5f84be2ba43c522bdc2e2d6f8d5e9` |
| `source/_dsa-surface/surface-shell.template.html` | `patterns/surface-shell/surface-shell.template.html` | 15,976 | `bec3c28f83f2fa67021f9816948f0529e0df43f1` | `9fab10a625cec1e0764f16ec40affe4b26a8333aefcb45f470b1623c338ee9f0` |
| `source/_dsa-surface/surface-text-link.css` | `surface-text-link.css` | 7,921 | `a9c51dd6e2ad41eb4b010a138d422e4c02d91909` | `9a6acf457ffbe2a0bb31ae28507855b6446195ff9dcd3cc7112f04ec5bf0fce3` |
| `source/_dsa-surface/surface-treatments.css` | `surface-treatments.css` | 48,906 | `3da092b5c26baccfc5fba2a8b001c09f695cceba` | `a277e97e99779f42053e6c1c4043ddda1ecdfaaa34945096dc1cf724b2625c31` |
| `source/_dsa-tokens/colors_and_type.css` | `colors_and_type.css` | 15,945 | `e16dfa72b55919f5487581550c70976781a6b0eb` | `d00f1f4f17d4af5201d840dd9f1f558800e69c77280826a3f8d07e9ffd99ef5e` |
| `source/_dsa-tokens/fonts/Inter-OFL.txt` | `fonts/Inter-OFL.txt` | 4,380 | `9b2ca37b3ffc77391d8b2ebef4a974ef32bf46ea` | `262481e844521b326f5ecd053e59b98c8b2da78c8ee1bdbb6e8174305e54935a` |
| `source/_dsa-tokens/fonts/InterVariable-Italic.woff2` | `fonts/InterVariable-Italic.woff2` | 387,976 | `b3530f3f5269165314114a9e1c2f129e20fddcbd` | `e564f652916db6c139570fefb9524a77c4d48f30c92928de9db19b6b5c7a262a` |
| `source/_dsa-tokens/fonts/InterVariable.woff2` | `fonts/InterVariable.woff2` | 352,240 | `5a8d3e72ad7ffb62af3b146e1b1f54ab5813a212` | `693b77d4f32ee9b8bfc995589b5fad5e99adf2832738661f5402f9978429a8e3` |
| `source/_dsa-tokens/fonts/JetBrainsMono-Italic.woff2` | `fonts/JetBrainsMono-Italic.woff2` | 123,160 | `5e8a82e3669297716702f70a5f9ca242ca050896` | `76a805b6ea613ce2e3973f1bac6fa29db23116b2881390b59247d22890844ecc` |
| `source/_dsa-tokens/fonts/JetBrainsMono-OFL.txt` | `fonts/JetBrainsMono-OFL.txt` | 4,399 | `5ceee0025da23d2cd5fd14b28569708a8db4db2b` | `a76abf002c49097d146e86740a3105a5d00450b1592e820a1109a8c5680cd697` |
| `source/_dsa-tokens/fonts/JetBrainsMono.woff2` | `fonts/JetBrainsMono.woff2` | 113,672 | `856547f84b0365f4db7bfee3ac88f558a117410e` | `31ec365b93e4bad6f202ce23352a56d01ca4462b2afc782ed2cf6fa42ca9ac0e` |
| `licenses/design-system-ASK/LICENSE` | `LICENSE` | 10,835 | `0c382f604647738e78449026c3dd3d5c26702a6f` | `8188fe74beac4005f834721ae459e84909cd42c55554549ad750f50fcfc20801` |
| `licenses/design-system-ASK/NOTICE` | `NOTICE` | 425 | `f978d4aa912e5691eafedc7cde560d7f694b04f5` | `58fb1aaa9c9eba885d5d72d10ee86764fe69753cd1bfe3a3ac175cdcbef0fc46` |

## Load order

The page loads, in this order:

```text
source/_dsa-tokens/colors_and_type.css
source/_dsa-surface/surface-action.css
source/_dsa-surface/surface-panel.css
source/_dsa-surface/surface-text-link.css
source/_dsa-surface/surface-document.css
source/_dsa-surface/surface-treatments.css
source/_dsa-surface/surface-shell.css
source/styles/output-artifact.template.css
source/styles/rqwst.css
source/styles/rqwst-assignment.css
```

The order is part of the design system's contract. `output-artifact.template.css` is the design system's `output-artifact` template overlay, kept here as the page's own copy: lines 37 to 196 of `patterns/output-artifact/static-output-artifact.html` at the donor commit above, the template's inline style block, without its `<style>` tags (9,357 bytes, SHA-256 `2a6d7f6ab9b8d12b39f83f9cb7e91f2c7104ccdd8863bb8540f5d149f5ef48b2`); `rqwst.css` is the page's layout and print rules; `rqwst-assignment.css` is the RQWST presentation assignment, which binds the light field and loads last.

Scripts load at the end of the body: `source/_dsa-surface/surface-shell.js`, for the navigation, then `source/_dsa-surface/surface-document-overflow.js`, for the tables' scroll cue.

`source/_dsa-surface/surface-shell.template.html` is loaded by no page and is not sealed. It is the shell's canonical markup specimen, which the shell contract asks every consumer to carry with `surface-shell.css`, so a page can be checked against it.

`index.html` carries all of these inlined. Each `<style>` and `<script>` block records its source path in `data-sealed-from`, and the foundation's eight font URLs are replaced by the embedded woff2 data.

## Re-syncing

The copies stay at their commit until someone updates them on purpose. Forking or cloning this repository does not update them.

1. Choose the new design-system-ASK commit and read what changed in these files since the donor above.
2. Copy each file listed above from that commit, unmodified, to the same place here (`git -C <design-system-ASK> show <commit>:<path> > <path here>`). Add a file only if the page now needs it, and add it to this list and to the load order. Re-extract `source/styles/output-artifact.template.css` the same way: the inline style block of `patterns/output-artifact/static-output-artifact.html` at that commit, without its `<style>` tags.
3. Update the donor, the byte counts, the git blobs and the SHA-256 values above, and the overlay's line range, bytes and SHA-256 under Load order.
4. Re-seal: `python3 tools/seal.py`. A re-seal changes `index.html`, so record it as a new release in `PROVENANCE.md`.
5. Run `python3 tools/check.py --donor <design-system-ASK clone>`, which checks every file here against the donor and runs the design system's role-conformance check on the sealed page. Then open the page in light and dark, at desktop and phone widths, use its navigation, and print it.
