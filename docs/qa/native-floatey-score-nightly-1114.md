# Shared popup score correction — November 14

The natural Mr Gimmick mushroom check exposed a shared score-table defect.
The popup says1,000 while the six native score digits increase by100.
Native run81769 and source62984 retain this negative without weakening the
score assertion; see `gimmick-natural-mushroom-1114.md`.

Candidate `5715bb7e3c772350a2a7420ec9061eabd948964a8789e5d348c49d3cfb3c57ee`
changes exactly ten table bytes over deliveredF11, at file1034694,
PRG126:`$89B6`. The first five award controls use digit3 for100..800 points;
the next five use digit2 for1,000..8,000. The final zero extra-life entry,
all instructions, fixed addresses, artwork, physics, helpers and all earlier
fixes stay exact. The corresponding source table in `src/game.s` agrees.
Manual coin and timer awards are separate and outside this correction.

Root source26572 PASS:468 declared actual-code component cases on F11 and
468 on the candidate cover all ten controls, carry/wrap across six digits,
no-popup and extra-life/clamped controls, and four incoming status values.
The genuine mushroom route also passes its original unchanged1,000-point
assertion: score100→1100, capacity/health2→3, cue45, erase and25 further
movement calls. Source receipt
`752287c12557c2138e7049a2c7a3fcf53b3b5d74d410ba0cfa3780fd87f56b2a`.
The component fixtures are explicitly separate from controller-only gameplay.

Root79519 private Mesen PASS with Lua
`87ecd7d56e4e29f16a8e1e1bf9f8f2add1719ec5f0f226adf2ad755143341e84`,
receipt `ad76099f9cfa67a80df6bfa0b7a741d7d853ee03e78a63dbda71a61722f8e652`.
The actual early Goomba awards100, then the mature mushroom awards1,000.
Birth/maturity/collector, health, cue and movement counters match the F11
negative:698 completedMain/809physical frames,405 GmMovement entries,
terminal430/176, health/capacity3, lives2, power1, Star0. There are no actor
seeds, state writes, screenshots or capture files. DownloadsF11 remains exact
through this private run, with clear pre/post sidecar guards.

This qualifies native score awards and this natural mushroom route, not a
fresh whole-roster/full-level audit or an audible cue check. Actual Downloads
delivery is pending its separately recorded repeat.
