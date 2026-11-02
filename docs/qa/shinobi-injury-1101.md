# Shinobi injury source component

Recovered donor entry `$DA1B..DA5D` and its 26-byte movement script
`$DA5E..DA77`. The relocated initializer and script assemble to 93 bytes.
The source sets state 16, pose 6, direction-dependent knockback, and resets
the original movement interpreter. It is not a generic SMB knockback routine.

`tools/audit/prepare_shinobi_injury_1101_v3.py` compares the original ROM
instructions against assembled relocated instructions for all 256 facing-byte
values. All cases pass: callback order, actor RAM, registers, flags and stack,
after normalizing the relocated script pointer. The three animator/interpreter
calls are trapped at matching boundaries; this does not test their behavior.
Receipt: `build/shinobi-injury-1101-v3/result.json`.

Reusable assembly: `tools/reference/shinobi_injury_1101_v3.inc`.
The donor is SHA256
`24e1e425b84776ab2116b4dd1a85545f78e9a507caa8367a490cc77adab46874`.

Still required: injury/death pose graphics, native damage/death integration,
remaining external source callbacks, menu admission and controller-only 1-1.
This component is not installed in the nightly and does not unlock Shinobi.
The installed Metal Storm nightly remains unchanged.

## Injury/death graphics recovery

`tools/audit/prepare_shinobi_hurt_art_1101_v4.py` now executes the donor's
animator and OAM emitter for poses 6 and 7, both facings. All six pose/frame/
facing packets convert to native 8x16 pairs with identical opaque pixels,
palette indices and sprite priority. Eleven new pairs (352 bytes) append to
the existing 96-pair atlas. The output retains the original OAM and converted
rows in `build/shinobi-hurt-art-1101-v4/packets.json`; additional patterns are
in `additional-art.chr`, with a hash-bound `result.json`.

These are real source poses, not replacement drawings. The converter has not
yet assigned a fourth hardware sprite window or expanded metadata. Do not
publish pair indices 96..106 through the existing three-page setup. The old
metadata uses 1696/2048 bytes, leaving exactly 352 bytes before adding these
poses; metadata compaction or another verified allocation is required.

## Implemented layout successor

`prepare_shinobi_hurt_layout_1101_v5.py` resolves the storage issue above by
moving the unchanged 256-byte terrain-attribute table into the kernel tail.
The kernel, including the original injury initializer/script, is 7160/7168
bytes. Expanded metadata is 1544 bytes; the additional art occupies
`D6A0..D800`, the last 352 bytes of existing physical CHR page 517. New
descriptors use pairs 117..127, leaving the metadata portion unaddressed.
The fourth sprite window must therefore publish page 517.

All 58 existing and new pose/frame/facing cases pass through the actual native
metasprite renderer in CPU fixtures, with original pixels, priority and palette
indices preserved. The private cartridge also passes actual PRG-resident cold/
warm loader, 32 header corruption and retirement tests. No new resource grant
or additional CHR page was needed.

Candidate: `build/shinobi-hurt-layout-1101-v5/candidate.nes`, SHA256
`f6658fb7532dc87b1583da8f388fd8e3f1094b2bbd71ea51a5c611bb37364db9`.
This supersedes the v2 private placement. Hardware CHR publication and gameplay
hooks are still absent; this is not an unlocked or installed nightly.

## CHR request service

The v6 successor adds ROM-resident `ShChr`, authenticating both cache headers
before requesting physical sprite pages 503/504/505/517 in windows 4..7.
It clears the competing special-window override and asks the native NMI path
to publish the banks. The actual `X5PublishChr` instructions produce those
four hardware register values in the CPU model, preserving other windows.
Twelve accepted cases and 38 invalid-header/foreign-character rejections pass.
The new resident size is 1053/1536 bytes.

Candidate: `build/shinobi-chr-1101-v6/candidate.nes`, SHA256
`e3bec84b8721984bebd84dfd1121080b21d95e4662a829611987ed0addd3657b`.
Source: `tools/reference/shinobi_chr_1101_v6.inc`; reproduction and test:
`tools/audit/prepare_shinobi_chr_1101_v6.py`. This service is not yet called by
the scene/main hooks. No emulator display, unlocked character or new nightly
is claimed.

## Scene ingress

The v7 successor patches the existing 18-byte `InitScreen` farcall to `ShScene`.
For Shinobi it loads/authenticates the component, requests CHR, and calls the
source constructor through service15 if Ready is absent. An authenticated warm
room change preserves source state. For other identities it retires Shinobi's
headers, then invokes the previous Metal/Karnov scene chain.

CPU tests exercise cold construction (470794 cycles, standalone minimum SP180),
warm scene entry with preserved inventory/health (2056 cycles), and foreign
retirement plus previous chain (4356 cycles). These are bounded instruction
fixtures, not NMI/Main stack-reserve or emulator proof. A new-life path still
needs an explicit Ready reset/retirement; warm room transitions must not reset
inventory accidentally.

Candidate: `build/shinobi-scene-1101-v7/candidate.nes`, SHA256
`249d9a7159048ea995b097df7d03f7d3b1182fc460d39fea5f66914e248c704d`.
Resident usage: 1145/1536 bytes. Reproduce with
`tools/audit/prepare_shinobi_scene_1101_v7.py`. Still not unlocked or installed;
normal character-service routing, damage/death, unresolved donor callbacks and
native gameplay remain.

