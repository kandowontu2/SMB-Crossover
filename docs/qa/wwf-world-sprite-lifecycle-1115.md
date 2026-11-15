# Current WWF native sprite lifecycle audit

This source-only audit executes exact delivered ae66
ae669c7ec7536f1c912b3000597be7b3416c20f312638b2589f52fab55f0bc01.
It tests real compiled Select/Start for Hulk Hogan role0 and Andre the Giant
role5. No character/actor/health/terrain grants, ROM changes or Mesen runs.
It does not certify rendered pixels or resolve the user's visual report.

Bounded run68593 is TERMINAL PASS for both identities, zero output files;
build/wwf-world-sprite-audit-1115 is absent. Full6 source-derived WWF cookies
match current WfCookieC byte-for-byte, aggregate SHA256
28d3347a5571d64d51f16027c2fa4c43def63b8b2c385b24c3856d0d1ba4bc7c.
This authenticates A1/C2/A3, selected metadata and all body pages together.
Selected full cookies are Hogan a71d00020aeb5db44a45967934005aca and
Andre a71d0502800cb7018937615fe408e7cd.

| Identity | Source audit receipt SHA256 | Ordinary two-spot controller SHA256 |
| --- | --- | --- |
| Hogan | 6a5644a544570018ed20abb098485dccbb757de29d5d11b36071b27e8ed5adfd | f7a3481ec32c0a8f74159ec1243664fb35c3a4ea04953b8605184766a29bdd5a |
| Andre | 7aef6d17ef356269414b0abcccb62847920a76b7ee86736c0700ba82985028a9 | 3bec48449168a32fbaa98caf1aa99b397b8eb471e0a3101c101b5b371f764db2 |

Both naturally reach the live Goomba and mature first mushroom; image-route
Main550 Hogan and542 Andre. They then normally walk to401, physically collect
the same mushroom, run60 real powerup-freeze ticks and25 actual WfMovement
entries after recovery. Final401/176/native0/engine8/power1/lives2. This
extends beyond the common startup reset into the actual private publisher
and powerup lifecycle, without inferring that the common29-byte fix covers it.

Actual X5SetPhysicalChr entry is PRG62:$A275, beginning
9947018a2903098099e073a9, with current A/X/Y and real call history retained
in the in-memory receipt. All selected gameplay/freeze/recovery publications
use Y0. Hogan body pages observed:445,446,447,570,629,634,636. Andre:
444,457,585,587,588,630,631,632,634. Menu traversal previously publishes
other characters' private windows1/2/3 and7; the real Start reset removes
those modes. Actual gameplay modes1..11 remain0, with window0 mode$81/$82.
Hardware windows1/2 stay native16/17 throughout the tested lifecycle.

Authenticated native page16 SHA256 is
fbdfcb689bab3c74a0f5ad235ab24dea6625378658f3e70fbbe0144200c6709d;
page17 is006c3d8e9cf3760a610ab3a8f89519d464e6d25fac12f26ab204eb538680269e.
The real source OAM has Goomba tiles162/164 at window2/page17/palette3,
and mushroom124/126 at window1/page16/palette2, for both roles. PPUCTRL $A8
selects16-pixel sprites. In these captured source OAM states, Goomba rows
have at most6 candidates Hogan/5 Andre; mushroom rows at most2. Neither
target is beyond the first8 eligible sprites on its rows. This is an OAM
candidate census, not console raster acceptance.

No source CHR-clobber cause is reproduced in these two ordinary routes.
The existing palette mux deliberately arbitrates source body/native groups;
these results do not certify its complete visual behavior. Native images
remain necessary before a graphics repair proposal. No code/art allocation,
ordinary ROM mount or change is proposed from these observations.

Minimal root-only image API:
replay_wwf_world_sprite_images_current_1115.controller(rawae66,'hogan'|'andre').
Factory SHA256
7eff456ff76edc9c94cb35a7382210418428a39269b44dd78f097e3c15b68089;
audit296b27909464c3ed124aed0306bb0d58a7ebfd6684a1a8a8922cc59510490f50.
It strictly inverts ae66→571→F11→cf7→1daca→82 and rebinds current config/
hook-bank hashes to the frozen82 image body. Old421/82 factories stay strict.
Two PNGs per identity, each at most64KB, RAM/stdout only: live Goomba and
naturally mature mushroom. Both identities total4 PNGs; root owns the sole
queue and actual Downloads launch. Source PNGs were labelled API fixtures
and never used as pixel evidence. Some inherited Prince-only state fields
in the generic image receipt are not interpreted as WWF physics/state.

Root71314 subsequently ran both exact current controllers against actual
Downloads ae66 and visually reviewed all4 in-memory PNGs: normal Goomba and
mushroom for Hogan and Andre; no corruption reproduced in those openings.
Hogan908 Main/1490 physical, receipt
d09e3f89ae5d01360d22c99e8fa8af830708e92239b22b81baecc8ad4d50b52d;
Andre963/1536, receipt
65297fc03f39237afc564dc96463f9b67717e1a13740de26721c3c325ecb7eb0.
Native latches were446/16/17 for Hogan and630/16/17 for Andre in windows0/1/2.
Independent current-ROM reads matched all8 target pattern pairs: page17
offsets544/576, page16 offsets960/992,16 bytes per half, across both roles.
The native controllers end at mature mushroom before collection. The60-tick
freeze/+25 recovery remains source-only. This is neither all6 wrestlers nor
all stages/poses. Root's native QA is `wwf-world-sprite-native-1115.md` and
runner `run_wwf_world_images_native_1115.py`; no ROM/image files changed.
