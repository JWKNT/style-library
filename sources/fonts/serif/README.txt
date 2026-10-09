EDITORIAL / SERIF COLLECTION: 22 CUSTOM REGULAR FACES

These are custom open-license derivatives, not reproductions of proprietary
fonts and not claims of wholly original full-repertoire type design. Each
face combines sixteen fully reconstructed glyphs with its own structural
choices, spacing, proportions and optical outline adjustments.

INSTALL / WEB USE
Install the Regular TTF with an operating-system font manager. For a website,
use the matching WOFF2 in a CSS @font-face rule, font-weight: 400 and
font-style: normal. Each family has a unique family, full and PostScript name.
There are no dedicated bold, italic or variable cuts.

CONSTRUCTION
The following sixteen characters are drawn from authored contours in build.py:
A M Q R J a e r t g 1 4 7 T E L.

Design variants include four Q endings, four R legs, three a structures,
four g structures, three r/J terminal treatments, different M vertices,
A crossbar positions, figure flags, cross-stroked sevens, serif reach and
bracketing, and independently controlled thick/thin contrast. This is more
than source renaming or uniform scaling. Every face also has a different
optical recipe for x-height, bowl-waist shape, descenders and spacing. Cap,
lowercase and punctuation spacing receives character-specific adjustments.

New contours are boolean-unioned before font construction. Curves in the
new drawings are densely sampled to polygonal contours (normally sub-unit
approximation error), with winding set explicitly for holes and outer paths.
Inherited source curves remain quadratic. Overlapping authored pieces are
resolved before export, rather than relying on browser overlap behavior.
After optical mapping, authored contours are resolved again on the integer
grid to remove small quantization tangencies and collapsed contour fragments.

COVERAGE
All 95 printable ASCII codepoints are present in every face. The metadata
states each face's exact Unicode count and Latin coverage. Source repertoires
are retained unless a TTF would exceed 500,000 bytes. In that case a conservative
web subset retains mapped characters in ASCII/Latin-1, Latin Extended A/B,
combining diacritics, Latin Extended Additional, general punctuation, currency,
letterlike symbols, arrows/mathematical operators, technical symbols and
geometric shapes, plus necessary layout and glyph closure.

Some listed blocks are only partially present in the original source. No
additional codepoint coverage is claimed where it was absent in the source.
The exact preserved cmap is tested; full Latin-1 and Extended-A status is
reported individually. These files are not an assertion that all languages
or specialist-script shaping have been tested.

COMPOSITES, SPACING AND LAYOUT
Accented composite glyphs are decomposed only after replacing their base
letter, so they inherit the new forms. Source glyph advances are preserved
before optical width/spacing changes. GPOS horizontal placement and advance
values and legacy kerning scale with the face's horizontal dimensions; mark
anchor heights follow the x-height map. GSUB and GDEF remain, with appropriate
subsetting closure when applicable. Math-specific layout is removed because
specialist mathematical geometry was not redesigned. Old hint bytecode and
hint-dependent tables are removed after outline edits.

All retained glyphs fit the hhea and Windows ascent/descent bounds, with a
20-unit buffer. This conservative choice can produce generous default line
spacing. Web typography can set a deliberate CSS line-height for its text.

VALIDATION / PROOFS
metadata.json is an array with per-face paths, sources, full license-notice
paths, design parameters, source and output hashes, codepoint coverage and
substantial-redraw fingerprints. Source glyph fingerprints use the source
outlines normalized to 1,000 units per em before customization. validation.json records automated checks.
There is one full proof sheet for every face and four contact sheets.
Proofs include capitals, lowercase, figures, punctuation, accents and running
paragraphs at reading sizes. These are actual rasterizations of the fonts.

Automated checks include cmap preservation, ASCII coverage, visible non-space
ASCII outlines, full-glyph compilation, source-versus-output fingerprints for
all sixteen redraws, WOFF2 cmap/metrics/ASCII-outline round trips, and FreeType
rendering at 12, 18, 32 and 72 pixels. This is development QA, not a claim of
exhaustive commercial typefoundry certification.

REPRODUCE
Python 3.10 or later.
Install standard packages: pip install fonttools Pillow shapely brotli
Run: python build.py
No network is needed during the build. All input fonts and source notices
are in the script-relative sources/ directory. No files elsewhere in another
task workspace are imported. Fixed font timestamps give reproducible output.
Proof labels use the bundled, licensed Noto Serif source. All input paths are
relative to this script, so the build is portable across workspaces.
Tested dependency versions are listed in requirements.txt.

LICENSES
Noto Serif and Noto Serif Display derivatives: SIL Open Font License 1.1.
Original copyright 2015 Google LLC / 2016 Google Inc. See sources/OFL-1.1.txt
and sources/Noto-Debian-copyright.txt for complete license and notices.

Liberation Serif derivatives: SIL Open Font License 1.1.
Digitized data copyright 2010 Google Corporation. Copyright 2012 Red Hat, Inc.
Reserved names include Liberation, Arimo, Tinos and Cousine. None is used as
a generated family name. See sources/Liberation-copyright.txt.

DejaVu Serif derivatives: Bitstream Vera license, with DejaVu changes in the
public domain. Copyright 2003 Bitstream, Inc. Bitstream Vera is a trademark
of Bitstream, Inc. Generated names contain neither Bitstream nor Vera.
See sources/DejaVu-copyright.txt for the complete license.

Custom outline designs and modifications copyright 2026 jehlp.net. Each
modified font remains under the same applicable license as its source.
Preserve the appropriate full notice and license when redistributing. The
fonts may be bundled with projects but cannot be sold by themselves under
these licenses. Documents made using them are not subject to the font license.
