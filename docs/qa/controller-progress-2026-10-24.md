# Current OG controller progress

The live private MMC5 ROM is checkpoint `inventory-stack-og`, SHA-256
`2e916d5da5448bec576a930fddf3d1469472b976756c95da6fadddb2ca98729a`.
Its1073-file source ZIP independently rebuilds that ROM. The published mapper
ROMs are preserved. The full goal remains active and incomplete.

On this exact hash, three identities now have zero-death1-1discoveries and
independent byte-exact input/trace replays through movable1-2 in both modes:

| Identity | Easy frames | Hard frames | Lossless replay PNGs |
|---|---:|---:|---:|
| Sophia |5410|5368|10378|
| Scrooge |4488|4627|8715|
| Simon |6057|5677|11334|

This is6 of the required74identity/mode pairs on OG, rather than a transfer of
earlier mixed-hash results. All37cold entries also pass, but entry is not a
level clear or an equipment test. Each pair passes the existing CHR, complete
PNG, scroll-scanline, adjacent-frame world<=8/camera<=4 bounds. Sophia's one
positively observed projectile-origin RAM sample is handled as documented in
`inventory-stack-repair-2026-10-24.md`; original failed evidence remains retained.
Root viewed two24-frame overview sheets per identity and Sophia's exact
borrowed-origin frames. These samples do not establish exhaustive human pixel
review. Significant measured lag remains on all three routes.

Scrooge's earlier controller fell in the late stair gap. Freezing and embedding
the existing character-specific native pogo/navigation policy, without its
workspace-output-path assumption, clears both modes. His game movement,
physics, collision and pogo remain unchanged.

Simon uses his existing source double-jump to clear the tall pipe. His original
generic Hard controller then died by falling onto a Goomba. A controller-only
wrapper stops on support, faces a nearby enemy and supplies native whip edges,
using the existing crouch whip against a Goomba. Both modes now clear and replay.
The older specialized policy stalled repeatedly at the first upgrade; those
failures remain retained. No Easy/Hard contact rule, jump or death assertion
was changed to obtain the passing runs.

Current receipts are in `build/verification/controllers-oh/` and
`build/verification/inventory-stack-og/`. Full external evidence is under
`C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-sophia-lock-og/fix-v1`
and `C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-controllers-og`.

Remaining work includes all other current-hash routes, every applicable item
with actual physical emergence/pickup/use/damage/expiry and SFX, remaining
graphics/body/lag defects, source audio and behavior fidelity, and the full
oversized MMC3 port. This note does not narrow that scope or mark the goal done.
