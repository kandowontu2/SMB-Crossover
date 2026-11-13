# Karnov Ladder extra resource request, November13

Root approved this request in commit4c027e30, recorded in
`docs/qa/allocations/karnov-ladder-extra-1113.json`. The1178-byte measurement
below is the reviewed reservation input. The subsequent implementation update
at the end remains within the same1180-byte envelope. No feature is delivered.

This requests **556 additional code bytes**, permission to repurpose the
original27-byte Ladder object transport, and a separate32-byte private font
edit. It is a measured source proposal, not a ROM candidate or a gameplay
qualification. No new Ladder code/art has been applied to a ROM, no emulator
has run, and `build/karnov-equipment-1113` contains no generated files.

The existing624-byte code reservation is
`docs/qa/allocations/karnov-equipment-tails-1113.json`, root commit389ff135.
The exact frozen parent remains
`aa50112845d1cf70cae0924f03326647b3d2514f876c756d70b134ee44f971d1`.
Fresh known Downloads62ba7f54 is explicitly normalized through
`steve_armor_idle_1113.reverse` to this exact parent. No implicit rebase occurs.

## Proposed source layout

The original owning-source link must first reproduce all3892 bytes and the
qualified compact source. The authenticated refactor-only preimage is
`13816e9ff6ecb4d4e10d6f1fa2f9be28c683c52e570a8abb29a9f5e944457c2c`.
Original source SHA256 is
`de34c6db8c92a61b59eaf0ef66c5d96ef309e525cf64cd33a6ee0f411611ab10`;
compact source SHA256 is
`59e57a8503d42834fc88a12f8755650c177ffe2f1192c5a60a4efd6a05043592`.
Neither existing tail may ever be patched on the unrelinked parent.

| Code region, inclusive | Available | Measured adapter | Status |
| --- | ---: | ---: | --- |
| RAM3 AA1A..AC05 |492 |492 | Already reserved |
| RAM3 AF20..AFA3 |132 |131 | Already reserved |
| RAM2 CE00..CFFF |512 |511 | Requested new conditional code/copy |
| RAM2 CDD4..CDFF |44 |44 | Requested unused end of existing HUD-name lease |
| Total |1180 |1178 | Two padding bytes |

The complete measurement source SHA256 is
`9d8a1cf29c03b977323d3a9b13b1eb9047451a11b1fc99871f041cbc066272f8`.
The checker emits each assembled payload hash. The44-byte routine that aliases
native table ROM into C remains in RAM3; it never executes from the C window
being switched. The proposed C2 code is reached only from existing selected,
two-header-authenticated A3/C2 services. All37 service slots and A087/AC06/AFA4
anchors retain their addresses. No neighboring pose/options storage is used.

This is the complete **measured transport**: original8×16 growth and guards,
four original probe positions, held-Down bottom recovery, dispatcher1/grow,
2/retract and0B/rebuild, saved native metatiles, scene cleanup, original artwork
quads, viewport checks, queue checks and attribute construction/restoration.
The new body has not yet passed executable lifecycle/ABI/interrupt gates.

## Exact extra code storage and loader change

CE00..CFFF maps to physical CHR1020 bytes256..767, file2093328..2093839.
Its512-byte current zero preimage SHA256 is
`076a27c79e5ace2a3d47f9dd2e83e4ff6ea8872b3c2218f66c92b89b55f36560`.
These bytes are part of the named Karnov2048-byte combat carrier, but are
currently **not copied or granted executable runtime**. Their zero contents
alone are not the ownership proof.

The owning cold helper is ROM29 BAED, file244477. Its complete27-byte preimage:

```text
a605bd20bb8504a904e009d002a9018507e0089005a902202cbb60
```

