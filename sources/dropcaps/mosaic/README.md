# Tessera

A complete original A–Z decorative alphabet for the JWKNT Style Library.

The silhouette uses broad, angular strokes, faceted bowls, and integral forked spear terminals. Nested lozenges, chevrons, triangles, and short angled joints are cut through the letter itself. The SVGs contain only one explicit currentColor path with true transparent inlays and counters. There are no fonts, text nodes, masks, raster images, or external references at runtime.

## Rebuild

Use Python 3.12 and the exact versions in requirements.txt:

    python -m pip install -r requirements.txt
    python build.py
    python validate.py

The G and T mappings in build.py retain every original coordinate. The build writes assets/tessera/A.svg through Z.svg, all 26 individual proofs at 96, 120, and 300 pixels high, full-alphabet proof sheets, and geometry metadata. Raster proofs and reference-study files are for local review only.

## Deliverable

Integrate assets/tessera/ and preserve metadata.json, LICENSE.txt, build.py, requirements.txt, and validation reports as source records. Do not package vendor/, proofs/, or references/ as runtime files.

Original artwork and generator: CC0-1.0. No borrowed font outlines.
