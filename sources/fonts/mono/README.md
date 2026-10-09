# Twenty-two custom mono families

A Regular-only collection of monospaced reading and coding designs for the
jehlp.net style library. The sources are openly licensed Noto Sans Mono,
Liberation Mono and DejaVu Sans Mono. These are custom derivatives, not claims
of wholly original upstream typefaces.

## Rebuild

Use Python 3.12, install the pinned packages in requirements.txt, then run:

    python -m pip install -r requirements.txt
    python build_fonts.py
    python validate_fonts.py

All font, notice and output paths are relative to these scripts. No proprietary
font, installed system font, network fetch or sibling working directory is
needed. The adjacent source files are complete, unmodified upstream inputs.
`--only Quasar,Quay` is available for an individual design iteration; a complete
build is required to refresh the collection metadata and contact sheets.
OpenType created/modified timestamps are fixed for deterministic binary output.

## What was designed

Each profile combines explicit letter and symbol constructions with a nonlinear
redesign of the remaining licensed body outlines. X-height, cap-height and
descender regions have independent mappings. Height-dependent width changes
alter bowl/shoulder relationships. No face is produced by merely changing names
or by applying only a uniform scale.

Each family has 46 to 54 newly constructed glyphs, including 0, O, Q, o, a, g,
I, i, j, l, 1, 4, 7, f, r, t and its code punctuation. Angular designs add a new
A, M, N, V, W, Z and z. There are oval, capsule, organic, octagonal, chamfered and
square bowl constructions; round, square, stepped, hooked and serif terminals;
dotted, slashed, diamond, square and bar-marked zeros. The manifest lists the
exact redraw set and the complete art-direction profile for each family.
Accented composite glyphs are recomposed from the redesigned bases.

## Metrics and coverage

All fonts use 1000 units per em. Printable mapped characters use one fixed cell,
565 to 670 units according to the design. Mapped Unicode combining marks and
format controls have zero advance. The GPOS anchors receive the same coordinate
mapping as body outlines. Existing canonical composition, localized forms,
mark placement and relevant script-form GSUB data are retained. Optional
ligatures, alternate zero substitutions, small-cap and fraction features that
would replace coding shapes or contract character sequences are omitted.
Inherited TrueType hint programs are removed after outline changes.

The web set retains supported characters from Basic and Extended Latin,
combining accents, Greek/Cyrillic, phonetic extensions, punctuation, currency,
letterlike symbols, arrows, mathematical operators, technical symbols,
box drawing, geometric shapes, dingbats, Latin ligature characters and U+FFFD.
Availability still depends on each source. The exact mapping count is recorded
per family; this is not a promise of complete support for every listed block or
for scripts outside them. Source fonts remain complete in sources/.

## Verification and evidence

- Every font has all 95 printable ASCII characters; the 94 visible characters
  have nonempty outlines and ink inside their fixed cells.
- Every output glyph is decomposed and checked for structural coordinate and
  contour integrity, finite int16 coordinates and fit within hhea/Windows bounds.
- The fixed-pitch flag and unrestricted embedding flag are checked.
- The five actual outlines 0/O/1/l/I are distinct in every face.
- WOFF2 reopening must preserve the exact ASCII RecordingPen outline sequence,
  cmap and all horizontal metrics from the TTF.
- FreeType tests at 12, 14, 18, 24 and 48 px require equal ASCII advances, unchanged
  multi-character code spacing and single-cell NFD combining clusters.
- SHA-256 hashes record source and output ASCII glyph drawings, independently
  from metadata and file hashes. Pairwise checks compare all 22 font outputs.
- All 22 real font-rendered proof pages include capitals, lowercase, figures,
  punctuation, accented text, reading paragraphs, code and small-size samples.
  Four contact sheets and a combining-mark sheet supplement those proof pages.

Metadata and validation results are written to metadata.json and validation.json.
The fonts are TTF and WOFF2 files in fonts/. Proofs are in proofs/.

## Licensing

Read LICENSE.txt and all relevant full notices in sources/. Each derivative
retains its source font license, and the build/validation scripts use MIT.
Upstream copyright notices also remain in each output font's naming table.
The collection uses new family names and no proprietary font inputs.
