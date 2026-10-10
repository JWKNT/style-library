# Medieval decorative initial alphabets

78 standalone SVG illustrations: three complete A–Z sets.

- **Thornwood:** floriated woodcut letters, lobed thorn leaves and engraved botanical detail.
- **Scriptorium:** illuminated blackletter penwork with open curls and newly incised scrolls.
- **Ribbon:** insular band letters with transparent channels and genuine over/under strands.

Each SVG has a descriptive title, a 120 × 120 viewBox, generous transparent bounds and only currentColor path geometry. No font, text, image, mask, white paint, script or external runtime resource is present. The letters are readable at the supplied 96px and 120px proof sizes. Inline SVGs inherit CSS color; a separately loaded SVG defaults to black.

## Rebuild

Install the packages in requirements.txt, then run:

    python build.py --render
    python validate.py

The build entrypoint imports compose.py, derive.py and glyph_geometry.py. It reads the 78 exact source SVGs in sources/morris-initialen, sources/royal-initialen and sources/carrick-caps. It writes assets, metadata.json and LICENSE.txt. With --render it also writes local proof PNGs. There are no network calls or machine-specific input paths.

## Modified works and source availability

These are materially recomposed derivatives, not renamed unmodified alphabets. Thornwood retains only the Morris letter bodies and replaces their surrounding ornament. Scriptorium reconstructs Royal bodies and adds new pen sprays and internal engraving. Ribbon removes old fine interlace, rebuilds the letter as channeled bands, and adds new woven strands. Ribbon I and T were redrawn for distinct letter anatomy; E has a strengthened exposed middle arm, and Q has an extended descender. Thornwood E preserves the source's separate central stroke. Full per-style modifications and exact hashes are in metadata.json.

Original artwork was digitized by Dieter Steffmann / Typographer Mediengestaltung. Original notices, source illustrations, the collection permission, and LPPL 1.3c are retained under sources/. The source SVG extracts are the exact illustrations used to rebuild this work; they are not represented as the complete CTAN font collection. The complete unmodified collection is available at https://mirrors.ctan.org/fonts/initials.zip and its catalog page is https://ctan.org/tex-archive/fonts/initials.

The derived artwork is distributed under LPPL 1.3c or later with distinct modified-work names. The new generator code is MIT-licensed; this does not replace the artwork's LPPL terms. See LICENSE.txt and sources/LPPL.txt.

## Verification

All 78 illustrations were rendered and visually inspected at 96px and 120px. All A–Z grids and both light/dark specimen sheets are local in proofs/. They are review images, not substitutes for the SVG deliverables. validation.json records structure, exact source hashes, bounds, transparency and raster checks. No files were uploaded or published by this generator.
