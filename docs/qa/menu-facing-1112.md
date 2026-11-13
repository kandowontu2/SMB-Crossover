# Right-facing roster menu — November 12

The in-memory proposal changes three colored portraits and four shared grid
icons. It preserves the other98 colored portraits and the other28 grid icons
across all101 named Select identities in the current32-slot menu.

Input Downloads SHA-256:
`cebb0ae64b4e6cc92e473a239cb8fd4011d54cfd5e6814013a3afbd2de2bf7d7`.
Proposed image SHA-256:
`b2b0cae302986edf490f05b06ecdebff365ab930a3ae72911e11dbc3eb52a145`.
The helper did not write or deliver a ROM or patch, and did not run Mesen.

## Affected identities

Colored preview corrections: Zelda1 **Link**, **Sonic**, **Super Sonic**.
Their previous portraits contain left-facing pixels despite the menu's native
PlayerFacingDir1 initialization. Each revised portrait is the exact complete
horizontal reflection, preserving colors, opacity, dimensions and cell count.
Zelda2 Link's already right-facing portrait is unchanged.

Shared gray grid icons:

| Menu slot | All Select identities using the corrected icon |
| ---: | --- |
| 14 | Little Mac; Doc Louis; Mike Tyson |
| 16 | SMB3 Mario; SMB3 Luigi; SMB3 Toad; SMB3 Peach |
| 24 | SMB2 Mario; SMB2 Luigi; SMB2 Toad; SMB2 Peach; Imajin; Lina; Papa; Mama |
| 26 | SMB3 Bowser; SMB1 Bowser |

These are17 identity appearances sharing four icons. The selected gray icon
does not change to a separate alternate's art in the present menu; the audit
still checks its exact pixels at every Select state. Each changed icon is the
complete16x24 reflection. No letter, border, cursor, nametable byte or other
icon is changed.

The native Donkey Kong/Donkey Kong Jr portraits and Mike Tyson's enlarged
head are frontal and have no meaningful left/right side profile. They remain
unchanged. FF Fighter's source standing pose is a frontal/three-quarter pose;
its existing source pose is retained. The audit does not invent a side-facing
pose by reflecting an approximately symmetric front view. Goku already uses
the source-qualified right-facing standing record from the earlier portrait
repair and is unchanged.

## Source and byte ownership

Composable entry point:

```python
import compose_menu_facing_1112 as Facing
candidate, info = Facing.proposal(raw)
# info['edits']: (file_offset, exact_preimage, replacement) triples
```

The function authenticates each local preimage, so it can compose over later
disjoint Prince/Metal updates without undoing those updates or rebuilding an
old whole-ROM parent. Root must bind the resulting combined hash to its own
native qualification and delivery.

`tools/reference/menu_facing_1112.s` replaces the existing58-byte native
intermediate/lives setup prefix at PRG3 B345–B37E. It factors duplicate
selected-character loads and constant loads inside that same source-owned
prefix. Zelda1 Link receives facing2 before its original portrait selector;
other identities retain facing1, including Zelda2 Link. The original selector
tail atB37F, the independent Getsu status packet atB3DD and the old constant
table atB3EC are untouched. No gameplay movement or combat routine is hooked.

The same source supplies one3-byte instruction at PRG9 BC94 in the existing
Sonic-only static portrait leaf. `ASL PlayerFacingDir` replaces a redundant
ReloadCHRBank store: the sole intermediate caller already incremented that
reload request. The native four-cell box then selects its mirrored record.
Both Sonic forms retain their existing form-specific CHR page and palette.
The leaf restores processor flags after this instruction. Normal Sonic
gameplay code and CHR224/226 pixels are unchanged.

The four gray icons use24 unique8x8 menu tiles:139–144,151–156,194–199,
205–210. The actual native BuildScreen and NMI map the menu background to
physical CHR4–7. The recipe proves that every reference to those tile IDs in
the complete960-cell menu nametable belongs to the four targeted icons, and
rejects font/reserved IDs. It swaps each icon's left/right tile payloads and
reverses each row's bits, retaining all tile IDs and nametable bytes. Its
ownership follows the dedicated menu atlas producer
`tools/audit/build_full_roster_menu_v1.py`, which reserves64–251 for portraits
and keeps the alphabet below64. No new tile or memory allocation is made.

Total edited source envelopes:445 bytes (58 prefix +3 Sonic +384 menu CHR).
The checked assembly source SHA-256 is
`f4d982169fb25a8969bd5cca7ac39f3fb4017bff898c8d1ef87e9792b3ef1263`.
Existing shared source files were not edited; the scoped recipe and assembly
are the reviewable source for these current-ROM changes.

## Verification and limits

`check_menu_facing_1112.py` builds the real native menu background, resolves
each slot, walks its actual Select cycle, runs the real portrait renderer and
NMI, and reconstructs pixels from OAM, published physical CHR and the palette.
The main-loop NmiDisable/FamilyMainCommit guard is restored before each next
menu input. The audit enumerates101 names; the unused raw slot32 is excluded.

`compose_menu_facing_1112.py` compares all101 before/after portrait images and
all101 selected-icon images. The three colored changes and17 shared-icon
appearances must be exact horizontal reflections; every other image must be
byte-identical, including size. Names, selected owner IDs and cycle order
also match.332 NMI cuts and332 IRQ cuts pass at every reached instruction in
the new setup prefix and the Sonic instruction, across menu and lives modes.
Live player fields, registers, stack and bank mappings survive.

The public `DrawSelectionPreview` call also matches incoming/outgoing A/X/Y/P
and minimum stack depth in404 old/new comparisons: all101 identities at four
incoming flag sets. This includes the three deliberately reflected portraits.

The optional native1-1 startup comparison passed for Link, Sonic and Super
Sonic. Each starts gameplay facing1 and matches its unpatched parent through
60 ordinary opening updates, including all60 OAM DMA inputs and published
CHR maps. The reflected menu/lives facing does not leak into those starts.
The first attempted startup fixture lacked a scoped Continue label in the
compact symbol bundle; the final fixture reads only that label from the
retained, hash-pinned Kirby authority and authenticates its current eight
entry bytes. No source or debug tree was restored.

Root owns actual Mesen review and any publication. The unrelated active
ADOFAI emulator was left untouched. Root separately reported that its combined
Prince-sword/menu image passed a complete physical Prince1-1 replay; that
result is root-owned and is not a helper claim of full-roster gameplay QA.

Root replaced the initial inspection sheet with the corrected combinedc5ce8c
candidate sheet at `build/menu-facing-1112/roster.png`, one CPU-derived PNG,
and visually reviewed all101 identities. Directional silhouettes and previews
face right; intrinsically front-facing portraits remain front-facing.
No image sequence, video, emulator capture forest, ROM
candidate, backup or patch file was created. All tests used the bounded
runner with `--output build/menu-facing-1112 --resume --max-files 1` after the
single sheet existed. The comparison and interruption tests generate zero
additional files.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/menu-facing-1112 --resume --max-files 1 --timeout 180 -- python -B tools/audit/compose_menu_facing_1112.py --gameplay
```
