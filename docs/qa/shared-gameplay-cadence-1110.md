# Shared gameplay cadence on MMC5

The previous public ROM `c8bd2e2c` applied shared work reductions to the native
game loop, terrain parser, platform pairing, and ordinary player contact.
The paired contact proof measured 63–84 cycles saved per update for Mario and
75–100 for the other sampled owners, including Samus and Mini Mario, in the
same three- and four-contact scenes. The shared game-loop tail separately
saves 27 cycles per completed call. Mini Mario's actual Downloads 1-1 route
has 3,494 active video frames, 3,494 game updates, and zero missed controller
reads. The replay reports loading and stage transitions separately.
[Delivery and scoped results](continuation-current.json)

## Samus and Bill opening replays

Each replay starts from the title in Easy, with cheats off. After 120 active
idle frames with no enemies, it holds Right from world X40 to X258. The walk
includes the first natural Goomba. Both characters reach 94 ordinary player
contact calls across 175 walk updates. The exact previous ROM `df03fc35`
differs from current `c8bd2e2c` by the latest ordinary player contact change.
For each character, every measured field matches between the two images.

| Character and phase | Physical frames | Main entries | Missed controller reads | Lag NMIs | Frames with no Main entry |
|---|---:|---:|---:|---:|---:|
| Samus idle | 120 | 120 | 0 | 0 | 0 |
| Samus walk | 181 | 175 | 22 | 22 | 6 |
| Bill idle | 120 | 120 | 3 | 3 | 0 |
| Bill walk | 184 | 175 | 29 | 29 | 9 |

Input polling and game-loop entry can fall on different sides of the video
frame boundary. Both counts are recorded so a catch-up Main entry cannot
hide a missed controller read. The paired samples show no cadence change from
the latest contact optimization in these opening routes.
[Controller observer](../../tools/audit/shared_gameplay_cadence_1110.lua)

The current Bill replay also recorded the actual interrupted address for all
32 active lag NMIs. The three idle samples interrupt PRG63 `$B42B` and `$B446`,
and PRG4 `$A525`. Of the 29 walking samples, nine interrupt PRG4, seven PRG3,
six PRG2, four the RAM farcall trampoline, and one each PRG63, PRG86 and PRG126.
These are deadline locations. The code running when NMI arrives can be a
consumer of earlier time in the same update. The three idle misses occur
before the first enemy or any projectile.
[Deadline observer](../../tools/audit/shared_gameplay_nmi_1110.lua) ·
[Interrupted PCs](../../build/shared-gameplay-nmi-1110/capture/deadlines.json)

The shared shot-bank selector remains active with four empty projectile
slots because it also maintains the logical CHR shadow. An in-memory trial
at PRG78 `$BC9A` skips the type comparisons for empty slots and preserves
the ordered CHR shadow writes. It saves 24 cycles with all four slots empty
and can add up to eight with all four occupied. The trial matched registers
and publication writes in 13,156 CPU controls and passed 80 IRQ or lag-NMI
pairs. In native runs of that change alone, Bill missed two idle reads and
Samus missed 21 walking reads.
[Shot-only native replay](../../build/shared-shot-scan-native-1110/proof.json)

## Sparse world draw and projectile scan

The released `f33c7b19` nightly avoids a second native scan when the current
enemy IDs cannot draw firebars or small lifts. Firebars and lifts still use
their existing renderer. The combined CPU proof verifies 544 cold-entry
updates for Mario, Bill, Samus and Rogue Dawn with exact game state and sprite
output. The world change saves 80 cycles on those updates. The combined
change saves 104 cycles in the Mini opening fixture. Real positive firebar
and small-lift OAM and the existing native actor IDs were checked.
[Combined CPU proof](../../build/native-sparse-world-draw-1110/combo.json)

| Easy opening | `c8bd2e2c` missed reads | `f33c7b19` missed reads |
|---|---:|---:|
| Bill idle | 3 | 1 |
| Bill walk | 29 | 28 |
| Samus idle | 0 | 0 |
| Samus walk | 22 | 18 |

