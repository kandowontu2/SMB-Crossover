# Steve Hermann’s Shatterhand punch

The reference is `C:/NES/Shatterhand (USA).nes`, SHA-256
`fbdfaab40aedda270d7473be37566b59e68811d932740c105d84fa6b1a7f19e1`.
It is MMC3 with 128 KiB PRG and 128 KiB CHR. The crossover parent is
Downloads SHA-256 `4df817587ea5b0aff3f278a4201976745bad4d9dd1b2a99d6cb5fd3b9c74dadc`
at checkout `7945ccef`. Its native roster route still brings Steve to the
Mike weapons worker in physical PRG98 at CPU `$A000`.

`tools/reference/steve_shatterhand_punch_1111.s` implements the source input
and attack animation leaf. In the donor, physical PRG12 `$94AB` ages the
combo counter before control, `$9F74` chooses the standing punch,
`$A0A0` chooses the airborne punch, and `$9D37` chooses the crouched punch.
Physical PRG13 `$B79A` advances the selected animation and `$B86E` constructs
the punch object. The combo uses the original low two count bits, four-unit
age increment, `$50` threshold, and `$FC` saturation. The source publishes
the original `$0C` sound request on a new punch.

| Input and posture | Donor animation ID | First hit update | Object countdown on birth | Signed forward offset | Vertical offset |
| --- | ---: | ---: | ---: | ---: | ---: |
| Standing B | `$01` | 3 | 10 | 15 px | −4 px |
| Airborne B | `$08` | 3 | 10 | 15 px | −4 px |
| Crouched B | `$09` | 3 | 10 | 15 px | +0.5 px |
| Standing third hit | `$0F` | 8 | 20 | 18 px | −3.5 px |
| Crouched third hit | `$16` | 8 | 20 | 18 px | +0.5 px |

Offsets are the nominal Q4 data before the donor’s 6502 carry propagation.
The ordinary object can outlive its body pose. Armor selects the original
alternate animation table. Its moving hit object is a separate donor path at
PRG13 `$A86E` and still needs porting.

The checker cold boots the donor and replays the original Start and A input.
Idle, walk, and jump OAM body cells match the prior hardware capture at
frames 2400, 2436, and 2450, receipt SHA-256
`17c0545be1644ca5020754caa0b59bc325bb6e61fc445d4841c37aba51d79c6a`.
The compiled worker matches 604 calls to the unmodified original animation
routine and 16 exact hit births, including both facings and the armor table.
Each birth compares the shape, nominal lifetime and actual Q4 object point.
The five live donor controller sequences compare another 222 updates, with
pose, combo, hit birth and sound-request agreement. Tapping and holding B
each produce a single hit on update 3. Repeated new edges reach the standing
and crouched strong punch on updates 38 and 42 of their respective sequences,
both with the original countdown of 20. Airborne B produces the air punch
on update 9 after the sequence starts with six A-only updates.

The exact parent CPU test selects Mike, Jay, and Steve through the real menu.
Each opening calls PRG98 `$A000` for 22 consecutive controller updates. On
Steve’s true B edge at `$5C02`, a detached instance of the new worker emits a
punch on the third update. The exact predicate is raw character 16 and
`$730B & $60 == $40`. Mike and Jay produce zero Steve worker births.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/steve-shatterhand-punch-1111 --max-files 1 --timeout 240 -- python -B tools/audit/trace_steve_shatterhand_donor_1111.py
```

The replay writes no files. The compiled 337-byte worker SHA-256 is
`0791b3f46a65e6f984c52d9a8733f764f86c2039773f95e468420c2afac15343`.
The assembly uses symbolic state and remains detached from the installed
ROM. The live hook still needs cartridge space,
private state initialization, hit collision and rendering, with separate
ownership for power-ups, companions, and the original movement. No Steve
candidate was delivered, and Steve’s 1-1 clear remains open.
