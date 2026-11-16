# Detached Bowser life-gain repair

Owning ROM is exact bc5:
`bc5e275d1dd4dabab4b5b2def66f7643ae46aee17a31ab37887528b791594040`.
This is a detached proposal and flat CPU proof. No NesBus/gameplay overlay,
ROM composition, native run, installation, new RAM or capacity is authorized
or performed here. Existing S/L controls and all item negatives stay frozen.

## Concrete repair and funding

Only `BwEnsure`, work3 A133..A15B, packet offsets307..347, changes. Its three
existing long constructor branches share one local JMP, funding the saved-life
store inside the same40 bytes. New code uses39 bytes and one unreachable NOP
inside that function. `BwSavePlayer`, `BwSelectPlayer`, `BwConstruct`, their
public entries, the service table, all pose/art/data and all other packet bytes
stay exact. No historical padding is borrowed.

For valid ready/current-player state, equal life counts return without writes;
a small positive modular native INC delta updates only the active player's
existing saved-life byte. A negative native DEC delta takes the original
constructor, including last-life0→FF. Invalid ready and player changes retain
the original constructor path; explicit new-game construction is unchanged.
No pose, movement, health, tier or inventory field is reset on an earned gain.

Exact old40 bytes:
`ad26bec9b7f0034c71a0ad580729010a0acd27bef0034c71a0ae27bead5f07dd82bff0034c71a060`

Exact proposed40 bytes:
`ad26bec9b7d01dad580729010a0acd27bed011ae27bead5f07dd82bf3006f0039d82bf604c71a0ea`

Old span SHA `c4a5089adfc51fb198aa1147a91901118a7be1400530b9bcbf1fc863726bb658`;
new `48e4bdd173038caaa1f96fcc1e4157c45c582df3ddab86fec944d166799ed7c2`.
The40-byte envelope has32 changed bytes. The detached8KB packet digest changes
from `bb43cfb45f5b931dd1beff853825bcb1f3c3d70c63599b9e69a442959e561b2f`
to `316cde097972dcf0b1ebfd2d98c955e8c6ccaf4d1d92f0844732623e832e85da`.

The actual old packet is contiguous at file1997840, CHR927..934. A later
composer would need exactly these three authenticated physical views; none
has been written:

| View | Half-open file range | Bytes | Changed |
| --- | --- | ---: | ---: |
| Ensure within existing carrier |1998147..1998187|40|32|
| BwLoad copied fingerprint |565244..565260|16|12|
| BwCheck expected fingerprint |693672..693688|16|12|

Total72 owned/56 changed physical bytes. Both complete fingerprint views change
from `a71b0005bb43cfb45f5b931dd1beff85` to
`a71b0005316cde097972dcf0b1ebfd2d`. The NES header is unchanged. No new packet,
cookie or ROM was serialized.

## Executable contracts

Within the actual packet, PlayerNew writes saved HP/tier/life/valid; SavePlayer
updates only HP/tier. There is no existing saved-life update to reuse there.
Compacting Ensure avoids changing either writer or constructor policy.

Recursive decoding from all36 public service JMPs reaches1127 instruction
boundaries. Exactly four JSRs enter A133: movement A19F, weapon tail A248,
injury A294, graphics A417. There is no interior or external relative ingress,
no indirect JMP, and the four raw word aliases are precisely those operands.
The old internal branch targets are replaced inside the owned function.

Flat CPU comparison proves caller AXYP/SP exact. Equal lives keep47 cycles;
an earned gain takes51 cycles instead of699/702 constructor cycles. Existing
reset paths retain their complete ordered writes; their small branch timing
changes are reported by the checker. No new stack use or mapper operation is
introduced. Live IRQ/NMI/gameplay proof remains a later source-lease gate.

Owning native writer audit receipt
`ccfa71b0ac592e5a530637aa366475ed6a0e9ead59afb9a91711fdbd72dc7951`:
native popup INC8987 and coin INCB808 credit lives. PlayerLoseLife's actual
far target C2:B6A1 decrements atB6AE, preserves flags, returns the life byte,
then the real caller tests BPL atA27F. The first adjacency-only observer was
corrected to follow that actual callee/return pair. Fresh setup and player
transpose remain original construction paths. The proposed delta rule covers
native per-update INC/DEC, not arbitrary external counter rewrites.

