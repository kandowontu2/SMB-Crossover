# Steve Hermann’s live movement bridge

Steve’s authenticated movement path now calls the original Shatterhand
walking, reversal, crouch, and variable-height jump worker. The bridge uses
native camera, terrain, actor collisions, damage, and scene scripts. It
retains the Mike-family setup and controller-edge publication used by the
existing punch. The stock body renderer still supplies the movement art.

The bridge claims caller `$E0` at the existing raw A3 `$BF22` fallback and
keeps the preparation caller `$D6` on its existing path. Both previous
resident segments were relinked together to retain the punch renderer’s
cross-segment pointer. Physical CHR167 loads the 658-byte bridge at C2
`$DC00` and the 286-byte motion worker at `$DEC0` through the already
authenticated cold loader. The private state uses `$5C8D..$5C9E` in the
Mike-family area-reset overlay. The [donor qualification](steve-shatterhand-motion-1111.md)
records the original controller and source traces.

Native Main supplies real controller edges. The bridge retains separate
Q4 X/Y fractions and publishes signed integer movement to the camera and
terrain. The launch update publishes negative velocity before the first
upward displacement. The next movement update imports resolved wall,
ceiling, floor, or ledge changes from native state. Swimming, climbing,
scripted entry, death, and springs use the stock movement handler.

| Actual CPU Main check | Result |
| --- | --- |
| Eleven flat opening controller sequences | 467 updates matched donor endpoint X and maximum jump height in Q4. The native crouch flag followed the private crouch state on every update. |
| First naturally spawned Goomba | Steve punched from (220, 176). The hit appeared on the third update, native defeat scored on the seventh, and both lives remained. |
| First pipe side contact | Native wall correction stopped Steve at (433, 176) and cleared native horizontal speed and scroll. The next Right update published zero displacement and restarted donor acceleration at +2 Q4. |
| First pipe crossing | Right+A followed by Right landed at (499, 176) after 60 updates. The minimum screen Y was 107. Steve retained 6 HP and both lives, and the camera crossed a world page. |
| Punch regression | A held B produced one edge and one hit birth. Both facings each produced six matching modeled OAM DMA draws. |
| Mike and Jay | Each matched 80 controller updates against the parent, including gameplay, OAM, VRAM and CHR registers. Mike issued zero cold PPU reads. Jay and Steve each issued 16,400. |
| Header and script controls | All 32 single-byte header faults returned to native movement. Five directed stock-path comparisons matched. |
| Interrupt and cost sampling | Eight IRQ and eight lag-NMI cuts preserved the mapped RAM, current maps, active stack, OAM, Steve state and far-call operands. The movement entry through claim used 1,095–1,159 CPU cycles across 225 first-pipe approach and crossing updates. |

| In-memory image binding | SHA-256 |
| --- | --- |
| Original live-punch parent | `409d5a2e3b8ca1fdf6fa4512cac399310c44c1837b88b9f7d2a1e5bde858d280` |
| Movement candidate | `082304d4e680d450e991699d833b33e019fbff8e20f44e0ed798d3c358411bc4` |
| Current Prince brick parent | `ac2624467d4c3abc8988088ab22a4d2a0f52059e2e2d23373940fc9d17006066` |
| Combined candidate | `e6b152e26b43449115a7ff21903ae756346052e55dbdd94d8751e8c3a0951f23` |

The Prince change and Steve change affect disjoint sets of 11,697 and 1,223
ROM bytes. The movement cookie is `a710200ac5ae56e39c60ac56c337a8c7`.
The CPU movement replay uses `082304d4`. The
[physical delivery report](steve-move-delivery-1111.md) covers the combined
image. The full 1-1 route, original attack movement interactions, armor and
companions remain open. This CPU qualification writes zero files.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/steve-shatterhand-motion-1111 --max-files 1 --timeout 240 -- python -B tools/audit/check_steve_shatterhand_move_live_1111.py
```
