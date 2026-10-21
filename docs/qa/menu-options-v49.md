# Title menu and behavior options

The user subsequently renamed the behavior values to EASY and HARD. Those
labels are preserved. The request to put all original character behaviors
under Easy is being implemented privately; see [current scope and
evidence](easy-hard-legacy-v49.md). The S2 evidence below describes the earlier
ordinary-stomp option, not completed full legacy character behavior.

The working update adds START and OPTIONS to the static title. START opens the
existing character grid. OPTIONS contains PLAYER SHADOWS and BEHAVIOR. There is
no setting row or hidden setting focus on character select.

Power-on defaults are shadows OFF and behavior 1.0. Up/Down chooses a menu row;
A or Start confirms on the title. In Options, Left/Right, A, Start or Select
changes the highlighted setting, and B returns. Preferences survive character
selection, gameplay, deaths and area changes until reset.

Behavior 1.0 enables ordinary descending stomps for the roster. Behavior 2.02
retains the previous character-specific ordinary contact rules. The setting
does not replace character movement physics. Paid kicks, Screw Attack, pogo,
Jump Slash and Link's thrust keep their existing priority; side contact,
underwater contact and protected hazards retain their existing rules.

Both mapper builds use the same nine-byte policy gate and one appended SRAM
byte. Existing RAM addresses, graphics banks, DPCM data and the previously
validated Sophia optimization are preserved. Mega Man and Samus now consume
the native stomp sound cue through their existing hit-effect dispatchers.

The immutable candidate is
`build/verification/root49-menu-options-private-s2/report.json`. Native ordinary
controller UI checks pass on MMC3 and MMC5: 31 sequential checks, 2,691 frames,
no emulated memory writes, no title gameplay or attract demo, actual PPU text,
edge-triggered settings, defaults/persistence, alternates, outline previews,
normal launch and movement. Real screenshots of title, both option values,
character select and gameplay are retained beside each UI result. Title,
Options and character select were visually inspected.

The original UI fixture's HUD assertion also covered native setup before menu
ownership. Its failure is retained. The additive fixture records the native
setup flag increment and checks the actual menu clear; every stable-menu HUD,
controller, PPU and gameplay assertion remains in place.

All 16 ordinary-contact groups pass across both maps and modes: 688 seeded
arenas per mapper cover all 14 identities, their power states/facings, native
Goomba/Koopa bounce, score, actual sound-effect dispatch, side injury, protected
hazards and swimming controls. All 32 protected-attack groups also pass,
including paid last-energy kicks, armor, hostile projectiles, shell kicks,
Screw Attack, Jump Slash, Link thrust, pogo and frozen-enemy contacts. The
initial generic high-ID21 arena never entered the ordinary body handler; that
setup failure is retained separately. Its compiled exclusion and flame pipeline
remain literal to R; protected projectile21 contact is checked independently.

Sixteen targeted regression checks pass on the final fixture migration. They
cover genuine front-end defaults/navigation, all previews' outline filtering
and colored pixels, persistence through death, source2.02 ordinary contact,
protected spin contact and the read-only mode-aware route audit. Original
source oracles/goldens remain unchanged. The separate integrated optimization
R passes the full original 761-case suite and both native performance checks.

The aggregate is `build/verification/root49-menu-validation-s2.json`. The
working ROMs are rebuilt as checkpoint `roster-audit-v49-menu-options-s2`, with
ROM and labels required to match the tested candidate exactly. These component
checks do not constitute complete level playthroughs or PCM audio review.
The broader roster and final recording work remains open.
