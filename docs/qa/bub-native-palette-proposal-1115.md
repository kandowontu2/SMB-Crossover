# Bub native enemy palette ownership proposal

Research parent is exact delivered40a
`40a11ffb8452c3b54caef56ddd5912e2bdda2c276545f20a589baa053de4d20e`.
This is a read-only source proposal. No changed image, CPU overlay, native run
or installation has been created by this helper. Root owns those gates.

Actual21455 native replay completes the functional M/F route but exposes a
green/pink/white opening Goomba. Main135/frame601: OAM A2/A4, attributes67,
physical page17 offsets544/576; Bub also uses palette3. Observed P3 is
0F/2A/26/30. The G PNG is
`c3b661abe29ae04d9dac2b629478bca3a9429c10e02adc17229a1d164be17631`.
The earlier item-only pictures did not include an enemy and do not contradict
this failure. See root's `bub-natural-flower-native-1115.md` for native scope.

`audit_bub_palette_40a_1115.metadata(raw40a)` authenticates actual bytes and
returns the four proposed logical spans; it never constructs an image.
`cold_observe(raw40a, identity)` runs the real compiled menu Select/Start and
ordinary completed Main/NMI. Bound output root is absent
`build/bub-palette-audit-40a-1115`, max1/600s, zero files.

Read-only cold receipt
`fd0678f6c3a03da16e14eb5be3d4139a5e29963be4df6026dd8f00c4d74a6c00`
shows eight returned Main snapshots per identity, healthy40/176/lives2:
Bub's original Pair inputs3/3 and P3=0F/2A/26/30; Bob's inputs0/0,
P0=22/2C/23/30 and correct native P3=0F/0F/36/17. Bub's helper packet is
`3F1D032A2630`; Bob's is already `3F11032C2330`. Thus Bob must not receive a
blanket palette remap.

The original World SMB ROM SHA256 is
`0b3d9e1f01ed1668205bab34d6c82b0e281456e137352e4f36a9b2cfa3b66dea`.
Its four complete36-byte native palette commands equal current40a commands:
Water file3252/current1032546, Ground3288/1032582,
Underground3324/1032618, Castle3360/1032654. Sprite P3 values are respectively
0F/0F/30/10, 0F/0F/36/17, 0F/0C/3C/1C and 0F/00/30/10. The observed Goomba
patterns independently equal original8x8 tiles: page17 offset544 comprises
original file34576+34608; offset576 comprises34592+34624. The corresponding
32-byte SHA256 values are86cc81eb… ande2b6e796…. This is correct art with a
wrong palette, not a CHR allocation fault.

Original attributes are gameplay state. Actual source DF14 atB003 masks
private sprite attr with3 and sets a captured-enemy owner bit; DA30 atAA84
shifts the attr to select input C030 versus C044. Their current byte strings
are `B902C12903F008BD02C009019D` and
`B902C14AAD30C0B003AD44C02940`. Changing original Bub constants3→0 would
change that owner/input contract. The proposal leaves every original private
OAM byte and every attribute writer untouched.

The visual boundary is `BbNativePair` BDC9..BE45. Its exact125-byte hash is
`f8c250dbe5101ea932eede2ba92f53016dff5a262618a4a0801bcf05e2124761`.
There are only two direct callers, BD5C for the selected original actor and
BD77 for the private proxy/bubble scan. The selected actor is X2E/Y0 or
X42/Y8; proxy records X68..7C/Y10..38 require original trapped flag16;
active original bubbles X88..C0/Y88..F8 are rendered by the same Pair.
The separate native victim remains a native actor; the private proxy pair
supplies its surrounding original bubble art. No native actor OAM, shared
palette command, tile, position, hit box, native CHR publisher or other
character's renderer is edited.

The source census authenticates all26 explicit original C102/C106 indexed
attribute stores against current instructions. Initial bulk sprite-table
copies, native constructor/facing, original death43/00, damage/grace palette
switches, animation masks/flips, fresh and aging bubbles, native trapped-ring
assignment and later blinking palette1 writes all remain original. Source
DA30/DF14 continues to read original values; the mapper writes no original
state. It changes only the two C3E6/C3E2 pose-copy values. All upper6 bits,
including flip/priority/software flags, remain equal; palettes0/1/2 remain
equal. Bob/nonzero identity returns every attribute byte unchanged.

MetaspriteRenderLoop reads that temporary pose and combines R3=0, then masks
software bits2/3 with F3 before hardware OAM. Private Draw never calls the
generic outline compositor; its fixed two8x16-sprite pose and software flags
are unchanged. Sprite-bank0 uses actual art441; world native windows keep16/17.
The color helper writes the actual area backdrop and only its six-byte RGB
packet, preserving registers/R0. Moving Bub's packet address1D→11 leaves the
four native area palette3 commands in control. Bob's existing P0 packet,
packet length/admission, menu/status names, water backdrop logic and art bytes
remain unchanged. Fresh-start, warm scene, injury/Star, busy queue and foreign
admission still need source candidate regression after allocation.

The older retired source interval B261..B539 is partly reused and is not a
blanket spare grant. B300 is live deferred-head code and was rejected during
research without mounting it. v55 endsB320; v87 initial-tier adds10 bytes to
B32A; the frozen delivered empty-loop source996003a0… consumes270 more to
B438. Its tracked declaration records258 remaining FF bytes B438..B539.
Actual40a authenticates all258 and has no two-byte word anywhere in the
private8KB image targeting proposed B438..B454; no published/private source
label enters it. The complete current code hash is
`dc2ec9d798163e5ff352ae913d1e77f4d582f7a3391c713103c695f2e098da53`.
This combines source ownership/declarations with current preimages; FF alone
is not the allocation argument.

Proposed36 logical bytes, no new ROM/CHR/RAM or source growth:

| Runtime span | File offset | Exact old → new |
| --- | ---: | --- |
| Private3 BDFA..BDFC |1731082|`B902C1` → `203EB4`|
| Private3 BE00..BE02 |1731088|`B906C1` → `2038B4`|
| Private3 B438..B454 |1499208|29 FF → `B906C14C41B4B902C148AD00C3D00C684829034903D0046829FC606860`|
| Helper2 D3BB |1501131|`1D` → `11`|

The29-byte routine has two load entries, a common identity check and one
conditional3→0 mask. It uses no ADC/SBC/CMP/shift, so C/V/D/I are untouched;
X/Y are untouched, stack is balanced, and NZ describes the returned byte as
for the original LDA. Each load hook replaces exactly one LDA with JSR;
source and pose addresses/public Pair entry remain fixed. The two old live
head/empty-loop ranges and all other instructions are preserved. Required
existing owner cookie re-encoding is additional metadata, not spare code.
The mapper leaves229 declared spare bytes; those are not leased to anything
else by this proposal.

Root review/allocation is required before composing or mounting. Then finite
all-byte/all-status identity ABI, all source owner/input and private-OAM
parity, complete palette lifecycle/busy queue/cold/foreign, reached IRQ/busy
NMI and ordinary M/F/L regressions must qualify. Native gates should show
the real opening Goomba retains original palette3 while Bub/bubbles use P0,
Bob art/colors remain unchanged, and real item/ability inputs still function.
Natural Star and extended visual/audio/performance coverage remain open.
