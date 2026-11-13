# Passive Karnov native suffix diagnostic

Root's default d6 replay again stopped at physical24001 /13559 epochs,
four genuine pickups and underground353, no new helper or images. Passive
image Lua `3bd75937f972ae7fb096f08fdd315aee092dc88b19d550675986b981782be72e`
and receipt `91c91cffa6e5e436797461d3f689629bd9e62d2491db6891bdedaf6df62c6b02`
are recorded by root. The compact
receipt omitted the suffix state, so neither a runtime defect nor the reason
the suffix skipped the wall is established.

This separately named factory authenticates the exact unchanged d6 text:
`replay_karnov_ladder_suffix_diagnostic_1113.controller(exact7ef)`.
It records every suffix call's gate, all last gate inputs, handled/pad result,
done/stage/bypassed transitions, and the whole control's final requested pad.
It also records native SavedJoypadBits/1Bits, source held/pressed/flags,
routePhase and actual actors in all six slots at the wall. Full nav and
diagnostic state are top-level receipt fields as well as under fifth.

The wrapper returns exactly the original controller values; it does not
change inputs, game fields or ROM. Only the diagnostic terminal condition is
added: after four items and180 consecutive physical endFrame observations at
the same X in351..359 in1-2, it emits a false receipt with reason
`passive-diagnostic-wall-stall180`. The last twelve samples, one per15frames,
are bounded. This is not an acquisition or game-clear qualification. The
frozen d6/7d1 factories and both successful Bowser item controllers remain
unchanged. No emulator or generated output is owned by this task.

The compiled diagnostic Lua SHA-256 is
`1b998db9a3758e697e1ccc6eecffcc85097370767aaa1cad5f3d575666a41937`
(46,620 bytes). A bounded synthetic observer-only check compared twelve gate
cases against the actual unchanged nav source and confirmed identical
handled/pad/done/stage/control returns. It also verified the exact180-frame
false stop, twelve-sample cap and six actor slots. These are tests of the
instrumentation, not newly seeded game fixtures or actual Main/native replay
qualification. Root owns the next actual Mesen diagnostic.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/karnov-equipment-1113 --resume --max-files 1 --timeout 180 -- python -B tools/audit/replay_karnov_ladder_suffix_diagnostic_1113.py --self-check
```

The top-level receipt fields to retain are `native_suffix` and
`native_suffix_diagnostic`. The latter separates `last_control` from
`last_nav`, allowing a skipped call to be distinguished from a gate inside
the nav function. `first_bypass`, `first_done`, `min_x` and `max_x` preserve
evidence if the route crossed416 and later returned to353. `requested_pad`
is the unchanged complete control return; native pad1/SavedJoypadBits are
separate reads. No exception is inferred for Buzzy or any other native actor
before the actual diagnostic identifies the source of the stall.
