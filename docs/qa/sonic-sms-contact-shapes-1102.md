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
