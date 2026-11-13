# SMB2/Doki full-stage follow-up: native route development

Public ROM remains7ef2de35. These are controller-only native diagnostics,
not a new ROM, new helpers, or completed eight-character stage coverage.
`replay_smb2_stage_current_1113.py` adapts the frozen Bowser route's native
menu/return/terrain observers to raw25, actual S2Variant/Ready/health, and
requires both lives, positive original health, real flag/castle/entrance and
25 consecutive grounded quiet underground1-2 updates for success.

The actual menu uses Down three times to position24, then Select0..7 for
SMB2 Mario/Luigi/Toad/Peach/Imajin/Lina/Papa/Mama. Linked state addresses
5FE3/5F98/5F9B are authenticated. No controller writes game state.

## Imajin findings on actual Downloads

All recorded attempts have the same clean empty opening:48 completed Main
updates in48 physical frames, skipped-NMI delta0, X40/Y176, original
health31, both lives, no native actors. This is a scoped idle result, not a
full-stage60Hz claim.

| Ordinary controls / observer | Lua SHA256 | Native receipt SHA256 | Result |
| --- | --- | --- | --- |
| Eight-update A hold |7a8472c553b4e7c863ac38c1c34bce210daeefffb2345c08fef0d01f6daa25a3 |177035834cb911b05bd5a568a57f2b39e1186e6206f96a9f8ba26ad2ddfc908b |Second-pipe wall at X595, healthy; a short tap does not demonstrate maximum jump height. |
| Twenty-four-update A hold |827ecd160f19092d71217ee665035f90434871f07b9666ec027112a3c96b13e0 |01785e30b8521f86470856ce0534b05b8ee424af89e45daa9156b48e4e4971f7 |All four pipes/first pit crossed; second ordinary enemy injury at X1226 is fatal. |
| Same inputs, passive injury entries |cbd5fce3ced3d3c840026ca8c5c51b0eb1532172084f7a90c85bd34aff30a988 |efb51c4628c2dc4e80ad71d2b0465490f28054c1c8286d064fb47762b667fd85 |Actual sourceAir0/VY0, player297/176 vs Goomba305/184 at first injury; later player1226/112 vs1235/120. The route landed beside them. |
| Enemy jump begins within48px, passive injury entries |8be381ff593f604a2438c560cf0829f1d560fe88ffcc2c9b1b973ee0f2c8e260 |e4a1e2cfa237bad19be2cd28b918664550cc3f0286c1fab4b6a6c78cbc0ab585 |First Goomba defeat retained; one later injury, then final stair/pit fall at X2471. |
| Wait for real source held-A release |f2f2c5159ccbefcd21bd3ab09113592408b15030cca9be1d0b17a8e5366322b8 |e4a1e2cfa237bad19be2cd28b918664550cc3f0286c1fab4b6a6c78cbc0ab585 |Identical physical result; stale planned A edges are not the demonstrated cause. |
| Passive final-pit window |4d2faefaed53e35c6d4db40de2940532c577961a3f3fa3fefe8a78ba1cce53da |e33de7de5795e1b697a7d91559b20a6550fa1a2cfc110425c7f6c589e56dc3e1 |Bounded trace, unchanged inputs. Tool output truncated; only selected complete rows were recovered in memory. No full trace file is claimed. |
| Neutral settle at X2416 |09c211e07b42df934448206ad7b13ec053fa2fdf8a51049cdfe62b0baabdd450 |d1af7afd85993ffc12b5416402a587d2714e22bb19ec81fe84102361485c72b2 |Entered settle airborne at2416/72, but neutral input retained air inertia and the player moved beyond the ledge to2467. Original pit death at1771Main/2478physical. |
| Air countersteering, then standing jump |2b2919c5f598a39b6f06d875804527112ff63cc9e6c08852109eacb38643fb3d |98e1a3c814b2775a1e570923fee75306cb5a93854224ced65311937a30c0889e |Actually lands at2416/112, but the stationary launch begins too early; side/fall near2474. |
| Land, run to edge, then ordinary jump |6371ab8df461a9a347ad6baf5f7f3d84de78fa1472af4a49d73b98574958231e |647e5ec7af75dec63681a17f5c7fc432d24d0a1092f2255179f9e9229845cacc |Final pit crossed and all terrain traversed without helpers. Healthy horizontal stall at the flagpole3155/162 prevents the required stage exit. |

The one48px-route injury is actual rising contact: player1257/91,
sourceAir1/VY178, versus live Goomba1263/87. The preceding Goomba1232/120
already has native defeated state4. This does not demonstrate a broken stomp.

The first final-pit trace mislabeled read074A as `actualNativeHeld`;
074A is TimerControl. That unused observer field is corrected to
`timerControl`; no held-input inference is made from it. Selected retained
rows show the second jump already descending by X2446/Y86 and side contact
near X2467, not an unexplained teleport. Complete terrain/landing causality
and a safe crossing remain under investigation.

The final ordinary-controls branch actually settles at2416/112, runs to
2434/112, jumps and lands2518/144 on the right stair. It then traverses the
remaining terrain and final staircase. It stops at3,283 physical frames /
2,531 completed Main, source health15/both lives, engine8, worldX3155/Y162,
after240 updates without horizontal progress beside the flagpole. No native
flag/castle/entrance state has occurred, so this is not a full-stage pass.

The retained source has an explicit RTS `S2WorldInteraction` stub, and
`S2MainWorld` currently implements head/coins/down-pipe interactions without
a flagpole call. This is a strong integration lead, not yet a source-bound
patch diagnosis: the source agent is binding actual current bytes/callers and
will qualify a real native handoff. All eight share this implementation;
only Imajin has had the full native route diagnostic here.

No physics, collision, difficulty, actor, health, block or helper placement
is changed to accommodate these tests. Normal running/jumping can traverse
the final pit; no additional helper is indicated by this route.

All tests reuse root's existing two-file bounded output and single Mesen
queue, with zero screenshots, capture files, videos or state dumps. The
private DK candidate file stays unchanged. GitHub releases remain empty;
the new source receipt is not permission to recreate Current.
