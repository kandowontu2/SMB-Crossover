# WWF native death completion — November 2

Current installed MMC5 SHA256: `1966a4883a888a5e62f90c4d3e96d25ecf028ddd7d714214727793418d633243`. Actual Downloads launch is verified;
the ROM was replaced directly with no backup or sidecar patch.

Hogan's natural1-1 attempt cleared all four pipes and defeated three enemies,
then fell into the first pit. Engine11 never completed because WWF's typed
death-tick row8 pointed to WfNoop. The stall is reproduced through the actual
public service: ten calls leave death age0 and engine11 unchanged.

The repair changes only three existing table bytes in PRG96 at B7F4, shared
by all six wrestlers. Row8 now selects the existing native guest death worker.
It uses the already initialized150-tick pit or168-tick contact sequence, then
enters native life loss. No new timer, RAM, physics or art is added.

CPU verification covers both complete death sequences and real PlayerLoseLife
for all six variants,420 unchanged other WWF service resolutions,84 foreign
resolver full-state comparisons and two invalid WWF selectors. Real Mesen
controller runs verify ordinary enemy-contact death→one life lost→active1-1
respawn for every wrestler, retaining identity. Hogan's original first-pit
route also recovers into active1-1. Actual Downloads repeats his contact case.

Full1-1 is still unqualified. The first controller jumps too early for the first
gap, so that failure does not establish a helper-platform requirement. Other
gaps, all earned powerups, authentic endurance/advanced moves and lag remain
open. This fixes life-loss progression, not original WWF death artwork.

Compact evidence: `docs/qa/checkpoints/2026-11-02/wwf-death-v2/receipt.json`.
