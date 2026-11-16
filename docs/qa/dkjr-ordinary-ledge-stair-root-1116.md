# DK Jr. ordinary ledge and stair controls

These are source-only controller studies on historical privatef544, not the
installed91dc image or a native/full-stage qualification. The strict typed
91dc inverse supplies only the frozen6a3 reference from which the already
leased camera/footer image is reconstructed. All game code stays exactf544;
all13 existing helper placements remain unchanged.

The unchanged ed3e controls clear the repaired fourth-pipe descent, then fail
the inherited falling-Goomba wait. Root4705 receipt
`e333cbb6fbacc469a04078718ec4fa6dcdd6f5b799cf5a987bc15e826bff6d5a`
retains the actual sequence: Right+A at1164/176, ground Goomba1193/184 and
upper Goomba1251/120. The wait starts at1175/162 while already airborne.
Neutral input keeps the original horizontal jump motion; the first Goomba is
stomped and the bounce keeps the character airborne. At3221 the wait-distance
guard stops at1205/155 as the upper Goomba falls nearby. Grounded-only
braking never had a chance to run. No new engine defect is inferred.

The separate `replay_dkjr_ledge_vertical_hop_root_1116.py` changes only that
first near-enemy hop at1136..1181 to A with neutral direction. Both Goombas
are naturally cleared and both early gaps pass. Partial63520 ends alive at
1755/163 after4500 updates, receipt
`907b3a6e95a431caeb4af8dd7622d5d2aca0fa8c1d8e650d666c617ebd332f26`;
its bound is not a full-stage pass.

Full74060 with the same input successor is negative later, receipt
`25f4d8afa0ecfba037f5ecaa7c8f2010930e20a7d1714222e7a6e976115e3619`.
Four fresh Right+A attempts from2127/176 gain no height against the first
late step at2128. It stops at5573,2126/176/source1/lives2. The original
15–17-pixel jump and broad body rectangle make that late takeoff suspect;
this observation alone does not establish a new collision defect.

The new `replay_dkjr_clear_stair_head_root_1116.py` uses the existing idea of
retreat, four neutral updates, then eight Right+A updates. It observes world
position and a target16 pixels higher; it keeps all old success/fall guards.
At the first step it starts from2118. Root22247 is still negative, receipt
`956398060b8d1c8508d3ad3e7b997958edca454823512cbcc68f271c9f9c7911`:
minimum nativeY160 and maximumX2128, but no stable grounded160 endpoint;
the120-update input bound ends at2127/176/source1/lives2. Thus it now gets
height, but this is not a staircase crossing.

Root14482 next traces the same ordinary prefix at instruction-after-write
boundaries around that jump, recording nativeY/state and original sourceY/
phase/body/query. Its purpose is to identify any actual landing/handoff loss
before another controller or game-code proposal. No result is claimed here.

The detached current91dc join descriptor56acde98 predictsa3fb with exactly
383 owned/281 changed bytes across seven disjoint spans. Whole current BT8192
and487 native-header/cookie bytes are outside those spans. The NEW source-only
join allocation fdd63361 permits strict in-memory current qualification;
physical/native/delivery remain unauthorized by that allocation. All earlier
frozen factories and negatives remain separate. Old private floor/entry1073
and one-way769 proposals are not silently included.

All jobs use bounded absent output roots, zero game-state seeds, files,
captures and Mesen launches. The verified Downloads nightly stays91dc.
