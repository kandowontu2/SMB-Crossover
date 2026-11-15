# Gimmick temporary bounce marker side collision

The proposed correction makes only Gimmick's side probe return empty for native
temporary blank-bounce metatile `$23`. Head/foot queries retain their raw tiles,
and R3/the block buffer retain `$23`. Other 255 tile values, real pipes/bricks,
all other characters and the shared wall clamp are unchanged. This is a private,
source-qualified proposal, not an installed or native-qualified update.

Official parent is current16a
`16a385654e80105f83470e14cd328d8bbceaa659730f4a81a2f36ca039cfbcfb`.
Combined proposal is
`7a80f0f37e316436be0825bbd6fd9d372af6b0b7741f84ea87356282033d9b79`.
The historical590-only proposal is
`05fb72a3d7928c4ec5f2267e7f52a9aa739f682cb0c3629057c2342962486a96`;
that model is kept strict and is not relabeled current16a.

Root's native side diagnostic80386 on590, receipt
`360b8ce702100ba28fe639aedf28963c8b79cfd7e09cd7ce59dac816b67a7dd2`,
proves the actual GmSide query returns A/R3=35 at block-buffer cell `$037D`:
Main1562 player1229/137, requested1234/159, then Main1563 player1231/137,
requested1236/159. StopPlayerMove and the unchanged shared LeftClamp follow.
Earlier actual first-writer43924, receipt
`55bc8f9fa852adf0b613bac6ed98d8dadbc2cc8fb1f166ac71110a51dd7e79dd`,
locates native `STA $75` at PRG10:A2E6 before GmImport mirrors native1231→1247.
The shift survives the complete Main. This is not inferred from borrowed star
collision fields. GmReadPoint already treats `$23` as empty; native generic
side collision treats its nonzero raw value as a wall. See root-owned
`gimmick-flower-native-1115.md` for the unchanged-control native negatives.

Root explicitly authorized source testing only within the four spans below.
The initial candidate gate correctly rejected BBCF tail reuse: those bytes
are live foreign MiniLiftTick code despite stale Gimmick end metadata. No byte
of that tail, new RAM, CHR, helper or foreign/shared routine is borrowed.

| File span, end exclusive | Old SHA256 | New SHA256 |
| --- | --- | --- |
| 202882..202998, 116B | 61350a794b9fc3f4bab8881459248f2b73927144abdf0ee43988e502d124da34 | 80f3bf89a7fc0712693f9bd2303340f65b52039e232f1b730611f4d105cbd6aa |
| 202998..203069, 71B | 188bbd8d510f23d9bc8f35ac1b291c599283968aee948209a813445605b687a3 | 8e982ff8a190835e93ddc56b50af30dbddb72e38f88ef623cdfe8923ce31a638 |
| 203358..203360, 2B | 2a473b964396560ab1d802b3ef5e264d221a4cc885098c8f4e109c36ce0d5f81 | 6b61208b73ad1b1667f803ec3ce45082e542dba74258d86d5976fcab1545ed2f |
| 203560..203562, 2B | 2a473b964396560ab1d802b3ef5e264d221a4cc885098c8f4e109c36ce0d5f81 | 6b61208b73ad1b1667f803ec3ce45082e542dba74258d86d5976fcab1545ed2f |

191 owned bytes contain160 changed bytes. Both Draw operands are explicitly
included, old `1db9`→new `13b9`; the second consumer was discovered and granted
before composition. All other current16a bytes are exact, including Prince's
new transition, prior graphics/BT/score changes and the Mini tail.

Composer `compose_gimmick_empty_side_1115.py`, SHA
`a9eaabb0dc63a8c457b35bc908da5e887460a7f70dc8f57a29c88a7a9a85b02c`,
exposes `current_proposal(exact16a)` and `current_inverse(exact7a80)`.
`proposal(exact590)`/`inverse(exact05fb)` remain separately typed. Every forward
patch authenticates old bytes regenerated from the retained source; inverse
requires the exact full candidate hash, regenerates source preimages, requires
exact parent and repeats the forward roundtrip. No inverse reads Downloads.
The typed loader reads Downloads once and explicitly uses frozen Prince inverse
when presented16a; it does not relax the590 APIs.

