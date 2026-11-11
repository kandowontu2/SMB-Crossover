# Prince’s 1-1 side contacts, November 11

The installed ROM `4df817587ea5b0aff3f278a4201976745bad4d9dd1b2a99d6cb5fd3b9c74dadc`
ran from the existing translated third-pipe CPU scene. Controller input,
native terrain and enemy parsing, GameLoop and normal NMI produced two live
ground enemy contacts after the second gap.

| Enemy and update | Prince X/Y | Enemy X/Y | Player box and enemy box | Previous/current sole Y |
|---|---|---|---|---|
| Goomba, 1298 | 1516/176 | 1527/184 | 1518,185,1530,209 and 1530,198,1540,204 | 209/209 |
| Green Koopa, 1923 | 1661/176 | 1672/184 | 1663,184,1675,208 and 1674,193,1686,205 | 210/208 |

Box coordinates are left, top, right, bottom in world pixels. Both contacts
occurred in original running action 1, with Prince’s previous sole already
below the enemy’s top and all six protection fields at zero. Each contact
reached `FE:976C InjurePlayer` once, then `3:BD22` and the translated
defender at `2:DADD`. Four writes at `3:A342` reduced HP from 4 to 0 and
the defender selected original death action 85.

The original NES ROM
`5f14d4d31cc588ddcdfb2b4d46eb7051b06d02655c9208037ef7ae137c4740e4`
reproduced each captured unarmed defender state at `4:ACEC`, including the
same actor bytes and four HP debits at `5:8725`. Explicit donor-only
sword fixtures gave HP 0/action 85 for modes 0 and 1, and HP 3/action 74 for
drawn sword mode 2. The donor checks mode 2 at `4:AD0C`; the unarmed
response calls the debit routine five times at `7:E9A4`, stopping HP at zero.

The original game reaches its defender from an attacking actor’s sword
pose 154 at `4:ACD6..ACEB`. The crossover uses valid damaging SMB enemy
contacts as the input to that defender. The two side overlaps passed the
host’s native collision checks and followed the original damage response.
The witness gives no reason to change contact, health or protection policy.

The checker starts from a translated CPU scene and observes naturally
parsed enemies. It writes no ROM, report or capture files, and leaves the
bounded output directory absent. Physical replay and a full 1-1 clear are
outside this witness.

## Reproduction

Checker SHA-256
`8dd1a644462b6834ed8747e2257c7114f109df5b5cee51b4801e7b9bba74cfbe`.

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -B tools/audit/run_bounded_build_v1.py --output build/prince-side-contact-1111 --max-files 1 --timeout 600 -- python -B tools/audit/check_prince_side_contact_1111.py
```
