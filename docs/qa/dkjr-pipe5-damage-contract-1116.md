# DK Jr pipe5: injury and original fall classification contract

Root's new Left-facing ordinary controller clears all ten late stair steps and
the third gap in actuala3fb source, then stops at pipe5-depart6757/x2684/Y176/
source5/lives2. Receipt
`300d35d121fd24563ec566ea888d18d4199d227129cf72cd0f133708106e3d31`
does not by itself identify the cause. Pipe5 boarding/ascent/cross/roof/lower
pass;2640 has57 recorded actual carries, first6675 at2638/138 and last6731 at
2673/162. Depart starts6721 at2667/163. No new helper or game change is implied.
Root owns the unchanged-input first-writer/injury observer50719.

The read-only descriptor `inspect_dkjr_damage_contract_1116.contract(a3fb)`
reassembles the exact owning injury, Damage, fall and landing routines. It
executes no CPU or natural prefix. Final receipt:
`896b06c4178fceb0bba5f16b97b4e0b282c4a7eb16c3396778c6864bfef6b7e3`.

The actual service table has:

| Service | Entry bytes | Target |
|---|---|---|
|5, native injury | A00F `4c93bd` | BD93 DkNativeInjury |
|6, injury profile | A012 `4c8fbd` | BD8F DkNativeInjuryStatus |
|7, native death start | A015 `4c9fbd` | BD9F DkNativeDeathStart |

BD93 is an external native-injury API, **not** the original landing-damage
comparison. It absorbs the call if source hit-active C068 is nonzero or the
source is already phase5. Otherwise it falls through BD9F, requires constructed
ready C8FE2, calls the existing pause unwind and original Damage A2D8. The
handled Cset return prevents native shrink/recoil/death substitution. Direct
DeathStart may enter BD9F without BD93, so absence of BD93 alone is not proof
against an external death path. BD8F..BDAE is31 bytes with SHA256
`9ebdc2e9b9fb72b6019407faafd3c51862e5613af1827b50a98c77c0caeef116`.

These actual WRAM3 first-store sites distinguish the mechanisms:

| Current store PC | Original site | Meaning | Eight-byte preimage |
|---|---|---|---|
| A2DA | D407 | Explicit original Damage entered by external injury/deathstart | `8d6bc0a9048dffc0` |
| A8DD | DA31 | Landing result: safe phase1 or unsafe phase5 | `8d6bc060ad10c2cd` |
| A406 | D64D | No-support fall reaches SourceY216 | `8d6bc06020e1a8f0` |
| A3BF | D60F | Jump reaches SourceY216 | `8d6bc060ad42c038` |

Original DA34 returns unsafe only when sourceY is at least the saved origin
and unsigned `sourceY-origin >= C07B`. DA22 checks this **before** the original
DAA5 landing snap, writes5 if unsafe, or snaps contact top−17 and writes1 if
safe. The no-support fall branch A406 is separate: after its support query
returns empty, SourceY>=D8 (216) directly writes5 without using the fall limit.

Classification therefore requires the actual first store, requested A and old
state, together with BD93/BD9F entry and its context. An admitted BD93 then
A2DA supports native injury; it still does not identify enemy versus hazardous
terrain without that caller/contact witness. A8DD or A406 instead identifies
the corresponding original source decision. A later absorbed BD93 must not be
mistaken for the first cause. No diagnosis or repair is asserted before root's
50719 data.

The bounded absent root `build/dkjr-damage-contract-1116` uses max-files1/
600seconds and produces zero files. The invocation is terminal. No ROM,
controls, helpers, Mesen or game fields were changed.
