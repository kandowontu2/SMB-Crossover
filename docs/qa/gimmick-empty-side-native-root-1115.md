# Gimmick blank-block collision: root native checks

The private7a80f0f37e316436be0825bbd6fd9d372af6b0b7741f84ea87356282033d9b79
candidate changes191 owned Gimmick bytes,160 actually different, over16a.
All other bytes, including Prince's fixes, MiniLiftTick, shared collision
code and CHR remain exact. The source composition, caller/scratch closure,
Draw/Portrait equivalence and205 paired IRQ/busy-NMI cuts are separately
recorded in `gimmick-empty-bounce-side-1115.md`.

All checks here use the default Easy behavior, normal controller input,
real authored items and no game-state writes. Hard and audible audio
output are separate gates. No helper platforms are added or moved.

Root70234 passes the private collision diagnostic, receipt
fb8f94243b990fc2119e3a483298206a6e438ab963e7f606ff7783ab4a5996fa,
Lua53f0bb04. Among5510 actual side queries, four marker35 cells returnA0
at the publicB92C/SP221 wrapper while retaining rawR3=35. AtMain1562/1563,
playerX moves1229-to1228 rather than jumping16 pixels right. Real pipe
tiles18 and16 at725/128 and901/128 return unchanged and remain solid.
The old Flower policy still fails its later jump at1673Main/2215frames,
alive1243/176/HP2/lives2; that negative is retained, not called a pickup.

Root67035 independently passes both frozen stock regressions:

| Route | Main / video frames | Receipt SHA256 |
| --- | ---: | --- |
| Natural Mushroom and hidden1UP | 1357 / 1691 | 9df0b6f5db64ca07be8bbeb15454f35534cb2771630debabf3cbb2c7bfa7f0e8 |
| Natural Mushroom and Star | 1948 / 2639 | a3eab802cc111d599d63df0ae07397f71a385f20d78429ab920dec2866f86b55 |

The1UP route ends1069/176/HP2/capacity3/lives3/power1 after the actual
delayed life credit and25 later Gimmick movement calls. The Star route ends
1868/176/HP1/capacity3/lives2/power1/Star34 after the actual collector,
erase/popup6/timer35/music64/cue32/score+1000 and25 later movements. Earlier
ordinary injuries are retained; neither run is presented as injury-free.

Root79338 passes two real in-memory PNGs, receipt
5868476fae3883e9dfe36be0668662d7dcd94cb9f75683e5bb110c311e80117d,
Luaa3e6e77e,622Main/715frames. Root views coherent Gimmick/Goomba and
Gimmick/mature Mushroom images. All11 observed OAM-selected pattern pairs
independently match the private ROM. PNG hashes:
6999d64224a9e2fa2c863803092d60ae1f13bbceb9b94c9638d39b05c55cef60 and
712843418af7cafae96f9c91f5f964ac8f4feb4991dd4f0b6a2b1f5adcc18b75.

Root34274 passes the new reflected-star Flower route, receipt
c1e45e1b048d69a1b3f578a90a27f41743bd97e3621e9e56a26b6880f42afef0,
Lua15d21220. This changes only ordinary chase direction after actual
reflection to brake the remaining leftward velocity. It earns real star
support atMain1572/player1218/151 and a fresh original jump. Physical
Flower collection at1596/frame2118 pairs player1239/100 with1248/119.
The actual path gives inventory code2/next2/cue1C, erases the actor and
awards1505-to2505. Exactly25 later Gimmick movements finish1622Main/2152
frames at1266/112, HP2/lives2. No emulated terrain, actor or upgrade is seeded.

These private results close natural M/F/Star/hidden1UP collection and
resumed movement on this exact candidate. A full current1-1 run, all
weapons, Star expiry/protected contact, audible output and sustained
performance remain open. ScreenPoint costs20 more cycles; complete source
Draw/Portrait deltas are0/40/60. This fix is not a lag reduction.

The separate delivery recipe requires exact installed bytes, sidecar guards
and reproduction of34274's Flower receipt from the actual Downloads path.
Installation is pending until that recipe succeeds. No backup, capture
files, video, patch assets or releases are created by these private tests.

## Actual Downloads delivery

After source push889c2307, root29773 directly replaces16a with the exact
tested7a80 candidate. The same frozen15d21220 route is replayed from the
actual Downloads path. It reproduces the privatec1e45e1b receipt exactly,
including the real reflected support, physical Flower pickup, inventory
code2/next2/cue1C/score+1000 and25 resumed movements:1622Main/2152frames,
1266/112/HP2/lives2. Installed bytes equal the tested candidate. Pre/post
CLI sidecar guards are clear. No backup files, capture files, patch assets
or releases are created. The current official nightly is7a80f0f3.

The private scope and open limits above remain unchanged. The new ordinary
Flower control corrects its earlier leftward momentum; it is not another
game-byte change or a source of granted upgrades.
