# Prince: funded native floor admission, November10

This is a **source-qualified, in-memory proposal**, SHA256
`c3fb87bcbab3a9ad2d3537f9444797fee50344c8a08195d8b9b4b02ff309bba3`,
over the exact combined Sonic cold-only parent
`d07012de9762e93ca76cb283ba84e9b8a9a7bd532364fd94ce4ca6101687cb72`.
No ROM, receipt, capture, compiler temporary or other build file was written.
Downloads/public c10, the private34d ROM, frozen v1 proofs and frozen103B
geometry source/checker remain unchanged. Mesen, cadence, fourth-pipe crossing
and full1-1 qualification remain pending. No helper actor was added.

## Repair and first-state evidence

The earlier [floor diagnosis](prince-fourth-pipe-floor-method-1110.md) remains
the oracle: physical sole213 / logical anchor208 / Delta8 / DY0 makes native
floor residue5 appear as a side contact. Native bank138:`A2E6` then pushes
X897→911 before original source movement imports that incorrect position.
Correct pipe solidity was already present; the original roll displacement
was only2 or4 pixels.

Cold activation exposed an overbroad admission in the preserved103B geometry
leaf. At translated update3, X684/sole209/Delta4 has actual native DY`FF`
(rising). Original native collision correctly leaves Y177; unconditional
geometry projection moved it to176. The subsequent route drift was not
accepted or hidden by changing the frozen fixture.

The new44B `prince_native_floor_admission_1110.s` at RAM2:`D53E..D56A` wraps
the unchanged103B leaf at `D4D7..D53E`. It preserves engine!=8, rising motion,
and every contact already admitted by the actual native landing window:
five pixels for DY0..4, DY+1 for DY5..127. Only a rejected residue proceeds to
the existing source-anchor / exposed-solid-surface geometry check. It uses
no RAM or SMC scratch. The existing four-byte RAM3:`BD3E` leaf becomes
`JMP D53E` plus NOP. Original actor physics/scripts/state, C084, terrain
OldFoot, rendering geometry, source no-bounce behavior and hard-fall damage
remain unchanged. Native BG Y is projected only for the qualified contact.

## Closed storage and decoder bounds

[Conditional page329](allocations/prince-append329-1110.json) is appended only
after the already qualified Zelda-II alias table change. It is **not free in
the public ROM**. Sonic321..328 stays byte-identical;329 is now Prince cold
storage;330..334 remains conditional shared future storage. Canonical fairy
pages319/320, ordinary forms308..318, world335 and HUD236..243 remain intact.

The actual cold-tail table grows14→15 rows; low table staysC23F and high
table movesC24D→C24E. Only the high indexed-load operand and declared stream
constants/source start change. The349B worker/data endsC25D, within the
unchanged512B C100..C300 boot copy. Art remains31072 bytes, decoder254 bytes,
loader446 bytes. Packed runtime/metadata/state are6386/5767/1232 bytes.
Payload45157 fits45 existing-plus-granted pages46080, leaving923 bytes.
Appended329 holds the last101 payload bytes plus FF padding.

Metadata startsCA79, with the existing C300..C800 cold-only fragment retained.
Actual decoder reads consume every6386/5767/1232 staged byte before overwrite;
minimum overlapping unread margins are416(metadata) and130(state).
Deliberately staging metadata atC800 instead triggers an actual unread-input
overwrite atD5C2 before either header commits.

The new immutable Prince cookie at physical65:`AB9F` is
`a72602b98a9df4ea3c0b1b4650c8b52f`. Actual ordinary cold takes7919503 CPU
cycles /30902 PPU reads, minimumSP180, commits both exact headers and passes
actual authentication.329 is read204 times:101 bytes twice plus two mapper
dummy reads. Copy-first/last, independent-reread-first/last and final decoded
state-byte faults all fail closed with both headers invalid.

## Source qualification

- Frozen13 geometry positive/negative cases remain exact. The derivative
  gate passes4096 DY/residue cases, including2048 actual native-window calls:
  3986 original cases remain unchanged and110 rejected windows reach geometry.
  All256 engine values preserve the legacy behavior except intended engine8.
- All239 decoded geometries,408 actual native poses and2578 original parts
  retain identical OAM/CHR/source packet/register behavior.
- The frozen172-update third-cap fixture passes without modification.
  Original X745 jump admission and X891/HP5/native state4 landing reproduce.
  All19 original v1 contact cases retain Hard/water/hazard/rising/side rules;
  seven pause/epoch/powerup/foreign/retire/fresh-life cases pass.