## Native service routing

The v8 candidate routes raw36 through all 36 public Hu entries to Shinobi's
resident veneers. It extends the existing Metal gate within its 48-byte
source-proven HUD padding (46 bytes used), and reuses 26 bytes of the old,
unreachable Metal route after its existing JMP. No new allocation is borrowed.
Service1 goes directly to authenticated `ShChr` rather than the unimplemented
RAM graphics row. Karnov and Metal keep all 72 original route destinations,
including Metal's cold world-palette special case.

The real HuGraphics, HuDraw and guarded HuMovement entry points execute in CPU
fixtures. Drawing emits six native body sprites. This does not establish active
movement, combat or emulator correctness. Remaining services still reject;
do not enable the menu based only on these routing checks.

Candidate: `build/shinobi-route-1101-v8/candidate.nes`, SHA256
`12db8aa78ac0fb5de9591fdf34a82a1b0c13a94106cf3b430660c1091072deb7`.
Reproduction: `tools/audit/prepare_shinobi_route_1101_v8.py`. The v8 ROM includes
a three-byte service1 veneer edit absent from the inherited v7 resident binary;
preserve it when extending the resident code. Downloads is unchanged.

## Active movement through native entry

`check_shinobi_active_1101_v9.py` now runs 620 updates through the actual
`HuMovement` cartridge entry across idle, both walk directions, standing jump,
running jump, crouch, standing throw and crouching throw. No donor callback
is stubbed. Assertions cover one pixel/update walking, 66-pixel jump height,
landing, horizontal running-jump travel, crouch state and live projectile slots.
Duplicate-frame and paused calls preserve the simulation phase and position.
All assertions pass on v8's exact ROM hash.

The fixture places floor metatiles in native row12 (world Y224), matching
the source feet position224/native player Y192. An initial row11 fixture
incorrectly embedded the body16 pixels into the floor; that invalid placement
was corrected before accepting movement results.

Peak measured service costs are 2447 cycles idle, 3244 walking, 3430 running
jump and 5100 throwing. They exclude Main, NMI, camera and other actors and
cannot establish whole-frame lag. This remains a flat-buffer CPU fixture,
not native playability, collision-with-enemy or stage-clear proof.

Next damage boundary: donor `$D771` decrements `$0539`; only underflow clamps
it to0 and sets `$0038` bit1 (unless source bit0 suppresses death). Thus the
constructor's value6 is seven hits, not six. Inspect the preceding contact
gate and `$0752/$0549` timing before wiring the health adapter.

## Native damage adapter

The v10 candidate implements `HuInjury` in resident ROM. It authenticates both
headers, maps source state, applies donor immunity conditions (states10/16,
flags0460 bit1 and magic timer054C/D), and applies the donor health-underflow
rule. Nonlethal damage invokes the recovered original `$DA1B` through private
authenticated service36; the original interpreter supplies vertical knockback
as well as horizontal direction. Foreground R0..7 and mapper state are restored.

Twenty health/facing/immunity cases and 32 corrupt-header rejection cases pass.
The original `$0752` flag is a dirty-HUD request (consumed at `$9495`), not a
post-hit invulnerability countdown; hurt state16 itself excludes further hits.
Death currently only sets original0038 bit1. Native death/life handoff, injury
status routing, HUD, sound and actual enemy-contact gameplay are incomplete.

Candidate: `build/shinobi-damage-1101-v10/candidate.nes`, SHA256
`6d43da1f12248a1763ad3d8c68353611f72342e3b32a9294f7ff30b14b61014a`.
Resident1333/1536 bytes, leaving203. New cache cookie binds the private vector36
change; rebuilt resident preserves v8's CHR veneer. Reproduction:
`tools/audit/prepare_shinobi_damage_1101_v10.py`. Not installed or unlocked.

## Death and new life

The v11 successor adds authenticated cache rows6/7/8 for injury status and
death. Status returns1 so native damage arbitration reaches the source-health
handler even when its zero-based health counter is0. Lethal injury enters
original pose7, initializes its animator, and holds for the donor's200 updates.
The final tick clears Ready and selects SMB engine6; only native GameRoutines
deducts a life. The next scene initializes a fresh source actor.

The 122-byte worker occupies previously zero metadata padding `D608..D682`,
before the injury-art tail atD6A0. A four-byte status leaf uses the kernel tail
atBBF8. Updated cache cookie covers both changes. Resident1351/1536 bytes.

CPU fixtures exercise actual HuInjuryStatus, lethal HuInjury, HuDeath and
GameRoutines:200 ticks,200 duplicate checks,200 paused checks, exactly one
native life decrement and a fresh health/death state after scene entry. The
animator advances before every nonfinal tick as in the original death loop.
This does not establish native emulator visuals, sound, enemy collision or1-1.

Candidate: `build/shinobi-death-1101-v11/candidate.nes`, SHA256
`fa5e38ce1202f6cb8de9eb79b25dd27627006ea020afded5ce090f40f1bab5aa`.
Reproduction: `tools/audit/prepare_shinobi_death_1101_v11.py`. The local damage
include override in this output connects lethal damage to death row7; retain
it when rebuilding. Downloads remains unchanged; menu remains locked.
