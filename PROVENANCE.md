# Provenance

This repository's history is new and public. It carries a design demo of RQWST's identity on design-system-ASK: RQWST's public landing page, then a content-reduced concept example. The landing section's copy, apart from the label above its headline, is RQWST's own, as rqwst.com showed it on 14 November 2026. The rest of the page copy was written for this public demo, and its words are not drawn from any private document. The concept samples are synthetic: every name, outlet, date and count in them is invented. The design implementation, the page shell's composition, the presentation assignment and the identity artwork, descends from an earlier private prototype; none of that prototype's content or release history is part of this repository.

## The page

- **Artifact id:** `rqwst-public-demo`.
- **Source:** `source/pages/public-demo.html`, sealed by `tools/seal.py` into `index.html`.
- **Published as:** [rqwst.a-s-k.studio](https://rqwst.a-s-k.studio/).
- **Built on:** design-system-ASK's `output-artifact` v3 register inside its surface shell, with the `rqwst` presentation assignment.

## Releases

### Release 1 // `public-demo-v1`

- **Sealed page:** `index.html`, 2,970,841 bytes, SHA-256 `07e9411551b9684150415caa79a5c62b5db64e4cebd3d701d4b2b0c1486169fd`.
- **Design system:** design-system-ASK at `300ec48fae21304a03c9b81ea6e056e675947ed3`, as listed in `VENDOR.md`.
- **What it is:** the first release: RQWST's landing page in the design system's roles, with its actions leading to rqwst.com; then a concept statement, a sample request, a five-step sequence, a status panel, a table of sample requests, and a note on the demo.
- **Checked:**
  - `python3 tools/check.py --donor <design-system-ASK clone> --denylist <list kept outside the repository>` passes. That covers the vendored files against the donor commit, the seal reproduced byte for byte, a page that loads nothing from outside itself, no local path, no listed term, no rqwst.com email address other than RQWST's public contact and no rqwst.com URL other than its three public pages in the repository's own files (the vendored design-system files are verified by identity instead), the artwork exports, and the design system's role-conformance check in light and dark at 1440px and at 375px on a phone.
  - The page was rendered at desktop and phone widths in light and dark, its navigation was used, and it was printed from a desktop and a phone-width window in both themes.

## Presentation assignment

- **Name:** `rqwst`, declared on the page root as `data-surface-assignment`.
- **Field:** `rqwst-lavender`, declared on the page root as `data-surface-field`.
- **Declaration:** `source/assets/rqwst-assignment.json`, which names every bound role per context, for the role-conformance check.
- **Light:** binds the field only. `--bg-from` / `--bg-to` are `#D4C6E1` / `#EBDEE8`, on the shared 45° mechanism. `--bg-gradient` is `linear-gradient(45deg, #D4C6E1 0%, #EBDEE8 100%)`, and `--bg-edge` is `#EBDEE8`. The foreground ramp, lines, materials, shadows, accents, links and focus are the design system's light values.
- **Dark:** binds nothing below the identity: every role is the design system's.
- **Identity, in both themes:** the wordmark `#8B79A2` and the plume `#B18DFE` are the artwork's own fills.

**Computed.** WCAG 2.x contrast at the field's two stops, from the declared colors, with translucent foregrounds composited on each stop.

| Ground | `--fg-1` | `--fg-2` | `--fg-3` | Wordmark | Plume | Design-demo note |
|---|---|---|---|---|---|---|
| Light field | 3.50 / 4.36 | 2.67 / 3.32 | 1.76 / 1.98 | 2.42 / 3.02 | 1.60 / 1.99 | 1.94 / 2.41 |
| Dark field | 10.25 / 12.26 | 5.98 / 6.61 | 3.41 / 3.49 | 4.23 / 5.06 | 6.41 / 7.67 | 5.29 / 6.33 |

- **`--fg-3`** carries the labels and metadata: the landing section's label, language note, offer lines and terms and contact line, the metadata strip, the step labels, the bordered label, the labeled pairs' names, the table headings and the provenance footer, whose code takes `--fg-2`.
- **The design-demo note** is the shell's note role, in the design system's emphasis magenta (`#FF00FF`) in both themes.
- **The wordmark and plume** are identity artwork, not text.
- **Not reviewed:**
  - `rqwst-lavender` has no rail calibration, and no rail is drawn;
  - the panel material and the navigation glass are not measured here;
  - no semantic signal is used.

## Adding a release

1. Change the source. If the design system moves, copy its files again and update `VENDOR.md`.
2. Seal with `python3 tools/seal.py`, then run `python3 tools/check.py --donor <a design-system-ASK clone>` until it passes. Open, navigate and print the page in light and dark, at desktop and phone widths.
3. Add the release above the previous one. Record its number, the sealed page's size and SHA-256, the design-system commit, what changed and what was checked. Declare its tag, `public-demo-v<N>`, and create that tag at the commit that lands the release on `main`.
4. If a release moves the page to another route, its entry records the new route. The artifact id stays.
