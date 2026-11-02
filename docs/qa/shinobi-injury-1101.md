# Shinobi injury source component

Recovered donor entry `$DA1B..DA5D` and its 26-byte movement script
`$DA5E..DA77`. The relocated initializer and script assemble to 93 bytes.
The source sets state 16, pose 6, direction-dependent knockback, and resets
the original movement interpreter. It is not a generic SMB knockback routine.

`tools/audit/prepare_shinobi_injury_1101_v3.py` compares the original ROM
instructions against assembled relocated instructions for all 256 facing-byte
values. All cases pass: callback order, actor RAM, registers, flags and stack,
after normalizing the relocated script pointer. The three animator/interpreter
calls are trapped at matching boundaries; this does not test their behavior.
Receipt: `build/shinobi-injury-1101-v3/result.json`.

Reusable assembly: `tools/reference/shinobi_injury_1101_v3.inc`.
The donor is SHA256
`24e1e425b84776ab2116b4dd1a85545f78e9a507caa8367a490cc77adab46874`.

Still required: injury/death pose graphics, native damage/death integration,
remaining external source callbacks, menu admission and controller-only 1-1.
This component is not installed in the nightly and does not unlock Shinobi.
The installed Metal Storm nightly remains unchanged.

## Injury/death graphics recovery

`tools/audit/prepare_shinobi_hurt_art_1101_v4.py` now executes the donor's
animator and OAM emitter for poses 6 and 7, both facings. All six pose/frame/
facing packets convert to native 8x16 pairs with identical opaque pixels,
palette indices and sprite priority. Eleven new pairs (352 bytes) append to
the existing 96-pair atlas. The output retains the original OAM and converted
rows in `build/shinobi-hurt-art-1101-v4/packets.json`; additional patterns are
in `additional-art.chr`, with a hash-bound `result.json`.

These are real source poses, not replacement drawings. The converter has not
yet assigned a fourth hardware sprite window or expanded metadata. Do not
publish pair indices 96..106 through the existing three-page setup. The old
metadata uses 1696/2048 bytes, leaving exactly 352 bytes before adding these
poses; metadata compaction or another verified allocation is required.

## Implemented layout successor

`prepare_shinobi_hurt_layout_1101_v5.py` resolves the storage issue above by
moving the unchanged 256-byte terrain-attribute table into the kernel tail.
The kernel, including the original injury initializer/script, is 7160/7168
bytes. Expanded metadata is 1544 bytes; the additional art occupies
`D6A0..D800`, the last 352 bytes of existing physical CHR page 517. New
descriptors use pairs 117..127, leaving the metadata portion unaddressed.
The fourth sprite window must therefore publish page 517.

All 58 existing and new pose/frame/facing cases pass through the actual native
metasprite renderer in CPU fixtures, with original pixels, priority and palette
indices preserved. The private cartridge also passes actual PRG-resident cold/
warm loader, 32 header corruption and retirement tests. No new resource grant
or additional CHR page was needed.

Candidate: `build/shinobi-hurt-layout-1101-v5/candidate.nes`, SHA256
`f6658fb7532dc87b1583da8f388fd8e3f1094b2bbd71ea51a5c611bb37364db9`.
This supersedes the v2 private placement. Hardware CHR publication and gameplay
hooks are still absent; this is not an unlocked or installed nightly.
