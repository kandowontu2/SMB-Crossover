# Karnov room initialization — delivery qualification

Parent ROM SHA256:
`65ee94ca9ac6e1b5ad44303d08f76ecbc175a88232c82ef8c32712edf150a643`.
Candidate ROM SHA256:
`a3c5fa63872fbb3103ae57d9748fef233e8b2273e26d985aa4006b2492d81b8a`.
Matching IPS SHA256:
`57b84a6d2cf38f3ff2e8fc7057b03d2d3ab81602906fbe256612c9972a322827`,
2,099,506 bytes. In-memory patch reconstruction equals the candidate;
the inverse recovers the exact installed parent without a backup file.

The same-life room constructor clears the original jump timers. Its
right-facing branch previously kept the old movement selector, including
rising selector8 after a completed jump. Starting 1-2 therefore combined
selector8 with timer0, underflowed the timer and read invalid motion
values. The source-sized12-byte facing span at B0D4 now stores selector0
for right or80 for left before publishing. Weapons, gear, stock and
equipment cycle are retained. With the two owner cookies,29 bytes change;
no allocation grows and all other character bytes remain identical.

## Native negative and positive

The parent dies on actual 1-2 entry even with genuinely neutral input.
It reaches active engine8 at X40/Y48, then jumps through Y44,11 and75,
eventually native highY2. Death writer is E743, SP236, input0. Receipt
`80dbed86aa36db1bd042e9c2389d03c523469d1e5fae9e1aa25226a5fd3c1cf4`,
controller `7a880eccf13382d524dab4d4535a9917b50f514aa62c31cbaa45446545af059d`.
An earlier supposed neutral test used the wrong AreaType constant (water0
instead of underground2); it did not qualify neutral entry.

The candidate passes the same ordinary-input natural route in Mesen:
first mushroom upgrades the shot, flower upgrades to triple shot, full
non-shortcut1-1 clears, 1-2 starts safely, and its first mature flower
grants Boots (cycle1, ownership1, selected option0). Final X163/Y96,
health0 (full), both lives, active engine8. No game state writes or cheats.

- Physical frames9781; accepted updates5594.
- Native receipt: `4d0e7e4ffbf11b56b4aad0f18d87da629804d00f7993de9499687a8fe96b90e0`.
- Controller: `57763e630aeae8ea0a0792646dd200bec841410b72942b1d1cde89af96754f35`.

This route uses existing Up+Select manual vertical platforms, width32,
initial topY208: 1-1 leftX1201/centerX1217 (141 native carry updates),
1-2 leftX112/centerX128 (143 carries). These are observed player-triggered
locations, not new fixed stage placements. The helper inventory records
their verification scope. Natural Bomb collection/use is a separate gate.

## Delivery gates

Source qualification completed in commits f19ecfb5 and77139df8:512 actual
InitScreen selector/facing cases, stale-selector parent negative, four
native collector progression cases,11 foreign public-call comparisons,
23,064 cold readbacks, changed-byte fault rejection,121 IRQ and121 lag-NMI
cuts. Minimum interrupted SP150. The controller-only CPU natural-three-item
route also passes with the identical controller57763e63. See the scoped
source report for fixture details and exclusions.

Root retains one candidate and
one controller in its existing bounded output; no captures were created.
The installer requires the exact tested controller, repeats this route
from the directly replaced Downloads ROM, checks automatic patch sidecars
before and after, and restores the parent from memory on failure. The
publisher requires pushed source and independently downloads/reconstructs
the sole Current IPS while verifying Current is Latest.

The direct Downloads replacement completed and repeated the exact native
receipt4d0e7e4f and controller57763e63. Installed bytes equal the tested
candidate, both patch guards pass, and no backup files were created.
Release publication is recorded in the current continuation note.
