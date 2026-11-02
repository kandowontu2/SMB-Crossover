# Metal Storm 1-1 route and performance

ROM SHA256 `fae2f7e83d4afe8aa54fd580715e241d1b9735610b2c465c2e63a4d6cb15c2e5`
matches the installed Downloads nightly. No ROM changes in this pass.

## Full route

`build/metal-storm-route-1101-v37/native-v3/capture/result.json` passes:
6019 total physical frames from cold boot, both lives retained, actual active
1-2 gameplay after completing flagpole, castle, timer conversion and next-area
load. Final screenshot inspected: correct underground 1-2 background. It is
the first active gameplay frame; it does not prove the subsequent spawn motion.
This is a controller-only route with no RAM/PC/health/position writes.

All four opening pipes, gaps and staircases were crossed with ordinary source
jumps. No helper platform was added for Metal Storm, and raw35 is not admitted
to the shared authored helper table. The controller stops to shoot nearby
enemies before proceeding. Earlier attempts that jumped too late underneath
blocks lost a life and remain negative diagnostics, not current passing proof.

This proves the full non-shortcut 1-1 route on the default selected difficulty.
It does not prove every mode, the shortcut pipe, every enemy killed, or any
powerup collected. All powerup flags were false. Those requirements stay open.

## Gravity escape bug

The first pipe test (`metal-storm-pipes-1101-v36/native`) used timed gravity
changes. Its weak X-coordinate-only condition returned true while the actor
was above the visible world. The screenshot contradicts a legitimate crossing.
Do not count it as a pass. The corrected ordinary-jump run (`native-normal`)
requires grounded visible-domain landings beyond each pipe and passed atX1001.
The offscreen upward-gravity escape still needs investigation/fixing.

## Idle/walking performance — still needs reduction

`build/metal-storm-idle-1101-v38/native/capture/performance.json` measures real
foreground loops from `NoDecTimers` to `PauseSkip+2`, including intervening
interrupt cycles. The controller stands for120 physical frames, then walks
for120, without shooting or test-state writes. Final worldX155; no pickup or
life loss. This is the empty opening region, not a synthetic crowd fixture.

| Phase | Completed updates /120 physical frames | Mean CPU cycles | Maximum |
|---|---:|---:|---:|
| Idle | 80 | 34952.2 | 40993 |
| Walking | 77 | 36939.6 | 43195 |

This is about40/38.5 updates per60 physical frames, so lag remains observable
even without firing. No claim of adequate lag or full-roster performance is
made. Next action: profile the actual hot paths and reduce recurring dispatch,
transport or rendering cost while preserving the now-proven route and source
movement. The all-character goal remains active.
