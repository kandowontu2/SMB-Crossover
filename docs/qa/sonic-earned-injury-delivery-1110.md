# Sonic earned mushroom and injury verification

The MMC5 nightly at
`C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes`
is `49295acff1d70349119b599882a2ec0b4e2f58d21f153c90b2228dc9aceee2a7`.
The previous nightly was
`47a7a6aeabe2cc7db593f431591e52331b834485b3d7638e3f10f95cbf43db4b`.
The IPS is 2,099,510 bytes, SHA-256
`3981798af56cbd37efcd3283bfdd9e2bf339340476de553e7e99df86eabdb2af`.

Both Sonic runs start from the title. On the character grid, Right then
Down three times reaches Mr. Gimmick without passing through SMB2 Mario.
Select three times chooses Sonic. The replay starts with tier 0 and earns
the first mushroom through native block contact and collection. Its
inputs, block, item birth, maturity, pickup, transformation and injury
witnesses agree through Goomba contact after accounting for the ROM cookie.

| Event | Mesen observation |
| --- | --- |
| Authored block | The native head handler sees tile `$C1` at player X336/Y160 with block pointer bytes `70 D5 03`. |
| Mushroom | Slot 5 spawns at X336/Y136. The mature item is collected at X398/Y124 by Sonic at X408/Y134. The native actor is erased and the pickup sound writes `$20`. |
| Growth | All 60 transformation updates run and Sonic reaches tier 1. |
| Enemy contact | Grounded Sonic at X678/Y176 touches a live Goomba at X688/Y184. The previous ROM stores tier 43. The corrected ROM stores tier 0, with carry clear in both. |
| Recovery | The corrected ROM resumes active play after 55 recovery updates. Sonic jumps from recovered X722/Y176 to X738/Y104 with both lives. |
| Prince regression | Original jump and climb cross four pipes and two gaps. Prince reaches X1461/Y176 with four health and two lives. The route uses zero helpers. |

| Evidence | SHA-256 |
| --- | --- |
| Sonic Mesen controller | `a6e1dc5caf708a6d7fbe21bc7d7d18207061befc5e9bb1972bedb2e7125b182c` |
| Old Downloads Sonic replay, reproduced defect | `00ac3ee5ae97f7eeed76aa2add63cdacfeda217d8f53fe5dd4b8873b39188f50` |
| Fixed candidate and Downloads Sonic replay | `b27c49992aa49955eec69819c3b6d1fc2f53cad6754b7ff6ba24fa1e28c7798d` |
| Candidate and Downloads Prince regression | `800fd9ee54cb740e1d065ecf777dd4ca6cf5cb7497f6a5261e55d268977c9572` |
| Mesen executable | `8b92daa209ee5052845e02a663aeb1afd6194eca55d86e6628c51114c61da0a9` |

The ROM changes 19 exact bytes including the authenticated cookie. All
14,244 previously changed Prince bytes stay intact. The installer
reconstructs the image from source, verifies the IPS round trip and
replays both controllers after installing directly to Downloads. The
automatic patch guard is clean before and after installation. The tests
emit stdout receipts and create zero capture files or backups.

The first physical route went Down three times and then Right. Highlighting
SMB2 Mario along that path changed the native power tier from 0 to 1,
which carried into Sonic and caused the authored block to dispense the
next upgrade. The real compiled menu reproduces this write at physical
PRG 118, CPU `$AF8A`, while switching among SMB2 and Doki Doki alternates.
That separate selection-state bug remains open. The confirmed Sonic
route starts at tier 0 using ordinary D-pad navigation.

The corrected Sonic route recorded 520 of 1,123 gameplay frames without
a logical gameplay update. Original ring progression, additional earned
upgrades, and the broader lag pass remain open. The previous
[full-stage Sonic replay](sonic-original-delivery-1110.md) and
[Prince delivery](prince-native-pipe-gap-delivery-1110.md) document their
separate verification scopes.
