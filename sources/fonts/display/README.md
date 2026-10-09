# Display and calligraphic font collection

23 mixed-case families; each has TrueType and WOFF2 files in `fonts/`.

## Rebuild

Use Python 3.12 or later. Install the ordinary open-source dependencies in
`requirements.txt`, then run `python build.py` from this directory.
The builder uses only relative source files and installed dependencies. It does
not download fonts or depend on the surrounding project. Builds use a fixed
font timestamp. `metadata.json`, `validation.json`, and proofs are regenerated.

## Design and provenance

Nine readable calligraphic/italic faces are Noto derivatives, retaining a
Latin-focused extended repertoire, original advances, source kerning, and mark
positioning. Their complete basic Latin letters/digits and ampersand are newly
drawn; 36 named characters have substantial discrete anatomical changes.
No global transformation is applied to a source font. The source cap height and
x-height guide the independent drawing fits. Standard source ligature features
are disabled so they do not silently replace custom letters with source forms.
Composite glyphs are rebuilt from their references. All source raster hints are
removed, including composite instructions that referenced old point indices.
Subsetting preserves layout
and component closure while keeping the web files practical.

Fourteen faces use the supplied original skeleton drawings and wholly generated
outlines. These include new capital construction, five lowercase a/g systems,
several Q/R tails, numeral alternates, independently tuned crossbars, shoulder
shapes, optical bowl stress, and letter-specific spacing. Distinct pen and serif
systems are additional design decisions, not the sole differences among faces.
ASCII 95 and nine typographic characters are included in every original face.
These faces do not contain an extended-Latin repertoire.

`metadata.json` identifies each basis, complete files, hashes, and anatomy list.
`licenses/` contains the complete OFL and original source copyright notices.
The exact source TTFs and original skeleton script are in `sources/`.

## Checks and proofs

`validation.json` checks ASCII coverage, nonempty drawing bounds, clipping metrics,
WOFF2 coordinate and metric round trips, per-face semantic outline fingerprints,
and source-versus-output outline differences. All family fingerprints must differ.
`proofs/` contains all 23 full-size proofs, including uppercase, lowercase, figures,
punctuation, paragraphs at 28–32 px, and extended Latin where supplied. Three
contact sheets permit cross-family comparison; full proofs are the reading check.

These fonts are standalone regular styles with intentionally slanted designs
where named. They are not variable fonts and contain no drop caps.

## Extended verification

Run `python deep_validate.py` after the build for semantic ASCII outline round trips,
nonempty visible characters, integer-grid contour simplicity, file size limits,
embedding permissions, and unique outline design checks. The report is
`deep-validation.json`. Tested package versions are in `tested-dependencies.json`.
`visual-review.md` records the per-family proof review and the corrections made.

All 46 generated font files were byte-identical across two final full builds.
See `reproducibility.json` for the compared hashes and build method.
