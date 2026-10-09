SANS COLLECTION: 23 CUSTOM REGULAR TYPEFACES
Version 1.000, 9 October 2026

This collection supplies 23 TTF desktop fonts and 23 matching WOFF2 web fonts.
It is a set of custom open-license derivatives. It does not claim that all
inherited Unicode characters were drawn from scratch or tested in all languages.

DESIGN
Each face contains 23 freshly authored character outlines:
A M O o 0 C c Q G R a e g r t i j l f I 1 4 7.

The faces use separate design combinations: circular or rounded-square bowls;
single- or double-storey a; single-storey or two-loop g; swept, diagonal,
hooked or right-angle Q tails; low or high A bars; deep or raised M joins;
flat, cut or wedge r terminals; curved, angled or flat t feet; and circular,
square or diamond dots. Letter spacing and optical kerning corrections differ.
The script contains the complete coordinate drawings and configuration for each.
No source font is globally stretched, skewed, or merely renamed.

The metadata identifies reading-oriented and display-oriented designs. The more
geometric and unusual forms work best in short text or headlines. The specimen
paragraphs at 14, 18 and 24 px also show how every face behaves in smaller text.
These are Regular upright styles only. No artificial bold or italic is supplied.

SOURCE PALETTE AND LICENSES
Noto Sans and Noto Sans Display: SIL Open Font License 1.1.
Liberation Sans: SIL Open Font License 1.1.
Open Sans, this installed 2010–2011 version: Apache License 2.0.
DejaVu Sans: Bitstream Vera and Arev license notices; DejaVu changes public domain.

Full distribution notices and embedded original copyright/license records are in
licenses/. The complete Apache 2.0 text is included separately. Original font
binaries are in sources/ so the set can be rebuilt without network access.
Modified names do not use the reserved upstream family names. The original
copyright and license notices remain in every output font. Modifications follow
the applicable source license; they are not all relicensed as OFL.
Do not remove notices when redistributing. Read the license for the chosen face.
No proprietary font binary was used.

COVERAGE AND LAYOUT
Every face includes all 95 printable ASCII characters. Per-face metadata records
Latin-1 and Latin Extended-A completeness and actual Unicode/glyph counts.
Noto, Liberation and Open Sans retain the source character maps. DejaVu derivatives
are conservatively subset to ASCII, Latin-1, Latin Extended A/B, Latin Extended
Additional, general punctuation, currency, letterlike symbols, arrows, common
mathematical symbols and box/block symbols, with composite and layout closure.
All output TTFs are smaller than 500,000 bytes.

Existing glyphs, mark anchors and component offsets stay in their original
coordinate system. Accent composites use redesigned bases. Source GSUB and GDEF
are preserved after any subset closure. Preservation is checked by canonical
recompilation; compiler offset packing can differ from raw upstream bytes. Source GPOS positioning is retained.
Open Sans legacy kerning is converted into GPOS without dropping pairs; 12 small
family-specific optical corrections are added. Legacy kern tables are removed
from outputs to prevent duplicate or divergent kerning and the length overflow
in the old Open Sans source. Original bytecode is removed after outline changes.
Modern grayscale rendering is recommended. Windows and hhea vertical metrics
include the full retained outline bounds. Fonts permit embedding (fsType 0).

BUILD
Use Python 3.12 or newer. Install the versions listed in requirements.txt:
  python -m pip install -r requirements.txt
Then run:
  python build_fonts.py
  python verify_fonts.py --rebuild

All source paths are relative to this folder. No external helper code or fonts
are needed. Outputs use fixed font timestamps. Verification compares two builds
byte for byte for both TTF and WOFF2. Do not treat the retained proof-review record
as approval of a later design change: it is tied to the exact reviewed font hash.

FILES
fonts/                 23 TTFs, 23 WOFF2s, per-face metadata
fonts.css              @font-face rules with relative WOFF2 URLs
metadata.json          Collection metadata, coverage, changes, source and hashes
validation.json        Technical checks and exact-hash visual-review status
geometry-validation.json  Sampled authored-contour intersection checks
visual-review.json     Record of inspected final proofs and corresponding hashes
proofs/                All 23 actual-font PNG specimens and 6 combined proof sheets
sources/               Five original open-license source fonts
licenses/              Full source notices and licenses
build_fonts.py         Complete drawings, compilation, metadata and proof generation
verify_fonts.py        File, outline, layout, geometry and deterministic-build checks
check_geometry.py      Curve-sampling geometry checker used by verification

QUALITY SCOPE
Every proof was visually inspected. The inspection covers upper- and lowercase,
numerals, punctuation, accents, characteristic glyphs, spacing pairs and paragraphs
at reading sizes. Technical checks cover cmap, contours, components, bounds,
nonempty printable glyphs, distinct source/output outline fingerprints, unique
ASCII fingerprints across the set, and all-outline WOFF2 round-trip equality.
This is not independent certification across every platform or inherited script.