Public Head B872, Foot B877, Side B87D and ScreenPoint B8E6 remain fixed.
Raw Body moves B87F→B882; the two actual Head/Foot JMP operands are updated.
ScreenPoint's four repeated shifts become a two-iteration loop with saved Y,
and it falls through CameraPoint, now B913 instead of B91D. This releases ten
bytes for wrapper B923: `2082b84923f002492360` (JSR Body; EOR35; BEQ; EOR35; RTS).
Only A35/NZ become A0/Z; C/V, X/Y and R0..7 remain exact. Source-defined side
indices3..6 and head/foot0..2 retain their original geometry and Y return.

Body retains the probe index temporarily in X, restoring Y before raw lookup
and X0 before owned return. This removes its old STY/LDY GmTemp2 scratch pair.
The removed write previously left probeY in `$5C7B`; its changed final scratch
value is explicitly classified, not masked as arbitrary private RAM. Whole
retained-source census finds only the two old Body accesses and renderer
accesses. Portrait writes input facing at line115 before its read143/Emit.
Draw writes star facing296 before trails, zero365 before effects and hero
facing414 before body Emit. EmitRecord234 reads that caller-facing value;
the direct component API requires caller-supplied facing. No GmClock/audio/ISR
reader consumes old probeY. Full renderer comparisons below deliberately
start with different Temp2 values and compare every private byte at return.

Current actual Body consumers are solely the two source-bound Head/Foot
jumps. CameraPoint consumers are ScreenPoint and both Draw calls. The complete
retained source-reference census and actual Gimmick code operand census agree.
Neither moved private label is in the actual host admission's published/imported
service list. GmScreenPoint/StarRecord/EmitRecord are internal renderer APIs,
also absent from that host ingress list. Manual CPU calls to removed private
entry addresses are outside the legal native caller domain.

Source component checks are terminal PASS:

- `check_gimmick_empty_side_components_1115.py`, receipt
  `abb801c759b3e11064c6ffe83fb86848b06ee1849275e6fd0a7b65e31beb980b`:
  7,168 tile/role/status pairs,16 intended side23 changes;2,520 coordinate/wrap
  pairs;3,570 foreign-owner pairs;1,080 ScreenPoint AXYP/R0..7 pairs. Other255
  tiles and raw head/foot/R3 are exact. ScreenPoint adds **20 cycles**, including
  a real page-crossing branch, rather than the initial estimated19. Initial
  harness-only missing-SP-key/cycle assertions were corrected without changing
  candidate bytes; invoke itself checks returned SP.
- Historical native-side CPU fixtures on05fb, receipt
  `84a9a4c74ee760c1d360ac42c70a846d157680b8df7278935a5b0773e7ae867e`:
  marker35 previously clamps1231→1247/stops VX254→0; new leaves1231/VX254,
  side timer0 and raw tile35. Real brick81/pipe97 still clamp; hidden96 and
  empty0 retain their old behavior. Nonmarker query adds14 cycles; four empty
  native side probes add56. These are declared CPU fixtures, not seeded play.
- Fresh exact-current native-side CPU fixtures in
  `check_gimmick_empty_side_current_1115.py` also PASS, receipt
  `1eed2e7952f42c8d05772eb4d84232576f3188d32aa551d8bce3afd3de7e51ae`.
  Parent16a versus7a80 reproduce the same marker/real-wall distinction. Strict
  parent/candidate/truncation/dirty-owned/dirty-Mini/dirty-CHR rejection and
  portable inverse without a mutable-nightly dependency pass.
- `check_gimmick_empty_side_interrupts_1115.py`, receipt
  `02fe9ec577a7fd7b9d961874647d71241126828fdb6b86040188c7b1ce1e745a`:
  actual combined7a80,58 component calls,205 reached contexts/94 PCs,
  205 actual IRQ plus205 busyNMI pairs, minimum ISR SP195. Old/current same
  reached context follows exactly the same real ISR instructions and full
  native/private/audio/stack effects. Interrupted AXYP/SP, R0..7, SMC, mapper
  and above-entry stack are preserved. No changed Gimmick code/data is read by
  either ISR; no ISR stub or native-RAM/audio allowlist.
- `check_gimmick_empty_side_callers_1115.py`, receipt
  `545abb4259321b7335725faab2ab40ba1cb29afaf9e78af6f424b3d4b6b6084f`:
  genuine current combined cold Select/Start;116 full Draw/Portrait pairs:
  22 hero poses×2 facings,66 star/history frames,4 effects,2 portrait facings.
  Incoming Temp2 differs3 versus109. Exact AXYP, full ZP/full5C00..5C7F/SMC,
  ordered OAM/maps at return, with no private mask. Cycle deltas0/40/60 reflect
  actual ScreenPoint calls. Source closure is included in the receipt.

