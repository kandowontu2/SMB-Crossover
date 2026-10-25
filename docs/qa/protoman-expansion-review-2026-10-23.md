# Proto Man versus production MMC5 staging — independent review

Reviewed 23 October 2026. This review reads the frozen Proto Man packet and the guide agent's frozen `mmc5-native-kb-private/merge-staging/` overlay. It changes neither packet, their tests/output, nor main. `review.json` and `mapper-core-source-diff.patch` are retained in `build/verification/protoman-expansion-review-agent/`.

**The supported expanded target has no mapper/core behavioral difference. Diagnostic signatures and probe routines are not required.**

## Compiled comparison

* Both headers are exactly `4e45531a408051080000070000000000`: mapper5, 1 MiB PRG, 1 MiB CHR, 8 KiB work RAM.
* The whole 8 KiB bank62 is byte-identical, SHA256 `8889e4ac168ac66a61c0e68842b12bc4b73474358c9e333643847ebb7238844a`.
* `MapperInit` (108 bytes including its initial CHR table), `BankSwitchCHR` (150), `NonMaskableInterrupt` (218), `IrqScrollSplit` (68), and `CrossoverGraphicsBank` (68) retain identical CPU addresses and bytes.
* All five public expansion API entry addresses and all fifteen ABI bytes match. Shared low-memory/RAM symbols have no address mismatch.
* The existing 256 KiB CHR is identical. Production has 768 KiB of zero-filled upper CHR. Proto replaces its first 20,480 bytes with the authentic prepared character art; the rest remains zero.
* The differing PRG banks are 1,3,4,9,10,29,64,65,66,127: Proto's game/presentation/menu/audio hooks and assets. Bank62 and resident bank126 are unchanged. These differences do not imply the whole NMI route is identical: Proto deliberately changes the called `MegaManAudioUpdate` leaf, while preserving the native NMI dispatcher itself.

The new independent linked-code checks execute both ROMs directly: eight cold-init cases and 216 set/publish/clear cases. Expected physical banks are computed explicitly for all twelve windows at 0,255,256,275,511,512,767,768,1023. No diagnostic CHR is read. Cold initialization/clear preserve Proto's neighboring `$73DD/$73DE` bytes, and the upper latch ends at zero. These are additional CPU/register checks, not new hardware or full-campaign claims.

## Source/build differences

| Item | Proto private packet | Production staging | Adoption |
|---|---|---|---|
| Cold expansion core | Old experimental comment | Updated ABI reservation comment | Keep production file; executable bytes are identical. |
| Mapper source | Separate expanded-only `mmc5_expanded_mapper.s`, selected by entrypoint | `mmc5.s` contains guarded expanded and original branches | Keep production `mmc5.s`; do not adopt Proto's include-redirection hunk. |
| Default flag | Entrypoint `.ifndef` fallback to0 | `bool_option ENABLE_MMC5_EXPANDED,0` in options | Keep production options/default. |
| Target guard | Expanded header asserts MMC5 | Expanded header/include gated by MMC5 AND flag | Keep production guard. Gate Proto aliases/include by MMC5, Crossover and expansion. A forced flag on MMC3 is rejected by the private Proto header, while the production hardware-only overlay selects its legacy path. This is a build-configuration difference, not a supported-target runtime difference. |
| Core include | Tail block includes core and Proto | Tail block includes core once | Keep exactly one production core include; append only the guarded Proto include. |
| Linker | Adds four Proto segments and requires upper-CHR segment | No Proto segments; upper-CHR segment is optional | Add only the four segments to production config, retaining the reserved banks64/A,65/C,66/A. |
| Asset delivery | `protoman.s` emits the upper-CHR asset itself | Builder optionally accepts `--chr-extra` | Choose one owner of these bytes. With Proto's current include, do not also pass that same asset through `--chr-extra`. |
| Builder | Private reproduction script imports the older frozen experiment | Production separate target has default/off protection and prepared-art input | Use the production builder for adoption; the private script remains a reproduction artifact. |

Retain early fixed aliases/export declarations for `ProtoVariant=$73DD` and `ProtoAudioState=$73DE`; no SRAM `.res` should be inserted. Merge Proto's seven source hooks by context to preserve root's newer Bass/level work. Do not replace whole files from the older private snapshot.

## Diagnostic independence and frozen evidence

Neither linked ROM exposes `X5Probe64` or `X5Probe125`. Neither production core nor Proto core contains probe segments. Proto source contains no diagnostic graphics asset, and Proto bank125 is entirely `$FF`. Bank64 contains the actual native MM3 driver/scores. The private reproduction script mentions probe names only to remove them. No test-signature value is consumed by any character code.

Frozen identities verified directly:

* Proto ROM: `21026233c3e8a37f766d9b2512d42d33b9263fdfe223b5972be916ccd8072c4c`.
* Production staged ROM: `757c2f0ac7bc53993bdcb597f9cec77d6fd1130bc21024e141a5659202f223cd`.
* Proto manifest: `c552788fcbc3e226a6a7160bb70df41736d38330c452392f8e64ab952a156b6a`.
* Production manifest: `ef35b80bcb4e37ea260a14e785ad9c1aea50daf8da91cea6cc1e0dd2d01a0090`.

Every file in the original Proto tree and production staging tree was hashed before and after this review; both trees remained unchanged. All artifact hashes recorded by their existing manifests still match. Only new review files were written.
