# Steve Hermann’s earned upgrades

On exact Downloads ROM
`677aad54c55f829d9e7b2aab9e2b1f4eddebcd3c6e6532eeddd9f2ce4e1a26ab`,
Steve’s authored 1-1 mushroom still feeds the Mike-family pickup handler.
After the real first Goomba punch, the controller walks to X333 and jumps
into the block. `JnPreparePickup` reveals the actor at X336/Y136. The
controller backs to X298/Y176, holds Right+A for nine updates, and collects
the mature actor at X336/Y120 from player X324/Y112. Its native payload
is `$81`, owner 16. Health rises 6→8 and the maximum rises from three to
four hearts. The weapon tier stays 1 and Steve’s armor byte stays zero.

The Shatterhand cartridge is the US release, SHA-256
`fbdfaab40aedda270d7473be37566b59e68811d932740c105d84fa6b1a7f19e1`.
Bank 8 `$82B5/$82F3` accepts contact with an Alpha/Beta token. The actor
stores the candidate in its own `$0620` field and commits the first empty
two-bit HUD slot only after flight ends. Bank 3 `$AA40` writes the committed
pattern to `$05C4`. The controller-only donor opening observes authored
actors `$04` at X848/Y368, `$05` at X912/Y368, and `$08` at X1072/Y368 in
donor world coordinates. Actor `$08` dispatches through the original token
flight handler `$AA04`. The full pickup and armor proof uses directed actor
contacts and original cartridge execution for both grant paths.

| Alpha/Beta order | Packed pattern | Native companion ID |
| --- | --- | --- |
| Alpha, Alpha, Alpha | `$15` | 1 |
| Beta, Beta, Beta | `$2A` | 2 |
| Alpha, Alpha, Beta | `$25` | 3 |
| Alpha, Beta, Beta | `$29` | 4 |
| Beta, Beta, Alpha | `$1A` | 5 |
| Beta, Alpha, Alpha | `$16` | 6 |
| Alpha, Beta, Alpha | `$19` | 7 |
| Beta, Alpha, Beta | `$26` | 8 |

Three collected tokens trigger the original display countdown. At update
80, a different or absent companion produces the table’s new actor. An
active matching companion instead starts the armor transform in state
`$0D`. The transform leaf counts down by four and installs `$7F` in the
armor timer on its 32nd decision. These grants occur automatically when
the token pattern is earned. Native coin credits and Down-operated
purchase pads use a separate path. The original coin leaf credits 5 or 20
and the affordability leaf tests prices 10, 30 and 200. The directed
same-companion case begins its transform at frame 80 and activates armor
at frame 159. In the ordinary cartridge frame loop with no damage, the
timer begins at `$7F`, steps about every 16 frames and expires at frame
2169, giving 2,010 active frames. Down alone leaves Steve crouching in
state 3. Pressing A while Down is held changes him to the companion
assist state 4 in the original player controller.

The 231-byte source worker matches 38 token previews and terminal flight
commits, 16 full-slot rejections, 8,256 token update pairs, 48 companion
grants, 16 armor grants, and 512 transform decisions. It executes with the
original 6502 leaves in the comparison and uses the existing donor boot
whose OAM matches three physical opening anchors. The paired timer and
actor tests begin from explicitly directed state.

The host still needs a physical Alpha/Beta producer, separate pickup
ownership for Steve, and a loaded companion or armor runtime. The current
authenticated movement page has 48 spare bytes across its two segments,
which cannot hold this 231-byte worker and its host bridge. The current
punch worker already has original armored animation rows and a dedicated
armor field. Its use still depends on an actual earned grant and on the
remaining original armor combat and rendering paths. The installed
movement, punch, and stage route are the baseline for those tests.

| Source result | SHA-256 |
| --- | --- |
| Linked upgrade worker | `65fe9380ba6b8fd8c6adc1c0e1db0986b07f8e1a011b7485263690c3d046f975` |

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/steve-shatterhand-upgrades-1111 --max-files 1 --timeout 240 -- python -B tools/audit/trace_steve_shatterhand_upgrades_1111.py
python -B tools/audit/run_bounded_build_v1.py --output build/steve-shatterhand-pickups-1111 --max-files 1 --timeout 240 -- python -B tools/audit/trace_steve_shatterhand_upgrades_1111.py --host
```
