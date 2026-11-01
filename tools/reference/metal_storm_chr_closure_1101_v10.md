Metal Storm / Tank shared physical-CHR consumer closure, revision 10

This is a source/compiled-consumer and CPU-publication audit for the current
c864e46a8f333ab7a936c8d8f330944041a3eff12bc6dd4d9ba96892144ff3c7 ROM.
It grants no resource and changes no ROM, menu, shared source or installed WIP.
Parent root must explicitly allocate resources before either producer writes
them. Actual loader/Main/ISR/controller/native admission remains separate.

The proposed Metal set is247..250,494..500,827..831. Proposed Tank pages are
501/502. Existing legal consumers and their source-valid table/index domains
avoid these pages. Thomas's upper1 cold table really reads511, so494..517 is
not a free block. Karnov HUD now owns1023; the old v8 loader's1023 must be
replaced with500 only after root grants500.

The audit reads one pinned current debug into compact metadata, then reuses
that metadata. It never retains a full ROM/debug/sideoutput image. ld65 ooffs
is correctly interpreted in each segment's oname output namespace; a private
WRAM image is not an offset in the complete cartridge. Actual linked tables
include all122 Kirby and90 Meta Knight rows; CV3 counts are41/43/34 for each
facing, not guessed equal lengths.

The inherited global inventory has845 classified source instructions.
831 current instruction bodies are byte-exact. The other14 historical PCs are
all inside current Karnov ownership:12 within ROM29 [243264,245696], and2
inside its authenticated RAM3 kernel image. They are replaced using exact
semantic source from the frozen authoritative HUD source packet
ae5e53e01d7796f6d5beab97668b4f02a270c5dc60027d1cda181b6dfe11f777.
The current Kirby owner link proves that all these regions remain byte-exact
from99bf88c8. No unrelated owner was silently waived.

Karnov range checks execute the actual current24-byte carrier-map leaf for
all12 source rows:0..7 produce399..406;8..11 produce1019..1022. Body selection
is407 plus the genuine five-value pose-page table, hence407..411; shots410,
cold body408, HUD1023. The real current renderer/HUD leaves are matched against
their original source constants. The frozen complete loader/HUD Main receipts
remain bound external evidence; no new native run is claimed by this audit.

All43 typed physical publishers are bound to exact named source. Actual
current table bytes tighten every upper1 argument owner beyond the old coarse
"below768" result. WWF is safe for every possible A byte: only58..75 selects
upper1, mapping442..459; other branches force upper2. Thomas's168 body-window
bytes are0..5, selecting434..439, while its cold table selects426..433/511.
Legacy ChrPhysicalMap never exceeds246. Existing special/HUD, forced-blank
loader and indirect/zero/array invariants remain inherited under their exact
source and finite ABI contracts. Arbitrary corrupt RAM is not authorized.

An interrupt may see a low byte before its new mode. The real setter tests
deliberately create transient shadow pairs naming494..502/827..831. Neither
FamilyMainCommit nor NmiDisable alone is a universal CHR fence. Actual lag NMI
calls the native owner-specific guard: selected nonzero owners and Mario
variant2 retain old hardware CHR. Plain rawMario0 is different and may publish.

Actual source QueueSelection retires CF/cache state without new CHR stores,
then FmNativePrepare clears all12 interpretation modes, both override upper
fields and wide-active before it writes any new native low page. Thus native
Mario's allowed lag publication sees old-valid pairs or the bounded legacy map.
Prebuilt gray roster background glyphs do not draw a second body's CHR while
Mario is selected. The colored native preview uses the current selected owner.

The CPU proof inserts real lag NMI at2240 typed-setter cuts and2376 genuine
native-Mario clear/restore cuts, covering native Mario variants0/1/3..6 and36
busy-guard identity cases. It executes4652 actual ISR returns and168816
hardware CHR writes without selecting a proposed page. Saved AXYP/SP and
foreground03..0A are preserved. The audio child alone is an explicit return
port. At resident166/175, NMI may finish the pending shadow-before-hardware A
map one instruction early; exact saved registers resume the same STA5115.
This is modeled explicitly rather than called bit-exact hardware-map retention.
IRQ's source-resolved low0 write can only fetch0/256/512/768 for any upper latch.

Reproduce under the bounded runner in a new owned revision root. The frozen
v10 root cannot be resumed. Its four producer scripts capture compact inputs,
audit tables/source, test publication cuts, and close the replaced owner leaves.
The freeze tool packages source/receipts only. Historical proof graphs and
whole source/object/debug trees are neither recursively restored nor archived.

Any new publisher, loader, source table, alias, handoff or menu ordering change
must invalidate/recheck this closure. The explicit selected-player palette
adaptation and star/flower phase0 exceptions from frozen v9 still apply. There
is no native emulator, hardware timing, full-stage or complete-character claim.