Samus's walk also went from six to five frames with no game-loop entry.
The identical Mini controller cleared the full nonshortcut 1-1 and rode all
three lifts with 3,494 updates in 3,494 active frames and zero lag NMIs.
[Matched native openings](../../build/shared-sparse-draw-native-1110/proof.json) ·
[Mini native timing](../../build/shared-sparse-draw-native-1110/mini/capture/timing.json)

The actual Downloads launch repeated Mini's timing, lift contacts and audio
order. The sole Current IPS reconstructs the tested Downloads file exactly.
[Delivery verification](../../build/shared-sparse-draw-delivery-1110/verified-delivery.json)

## Shared side collision

Native side collision used to enter Mario the Tank's bank four times per
gameplay update in the Bill and Samus opening. The shared dispatcher can
reject nonzero character IDs before changing banks. It preserves the saved
argument and mapper packet fields used by subsequent terrain and audio code.
The CPU proof covers 2,455 probe cases, 672 complete idle/walk updates and
real IRQ and lag NMI cuts. It saves 248 cycles per tested Bill and Samus
update. The Mario opening adds 12 cycles per update. Rogue Dawn's tested
opening takes its existing early route and measures the same cycle count.
[CPU proof](../../build/shared-side-tank-precheck-1110/proof.json)

| Easy opening | `f33c7b19` missed reads | `ba3cba07` missed reads |
|---|---:|---:|
| Bill idle | 1 | 1 |
| Bill walk | 28 | 19 |
| Samus idle | 0 | 0 |
| Samus walk | 18 | 14 |

Both walking routes had the same 175 gameplay updates and 94 native contact
calls. Bill's frames with no gameplay update fell from nine to five. The
same Mini controller cleared nonshortcut 1-1 with both lives, boarded all
three offscreen lifts, and recorded zero missed reads in 3,494 active frames.
[Bill replay](../../build/shared-side-cadence-native-1110/candidate-bill/capture/result.json) ·
[Samus replay](../../build/shared-side-cadence-native-1110/candidate-samus/capture/result.json) ·
[Mini timing](../../build/shared-side-cadence-native-1110/mini/capture/timing.json)

The actual Downloads ROM repeated Mini's route with identical audio and lift
timing. The sole Latest IPS reconstructs those tested bytes.
[Interrupt and audio shadow proof](../../build/shared-side-tank-precheck-1110/shadow.json) ·
[Delivery receipt](../../build/shared-side-tank-delivery-1110/verified-delivery.json)

## Empty-area comparison on the 59e1a591 Downloads nightly

These controller replays start through the normal menu, take four warm-up
updates in Easy 1-1, then measure 48 idle updates and 16 while holding Right.
All six enemy slots stay empty. Native game-loop returns and literal
controller port reads are counted separately. The replay uses the existing
two-file test slot, with no captures.

