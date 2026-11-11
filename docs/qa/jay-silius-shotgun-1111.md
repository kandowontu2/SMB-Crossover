# Jay McCray donor weapon selection and three-way shot

The donor is Journey to Silius (USA), SHA-256
`12f5c5e413a2aa5bff75b5077e4477497d7e49aa432560c2e8c3fd3cc71910cc`.
The detached host test uses exact installed
`b1d449ebd7bbcc6f9c75be00891afc627a8354acb56a18bb9cd7a4ef40129576`
with the released Jay stock cookie `a7102007de73e237c21c140b1055419b`.

## Donor weapon table

The inline dispatch at PRG6 `$81DE` selects six rows through fixed
`$CD36`. The nonzero cooldown at `$81D2` runs before every row. Velocity
bytes are signed sixteenths of a pixel. Projectile kind indexes the
original fixed `$C50E` update table.

| Row | PRG6 fire entry | Input | Ammo and cooldown | Spawn behavior |
|---|---|---|---|---|
| 0 | `$844E` | New B press | Free, 4 updates | One of three slots, kind 0, horizontal `$40`, damage 1 |
| 1 | `$8480` | Held B | 1 ammo, 4 updates | One of five slots, kind 0, horizontal `$50`, damage 1 |
| 2 | `$84C0` | New B press | 2 ammo, 4 updates | All three slots must be free. Kind 0 pairs `48 1A`, `48 E6`, `50 00`, damage 1 each |
| 3 | `$85ED` | New B press | 4 ammo, 12 updates | One slot, kind 3, horizontal `$40`, damage 2, retained on an enemy hit |
| 4 | `$8521` | New B press | 3 ammo, 8 updates | One of three slots, kind 1, horizontal `$30`, damage 3, original rotating enemy search |
| 5 | `$85A8` | New B press | 6 ammo, 8 updates | One slot, kind 2, initial horizontal `$0C`, damage 5, timer 16 before acceleration |

Rows 1–5 share ammo `$B1` and call the original spend leaf at `$8E20`.
Zero ammo at entry returns to stock. A nonzero amount below the cost
still allows the accepted shot, then clears ammo and selection. The
type `$22` pickup reaches fixed `$E82C`, consumes the pickup actor,
requests sound `$18` and adds 16 ammo up to 63. The pickup does not
change the selected weapon or erase Jay's actor.

The actual paused Select loop is PRG1 `$9644`. It respects the original
`$0608` lock, skips rows absent from the `$B7` unlock mask and wraps through
stock. A fresh donor game starts on stock with ammo 63 and mask `$02`,
so row 2 is immediately available. Stage masks at fixed `$DCC9` are
`02 03 0B 0F 1F`. The donor's stage-clear pickup at PRG6 `$99AF..$99CB`
ORs masks `01 08 04 10 00` from `$99CC`. The grant order is therefore
row 1, row 4, row 3, and row 5 after the initial row 2. Those later
grants are static source findings.

An SMB adaptation can preserve the donor's initial stock selection,
paused Select and starting ammo, award the remaining rows on native
stage clears in the donor order, and spawn the 16-ammo pickup through an
authenticated Jay enemy-drop route. This leaves the original SMB item
and invulnerability behavior available for separate integration.

## Executed checks

From a genuine donor new-game controller opening, Start enters the real
pause menu, Select picks row 2 on frame 1526, and Start resumes. The
first actual B burst on frame 1567 spends 63→61 ammo and creates all
three original projectile records. Continued held B produces no extra
burst. The controller supplies all input for this donor route.

The relocated adapter matches 300 original donor firing cases, 144
original paused-selection cases and nine original refill cases. The
input comparisons include AXYP/SP, private actor state and all 48
projectile bytes. The refill cases separately verify pickup consumption
and preservation of host player flags.

The angled flight uses original tentative Y, side-before-vertical
contact, signed commit and floor snap. All four probe directions use
the donor's one-point `$D097` record. The 64 full donor projectile
comparisons feed the real host D002 class back to the donor boundary.
Both CPUs compute the same 128 probes and full records. The host adapter
returns 72 clear and 56 blocking results.

The host controller cold-starts the released Jay path and then attaches
the proposed code and the proven donor selection in detached private
RAM. The following 22 ordinary Main updates use controller input. A real
B edge at update 4 produces these first projected rounds, in slot order.

| Slot | X | Y | Signed velocity bytes |
|---|---:|---:|---|
| `$D0` | 57 | 191 | `$50`, `$00` |
| `$E0` | 56 | 189 | `$48`, `$E6` |
| `$F0` | 56 | 192 | `$48`, `$1A` |

The existing production renderer and regular NMI publish matching stock
CHR216 OAM cells for the active rounds. Jay retains two lives and 61
ammo. The attachment is a directed host fixture. The released SMB pause
menu, progression and ammo pickup have yet to call these leaves.

The proposed fire and flight section is 390 bytes and the selector and
refill section is 123. The present CHR218 payload has 22 bytes left, and
the preserved CHR216 art leaves a 352-byte blank tail. Together they are
16 bytes short of the fire and flight code even before another transport
or UI hook. No new cartridge allocation, ROM file, build output or
Mesen run was made.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/jay-silius-shotgun-1111 --max-files 1 --timeout 600 -- python -B tools/audit/check_jay_silius_shotgun_1111.py
```

- Source SHA-256 `c63bd4041dc5f0d825ab3810749c6d88b5474c1289e5a5112070fdc26af6e05a`.
- Checker SHA-256 `a898b160457716d43e3b9858173f40525cc253c935b4a77eb6cc5a2e9e0e6a9a`.
