# Metal Storm weapon-item source recovery

The first flower can grant the donor's **item 0 upgraded-shot mode**, using its
complete original grant. The existing current actor already consumes that mode
and creates original type `$81` shots. GravityFire and the third effect need
additional object work and must not be enabled by cycling repeated flowers.
This is a proposed native item adaptation, not an implemented pickup.

The donor is `C:/NES/Metal Storm (USA).nes`, SHA-256
`22e7576958e842c564153bf799293cedf90c6a0aaee302b73ec8af88a7481d87`.
The source reads `docs/qa/checkpoints/2026-11-02/metal-reservation-v42/inputs.zip`
in memory, SHA-256
`f1548d2f32972aa150939ab9b33ab829aa4f19f60013cf813031ac21888724e9`.
The final check independently confirms that its actor, renderer and extra code
carriers match the actual installed ROM
`6d0346164b7099f8e75cdbe22a9e9f1fd5f4f673116fd1dcb48a3cee620734c2`.
No expanded source tree or candidate ROM was created.

`tools/reference/metal_weapon_items_1112.inc` semantically reproduces all 90
original bytes at fixed PRG bank15 `$E7B3..$E80C`. With
`MS_WEAPON_ITEM0_ONLY` defined, it provides the 41-byte item0 body and shared
pose/sound tail. Both forms are assembled and tested entirely in memory.
The source checksum is
`c5a9317019692fe5011fe6bff7a1f92cfc174aa63933fe7d1040ff55259beba1`.

| Actual donor entry | Selection and state effects |
| --- | --- |
| `$E77B..$E79E` | Reached item dispatch: reads slot `$60`, then `$04F8,X` plus 8 when `$04E0,X` bit0 is set. Table is `$E79F..$E7B2`. |
| `$E7B3`, table row0 | Sets `$0718=$80` and `$0499=$80`; clears `$0717`, `$043C` and `$0511`; enters the shared pose/sound tail. |
| `$E7C9`, table row1 | Sets GravityFire `$0717=$80`, copies facing `$043F` to `$043E`, sets `$074A=2`, clears `$043C/$0718`, and enters the shared tail. |
| `$E7E1..$E7F3` | If player state `$04E0` is 5, changes it to 4 and returns. Otherwise queues original sound `$0A` in `$07E7`. The state-5 path deliberately does not queue that sound. |
| `$E7F4`, table row2 | Sets third-effect `$043C=$80` and `$0499=$80`; clears `$0717/$0718/$0511`; queues original sound `$0A`. This recovery does not establish the complete third effect. |

The remaining table targets are `$E80D`, `$E833`, `$E84C`, `$E861`, `$E878`,
`$E88D` and the already adapted armor grant `$E8BE`. No new mapping is inferred
for those items. The three recovered grants are mutually exclusive source
weapon modes, rather than a generic incrementing power tier.

The consuming shot phase is already present in the installed actor. Original
`$B057` (current `$A5A2`) checks the held B bit and original even-clock gate,
then chooses free source slot2 or slot3. Original `$B0B7` (current `$A609`)
creates the source projectile with its original aim and world position,
gravity handling, velocity and flags. At `$B224`, negative `$0718` changes the
new shot's animation `$04E0,X` from 0 to `$80`, increments its type
`$0528,X` from `$80` to `$81`, and changes shot sound `$07E3` from 3 to 4.
Vertical upgraded shots also retain the original `$B156/$B1C0` muzzle-offset
branches. Both occupied slots suppress another birth; `$B057` still makes its
original unconditional `$0499=$80` write.

The zero-output checker `tools/audit/check_metal_weapon_items_1112.py` passed
the final bounded invocation, exit0. Its checksum is
`df16b4c48f633f4947905f411bfaaf9f11573aa7f4baf42579d3827718a337dc`.
It proves:

- Exact 90-byte donor reproduction, plus 12 executions of the actual reached
  dispatcher using original object slots4/5/12/23 and item selectors0/1/2.
- 12,000 donor/relocated grant pairs across player states0..7, old mode flags
  and incoming status flags. Complete source state, AXYP and cycles agree.
- Another 4,000 pairs for the 41-byte item0-only form. Minimum standalone SP
  is238; this is not a live Main/ISR stack qualification.
- 1,920 original/current-frozen shot-phase pairs using that new item0 source,
  both source slots, four aim directions, both gravity directions, world/page
  edges and both donor world-Y modes. This includes640 upgraded births and640
  both-slots-busy controls; original/current source state and AXYP agree.
  Relocated absolute reads can cost more cycles than original zero-page reads.
- Six actual current preflight cases: item0 and type81 remain admitted, while
  GravityFire is rejected. The preflight alone does not qualify item2's object
  effect, even though its flag currently passes that predicate.

Only the artificial return-stack cells `$01EF/$01F0` are excluded from source
state comparison. The shot phase additionally excludes its actual `$B0E1`
PHA temporary at `$01EE`; the relocated source image does not own the host CPU
stack. Initial harness failures exposed label-file CRLF parsing and these
explicit stack/slot1-marker expectations, without requiring any game change.

The concrete owning integration is to retain `Ms25Pickup`'s real mature-item,
owner and source-ready gates, route native flower type1 to `MsWeaponItem0`,
then use the existing native item erasure, score/SFX and inventory cleanup.
Keep armor/source `$05D0` independent of weapon `$0718`. Native progression
bookkeeping may advance the flower tier, but must not replace the source grant
or invent a GravityFire/third-effect cycle. A repeated flower should execute
the same original item0 grant, including its mutual-exclusion and pose writes.

Current packet use is actor8128/8160 bytes, renderer2991/3072, extra257/352.
The existing extra allocation has95 bytes remaining; the41-byte item0 form
leaves54 before the native flower branch/caller and any necessary relocation.
The full90-byte family would leave only5, so it is unsuitable for blindly
including the new pickup bridge. This capacity observation is not a new lease
or a qualified linker layout. Update the existing extra image and complete
authentication inputs together, preserving all current extra helpers.

Before delivery, qualify the genuine `HandlePowerUpCollision`/`HuPickup` chain
and immature rejection, real authored mushroom-to-flower collection, both
source slots and aim directions, source/native projectile rendering and native
enemy/terrain effects. Check current cold/readback/fault/retirement and actual
Main IRQ/FF-NMI boundaries after linkage, plus death/area persistence and the
existing full1-1 route. Original sound requests are source writes here, not
audible donor sound. No Mesen, controller-earned pickup, live interrupt,
installation or release result is claimed by this source component.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/metal-weapon-items-1112 --max-files 1 --timeout 600 -- python -B tools/audit/check_metal_weapon_items_1112.py
```

The shared storage checks passed and the output directory was never created.
No captures, ROMs, expanded dependency trees or test-case files were written.
Only this note, the new reference include and its new checker were edited.