Ordinary current7a80 Main source job3658 is terminal: aggregate is **negative**
because frozen Flower navigation still fails; its successful cases remain valid.
It uses compiled cold Select/Start and normal inputs, with no gameplay seeds.

- Hidden1UP PASS,1085 Main/1084 Gm movements, receipt
  `86ec669288fff6a57ecf52aa33208145309e63a571b1f7b5ff05c9a48e0ad63c`.
  Real first M, then hidden1UP, life2→3 and25 actual post-writer Gm movements.
  Terminal1069/176/HP3/cap3/lives3/power1/inventory0. Source-only.
- Star PASS,1675 Main/1674 Gm movements, receipt
  `904805770161e9ef0599d7a0aa0442bd5a4a87d5812a90fabd3016c49c4edd1a`.
  Real M/Star/erase/timer/music/cue/+1000 and25 post-collector movements;
  terminal1866/176/HP2/cap3/lives2/power1/Star34. Source-only.
- Frozen Flower controls NEGATIVE,1397 Main/1396 movements, receipt
  `4a84bdea9eacc842de68d6f6d6ea5933d3e094c5b774b2a000422d5c2ddff850`.
  Genuine reflected-star support is reached Main1296 at1214/151, VY0,
  ground128/starflag64. Its later ordinary jump misses the Flower and reaches
  the unchanged bounded post-support assertion, alive1243/176/HP3/lives2.
  No Flower/inventory grant or full-route pass is claimed. Aggregate receipt
  `540e6f5cf7abbed8468c780c8d92b95c2903027ffc76f47dba0c6693f38c1d2a`.

Frozen-control adapter `replay_gimmick_empty_side_current_1115.py`, SHA
`5c5a77a49f34af37bc2f90f51efa342ecbed6badf79590b639526c1967963e00`,
exposes `controller(raw7a80, key)` for flower/oneup/star. Bodies/assertions are
byte-identical to their strict590 parents, only current SHA/hook bank metadata
are rebound. Lua hashes are respectively
`cce79facd3c60f504c06df43c32d18cae932b135334600d10e6fc5a9e5c7dfbc`,
`ede6a71ab413e07b146c33c39e23d344554f13b21c82a7eb9f361fba197a637c`,
`95d6711043a0c01bde447b38fc143d97891886ea3789f00c473f19ae4c542ed8`.

Root-only native diagnostic API is
`replay_gimmick_empty_side_probe_current_1115.controller(raw7a80,'mr_gimmick')`,
factorySHA `e5f97f76d9dffbc1a7bf9d9212bb36fc3efd96bd47de062bfa1f2af4c4445a9b`,
LuaSHA `53f0bb046d049aac36f4aeeb008781f6d0bc0c5c69967659a1af7c39b2d70b5d`.
API/compile/hook gate receipt
`52f6e669c4df47915eae1a60d7ba10c24c140f09f0a1199e07cb8a8d32682960`.
It retains105ff controls/assertions and relocates the raw Body RTS toB8D6 and
actual public Side return toB92C, checking actual caller SP/returnPC. New
read-only arrays retain at most8 marker returns,8 actual solid returns and12
raw prefilter rows. Every owned side return asserts A=(raw35?0:raw), with rawR3
preserved. All hooks authenticate actual bytes/current bank hashes. Old plus16
shift is observational, never asserted as expected behavior. No images/statewrites.

Remaining private native gates: actual marker35→empty/no+16 and real walls
solid, first-M/Star/1UP regressions, native artwork observations. Flower's full
collector/navigation route remains open independently. Existing public M/S/L
receipts remain versioned590; no automatic promotion to7a80 or16a. Performance,
all abilities/audio/expiry/protected hits remain separate. No helper locations
or platform inventory change. Root alone may grant/stage/test/deliver.

Root's private staging/probe grant is now
`allocations/gimmick-empty-side-native-1115.json`, SHA
`ad854a2d2eb1a2d57744f5dd2a2aea4568f32d1fe094ba14f30007faee71075f`.
It grants root's private composition/staging/diagnostic only, explicitly no
Downloads delivery. At this checkpoint root70234 is live; no native result is
inferred. Composer/core/probe sources are frozen through root's native gates.

All producers used exact absent bounded roots under build/gimmick-empty-side-*,
max-files1/600s, in-memory fixtures and compact stdout receipts. Zero generated
ROMs, capture/state/image files or build artifacts; frozen parent factories and
game sources unchanged. Protected user progress/Steve files untouched.

