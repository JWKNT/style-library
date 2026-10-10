# JWKNT display initials

Three complete new decorative A–Z alphabets, provided as 78 transparent, standalone
SVG illustrations. They contain geometry only. Each SVG has an accessible title,
a description, a 1000-unit square viewBox, and currentColor fill.

- Nocturne: blackletter anatomy, flowing pressure-written swashes, linked pen loops,
  quill-cut highlights, and fitted counter arabesques. Q has an independent,
  substantial descending tail. J has a stronger lower hook.
- Obelisk: original Art Deco alphabet with faceted bowls, deliberately low crossbars,
  fluted strokes, terminal collars, and restrained architectural accents.
- Cameo: Roman capitals with new cut-stone relief, diagonal graver shading, inset
  highlights, and letter-fitted laurel/acanthus ornaments.

All negative areas are actually transparent. There is no white paint, embedded
font, SVG text, bitmap, external URL reference, filter, or masking dependency.
The familiar source letterforms in Nocturne and Cameo have been expanded into new
decorative compositions. Obelisk's 26 skeletons are authored in the generator.
These are not renamed copies of the Readers initials.

## Files

- assets/nocturne/A.svg through Z.svg
- assets/obelisk/A.svg through Z.svg
- assets/cameo/A.svg through Z.svg
- generate.py: reproducible construction source for all 78 illustrations
- metadata.json: descriptions, exact sources, source hashes, licensing, and changes
- NOTICE.txt, CC0-1.0.txt, sources/*COPYRIGHT.txt, sources/OFL-1.1.txt: notices
- sources/Euler-Bold-eufb10.pfb and sources/NotoSerifDisplay-Bold.ttf: unchanged fonts
- requirements.txt: exact tested Python package versions
- validate.py and quality-review.json: automated audit and recorded visual review
- proofs/: local-only inspection images, including every letter at 96px and 120px

Proof PNGs are not publication assets. Publish the SVGs and applicable notices.
Source programs and fonts may be packaged separately from per-style illustration
ZIP downloads. Source fonts are never needed by a browser rendering these SVGs.

## Rebuild

Use Python 3.12 and the system Cairo library (CairoSVG's usual requirement):

    python -m pip install -r requirements.txt
    python generate.py
    python validate.py

The generator uses only paths relative to itself and ordinary Python imports.
It regenerates the SVGs, all 96px/120px proof grids, 120px individual PNGs,
dark-paper A proofs, and validation.json. It does not modify site UI or publish.
The metadata, notices, and this editorial documentation are maintained separately.

Coordinates are simplified by at most 0.65 units on a 1000-unit canvas and rounded
to 0.1 units. Relative path commands avoid redundant coordinate digits. This is
less than 0.08 screen pixels at the 120px proof size. All SVGs remain below 40 KB.

## Rights and provenance

New original illustrations, original ornament geometry, and generator: CC0-1.0.
The unchanged Euler and Noto source font programs remain under SIL OFL-1.1.
Their exact original notices and full license are included. The OFL output
exception permits generated illustration documents to be licensed separately.
No original font source is relicensed, renamed internally, or modified.

Euler Bold: AMS Fonts, source version 003.003, Reserved Font Name EUFB10,
copyright 1997, 2009, 2011 American Mathematical Society.
https://ctan.org/pkg/amsfonts

Noto Serif Display Bold: source version 2.003, copyright 2016 Google Inc.,
designer Monotype Design Team.
https://github.com/notofonts/latin-greek-cyrillic

Rothenburg Decorative, Gotische Initialen, and Royal Initialen were rendered and
inspected from the Readers assets as art-direction references. Their notices and
LPPL source-permission statement were read. No paths from those assets are included.
