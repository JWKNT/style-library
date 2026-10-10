# JWKNT botanical initial alphabets

Three new, complete A–Z sets of monochrome decorative SVG illustrations:

- **Iris**: original drawn plant-stem lettering, contrasting bowed strokes, whiplash tendrils, iris petals, and lanceolate leaves attached to letter anatomy.
- **Laurel**: individually fitted, bowed high-contrast Roman contours with fine engraving, rooted sprays of paired laurel leaves, flowers, and berries.
- **Briar**: broad light capitals carved transparently through an original dense Arts-and-Crafts tapestry of dog roses, stems, and engraved leaves.

The runtime assets are `assets/<slug>/A.svg` through `Z.svg`. Each is a titled 128 × 128 standalone illustration with six units of minimum breathing room. The only visible paint is `currentColor`. There are no text elements, font programs, images, external resources, white backgrounds, or paint masks. Letter and leaf negative spaces are actual compound-path holes. Each SVG can be recolored by its `color` property when embedded inline, or used as a monochrome image/mask.

## Sources and license

Iris's letterforms and all three families' ornaments are original drawings in `build.py`. These original contributions, the build scripts, and the proof layouts are dedicated to the public domain under CC0 1.0: https://creativecommons.org/publicdomain/zero/1.0/ .

Laurel uses capital-outline material from **Noto Serif Display Regular**, version 2.003, copyright 2016 Google Inc., Monotype Design Team, under the SIL Open Font License 1.1. Its source font and full OFL notice are in `sources/`. The letter forms have illustration-specific bowing, asymmetric fitting, hatching, and new floral artwork; this is an SVG illustration series, not a new font distribution.

Briar uses capital-outline material from **DejaVu Serif**, version 2.37. Copyright (c) 2003 Bitstream, Inc. All rights reserved; DejaVu changes are in the public domain. The font source and full permission notice are in `sources/`. The derived SVG illustration series has a distinct name, altered fitting/contours, and an entirely original floral composition. Source fonts are included unchanged only for reproducibility.

The font notices remain applicable to inherited material; the CC0 dedication does not replace them. Detailed per-family changes, source SHA-256 hashes, and asset hashes are recorded in `metadata.json`.

### Reference inspection

The existing Readers Art Nouveau Initialen (Urth), Acorn Initials (Green), Eileen Caps (Nightside), and Elzevier Caps (Lake) SVGs and their CTAN/LPPL notices were inspected. A/B/M/Q from all four were rendered and viewed before the new drawings were made. No reference SVG paths were copied. `references/reference-grid.png` is a local review aid, not a runtime asset or a newly licensed contribution.

## Rebuild and check

Install the pinned packages in `requirements.txt`, then run:

    python build.py --proofs
    python validate.py

`build.py` creates the composition. `vector_boolean.py` resolves filled shapes, counterforms, engraving, clipping, and interlacing into one transparent even-odd compound path per letter. No SVG mask behavior is required at runtime.

Local proof images cover every letter at 96 and 112 px and selected letters at 96/120 px on both light and dark surfaces. `validation.json` tests all 78 at 96, 112, and 120 px for visible ink, transparent margins, and safe bounds. Proofs and source reference renders are review files only. They have not been uploaded.
