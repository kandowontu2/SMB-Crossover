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

First ordinary Star source job84267 is pending under absent
`build/sunny-natural-star-bc5-1115`, max1file/600s, zero outputs. It requires real
birth/maturity/physical collection, Star35/music64/grab cue32, the actual delayed
popup1000 score return, then25 actual returned Sunny updates at Main return.

Natural native S/L, audio fidelity, idle performance and a fresh current full
stage remain separate scopes. Historical Hard/M/F/fireball receipts stay
versioned; no shared progress JSON is edited.
