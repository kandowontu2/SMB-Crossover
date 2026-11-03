# Sonic SMS terrain component progress

Private components use the exact reproduced original Master System ROM,
SHA-256 `6ad738965ece231427ee046b9905cfee470d5c01220afdd934da4673e4a2458b`.
They have no host allocation, character-select admission or nightly change.

V16 compares the original resolved horizontal and vertical contact
instructions against compiled 6502 code in 5,120 cases. Position fractions,
signed offsets, absent-shape sentinel, velocity resets, source slide tables
and support flags match. The cumulative component is 1,559 bytes. Receipt:
`build/sonic-sms-contact-1102-v16/receipt.json`.

V17 adds the original four directional shape tables and probe selection.
All eight original zones use flags 0 through 46. The tables reduce
losslessly to 46 distinct 32-byte shapes (1,472 bytes); cumulative code and
data total 3,529 bytes. All 47 flags, 32 sample rows and both velocity signs,
plus 4,096 carry/mask fixtures, pass: 10,112 cases. Lookup takes 59–109 CPU
cycles. Receipt: `build/sonic-sms-shapes-1102-v17/receipt.json`.

V17 compares actual donor pointer indirection rather than executing the
whole original collision dispatcher. Its caller still supplies the original
zone flag. Mapping native SMB terrain to those probes, composing full Main,
animation, rendering, audio, lifecycle and resource admission remain open.
These isolated checks do not establish playable Sonic or a stage clear.

V18 connects each directional lookup to its contact leaf and executes X
followed by Y in 4,096 cases (8,192 axis calls). The original lookup data and
original contact instructions produce matching coordinates, velocities and
flags, including X-slide effects on the subsequent Y probe. Each axis costs
90–343 cycles. This retains the same 3,529-byte component and still requires
caller-supplied world flags. Receipt:
`build/sonic-sms-shape-contacts-1102-v18/receipt.json`.

V19 adds the original physics selector and Down-to-roll entry. Actual donor
instructions select normal, underwater, speed-shoes or airborne special
coefficients, with the original precedence, tempo restoration and phased
shoes timer. The compiled selector and original roll admission pass 16,384
cases covering every player flag and the mode/timer boundaries. Cumulative
code/data is 3,774 bytes; the selector plus roll entry costs 153–230 cycles.
Receipt: `build/sonic-sms-physics-selection-1102-v19/receipt.json`.
Tempo fields and sound-event requests are private fixture outputs, not a
working NES audio driver. Full Main and native admission remain incomplete.

V20 adds the original animation streams, frame reset on animation change,
loop decoding and ordinary/walking/rolling frame advancement. All 25 valid
streams and each frame through their loop marker pass 2,382 comparisons
against original instructions; 231 invalid animation indices reject. The
donor's empty animation 03 would loop forever and is excluded from valid
gameplay fixtures. Changing animation resets the frame without resetting
the speed subframe, as in the donor. Combined read/advance takes 100–189
cycles; cumulative private code/data is 4,356 bytes.
`build/sonic-sms-animation-player-1102-v20/receipt.json` records the scope.
Main still must select the pose and call these routines at the original
point relative to velocity clamping. CHR conversion, OAM and audio are open.

V21 decodes all 42 original sprite frames in both facings and verifies each
against the exact ROM bytes. Three disjoint NES 2bpp layers reconstruct all
64,512 source pixels and seven visible color indices. Deduplicated data is
25,056 bytes (783 8×16 pairs). The original-color atlas was inspected.
Only 29 of the 42 facing pairs are exact mirrors; the original left/right
art must be retained where they differ. Several effect images are only
valid under the original Main's facing rules.

This is a palette/resource proposal, not an admitted renderer. Preserving
all colors this way needs three palette groups and as many as nine sprites
on one scanline (17 total body sprites). Native enemy-palette coexistence,
CHR mapping and overflow handling need resolution before use in the game.
Receipt: `build/sonic-sms-sprite-layers-1102-v21/receipt.json`.

V22 translates the original post-velocity pose choice and hard velocity/top
limits. Actual donor instructions match in 5,632 pose cases and 66,560 cap
cases, including every unsigned Y coordinate and all velocity pixel bytes.
The original pose test continues only when the absolute fractional/pixel
word is strictly greater than `0100`; airborne rolling and the `85` flag
mask retain their precedence. The velocity caps change only the pixel
bytes, preserving fractions and high bytes. The top clamp preserves the
fractional Y coordinate. These two leaves add 115 bytes, bringing the
private component to 4,471 bytes. Receipt:
`build/sonic-sms-post-velocity-1102-v22/receipt.json`.

This still does not compose the complete original Main or establish its
call order in the host. Native world queries, lifecycle, rendering, audio
and allocation remain open; no Sonic roster admission is claimed.
