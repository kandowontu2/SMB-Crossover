# Sunny natural stock on owning bc5

Source-only work on exact public ROM
`bc5e275d1dd4dabab4b5b2def66f7643ae46aee17a31ab37887528b791594040`.
Root owns Mesen and all ROM staging/delivery. These checks write no build files,
change no game bytes and add no helpers. Natural Star/1-UP are separate from
Sunny's historical Hard full-stage/Mushroom/Flower/fireball qualification.

## Inputs and ownership

The retained live Sunny input is
`build/sunny-growth-prelude-1102-v9/candidate.nes`, exact
`16a9de64b18370a03885ff503141fc08edd25f3bd026d480854a1754efa1490b`.
Its retained controller is
`build/sunny-upgrades-stairs-1102-v3/native/controller.lua`, SHA
`01c5c0ec0805b033f09a6766f98371f0f942feef710e25bd0239b9cb735fb01a`.
Both were read in place. No historical tree was recovered or copied.

The initial source35825 check failed before CPU gameplay because it assumed the
whole Sunny core/art container still equaled that historical image. Census
`2b318d918975ffabcb1a8c6eedcb1f90d29b1f36f157f18b32723aefe3c4e944`
identified seven changed render references and later code in former trailing
padding. This is a preservation-observer negative, not a game failure.

The revised checks prove exact historical bytes for SunnyNativeMovement (63B),
SunnyCollectIntegrated (52B), Ensure/reset, head/body and the three integration
graphics/palette entries. The live core/integration through B6D8 differs only at
the seven declared render references. Current graphics metadata has its own
versioned hashes; no whole-art equivalence is claimed. Supplied CHR724..727 and
the 20-byte palette-deadline gate are byte-exact historical bytes.

`current_sunny_stock_live_bc5_1115.py` accepts only bc5, authenticates the frozen
Hot118 lease/NEW bytes, restores its exact OLD array and verifies whole-image67
as a reference. All route CPU execution uses actual bc5. This compact typed
inverse avoids recursively rebuilding prior character candidates. The earlier
graph-bound revised foundation1414 also passed; it is not a second gameplay
claim.

Compiled menu/Start/parser/constructor receipt:
`deca3e4e052b9df83733ed0aafe4a19484be5656d39ca447d768c187289e94fa`.
Actual Down2/Right6 selects slot22/raw23/variant0, Easy/default/cheats0. Cold
gameplay starts at40/176, lives2/status0, SunnyReady83/Form0/Life2. The source
peripheral bus lacks real title vblank; native title/roster proof remains root's
scope.

## Frozen first stock controllers

- Factory `tools/audit/replay_sunny_natural_stock_bc5_1115.py` SHA
  `391f5303adea769e9447f29907f55e9893f053d6340df00c0565ea8e11c9be70`.
- Template `tools/playthroughs/sunny_natural_stock_bc5_1115.lua` SHA
  `d042a7640e2b0ce948f067954fb05e5ea976c77b661d9b55d613dfedbe6fe89d`.
- Hidden1UP `F.controller(raw, 'oneup')`, LF Lua SHA
  `88f963fba874bcdbd3de5c42b17874a31491b8f504d4ca8ae87c49c119c9db4a`.
- Ordinary initial Mushroom controls reuse the pinned historical v3 route;
  stock branches use actual position, velocity and live actors. No ability,
  position, item, health, inventory or outcome seeds occur.

Hooks authenticate current physical PRG mapping and instruction bytes. Main
entries and returns are separate. SunnyNativeMovement uses the actual stack
return PC/SP, including its RAM far-call return; nested native movement is not
counted as an extra Sunny return. The completion boundary is an authenticated
returned Main with both Main/Sunny pending witnesses clear.

## Hidden1UP source58144: PASS

