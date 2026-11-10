# DK Jr. four-pipe allocator funding

The funded source fits the existing DK Jr. worker and owner memory. From
exact installed a20d it assembles to in-memory candidate
`b031802c7bc4f4e9596683e66f2f53c124b3a3ac155b80bbec03c5965b8e4e65` with
cookie `a72801c55e103955b97b9a5ed589fcd2`. The builder changes only DK Jr.
carrier pages 881, 883, 960 and 961 and its existing cookie slot. The
active atlas and redirected hanging-fruit sprite pairs retain their bytes.

| Use | CPU range, half-open | Bytes |
|---|---|---:|
| Platform refresh | `$B624..$B6A2` | 126 |
| Ordinal bases | `$B6A2..$B6A5` | 3 |
| Box override | `$BD3C..$BD44` | 8 |
| Pipe scope, admission and stock birth | `$D18B..$D200` | 117 |
| Packed cold worker | `$D25E..$D2C4` | 102 |
| World X and oscillator tables | `$D2C4..$D2D4` | 16 |
| Camera starts | `$D2FC..$D2FF` | 3 |
| Camera masks | `$D7FC..$D7FF` | 3 |

The refresh reaches its empty return with N set by the final `DEX`, so a
short `BMI` replaces its jump. The native relative-position routine returns
X from `ObjectOffset`, removing the repeated reload in the private caller.
This supplies the three ordinal bytes. An empty native slot leaves A zero
and the admitted worker preserves carry set through the slot search. That
lets birth compute the actor page with `ADC ScreenLeftPage`. An eight-entry
oscillator table removes the two instructions needed to halve the ordinal.
The native ID `$25` constructor retains X and never accesses `ObjectOffset`
in the scoped stock branch. The existing box 5 override still executes.

The actual cold leaf returned with all 8,192 code bytes and 2,048 metadata
bytes equal to their carriers on both a20d and b031. The comparison runs at
the leaf return before the original constructor writes its mutable address
operands. Both complete headers then commit. The refresh comparison passes
810 cases across all six slots, the nine native platform IDs, active and
inactive flags, and five screen positions. AXYP/SP, native working RAM,
object output, SMC, mapper/PPU state and non-stack writes agree. Moved
return addresses account for the dead stack differences.

The admission proof passes 9,216 camera/ordinal combinations and 96 real
native retry-and-create cases. Each uses a full native slot pool before
releasing one slot. The new actor acquires the specified X, initial top,
oscillator center, and box. The five other slots retain their active IDs.
Wrong loaded room and warm life reset checks pass.

| DK Jr. stage 1-1 girder | Left X | Center X | Initial top Y | Oscillator center Y |
|---|---:|---:|---:|---:|
| First ascent | 416 | 432 | 192 | 128 |
| First descent | 480 | 496 | 192 | 128 |
| Second ascent | 560 | 576 | 192 | 177 |
| Second descent | 624 | 640 | 192 | 177 |
| Third ascent | 688 | 704 | 192 | 169 |
| Third descent | 752 | 768 | 192 | 169 |
| Fourth ascent | 880 | 896 | 192 | 161 |
| Fourth descent | 944 | 960 | 192 | 161 |

The third and fourth placement fixtures and the unassisted first-gap jump
have their own [geometry report](dkjr-third-fourth-geometry-1110.md).
Continuous controller and Mesen verification of b031 remain separate.

The pure builder is `check_dkjr_four_pipe_funded_1110.proposal(a20d_raw)`.
It returns the in-memory bytes, cookie and linked labels. With exact a20d
in Downloads, run the CPU suite with the existing one-file budget.

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -B tools/audit/run_bounded_build_v1.py --output build/dkjr-four-pipe-funded-1110 --max-files 1 --timeout 600 -- python -B tools/audit/check_dkjr_four_pipe_funded_1110.py
```

The suite writes its result to stdout and retains zero build files.