Change only its row9 immediate at file244491 from01 to03. Row8 remains four
pages at C900; row9 grows from one page at CD00 to three pages ending CFFF.
Combat copy/verify increases1280→1792 bytes. All other11 rows, banks, register
returns, stack and map mirrors remain exact in24 executions of the actual
helper. SourceCHR1020 bytes768..1023 remain untouched. The loop still has12
rows. No loader code growth or new loader entry is required.

CDD4..CDFF maps to physical CHR1020 bytes212..255,
file2093284..2093327. Its44-byte FF preimage SHA256 is
`463d5921a6bfd5c98f6047f561495800372e627c07ce458c23b7ac164a22be51`.
The exact owning HUD-name source still emits27 bytes at CDB9..CDD3. Its
existing declared lease ends CE00. The proposed44 bytes already pass the
current cold copy/readback; no existing helper byte moves or disappears.

The all37-root owning graph covers4027 instructions. It has no direct CE00
reference or code/data entry into CDD4..CDFF. Five conservative indexed
reads could reach the region under arbitrary8-bit indices, but their actual
owning bounds are:

| Instruction | Base | Actual index bounds | Last byte |
| --- | --- | --- | --- |
| CC8B, canonical enemy bits |CD24 |0..5 |CD29 |
| DD3F, HUD packet |CD55 |0..35 |CD78 |
| CDC0, new BOMB name |CD8C |36..44 |CDB8 |
| CDC5, original names |CD2A |0..35 |CD4D |
| CD97, Down+B hint |CD4E |0..6 |CD54 |

The latter four index intervals were also observed through512 actual current
HuUi cursor/ownership fixtures. The six owning indirect sites resolve to
native block/terrain buffers below8000, the readonly A3 pose image,
the original state clear, or the pose destination. In particular **KrCopyArt
writes D000..D540,1345 bytes**. Expanding row9 to four pages would overwrite
pose data and is explicitly ruled out. Original options remain D600..DDFF.

The current cold loader first zeros/verifies all of C2, then copies/verifies
every image row, and publishes both complete headers last. The extra512 bytes
will therefore be zeroed, loaded and read back before any new C2 opcode can
be admitted. Expected PPU reads increase23064→24088; that is a prediction
pending the future actual-loader candidate test. The new feature must update
both complete cookies, reject both old headers, prove new readback faults,
and reverse every code/data/loader change exactly before native review.

## Original state and existing control/UI leases

No new persistent address outside C624..C63E is requested. The native object
packing uses C624 count/camera column, C625 world-tile X low8,
C626 world-tile X high4/bottom row4, C627 next growth-tip Y,
C628 camera page and C629..C630 eight saved metatiles. These are bytes from
the original27-byte Ladder prefix/triples, not another character's state.
R0..R7 are transient and retained at the new frame/callback boundaries.

The eight conservative indexed writer candidates are the original C534 icon
writer at DB50/58/65/6D/7E/86/8E/96. Its actual table-derived Y values2B..3D
end at C5C2, below the Ladder object. No reached direct/effectively indexed
writer touches this object. Its existing indirect writer is the original
new-life C000..C7FF clear, which deliberately resets it. Same-life scene
cleanup will cancel the old world object without restoring into a new stage.

The control/HUD source relink also fits its existing named leases:
LADDER_LOAN156/162 and SHIELD_LOAN65/65. It adds cycle option2, ownership bit4,
the text LADDER, blank reusable-stock digits and the ordinary Down+B hint.
Existing Boots/Bomb/Boomerang/Wings indices/names/icons retain their behavior.
There is no new inventory icon; the original32-byte Ladder art is for the
level object. Other existing worker leases stay within their current bounds.
Paired execution of these proposed controls remains a feature qualification gate.

## Separate32-byte private art request

Request CHR1023 glyphs2C/2D, file2096848..2096879. Current32-byte preimage
SHA256 is `8d431612acbaebd7d4b54aa4e62a6fbf1d13726073a32d07e5466343df8f8be9`.
Original donor BE/BF patterns from CHR38 have SHA256
`a695f4fc2d1211572a01a2f65aa755c008f09da2d47d466010d4ddbb905e535e`.
All32 pattern bytes and opacity will remain exact.

