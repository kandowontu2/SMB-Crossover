# Prince of Persia opening cadence

The installed `5c89b9b7` MMC5 build completed 96 Prince updates in
168 video frames in the empty Easy 1-1 opening. The linked CPU trace
attributed 6,876 cycles per update to 12 complete cookie checks. The
checks compare two 16-byte headers before dispatching to the Prince.

The proposed dispatcher keeps the first call on the complete checker.
Later calls may use the Prince's existing stamp for that same ordinary
game update. The quick path still checks both owner headers and rejects
paused, expired and invalid requests. The Prince's compressed data and
movement code match the installed bytes.

The dispatch change sends variable fast calls to the same bank 85
mirror. The original row remains on the caller's stack for either
dispatch outcome. The fixed Mini Mario entry and the direct bank 85
entry retain their old addresses. The caller audit identified the
unused space for the two new routines. Receipt
`7f1c07af9d7d1159050fc37ffffd8782a86369028381d909a61d4513d3c7c34a`.

The linked test compared 262,144 combinations of owner and target.
Actual gameplay used one complete check and 11 quick checks per
ordinary Prince update, saving 3,975 cycles. Donkey Kong Jr., Mini
Mario, Sonic and Super Sonic matched their earlier gameplay state in
the linked tests. Their common dispatch costs increased by 10–128
cycles per update. Separate tests covered 570 interrupts and 570 busy
NMIs through the Prince's changed path.

The epoch change alone, `c1d57f50`, still took 168 video frames for
96 updates in Mesen. Receipt
`9f170c4a34c83caa63ac427e7000852484266b6e06b3d4b9b2cda00967c9fcb4`.
It was retained as a source trial.

The standing trace led to a second change. Four side queries per update
traversed the expanded guest dispatcher and ended at the native
side collision routine. A route for the Prince in ordinary gameplay
calls the native query directly from the existing bank 33 dispatch.
The combined candidate `c08af795` saved 9,663 cycles per update in
the linked opening. The compared standing, walking, jumping, airborne
and release states matched.

The exact combined test ROM took 144 video frames for 96 game updates
in Mesen. Frames with no update fell from 72 to 48. The player covered
the same distance, from world X40 to X92. The empty opening still
misses updates.

Mesen receipt `519a555e8c0592549ea6dc46b69b2721bdf3b9b5fe68ece48d88a0f853fe6ace`.

## Guarded side queries

The first direct query could run when the old owner header check would
have rejected the call. It also failed to reveal the Fire Flower in the
full-stage replay. The earlier candidate stayed private.

The guarded ROM `c85cde8f` uses the existing owner and update check. A
rejection follows the original dispatcher and returns the original
fallback. Eighty-eight paired source checks covered a cold start, invalid
headers, a stale stamp, pause and water. Receipt
`6511d2282752f0639b633968eeb53e248e8411996e37f0953fe111b406376bd2`.
The selector matched 262,144
owner/target combinations. Another 559 IRQ entries and 559 busy NMI
entries matched their uninterrupted foreground endpoints. The guarded
Prince path saved 8,439 cycles per update in the opening. Paired checks
for Mini Mario, Donkey Kong Jr., Sonic and Super Sonic matched gameplay
state and added 10–166 cycles per update.

The guarded ROM took 145 video frames for 96 updates. Forty-nine frames
had no completed update, down from 72 on the Downloads nightly. Both
runs advanced from X40 to X92. Mesen receipt
`fa61ad0e664f27fd1334298601d7bfffcc4c7b1660501c422acb8a67dda93f49`.

In the first guarded full-stage replay, the upward strike contacted the
adjacent brick while rising. The probe reached the real Flower block at
world X1248 only after the rising speed had reached zero. No Flower
appeared in any object slot. Mesen receipt
`e88f7fc85995dcd29180812bd1f4a6d4a62b5975499ce94d061b7b59ac80dd8b`.
The baseline `5c89b9b7` passed the full replay, earned the sword and
completed 25 grounded updates in 1-2 with both lives. Mesen receipt
`dedee1bbc365e91de5fbacf586a6f37dc05b156c303db59ca57ebf1b68c7e7dc`.

The guarded ROM passed the separate natural hidden 1-UP replay. The
ordinary block hit revealed the item, the native collector awarded a
third life and the Prince retained it over 25 more game updates. Mesen
receipt `688b96d921aaa14bfcfa00dbcbd5988b7f823b78b6627205f0f76b0932fd9f15`.

The stage replay's second Up attempt hit the authored Flower block
while rising and brought the item to full height at X1248/Y119. The
Prince also climbed to X1291/Y113 during the retry. The first version
of the replay waited for a grounded position in that situation and
timed out beside the mature Flower. Receipt
`1ee2e64fa376bc74063e869d2b3ef215f9d2613960be49013a7704a187698266`.
Walking back from the ledge collected the native Flower and earned the
sword. That run reached X3084/Y177 after the final staircase. The replay
timed out waiting for the source ground flag while the Prince was over
the authored ground. Receipt
`9247ad01e23ea4d9f7d73fe76837c86ee5cd6a4202ec6703af65686a58d712c7`.

With the replay checking the actual terrain after the final staircase,
the same guarded ROM completed 1-1. The Prince kept the sword and two
lives through 25 grounded game updates in 1-2. The replay used controller
inputs and read-only observations. The ROM bytes were identical to the
earlier guarded trials. Mesen receipt
`4dbd014b139fae217e529b806aeefb080df8b472d3a09230cc80845f811c89ef`.

The Downloads nightly now uses `c85cde8f6944b803b57897835ec800667a3d1e08e8a6cdea8aa43e9510ca3171`.
Mesen reproduced the exact 145-frame timing receipt from Downloads.
The installed file matches the tested candidate byte for byte. The
before and after patch checks found no matching sidecar patch.

The guarded foreground still averages 37,688 CPU cycles during grounded
idle. Far-call handling in the internal RAM trampoline consumes 5,873
cycles per update. The remaining calls also spend 3,008 cycles across the
two hot bank 65 transport regions. These costs leave work for another
performance pass after the pickup and stage replay checks.
