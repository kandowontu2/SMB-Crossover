# Steve Hermann’s earned upgrades

On exact Downloads ROM
`677aad54c55f829d9e7b2aab9e2b1f4eddebcd3c6e6532eeddd9f2ce4e1a26ab`,
Steve’s authored 1-1 mushroom still feeds the Mike-family pickup handler.
After the real first Goomba punch, the controller walks to X333 and jumps
into the block. `JnPreparePickup` at PRG98 `$A61E` reveals the actor at X336/Y136. The
controller backs to X298/Y176, holds Right+A for nine updates, and collects
the mature actor at X336/Y120 from player X324/Y112 through
`JnCollectPickup` at PRG98 `$A72A`. Its native payload is `$81`, owner 16.
Health rises 6→8 and the maximum rises from three to four hearts. The
weapon tier stays 1 and Steve’s armor byte at `$5C85` stays zero.

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

The host still needs a Steve-specific pickup actor that reveals and awards
Alpha and Beta tokens, plus the companion and armor runtime. The current
punch worker already has original armored animation rows and a dedicated
armor field. Its use depends on an earned grant and the remaining
original armor combat and rendering paths.

## Cold transport alongside Jay’s machine gun

The exact in-memory transport starts from Jay machine gun candidate
`c8d328a27efbc900216985aeb86600a1f626f8cc76e93a91bb30b2c1f8c2e727`.
The finite selector census checks 88 domains, 49 exact legacy tables, and
four copies of the native map. Physical CHR230 and CHR226 start with
identical bytes. Sonic’s mode `$85` NMI selector rebinds the two inputs
that select CHR230, `$13` and `$93`, to CHR226. The patch uses PRG62
`$A9B8–$A9FF` and rebinds the existing `$B690` graphics jump to its
relocated entry. The 2,809 selector comparisons preserve X, Y, processor
flags and the mapper’s upper-page selection. Both rebound inputs read
identical pixels from their replacement page.

The Mike-family cold wrapper grows from 159 to 161 of its 162 reserved
bytes. The loader adds CHR230 as its fifth code row and stages it at raw3
`$B000–$B3FF`. The `$A000` packet entry jumps to the 27-byte copy-and-readback
routine at `$B100`. The relocated 239-byte worker ends at raw2 `$C1EE`
and reserves `$C1F0–$C1FF` for its fields. The original bootstrap then
restores the staging window byte for byte. There is no mapper expansion.

Actual menu-to-1-1 entry and 80 native Main updates for each of Mike,
Jay and Steve preserve application RAM, OAM, VRAM and mapper latches
after excluding the new code and authentication headers. Jay’s
machine gun dispatcher runs on all 80 updates, and Steve’s movement
worker runs on its 160 existing calls. Jay and Steve cold reads grow from
16,400 to 18,450. Mike and authenticated warm calls make no cold reads.
Readback corruption in the CHR staging destination or at either end of
the raw2 resident worker prevents both headers from authenticating.
The same image also completes both existing CPU controller routes. Jay
reaches 1-2, equips his earned machine gun from Pause and produces five
matching DMA shots five updates apart, leaving 58 rounds. Steve punches
the first Goomba, crosses all nine existing route landmarks, and reaches
playable 1-2 at X40/Y48 with six health and two lives.
The transport has no live pickup or combat caller and exists only in
the in-memory source test.

| Source result | SHA-256 |
| --- | --- |
| Linked upgrade worker | `65fe9380ba6b8fd8c6adc1c0e1db0986b07f8e1a011b7485263690c3d046f975` |
| In-memory transport image | `116c48b7ca8c8ae6a31feb1b322b11c43b09c45bcc686fac98fc9c65accd04fd` |

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/steve-shatterhand-upgrades-1111 --max-files 1 --timeout 240 -- python -B tools/audit/trace_steve_shatterhand_upgrades_1111.py
python -B tools/audit/run_bounded_build_v1.py --output build/steve-shatterhand-pickups-1111 --max-files 1 --timeout 240 -- python -B tools/audit/trace_steve_shatterhand_upgrades_1111.py --host
python -B tools/audit/run_bounded_build_v1.py --output build/steve-upgrade-transport-1111 --max-files 1 --timeout 240 -- python -B tools/audit/check_steve_shatterhand_upgrade_transport_1111.py --full-routes
```
