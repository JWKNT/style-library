# Style Library

[Open the library](https://jehlp.net/style-library/).

The library contains 100 custom font faces and 1,148 SVG icons. Each font has a TTF file and a WOFF2 file.

## Font sources and licenses

The original ten fonts remain unchanged. The added fonts include original designs and modified open-license fonts.
The new designs change glyph outlines and spacing. They are not renamed copies of their sources.

See `data/fonts.json` for each face’s source, license, and design changes.
The full source fonts, notices, build scripts, and design records are in `sources/fonts/`.
Keep the applicable notices when you distribute the fonts.

- `serif/`: 22 text, editorial, display, and slab-serif faces
- `sans/`: 23 humanist, geometric, and grotesque sans-serif faces
- `mono/`: 22 fixed-width faces with distinct coding characters
- `display/`: 9 calligraphic derivatives and 14 original display faces

These are first-release single-style fonts. Some named faces have italic outlines.
The inherited character sets have not been checked in every language or application.

## Build

Use Python 3 with `fonttools`, `Pillow`, `brotli`, `numpy`, and `shapely`.
Run each group’s `build.py` or `build_fonts.py` in `sources/fonts/`.
Each script uses its bundled sources and writes font files, proof images, and validation records.
The group README files give the exact commands and limits.

The public TTF files are in `assets/Fonts/`. The WOFF2 files are in `assets/Webfonts/`.
Update `data/fonts.json` after you add or replace files.
Run `python tools/build-fonts-page.py` to build the font previews and CSS.
Run `python tools/build-icons.py` only when the icon manifest changes.

## Checks

Run `npm test` for asset, preservation, and interface behavior checks.
Run `python tools/validate-fonts.py` for cmap, outline, bounds, file-format, and raster checks.

The page loads a webfont when its preview approaches the viewport.
The shared preview field also updates fonts that have not loaded yet.
The original font files and complete icon wall have byte-preservation tests.

Actual-font proof sheets are in `assets/Specimens/`.
