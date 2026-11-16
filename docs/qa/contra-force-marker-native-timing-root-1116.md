# First palette optimization does not improve physical cadence

Root4846 passed both matched timing observers, but the private optimization
does **not** satisfy the lag objective. Downloads remains the verified6a3
Bowser build; candidateffbb is private and is not published as a lag fix.

Actual parent6a3 receipt:
`12420f353236da4a02316e488f6e60bb2486b8161ad75de4f42e212b788ad4d6`.
Privateffbb receipt:
`f08a9d7ef207bbe66637b54cc4612f0d7dc3e6fafc996c64a84f0a84d750f35c`.
Both use the exact frozen8752 observer body6e1bab, new strictly typed
factoryde056f20, parentLua94012d8b and candidateLua564fcbee.

| Metric | Actual6a3 | Privateffbb |
|---|---:|---:|
|Idle completeMain / physical frames|48 /96|48 /96|
|Idle NmiSkipped delta|72|72|
|Idle missed port-read frames / complete samples|71 /95|71 /95|
|Idle port reads|384|384|
|Right completeMain / physical frames|16 /32|16 /32|
|Right NmiSkipped delta|24|23|
|Right missed port-read frames / complete samples|23 /31|23 /31|
|Right port reads|128|128|
|Total completeMain / physical frames|400 /511|400 /511|

Literal completed-Main histograms also match: idle48 zero/47 one, Right16
zero/15 one. The one NmiSkipped/input-poll difference on Right does not
establish a meaningful cadence gain. Both end58/176, lives2/power0/Star0,
65 balanced movement/Input/Body calls,198 complete-cookie/zeroactor-shot
checks and no A/B input during measurement. No 60fps/render-rate claim.

The actual mounted source profile saved3966 CPU cycles per ordinaryMain
(56240.375→52274.375 idle;56411.25→52445.25 Right), with all14 checks/services
retained. That source gain is real within its scope, but insufficient to
change these physical measurements. The next work is finer service/transport
attribution and a larger guarded dispatch reduction; no unsupported callback
may be skipped merely because it appears idle.

Root stagedffbb only after the parent actual Downloads run passed, using the
existing candidate/controller slot and strict1042-owned/714-changed composer
and inverse. Previous private6d7 was discarded by direct overwrite, with no
backup. Official2097168 bytes stayed exact6a3; guards clear before/after.
No captures/images/game writes/files/releases/patches. Both runs left other
Mesen sessions untouched; none were present at these launches. Queue is free.

New opcode source gates preceding timing: all4 cold/readback07c5700e,
renderer35944/c17a6363, reached4138IRQ+4138busyNMI/d5377086,
public/header/foreignd08fe8d1 and loan-retirement4/9354cc30. Source fullBurns
route was started independently; other extended routes are deferred pending
a material performance change. These source scopes do not imply delivery.
