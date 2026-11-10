# FF unused OAM tail, November 10

This source-only proposal extends the qualified `58811ce678361678deff8f32966e945869be75e0f017e2bf36b2e2430ab96ebd` duplicate-guard proposal. Its in-memory image is `a5c54d7624ee961f11b45598ca7cf7fecc24de6ee87d8e8aa70dad55834f2eaa`; no ROM was written or installed and no emulator was run.

The current FF palette mux repeats its used-slot comparison, mask initialization and logical-cursor arithmetic for every unused sprite. After its existing comparison establishes that a slot is unused, the new tail performs the same attribute-bit4 clearing through every remaining physical OAM position until X wraps to RgOamRotation. It assumes no stale attribute is zero. The original visible-family scan, selection, cursor advancement, palette packet and complete register/scratch restoration remain intact. Native world-firebar admission, all 24 shuffle positions, body/shot/debris/floatey/input and PPU lifecycle work remain intact.

The 18-byte helper occupies `B679..<B68B`, the remainder of the already closed 27-byte FfPalettePointer retirement after v2's 9-byte native pipe-priority leaf. The 6-byte stub occupies `BFD6..<BFDC` inside the source-declared 273-byte epoch MAIN reservation ending at BFE0; the old MAIN used 263 bytes. Source reservation and actual gateway/control-flow checks fund these regions. The only existing instruction change is branch `BF71: B0 3A -> B0 63`; the stub rejoins the original packet call at BFC2. Neighboring priority, packet and cookie-placeholder bytes remain protected.

| Verification | Passing scope |
| --- | --- |
| Actual cold/controller Main | 16 idle and 16 Right-only empty updates; exact native state, AXYP/SP, OAM, PPU, mapper publication and NMI outputs |
| Complete mux units | 4,096 pairs: all 64 legal OAM rotations × all 64 used counts, poisoned nonzero attributes, mixed visible/clipped parts, projectile families, cursor and native palette-control values |
| Lifecycle | Four classes × ready/new life/life award/new area/new world/unready = 24 paired actual Main executions |
| Header/lifetime | All 16 header bytes × two flags reject source graphics; new warm check reads 0 PPU bytes; old 588 cache rejects and genuine new cold reload reads 16,400 bytes |
| Interrupts | All 13 changed instruction seams; 27 real NMI returns/resumes, 14 real IRQ returns/resumes, 13 masked requests and one nested IRQ at the real lag-NMI CLI; 84 paired actual ISR executions, complete native hardware and foreground-resume equality |

In the 32 real empty updates, the change saves 1,136–1,158 cycles per Main, mean 1,153.875 beyond 588's 2,728. The final walking Main costs 49,011 cycles. The directed dense limit with one unused sprite costs 8 additional cycles; the original zero-unused path is unchanged. The full mux matrix ranges from −8 to 1,378 cycles saved. This proposal does not resolve overwhelming idle lag. Fullstage, powerup-route and physical cadence qualification of a5 remain pending; earlier 96/588 receipts retain their original pins.

Frozen source: `tools/reference/ff_mux_unused_tail_1110.s`, SHA256 `cd934178747bb70e8d22a61e3695421ac9cf28b2391a69161215e6cd257d2dc4`. Frozen checker: `tools/audit/check_ff_mux_unused_tail_1110.py`, SHA256 `210c6f7cd8bd30bbf6826e1e12a37888dd2a4ee04433694b45e03f0fcf1375d2`.

The new kernel SHA256 is `d2e66b5d1d55ac8b559ded5c2e16054b1bb0cf26dfe05c1a361d089dda06cc31`; full cookie `a716000cd2e66b5d1d55ac8b559ded5c` advances coherently to revision 12. The actual cold menu still reaches first active Main 167, followed by its first active-body update 168, with 16,400 PPU reads and 8,209 RAM3 writes. Tests use Python `-B` under the bounded runner with `--max-files 1`. Output root `build/ff-mux-unused-tail-cpu-1110` remained absent; all generated results were stdout only.
