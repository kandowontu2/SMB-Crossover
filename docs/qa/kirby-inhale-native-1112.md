# Kirby inhale contact ordering

On installed `f228e61399432c1a205b8f5ac6dad13d990515f9c2e2f5024bcd5ce443c76653`,
Kirby can capture a Spiny and lose it to the adjacent Lakitu in the same update.
In Easy and Hard, fresh B at X112 with Lakitu 14 pixels ahead starts suction
and protects Kirby from the approaching Lakitu. On the second held-B update,
Suction captures the Spiny spawned by Lakitu's native behavior in slot 1 and clears inhale.
The later native contact from Lakitu in slot 0 then sees action 0, injures Kirby
from 6 to 5 HP and clears the mouth. Both witnesses run through the real
GameLoop, enemy initialization, actor update, contact bridge and injury handler.
Actor positions are directed CPU fixtures.

Candidate `d8e9b6871f56139f355f5b3ef42a0ffa56a26b0b3b17ab8d286f5ff76082a8c0`
keeps the current inhale action for the remainder of a capture update. The
capture tail sets its age to 1 and the next weapons update clears the action
before reading mouth input. An edible enemy in front within the existing
suction bounds uses the ordinary inhale protection on the capture update.
Kirby has HP 6 and Spiny copy 11 in the mouth. The same Lakitu still injures
Kirby on the next update when B remains held and Kirby stays in contact.

The installed body predicate accepts a positive family, enemy page 1, forward
world X distance 0 to 56, world Y difference -4 to +20, and active B inhale. It
protects during startup and held suction. Underwater B uses the authored water
projectile branch. Rear contacts, targets outside vertical range and Bowser's
flame can still injure Kirby on the same update he captures another enemy.

## Source and verification

`tools/reference/kirby_inhale_capture_frame_1112.s` uses 27 and 11 bytes in
the existing PRG74 `$A092..$A0B0` and `$A31A..$A326` spans, with six bytes of
padding. It uses the existing action clock and mouth flag. The existing capture
entry, native erase call and return entry keep their addresses. Source SHA256
`03b5152bb3146f2bb7084a12387af8d491630fe4442537479739ea564c4cc467`.

`tools/audit/check_kirby_inhale_native_1112.py` authenticates the installed
owners, composes the exact preimage edits in memory, and runs the cartridge CPU
paths. `proposal(raw)` returns `(candidate_bytes, info)` with exact file edits.
The CPU harness enters gameplay through Kirby's actual menu selection, Start
and native parser, then observes the real IdleLoop caller and GameLoop.

| CPU check | Result |
| --- | --- |
| Family admission, all 256 IDs and representative flag/state/slot values | 11,520 calls, 210 accepted and 11,310 rejected |
| Dry first update, 18 inhaleable IDs, both facings, both difficulties, seven distances and B on/off | 1,008 cases, 136 captures, no front+B damage, 268 other injuries |
| Dry through nine updates, same matrix | 1,006 matched outcomes, two corrected Lakitu witnesses, 248 captures. Injuries drop from 298 to 296. |
| Close vertical boundary matrix | 720 matched cases, 204 captures and 180 injuries on each image. All 28 front+B injuries occur outside vertical eligibility. |
| Underwater first update | 1,008 matched cases, 252 injuries and zero captures in the water projectile branch |
| Matched same-frame two-actor controls | 4 protected front edible contacts, 4 rear injuries, 4 injuries outside vertical range, 4 Bowser flame injuries |
| Capture lifecycle through later input | 12 Down swallows, 4 released/repressed B spits, 4 mouth holds |
| Native vector continuation | 19 NMI and 19 IRQ instruction cuts, one nested IRQ at foreground SP183 |

Run the checker through the bounded runner. Each command writes zero files.

```text
python -B tools/audit/run_bounded_build_v1.py --output build/kirby-inhale-native-1112 --max-files 1 --timeout 180 -- python -B tools/audit/check_kirby_inhale_native_1112.py --part capture
```

Other suites use `--part families`, `--part land`, `--part land --held 8`,
`--part vertical`, or `--part water`. Add `--compare` to a land, vertical,
or water run for paired old/candidate outcomes. Run held-land comparisons
once with `--face 1` and once with `--face 2` to fit the 180-second bound.

Root's controller-only Mesen replay on the candidate passed Hard close-left
inhale. Capture at frame 816 and completion at frame 818 left Kirby at HP 6,
lives 2, mouth 7 and mouth copy 1. The existing post-erase observer needed the
new exact instruction bytes at `$A31A`. The corrected receipt is
`384a93927211cb375290bef04b98753d56e37ab5bb48b6dac4d5499527bee37b` and
the controller SHA256 is `ab88ad92e07d73a1b6f9f251f573f760976bf0baea9f451b1e913ed7285cc26d`.
The Lakitu/Spiny result is qualified in the CPU fixture. A controller-only
Lakitu encounter and a full underwater stage are outside the replay scope.
