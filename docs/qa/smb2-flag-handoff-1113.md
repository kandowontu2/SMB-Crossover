# SMB2/Doki native flagpole handoff — November 13

Private source candidate only. Parent Downloads image is
`7ef2de351d3a4ae60b3ada2eb1aa56b330873dc106ad43428ec6803bf420d4fc`.
Candidate is
`0e9e9254927236bcc651e79da36a77924eea5481421858a05f869b15298412e1`.
No ROM, capture, receipt, object or extracted source tree was written by this
helper. No emulator was launched. Root owns native qualification and delivery.
GitHub releases must remain empty.

## Demonstrated blocker

Root's unchanged ordinary-input Imajin route cleared every terrain obstacle
without helpers, then stopped at X3155 while engine8 remained active. The
passive diagnostic controller
`183451c88967a850a88aa9b7af14c3714aa20d7caa77d59379cdaca824db16dc`
returned the expected negative at3102physical/2349returned-Main:
`6dc5fb1a4d7567d0ae158c0298876101e9d8c78512fc46fe44dfb81982847081`.
Source and native X both3155, base nibble3, source YPage0, size0/duck0,
HP15/lives2; real Right/Right+A cycled Y110..174 with VX0.

The authored flag column at worldX3168 contains native ball24hex atY32 and
shaft25hex atY48..176, both attribute7 (SOLID|BUMP|CLIMB). Stone61hex starts
atY192 and ground54hex at208. Adjacent columns3136/3152/3184 are empty through
Y192. The source right probe at playerX+13 hit the shaft while the native
base nibble was still3. The retained S2WorldInteraction callback is an RTS
stub; MainWorld previously performed head rewards, coins and Down-pipes only.

## Source ownership and implementation

Only raw25's existing bank118 bodies change. No additional allocation, RAM,
CHR, palette, native helper, actor or gameplay constant is introduced.

| Existing owned body | CPU range | File offset / length | Exact parent SHA256 |
|---|---|---|---|
| NativeTileProbe + WorldInteraction RTS | B128..B1D5 |971064 /174|339793404b889bb222919af51d6c138cf67a2837ebf195510a37a39c1a56a8a9|
| MainWorld |B9AE..BA7C|973246 /207|e7aab226f1ac2d644dbf04ad3d6e9a0bd5147fb202dfb18c264386361af68798|

The assembler independently reproduces both entire original bodies from the
owning source before replacing them. Probe174B and World205B+2EA fit their
existing ranges;216ROM bytes differ. GroundInteraction B1D6, WorldInteraction
B1D5, MainWorld B9AE and MainPickup BA7D retain their entry addresses. Other
bytes and ROM length are exact. No neighboring tail or bank padding is used.

The source probe now passes native23..26 instead of just23/26. Thus the two
actual flag tiles become passable; stone, ground and every other tile retain
their original response. A shared final RTS funds the SEC needed to preserve
the original carry behavior of23/26. The original WorldInteraction entry still
executes that RTS directly.

MainWorld factors the identical coin/pipe player-to-cell calculation. It keeps
the original nine coin points/order, at-most-one coin per Main, native head
writer/velocity handoff and native Down-pipe pair. Actual MainPlayer publishes
the same source Down bit in Up_Down_Buttons before movement. Its continuation
replaces dead query scratch with the original priorY and native bounding box.

For source YPage0 and native Y8..207, the adapter uses the real lower native
side probes (left2/right13, Y+24). Only returned24/25 calls HandleClimbing.
The original function retains player-nibble6..9 admission and owns the actual
FlagpoleCollision score, sound/music, scroll lock, state and snap. The adapter
does not write engine4 or force coordinates. Nonactive engine handoff exits
the reward query immediately. Source movement constants remain unchanged.

## Reproduction and qualification

API: `compose_smb2_flag_handoff_1113.proposal(exact7ef) -> (candidate, info)`;
`inverse(candidate) -> exact7ef`, with exact scoped preimages and full forward
roundtrip. The reference assembly SHA256 is
`baea41189476b5988708e7d0c5350ab32e2a4b46e55333109a8de92898565330`.

Run each mode through the same zero-output bounded root:

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/karnov-equipment-1113 --resume --max-files 1 --timeout 180 -- python -B tools/audit/check_smb2_flag_handoff_1113.py --controls
```

Modes `--cpu`, `--foreign`, `--vectors`, and `--measure` use the same wrapper.
The source tests explicitly use synthetic in-memory geometry/position fixtures
where noted; they are not natural earned-item or physical full-stage evidence.

- All eight real menu/Select/Start/constructor openings reach raw25, ReadyB2,
  initial health31. Finite flag matrix:160 native accepts and992 nibble/cell
  rejections across all8 identities. Native state3/engine4/scroll lock/sound/
  score Y and both lives are checked after real collision.
- Nonflag parent comparisons cover every256raw tile, both incoming carries,
  player/object probe owners, and all four probe-direction/cache modes. The
  4064 AXYP/all-RAM comparisons match;32 intentional24/25 cases become empty
  to the source.
- Controls:60 page/carry/Y-bound/Down/air pairs, all9 actual native coin-writer
  point cases,12 real head-writer pairs (51/54/61/C0/C1/C4, both native tiers),
  two actual Down-pipe engine3 entries, and18 actual input/Main/NMI caller
  continuations match the parent. Head54 remains native policy, not excluded
  ground. Query R0..R7 and dead stack bytes are excluded in leaf comparisons;
  the actual Main continuation independently consumes them.
- Foreign:510 paired admissions cover every raw owner except25 and two flag
  inputs. The real unchanged S2BoundaryGame bank63/AD21 literal is authenticated
  through its current A14D legacy chain; this older symbol bundle calls A021
  GameRoutines, so the test reads the actual literal. It stops before executing
  uninitialized foreign physics. No source-owned modified routine is reached.
- IRQ:390 reached changed-instruction/SP boundaries,390 real IRQ plus390 real
  FF lag-NMI injections, minimum SP171. AXYP/live SP/scratch/SMC/overlay/maps
  restore exactly. Scenarios include source probe, native flag admission and
  rejection, coin/head/pipe transactions and actual Main/NMI input. Cold
  copy/headers are unchanged; constructors are separately exercised for all8.

`replay_smb2_flag_handoff_1113.controller(candidate, variant=4)` binds the
unchanged full-stage root controls
`6371ab8df461a9a347ad6baf5f7f3d84de78fa1472af4a49d73b98574958231e`
to the exact private candidate. Imajin Lua SHA256 is
`09c0f838b1c8f592d7a470f51892cafe03227dbd898e5c1b61d317fc1873c453`.
No ROM/state/input-seeding callback, capture or file API is added. Root's
actual flag/castle/grounded1-2 run is pending at this checkpoint; all8 complete
physical stages and healthy natural mushroom/flower semantics remain open.

Affected identities: SMB2 Mario/Luigi/Toad/Peach and Doki Imajin/Lina/Papa/Mama.
No helper platforms were added or changed.
