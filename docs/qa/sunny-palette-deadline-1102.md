# Sunny transform rendering deadline

The delivered Downloads nightly is now `16a9de64` (November2). On the
previous `22d09909` nightly, Sunny's cold Hard non-shortcut 1-1
test reproduced a genuine late rendering enable at frame968, engine9,
X416/Y176, PPU line0/dot105. NMI took2,413 CPU cycles before enabling
rendering. The42-byte command buffer contained the same P0 palette command
twice. The negative was retained with exact timing and a single screenshot;
the hardware deadline assertion was not weakened.

The first private change preserves Sunny's valid palette cache during
engine9. Its432 CPU cases and36 repeated-call checks pass, including
complete A/X/Y/P return equality outside that engine. This passes the first
mushroom sequence, but later native testing found repeated P3/P2/backdrop
preludes during shrinking: frame1764, X1524/Y169,44 bytes and2,501 cycles.
A P3-only trial progressed another five frames, then caught a65-byte burst.
Neither intermediate is delivered or qualified as a full-stage pass.

The current private successor is `16a9de64b18370a03885ff503141fc08edd25f3bd026d480854a1754efa1490b`,
`build/sunny-growth-prelude-1102-v9/candidate.nes`. It omits unchanged
world palettes only for Sunny engine9 and retains the actual P0 callback.
Normal/cold callbacks and the Ice/City owners retain exact queue and
A/X/Y/P results in60 CPU cases. The native weapon palette routine does not
read its incoming A/C; its removed argument store funds a local C-result
branch to the existing Sunny tail. The new20-byte gate occupies verified
unreachable padding at bank3:$B206..$B21A. All existing formatter/private
getter bytes preceding it remain exact. No RAM or carrier allocation was added.

Native full1-1 passes on both the exact candidate and actual Downloads:
3,948 physical frames / 3,102 gameplay updates, lives2 to2, active1-2,
minimum stack pointer196. Both terminal Mesen exits are0. No late enable,
DMA, CHR, IRQ or stack assertion fired. The root queue used
`build/sunny-growth-native-1102-v9/native/run.py` with the unchanged deadline,
DMA, interrupt, CHR and stack assertions, and controller-only input. A
passing result and actual Downloads-context testing were required before
nightly delivery. Before/after same-name patch guards pass. Current remains
the sole Latest release with one IPS, SHA-256
`6ef620d62c4eff2aabc9bfd2dc553963fb37bf6bfdf74b56e71e235006e4b114`;
the remote asset digest matches and IPS round-trip reconstructs the installed
ROM. Other characters and all-powerup qualification remain open.
