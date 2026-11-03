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
