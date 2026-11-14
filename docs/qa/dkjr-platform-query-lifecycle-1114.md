# DK Jr legal platform-query lifecycle — November 14

`jump_age == 0` is redundant **at the current `Platforms` ingress**. Every legal
source-state3 query reaching that leaf has age at least3. This supports omitting
the separate five-byte age check from a source3 rising-platform predicate at
that location. The signed acceleration-minus-impulse check remains necessary:
ordinary upward jumps query platforms at age3 and later.

This is a source/caller proof plus ordinary controller witnesses on exact private
`769afe8d7fcdb58bed5f9f43109d7aabab3d93b1a7afb0535926e51cffce94ff`.
It neither composes nor qualifies a new game image. The fit owner and root retain
allocation, candidate and native-test ownership.

## Why the apparently dangerous fresh query cannot reach Platforms

The original `D_d291` jump transition really clears `C07E` without clearing the
previous acceleration `C083:C082` or impulse `C087:C086`. A legitimate repeat
jump therefore can begin with age0 and a nonnegative stale signed difference.
The controller witnesses below observed this directly. The broader claim that
every source3 query has already initialized gravity would be false.

The relevant query classes are original `E893` vine0, `E897` hand1, `E89B` wall2,
`E89F` support3 and `E8A3` platform4. `D_d5D7` first asks vine0. It then executes
`LDA C07E / CMP #3 / BCC D_d5EE`, so support3 is skipped at ages0,1,2. `D_d5EE`
asks wall2. Current `NativeObjects` admits classes0/1 to the vine path, returns
for wall2, and branches to `Platforms` only for classes3/4. Thus neither fresh
query can run the proposed platform predicate.

After those initial queries, `D_d913` calls `D_e9AE` before reading the latched
direction `C054`. At age0 that original gravity routine sets acceleration high0,
low8 and fraction`F0`, applies the existing impulse, then increments age. All
five original directions (neutral/up/down/left/right) share this order, including
both forward and backward horizontal jumps. Gravity initializes acceleration,
not the retained impulse; this proof does not assume that initialization happens
before the fresh vine/wall queries.

## Complete current support callers

The conservative literal JSR/JMP census covers both executable carriers: WRAM3
`A000..BFDF` and metadata WRAM2 `D000..D7FF`. It finds precisely these five
support3 callers, with no additional literal caller:

| Original site | Current PC | Legal state at the query |
| --- | --- | --- |
| `D_cf49` | `A140` | Defeat state5 |
| `D_d575` | `A318` | Ground state1 |
| `D_d593` | `A338` | Vine state2 |
| `D_d5e7` | `A396` | Jump state3, dominated by age>=3 |
| `D_d631` | `A3E8` | Fall state4 |

The ground and vine paths change state only after their corresponding query;
they do not create an age0 source3 platform query. `DkjrNativeSourcePhase` calls
input before transition and movement, and skips input for already airborne
states3/4. Native bounce writes state3 and invokes `DkjrJumpRestart`, which
restarts the ordinary transition at `D_d257`; its next jump movement still passes
the same age gate. Constructor startup does not bypass that movement path.
Even an age-byte wrap would re-enter the gate's skipped0/1/2 interval, so this
proof does not need a finite airborne-duration assumption.

The defeat query is reached through native Phase/SourcePhase death branches
guarded by state5, or the native death API that calls Damage before DefeatTick
when not already5. The current standalone class4 wrapper has no literal caller,
no DkServices entry, and no named probe consumer in the native `src/*.s` sources.
The only WorldBuild JSR is the terrain hook. The only literal transfer to
`Platforms` is the class3/4 branch in `NativeObjects`; frozen `ObjectsDone=B54B`,
`Platforms=B54C` and the existing `LDX #5` entry are unchanged.

Calling an exported query wrapper manually with a seeded age0 state would be a
defensive ABI fixture outside these legal current callers. This proof does not
permit removing an age check from an earlier generic WorldBuild ingress or from
a future caller that can actually submit age0 support/platform queries.

## Byte binding and controller witnesses

The checker reassembles seventeen relevant source fragments in memory and
requires their complete bytes to equal exact769: input, defeat support,
transition, movement dispatch, ground/vine, jump support gate, fall support,
directional jump, gravity, all query-class wrappers, terrain hook, WorldBuild,
NativeObjects, Phase/SourcePhase, native bounce and native death. It reassembles
the complete retained source only to recover private labels omitted by the
published map, and requires every published address to match that map.

Current WorldBuild contains the earlier signed-terrain repack. The checker
rebuilds its small retained reference, including the relocated row pointer, and
checks the resulting entire418-byte current WorldBuild span. It does not
silently equate that span to the older original text.

The controller arm uses the genuine cold menu/Start/constructor source arena,
finishes the opening hop with ordinary Main frames, and requires the real
manager's exact769 cookies in both WRAM banks. It then performs two ordinary
static-floor jumps for each original direction in each facing orientation:
twenty launches, each returning to source/prior state1 after46 Main steps.
Neither source state, acceleration, impulse, age, terrain nor actor state is
seeded. It invokes no query leaf directly.

Terminal PASS counts:

- 2,800 World queries during the measured jumps and settling steps.
- 900 actual Platforms entries, including840 in source3.
- 40 legitimate source3 age0 queries, all vine0/wall2; zero age0/1/2 source3
  Platforms entries.
- Each route's first source3 Platforms entry was step4, age3, acceleration40,
  impulse352, signed difference`-312`.
- The real age0 stale witness was acceleration696, impulse352, signed
  difference`+344`, fraction240. Both vine0 and wall2 saw it. The second jump
  repeated the same legitimate stale condition after ordinary landing.
- Actual sampled launch directions0..4 and both requested facings are asserted.

Bindings:

- Checker `tools/audit/check_dkjr_platform_query_lifecycle_1114.py`:
  `c542d3f397e7714089191f2a4192875cbf6998f9da35812409d89cd0adcb4a61`.
- Frozen source `native-entrance-v89.s`:
  `82cca72d6091ca2569093e7fd35aba55f43e0d191de06224d8b2335e316c839d`.
- Frozen public labels:
  `0d3926e7791164c76f3727a35b748ebddf5357d58b28891473fbd05dcb1998be`.
- Signed-terrain reference `tools/reference/dkjr_scroll_publish_1110_v1.s`:
  `41ee050c7fc80ec323f7af27214750687bb5554d16ea2c86e53845ed6f3d53f6`.
- Full aggregate in-memory result:
  `0bf29a8e8a6410a1c6e4cd77c4b34190fd9e6220bf600ef8e48bab7c03ec6151`.

Reproduction:

```text
python -B tools/audit/run_bounded_build_v1.py --output build/dkjr-platform-query-lifecycle-1114 --max-files 1 --timeout 600 -- python -B tools/audit/check_dkjr_platform_query_lifecycle_1114.py
```

The terminal invocation returned0/PASS. The bounded output directory was never
created: zero generated files, ROM outputs, images or Mesen runs. Only the new
checker and this QA note are owned changes. The source result funds the narrower
legal-ingress proposal; native traversal and full defensive ABI preservation
belong to its separately qualified successor.
