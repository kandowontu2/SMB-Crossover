# Jay McCray donor motion and terrain

The original control trace now extends through Jay’s position setup, camera
requests, gravity, and contact resolution. The source reassembles 1,045 bytes
exactly from the same Journey to Silius (USA) mapper 1 cartridge used for the
first control slice. The donor SHA-256 is
`12f5c5e413a2aa5bff75b5077e4477497d7e49aa432560c2e8c3fd3cc71910cc`.
The in-memory run starts at reset, repeats the earlier controller sequence,
and matches all three retained hardware OAM anchors before forking the
actual stage at frame 1500.

| Physical PRG bank | CPU interval, end excluded | Bytes | Original role |
| --- | --- | ---: | --- |
| 6 | `$81EA..$8304` | 282 | Position setup, scroll requests, screen clamp and scripted fallback |
| 7 | `$CD88..$CE18` | 144 | World minus camera projection and visibility |
| 7 | `$E1A4..$E1AA` | 6 | Player integration entry |
| 7 | `$E20E..$E247` | 57 | Gravity and tentative 16-bit Y/X integration |
| 7 | `$CE4D..$CF07` | 186 | Bank selection and side/vertical contact resolution |
| 7 | `$CF07..$D002` | 251 | Sample ordering and original tile-class effects |
| 7 | `$D002..$D03E` | 60 | Packed donor tile lookup |
| 7 | `$D03E..$D042` | 4 | Nibble masks and player X=0 list pointer |
| 7 | `$D058..$D08F` | 55 | Five exact player geometry records and their pointers |

## Executed donor evidence

The eight controller sequences supply 249 actual donor updates. The
original `$804B` caller reaches `$81EA` and returns to `$804E`. The original
`$8055` caller enters `$E1A4` with X0 and returns to `$8058`. The checker
pairs all 249 calls at each site against the relocated instruction image
with the original donor geometry addresses. All 498 return pairs preserve
AXYP/SP, CPU cycles, live stack, modeled RAM/PPU and mapper state, and the
ordered non-RAM writes. The original mapper service, event routine and
sound request remain authentic external donor calls.

Moving the probe data with the code produces one address-specific residue
at the integration return. Zero-page `$01` holds the last probe record’s
high byte, `$D0` in the original and `$68` in the fixture. In all 249
additional pairs, the first subsequent access is the genuine pose reader’s
`PRG7:$E49D STA $01`. This overwrites the address before any read and
restores full exact state. The proof compares every other byte and the
ordered mapper writes at the original integration return.

| Witness | Result |
| --- | --- |
| Grounded walk | 40 Right updates keep Y176. Actor X moves from 96 to 152.25 px. Camera X advances 742/16 px using genuine 22/16 and 26/16 requests |
| Reversal and release | Native left, right, and neutral support probe lists all execute |
| Crouch | 12 genuine crouched updates followed by the standing state |
| Tap jump | Apex Y156.5, then native landing at frame 1525 and final Y176 |
| Held jump | Apex Y123.5, then native landing at frame 1545 and final Y176 |
| Landing tile | Both jumps read packed byte `$11` from mapped PRG3 `$80B9`, coarse column6/row12. The high nibble returns class1 and original `$CEF7` snaps Y |
| Original terrain | 249 bank3 resolutions, 495 directional probe calls, 839 actual packed map reads |

The opening exercises empty head and side probes and solid floor contact.
The original ceiling-block, side-block, special-tile, and scripted clauses
are byte-exact in the recovered ranges. Their effects require separate
gameplay fixtures beyond this opening.

## Host integration boundary

Keep `$81EA` and `$CD88` ahead of integration. They compute relative
coordinates and camera requests from the original actor and scroll fractions.
`$E20E` applies gravity before generating tentative coordinates.
`$CE63` checks horizontal contact and commits X before the vertical probe
and Y commit. Its actual floor branch
clears the airborne bit, queues landing sound, and masks the Y fraction.
Substituting an entire host movement or collision update at that boundary
would change the donor’s state transitions.

`$CF07` picks one of the original player lists using X0 and Y0/2/4/6/8.
Each list contains two signed Y/X offsets in sixteenths of a pixel. Preserve
that order and the original short circuit on a blocking result. The native
map seam is the actual `$D002` read. It receives coarse Y at `$02` and coarse
X at `$03`, computes a packed room offset through `$44`, preserves X, and
returns the masked nibble in A with its normal N/Z. Even columns return
the high nibble. Odd columns return the low nibble. `$CF76` then uses the
same column parity to decode the class and apply source behavior.

A future host terrain adapter should bind that low-level lookup to the
host’s actual tile information and explicitly qualify any class beyond
empty and solid before enabling its effects. The camera adapter must
separately honor the source’s previous-update scroll request handoff.
The existing Mike variant gate stays the intended entry for a Jay-only
implementation once root has granted the private code and state leases.

The source checker used the bounded stdout runner with `--max-files 1`.
The output roots stayed absent. Source SHA-256
`7dc9bb8d4bbda5dc8709e1c9ae69f7906dcbe8c59ecd4448625fa61bbc7049bc`.
Checker SHA-256
`0488710d949951319fe64fdbce12c4f79f189400705cce281314f200e8708dba`.
The earlier donor input source and original hardware receipt remain the
independent bindings for the opening.
