# Battletoads camera handoff research, November14

This is unallocated source/RAM research. No cartridge was composed, no file
candidate or capture was written, and no Mesen/Downloads/install action ran.
Root owns the current route controls/checker and the sole native queue; those
files are read-only dependencies here. Own code is
`tools/audit/check_battletoads_camera_handoff_1114.py`.

Input boundary accepts exact delivered1daca
`1daca93f837e894a3ee5b3d8cef54622336726f4df243c6bfb997130323f3baa`,
or exactGimmickcf7 through its separate strict portable inverse to1daca.
No frozen API assertion is broadened. Eventual composition must preserve all
192 Gimmick bytes when the owning current input iscf7.

## Existing actual failure and source cause

Root actual Rash79559 on1daca:1000Main/1388physical/728 actual original
Btsteps,HP47,lives2,x217/Y176. The initial generic B cadence repeatedly
restarted stationary punches; root corrected that controller policy separately.
Root ordinary near-source23888 still reaches only239 through8500Main while
jumping,HP47. Root direct source90630: Right-only80Main x179/Y176,120Main
x239, unchanged through180; Right+A200 Y111,230 Y127,260 Y176, alwaysx239.
All8 snapshots have Player_X_Scroll=0,Player_Pos_ForScroll=0,ScreenLeft=0,
ScrollAmount=0,ScrollLock=0,SideCollisionTimer=0,lives2.

Current native ScrollHandler reads701 for movement and75A for the pre-step
relative position; its offscreen handling clamps at the right viewport edge.
The BT adapter's actual ImportAED8 and ExportAF9E omit both camera handoffs.
Read original source state in physicalRAM3. The current mapped nesDebug view
can show another bank and is not valid source state evidence. Real menu gives
raw33,FmGroups64/96,BtVariant0/32,HP47 forRash/Zitz respectively.

## Exact measured proposal

Current private8192B cache is carried at file1989648 in CHR919..926, SHA256
`e6548f57de4aefbd6ece22193bcf7a5320f5b9a151fd3ba28209c688d211d876`.
Current ROM cookie at765863 is
`a7210175e6548f57de4aefbd6ece2219`; cacheBFE0..BFF0 is zero before loading.
Cookie recipe is A7/33/1/117 plus the first12 SHA256 bytes of that exact cache.

The actual BT_CACHE_HOST segment456 is AD9C..B5E6,size084A, with87 current
symbols. Lives/status code extends beyond old BtUnavailableB546, soB548 is
not a free pad. B5E6..B603 is29FF bytes, SHA256
`6a99cf1e02ff68b7972440d13ec3038fcd79c6546e7533e67412a79b3ee4ab72`.
No host symbol/declared emitted consumer occupies this tail; its sole physical
overlap is the existing complete8192B BT_STREAM carrier container. Ownership
is the selected33 private RAM3 partition, not a general free-space claim.

| CPU/file | Exact old bytes | Proposed bytes |
|---|---|---|
| AED8 /1993448 | `a575186908` | `20e6b5eaea` |
| AF9E /1993646 | `bd1cbf38e908` | `20f2b5eaeaea` |
| B5E6..B603 /1995254..1995283 |29×FF | `ad71058d5a07a57518690860bd1cbf38e908084838e5758d0107682860` |

The import helper is12B: cache native pre-step Player_Rel_XPos0571 into
Player_Pos_ForScroll075A, then reproduce LDA75/CLC/ADC8. The export helper
is17B: reproduce LDA BF1C,X/SEC/SBC8, save P/A, calculate committed signed
low-byte movement delta relative to native75 into701, restore A/P and return.
The second SEC is required for page-wrap/left movement arithmetic. Exact
original export result and carry must reach the following high-byte subtract.
The initial16B estimate omitted a byte; retaining all architectural flags
requires29B total and does not need a weaker flag contract.

This changes40 cache bytes. Proposed cache SHA256 is
`8605ac5665158653b677e7e12f44f712afb9b003c9d8a7998a632aeaedaf5c66`;
derived proposed ROM cookie at765863 is
`a72101758605ac5665158653b677e7e1`. The cookie's12 digest bytes also need an
explicit grant before a production composer. No other code, CHR art, native
physics, map, actor, helper, health or control bytes are proposed.

## Completed source gates

Every producer uses bounded root `build/battletoads-camera-handoff-1114`,
max-files1,timeout600, zero outputs with file-write/Mesen traps. Actual flags
are `--max-files 1 --timeout 600`. Output directory stays absent.

Session66251 `--interrupts`, terminal exit0: snapshots genuine compiled
Rash cold/Start and source calls. Import entryAED8/SP202/P33 returnsAEAB/SP204;
ExportAF9E/SP202/P30 returnsAEB3/SP204. Every reached trampoline/helper
instruction boundary is cut:9 import and15 export, each with actual unmasked
IRQ and busy NMI (48 cuts total), minimumSP177. Architectural registers,
private RAM, raw bank mappings, live farcall SMC, modes, latches, upper selector,
and continuation outcomes are unchanged. Busy NMI has its genuine skip
accounting. These real Main contexts have NmiDisable busy; no regular arm was
forced inside them and no universal regular-NMI claim is made.

Preliminary harness negatives are retained:19693 misread root's hex0571 as
decimal571 (stopped at symbol binding before placement);70192 initially
rejected the exact carrier container itself as overlap (no other overlap);
41737 compared PHP/PLP's nonarchitectural emulator break-copy bit as a live
flag. The corrected comparison masks onlyB withEF, preserving C/Z/I/D/V/N.
These are fixture issues and do not discard the observed current x239 failure.

Gates33463 corrected prefix matrix and44506 ordinary old/RAM-camera
Rash/Zitz movement comparison are now terminal exit0:

- 33463 `--units`:12288 import and20480 export CPU prefix cases, all256 native
  low bytes, both player slots, all carry/overflow/sign input corners, positive,
  zero and negative deltas including wraps. A/X/Y/SP, all architectural flags
  and original result/carry match exactly; only the two intended camera fields
  are added. Extra cycles are24 import/41 export (65 per original BT step),
  primitive minimumSP220. NES PHP/PLP's break-copy bit is explicitly excluded
  from the model flag comparison; actual reached caller status already hasB.
- 44506 `--functional`: both real Rash and Zitz constructors, ordinary Right
  for180 completed sourceMain. Exact parent staysx239 with all camera fields0.
  RAM research reaches379/Y176 with ScreenLeft267,Scroll2,PosForScroll112,
  ScrollAmount2. Both retain2 lives; HP47→43 is real Goomba contact, retained
  accurately. This proves the camera handoff component, not enemy immunity,
  native timing or a full stage.

No active process remains for these three gates; terminal output is retained
in `functions.store` by handle. Full1-1/1-2 investigation follows separately
after these primitives. Native and production loader/cookie qualification are
pending a formal allocation/composer. RAM research installs code only after a
genuine cold load; it does not update the live cache cookie or claim the new
loader/copy recipe has executed. The proposed production cookie is derived
and pinned above for that later exact composition.

Frozen checker SHA256:
`669b67b7b92ac7050ceafd2043885a343b629b02a2b61fe3f5dbf22d5623921e`.
Root-independent entrypoint is the checker CLI with default inventory,
`--units`, `--functional`, or `--interrupts`, each through the bounded command
above. Maximum proposed changed cartridge bytes are52 (40 cache +12 cookie
digest); no candidate cartridge SHA exists because none has been composed.
