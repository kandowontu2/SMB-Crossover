# Karnov same-life scene motor reset

Private candidate `a3c5fa63872fbb3103ae57d9748fef233e8b2273e26d985aa4006b2492d81b8a`
fixes the actual1-2 entrance death after earning double and triple shot. Root
owns native emulator validation, installation and publication. The installed
input was exact Downloads65ee94ca; no ROM was written by this source task.

The retained original integration packet
`docs/qa/checkpoints/2026-11-01/karnov-hud-nightly-v9/source.zip`, SHA256
`ae5e53e01d7796f6d5beab97668b4f02a270c5dc60027d1cda181b6dfe11f777`,
contains `host/kr-terrain.inc`. KrKeepLife clears original motor timer66 and
accumulators6A/6B. Its facing publication only stores selector62 for leftward
facing2; rightward facing1 keeps the previous source selector. After the
natural castle seam that selector is original jump8, paired with expired
timer0. The first1-2 Main updates underflow that timer and index the original
jump motion incorrectly. NativeY48 becomes44,11,75,158,154,218, followed by
fatal entry. Correct neutral input reproduces this in both CPU and Mesen.
Root negative receipt80dbed86aa36db1bd042e9c2389d03c523469d1e5fae9e1aa25226a5fd3c1cf4,
controller7a880eccf13382d524dab4d4535a9917b50f514aa62c31cbaa45446545af059d.

The same-size source block at conditional raw3/B0D4..B0DF changes
`AD3E05C902D005A9808D62C0` to `AD3E052902F002A9808D62C0`. It reads the native
right1/left2 direction mask, then always publishes fresh donor stand0 or
leftward stand80. Three code bytes change. Both complete authenticated cookie
copies change from `a707011147d338f92c669d26e11e5b71` to
`a7070112fd9d8e091d29e8be18360c27`:29 changed bytes overall. There is no
allocation growth, relocation, native jump change, geometry change or new
helper. Every other roster byte remains identical. All gear, stock, shot
level, original health and collection cycle survive the same-life reset.
The existing source constructor still clears these fields on a new life.
KrCopyArt after the changed block consumes no incoming carry; KrSave/restore
retains its existing caller ABI.

`tools/audit/compose_karnov_scene_motor_1113.py` accepts disjoint roster edits
through the exact Karnov actor preimage and both old headers. It returns only
an in-memory candidate and compact layout. `inverse(candidate)` restores the
exact parent and validates forward recomposition; it creates no backup.
The separate12-byte assembly source is
`tools/reference/karnov_scene_motor_1113.s`.

Completed CPU gates in `check_karnov_scene_motor_1113.py`:

- Actual cold copy/readback:23064 PPU reads, both complete cookies, minimumSP192.
- All256 prior source selectors × both valid native facings through actual
  InitScreen:512 cases. Timers66/67/6A/6B reset, shot/health/gear/stock/cycle
  preserved, callerAXYP `[1,3,0,49]`. Includes expired jump8/9 timer0.
- Exact parent reproduces stale selector8/timer0 under the same constructor.
- Actual four native item collectors retain the original double→triple→Boots→Bomb
  sequence; the mature-actor supply is an explicit fixture.
-11 foreign owners through actual public HuFresh have identical AXYP,
  mapper results and RAM write deltas against the parent.
- Changed-byte cold readback corruption rejects atPPU read9442, carryclear,
  neither authenticated header published.
-121 IRQ and121 lag-NMI instruction/SP cuts through fresh and same-life
  constructors, minimumSP150; caller and bank restoration pass.

Root's actual controller-only native three-pickup route passes in9781 physical
frames/5594 updates, both lives, source shot2/health0. The authored1-1 mushroom
and flower are earned before a normal1-1 clear and1-2 entrance; the1-2 flower
at160 matures and is genuinely collected to grant Boots (cycle1/owned1/option0).
Receipt `4d0e7e4ffbf11b56b4aad0f18d87da629804d00f7993de9499687a8fe96b90e0`,
script `57763e630aeae8ea0a0792646dd200bec841410b72942b1d1cde89af96754f35`.
Existing controller-created helpers:1-1 left1201/center1217/initialtop208 and
1-2 left112/center128/initialtop208, width32; fixed1-1 pipe helpers688/704/208
and872/888/208 remain. Full details are in the helper inventory.

The full CPU controller route is still running at this note's initial write.
Its independent final result will be appended. The bounded command is:

```
python -B tools/audit/run_bounded_build_v1.py --output build/karnov-scene-motor-cpu-1113 --max-files 1 --timeout 600 -- python -B tools/audit/check_karnov_scene_motor_1113.py --route --stop-after 3
```

Zero generated files. Natural fourth flower/Bomb acquisition and use remain
pending, and Ladder, Clapper, Glasses, Swimming Mask and Shield remain required.
