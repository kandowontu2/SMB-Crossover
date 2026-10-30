Private Benj Edwards SMB1 Toad/Peach graphics phase

Exact installed a7cc52 source parent. Variants5/6 remain outside Select.
Own source uses581/1077B in62:B772..<BBA7 and14CHRpages901..<915.
All other ROM bytes, public Kama entries, CHR, header and menu are preserved.

Actual native DrawMetasprite+X5PublishChr/source pixel controls pass744cases,
including both facings, original pose offsets, fire art and omitted zero pairs.
480wholeMain comparisons for existing0..4 preserve gameplay/OAM/33SMC/maps;
the added selected/variant checks cost0..21CPU per tested ordinary Main.
510foreign stale-variant guards pass. These are CPU controls, no native run.

The palette still uses Mario colors. Native movement, float/contact callbacks,
Fresh/lifecycle, source palettes and new menu exposure are subsequent work.
No readiness, gameplay, installation or performance claim is made.

Builds use private_build_outputs_v1 before every assembler/linker invocation.
Earlier local link attempts rejected the wrong CHR MEMORY region. The final
producer uses the formally granted range inside RECLAIMED_PARODIUS_CHR_MEM.
The frozen old Kama-map negative (27phase differences) remains in pose-proof.
