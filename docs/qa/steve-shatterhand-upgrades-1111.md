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

The [live token candidate](steve-shatterhand-token-ingress-1111.md) now
reveals and awards Alpha and Beta through native pickups. The companion
and armor runtime still needs to be connected. The existing punch worker
already has original armored animation rows and a dedicated armor field.

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

## Transport on the current Prince nightly

The same token worker also loads on exact `2d7fb6e6`. Its transport image
is `cd2f40fe6c2520c147cd2c5e6ac3d7e5aa8b0e731c8cf9f3a53c768c3a0be354`.
The transport and Prince staircase/flagpole changes occupy disjoint ROM
bytes. The CPU run preserves Prince's 30-update flag approach, including
his real flagpole entry at X3167/Y176 and native castle handoff. Mike, Jay
and Steve repeat their 80-update opening comparison. Jay and Steve also
repeat their full CPU 1-1 routes, including Jay's five earned machine-gun
shots in 1-2. This transport image exists only in memory.

The extension uses the same page and staging buffer. It can copy and
verify 447 bytes at raw2 `$C200–$C3BE` for pickup code and another 128
bytes at `$C400–$C47F` for its caller. The 79-byte transfer without the
optional drawing scan keeps the
original raw3 `$B3BF–$B3FF` staging suffix zero. That matters when the
existing mapper loader rejects a staging write before calling the new
transfer. All seven injected endpoint faults leave the two headers
unauthenticated and preserve the zero suffix. In a separate full-size
transport test, the three families repeat their 80-update openings
without application state, OAM, VRAM or mapper changes.

The token renderer adds a scan of all six native pickup slots. Its
additional 32-byte allocation at raw2 `$C480` uses the free end of the
transfer page. The scan has an empty-mask fast path. With that allocation
included, the transfer is 95 bytes. Nine injected readback faults leave
both headers unauthenticated. The 80-update opening comparisons still pass.

## Original armor expiry

The ordinary donor clock at bank 12 `$9191` runs once per 16 committed
frames. Timer value 2 starts the exit state `$0F`, queues sound `$24`,
resets the punch animation and steps the timer to 1. Timer value 1 keeps
the armor active and publishes warning `$57`. The separate exit state
clears the timer and its effect actor, starts a 16-update exit counter,
and advances the state. The ordinary clock also leaves timers above 2
alone during states `$11` and higher.

The 73-byte reference worker passes 1,064 clock cases and 12 exit cases
against the original cartridge, including 24 warnings, 24 exit starts
and 84 decrements. Its linked SHA-256 is
`b900d4d982973e612a992c3043c35f368562987c5e5b89d4ead133b037a2d40b`.
These checks cover the clock and exit writes. The live overlay and
companion behavior still need their own callers and visual checks.

## Token graphics and physical pickup

The original Shatterhand HUD draws the two 16×16 glyphs using tile pairs
`$23/$25` and `$27/$29` on the original mapper. The donor proof checks
the actual OAM and reads the matching CHR data through that mapper.
The same 128 bytes are in CHR710 at offset `$300` in the crossover
candidate, using previously blank sprite cells. The world, moving token
and committed HUD share those glyphs and the native OAM rotation and
clipping path. The HUD columns keep the source X positions at 96, 120
and 144. Their Y position moves from 16 to 34 to clear the SMB status
line. Other Mike-family variants keep their ordinary item sprites and HUD.

In the candidate `f61501cc1c173f5437ef3ae5c7b179116deb1c6bbebe118f41e68fced9497cea`,
the Mesen Alpha and Beta replays each publish 64 world pairs, six flight
pairs and one committed HUD pair checked against physical OAM DMA. The
Beta replay punches the exposed Alpha exactly once. Both earn the
selected symbol through native contact and finish with both lives.
The full CPU route collects the three authored 1-1 blocks at X336, X1248
and X1744, reaches pattern `$15`, and shows all three glyphs with six
health and both lives. A directed simultaneous-token case also verifies
that a slot-4 Beta and slot-5 Alpha publish all four cells in one frame.
Mike and Jay render byte-identical OAM for all six directed item draws
at payloads `$81`, `$8C` and `$8D`. The candidate displays one flight at
a time. If two tokens are collected before the first lands, it commits
the older preview before starting the second flight.

| Physical proof | SHA-256 |
| --- | --- |
| Alpha pickup and HUD | `6a9387382c2688f27ac5e4d436f4337b4f1accef9e4d98e9805a80432d986086` |
| Beta switch, pickup and HUD | `b3b3cf98792f2b4fc7da03a405c41711a93f55b728444547f0e92ced15673f4f` |
| Assembled controller | `3f8d4c12877be73ecd76ee4d1cc9151dfce19dd3340409b9c89065ef3399e0f8` |

This is an integration candidate. The playable nightly still uses the
previous pickup behavior while the earned companion is under development.

On the original donor's stationary first-companion fixture, the Alpha
companion sits roughly 17 pixels ahead of Steve and 30–34 pixels above
him. A fresh B sets the companion's `$064C` state from 0 to 4. Down+A
changes the player's state from 3 to 4 and moves the companion inward by
three pixels on that update. The first companion's terrain, enemy contact
and projectile paths need separate source traces before integration.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/steve-shatterhand-upgrades-1111 --max-files 1 --timeout 240 -- python -B tools/audit/trace_steve_shatterhand_upgrades_1111.py
python -B tools/audit/run_bounded_build_v1.py --output build/steve-shatterhand-pickups-1111 --max-files 1 --timeout 240 -- python -B tools/audit/trace_steve_shatterhand_upgrades_1111.py --host
python -B tools/audit/run_bounded_build_v1.py --output build/steve-upgrade-transport-1111 --max-files 1 --timeout 240 -- python -B tools/audit/check_steve_shatterhand_upgrade_transport_1111.py --full-routes
python -B tools/audit/run_bounded_build_v1.py --output build/steve-extension-parity-1111 --max-files 1 --timeout 340 -- python -B tools/audit/check_steve_shatterhand_upgrade_transport_1111.py --extension
python -B tools/audit/run_bounded_build_v1.py --output build/steve-armor-clock-proof-1111 --max-files 1 --timeout 65 -- python -B tools/audit/check_steve_shatterhand_armor_clock_1111.py
python -B tools/audit/run_bounded_build_v1.py --output build/steve-token-art-1111 --max-files 1 --timeout 145 -- python -B tools/audit/check_steve_shatterhand_token_art_1111.py
python -B tools/audit/run_bounded_build_v1.py --output build/steve-token-all-draw-1111 --max-files 1 --timeout 320 -- python -B tools/audit/check_steve_shatterhand_token_draw_1111.py --all-blocks
```
