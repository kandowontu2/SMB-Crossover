# 85-character Doki nightly

The SMB2 slot cycles Mario, Luigi, Toad, Peach, Imajin, Lina, Papa and Mama.
The four Doki modes use original FDS character graphics, palettes and frame
data. Their conditional original movement has no B speed boost, Mama's
original jump table, original carry offsets, and no USA small-form transition.
Changing between lineages with the same native class resets the right stats.

All eight characters pass cold controller routes through selection, lives,
idle, jump/landing and the opening camera boundary. Actual DMA descriptors,
CHR patterns, displayed sprites and interrupt register/SMC restoration are
observed with the normal eight-sprites-per-scanline limit. These are opening
routes, not full1-1, shortcut, combat or every-powerup clears.

CPU comparisons cover192 jump,32 movement, four lift and720 carry contexts,
plus3,360 old USA carry cases across both sizes and all seven lift stages.
There are10,512 engine executions. All128 original Doki drawing packets,
256 USA pose cases,73 old art records, four original palettes,16 HUD/title
names and720 Start/A cases pass. The90-identity native menu sweep covers124
transitions and2,480 frames with identical heading pixels and no visible
PPUMASK writes. Harmless portrait-preview overlap hashes are diagnostic.

Original vegetable tiles are preserved. Doki art fits existing CHR804..807
without expanding the12KB S2 segment. Duplicate USA record/pointer tables
and branch encodings fund the code within the existing banks. The17-byte
draw packet reuses a mutually exclusive active-character buffer; no new
host-global or zero-page state is allocated.

Full levels, all upgrades, original Doki music, steady60Hz and other remaining
goal characters are unfinished. Doki currently uses the SMB2 audio path.
`source.zip` contains the current reviewed compilation unit, menu override
and recipes; it reuses prior frozen inputs, not an expanded source forest.
It does not replace the canonical37-identity prepared builder. Native proof
keeps four PNGs per run and small aggregate logs; no videos or frame dumps.
