# Kirby inhale safety follow-up, November 13

Input nightly: `a3c5fa63872fbb3103ae57d9748fef233e8b2273e26d985aa4006b2492d81b8a`.
Kirby PRG74 SHA256:
`119a6fe415a914c415a51bc46f0cc22569cd4c7e1282d83f512c3b2031573e9d`.
The delivered capture-frame and red-catch code authenticate by exact inverse
preimages and source forward recomposition. No ROM change is proposed yet.

The retained1112 audit already covers the18 positive mapped IDs at ordinary
distances, both directions/difficulties, vertical boundaries, water branch,
the Lakitu/Spiny same-capture update, and green/red shell behavior. This
follow-up does not rerun those passed suites or claim new emulator coverage.

New explicit CPU fixtures cover initial front gaps0..5 for all18 named inputs,
both facings and both difficulties. Actual native enemy initialization and the
real reset-tail/IdleLoop/GameLoop caller execute. Walking velocities are
mirrored as legal actor-data fixtures; no ability, result or executable bytes
are seeded. All432 cases retain HP6;408 capture an enemy. The24 noncaptures
remain separated from a claim that every initializer yields a live visible
actor. No front-start contact-order injury was demonstrated.

Source: `tools/audit/check_kirby_inhale_safety_1113.py --part boundaries`, run
through the bounded runner with Python `-B`. All results remain in memory;
zero outputs, captures and Mesen launches. No allocation is requested.

Remaining scope: live native state changes including enemies descending below
the visible playfield, front/rear contacts after another capture, and actual
mouth→spit/copy attacks against grounded native targets. The general non-shell
projectile Y-page admission also needs a current witness; the older source
audit flagged it separately from the already repaired shell contact helper.
Those are investigation targets, not new qualified defects or delivered fixes.

## Follow-up on installed Quick/Jay, November13

The added sections freeze one complete ROM read in memory per invocation.
Initial runs use installed Quick4641
`4641ca4fb72699c0478e31b831d4c4ea0ffd2227be7f8446666092d2cc26e1d3`;
later runs use installed Quick+Jay
`aa50112845d1cf70cae0924f03326647b3d2514f876c756d70b134ee44f971d1`.
Both authenticate the identical complete Kirby PRG74 hash above, the current
125-byte GameLoop and the retained input/body/owner callbacks, plus capture
and red-catch source inverse/forward closure. No unrelated character bytes
are rehydrated. The original432-case test is retained rather than rerun.

All tests below are explicit actor/terrain data fixtures after actual Kirby
menu/parser entry167 and40 settling updates. The reset-tail/IdleLoop/GameLoop
instructions and normal NMI-consume step execute. No ability, copy, mouth,
shot, grant, health, result or executable code is injected.

- `frenzy-initializer`:24 targeted checks explain the original24 noncaptures.
  The genuine FlyingCheepCheep constructor relocates the input actor from
  requested gaps0..5 to worldX65520 (signed−16) with this native PRNG state,
  outside the tested mouth, while retaining active flag1 and positive family8.
  It does **not** clear the actor flag or make this type non-inhaleable.
  Four separate declared legal-position fixtures restore only NPC X after
  that constructor; both facings/difficulties then capture mouth21/copy8 atHP6.
- `compound`:128 new two-enemy cases. Goomba in slot5 is captured first;
  another16 named types in slot0 are in front or behind, both facings and
  difficulties.60 eligible front contacts remain protected atHP6 with the
  captured mouth retained.60 rear contacts still damage toHP5/clear mouth.
  Eight FlyingCheep constructor-relocation cases have no contact, yielding
  120 total actual body calls,60 injured/68 uninjured. The existing specific
  Lakitu/Spiny capture witness is not rerun.
- `descending`:ten cases, Goomba/GreenKoopa/Buzzy/HammerBro/Spiny × both
  facings. A declared pit opens only under the NPC while Kirby stays on
  supporting ground. Actual native gravity reaches Y197 at update11; B is
  then held through descent and native retirement at update31. No enemy is
  pulled or captured below eligibility, HP remains6. All20 remaining NPC
  updates per case match a paired B-released control exactly in live native
  flag/state/ID/XY/page/velocity/force fields (200 paired updates total).
- `ground-pull`:ten longer56-pixel inhale approaches for those five types,
  both facings, reach actual capture in19..27 updates atHP6. Ordinary bodies
  stay Y184/page1 with native foot208. Hammer Bro naturally jumps to178 and
  returns184; it is not forced flat. None is buried below the ground.
- `plant-cycle`:two genuinely initialized PiranhaPlant actors, native down192
  and up168. The source movement completes rise/wait and starts a downward
  leg. B begins only after actual descending Y180 at update133; capture is
  update152, mouth14/copy12/HP6. Y stays180..185/page1. This is a native
  movement-state fixture, not an authored-pipe occlusion or visual test.
- `ground-actions`:32 cases earn a mouth or copy by real inhale and optional
  Down swallow, then use a fresh B attack against initialized grounded Goomba
  and GreenKoopa targets in both facings. Spit, Hammer5, Jet6, Bubble7,
  Wave8, Needles11, Bite12 and Fire13 all reach actual ShellOrBlockDefeat,
  native defeated state34 andHP6. Copied family remains exact. These are
  close-range grounded contacts, not a qualification of every attack range,
  trajectory, animation, pool-pressure condition or original donor behavior.

No new live contact-order or ground-alignment defect is demonstrated by those
cases, and no ROM change or allocation is proposed.

## Unresolved synthetic projectile admission

`projectile-pages` independently earns Goomba in Kirby's mouth, releases B,
and spits a real star at one initialized target in slot3. Only the target's
Y-high byte varies0/1/2 while lowY184 and legal visible X are held constant.
In six real GameLoop fixtures, both facings, generic non-shell EnemyContacts
calls actual ShellOrBlockDefeat on every page before native cleanup. ShotY196
and target lowY184 alias across the high page; page0/page2 hits are wrong as
world-space intersections. The real star is consumed; page2 native retirement
occurs later in the same update. This is stronger than the old isolated-leaf
observation but still uses deliberately seeded off-page NPC states.

`native-podoboo` tests reachability without writing target Y after native
construction. An earned mouth remains held while a native Podoboo runs700
GameLoop/NMI updates per facing. Each starts high2/Y2, has two page2 updates
and698 page1 updates, resets through its actual timer/physics, and never
reaches the off-page lowY184..208 alias. The ten descending native walkers
also retire before reaching it. These finite states do not establish that
every native lifecycle is safe; they provide no naturally reachable witness
for this alias. It remains a scoped admission concern, not a newly delivered
gameplay fix. Bowser fallback and copied bite off-page admission are not
qualified by these six star cases.

Run any named section through the same zero-output bounded runner, for example:

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/kirby-inhale-safety-1113 --max-files 1 --timeout 180 -- python -B tools/audit/check_kirby_inhale_safety_1113.py --part descending
```

Only `check_kirby_inhale_safety_1113.py` and this note change. No emulator,
captures, output roots, ROM, release, helper placement or shared inventory
changes. Full natural-stage/original-ability review remains a separate goal.