Root70234 is now terminal private7a80 **collision diagnostic PASS**, receipt
`fb8f94243b990fc2119e3a483298206a6e438ab963e7f606ff7783ab4a5996fa`,
using exact53f0 controller. Across5,510 actual side queries, four observed raw
R3=35 queries at Main1562/1563 return A0 from public B92C/SP221. Native x1229
then1228 has no old plus16 shift. Actual real wall tiles18 (Main918/x725/Y128)
and16 (Main1103/x901/Y128) retain their nonzero returns. This is the actual
native correction witness, separate from the declared CPU fixtures above.

Its inherited ordinary Flower endpoint remains **negative** at the unchanged
post-support jump bound:1673 Main/2215 physical, alive1243/176/HP2/lives2/power1.
That does not invalidate the narrower side-marker witness or qualify Flower.
Official Downloads remains16a at this point; root owns native QA and any later
regression/delivery decision. Core/composer/probe remain frozen.

New two-picture graphics API is
`replay_gimmick_empty_side_images_current_1115.controller(raw7a80,'mr_gimmick')`.
FactorySHA `ef0ec51a99a8cfa731e82fa629cfcd40657a6afc7321093e35ab94e9beac316a`,
LuaSHA `a3e6e77e39e9d90d740f3169affc8a8c57082ac031a10700395baec2145a3354`.
It explicitly inverses all intervening parents to frozen cf7 image controls,
then rebinds only actual candidate SHA/hook bank hashes. Private deep copies
avoid the old image recipe mutating cached Stage RAM metadata. Bound is two
RAM PNGs, each at most65,536 bytes, no disk outputs; ends at maturity before
pickup. New checker source51488 passes strict API and ordinary compiled cold
opening route, receipt
`1a872ec542e893ed512ae0c1df8beb83cea4be10ac57dc710de7bdfe7ef64099`.
Source Goomba snapshot is Main140 hero216/176, live actor328/184; mature M is
Main306 hero333/176, actor336/119. Both actual model bank lists are
[816,16,17,18,19,20,21,818]. The model's marked PNG is only an API fixture,
explicitly not a native raster/art witness. Root's native two images remain
pending at this checkpoint;116 complete renderer CPU pairs remain qualified.

A separate ordinary-input Flower successor now passes source24689, receipt
`71f18c5a3f091119050cdcb453a82860eeaa2c7b61e3f005119cdd729ab78f5d`.
The old native/source fresh support jump is genuinely admitted, not a lost A
edge. Both old source and private native ride at1214/151 with residual VX232
(−24). The new controller changes one navigation choice: after the actual star
wall reflection, hold Right instead of Left while still waiting for the same
current actual RideStar/released-A/poll-consumption gate. This brakes existing
left momentum; it does not change game physics, support or terrain.

New source reflection1288 leads to braking1289 at1226/138/VX231. Current real
ride1296 is1218/151; the next actual freshA172 jump1297 has VX248 (−8), preserving
enough room to rise beside the existing brick. Actual mature Flower collector
1320 is hero1239/100 versus real actor1248/119/kind1. GmPickup yields inventory
count1/code2/next2, actual cue1C and erase; the unchanged finish gate requires
score at least1405+1000 and25 strictly later GmMovement entries. Endpoint is
1346 returned Main/1345 Gm entries,1266/112/HP3/cap3/lives2/power1. These HP and
timing values are source-only; the actual private native route had HP2.

New API `replay_gimmick_empty_side_flower_current_1115.controller(raw7a80,
'mr_gimmick')`, factorySHA
`7ad1efcba9b8a6c992e6e538811b2d6d47b46db6a67d68b9d640f1a68e546d73`,
LuaSHA `15d21220bc91a5f3ee24e4fd3e1253587ea088f2755bc55e6076076f82345093`.
The only post-run file change fixes inherited diagnostic metadata to describe
the actual7a80 hook-bank hashes and removes an unused import; generated Lua is
unchanged. Separate source API69492 is terminal PASS with the final factorySHA
and same15d212 Lua: strict truncated/dirty/old-parent rejections, zero mutable
nightly rereads/file/native traps, actual bank24 SHA
`f9007727c468bc8713894bdafb88519f7661b1c3118a6a9fb4ee4128b471cebe`.
Original53f0/0a644/cce79 bodies
and their negative receipts remain frozen. Root native qualification remains
pending; this source pass does not close the native Flower stock cell.
