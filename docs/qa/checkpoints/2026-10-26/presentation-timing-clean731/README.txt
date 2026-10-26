CLEAN731 FINITE TIMING COMPONENTS -- NOT AN ADOPTION RECEIPT

Original Mega/Proto shots are restored; the held shot-budget experiment is absent.
Fresh 450-frame physical input test:402 full DMA pages,72 safe enables,
442 NMI returns and79 IRQ31 checks pass.275 actual PPU frames176..450
are hashed; eight actual wholeframes appear on the sheet. ROOT viewed
all eight. The first-active372 HUD does not wrap; enable is260:83 and
DMA completion260:72. Queue/phase differences also affect that timing.

Fresh staged heavy-audio Hard1F240 control passes the strict existing
source/hardware/cadence comparison with3cee:280 source calls,850 APU
stores and no draw-prefix deferral. Complete totals240updates/168draws;
the compared280-frame scope has167draws. ROOT separately compared
every byte of all168 physical DMA pages while rendering was disabled.
The actual case-end ARGB is byte-exact to3cee. This preserves cadence;
it does not remove existing gameplay lag or prove sprite visibility.

Full-menu1800 review, broader gameplay and every-powerup work remain
separate. Old b0/59 negative and prototype results keep their own hashes.
External capture paths are hashes only; no private binaries are included.
