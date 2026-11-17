# Rogue Dawn HUD disappears after the area transition

Actual Downloads86516 completes its passive diagnostic, exit0, on cb95.
Receipt `dd0dae085d90d268801c500b0a62553600b70861bd519777d42d55d5d512203b`
reduces to the entire exact native Bomb728a8c62 receipt after removing only
`hud_continuity`. The same real energy tank, missile tank,1-1 clear,1-2
Bomb acquisition and original Bomb lifecycle remain qualified. Factory
c2295634 / native Lua64cbc38b changes no game input or memory.

At Main1917 in1-1, actual nametable2023..202D contains **E191 M005**.
Its cache holds ammo5, health high19hex/low10hex and dirty0. At the next
native status redraw (area41, Main4237), both2023 and2423 eleven-character
rows become blank24hex. The unchanged cache survives. Both rows are still
blank during underground area192 initialization at4736, first active
underground frame4775 and terminal5138. Normal ROGUE/score/world/time
rendering is visible in the separately viewed Bomb screenshots.

Underground has381 HUD attempts and236 eligible calls. All236 reject as
cache-equal; there are **zero HUD packets, cache writes or dirty writes**.
This is not queue starvation or a nametable-mirror ambiguity. There are
only six phase markers plus one terminal snapshot, each reading two short
HUD rows; no per-frame PPU dump or capture file is produced.

The source diagnostic independently reproduces the surviving-cache/cleared-
display mismatch, receipt409ec94d. RdHsEnterScene preserves the HUD caches
while scene setup clears the nametable; ordinary status drawing restores
the name but does not invalidate the optional energy/ammo row. A lifecycle
event must invalidate that cache. A minimal private-tail proposal is under
review; no HUD patch or new nightly is qualified by this diagnostic alone.
The earlier94269 ammo-refresh proof remains specific to1-1.
