# Current85 compact WWF menu repair

The six WWF colored previews now use the existing16x32 original-body menu art.
Full-size source poses previously overlapped the bottom gray roster row and,
for some wrestlers, the selected name. Their lives/gameplay graphics stay full
size. The source change fits the same234-byte routine, alters193 ROM bytes,
keeps all public entry addresses and adds no RAM or stack slots.

CPU checks cover90 identities,720 Start/A cases,8192 X/flag combinations and
exact whole-application outputs for84 non-WWF contexts. The six WWF changes are
compared against the existing compact art pipeline with explicit draw-local
metadata differences and unchanged persistent identity/health/gear state.

The native sweep covers124 transitions/2480 observed frames, requiring an
unchanged sampled gray roster, exact heading and zero visible PPUMASK writes.
All six wrestlers then start through the real menu into their original lives
and gameplay display for30 Main updates each, with actual ISR-return checks.
This is a menu regression qualification, not another full-stage test.

Downloads was replaced directly, with no backup. Playable count remains85.
Original-source character components and private Karnov opening remain separate;
they are not unlocked by this delivery. Exact hashes/scopes are in handoff.json.
