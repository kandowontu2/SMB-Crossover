# Steve Hermann’s Alpha/Beta token ingress

The CPU candidate starts from exact installed Prince successor
`2d7fb6e63ea55f2d0eb9ef3af4efc467233da013dc70e295952a4adcdd14ecdb`.
Steve’s 1-1 item at X336 now emerges as Alpha. Press B to hit the exposed
item with Steve’s fist and change the letter to Beta, then touch the item
to take it. The stock SMB head bump opens the block and the stock item
actor handles emergence and physical collection. The letter-change
control comes from the original Shatterhand manual.
[Jaleco Shatterhand instruction manual](https://www.thegameisafootarcade.com/wp-content/uploads/2017/03/Shatterhand-Game-Manual.pdf)

Actual menu and Main replays punch the first Goomba, reveal the item from
Steve X333/Y156 at update 100, then jump Right+A from X298/Y176. A fresh
B edge at jump age 17 changes the mature item from `$8C` to `$8D` with
the original fist at age 19, Steve X308/Y110. Holding that B press produces
one change. Both controllers collect at X324/Y112 on update 225, while
the item is X336/Y120. The native object is erased, the Mike-family health,
heart capacity and tier stay 6/3/1, and the letter commits to the token
pattern after 12 active updates. Alpha commits `$01` and Beta commits
`$02`. With a fixed camera, the screen-space flight matches 1,552 successive
steps of original bank 3 `$AA15` across 144 starts.

The two PRG98 call sites at `$A681` and `$A745` share an 18-byte gate at
`$BFED`. The Steve path goes through the existing dual-header check, then
accepts only the two exact native return sites. The 391-byte ingress code
starts at raw2 `$C200`. Raw3’s Steve combat entry at `$BED4` routes the new
typed calls, and the existing fist hit path checks the token before native
enemies. The six-bit mask at `$C3FC` binds each stamped native object slot.
In a directed two-actor test, slots 4 and 5 both retain their stamps, the
fist flips only slot 4, and both collections preserve the packed Beta–Alpha
order even while the first letter is still in flight.
`$C3FD–$C3FF` hold the in-flight pattern and coordinates, and `$C1F1` holds
the committed pattern for the companion worker. Mike and Jay each match
24 original prepare and collection calls across native item kinds and
starting tiers. Corrupting the first or last byte of either authentication
header keeps Steve’s new reveal out of the stock pickup path.
The ingress-only candidate SHA-256 is
`cc6981309bde3200b1e218315ceebaad11b5147514da677c7664522cb0f71f56`.

A continuous controller run collects three Alphas from the authored 1-1
blocks. It opens the second block from X1242/Y176, launches Right+A from
X1210/Y176, and collects the X1248/Y120 item from X1236/Y112. Its flight
commits the combined pattern `$05`.

For the third letter, Steve jumps from X1722/Y176 onto the native lower
block at X1744/Y144. After 15 idle updates he is settled at X1747/Y112.
A fresh stationary jump reveals the X1744/Y80 item block, and the actor
matures at X1744/Y56. Steve backs to X1666/Y176, jumps onto the neighboring
native lower block at X1696/Y144, and settles at X1702/Y112. A Right+A
jump collects the third letter from X1732/Y44 at age 27. The sequence
ends at X1740/Y48 with six health, two lives, and the complete `$15`
pattern. It uses the existing blocks and no helper platforms.

This candidate still draws the stock Mike item icons. The authentic world
glyphs, visible flight, HUD, companion and armor are separate integration
work.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/steve-token-ingress-1111 --max-files 1 --timeout 240 -- python -B tools/audit/check_steve_shatterhand_token_ingress_1111.py --all-blocks
```
