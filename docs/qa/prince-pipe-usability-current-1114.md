# Prince current421 pipe usability — November14

The user-reported problem is reproduced with ordinary controls on the exact
installed421 ROM. Historical7ef full-stageH remains valid history; its tuned
brakes and201 Up+Right+A+B fallback do not qualify intuitive first-try climbing.
No game bytes, helpers, ROMs or delivery were changed by this investigation.

Current Prince's three authenticated decoded streams and cookie equal12397.
All176 current hidden/cheat fixes remain present. Stream SHA256 values:

```text
c1f64b964b03c2cd7e7184f294f8ed53e1f8ebdd17ef21666a27da9c1ae034f4
12723b0ee33c0e9acda75831e5c0b20a4afd61c96daead0b9d396096cacf89ea
6d9c266eacade9eda0fa8414d403785ee7408515f886440ab8f45178468c0f60
```

Cookie is `a726026f8a1229edf5a0683733ba6baf`. Metadata compiles the controllers,
rejects unknown/truncated/corrupt ROMs and passes file-write/process-launch
traps. Source cold uses compiled Select/Start and the real constructor/parser,
with the established frontend arena rather than real vblank. Subsequent game
execution changes controller inputs only. CPU scheduling is not physical
cadence or raster evidence. Root owns all actual Mesen results below.

## Right-only approach blocks before the requested Up case

Frozen `replay_prince_pipe_usability_1114.controller(raw,target=1,pad=8,
approach='contact')` Lua8280:
`82800c78790fdc7701aacf15ef3a44c76423fc65edbb16b513e65ce6f233ade1`.
The real first-Goomba jump precedes walking Right toward the first pipe.
The Up case waits for native wall contact or64 updates at unchangedX.

Actual Downloads root78766 fails the approach progress bound before Up is
ever applied:3012 physical frames,1997 gameplay frames,888 without an original
commit,1109 commits/source updates and576 draws, maximum1 commit/frame.
MaximumX429 oscillates/backtracks; terminal429/176, action32/pose123/mode1/
lock0/facing255/foot210,HP5/lives2/inputRight. No hang/top, wall callbacks,
samples or injuries. Receipt SHA256:
`b8b1e160bb3cd6add284750bd43ef0a274859de9e97d2b1e5479b5cfcea26bb1`.
This is a real approach negative, not an Up-input failure. The two sibling
held-input cases were not launched because they share that same approach.
Earlier root69106 lost its result to a compact-printer error and is not proof.

The source direct-from-cold query trace reaches the same class of failure,
1113 Main updates/max432/terminal429/176/action32/pose123/HP5/lives2:
`a687e9ef993200db09067fb22bd9b8799c01f1a201e96b9e5ca23a0ff501079d`.
The genuine executedX404 checkpoint replay independently fails after901
relative updates/max431/terminal417:
`f0330d965e57aa6607818d117d875887a6f654d382c4a27f3fd228c3490de357`.
The corrected source formatter also records identical pre-input failure for
the Up+Right sibling, `142f9008dbb82d38efa66aa478316cb97fbe58d7529d3b7fdb8b1f5e0dcdc0bd`.
These do not imply hardware frame-count equality.

## Direct intuitive controls also fail to climb

`replay_prince_pipe_direct_1114.controller(raw,pad=9)` holds Up+Right from the
actualX404 approach for240 original commits, with no wall timer, neutral,
braking or idle prerequisite. Lua:
`196904c85c47087fcdfb65010d040505d8d3fe0e7d442cdb17ca93239086bac4`.
The Right+A129 counterpart is:
`00c6e0a528c1393efbcfe649691abf0b91efded77a3edf74bd2b0dd4773ce326`.
Neither tested first-pipe route uses the old201 fallback.

Actual Downloads root50286 completes both bounded observations, but both
have **hang=false/top=false**. Observation completion is not traversal success.

| Input | Physical/commits | Terminal native/source X | Actual native body world box | Native receipt SHA256 |
|---|---|---|---|---|
| Up+Right9 |1858/450|417/425|[419,184,431,208]|`830965be5c940806bb6ccef225a311dc11b42637181b905c98369db487de35d9`|
| Right+A129 |1895/450|413/421|[415,184,427,208]|`f4f2c62b7579bfa53199eae75727f6827678de483fa399693da9abfed6a953c8`|

Both start native400/source408/Y128; first samples advance native410/414/420
with source418/422/428 and projection widths32/32/24. Up+Right's body boxes
span412..424,416..428,422..434 while the pipe begins448. It ends action47/
pose15/mode0/lock0, with native/source pad9, foot208, sourceY128, cached425,
oldNative417, projection16 and wall timer0. Right+A reaches real action4/
pose34/lock200 at commit218, but fails to clear; it ends action0/pose15/mode0/
lock200/pad129, cached421/oldNative413. Both retainY176/HP5/lives2/sword0,
with no injuries/wall callbacks. Guards clean; zero outputs/images.
The observer's misnamed `native_status` is raw0759/size, not a natural pickup
witness; no powerup claim is inferred from it.

Direct Up+Right source observation completes454 Main updates, hang/top false,
terminal417/176/action47/mode0/HP5/lives2, body419..431. Receipt:
`4eec25f92df575ae72f4c7b51a288976003f9bf590e7768e6c18ac210d7d758d`.

## Measured translation cause and pending repair

At native425/source433, actual WorldTile returns material20 for raw query429
with translated cell416. The adapter samples cell+24 and cell+40:440 is air,
456 is the real pipe at448. The two16px halves become one32px wall. Neighbor
cell384 returns floor1. This is not a native wall callback or health injury.

The original reference model explicitly preserves a visual+16 origin for its
32px donor cells. A global -16 query shift is therefore not justified. Current
horizontal export independently defines nativeX=sourceActorX-8, with a16px
physical-body contract distinct from changing sprite projection width. A
scoped wall-read refinement proposal is being measured against that ABI;
it must use current sourceActorX before export rather than a stale nativeX.
No production funding, mounted change, caller/IRQ closure, natural-powered
stance comparison or repaired native traversal is claimed yet.

The72 explicitly seeded primitive WorldTile vectors cover both faces, both
16px tile halves and page-boundary placements240/256/448/464.18 return wall20
without the native body's actual overlap. This isolates translation behavior;
it is not normal gameplay qualification. Receipt:
`1c74dba075a94f0ba4c3f422e0c9645b8236ed48ed037c5b515a30a53ee0936c`.

All bounded source output roots remain absent. No captures, archive recovery,
ROM outputs, install, patches or releases. Protected user progress and Steve
QA are untouched. Prince movement/collision remains open.