- Six existing owners pass cold/warm,192 header poisons,36 guards,18 readback
  faults and36 paired ordered transitions. Five unaffected owners retain
  complete RAM/maps/PPU/ABI; Prince's identical constructor prefix and intended
  new code/header are checked separately. Retirement is compared against the
  actual parent transition, including foreign unowned tails.
- All100 named menu entries remain exact. Sonic's cold/warm,32 poisons,
  eight faults,six guards,six owner roundtrips and foreign retirement pass.
  Public raw43 remains rejected; original Sonic gameplay is not admitted.
- Actual Zelda-II publications retain512 pose/facing+regular-NMI pairs and
  54 menu/54 lives/54 gameplay-world-HUD pairs. Undoing the alias makes pose21
  publish overwritten329 and is detected. Existing finite source authority
  is rebound;329's original art equals canonical319.
- Actual cold vectors pass2571 forced-blank NMI and145 unmasked IRQ cuts,
  including198 appended-row cuts and164 resumed interruptions in the original
  cold trace, minimumSP159. Actual fourth-floor GameLoop passes111 IRQ and
  111 lag-NMI cuts, minimumSP139, with complete state/register/mapper/PPU parity.

Controller-only fourth-pipe exploration uses actual native1-1 parser data,
GameLoop and normal NMI; no terrain/outcome writes follow initial translation.
The correct fourth pipe is X912..943/top144, cap10/11 and shaft14/15; first
gap is X1104..1135. Natural failed controls and the current controller search
remain explicit CPU scenes, not native crossing or full-stage proof.

The exact baseline controller confirms X891/HP5 landing, authentic HP4 on the
next update, and X897 throughout the fourth-pipe contact poses, including
sole213. It never enters X912..943. Native Goomba0 reaches X886 and causes real
contact death at update143. Park/wait/A/Up exploration reaches X862 on the
floor, then fails nearX879/873 and dies at524. Neither path witnesses a fourth
cap or first-gap crossing. Subsequent controller/attack investigation is kept
separate from the frozen funded repair.

## Zero-output reproduction

From the workspace, set `PYTHONDONTWRITEBYTECODE=1`, then use the bounded
wrapper with `--output build/prince-floor-carrier-audit-1110 --max-files 1
--timeout 600 -- python -B` and one of these source commands:

```text
tools/audit/check_prince_floor_carrier_1110.py --admission --poses --lifecycle --negative
tools/audit/check_prince_floor_carrier_1110.py --owners --alias
tools/audit/check_prince_floor_carrier_1110.py --readback
tools/audit/check_prince_floor_vectors_1110.py --both
tools/audit/check_prince_funded_route_1110.py --baseline
```

The wrapper retains zero files and removes its empty reservation root.
`proposal()` reconstructs only in memory and asserts the exact parent, frozen
source hashes, unchanged Sonic pages, art, decoder, loader/table bounds and
new type/cookie. This allocation grants no publication or native gameplay.

## Frozen qualification source

| File | SHA256 |
| --- | --- |
| `tools/reference/prince_native_floor_admission_1110.s` | `5805c356fed1bdbad99b2519a444a41a951b05b6db4274c676a6baeb871c36e5` |
| `tools/audit/check_prince_floor_carrier_1110.py` | `660dcefca52122fbcacc73ae6b366fe5a059313208265cccbe195a98726de6f7` |
| `tools/audit/check_prince_floor_vectors_1110.py` | `8facad13071d83e059ffb42c028506ca4916599f1e37e7f8348584d40eefc963` |
| Frozen103B geometry source | `98dd9c59e473a3952a7002b634e806bf5f1f5aa9654c54eb9094b5d01104997e` |
| Frozen103B geometry checker | `438250e4dd3955e8db70e09adb982e07a143c4fbc9998b2b4063c015fa252eee` |

Exact payload SHA256:
`7f0cd66a7a39a1ada52fdf3490e25fd4f1131d2c2b7e476363141f675685687c`.
Appended page329 SHA256:
`0b02f8af71f077129c495cdce1eb6dd32dbf1d53ed4635bcfde268d28ee8998a`.
Decoded runtime/metadata/state SHA256 values are respectively
`37f6afc726d259a49f8c0c08d96c215286927aa6f72f2505129bd2ad54775f5c`,
`1c425259d1acec63adc10b0280f529379e7c684646df33aac4560148d372907c`,
`80ee0e087f0f41f4575084f96c88e2945ee6c8574a171256bf3e67eaa164e4d9`.
Controller exploration remains an unfrozen diagnostic; it does not alter this
candidate, its source qualification, or any ROM on disk.