## Detached proof and retained unsigned negative

Final signed proof receipt:
`5914f938f38e22539dc4f033dc3b80eb63e5cd1f62a18257460a6ffd69bff5ca`.
10,752 cases cover equal/increase/decrease/death/ready-invalid/player-change/
newgame, both forms, both players, tiers0/1/2, full/injured HP and64 flag
combinations. Caller AXYP/SP and all original reset ordered writes match.
Gains write only the active saved-life snapshot; every other byte is retained.
Minimum SP213. These are explicitly seeded flat primitives, not gameplay.

Another3,072 cases sweep all256 old counters, steps-1/+1/+7, both forms and
both players. Death paths match original writes, and INC wrap retains current
HP/tier/pose. The first boundary fixture mistakenly recopied the entire packet
over its primitive state; it was corrected to install only the declared40B
code span before this terminal proof.

The earlier unsigned BCC proposal is frozen and **not eligible for mounting**.
Its original10,752-case receipt `cb2f6b05056f2f982ff0d93b68e19b2e00b505fd953dd17bfc4755d4a855c814`
did not cover the actual last-life boundary. The new explicit0→FF witness
records original constructor1 / unsigned0 / signed1. No unsigned code was ever
mounted in a game or ROM. Its static views receipt64bc4199 remains historical.

Final source pins:

- `plan_bowser_life_gain_signed_bc5_1115.py`:
  `c1308b6f81629def6d2f0b579b17b3196e188861fdf8c4ded9f6f493294e497d`.
- `check_bowser_life_gain_signed_detached_bc5_1115.py`:
  `5b1cfcdda5bc78ad1b30539d617a6edc640e94b50f8da127ff031c6b2d653a98`.
- `inspect_bowser_life_native_writers_bc5_1115.py`:
  `1b1ebde9a390caa031d6903d3782be3c2f25481e003628c8a5ebee385763a6d9`.

Run the signed checker through the bounded runner with an absent output root,
max1file/600s. The plan is ready for independent root review and a separately
scoped source composition/qualification lease. All task output roots remain
absent and no helper used Mesen.

## Frozen native calibration controls

Metadata/strict-rejection receipt
`e6818e2b2325af33bc2a5267b575e9806d2e276f82bf0a7837fffb4fb51e95c0`.
Both factories reject truncated, unrelated-byte and reference67 inputs.

Base L factory `replay_bowser_natural_stock_bc5_1115.py`, SHA
`2d4fe5399d4da143fcfb8d1db40d62315bec5403ed65073eaf7c9d3d9cdfd48f`:
`controller(raw, identity=0|1, kind='oneup')`.

| Identity | LF Lua SHA |
| --- | --- |
| SMB3,0 |`cc61cb805e6f47d2c100a482bd5c697c076ddba99b5a825f73dbd3a970037a5a`|
| SMB1,1 |`628a1675c2304baab9238e301894d94a446b833c2be3b9122c2e58e587b8174d`|

First-writer factory `replay_bowser_oneup_lifecycle_bc5_1115.py`, SHA
`ad9c1355f48df620df214e2e661a1c2890df5f4936b944cd9cf2e75c11e6e768`:
`controller(raw, identity=0|1)`.

| Identity | LF Lua SHA |
| --- | --- |
| SMB3,0 |`882e6226224f6f5ffb91d9eb54750b138f023c606b2bc9aa9c6d459af5a5c0fa`|
| SMB1,1 |`7ae6edbc8963149c065d360063e138c0772cc7e9f13c494b11dbd92864fc4322`|

The observer intentionally stops diagnosticFALSE after the actual constructor
return; this is not a stock pass. Identity0's source causal episode is retained
in the stock QA. Identity1's observer has compile/binding proof only. Both use
the same frozen ordinary controls and real menu selection; base preservation
gates are not weakened. Root owns any native calibration.
