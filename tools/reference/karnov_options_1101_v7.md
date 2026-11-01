# Karnov options source component, v7

This component has no granted code/CHR/SRAM lease and has not been linked into
the host or tested in Mesen. The complete source component is1701bytes. The
additional3947bytes in its test image are the existing original actor/weapon
fixtures, not another production implementation.

Recovered source includes fixed-bank EAA7..EDB6, all nine original activation
and selection branches, bank12 ADA8..AE32 effect scheduling, original ownership
test C28C..C29C, BCD decrement CF9A..CFB9, effect enqueue C5A0..C5BA, and the
private donor HUD updater C534..C59F. The1107 original island bytes reproduce
the donor exactly. Original dispatcher words and mask lookup bytes are
relocated explicitly. Donor hash:
`0d49c1120fc13ead1efe4429f7cbb4f01b90e2486c66661c46e922dda6dc830a`.

Only Boots0, Boomerang3, and Wings7 are exposed by the proposed SMB controls.
Bomb, Ladder, Clapper, Glasses, Mask, and Shield remain unsupported host
equipment. Their recovered source branches are proof/reference material,
not claims of working native attacks, objects, collision or graphics.

| Control | Proposed host behavior |
| --- | --- |
| A | Original jump |
| B | Original fire/active source weapon |
| Select, fresh press | Cycle owned Boots, Boomerang, Wings, then NONE |
| Down + fresh B | Activate the selected supported option using its original leaf |

Cycling grants nothing and consumes no stock. NONE means no option selected;
already active original effects continue until their original expiry/return.
An unsupported or unowned selection leaves ordinary B live. A recognized
activation consumes its B edge even when the original active/busy guard rejects
another use. The returned C means input handled, not activation successful.

The existing bit converter currently retains only source21 bits0/1. The pure
`transform_terrain()` proposal removes that mask, calls KrOptionsControls
before KrSourceFrame, then calls KrOptionsTick after KrSourceWeapons and before
the existing INC E8. It adds four net bytes to that owning kernel and requires
two new imports. Its256×256 previous/current edge combinations are checked in
both original and proposed assembled converters. Source button bits are
Select04, B02, Down20; host held bytes retain their ordinary layout.

The exact original effect queue is important. C5A0 puts jobs into063F..064E;
ADA8 decrements them on source0F multiples of64. Boots schedule a warning at
448updates and removal at640. Wings warn at768 and end at960. The original
NMI increments0F at C1FC; this proposal copies the accepted source E8 epoch
into0F for the scheduler. Thus effects pause with accepted source updates.
This is an explicit host clock adaptation, not a claim of identical elapsed
wall time during lag/pause. Raw KrOptionsNativeTimers accepts the original0F
directly if a later owning adapter supplies a different clock.

The production entry points KrOptionsControls and KrOptionsTick consume AXY/P.
They preserve the actual borrowed host zero-page pair3/4 through the existing
KrSaved0/1 at C7FE/C7FF. Calls must be sequential with KrSourceFrame/Weapons,
never nested inside those routines' saved-pointer frame. One new transient
byte C865 holds the consumed pressed-input byte. It does not overlap combat
C840..C85F/C868..C879 or pickups C860..C864. There is no NMI0..2 use.

The owning link supplies KrState, KrPointer, KrSaved0/1 and callbacks
KrOptionSound/KrOptionUnsupportedScene. Source sound requests were isolated
identically in proof; a real callback must meet the existing source sound
callback register contract. The unsupported scene callback is unreachable
through the production0/3/7 whitelist. Donor HUD writes target private state;
native icons, stock counters and selection graphics are still required.

The final differential includes13073 original/ported pairs and26146 engine
executions, plus131072 assembled converter cases,1280 earned-selection cases,
12 mapped activations,308 ordinary/unsupported-input cases and18 clock mapping
pairs. Three1100-update sequences exercise original jump, upward/downward
flight, boomerang firing/return, warnings and expiry. The observed boomerang
returned at update145 and restored the saved double-fireball state; that return
time depends on this declared motion fixture. Boots rise88pixels and wings
move upward20pixels in their respective fixtures.

Returned A/X and N/Z differences are accepted only when the exact last writer
is the original inline dispatch pointer load/TAX, the translated writer is its
corresponding instruction, and both pointer targets/bytes match the recovered
label map. All other flags, Y, source state and callbacks remain compared.
Declared scratch boundaries are original58/59, stack100..1FF, and private saved
pointer7FE/7FF. Minimum standalone source-test SP214 is not an actual host Main
interrupt reserve result. Owning relink, resource allocation, actual Main/ISR,
native controls/graphics/audio, and complete campaign testing remain gates.

The proposed hook input comes from the exact frozen0162287e nightly source
packet. No mutable current integration build, whole ROM, dependency tree or
emulator capture is copied into this component.