| Character | Completed updates | Video frames in the measured window | Frames without a gameplay return | Frames without controller port reads | Mesen receipt SHA-256 |
| --- | ---: | ---: | ---: | ---: | --- |
| Mario | 64 | 64 | 0 | 0 | `1f877af33ca4a94087d990bbe79a73ca5d49a2001f4e6378e3103c2cfd7a3c05` |
| Mini Mario | 64 | 64 | 0 | 0 | `8aec6c70a1f718e7399f9cf4c66512fed1e8767535c3642b71ba08123dfb98cb` |
| Mario the Tank | 64 | 64 | 0 | 0 | `69b500802bc83cd48f9dc3e7752e99ae41d761410a2585460ddfac1f2f55d906` |
| Kirby | 64 | 64 | 6 | 6 | `40aea987513b90f79b36aecb71a0ae3c4ac33a0d5baa510576bfd57d3e766680` |
| Sonic | 64 | 129 | 65 | 97 | `4dd200d50a27d42340217fab5756c3fae87f0154c100ae9eaf2c1aed447a8400` |
| Super Sonic | 64 | 129 | 65 | 97 | `100bb0a7c4a5a55c9a18cd00be38c4ef6c68275050cfeb57335c44d9152702e8` |
| Leonardo | 64 | 64 | 0 | 0 | `425121b476539a372ab69f4cb487a08ba26fea200cd22eee448ad885d723b7e6` |
| Raphael | 64 | 64 | 0 | 0 | `c7a2c276094285781a23fcc0012261fa5f634bf7648b80b3451c5e10df280fdd` |
| Michelangelo | 64 | 64 | 0 | 0 | `56472404f1431f2146329d331283be69c57ffa30fe0a0284077bc2d525c91e37` |
| Donatello | 64 | 64 | 0 | 0 | `d55ce98700d39b45af4c0f8a5c3137a32d4529b9be2d23bb76c9b85cd2e38234` |
| Donkey Kong | 64 | 64 | 32 | 32 | `36cc0024d35c4758bc55286c0b0d5a9a74c489006511c7855c545d9d328c3971` |
| Donkey Kong Jr. | 64 | 128 | 64 | 96 | `6a4cf967e575c0b7c397666f176de4b569aa812a63d289eacc7fd95614c3b41b` |
| Rash | 64 | 64 | 20 | 18 | `938fe1abbcbd6314aaf029d2c9c7d9d46cca706cabf3cbaf0fcaeaa08f6d95a3` |
| Zitz | 64 | 64 | 20 | 12 | `2d754d765cb5ee60a0c379d2761f7d2be4def8cc2e12bbf6be33148301ab4aa8` |
| Mega Man | 64 | 64 | 0 | 0 | `c44dab6e367538c68c56d3ff40877b1880f6eb3bcae592f21d1318f15aa49c41` |
| Proto Man | 64 | 64 | 0 | 0 | `8364eb55c5d995589a49c9ad2c672b30eed2b7b9354b88252b48670a84961d05` |
| Samus Aran | 64 | 64 | 0 | 0 | `047b1ae9f75820670e04b2716d1ee176032f59dc60c68cdaff41f21476c329d7` |
| Bill Rizer | 64 | 64 | 5 | 2 | `364b7388c502e7c5b38ecd400ebc297545c7ac7f43c63081a353050324148f9b` |
| Lance Bean | 64 | 64 | 11 | 7 | `299a066c2c61225cf33d3d22282ca37116ce8c4c37b5a34c66b375dab88780fb` |
| Bass | 64 | 64 | 31 | 32 | `626557e2888f9184e576ed8652fda20ac5b401d43be71dd68ef823602b098726` |
| Burns | 64 | 96 | 32 | 64 | `75d55b2409308430713ddf8061bf1ad9f9ce63ba1b60ad52d767b42f3b83bbc1` |
| Steve Hermann | 64 | 64 | 30 | 32 | `d8a888c616358f2407e150f25e5f6e28be547c12f0ceceaba231d63985c2f54a` |

Kirby completed two updates on six frames, making up the six frames that had
no return. The first and last frames in each interval can be partial. The
sample covers stationary and Right-only movement in the empty 1-1 opening.

All four turtles completed one gameplay update on every measured frame.
Donkey Kong averaged 60 updates per second by running two updates on half of
the frames and zero on the other half. Donkey Kong Jr. ran about 30 updates
per second. Both Battletoads averaged about 60 with irregular returns. An
earlier linked CPU trace for DK Jr. measured about 16,220 cycles per update
in the same code-check bank that dominates Sonic's trace. [DK Jr. CPU trace](dkjr-opening-cadence-1113.md)

Mega Man, Proto Man and Samus completed one update every measured frame. Bill
and Lance caught up after five and 11 frames without a game-loop return.
Bass and Steve each lacked returns on about half the sampled frames and
reached 64 total updates through catch-up. Burns averaged about 40 updates per
second in the empty opening.

[Roster replay driver](../../tools/audit/run_roster_empty_cadence_1122.py) ·
[Sonic measurements](sonic-ceiling-native-root-1116.md#enemy-free-idle-and-walking-cadence)