Bounded absent root `build/sunny-natural-oneup-bc5-1115`, max1file/600s, files0.
Actual current CPU ordinary controls earned a Mushroom, head-bumped the authored
hidden1024/128 block, observed native item birth/maturity and physically
collected it through SunnyCollectIntegrated with inclusive positive body
overlap. Native erase/popup11/grab cue32 and the genuine delayed INC2→3/cue64
were required. Exactly25 actual Sunny returns follow credit at a returned Main.

Terminal: Main1154, Sunny entries=returns1094, x1080/Y176, Player_State0,
PlayerStatus=SunnyForm1, lives=SunnyLife3. This tests SunnyEnsure's real life-INC
persistence rather than treating the new life as a death reset. No current
native or full-stage claim follows from this source result.

## Star

First ordinary Star source84267 is a retained observer-bound negative, receipt
`25d7c6670c11a94aba9990a97509e7342c6c365856b140ff8c1afc3764d48e46`,
LF Lua `bd1f9106e579e8c2ff7333d0cd4e5ae40982b0171fe870193d9890f5e04cd92a`.
Bounded absent `build/sunny-natural-star-bc5-1115`, max1file/600s, files0.
Real birth Main1247, mature1314, physical collector1431/Sunny1312 at1678/123
against Star1674/124, inclusive overlap8x3. Actual return016E/SP239,
erase/popup6/Star35/music64/grab cue32 all passed. A real preceding injury reduced
form1 to0; no injury-free claim is made. The neutral continuation reached
Main4501/Sunny4381, x1681/176/lives2/score2640 versus1440 at collection, but its
target-slot/timer score observer did not finish. No missing-credit game bug is
inferred from that observer negative.

A separate same-input observer69134 under absent
`build/sunny-star-credit-observed-bc5-1115` closed the causal diagnostic, receipt
`714449a5a4cb3a4ea17060c6bc8a35092ea9883802528cc453c6d5dd9c73a0db`.
At most8 popup/core/score events were retained in memory. Popup6/slot5 timer43
at Main1436/Sunny1316 became42 with score2440 at returnedMain1437. Actual
AddToScore return016E/SP244 independently measured1440→2440. The assumed
FloateyNumbersCore entry callback was not reached, although its downstream
native credit executes. The entry-only observer was insufficient. No game
bytes, input policy or score/return requirements were changed.

### Reached-writer successor33346: PASS

New factory `tools/audit/replay_sunny_star_credit_bc5_1115.py` SHA
`14d741be867e35faee2cd8feec395ed4e5de10b53f4c4d73e17f5d130337fc19`.
`F.controller(raw, 'star')` LF Lua SHA
`1452dc2ecaf9bc86e7d274e78fcf96f20d545db855942daa7e8794c32540398f`.
The original factory/template and both first controller texts remain frozen.
This successor changes only configuration and the credit observer, retaining
the same ordinary gameplay inputs.

Bounded absent `build/sunny-star-credit-bc5-1115`, max1file/600s, files0. Source
receipt `8c87c1fb33136657937688a047a7a8174f94cceb4f6a4451b431ebabd62047f4`.
Actual DEC897C/SP245/A43/Y6 authenticates popup6/slot5/timer43, then actual
83D6/SP247 return proves1440→2440 at Main1436/Sunny1317. Exactly25 further
Sunny returns end at Main1462, actual Main return82BE/SP252, pending Main and
Sunny clear. Terminal1681/176, Player_State0, form/status0, lives2, Star34;
Sunny entries=returns1342. The preceding real injury remains part of the
ordinary route. Birth, maturation, positive physical overlap, erase and cues
are the same observed lifecycle as the first controller.

Both current bc5 S/L source controllers are native-ready narrow item scopes.
Root has the exact APIs and Lua pins. No emulator was launched by this helper.
All Sunny source jobs are terminal, output roots remain absent and no ROM or
release assets were created.

Natural native S/L, audio fidelity, idle performance and a fresh current full
stage remain separate scopes. Historical Hard/M/F/fireball receipts stay
versioned; no shared progress JSON is edited.
