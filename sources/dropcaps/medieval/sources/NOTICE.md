# Initial artwork

Only individual SVG illustrations are included: there are no font programs in this package.
Each artwork is cropped to its ink bounds. `initials.css` contains a conservative right-edge
contour sampled from the illustration; the text remains selectable in its original order.

| Volume | Artwork set |
|---|---|
| Shadow | Yinit |
| Claw | Goudy Initialen |
| Sword | Royal Initialen |
| Citadel | Gotische Initialen |
| Urth | Art Nouveau Initialen |

Yinit: Yannis Haralambous, historical ornamental initials. CTAN's yinit / yinit-otf
packages document the original and conversion: https://ctan.org/pkg/yinit and
https://ctan.org/pkg/yinit-otf .

The other four designs are rendered from the CTAN `initials` collection, digitised by
Dieter Steffmann / Typographer Mediengestaltung. Copyright notices in the originals:
Goudy Initialen, Gotische Initialen and Art Nouveau Initialen (c) 2000;
Royal Initialen (c) 1999. The collection README records the designer's permission
under the LaTeX Project Public License: https://ctan.org/tex-archive/fonts/initials .
The Goudy notice credits the underlying floriated designs to Frederic W. Goudy.
These are rendered illustrations, not modified or redistributed font programs.

The original five scene-divider SVG motifs are new geometric ornaments for this edition.
They are decorative choices, not assertions about the source book's symbolism.

## Long Sun and Short Sun alphabets

The seven volume-specific alphabets now use complete decorative letter designs from
CTAN’s `initials` collection, rather than plain type surrounded by drawn borders.

| Volume | Artwork set | Character |
|---|---|---|
| Nightside | Eileen Caps Regular | Light letters and curling vines in a dark engraved panel |
| Lake | Elzevier Caps | Floral capitals with open, intertwining strokes |
| Caldé | Carrick Caps | Dense ribbon interlace and insular capitals |
| Exodus | Rothenburg Decorative | Blackletter with fine pen flourishes |
| On Blue’s Waters | Nouveau Drop Caps | Curving light letters and leafy stems in dark panels |
| In Green’s Jungles | Acorn Initials | Outlined capitals against engraved oak foliage |
| Return to the Whorl | Morris Initialen | Bold medieval letters interwoven with leaves |

Dieter Steffmann / Typographer Mediengestaltung digitised these designs. The source
notices credit Eileen Caps to David Rakowski (1992), and Elzevier Caps to David
Rakowski’s EPS art. The remaining notices and exact source-file hashes are recorded
in `decorated-initials.json`.

The [CTAN archive](https://mirrors.ctan.org/fonts/initials.zip) includes the author’s
permission to redistribute or modify the collection under the LaTeX Project Public
License. A verbatim UTF-8 copy of that permission and source inventory is retained
in `CTAN-initials-README.txt`; the LPPL text is in `LPPL.txt`. These assets are SVG
illustrations exported from glyph outlines, with ink-bounded viewports. They are
not font programs, and do not download or require a font at runtime.

Rebuild with `tools/build_decorated_initials.py --source-dir /path/to/initials` after
extracting the CTAN archive. Build dependencies are FontTools, CairoSVG, and Pillow.
The tool updates only the seven listed families and their contour rules; the five
New Sun families are preserved. The choices are editorial decoration, not claims
about the books’ symbolism.

The seven existing Long/Short Sun scene-divider motifs remain original drawings
for this edition and are separate from these replacement initial alphabets.