The corrected donor CF attribute is25: class9, **palette1**. The retained
original hardware palette gives pattern index2 color22 and index3 color02.
The proposed adaptation uses existing native BG palette2: index2 color21
(blue), index3 color0F (black). This is an explicit NES color adaptation,
**not exact donor color parity**. No global palette entry changes. Attribute
construction changes only active Ladder quadrants to palette2, derives all
other quadrants from current native metatiles, and restores the removed cell's
saved native metatile/palette.

The cells presently hold dot/chain glyphs. All256 native metatile quads have
zero2C/2D references. All512 actual current equipment-HUD fixtures emit neither
glyph. Pinned ordinary game-text strings use neither dot nor chain. Actual
X5BounceUiDispatch/X5PublishChr calls publish private page1023 during Karnov
gameplay and restore native page0 on OperMode0/2, task2 and engine5/9 fixtures;
actual KrRetire also restores the native font. The current GameLoop's
unconditional UI farcall is authenticated at file1032948, before mode work.
Thus ending punctuation is outside the private font lifetime in this source
contract. These are CPU context fixtures/source checks, not native transition
or new Ladder-art observations.

## Transaction and remaining qualification

Growth/restoration issue one quad plus attribute command (14 bytes). A full
eight-segment redraw uses two vertical pattern commands (38 bytes) plus at
most five4-byte attribute commands:58 bytes and a terminator. It requires
negative NmiDisable, a visible screen, zero control/offset and an existing
zero terminator. It defers without replacing prior commands. The current
source-color append would take58→65, within84-byte VRAM1. Later native-producer
budgets, actual NMI cycle cost, queue contention/timing and complete frame
integration still require executable tests; the transaction arithmetic alone
does not qualify those paths. No full-frame queue-safety claim is made yet.

Before candidate readiness: execute the complete grow/climb/retract/rebuild
and zero/solid/camera/life/area/pause cases, all native tile/palette quadrants,
earned-in-fixture progression, paired existing powers, exact inverse, cold
faults, all public ABI/foreign ownership and IRQ/NMI cuts. Only then request
root's native queue. No root candidate/controller or delivery file is touched.

All checks are zero-output bounded invocations of
`tools/audit/check_karnov_ladder_native_1113.py --part measure`
(or storage-plan, loader-geometry, font), using the existing
`build/karnov-equipment-1113` root, `--max-files 1 --timeout 180` and `python -B`.

## Implementation update after reservation

The next source revision uses1179 bytes:492/131/512/44 in the same four regions.
Its source SHA256 is
`61d5f1385d74500ce6670613e3edb9b591e16dc9bc12454f60e7aa0f149e8247`.
No extra address, carrier, font cell or state byte was consumed. Tip627 is the
inactive-object marker; clearing count/tip makes leftover packed coordinates
inert. This avoids redundant anchor clearing and leaves room for the following
native coordinate bridge.

Original F62B..F631 snaps the source screen coordinate to16-pixel cells at+8.
The bridge applies that same grid in native world coordinates, then subtracts
the actual camera. It replaces only the existing10-byte instruction group;
its24-byte helper keeps A/X/Y/C/V/D/I/SP and final N/Z correct. Original source
continuation F633 (host A48C) still begins with LDA source62.132352 standalone
CPU cases pass: every camera/source-X pair ×both incoming carries, plus all256
status values on representative boundaries. An aligned camera reproduces the
old snap exactly. No jump speed/height, acceleration or climbing constant changes.

The ordinary path also retains the original KrOptionsTick entry, including its
E8→0F clock transfer before the existing Bomb/timer scheduler. Whole-frame
queue budgets and the full feature lifecycle remain pending. The revision is
still source/standalone qualification; no new ROM candidate has been retained.
